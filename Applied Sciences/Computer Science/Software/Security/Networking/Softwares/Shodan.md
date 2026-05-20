---
title: Shodan
domain: sciences-appliquées
subdomain: informatique / sécurité / outils
tags: [shodan, osint, reconnaissance, attack-surface, sécurité, outils]
date: 2026-03-22
---

# Shodan

Shodan est un moteur de recherche d'équipements connectés à Internet. Il indexe en permanence les bannières des services exposés (HTTP, SSH, FTP, Telnet, HTTPS, SNMP…) sur l'ensemble des IPs publiques. C'est l'outil de référence pour la cartographie de la surface d'attaque.

## Opérateurs de recherche

```
Filtres principaux :
  hostname:target.com          → Résultats pour un nom d'hôte
  ip:93.184.216.34             → Résultats pour une IP spécifique
  org:"Company Name"           → Par organisation (ASN WHOIS)
  net:93.184.216.0/24          → Par CIDR
  port:22                      → Par port
  product:nginx                → Par logiciel détecté
  version:"2.4.49"             → Par version exacte (CVE recherche)
  os:windows                   → Par système d'exploitation
  country:FR                   → Par pays (code ISO)
  city:"Paris"                 → Par ville
  ssl:target.com               → Certificats TLS contenant ce domaine
  http.title:"Admin Panel"     → Par titre de la page HTTP
  http.html:"powered by"       → Par contenu HTML
  has_screenshot:true          → Services avec capture d'écran
  vuln:CVE-2021-44228          → Services vulnérables à une CVE (compte payant)
```

### Combinaisons utiles pour le pentest

```bash
# Surface d'attaque d'une organisation
org:"Target Corp" port:443
org:"Target Corp" port:22,3389,5900

# Trouver des instances vulnérables
product:nginx version:"1.14.0"
http.title:"phpMyAdmin" country:FR

# Équipements industriels exposés
product:modbus
port:102 product:siemens        # Siemens S7
product:"Schneider Electric"

# Caméras IP sans authentification
has_screenshot:true port:80 product:"Hikvision"
http.title:"Live View / - MOBOTIX"

# Elasticsearch / MongoDB sans auth
port:9200 product:elasticsearch http.status:200
port:27017 product:mongodb

# Interfaces d'administration exposées
http.title:"Kibana" port:5601
http.title:"Grafana" port:3000
http.title:"Jenkins" port:8080

# VPN et accès distants
product:fortinet port:443
port:4443 product:"Pulse Secure"
port:8443 product:"Cisco AnyConnect"

# Téléphonie
port:5060 product:asterisk      # VoIP SIP

# Recherche par certificat SSL/TLS (très utile pour trouver toute l'infra d'un domaine)
ssl:"target.com"
ssl.cert.subject.cn:"*.target.com"
ssl.cert.subject.organization:"Target Corp"
```

## CLI Shodan

```bash
# Installation
pip install shodan

# Configuration de la clé API
shodan init API_KEY

# Informations sur son propre compte
shodan info

# Recherche en ligne de commande
shodan search "org:Target http.title:admin"
shodan search --fields ip_str,port,org,os "nginx 1.14"

# Informations sur une IP spécifique
shodan host 93.184.216.34

# Scan d'une IP (payant — utilise les crédits Shodan)
shodan scan submit --filename result.json 93.184.216.34

# Télécharger les résultats d'une recherche
shodan download results.json.gz "org:Target"
shodan parse results.json.gz --fields ip_str,port,hostnames

# Alert — surveiller une plage IP (notifications si nouveaux services)
shodan alert create "Target Monitoring" 93.184.216.0/24
shodan alert list
```

## Shodan en Python

```python
import shodan

api = shodan.Shodan("API_KEY")

# Recherche
results = api.search('org:"Target Corp" port:443')
print(f"Résultats : {results['total']}")
for result in results['matches']:
    print(f"IP: {result['ip_str']}:{result['port']}")
    print(f"  OS: {result.get('os', 'N/A')}")
    print(f"  Org: {result.get('org', 'N/A')}")

# Informations détaillées sur une IP
host = api.host("93.184.216.34")
print(f"Hostname: {host['hostnames']}")
print(f"Country: {host['country_name']}")
for service in host['data']:
    print(f"Port {service['port']}: {service.get('product', 'N/A')}")

# Énumérer tous les services d'une organisation
results = api.search('org:"Target Corp"', limit=1000)
services = {}
for r in results['matches']:
    port = r['port']
    services[port] = services.get(port, 0) + 1

for port, count in sorted(services.items(), key=lambda x: -x[1]):
    print(f"Port {port}: {count} instances")
```

## Cas d'usage en pentest

```bash
# 1. Cartographier la surface d'attaque externe avant un pentest
shodan search "org:\"Client Corp\"" --fields ip_str,port,product,version,os

# 2. Trouver des services avec des versions vulnérables
shodan search "product:apache version:2.4.49"   # CVE-2021-41773 (Path Traversal)
shodan search "product:log4j"                   # Log4Shell

# 3. Trouver des secrets dans les bannières HTTP
shodan search "http.html:\"api_key\" org:\"Target\""

# 4. Identifier des sous-domaines via les certificats SSL
# (équivalent passif de certificate transparency)
shodan search "ssl.cert.subject.cn:*.target.com" --fields ssl.cert.subject.cn

# 5. Trouver des services cloud non protégés
shodan search "org:Amazon port:9200"  # ElasticSearch ouvert sur AWS

# 6. Pivot depuis une IP vers l'organisation
# Trouver l'ASN d'une IP
shodan host 93.184.216.34 | grep asn
# → AS15133
# Scanner tout l'ASN
shodan search "asn:AS15133"
```

## Shodan Dorks populaires

```
# Bases de données exposées
port:6379 → Redis
port:27017 → MongoDB
port:5432 → PostgreSQL
port:3306 → MySQL
port:9200 → Elasticsearch
port:8086 → InfluxDB (souvent sans auth)
port:7474 → Neo4j

# Panels d'admin
http.title:"phpMyAdmin"
http.title:"Adminer"
http.title:"Webmin"
http.title:"cPanel"
http.title:"WHM"

# CI/CD exposés
http.title:"Jenkins"
http.title:"GitLab"
http.title:"Bamboo"
http.title:"TeamCity"

# Routeurs / switches / IoT
http.title:"RouterOS"  → Mikrotik
product:"D-Link"
http.title:"ZyXEL"

# Credentials dans les fichiers .env
http.html:"DB_PASSWORD" port:80
http.html:"AWS_SECRET_ACCESS_KEY"
```

## Alternatives à Shodan

| Outil | Points forts | URL |
|---|---|---|
| Censys | Analyse de certificats TLS très complète | censys.io |
| FOFA | Fort sur les réseaux chinois, gratuit avec compte | fofa.info |
| ZoomEye | Focus Chine, API gratuite | zoomeye.org |
| GreyNoise | Contexte sur les IPs (scanner, bénin, malveillant) | greynoise.io |
| BinaryEdge | API riche, scan historique | binaryedge.io |
| Netlas | Alternatif récent, bonne couverture | netlas.io |
