---
title: "Monitoring, Logging et Bonnes Pratiques"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2026-02-22"
---

# Monitoring, Logging et Bonnes Pratiques

## Monitoring et Logging

### Syslog

Syslog est un protocole standard pour la journalisation des événements réseau. Les équipements réseau envoient leurs logs vers un serveur Syslog centralisé.

**Niveaux de sévérité** (0 = le plus critique) :

| Niveau | Nom | Description |
|--------|-----|-------------|
| 0 | Emergency | Le système est inutilisable |
| 1 | Alert | Action immédiate requise |
| 2 | Critical | Condition critique |
| 3 | Error | Condition d'erreur |
| 4 | Warning | Condition d'avertissement |
| 5 | Notice | Condition normale mais significative |
| 6 | Informational | Message informatif |
| 7 | Debug | Messages de débogage |

**Configuration Syslog Cisco** :
```cisco
! Configurer le serveur Syslog
Router(config)#logging host 192.168.1.100

! Définir le niveau de logging
Router(config)#logging trap informational

! Activer les timestamps dans les logs
Router(config)#service timestamps log datetime msec

! Vérification
Router#show logging
```

### SNMP (Simple Network Management Protocol)

SNMP permet de surveiller et gérer les équipements réseau depuis une console centralisée.

**Architecture SNMP** :

| Composant | Rôle |
|-----------|------|
| SNMP Manager | Logiciel de supervision installé sur la station d'administration |
| SNMP Agent | Logiciel s'exécutant sur l'équipement surveillé |
| MIB (Management Information Base) | Base de données des objets surveillables |

**Types de messages SNMP** :

| Message | Direction | Rôle |
|---------|-----------|------|
| GET | Manager → Agent | Demander la valeur d'un objet MIB |
| GET-NEXT | Manager → Agent | Demander l'objet MIB suivant |
| GET-RESPONSE | Agent → Manager | Répondre à un GET |
| SET | Manager → Agent | Modifier la valeur d'un objet MIB |
| TRAP | Agent → Manager | Notification spontanée d'un événement |

**Configuration SNMP Cisco** :
```cisco
! SNMPv2c (community string)
Router(config)#snmp-server community PUBLIC ro
Router(config)#snmp-server community PRIVATE rw
Router(config)#snmp-server host 192.168.1.100 version 2c PUBLIC

! SNMPv3 (recommandé — authentification + chiffrement)
Router(config)#snmp-server group ADMIN v3 priv
Router(config)#snmp-server user admin ADMIN v3 auth sha MonMotDePasse priv aes 128 CleChiffrement

! Vérification
Router#show snmp
Router#show snmp community
```

### NetFlow

NetFlow est une fonctionnalité des équipements Cisco qui collecte des données sur le trafic réseau pour analyse.

Un **flux NetFlow** est un ensemble de paquets ayant les mêmes caractéristiques (source IP, destination IP, ports, protocole). Les données sont exportées vers un **collecteur NetFlow** (ex : SolarWinds, ntopng, Grafana/Prometheus).

**Configuration NetFlow Cisco** :
```cisco
! Activer NetFlow sur une interface
interface GigabitEthernet0/0
 ip flow ingress
 ip flow egress

! Configurer l'exportation vers un collecteur
Router(config)#ip flow-export destination 192.168.1.200 2055
Router(config)#ip flow-export version 9

! Vérification
Router#show ip flow interface
Router#show ip cache flow
```

### SIEM (Security Information and Event Management)

- Centralisation des logs Syslog, SNMP traps, NetFlow
- Corrélation d'événements entre sources multiples
- Alerting en temps réel
- Exemples : Splunk, ELK Stack (Elasticsearch/Logstash/Kibana), IBM QRadar

## Best Practices

### Network Hardening

1. **Segmentation**
   - VLANs
   - Separate networks
   - DMZ

2. **Access Control**
   - Least privilege
   - Authentication
   - Authorization

3. **Encryption**
   - TLS/SSL
   - VPN
   - WPA2/WPA3

4. **Monitoring**
   - Logging
   - IDS/IPS
   - Traffic analysis

5. **Updates**
   - Firmware
   - Security patches
   - Regular audits

### Security Policies

- Acceptable Use Policy
- Password policy
- Incident response plan
- Change management
- Backup policy
