---
title: "Outils OSINT"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > OSINT"
tags: [sciences-appliquées, informatique, sécurité, osint]
date: "2026-02-25"
---

# Outils OSINT

Catalogue des outils OSINT organisés par catégorie, avec usage pratique et commandes.

## Frameworks tout-en-un

### Maltego

Outil de data mining et de visualisation graphique des relations entre entités (personnes, domaines, IPs, organisations). Idéal pour représenter visuellement des réseaux de connexions.

- **Transforms** : modules qui interrogent des sources de données (WHOIS, DNS, Shodan, etc.)
- **Community Edition** : gratuit, transforms limités
- **Pro** : accès complet au Maltego Transform Hub

### SpiderFoot

Plateforme d'automatisation OSINT, scanne automatiquement plus de 200 sources.

```bash
# Installation
pip install spiderfoot

# Démarrer l'interface web
python3 sf.py -l 127.0.0.1:5001

# Mode CLI (scanner un domaine avec des modules spécifiques)
python3 sf.py -s example.com -t INTERNET_NAME \
    -m sfp_dnsresolve,sfp_whois,sfp_shodan,sfp_ssl,sfp_threatcrowd \
    -o csv -f results.csv

# Modules disponibles
python3 sf.py -M | grep osint
```

### Recon-ng

Framework modulaire Python (similaire à Metasploit) pour l'automatisation OSINT.

```bash
# Lancer
recon-ng

# Créer un workspace
workspaces create target_company

# Chercher des modules
modules search github
modules search email

# Charger et utiliser un module
modules load recon/domains-hosts/hackertarget
info                    # Voir les options
options set SOURCE example.com
run

# Voir les résultats
show hosts
show contacts
show credentials

# Exporter
reporting load reporting/html
options set CREATOR "SOC Team"
options set CUSTOMER "Target Company"
run  # Génère un rapport HTML
```

### theHarvester

Collecte d'emails, sous-domaines, IPs, URLs depuis des moteurs de recherche et sources OSINT.

```bash
# Recherche sur plusieurs sources
theHarvester -d example.com -b google,bing,linkedin,twitter,shodan

# Toutes les sources
theHarvester -d example.com -b all -l 500

# Sauvegarder en XML
theHarvester -d example.com -b google -f results

# Sources disponibles
theHarvester --help | grep "b "
# google, bing, linkedin, twitter, github, shodan, certspotter, dnsdumpster, etc.
```

## Découverte de sous-domaines

### Subfinder

```bash
subfinder -d example.com

# Avec sources supplémentaires (API keys configurés)
subfinder -d example.com -all -recursive

# Output JSON
subfinder -d example.com -json -o subdomains.json

# Plusieurs domaines
subfinder -dL domains.txt -o subdomains.txt
```

### Amass

```bash
# Mode passif (pas d'interaction avec la cible)
amass enum -passive -d example.com

# Mode actif (résolution DNS active)
amass enum -active -d example.com

# Avec brute force
amass enum -brute -w wordlist.txt -d example.com

# Intelligence (sources OSINT)
amass intel -d example.com -whois

# Visualiser le graphe
amass viz -d3 -dir ~/.config/amass
```

### dnsx / massdns

```bash
# Résoudre des sous-domaines en masse
dnsx -d example.com -w subdomains-wordlist.txt -o resolved.txt

# Avec massdns (très rapide)
massdns -r resolvers.txt -t A -o S subdomains.txt > results.txt
```

## Recherche de personnes et d'identités

### Sherlock — Username search

```bash
# Installer
pip install sherlock-project

# Rechercher un username sur ~300 sites
sherlock john_doe

# JSON output
sherlock john_doe --json

# Avec proxy Tor
sherlock john_doe --tor

# Plusieurs usernames
sherlock user1 user2 user3
```

### Maigret — Username search avancé

```bash
# Plus de sources que Sherlock
pip install maigret

maigret john_doe

# Rapport HTML
maigret john_doe --html

# Top sites seulement (plus rapide)
maigret john_doe --top-sites 500
```

### Social-Analyzer

```bash
# Analyse multi-plateforme
pip install social-analyzer

social-analyzer --username "john_doe" --module "analyze" \
    --output pretty --method "all"
```

## Recherche d'emails

### Hunter.io API

```bash
# Trouver des emails d'un domaine
curl -s "https://api.hunter.io/v2/domain-search?domain=example.com&limit=100&api_key=$HUNTER_KEY" | \
    python3 -m json.tool | grep '"value"'

# Vérifier si un email existe
curl -s "https://api.hunter.io/v2/email-verifier?email=contact@example.com&api_key=$HUNTER_KEY"

# Trouver l'email d'une personne
curl -s "https://api.hunter.io/v2/email-finder?domain=example.com&first_name=John&last_name=Doe&api_key=$HUNTER_KEY"
```

### h8mail — Email OSINT avec fuites

```bash
# Installer
pip install h8mail

# Vérifier si un email est dans des fuites
h8mail -t target@example.com

# Avec fichier de configuration (APIs)
h8mail -t target@example.com -c h8mail_config.ini

# Vérifier plusieurs emails
h8mail -t emails.txt
```

## Analyse d'images et géolocalisation

### ExifTool — Métadonnées

```bash
# Extraire toutes les métadonnées
exiftool photo.jpg

# GPS (si présent)
exiftool -GPS:GPSLatitude -GPS:GPSLongitude photo.jpg

# Infos de l'appareil
exiftool -Make -Model -Software photo.jpg

# Date de prise de vue
exiftool -DateTimeOriginal photo.jpg

# Supprimer les métadonnées
exiftool -all= photo.jpg
```

### Reverse Image Search

| Outil | URL | Avantage |
|-------|-----|---------|
| Google Images | images.google.com | Grand index |
| TinEye | tineye.com | Historique d'apparition |
| Yandex Images | yandex.com/images | Très efficace pour visages |
| PimEyes | pimeyes.com | Reconnaissance faciale |
| Bing Visual Search | bing.com/visualsearch | Alternative Google |

### Géolocalisation via images

Technique de géolocalisation (GEOINT) :
1. Identifier des repères architecturaux, végétation, panneaux
2. Identifier les constellations (si nuit) ou l'ombre (heure et position soleil)
3. Google Street View et Map pour confirmer
4. Outils : GeoGuessr pro, Creepy (Twitter/Instagram geolocation)

```bash
# Creepy — géolocalisation depuis réseaux sociaux
pip install creepy
creepy
```

## Outils DNS et infrastructure

### DNSdumpster

```bash
# Via l'API
curl -s "https://api.hackertarget.com/dnslookup/?q=example.com"
curl -s "https://api.hackertarget.com/hostsearch/?q=example.com"
curl -s "https://api.hackertarget.com/reverseiplookup/?q=93.184.216.34"
```

### Certificate Transparency

```bash
# crt.sh — trouver des sous-domaines via les certificats TLS
curl -s "https://crt.sh/?q=%25.example.com&output=json" | \
    python3 -c "
import json, sys
data = json.load(sys.stdin)
names = set()
for cert in data:
    for name in cert.get('name_value', '').split():
        if not name.startswith('*'):
            names.add(name.strip())
for name in sorted(names):
    print(name)
"

# certspotter
curl -s "https://api.certspotter.com/v1/issuances?domain=example.com&include_subdomains=true&expand=dns_names" | \
    python3 -m json.tool
```

### Shodan

```bash
# Installer le client
pip install shodan
shodan init $SHODAN_API_KEY

# Recherches courantes
shodan search "org:\"Example Corp\""
shodan search "ssl.cert.subject.cn:example.com"
shodan search "hostname:example.com"
shodan search "net:93.184.0.0/16 port:22"

# Infos sur un host
shodan host 93.184.216.34

# Voir l'historique d'un host
shodan host 93.184.216.34 --history

# Statistiques
shodan count "apache country:FR"

# Alertes (monitoring en temps réel)
shodan alert create "example_monitor" 93.184.0.0/16
```

## Analyse de code et secrets

### trufflehog

```bash
# Scanner un repo GitHub
trufflehog github --org=target_organization

# Scanner un repo spécifique
trufflehog git https://github.com/org/repo.git

# Scanner un système de fichiers local
trufflehog filesystem /path/to/code

# Avec vérification (confirm que les secrets sont actifs)
trufflehog git https://github.com/org/repo.git --only-verified
```

### gitleaks

```bash
# Scanner un repo
gitleaks detect --source=/path/to/repo

# Avec rapport JSON
gitleaks detect --source=/path/to/repo --report-format json --report-path report.json

# Mode protect (pre-commit hook)
gitleaks protect --staged
```

### gitrob

```bash
# Scanner une organisation GitHub
gitrob --github-access-token $TOKEN target_organization

# Résultats dans le navigateur
# http://localhost:9393
```

## Tableau récapitulatif

| Outil | Catégorie | Open Source | API requise |
|-------|-----------|------------|-------------|
| Maltego | Framework visuel | Partiel | Non |
| SpiderFoot | Automation | Oui | Pour certains modules |
| Recon-ng | Framework CLI | Oui | Pour certains modules |
| theHarvester | Emails/domaines | Oui | Optionnel |
| Subfinder | Sous-domaines | Oui | Optionnel |
| Amass | Sous-domaines | Oui | Non |
| Sherlock | Username | Oui | Non |
| Shodan | Infrastructure | Non | Oui |
| Hunter.io | Emails | Non | Oui |
| ExifTool | Métadonnées | Oui | Non |
| trufflehog | Secrets code | Oui | Non |
| gitleaks | Secrets code | Oui | Non |
| h8mail | Email breaches | Oui | Optionnel |
