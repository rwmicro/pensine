---
title: "Shodan"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Shodan"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-04"
---

# Shodan

## Vue d'ensemble

Shodan est un moteur de recherche pour dispositifs connectés à Internet (IoT, serveurs, caméras, etc.). Contrairement à Google qui indexe le contenu web, Shodan scanne et indexe les bannières et métadonnées des services exposés sur Internet.

## Qu'est-ce que Shodan ?

### Fonctionnement

**Scanning**
- Scan continu d'Internet (IPv4)
- Connexion aux ports communs
- Récupération des bannières
- Indexation des métadonnées

**Bannières**
- Réponses des serveurs
- Informations sur services
- Versions de logiciels
- Configurations

### Information collectée

- Adresse IP et port
- Organisation et FAI
- Localisation géographique
- Service et version
- Système d'exploitation
- Headers HTTP
- Certificats SSL
- Vulnérabilités connues

## Utilisation

### Interface Web

**Recherche de base**
```
apache
nginx
port:22
country:FR
city:Paris
org:"Digital Ocean"
```

**Recherches avancées**
```
# Caméras webcam
title:"webcam" country:US

# MongoDB non protégées
mongodb port:27017 -authentication

# Elasticsearch exposées
port:9200 elasticsearch

# Panels de contrôle industriels
"SCADA" port:502

# Serveurs FTP anonymes
port:21 "230 Login successful"

# Serveurs RDP
port:3389 "Remote Desktop"
```

### Filtres Shodan

**Réseau**
- `ip:` - IP spécifique
- `net:` - Plage d'IPs (CIDR)
- `port:` - Port spécifique
- `hostname:` - Nom d'hôte

**Géographique**
- `country:` - Code pays (FR, US, etc.)
- `city:` - Ville
- `geo:` - Coordonnées lat,lon,radius

**Organisation**
- `org:` - Organisation
- `isp:` - Fournisseur Internet
- `asn:` - Autonomous System Number

**Service**
- `product:` - Nom du produit
- `version:` - Version du logiciel
- `os:` - Système d'exploitation

**HTTP spécifique**
- `title:` - Titre de la page
- `http.html:` - Contenu HTML
- `http.status:` - Code HTTP
- `http.component:` - Composants web

**SSL/TLS**
- `ssl:` - Certificat SSL
- `ssl.cert.subject.cn:` - Common name
- `ssl.cert.expired:` - Certificats expirés

**Vulnérabilités**
- `vuln:` - CVE spécifique
- `vuln:CVE-2014-0160` - Heartbleed

### CLI et API

**Installation**
```bash
pip install shodan
```

**Initialisation**
```bash
shodan init YOUR_API_KEY
```

**Commandes CLI**
```bash
# Recherche
shodan search "apache"

# Info sur une IP
shodan host 8.8.8.8

# Télécharger résultats
shodan download results.json.gz "port:22"

# Parser résultats
shodan parse results.json.gz

# Compter résultats
shodan count "nginx country:FR"

# Statistiques
shodan stats --facets country,org "nginx"
```

**Python API**
```python
import shodan

api = shodan.Shodan('YOUR_API_KEY')

# Recherche
results = api.search('nginx')
for result in results['matches']:
    print(result['ip_str'], result['port'])

# Info sur IP
host = api.host('8.8.8.8')
print(host['hostnames'])
print(host['ports'])

# Streaming (temps réel)
for banner in api.stream.ports([80, 443]):
    print(banner)
```

## Use Cases

### Sécurité défensive

**Asset Discovery**
- Trouver assets de votre organisation
- Shadow IT
- Services oubliés
- Mauvaises configurations

**Vulnerability Management**
```
org:"YourCompany" vuln:CVE-2021-44228
```

**Monitoring**
- Alertes sur nouveaux services
- Détection d'expositions
- Compliance checks

**Example: Find your exposed services**
```
org:"Your Organization Name"
net:YOUR_IP_RANGE
```

### Red Team / Pentest

**Reconnaissance**
- Phase de découverte
- Service enumeration
- Version detection
- Attack surface mapping

**Target profiling**
```
# Serveurs SSH vulnérables
org:"Target Corp" port:22 "openssh 7.4"

# Panels admin exposés
org:"Target Corp" http.title:"admin"

# Bases de données
org:"Target Corp" port:3306,5432,27017
```

### Threat Intelligence

**Botnet C2**
- Identifier serveurs de commande
- Tracking d'infrastructure malveillante

**IoT malware**
- Mirai botnet
- Devices infectés

**Phishing infrastructure**
- Faux sites
- Phishing kits

### Research

**Internet trends**
- Adoption de technologies
- Statistiques géographiques
- Evolution dans le temps

**IoT security**
- Devices non sécurisés
- Default credentials
- End-of-life products

## Exemples de recherches utiles

### Systèmes industriels (ICS/SCADA)

```
# Siemens PLCs
"Siemens, SIMATIC" port:102

# Modbus
port:502

# DNP3 (Electric utilities)
port:20000 DNP3

# BACNET (Building automation)
port:47808
```

### Devices IoT

```
# Webcams
title:"webcamXP"
title:"Blue Iris"

# Printers
"HP LaserJet" port:9100

# Smart TVs
"smart tv" port:8008

# NAS
"Synology DiskStation"
```

### Databases

```
# MongoDB
"mongodb server information" port:27017 -authentication

# Elasticsearch
port:9200 json

# MySQL
port:3306 "mysql"

# Redis
port:6379 "redis"

# CouchDB
port:5984 "couchdb"
```

### Panels et dashboards

```
# Kibana
"kibana" port:5601

# Grafana
title:"Grafana"

# Jenkins
"Dashboard [Jenkins]"

# Docker
"Docker-Distribution-Api-Version" port:2375

# Kubernetes
port:10250 "kubelet"
```

### Services mal configurés

```
# FTP anonyme
port:21 "230 Login successful"

# VNC sans password
"authentication disabled" port:5900,5901

# RDP ouvert
port:3389 "Remote Desktop"

# Telnet
port:23 -login -password

# RTSP (caméras)
port:554 "rtsp"
```

## Shodan Monitor

### Fonctionnalité

**Network Monitoring**
- Surveillance de plages IP
- Alertes sur changements
- Nouveaux services détectés
- Vulnérabilités

**Setup**
1. Ajouter réseau à surveiller
2. Configurer alertes
3. Recevoir notifications

**Triggers**
- Nouveaux ports ouverts
- Nouvelles vulnérabilités
- Changement de version
- Certificat expiré

## Shodan Exploits

### Recherche de vulnérabilités

```bash
# Chercher exploits
shodan search --fields ip_str,port,vulns --separator , "vuln:CVE-2014-0160"

# Compter devices vulnérables
shodan count "vuln:CVE-2021-44228"
```

**CVEs communes**
- CVE-2014-0160 (Heartbleed)
- CVE-2017-5638 (Apache Struts)
- CVE-2021-44228 (Log4Shell)
- CVE-2020-5902 (F5 BIG-IP)

## Shodan Maps

- Visualisation géographique
- Heatmaps
- Concentration de services
- Attack surface visualization

## Shodan Images

- Screenshots de services web
- Interfaces graphiques
- Panels d'administration
- Recherche visuelle

## Protection contre Shodan

### Pour organisations

**Firewall**
- Fermer ports non-nécessaires
- Whitelist IPs autorisées
- DMZ pour services publics

**Network Segmentation**
- Isoler devices critiques
- VLANs
- Jump hosts

**Banner hiding**
```nginx
# Nginx: masquer version
server_tokens off;

# Apache: masquer version
ServerTokens Prod
ServerSignature Off
```

**Authentication**
- Toujours activer
- Strong passwords
- MFA quand possible
- IP whitelisting

**Monitoring**
- Regular Shodan searches
- Alertes Monitor
- Security scanning

**Compliance**
- Regular audits
- Vulnerability management
- Patch management

### Opt-out

**Shodan opt-out**
- Nécessite contrôle du domaine
- robots.txt pas suffisant
- Demande manuelle

## Plans et pricing

**Free tier**
- 1 crédit de recherche/mois
- Résultats limités
- API limitée

**Membership ($59/mois)**
- 100 crédits de recherche
- Pas de CAPTCHA
- Plus de résultats

**Corporate/Academic**
- Credits illimités
- API étendue
- Support prioritaire

## Alternatives à Shodan

**Censys**
- Similar à Shodan
- Plus focus certificats SSL
- Recherche plus structurée

**ZoomEye**
- Cyberspace search chinois
- Similar features

**BinaryEdge**
- Internet scanning
- API-first

**FOFA**
- Cyberspace search
- Chine-based

## Aspects légaux

**Légalité**
- Shodan lui-même est légal
- Scan passif d'Internet
- Info publiquement accessible

**Usage des données**
- Ne pas exploiter vulnérabilités trouvées
- Responsible disclosure
- Usage défensif recommandé

**Termes d'utilisation**
- Respecter ToS de Shodan
- Pas de scan agressif
- Rate limiting

## Ressources

- [Shodan.io](https://www.shodan.io)
- [Shodan CLI](https://cli.shodan.io)
- [API Documentation](https://developer.shodan.io)
- Shodan Book
- Awesome Shodan Queries (GitHub)

## Sujets à approfondir

- [ ] Shodan Honeyscore
- [ ] Custom scanning avec Shodan
- [ ] Integration avec SIEM
- [ ] Automated monitoring
- [ ] Threat hunting avec Shodan


*Dernière mise à jour: 2026-01-01*
