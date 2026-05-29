---
title: "Shodan — moteur de recherche pour objets connectés"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > OSINT"
tags: [sciences-appliquées, informatique, sécurité, osint, reconnaissance, attack-surface, shodan]
date: "2026-05-29"
---

# Shodan — moteur de recherche pour objets connectés

Shodan (`shodan.io`) est un moteur de recherche qui indexe non pas des pages web, mais des **dispositifs connectés à Internet** : serveurs, routeurs, caméras IP, imprimantes, systèmes industriels (SCADA/ICS), bases de données exposées. Lancé en 2009 par John Matherly, il scanne en continu l'ensemble de l'espace IPv4 sur les ports connus et récupère les **bannières** renvoyées par les services. C'est l'outil de référence pour la cartographie de la surface d'attaque.

## Fonctionnement

Shodan opère comme un crawler de couche transport :

1. Il envoie des requêtes sur des ports communs (21, 22, 23, 80, 443, 502, 8080, etc.) à chaque IP publique.
2. Il capture la réponse brute du service (bannière SSH, en-têtes HTTP, réponse Modbus).
3. Il enrichit avec des métadonnées (géolocalisation, ASN, organisation, certificat TLS, OS, vulnérabilités connues).
4. Il indexe le tout pour la recherche.

Le résultat : un inventaire mondial interrogeable des services exposés. Contrairement à Google qui indexe le **contenu** web, Shodan indexe les **bannières et métadonnées** des services.

## Syntaxe de recherche

### Filtres courants

| Filtre | Usage | Exemple |
|---|---|---|
| `ip:` | IP spécifique | `ip:93.184.216.34` |
| `net:` | Plage CIDR | `net:185.15.0.0/16` |
| `port:` | Port ouvert | `port:22` |
| `hostname:` | Nom d'hôte | `hostname:gouv.fr` |
| `country:` | Pays (code ISO) | `country:FR` |
| `city:` | Ville | `city:"Paris"` |
| `geo:` | Coordonnées lat,lon,rayon | `geo:48.85,2.35,50` |
| `org:` | Organisation / FAI | `org:"OVH SAS"` |
| `isp:` | Fournisseur Internet | `isp:"Orange"` |
| `asn:` | Autonomous System Number | `asn:AS15133` |
| `os:` | Système d'exploitation | `os:"Windows Server 2012"` |
| `product:` | Logiciel identifié | `product:nginx` |
| `version:` | Version précise | `product:Apache version:2.4.49` |
| `http.title:` | Titre HTML | `http.title:"Index of /"` |
| `http.html:` | Contenu HTML | `http.html:"powered by"` |
| `http.status:` | Code HTTP | `http.status:200` |
| `ssl:` | Certificat TLS contenant un domaine | `ssl:"target.com"` |
| `ssl.cert.subject.cn:` | CN du certificat | `ssl.cert.subject.cn:*.target.com` |
| `ssl.cert.expired:` | Certificats expirés | `ssl.cert.expired:true` |
| `has_screenshot:true` | Services avec capture (caméras, VNC, RDP) | `port:3389 has_screenshot:true` |
| `vuln:` | CVE identifiée (compte académique/entreprise) | `vuln:CVE-2021-44228` |

Les filtres se combinent : `port:3389 country:FR has_screenshot:true`.

### Dorks courants

```
# Caméras IP avec flux accessible
webcamxp country:FR
title:"Live View / - MOBOTIX"

# Systèmes industriels (ICS/SCADA)
port:502                          # Modbus
port:102 product:siemens          # Siemens S7
port:20000 DNP3                   # électricité
port:47808                        # BACnet (domotique)
product:"Schneider Electric"

# Bases de données exposées sans authentification
product:MongoDB "MongoDB Server Information" -authentication   # 27017
port:6379 -authentication         # Redis
port:9200 json                    # Elasticsearch
port:5432                         # PostgreSQL
port:3306 "mysql"                 # MySQL
port:5984 "couchdb"               # CouchDB

# Panels / dashboards
http.title:"Dashboard [Jenkins]"
http.title:"Kibana" port:5601
http.title:"Grafana"
http.title:"phpMyAdmin"
http.title:"Webmin"
"Docker-Distribution-Api-Version" port:2375
port:10250 "kubelet"              # Kubernetes

# Services mal configurés
port:21 "230 Login successful"    # FTP anonyme
"authentication disabled" port:5900,5901   # VNC sans mot de passe
port:3389 "Remote Desktop"        # RDP ouvert
port:23 -login -password          # Telnet

# VPN et accès distants
product:fortinet port:443
port:4443 product:"Pulse Secure"
port:8443 product:"Cisco AnyConnect"

# Secrets dans les bannières HTTP
http.html:"DB_PASSWORD" port:80
http.html:"AWS_SECRET_ACCESS_KEY"
```

## CLI et API

### Installation et configuration

```bash
pip install shodan
shodan init <API_KEY>
shodan info                                   # crédits restants de son compte
```

### Commandes CLI

```bash
# Recherche
shodan search "apache"
shodan search --fields ip_str,port,org,os "nginx 1.14"
shodan search "org:\"Target Corp\"" --fields ip_str,port,product,version,os

# Info / pivot sur une IP
shodan host 8.8.8.8
shodan host 93.184.216.34 | grep asn          # récupérer l'ASN → pivot

# Compter et statistiques (facets)
shodan count "nginx country:FR"
shodan stats --facets country,org "nginx"

# Télécharger et parser les résultats
shodan download results.json.gz "port:22"
shodan parse results.json.gz --fields ip_str,port,hostnames

# Alert / Monitor — surveiller une plage IP (notif si nouveau service)
shodan alert create "Target Monitoring" 93.184.216.0/24
shodan alert list

# Scan actif d'une IP (payant — consomme des crédits)
shodan scan submit --filename result.json 93.184.216.34
```

### Python API

```python
import shodan

api = shodan.Shodan("API_KEY")

# Recherche
results = api.search('org:"Target Corp" port:443')
print(f"Résultats : {results['total']}")
for r in results['matches']:
    print(r['ip_str'], r['port'], r.get('product', 'N/A'))

# Info détaillée sur une IP
host = api.host("8.8.8.8")
print(host['hostnames'], host['ports'])
for service in host['data']:
    print(f"Port {service['port']}: {service.get('product', 'N/A')}")

# Streaming temps réel
for banner in api.stream.ports([80, 443]):
    print(banner)
```

## Cas d'usage

### Sécurité défensive (attack surface management)

- **Asset discovery** : trouver les assets de son organisation, le shadow IT, les services oubliés et les mauvaises configs.
- **Inventaire continu** : détecter un service qui change, via Shodan Monitor (alertes sur nouveaux ports, nouvelle vulnérabilité, certificat expiré).
- **Vulnerability management** : `org:"YourCompany" vuln:CVE-2021-44228`.

### Red team / pentest

```bash
# 1. Cartographier la surface d'attaque externe avant l'engagement
shodan search "org:\"Client Corp\"" --fields ip_str,port,product,version,os

# 2. Trouver des versions vulnérables connues
shodan search "product:apache version:2.4.49"   # CVE-2021-41773 (path traversal)
shodan search "product:log4j"                    # Log4Shell

# 3. Énumérer des sous-domaines via les certificats (CT passif)
shodan search "ssl.cert.subject.cn:*.target.com" --fields ssl.cert.subject.cn

# 4. Pivot IP → ASN → toute l'infra
shodan host 93.184.216.34 | grep asn   # → AS15133
shodan search "asn:AS15133"
```

### Threat intelligence

Identifier l'infrastructure malveillante : serveurs C2, panels de phishing, devices infectés par un botnet IoT (Mirai). Voir aussi `[[Threat Intelligence]]`.

### Recherche

Études sur la prévalence de CVE, l'état du déploiement TLS, la durée de vie des vulnérabilités. Shodan Maps (visualisation géographique) et Shodan Images (screenshots des services web) complètent l'analyse.

## Cadre légal

Interroger Shodan est **légal** — les bannières sont des informations publiques, et le scan est passif. En revanche, **exploiter une vulnérabilité trouvée via Shodan** sans autorisation du propriétaire est une infraction (articles 323-1 et suivants du Code pénal français, Computer Fraud and Abuse Act aux États-Unis).

Règle pratique : chercher sans se connecter, puis contacter le propriétaire pour signaler (*responsible disclosure*), ne jamais tester sans mandat écrit.

### Se protéger de Shodan (côté organisation)

- **Firewall / segmentation** : fermer les ports inutiles, whitelist d'IPs, DMZ pour les services publics, VLANs pour isoler le critique.
- **Masquer les bannières** : `server_tokens off;` (nginx), `ServerTokens Prod` + `ServerSignature Off` (Apache).
- **Authentification** : toujours activée, mots de passe forts, MFA, IP whitelisting.
- **Surveillance** : recherches Shodan régulières sur son propre périmètre + Shodan Monitor.
- **Opt-out** : possible mais nécessite de prouver le contrôle du domaine (robots.txt ne suffit pas).

## Plans et tarifs

| Niveau | Contenu |
|---|---|
| Free | 1 crédit de recherche/mois, résultats et API limités |
| Membership (~59 $/mois) | 100 crédits, pas de CAPTCHA, plus de résultats |
| Corporate / Academic | crédits étendus/illimités, filtre `vuln:`, API étendue, support |

## Alternatives et complémentaires

| Outil | Spécificité |
|---|---|
| **Censys** (`censys.io`) | Concurrent direct, données structurées, excellent sur les certificats TLS |
| **ZoomEye** | Équivalent chinois, API gratuite |
| **FOFA** (`fofa.info`) | Moteur chinois, très utilisé en CTI sur les APT asiatiques |
| **BinaryEdge** | Scans fréquents, bon sur les ports exotiques, scan historique |
| **GreyNoise** (`greynoise.io`) | Inverse de Shodan : qui *vous* scanne depuis Internet (bruit de fond vs ciblé) |
| **Netlas** (`netlas.io`) | Alternative récente, bonne couverture |

## Ressources

- [Shodan.io](https://www.shodan.io) · [CLI](https://cli.shodan.io) · [API docs](https://developer.shodan.io)
- Awesome Shodan Queries (GitHub)

## Sujets à approfondir

- [ ] Shodan Honeyscore (détection de honeypots)
- [ ] Intégration avec un SIEM
- [ ] Threat hunting automatisé via l'API
