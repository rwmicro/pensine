---
title: "Techniques Avancées et Cas d'Usage OSINT"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > OSINT"
tags: [sciences-appliquées, informatique, sécurité, osint]
date: "2026-02-25"
---

# Techniques Avancées et Cas d'Usage OSINT

## Techniques fondamentales

### Pivoting

Le pivoting consiste à partir d'un élément connu pour en découvrir d'autres :

```
Email → Nom → Profil LinkedIn → Entreprise → Autres employés
IP → WHOIS → Organisation → Autres IPs de l'AS
Domaine → Certificats TLS → Sous-domaines → Technologies
Username → Réseaux sociaux → Photos → Localisation
Hash de fichier → VirusTotal → IOCs liés → Infrastructure C2
```

**Exemple de chaîne de pivoting** :
1. Email `john.doe@company.com` → nom complet
2. Nom complet → profil LinkedIn → position, collègues
3. Collègues → emails des autres membres de l'équipe IT
4. Domaine → crt.sh → sous-domaines cachés
5. Sous-domaine dev → technologies exposées → CVEs applicables

### Corrélation de données

Relier des informations de sources différentes pour reconstruire une image complète :

- **Timeline** : ordonner chronologiquement les événements depuis différentes sources
- **Link Analysis** : cartographier les relations entre entités (Maltego, Gephi)
- **Clustering** : regrouper des entités similaires (même AS, même registrar)
- **Fingerprinting** : patterns uniques qui identifient la même entité sur différentes plateformes

### Vérification et cross-checking

Toujours vérifier une information avec au minimum 2 sources indépendantes :

```
1ère source → Information
2ème source → Confirme ou infirme
3ème source → Tiebreaker si contradiction
```

**Outils de fact-checking** :
- Snopes, AFP Factuel, Décodeurs (Le Monde) pour les infos virales
- Archive.org Wayback Machine pour les pages supprimées
- Google cache, Bing cache
- Cachedview.nl, archive.ph pour archiver/voir en cache

## Techniques d'anonymisation (OpSec OSINT)

### Pourquoi protéger son anonymat lors d'une investigation

- Éviter d'alerter la cible (logs de visite du site web)
- Protéger l'investigateur dans des contextes sensibles (crime organisé, gouvernements)
- Éviter le social engineering en retour

### Infrastructure d'investigation isolée

```
Machine dédiée (ou VM fraîche)
    → VPN (pays neutre)
        → Tor Browser (ou Firefox hardened)
            → Sock Puppet (faux comptes créés avec la même chaîne)
```

**VM OSINT dédiée** :
- Tails OS : Linux amnésique, tout le trafic via Tor
- Whonix : VM gateway Tor + VM workstation séparées

### Sock Puppets

Comptes fictifs créés pour effectuer des recherches sans exposer sa vraie identité.

**Création d'un sock puppet sécurisé** :
1. Utiliser une machine dédiée / VM fraîche
2. Se connecter via VPN + Tor avant toute création
3. Email jetable : ProtonMail, Tutanota, 10minutemail
4. Numéro de téléphone virtuel : TextNow, Google Voice, MySudo
5. Photo de profil : générée par IA (thispersondoesnotexist.com)
6. Cohérence biographique : âge, localisation, intérêts plausibles
7. Ne jamais se connecter depuis la même IP que les vraies activités

**Attention** : l'usage de sock puppets à des fins malveillantes est illégal. Usage légitime : investigations journalistiques, sécurité, tests.

### Traces à éviter

| Source de traces | Comment l'éviter |
|----------------|-----------------|
| IP publique | VPN + Tor |
| Logs du site web visité | Tor, en-têtes HTTP minimaux |
| Cookies de tracking | Mode navigateur privé, extensions (uBlock, Privacy Badger) |
| Fingerprint navigateur | Firefox + NoScript, Brave ou Tor Browser |
| Comptes Google/Facebook | Ne jamais utiliser en OSINT |
| Métadonnées des fichiers téléchargés | ExifTool avant analyse |
| Email d'investigation | ProtonMail via Tor |

## Cas d'usage concrets

### 1. Reconnaissance pré-pentest d'une organisation

**Objectif** : cartographier l'exposition externe d'une entreprise.

```bash
# Étape 1 : Découverte DNS
subfinder -d target.com | tee subdomains.txt
amass enum -passive -d target.com >> subdomains.txt

# Étape 2 : Résolution et filtrage des sous-domaines vivants
cat subdomains.txt | sort -u | dnsx -silent -o live_subdomains.txt

# Étape 3 : Scan des technologies
cat live_subdomains.txt | httpx -tech-detect -title -status-code -o web_discovery.txt

# Étape 4 : Shodan pour les ports et services
shodan search "org:\"Target Company\"" --fields ip_str,port,transport,hostnames

# Étape 5 : Recherche d'emails et personnes
theHarvester -d target.com -b google,bing,linkedin -l 200

# Étape 6 : Fuites de code
trufflehog github --org=target-org --only-verified

# Étape 7 : Certificats TLS pour sous-domaines cachés
curl -s "https://crt.sh/?q=%25.target.com&output=json" | \
    jq -r '.[].name_value' | grep -v "^\*" | sort -u

# Étape 8 : Regrouper et analyser
```

### 2. Investigation sur un domaine malveillant

**Objectif** : profiler l'infrastructure d'une campagne de phishing.

```bash
# WHOIS du domaine
whois malicious-domain.com

# Historique WHOIS
# https://whois-history.whoisxmlapi.com/

# DNS actuel et historique
dig malicious-domain.com ANY
dig malicious-domain.com NS

# IP et ASN
dig +short malicious-domain.com
whois $(dig +short malicious-domain.com | head -1)

# Autres domaines sur la même IP (reverse DNS)
curl -s "https://api.hackertarget.com/reverseiplookup/?q=$(dig +short malicious-domain.com | head -1)"

# Certificat TLS (identifie d'autres domaines liés)
openssl s_client -connect malicious-domain.com:443 2>/dev/null | \
    openssl x509 -noout -subject -issuer -dates -ext subjectAltName

# VirusTotal
curl -s "https://www.virustotal.com/api/v3/domains/malicious-domain.com" \
     -H "x-apikey: $VT_KEY" | python3 -m json.tool

# URLscan.io (historique de scans)
curl -s "https://urlscan.io/api/v1/search/?q=domain:malicious-domain.com" \
     -H "API-Key: $URLSCAN_KEY"

# Passage en revue sur MXToolbox
# mxtoolbox.com/SuperTool.aspx

# Contexte GreyNoise
curl -s "https://api.greynoise.io/v3/community/$(dig +short malicious-domain.com | head -1)"
```

### 3. Surveillance d'une marque (Brand Monitoring)

**Objectif** : détecter les usurpations d'identité, phishing, et mentions négatives.

```bash
# Typosquatting — trouver les domaines similaires
dnstwist example.com
dnstwist --format json example.com > typosquats.json

# Surveillance des certificats TLS (nouveaux domaines similaires)
# certstream monitor
pip install certstream
python3 - << 'EOF'
import certstream

def callback(message, context):
    if message['message_type'] == 'certificate_update':
        for domain in message['data']['leaf_cert']['all_domains']:
            if 'example' in domain.lower():
                print(f"[ALERT] New cert for: {domain}")

certstream.listen_for_certs(callback)
EOF

# Monitoring réseaux sociaux
# Mention.com, Brand24 (payant)
# Alertes Google : google.com/alerts

# Recherche sur les marketplaces dark web
# Pas d'URL à fournir ici - via Tor Browser avec précautions
```

### 4. Investigation géospatiale (GEOINT)

**Objectif** : géolocaliser une photo ou valider une localisation.

```bash
# Extraire les coordonnées GPS d'une photo
exiftool photo.jpg | grep -i gps

# Si pas de GPS : analyse visuelle
# 1. Shadow analysis : soleil.earth ou shadowmap.app pour l'heure
# 2. Architecture locale : Google Image Search + Google Street View
# 3. Panneaux, plaques d'immatriculation
# 4. Végétation endémique
# 5. Constellations (si nuit)
# 6. Direction des antennes satelites (géoloc approximative)

# SunCalc pour les ombres
# suncalc.org → entrer date/heure → vérifier direction soleil

# Pour les vidéos : InVID/WeVerify
# invid-project.eu
```

### 5. Threat Intelligence — Profiler un acteur malveillant

**Objectif** : identifier l'infrastructure d'un groupe APT.

```bash
# Partir d'un IOC (ex: hash de malware)
SHA256="abc123..."

# VirusTotal : relations, comportements, détections
curl -s "https://www.virustotal.com/api/v3/files/$SHA256" \
     -H "x-apikey: $VT_KEY"

# Relations : URLs contactées, IPs, domaines
curl -s "https://www.virustotal.com/api/v3/files/$SHA256/behaviour_summary" \
     -H "x-apikey: $VT_KEY"

# MalwareBazaar
curl -s -d "query=get_info&hash=$SHA256" "https://mb-api.abuse.ch/api/v1/"

# Depuis l'IP du C2 :
IP="1.2.3.4"
# 1. Autres malwares qui ont contacté cette IP
curl -s "https://www.virustotal.com/api/v3/ip_addresses/$IP" \
     -H "x-apikey: $VT_KEY"

# 2. Autres domaines sur cette IP
curl -s "https://api.hackertarget.com/reverseiplookup/?q=$IP"

# 3. Shodan pour les services exposés
shodan host $IP

# 4. ASN et géolocalisation
curl -s "https://api.ip-api.com/json/$IP"

# 5. Réputation GreyNoise
curl -s "https://api.greynoise.io/v3/community/$IP"

# 6. Passive DNS (quels domaines ont pointé vers cette IP)
curl -s "https://api.securitytrails.com/v1/ips/nearby/$IP" \
     -H "apikey: $ST_KEY"
```

## Géolocalisation de domaine / Attribution

```bash
# Passive DNS (historique DNS)
curl -s "https://api.securitytrails.com/v1/history/example.com/dns/a" \
     -H "apikey: $ST_KEY"

# Tous les domaines enregistrés par un email WHOIS
curl -s "https://api.whoxy.com/?key=$WHOXY_KEY&reverse=email&value=registrant@example.com"

# Tous les domaines sur un nameserver
curl -s "https://api.hackertarget.com/findshareddns/?q=ns1.example.com"

# Liens entre domaines via favicon hash (Shodan)
# 1. Calculer le hash MMH3 du favicon
python3 -c "
import requests, hashlib, base64, mmh3
r = requests.get('https://example.com/favicon.ico', timeout=5)
favicon_hash = mmh3.hash(base64.encodebytes(r.content))
print(f'shodan search http.favicon.hash:{favicon_hash}')
"
# 2. Chercher d'autres sites avec le même favicon
shodan search "http.favicon.hash:-123456789"
```

## Ressources et communautés

| Ressource | Type | Contenu |
|-----------|------|---------|
| OSINT Framework (osintframework.com) | Website | Catalogue d'outils par catégorie |
| Bellingcat Guide | Blog/Guides | Enquêtes approfondies, techniques avancées |
| SANS FOR578 | Formation | Cyber Threat Intelligence |
| TraceLabs | CTF | Recherche de personnes disparues |
| IntelTechniques (Michael Bazzell) | Blog/Podcast | Privacy & OSINT |
| Sector035 (Week in OSINT) | Newsletter | Actualité OSINT hebdomadaire |
| Dutch OSINT Guy | YouTube | Tutoriels pratiques |
| NixIntel | Blog | Techniques OSINT approfondies |
