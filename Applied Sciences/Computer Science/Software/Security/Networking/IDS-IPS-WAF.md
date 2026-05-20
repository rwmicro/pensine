---
title: "IDS, IPS et WAF"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2026-02-25"
---

# IDS, IPS et WAF

## Concepts et différences

| Système | Rôle | Position | Action |
|---|---|---|---|
| **IDS** (Intrusion Detection System) | Détecter | Hors bande (passif) | Alerte uniquement |
| **IPS** (Intrusion Prevention System) | Détecter et bloquer | En ligne (inline) | Alerte + blocage |
| **WAF** (Web Application Firewall) | Protéger les apps web | Devant les serveurs web | Filtrage HTTP/HTTPS |
| **NGFW** (Next-Gen Firewall) | Firewall + IPS + DPI | Périmètre réseau | Blocage + inspection |

Un **IDS** observe une copie du trafic (via un TAP ou un port SPAN) — il ne peut pas bloquer mais ne génère pas de latence. Un **IPS** est dans le chemin des paquets — il peut bloquer mais introduit de la latence et peut générer des faux positifs bloquants.

## Méthodes de détection

| Méthode | Principe | Avantages | Limites |
|---|---|---|---|
| Signature | Correspondance avec des patterns connus | Précis, peu de FP | Inefficace sur les 0-days |
| Anomalie (comportemental) | Déviation par rapport à la baseline | Détecte les nouveaux TTP | Taux de FP plus élevé |
| Basé sur les états | Suivi des connexions | Détecte les attaques multi-paquets | Consommation mémoire |
| Réputation | IP/domaine dans des listes noires | Simple, efficace | Dépend de la fraîcheur des listes |

## Snort

Snort est le moteur IDS/IPS open source de référence. Ses règles sont portables vers de nombreuses solutions commerciales.

### Structure d'une règle Snort

```
action proto src_ip src_port direction dst_ip dst_port (options)

alert tcp any any -> $HOME_NET 80 (msg:"Suspicious GET request"; content:"GET"; sid:1000001; rev:1;)
│      │   │    │  │  │           │
│      │   │    │  │  │           └── options
│      │   │    │  │  └── réseau destination
│      │   │    │  └── direction (-> ou <>)
│      │   │    └── port source
│      │   └── IP source
│      └── protocole
└── action
```

**Actions** : `alert` (logguer et alerter), `drop` (bloquer et logguer), `reject` (bloquer + envoyer RST), `pass` (ignorer)

### Règles Snort exemples

```
# Détecter un scan SYN (nmap -sS)
alert tcp any any -> $HOME_NET any (msg:"Possible SYN Scan"; flags:S,12; threshold:type threshold,track by_src,count 20,seconds 10; sid:1000010; rev:1;)

# Détecter une connexion vers un C2 via DNS sur un port inhabituel
alert udp $HOME_NET any -> any !53 (msg:"DNS over non-standard port"; content:"|00 00 01 00 00|"; depth:10; sid:1000011;)

# Détecter une tentative d'exploitation Log4Shell
alert http any any -> $HOME_NET any (msg:"Possible Log4Shell Exploit"; content:"${jndi:"; nocase; sid:1000020; rev:1;)

# Détecter des credentials FTP en clair
alert tcp any any -> $HOME_NET 21 (msg:"FTP Login Attempt"; content:"USER "; nocase; sid:1000030;)
alert tcp any any -> $HOME_NET 21 (msg:"FTP Password Sent"; content:"PASS "; nocase; sid:1000031;)

# Détecter Mimikatz via l'agent-string (si User-Agent est configuré)
alert http $HOME_NET any -> any any (msg:"Possible Mimikatz HTTP C2"; content:"User-Agent|3a 20|Go-http-client/1.1"; sid:1000040;)
```

### Options clés

| Option | Description | Exemple |
|---|---|---|
| `content` | Recherche de chaîne dans le payload | `content:"cmd.exe"` |
| `nocase` | Insensible à la casse | `content:"GET"; nocase;` |
| `pcre` | Expression régulière | `pcre:"/select.+from/i"` |
| `depth` | Limiter la recherche aux N premiers octets | `depth:50;` |
| `offset` | Commencer la recherche à l'octet N | `offset:4;` |
| `flags` | Flags TCP (S=SYN, A=ACK, F=FIN, R=RST) | `flags:S;` |
| `threshold` | Limiter les alertes répétées | `threshold:type limit,track by_src,count 1,seconds 60;` |
| `flow` | Direction du flux établi | `flow:established,to_server;` |
| `sid` | Identifiant unique de la règle | `sid:1000001;` |
| `rev` | Version de la règle | `rev:2;` |

### Déploiement Snort

```bash
# Installation
apt install snort

# Mode IDS (écoute passive sur eth0)
snort -A alert_fast -i eth0 -c /etc/snort/snort.conf

# Mode IPS (inline avec nfqueue)
snort -Q --daq nfq --daq-var queue=0 -c /etc/snort/snort.conf

# Test d'une règle
snort -r capture.pcap -c /etc/snort/snort.conf -A console

# Structure des fichiers
/etc/snort/snort.conf       # configuration principale
/etc/snort/rules/           # fichiers de règles (.rules)
/var/log/snort/alert        # fichier d'alertes
```

## Suricata

Suricata est l'alternative moderne à Snort : multi-thread, supporte EVE JSON (format structuré pour SIEM), compatible avec les règles Snort.

```bash
# Configuration /etc/suricata/suricata.yaml
af-packet:
  - interface: eth0
    threads: 4
    cluster-type: cluster_flow

# Lancer en IDS
suricata -c /etc/suricata/suricata.yaml -i eth0

# Lancer en IPS (avec nfqueue)
suricata -c /etc/suricata/suricata.yaml -q 0

# Tester sur une capture
suricata -c /etc/suricata/suricata.yaml -r capture.pcap

# Règles Emerging Threats (mise à jour quotidienne)
suricata-update
```

### EVE JSON (format de sortie Suricata)

```json
{
  "timestamp": "2024-01-15T10:23:00.000000+0000",
  "event_type": "alert",
  "src_ip": "192.168.1.100",
  "src_port": 54321,
  "dest_ip": "93.184.216.34",
  "dest_port": 443,
  "proto": "TCP",
  "alert": {
    "action": "allowed",
    "gid": 1,
    "signature_id": 2027865,
    "rev": 1,
    "signature": "ET MALWARE Possible Cobalt Strike Beacon",
    "category": "Malware Command and Control Activity Detected",
    "severity": 1
  },
  "http": {
    "hostname": "93.184.216.34",
    "url": "/updates",
    "user_agent": "Mozilla/5.0"
  }
}
```

```bash
# Intégrer EVE JSON dans un SIEM
# Filebeat → Elasticsearch
filebeat modules enable suricata
# /etc/filebeat/modules.d/suricata.yml :
# - module: suricata
#   eve:
#     enabled: true
#     var.paths: ["/var/log/suricata/eve.json"]
```

## WAF (Web Application Firewall)

### Modes de déploiement

```
Reverse Proxy (le plus courant) :
Client → [WAF] → Serveur Web

Inline Transparent Bridge :
Client → [WAF transparent] → Serveur Web

Out-of-Band (détection uniquement, pas de blocage) :
Client ─────────────────→ Serveur Web
         ↓ (copie)
         [WAF]
```

### ModSecurity

ModSecurity est le WAF open source le plus utilisé (module Apache/Nginx).

```nginx
# Nginx avec ModSecurity
server {
    listen 443 ssl;

    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsecurity.conf;

    location / {
        proxy_pass http://backend:8080;
    }
}
```

```apache
# Apache
LoadModule security2_module modules/mod_security2.so

<IfModule mod_security2.c>
    SecRuleEngine On
    SecRequestBodyAccess On
    SecResponseBodyAccess On

    # Mode détection uniquement (à utiliser d'abord)
    # SecRuleEngine DetectionOnly

    # OWASP CRS (Core Rule Set)
    Include /etc/modsecurity/crs/crs-setup.conf
    Include /etc/modsecurity/crs/rules/*.conf
</IfModule>
```

### OWASP ModSecurity Core Rule Set (CRS)

Le CRS est un ensemble de règles génériques contre l'OWASP Top 10.

```bash
# Installation du CRS
git clone https://github.com/coreruleset/coreruleset.git /etc/modsecurity/crs

# Niveaux de paranoia (1-4)
# 1 = peu de faux positifs, protection de base
# 4 = protection maximale, beaucoup de faux positifs

# /etc/modsecurity/crs/crs-setup.conf
SecAction "id:900000,phase:1,nolog,pass,t:none,\
    setvar:tx.paranoia_level=2"

SecAction "id:900110,phase:1,nolog,pass,t:none,\
    setvar:tx.inbound_anomaly_score_threshold=5,\
    setvar:tx.outbound_anomaly_score_threshold=4"
```

### Règles ModSecurity personnalisées

```
# Bloquer un IP spécifique
SecRule REMOTE_ADDR "@ipMatch 1.2.3.4" \
    "id:1000001,phase:1,deny,status:403,msg:'Blocked IP'"

# Détecter une tentative SQLi simple
SecRule ARGS "@contains union select" \
    "id:1000002,phase:2,deny,status:403,msg:'SQL Injection attempt',log"

# Limiter le rate (nécessite mod_ratelimit ou nginxlimit_req)
SecRule &TX:RATELIMIT_COUNTER "@gt 100" \
    "id:1000003,phase:1,deny,status:429,msg:'Rate limit exceeded'"

# Whitelist une règle qui génère des FP
SecRuleUpdateTargetById 942100 "!ARGS:description"
```

### Contournement de WAF (bypass techniques)

Connaître les contournements permet de mieux configurer les WAF :

```
SQLi bypass :
- Encodage URL : %27 = '
- Double encodage : %2527
- Commentaires SQL : SELECT/**/FROM
- Case mixing : SeLeCt FrOm
- Caractères spéciaux : /*!UNION*/ SELECT

XSS bypass :
- Encodage HTML : &lt;script&gt;
- JavaScript protocol : <a href="javascript:alert(1)">
- SVG : <svg onload="alert(1)">
- Template literals : `alert${1}`

Path traversal bypass :
- Double encoding : %252F = /
- Unicode : %c0%af = /
- Null byte : ../../../etc/passwd%00.jpg
```

## Tuning et réduction des faux positifs

```bash
# ModSecurity — identifier les règles qui génèrent des FP
grep -r "ModSecurity:" /var/log/apache2/error.log | \
    grep -oP 'id "\K[0-9]+' | sort | uniq -c | sort -rn

# Désactiver temporairement une règle pour un chemin spécifique
<LocationMatch "^/api/search">
    SecRuleRemoveById 942100  # désactiver la règle SQLi sur ce endpoint
</LocationMatch>

# Suricata — désactiver une règle par SID
suricata-update add-disablelist /etc/suricata/disable.conf
echo "2027865" >> /etc/suricata/disable.conf
suricata-update
```
