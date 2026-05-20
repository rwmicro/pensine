---
title: SNMP
domain: sciences-appliquées
subdomain: informatique / sécurité / réseau
tags: [snmp, réseau, énumération, community-string, sécurité, pentest]
date: 2026-03-22
---

# SNMP

SNMP (Simple Network Management Protocol) est utilisé pour surveiller et gérer des équipements réseau (routeurs, switches, imprimantes, serveurs). Ses versions v1 et v2c utilisent des "community strings" en clair, souvent laissées à leurs valeurs par défaut, ce qui en fait un vecteur d'énumération important.

## Versions et sécurité

| Version | Auth | Chiffrement | Problème |
|---|---|---|---|
| SNMPv1 | Community string | Aucun | Community en clair, broadcast possible |
| SNMPv2c | Community string | Aucun | Idem v1, datagramme plus efficace |
| SNMPv3 | User/password | DES ou AES | Sécurisé si bien configuré |

```
Community strings par défaut (à tester impérativement) :
  public   → lecture (très courant)
  private  → écriture (dangereux si accessible)
  community, manager, monitor, admin, ...
```

## Ports et protocoles

```
UDP 161 — agents SNMP (requêtes Get/Set)
UDP 162 — traps SNMP (notifications envoyées par l'équipement)
TCP 161/162 — SNMP over TCP (rare)
```

## Énumération

```bash
# snmpwalk — parcourir l'arbre MIB complet
snmpwalk -v2c -c public 192.168.1.1
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1  # Sous-arbre MIB-II

# Branches MIB importantes
# 1.3.6.1.2.1.1      → sysDescr, sysName, sysContact, sysLocation
# 1.3.6.1.2.1.4.34   → Table de routage IP
# 1.3.6.1.2.1.6.13   → Connexions TCP actives
# 1.3.6.1.2.1.25.1   → Informations système (OS, temps de marche)
# 1.3.6.1.2.1.25.4.2 → Processus en cours
# 1.3.6.1.2.1.25.6.3 → Logiciels installés

# Extraire des OIDs spécifiques
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.1.0   # sysDescr
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.5.0   # sysName

# Informations système Windows
snmpwalk -v2c -c public 192.168.1.10 1.3.6.1.2.1.25.4.2  # Processus
snmpwalk -v2c -c public 192.168.1.10 1.3.6.1.2.1.25.6.3  # Logiciels installés
snmpwalk -v2c -c public 192.168.1.10 1.3.6.1.4.1.77.1.2.25  # Utilisateurs (Windows)
snmpwalk -v2c -c public 192.168.1.10 1.3.6.1.4.1.77.1.2.3   # Partages réseau

# Connexions TCP actives
snmpwalk -v2c -c public 192.168.1.10 1.3.6.1.2.1.6.13
```

### Brute-force des community strings

```bash
# onesixtyone — scanner SNMP rapide
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt 192.168.1.0/24
onesixtyone -i ips.txt -c community_strings.txt

# nmap — script SNMP
nmap -sU -p 161 --script snmp-brute 192.168.1.0/24
nmap -sU -p 161 --script snmp-info 192.168.1.1
nmap -sU -p 161 --script snmp-sysdescr 192.168.1.1

# hydra
hydra -P /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt \
    snmp://192.168.1.1

# metasploit
msf6 > use auxiliary/scanner/snmp/snmp_login
msf6 > set RHOSTS 192.168.1.0/24
msf6 > run
```

### snmp-check — sortie lisible

```bash
# snmp-check — output formaté pour les humains
snmp-check 192.168.1.10 -c public
# → Système, utilisateurs, processus, services, interfaces réseau, partages, ...

# Extraction automatique des informations utiles
snmp-check 192.168.1.10 -c public | grep -E "user|password|share|process"
```

## Informations extractibles

```bash
# Utilisateurs (Windows MIB)
snmpwalk -v2c -c public 192.168.1.10 1.3.6.1.4.1.77.1.2.25

# Partages réseau
snmpwalk -v2c -c public 192.168.1.10 1.3.6.1.4.1.77.1.2.3

# Processus en cours (peut révéler des services, antivirus, etc.)
snmpwalk -v2c -c public 192.168.1.10 1.3.6.1.2.1.25.4.2

# Interfaces réseau et adresses IP
snmpwalk -v2c -c public 192.168.1.10 1.3.6.1.2.1.4.20  # IP addresses
snmpwalk -v2c -c public 192.168.1.10 1.3.6.1.2.1.2.2    # Interfaces

# Table ARP
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.4.22

# Table de routage
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.4.21

# Configuration (Cisco)
snmpwalk -v2c -c public router.company.com 1.3.6.1.4.1.9.2.1.73  # IOS config
```

## SNMP Write — modification de configuration

```bash
# Si community "private" est accessible en écriture
# Modifier un paramètre (ex: sysLocation)
snmpset -v2c -c private 192.168.1.1 1.3.6.1.2.1.1.6.0 s "Hacked"

# Cisco — modifier la config via SNMP (très dangereux si "private" accessible)
# Télécharger la config via TFTP
snmpset -v2c -c private router 1.3.6.1.4.1.9.2.1.55.0 s "router_config.txt"

# Activer/désactiver des interfaces
snmpset -v2c -c private router 1.3.6.1.2.1.2.2.1.7.1 i 2  # ifAdminStatus = down
```

## SNMPv3 — Exploitation si mal configuré

```bash
# SNMPv3 avec authentification MD5/SHA
snmpwalk -v3 -u admin -l authNoPriv -a MD5 -A "password" 192.168.1.1
snmpwalk -v3 -u admin -l authPriv -a SHA -A "authpass" -x AES -X "privpass" 192.168.1.1

# Brute-force SNMPv3
msf6 > use auxiliary/scanner/snmp/snmp_login
msf6 > set VERSION 3

# Si les credentials SNMPv3 sont connus → même accès qu'avec une community string
```

## Nmap pour SNMP

```bash
# Scripts Nmap SNMP
nmap -sU -p 161 --script snmp-brute,snmp-info,snmp-interfaces,snmp-processes,snmp-sysdescr 192.168.1.1

# Scan SNMP sur tout un réseau
nmap -sU -p 161 --open 192.168.1.0/24
```

## Contre-mesures

```
✓ Désactiver SNMP si non utilisé
✓ Utiliser SNMPv3 avec auth + chiffrement (authPriv)
✓ Changer les community strings par défaut (public/private)
✓ Utiliser des community strings longues et aléatoires
✓ Restreindre SNMP aux seuls hôtes de supervision (ACL réseau)
✓ Filtrer UDP 161/162 au niveau du firewall (accès depuis management VLAN uniquement)
✓ Community "private" (écriture) : accessible seulement depuis le serveur NMS
✓ Surveiller les requêtes SNMP anormales (volume, sources)
```
