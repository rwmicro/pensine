---
title: Recon Automation
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [recon, reconnaissance, automation, bug-bounty, osint, pentest, sécurité]
date: 2026-03-22
---

# Recon Automation

La reconnaissance automatisée permet de cartographier la surface d'attaque d'une cible de manière systématique et reproductible. C'est la première étape de tout pentest ou programme de bug bounty.

## Phase 1 — Découverte de sous-domaines

### Sources passives (sans envoyer de trafic à la cible)

```bash
# subfinder — agrège de multiples sources (Shodan, VirusTotal, CertSpotter, etc.)
subfinder -d example.com -silent -o subdomains_passive.txt

# amass (mode passif)
amass enum -passive -d example.com -o subdomains_amass.txt

# Certificate Transparency Logs
curl -s "https://crt.sh/?q=%.example.com&output=json" |
    jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u >> subdomains_passive.txt

# theHarvester (emails, sous-domaines, IPs)
theHarvester -d example.com -b all -f results.html

# Sources manuelles à vérifier
# https://dnsdumpster.com
# https://securitytrails.com
# https://shodan.io
# https://censys.io
```

### Sources actives (brute-force DNS)

```bash
# puredns — brute-force DNS ultra-rapide avec résolution valide
puredns bruteforce /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
    example.com -r resolvers.txt -w subdomains_active.txt

# dnsx — résoudre et filtrer une liste de sous-domaines
cat subdomains_passive.txt | dnsx -silent -a -resp -o resolved.txt

# gobuster DNS
gobuster dns -d example.com \
    -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
    -t 50 --append-domain

# Consolidation et dédoublonnage
cat subdomains_passive.txt subdomains_active.txt | sort -u > all_subdomains.txt
```

## Phase 2 — Découverte des hôtes actifs et des services

```bash
# httpx — vérifier quels sous-domaines ont un service HTTP/S
cat all_subdomains.txt | httpx -silent -o live_hosts.txt

# Avec informations supplémentaires
cat all_subdomains.txt | httpx \
    -title -status-code -tech-detect -web-server \
    -o live_hosts_details.txt

# Nmap — scan de ports sur les IPs découvertes
cat live_hosts.txt | while read host; do
    ip=$(dig +short "$host" | tail -1)
    echo "$ip $host"
done | sort -u > ip_to_host.txt

# Scan rapide (top 1000 ports)
nmap -iL ips.txt --top-ports 1000 -T4 -oG nmap_quick.gnmap

# Scan complet sur des cibles sélectionnées
nmap -p- -sV -sC -T4 -oA nmap_full target.example.com
```

## Phase 3 — Cartographie des endpoints

```bash
# katana — crawler web moderne (ProjectDiscovery)
katana -list live_hosts.txt -o endpoints.txt -d 3

# gospider — crawler
gospider -S live_hosts.txt -o crawl_output/ -c 10 -d 2

# waybackurls / gau — URLs historiques (Wayback Machine + CommonCrawl)
cat live_hosts.txt | waybackurls | tee wayback_urls.txt
cat live_hosts.txt | gau --subs >> wayback_urls.txt

# Extraire des paramètres des URLs historiques
cat wayback_urls.txt | uro | grep "?" > parameterized_urls.txt

# Trouver des fichiers sensibles dans les URLs historiques
cat wayback_urls.txt | grep -E "\.(sql|bak|zip|tar|gz|env|log|conf|backup|txt)" > sensitive_files.txt
```

## Phase 4 — Découverte de contenu

```bash
# ffuf — répertoires et fichiers
cat live_hosts.txt | while read host; do
    ffuf -u "${host}/FUZZ" \
        -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt \
        -o "fuzzing/${host//\//_}.json" -of json \
        -mc 200,301,302,403 -t 40 -silent
done

# Extensions sensibles sur tous les hosts
ffuf -u "https://TARGET/FUZZ" \
    -w /usr/share/seclists/Discovery/Web-Content/common.txt \
    -e .php,.bak,.sql,.zip,.env,.log,.config \
    -mc 200,301 -t 40

# Découverte de paramètres avec Arjun
arjun -u https://target.com/api/endpoint -oJ params.json
```

## Phase 5 — Fingerprinting des technologies

```bash
# whatweb — technologies web
cat live_hosts.txt | whatweb --no-errors -a3 --log-json=tech.json

# wappalyzer CLI
wappalyzer https://target.com

# webanalyze (open source)
webanalyze -host https://target.com -apps apps.json

# Shodan — recherche sur les IPs
shodan host 93.184.216.34
shodan search "org:example.com" --fields ip_str,port,hostnames

# Extraction des technos depuis les headers HTTP
cat live_hosts.txt | httpx -tech-detect -o tech_stack.txt
```

## Phase 6 — Recherche de vulnérabilités

```bash
# Nuclei — scan de vulnérabilités automatisé
cat live_hosts.txt | nuclei -tags cve,exposure,misconfig -severity high,critical \
    -o nuclei_results.txt -stats

# nuclei sur les endpoints découverts
cat parameterized_urls.txt | nuclei -tags sqli,xss,ssrf -o param_vulns.txt

# Vérification de subdomain takeover
cat all_subdomains.txt | subjack -w - -t 100 -o takeover.txt
nuclei -list all_subdomains.txt -tags takeover

# Port scan pour services exposés
nmap -iL ips.txt -p 21,22,23,25,80,110,143,443,445,3306,3389,5900,6379,8080,8443,27017 \
    --open -oG open_ports.txt
```

## Automatisation avec des frameworks

### ReconFTW

```bash
# Framework de recon tout-en-un
git clone https://github.com/six2dez/reconftw
cd reconftw && ./install.sh

# Scan complet
./reconftw.sh -d example.com -r  # --recon (toutes les étapes)
./reconftw.sh -d example.com -s  # --subdomains seulement
./reconftw.sh -l scope.txt -r    # Liste de cibles
```

### Pipeline bash personnalisé

```bash
#!/bin/bash
# Pipeline de recon minimaliste

TARGET=$1
OUTPUT="recon_${TARGET}"
mkdir -p "$OUTPUT"

echo "[+] Sous-domaines passifs..."
subfinder -d "$TARGET" -silent -o "$OUTPUT/subs_passive.txt"
curl -s "https://crt.sh/?q=%.${TARGET}&output=json" |
    jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u >> "$OUTPUT/subs_passive.txt"

echo "[+] Résolution DNS..."
cat "$OUTPUT/subs_passive.txt" | dnsx -silent -o "$OUTPUT/subs_resolved.txt"

echo "[+] Hôtes HTTP actifs..."
cat "$OUTPUT/subs_resolved.txt" | httpx -silent -o "$OUTPUT/live_hosts.txt"

echo "[+] Crawling..."
katana -list "$OUTPUT/live_hosts.txt" -o "$OUTPUT/endpoints.txt" -silent

echo "[+] Nuclei scan..."
cat "$OUTPUT/live_hosts.txt" | nuclei \
    -tags exposure,misconfig -severity medium,high,critical \
    -o "$OUTPUT/nuclei_results.txt" -silent

echo "[+] Résultats dans $OUTPUT/"
wc -l "$OUTPUT/"*.txt
```

## Outils par catégorie

| Catégorie | Outil | Description |
|---|---|---|
| Sous-domaines passifs | subfinder, amass, theHarvester | Agrégation de sources |
| Sous-domaines actifs | puredns, gobuster dns | Brute-force DNS |
| Résolution DNS | dnsx, massdns | Résolution en masse |
| HTTP probing | httpx | Vérifier les hôtes actifs |
| Crawling | katana, gospider, hakrawler | Découvrir des endpoints |
| URLs historiques | gau, waybackurls | Wayback Machine |
| Directory fuzzing | ffuf, gobuster dir | Fichiers et répertoires |
| Paramètres | Arjun, Param Miner | Découverte de paramètres |
| Fingerprinting | whatweb, webanalyze | Technologies |
| Scanning vulnérabilités | nuclei, nikto | Vulnérabilités connues |
| Takeover | subjack, nuclei | Subdomain takeover |
| Ports | nmap, masscan | Scan de ports |

## Gestion de la portée (Scope)

```bash
# Filtrer les URLs hors-scope
cat all_urls.txt | grep "example.com" | grep -v "out-of-scope.example.com" > in_scope.txt

# Vérifier si une IP appartient à la cible
curl "https://api.bgpview.io/ip/93.184.216.34" | jq '.data.asn'
whois 93.184.216.34 | grep -i "orgname\|org-name"

# Générer une liste de CIDRs depuis ASN
curl "https://api.bgpview.io/asn/15169/prefixes" | jq '.data.ipv4_prefixes[].prefix'
```

## Rate limiting et respect éthique

```bash
# Toujours respecter les limites de taux
# ffuf : -p 0.1 (délai entre requêtes)
# nuclei : -rl 50 (50 req/s maximum)
# nmap : -T2 ou -T3 (plus lent)

# Vérifier le robots.txt avant de crawler
curl https://target.com/robots.txt

# Respecter le programme de bug bounty (scope, exclusions)
# Ne pas tester en dehors du scope défini
# Ne pas tester des services tiers
# Signaler rapidement les vulnérabilités critiques
```
