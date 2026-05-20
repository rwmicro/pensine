---
title: "Méthodologie OSINT"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > OSINT"
tags: [sciences-appliquées, informatique, sécurité, osint]
date: "2026-02-25"
---

# Méthodologie OSINT

L'OSINT (Open Source Intelligence) est la collecte et l'analyse d'informations disponibles publiquement pour produire du renseignement exploitable. Contrairement à d'autres formes de collecte de renseignement, l'OSINT n'implique aucun accès non autorisé.

## Cycle du renseignement OSINT

```
1. Planification       → Définir objectifs, scope, contraintes légales
2. Collecte            → Identifier sources, collecter données
3. Traitement          → Organiser, normaliser, filtrer
4. Analyse             → Corréler, vérifier, interpréter
5. Dissémination       → Rédiger rapport, partager
6. Feedback            → Évaluer pertinence, améliorer
```

## Passive vs Active OSINT

| | Passive | Active |
|--|---------|--------|
| Définition | Aucune interaction avec la cible | Contact direct ou indirect |
| Traces laissées | Aucune | Oui (logs, connexions) |
| Exemples | Google, archives, réseaux sociaux | Scan DNS, Shodan, requêtes directes |
| Légalité | Toujours légal si source publique | Dépend du contexte |
| Usage recommandé | Reconnaissance initiale | Phase approfondie avec autorisation |

## Reconnaissance d'un domaine / organisation

### DNS

```bash
# Enregistrements de base
dig example.com ANY
dig example.com A
dig example.com MX
dig example.com TXT
dig example.com NS

# Transfert de zone (DNS zone transfer — souvent bloqué mais à essayer)
dig axfr @ns1.example.com example.com

# Sous-domaines via brute force DNS
dnsx -d example.com -w subdomains.txt
amass enum -passive -d example.com
subfinder -d example.com
assetfinder --subs-only example.com

# Reverse DNS (IP → hostname)
dig -x 93.184.216.34

# Historique DNS
curl -s "https://api.securitytrails.com/v1/history/example.com/dns/a" \
     -H "apikey: $ST_KEY"
```

### WHOIS et informations de domaine

```bash
# WHOIS
whois example.com
whois 93.184.216.34   # WHOIS d'une IP (ASN, organisation)

# Informations registrar, dates d'enregistrement, nameservers
# Souvent partiellement masqué (WHOIS privacy)

# Historique WHOIS
# https://domaintools.com
# https://viewdns.info/whoishistory/

# Certificate Transparency (trouver des sous-domaines via les certs TLS)
curl -s "https://crt.sh/?q=%25.example.com&output=json" | \
    python3 -m json.tool | grep '"name_value"' | \
    sed 's/.*: "//;s/".*//' | sort -u

# Avec jq
curl -s "https://crt.sh/?q=%25.example.com&output=json" | \
    jq -r '.[].name_value' | sort -u | grep -v "^*"
```

### Infrastructure IP

```bash
# ASN d'une organisation
whois -h whois.radb.net -- '-i origin AS15169'  # IPs de Google
curl -s "https://api.bgpview.io/search?query_term=Google"

# Plages IP d'une organisation
curl -s "https://api.hackertarget.com/aslookup/?q=google.com"

# Shodan
shodan search "org:\"Target Company\""
shodan host 93.184.216.34

# Censys
curl -s "https://search.censys.io/api/v2/hosts/search?q=services.tls.certificates.leaf_data.subject.organization=Target" \
     -H "Censys-Api-Id: $CENSYS_ID" \
     -H "Censys-Api-Secret: $CENSYS_SECRET"
```

### Technologies et stack

```bash
# Wappalyzer (CLI ou extension navigateur)
# Identifie CMS, frameworks, serveurs, analytics

# builtwith.com — stack technique complète

# WhatWeb
whatweb example.com
whatweb -a 3 example.com  # Plus agressif

# wafw00f — détecter un WAF
wafw00f example.com

# Headers HTTP
curl -sI https://example.com | grep -i "server\|x-powered-by\|x-generator"
```

## Reconnaissance de personnes

### Réseaux sociaux et profils en ligne

```bash
# Sherlock — trouver un username sur 300+ sites
sherlock john_doe

# Maigret (plus complet que Sherlock)
maigret john_doe

# theHarvester — emails, noms, IPs depuis les moteurs de recherche
theHarvester -d example.com -b google,bing,linkedin,twitter

# LinkedIn (sans compte)
# site:linkedin.com/in "company name" "job title"
# Google: site:linkedin.com "works at Target Company"
```

### Recherche d'emails

```bash
# Hunter.io — trouver des emails d'une organisation
curl -s "https://api.hunter.io/v2/domain-search?domain=example.com&api_key=$HUNTER_KEY"

# Formats d'emails courants à tester
# prenom.nom@example.com
# pnom@example.com
# n.prenom@example.com

# Vérifier si un email existe (SMTP verification)
# telnet mail.example.com 25
# VRFY user@example.com

# Fuites de données
# haveibeenpwned.com
# dehashed.com
# intelx.io
```

### Métadonnées de fichiers

```bash
# ExifTool — extraire les métadonnées
exiftool photo.jpg     # GPS, appareil, auteur, logiciel
exiftool document.pdf  # Auteur, organisation, logiciel utilisé

# Rechercher les documents publics d'une organisation
# Google Dorks :
# site:example.com filetype:pdf
# site:example.com filetype:docx OR filetype:xlsx

# Télécharger et analyser en masse
for url in $(curl -s "https://api.example.com/docs" | grep -o 'https://[^"]*\.pdf'); do
    wget -q "$url" && exiftool "$(basename $url)" | grep -i "author\|creator\|company"
done
```

## Google Dorks

Requêtes avancées Google pour trouver des informations cachées :

```
# Restreindre à un domaine
site:example.com

# Type de fichier
site:example.com filetype:pdf
site:example.com filetype:xlsx confidential

# Texte dans l'URL
inurl:admin site:example.com
inurl:login site:example.com
inurl:.php?id= site:example.com  # SQLi potentiel

# Texte dans le titre
intitle:"index of" site:example.com  # Directory listing
intitle:"admin panel" site:example.com

# Texte dans la page
intext:"password" site:example.com
intext:"api_key" site:example.com filetype:txt

# Combinaisons utiles
site:github.com "example.com" "password"
site:pastebin.com "example.com"
site:trello.com "example.com" inurl:public

# Fichiers de configuration exposés
site:example.com filetype:env
site:example.com filetype:conf
site:example.com filetype:bak
site:example.com "wp-config.php"

# Cameras et IoT
intitle:"webcam" inurl:view.shtml
inurl:"/cgi-bin/viewer/video.jpg"
```

**GHDB** (Google Hacking Database) : https://www.exploit-db.com/google-hacking-database — catalogue de milliers de dorks.

## Code source et fuites

### GitHub / GitLab

```bash
# Recherche dans GitHub
# Chercher des secrets hardcodés pour un domaine
# "example.com" "password"
# "example.com" "api_key"
# "example.com" "secret"

# trufflehog — scanner les repos pour des secrets
trufflehog github --org=target_organization
trufflehog git https://github.com/org/repo.git

# gitleaks
gitleaks detect --source=/path/to/repo --report-path=report.json

# gitrob — reconnaissance GitHub d'une organisation
gitrob --github-access-token $TOKEN target_organization
```

### Recherche de secrets dans les buckets

```bash
# AWS S3 — buckets publics
# Noms courants à tester : backup, data, dev, staging, prod, assets
aws s3 ls s3://company-backup --no-sign-request
aws s3 ls s3://company-data --no-sign-request

# Outils de découverte
bucket-finder -l wordlist.txt -r us-east-1 example.com
AWSBucketDump -l bucket_list.txt -g interesting_Keywords.txt
```

## Ressources de renseignement

### Sources de données exposées

```bash
# Shodan — moteur de recherche pour appareils connectés
shodan search "ssl:example.com"
shodan search "hostname:example.com"
shodan search 'net:93.184.0.0/16 port:22'

# Censys — alternative à Shodan
# search.censys.io

# Fofa (chinois, découverte globale)
# fofa.info

# GreyNoise — contexte sur les IPs (scanner connu vs attaque ciblée)
curl -s "https://api.greynoise.io/v3/community/8.8.8.8" \
     -H "key: $GN_KEY"
```

### Threat Intelligence pour OSINT

```bash
# OTX AlienVault — IOCs, TTPs
curl -s "https://otx.alienvault.com/api/v1/indicators/domain/example.com/general" \
     -H "X-OTX-API-KEY: $OTX_KEY"

# VirusTotal — réputation domaine/IP/fichier
curl -s "https://www.virustotal.com/api/v3/domains/example.com" \
     -H "x-apikey: $VT_KEY"

# urlscan.io — analyser une URL sans la visiter
curl -s -X POST "https://urlscan.io/api/v1/scan/" \
     -H "API-Key: $URLSCAN_KEY" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com", "visibility": "private"}'

# URLhaus — URLs malveillantes connues
curl -s -d "url=https://example.com" "https://urlhaus-api.abuse.ch/v1/url/"
```

## Opérateurs et frameworks

### Maltego

Outil graphique de data mining et visualisation des relations entre entités. Transforms disponibles pour :
- Domaines ↔ IPs ↔ ASN
- Emails ↔ Personnes ↔ Organisations
- Comptes sociaux ↔ Personnes

### Recon-ng

Framework modulaire Python pour l'OSINT :

```bash
recon-ng
# Créer un workspace
workspaces create target_company
# Charger un module
modules load recon/domains-hosts/hackertarget
# Configurer et lancer
options set SOURCE example.com
run
# Voir les résultats
show hosts
show contacts
```

### SpiderFoot

OSINT automation platform, scanne automatiquement plus de 200 sources :

```bash
# Démarrer
python3 sf.py -l 127.0.0.1:5001

# Mode CLI
python3 sf.py -s example.com -m sfp_dnsresolve,sfp_whois,sfp_shodan -o csv
```

## Aspects légaux et éthiques

**Généralement légal** :
- Consultation de sources publiques (Google, réseaux sociaux)
- WHOIS, DNS
- Certificate Transparency

**Zone grise** :
- Scraping automatisé intensif (violation ToS)
- Collecte de données personnelles sans finalité légitime (RGPD)
- Agrégation de données pour profiler des individus

**Illégal** :
- Accès non autorisé à des systèmes (même via credentials trouvés en OSINT)
- Violation RGPD dans le traitement des données personnelles collectées
- Utilisation des informations pour harcèlement ou fraude

**Principes éthiques** :
- Proportionnalité : collecter seulement ce qui est nécessaire
- Finalité légitime documentée
- Minimisation des données
- Destruction des données après usage

## Rapport OSINT

Structure d'un rapport OSINT complet :

1. **Executive Summary** — Conclusions principales, niveau de risque
2. **Scope** — Cible, périmètre, dates
3. **Méthodologie** — Sources consultées, outils utilisés
4. **Infrastructure exposée** — IPs, domaines, ports ouverts, technologies
5. **Informations sur le personnel** — Contacts, emails trouvés, profils LinkedIn
6. **Informations sensibles exposées** — Données dans GitHub, buckets publics
7. **Recommandations** — Actions correctives priorisées
8. **Annexes** — Captures d'écran, données brutes
