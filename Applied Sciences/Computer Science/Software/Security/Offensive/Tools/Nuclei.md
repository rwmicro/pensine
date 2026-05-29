---
title: Nuclei
domain: sciences-appliquées
subdomain: informatique / sécurité / offensive / outils
tags: [nuclei, scanner, templates, pentest, sécurité, outils, bug-bounty]
date: 2026-03-22
---

# Nuclei

Nuclei est un scanner de vulnérabilités basé sur des templates YAML. Chaque template décrit comment détecter une vulnérabilité spécifique. Il est rapide, extensible, et dispose d'une bibliothèque publique de milliers de templates.

## Installation et mise à jour

```bash
# Installation
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Ou via le binaire pré-compilé
wget https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip
unzip nuclei_linux_amd64.zip && mv nuclei /usr/local/bin/

# Mise à jour des templates (à faire régulièrement)
nuclei -update-templates
nuclei -update

# Lister les templates disponibles
nuclei -tl
nuclei -tags cve | head -20
```

## Utilisation de base

```bash
# Scanner une cible unique
nuclei -u https://target.com

# Scanner une liste de cibles
nuclei -list targets.txt

# Scanner un sous-réseau
nuclei -u https://192.168.1.0/24

# Sortie dans un fichier
nuclei -u https://target.com -o results.txt
nuclei -u https://target.com -jsonl -o results.jsonl  # JSON Lines (une ligne = un résultat)
```

## Sélection de templates

```bash
# Par tag
nuclei -u https://target.com -tags cve
nuclei -u https://target.com -tags sqli
nuclei -u https://target.com -tags xss
nuclei -u https://target.com -tags exposure  # Fichiers/informations exposés
nuclei -u https://target.com -tags misconfig  # Mauvaises configurations

# Multiple tags (ET)
nuclei -u https://target.com -tags "cve,rce"

# Par sévérité
nuclei -u https://target.com -severity critical,high
nuclei -u https://target.com -severity low,medium,high,critical,info

# Template spécifique
nuclei -u https://target.com -t http/cves/2021/CVE-2021-44228.yaml  # Log4Shell

# Répertoire de templates
nuclei -u https://target.com -t http/exposures/

# Exclure des tags
nuclei -u https://target.com -etags dos,fuzz  # Éviter les tests intrusifs

# Exclure des templates
nuclei -u https://target.com -exclude-templates http/fuzzing/
```

### Catégories de templates principales

```
http/cves/          → CVE documentées (la plus grande collection)
http/exposures/     → Fichiers exposés (.git, .env, backup, admin panels)
http/misconfig/     → Mauvaises configurations (CORS, headers, Nginx, Apache)
http/vulnerabilities/ → Vulnérabilités génériques (SSRF, XSS, SQLi, LFI)
http/fuzzing/       → Fuzzing actif (plus intrusif)
http/takeovers/     → Subdomain takeover
network/            → Protocoles réseau (FTP, SSH, Redis, Mongo open...)
dns/                → Vulnérabilités DNS
ssl/                → Certificats et TLS
```

## Scans courants

```bash
# Découverte d'informations exposées
nuclei -u https://target.com -tags exposure,config,backup

# CVE récentes critiques
nuclei -u https://target.com -tags cve -severity critical -stats

# Technologies et panels d'administration
nuclei -u https://target.com -tags tech,panel

# Mauvaises configurations courantes
nuclei -u https://target.com -tags misconfig

# OAST/OOB (Collaborator-like pour détection blind)
nuclei -u https://target.com -tags oast

# Scan complet (sans fuzzing intrusif)
nuclei -u https://target.com -etags dos,fuzz -stats -silent

# Portfolio bug bounty (liste de cibles)
cat scope.txt | nuclei -tags cve,exposure,misconfig -severity high,critical -o bounty_results.txt
```

## Performance et concurrence

```bash
# Threads et taux de requêtes
nuclei -u https://target.com -c 50    # 50 templates en parallèle (défaut: 25)
nuclei -u https://target.com -rl 100  # 100 requêtes/seconde max (rate limiting)
nuclei -u https://target.com -timeout 10  # Timeout par requête (secondes)

# Résumé des statistiques en temps réel
nuclei -u https://target.com -stats

# Mode silencieux (résultats uniquement)
nuclei -u https://target.com -silent

# Mode verbose (debugging)
nuclei -u https://target.com -v

# Bulk scan avec optimisation
nuclei -list targets.txt -c 100 -rl 500 -bulk-size 25
```

## Écriture de templates

```yaml
# Template de base — détection d'un fichier exposé
id: env-file-exposed

info:
  name: .env File Exposed
  author: security-researcher
  severity: high
  description: Le fichier .env est accessible publiquement et peut contenir des credentials.
  tags: exposure,config

http:
  - method: GET
    path:
      - "{{BaseURL}}/.env"

    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200
      - type: word
        words:
          - "APP_KEY"
          - "DB_PASSWORD"
        condition: or
```

```yaml
# Template avec extracteur — récupérer la version
id: apache-version-detect

info:
  name: Apache Version Detection
  author: security-researcher
  severity: info
  tags: tech,apache

http:
  - method: GET
    path:
      - "{{BaseURL}}/"

    matchers:
      - type: word
        part: header
        words:
          - "Apache"

    extractors:
      - type: regex
        part: header
        name: version
        regex:
          - "Apache/([0-9.]+)"
```

```yaml
# Template de détection de vulnérabilité (SSRF simple)
id: ssrf-open-redirect

info:
  name: SSRF via URL parameter
  severity: high
  tags: ssrf

variables:
  oast: "{{interactsh-url}}"  # Collaborator-like intégré

http:
  - method: GET
    path:
      - "{{BaseURL}}/fetch?url={{oast}}"
      - "{{BaseURL}}/redirect?to={{oast}}"
      - "{{BaseURL}}/proxy?url={{oast}}"

    matchers:
      - type: word
        part: interactsh_protocol
        words:
          - "http"    # Si une requête HTTP est reçue → SSRF confirmé
```

```yaml
# Matchers avancés
matchers-condition: and
matchers:
  - type: status
    status: [200, 201]

  - type: word
    words: ["error", "exception"]
    negative: true  # Ne doit PAS contenir ces mots

  - type: regex
    regex:
      - "root:[x*]:0:0:"  # /etc/passwd

  - type: dsl
    dsl:
      - "len(body) > 1000"
      - "contains(headers, 'Content-Type: application/json')"
```

## Intégration dans un pipeline

```bash
# Avec subfinder + httpx + nuclei (pipeline de recon)
subfinder -d target.com -silent |
    httpx -silent |
    nuclei -tags cve,exposure -severity high,critical -o results.txt

# Avec nmap (ports ouverts → scan Nuclei)
nmap -sV -p 80,443,8080,8443 192.168.1.0/24 -oG - |
    grep "open" | awk '{print $2}' |
    xargs -I{} nuclei -u "http://{}/" -tags tech

# CI/CD — intégration dans GitHub Actions
# Voir : projectdiscovery/nuclei-action sur GitHub
```

## Gestion des faux positifs

```bash
# Vérifier manuellement un résultat
nuclei -u https://target.com -t template.yaml -v -debug

# Inclure la requête/réponse dans la sortie
nuclei -u https://target.com -include-rr -o results.txt

# Mode proxy — passer par Burp pour voir le trafic
nuclei -u https://target.com -proxy http://127.0.0.1:8080
```

## Nuclei vs autres scanners

| Critère | Nuclei | Nikto | Nessus |
|---|---|---|---|
| Templates | YAML personnalisables | Intégrés | Intégrés (propriétaires) |
| Vitesse | Très rapide | Lent | Modéré |
| Communauté | Très active | Modérée | Commerciale |
| Personnalisation | Excellente | Limitée | Limitée |
| Faux positifs | Dépend du template | Nombreux | Peu (mais payant) |
| Usage | Bug bounty, pentest | Audit rapide | Conformité, entreprise |
