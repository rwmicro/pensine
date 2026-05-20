---
title: "Gestion des Logs"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc]
date: "2025-02-15"
---

# Gestion des Logs

La journalisation (logging) est le fondement de tout dispositif de surveillance en sécurité. Sans logs centralisés, de qualité et bien conservés, il est impossible de détecter les intrusions, d'investiguer les incidents ou de démontrer la conformité réglementaire.

## Pourquoi journaliser

| Objectif | Exemple |
|----------|---------|
| Sécurité | Détecter une tentative d'intrusion, retracer un attaquant |
| Opérationnel | Diagnostiquer une panne, analyser les performances |
| Légal/Conformité | ISO 27001, RGPD, PCI DSS, HIPAA, GDPR imposent la traçabilité |
| Debug | Comprendre le comportement d'une application |
| Forensics | Reconstruire la timeline d'un incident |

## Types de logs

| Type | Contenu | Exemples |
|------|---------|---------|
| Logs système | Kernel, boot, hardware | `/var/log/syslog`, Windows Event Log System |
| Logs d'authentification | Logins, sudo, SSH | `/var/log/auth.log`, Event ID 4624/4625 |
| Logs applicatifs | Erreurs, warnings, infos | Logs applicatifs custom |
| Logs web | Requêtes HTTP, codes de retour | Nginx/Apache access.log |
| Logs réseau | Trafic, connexions | Firewall, netflow, proxy |
| Logs base de données | Requêtes, modifications | MySQL slow.log, audit.log |
| Logs sécurité | Alertes IDS, EDR, AV | Snort alerts, Sysmon |
| Logs cloud | Actions API, IAM | CloudTrail (AWS), Azure Monitor |
| Audit logs | Actions administratives | AD audit, sudo logs |

## Sources critiques pour la sécurité

### Windows

**Event Log** — accessible via `eventvwr.msc` ou PowerShell :

```powershell
# Lire les derniers événements de sécurité
Get-WinEvent -LogName Security -MaxEvents 100

# Filtrer par Event ID
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 50

# Exporter en XML
Get-WinEvent -LogName Security | Export-Clixml events.xml
```

**Event IDs Windows critiques :**

| Event ID | Description | Canal |
|----------|-------------|-------|
| 4624 | Logon réussi | Security |
| 4625 | Logon échoué | Security |
| 4648 | Logon avec credentials explicites | Security |
| 4672 | Privilèges spéciaux assignés | Security |
| 4688 | Création de processus | Security |
| 4698 | Tâche planifiée créée | Security |
| 4720 | Compte utilisateur créé | Security |
| 4728/4732/4756 | Membre ajouté groupe (domain/local/universal) | Security |
| 4768 | Demande ticket Kerberos AS-REQ | Security |
| 4769 | Demande service ticket TGS-REQ | Security |
| 4771 | Échec Kerberos pre-auth | Security |
| 7045 | Nouveau service installé | System |
| 1102 | Journal d'audit effacé | Security |
| 4104 | PowerShell script block logging | PowerShell |
| 4103 | PowerShell module logging | PowerShell |

**Sysmon** (Microsoft Sysinternals) — journalisation enrichie :

```xml
<!-- Extrait sysmon config -->
<Sysmon schemaversion="4.90">
  <EventFiltering>
    <ProcessCreate onmatch="include">
      <CommandLine condition="contains">powershell</CommandLine>
    </ProcessCreate>
    <NetworkConnect onmatch="include">
      <DestinationPort condition="is">443</DestinationPort>
    </NetworkConnect>
  </EventFiltering>
</Sysmon>
```

```powershell
# Installer Sysmon avec config
.\Sysmon64.exe -i sysmonconfig.xml -accepteula
```

### Linux

**Chemins des logs :**

```
Authentification :
/var/log/auth.log       (Debian/Ubuntu)
/var/log/secure         (RHEL/CentOS)

Système :
/var/log/syslog         (Debian/Ubuntu)
/var/log/messages       (RHEL/CentOS)

Kernel :
/var/log/kern.log
dmesg

Web :
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/apache2/access.log
/var/log/apache2/error.log

Bases de données :
/var/log/mysql/error.log
/var/log/postgresql/postgresql-*.log

Sessions :
/var/log/wtmp    (historique logins - last)
/var/log/btmp    (logins échoués - lastb)
/var/log/lastlog (dernier login par user)
```

**Journald (systemd) :**

```bash
# Tous les logs
journalctl

# Depuis les 24 dernières heures
journalctl --since "24 hours ago"

# Par service
journalctl -u nginx.service

# Follow (temps réel)
journalctl -f

# Niveau d'urgence
journalctl -p err   # Erreurs seulement

# Exporter en JSON
journalctl -o json | head -10
```

**Audit Linux (auditd) :**

```bash
# Installer
sudo apt install auditd

# Règles d'audit (surveiller /etc/shadow)
sudo auditctl -w /etc/shadow -p rwxa -k shadow_access

# Surveiller les exécutions de binaires
sudo auditctl -a always,exit -F arch=b64 -S execve -k exec_commands

# Voir les logs
sudo ausearch -k shadow_access
sudo aureport --summary
```

### Logs réseau

**Format Apache Combined Log :**
```
127.0.0.1 - frank [10/Oct/2023:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://example.com/" "Mozilla/5.0"
   │         │      │                              │                          │   │
   IP        user   timestamp                     request                   code  bytes
```

**Firewall logs (iptables) :**
```
Feb 15 12:34:56 hostname kernel: [12345.678901] IN=eth0 OUT= MAC=... SRC=1.2.3.4 DST=5.6.7.8 LEN=40 PROTO=TCP SPT=4321 DPT=22 WINDOW=0 RES=0x00 ACK RST URGP=0
```

**NetFlow / IPFIX :**
Résumé des flux réseau (pas le contenu) : IP source, IP destination, port, protocole, bytes, paquets, durée.

## Pipeline de traitement des logs

```
Sources (serveurs, apps, réseau)
        ↓
Collection (Forwarder/Agent)
        ↓
Transport (Syslog, Kafka, Beats)
        ↓
Parsing & Normalisation
        ↓
Enrichissement (GeoIP, Threat Intel, CMDB)
        ↓
Indexation (SIEM, Elasticsearch)
        ↓
Corrélation & Alertes
        ↓
Visualisation & Reporting
```

### Parsing et normalisation

Objectif : transformer des logs hétérogènes en un format structuré commun.

**Exemples de parsing avec Logstash :**

```
# Filter pour logs Apache
filter {
  if [type] == "apache" {
    grok {
      match => {
        "message" => '%{IPORHOST:clientip} %{USER:ident} %{USER:auth} \[%{HTTPDATE:timestamp}\] "%{WORD:verb} %{DATA:request} HTTP/%{NUMBER:httpversion}" %{NUMBER:response:int} (?:%{NUMBER:bytes:int}|-)'
      }
    }
    date {
      match => ["timestamp", "dd/MMM/yyyy:HH:mm:ss Z"]
    }
    geoip {
      source => "clientip"
    }
  }
}
```

**ECS (Elastic Common Schema) :**

Format standardisé pour les logs dans Elasticsearch :

```json
{
  "@timestamp": "2024-01-15T10:30:00.000Z",
  "event": {
    "category": "authentication",
    "type": "start",
    "outcome": "failure"
  },
  "source": {
    "ip": "1.2.3.4",
    "geo": {
      "country_iso_code": "CN"
    }
  },
  "user": {
    "name": "admin"
  },
  "host": {
    "name": "webserver01"
  }
}
```

### Enrichissement

Ajouter du contexte aux événements bruts :

| Enrichissement | Source | Valeur ajoutée |
|---------------|--------|----------------|
| GeoIP | MaxMind GeoLite2 | Pays, ville, ASN d'une IP |
| Threat Intel | MISP, OTX, VirusTotal | IP/domaine malveillant connu |
| CMDB | ServiceNow, Netbox | Propriétaire machine, criticité |
| LDAP/AD | Active Directory | Département, manager du compte |
| DNS reverse | Internal DNS | Nom de machine depuis IP |
| Vulnérabilités | Nessus, Qualys | Failles connues sur l'hôte |

## Conservation des logs

### Politique de rétention

| Tier | Période | Accessibilité | Coût |
|------|---------|---------------|------|
| Hot (actif) | 3-6 mois | Temps réel, requêtes rapides | Élevé |
| Warm | 6 mois - 2 ans | Accessible, moins rapide | Moyen |
| Cold (archive) | 2-7 ans | Restauration nécessaire | Faible |

**Durées légales / réglementaires :**

| Réglementation | Durée minimale |
|---------------|----------------|
| RGPD (données personnelles) | Selon finalité (limitée) |
| PCI DSS | 12 mois (3 mois accessible immédiatement) |
| ISO 27001 | Selon politique interne (souvent 12-24 mois) |
| NIS2 (Europe) | Non spécifié explicitement |
| SOX (USA) | 7 ans pour les financiers |

### Logrotate (Linux)

```bash
# /etc/logrotate.d/nginx
/var/log/nginx/*.log {
    daily           # Rotation quotidienne
    rotate 30       # Garder 30 fichiers
    compress        # Compresser avec gzip
    delaycompress   # Ne pas comprimer le dernier
    missingok       # Pas d'erreur si fichier absent
    notifempty      # Ne pas tourner si vide
    sharedscripts
    postrotate
        nginx -s reopen   # Signal Nginx pour nouveau fichier
    endscript
}
```

### Intégrité des logs

Les logs peuvent être manipulés par un attaquant pour effacer ses traces :

```bash
# Vérifier que le journal n'a pas été effacé (Windows Event 1102)
Get-WinEvent -LogName Security | Where-Object {$_.Id -eq 1102}

# Logs immutables avec journald
sudo journalctl --verify

# Stocker les logs sur un serveur distant isolé (le plus tôt possible)
# Utiliser du write-once storage (S3 Object Lock, WORM)

# Signer les logs avec HMAC
# Forward immédiatement vers un SIEM hors de portée de l'attaquant
```

## Collecte et transport

### Agents courants

| Agent | SIEM compatible | Protocole |
|-------|----------------|-----------|
| Filebeat (Elastic) | Elasticsearch, Logstash | TCP/UDP, HTTP |
| Winlogbeat | Elasticsearch | HTTP |
| Fluentd / Fluent Bit | Tous | TCP, UDP, HTTP |
| Splunk Universal Forwarder | Splunk | TCP (splunkd protocol) |
| NXLog | Tout | Syslog, HTTP, file |
| Vector | Tout | Multi-protocol |

### Syslog

Protocole standard (RFC 5424, port UDP/TCP 514) :

```
Format : <PRIORITY>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG
Exemple : <34>1 2024-01-15T10:30:00Z server01 nginx 1234 - - "GET / HTTP/1.1" 200
```

**Niveaux de sévérité syslog :**

| Valeur | Niveau | Description |
|--------|--------|-------------|
| 0 | Emergency | Système inutilisable |
| 1 | Alert | Action immédiate requise |
| 2 | Critical | Condition critique |
| 3 | Error | Erreur |
| 4 | Warning | Avertissement |
| 5 | Notice | Condition normale mais notable |
| 6 | Informational | Message informatif |
| 7 | Debug | Debug |

```bash
# Configurer rsyslog pour forwarder vers SIEM
# /etc/rsyslog.conf
*.* @192.168.1.100:514    # UDP
*.* @@192.168.1.100:514   # TCP (double @)

# Avec TLS (syslog-ng)
# Recommandé pour éviter l'interception
```

## Analyse des logs

### Techniques d'analyse manuelle

```bash
# Compter les tentatives de connexion par IP
grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn | head 10

# Voir tous les accès sudo
grep "sudo" /var/log/auth.log | grep -v "pam_unix"

# Requêtes HTTP 500
awk '$9 == 500' /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn

# Grandes requêtes (potentiel exfil upload)
awk '$10 > 10000000' /var/log/nginx/access.log | awk '{print $1, $7, $10}'

# Connexions SSH actives
last | head -20
```

### Corrélation temporelle

Lors d'un incident, établir une timeline précise :

```bash
# log2timeline (plaso) pour timeline forensics
log2timeline.py plaso.dump /dev/sda1

# Analyser avec psort
psort.py -z UTC plaso.dump "date > '2024-01-15 09:00:00' and date < '2024-01-15 11:00:00'" > timeline.csv
```

## Questions à se poser lors d'un audit logging

1. Qu'est-ce qu'on logue ? (périmètre des sources)
2. Pour quelle finalité ? (sécurité, ops, compliance)
3. Quel niveau de détail ? (verbosité, champs collectés)
4. Combien de temps ? (politique de rétention)
5. Comment on stocke ? (cold/warm/hot, immutabilité)
6. Comment on protège les logs ? (chiffrement, accès restreint)
7. Comment on analyse ? (outils, processus, équipe)
8. A-t-on les ressources ? (storage, bandwidth, personnel)
9. Respecte-t-on les contraintes légales ? (RGPD, données personnelles dans les logs)
