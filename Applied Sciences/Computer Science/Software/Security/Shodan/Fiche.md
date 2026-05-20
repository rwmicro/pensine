---
title: "Shodan — moteur de recherche pour objets connectés"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Shodan"
tags: [sciences-appliquées, informatique, sécurité, osint, shodan]
date: "2025-01-15"
---

# Shodan — moteur de recherche pour objets connectés

Shodan (`shodan.io`) est un moteur de recherche qui indexe non pas des pages web, mais des **dispositifs connectés à Internet** : serveurs, routeurs, caméras IP, imprimantes, systèmes industriels (SCADA/ICS), bases de données exposées. Lancé en 2009 par John Matherly, il scanne en continu l'ensemble de l'espace IPv4 sur les ports connus et récupère les **bannières** renvoyées par les services.

## Fonctionnement

Shodan opère comme un crawler de couche transport :

1. Il envoie des requêtes sur des ports (21, 22, 23, 80, 443, 502, 8080, etc.) à chaque IP publique
2. Il capture la réponse brute du service (bannière SSH, en-têtes HTTP, réponse Modbus)
3. Il enrichit avec des métadonnées (géolocalisation, ASN, organisation, certificat TLS)
4. Il indexe le tout pour la recherche

Le résultat : un inventaire mondial interrogeable des services exposés.

## Syntaxe de recherche

### Filtres courants

| Filtre | Usage | Exemple |
|---|---|---|
| `port:` | Port ouvert | `port:22` |
| `country:` | Pays (code ISO) | `country:FR` |
| `city:` | Ville | `city:"Paris"` |
| `org:` | Organisation / FAI | `org:"OVH SAS"` |
| `hostname:` | Nom d'hôte | `hostname:gouv.fr` |
| `net:` | Plage CIDR | `net:185.15.0.0/16` |
| `os:` | Système d'exploitation | `os:"Windows Server 2012"` |
| `product:` | Logiciel identifié | `product:nginx` |
| `version:` | Version précise | `product:Apache version:2.4.49` |
| `ssl.cert.subject.cn:` | CN du certificat | `ssl.cert.subject.cn:example.com` |
| `http.title:` | Titre HTML | `http.title:"Index of /"` |
| `vuln:` | CVE identifiée | `vuln:CVE-2021-44228` (compte académique/entreprise) |
| `has_screenshot:true` | Dispositifs à capture d'écran | caméras, VNC, RDP |

Les filtres se combinent : `port:3389 country:FR has_screenshot:true`.

### Dorks courants

```
# Caméras IP avec flux accessible
webcamxp country:FR

# Interfaces industrielles Modbus (SCADA)
port:502

# Bases de données MongoDB sans authentification
product:MongoDB "MongoDB Server Information" -authentication

# Serveurs Redis exposés sans mot de passe
port:6379 -authentication

# RDP exposés sur Internet
port:3389 has_screenshot:true

# Instances Jenkins publiques
http.title:"Dashboard [Jenkins]"

# Elasticsearch sans authentification
port:9200 json
```

## Usages légitimes

- **Audit d'exposition** : découvrir ce qui, dans le périmètre de son organisation, est visible depuis Internet (*attack surface management*)
- **Inventaire continu** : détecter un shadow IT, un service oublié, une config qui change
- **Threat intelligence** : identifier l'infrastructure d'un acteur malveillant (serveurs C2, panels)
- **Recherche académique** : études sur la prévalence de CVE, l'état du déploiement TLS, la durée de vie des vulnérabilités

## Cadre légal

Interroger Shodan est légal — les bannières sont des informations publiques. En revanche, **exploiter une vulnérabilité trouvée via Shodan** sans autorisation du propriétaire est une infraction (articles 323-1 et suivants du Code pénal français, Computer Fraud and Abuse Act aux États-Unis).

Règle pratique : chercher sans se connecter, puis contacter le propriétaire pour signaler (*responsible disclosure*), ne jamais tester sans mandat écrit.

## Alternatives et complémentaires

| Outil | Spécificité |
|---|---|
| **Censys** (`censys.io`) | Concurrent direct, données plus structurées, bon pour les certificats TLS |
| **ZoomEye** | Équivalent chinois |
| **FOFA** | Autre moteur chinois, très utilisé en CTI sur APT asiatiques |
| **BinaryEdge** | Scans plus fréquents, bon sur les ports exotiques |
| **GreyNoise** | Inverse de Shodan : qui scanne *vous* depuis Internet (bruit de fond vs ciblé) |
| **Hunter.how** | Alternative émergente |

## API et CLI

Shodan propose une CLI (`pip install shodan`) et une API REST. Exemples :

```bash
shodan init <API_KEY>
shodan search 'port:22 country:FR' --fields ip_str,port,org
shodan host 8.8.8.8
shodan stats --facets country 'product:nginx'
```

L'API est limitée par le niveau d'abonnement (crédits de recherche, accès aux filtres avancés comme `vuln:`).
