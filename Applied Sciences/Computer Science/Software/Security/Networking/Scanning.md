---
title: "Scanning (Reconnaissance Active)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2026-02-25"
---

# Scanning (Reconnaissance Active)

Le scanning est la phase de reconnaissance active : on envoie des paquets vers une cible pour cartographier son infrastructure (ports, services, versions, vulnérabilités). C'est la base de tout audit de sécurité et test d'intrusion.

## Nmap — Référence complète

### Types de scans

```bash
# SYN scan (furtif, ne complète pas le 3-way handshake) — root requis
nmap -sS 192.168.1.1

# TCP Connect scan (sans root, moins furtif)
nmap -sT 192.168.1.1

# UDP scan (lent, nécessite root)
nmap -sU 192.168.1.1

# ACK scan (détecter les règles firewall stateless)
nmap -sA 192.168.1.1

# NULL scan (pas de flags TCP — evasion basique)
nmap -sN 192.168.1.1

# FIN scan
nmap -sF 192.168.1.1

# Xmas scan (FIN+PSH+URG)
nmap -sX 192.168.1.1

# Ping scan uniquement (découverte d'hôtes)
nmap -sn 192.168.1.0/24
```

### Sélection de ports

```bash
# Ports spécifiques
nmap -p 22,80,443 192.168.1.1

# Plage de ports
nmap -p 1-1024 192.168.1.1

# Tous les ports (65535)
nmap -p- 192.168.1.1

# Top 100 ports les plus courants
nmap --top-ports 100 192.168.1.1

# Top 1000 (défaut)
nmap 192.168.1.1

# Port UDP spécifique
nmap -sU -p 161 192.168.1.1  # SNMP
```

### Détection de services et d'OS

```bash
# Version des services (banner grabbing)
nmap -sV 192.168.1.1

# Niveau de détection (0-9, défaut 7)
nmap -sV --version-intensity 9 192.168.1.1

# Détection OS
nmap -O 192.168.1.1

# Tout en un : OS + version + scripts + traceroute
nmap -A 192.168.1.1

# Verbosité
nmap -v 192.168.1.1    # verbose
nmap -vv 192.168.1.1   # très verbose
```

### Nmap Scripting Engine (NSE)

Les scripts NSE automatisent des tâches courantes d'énumération et de détection de vulnérabilités.

```bash
# Scripts par défaut (catégorie 'default')
nmap -sC 192.168.1.1

# Script spécifique
nmap --script http-title 192.168.1.1

# Catégorie de scripts
nmap --script auth 192.168.1.1         # Authentification
nmap --script vuln 192.168.1.1         # Vulnérabilités connues
nmap --script exploit 192.168.1.1      # Exploits
nmap --script discovery 192.168.1.1    # Découverte
nmap --script brute 192.168.1.1        # Brute force

# Scripts avec arguments
nmap --script http-brute --script-args http-brute.path=/admin 192.168.1.1
nmap --script smb-brute --script-args userdb=users.txt,passdb=pass.txt 192.168.1.1

# Scripts utiles par protocole
nmap --script ftp-anon -p 21 192.168.1.1           # FTP anonyme
nmap --script ssh-auth-methods -p 22 192.168.1.1   # Auth SSH disponibles
nmap --script http-methods -p 80 192.168.1.1       # Méthodes HTTP
nmap --script smb-security-mode -p 445 192.168.1.1 # Sécurité SMB
nmap --script ms-sql-info -p 1433 192.168.1.1      # SQL Server
nmap --script mysql-info -p 3306 192.168.1.1       # MySQL
nmap --script ssl-cert -p 443 192.168.1.1          # Certificat SSL
nmap --script ssl-enum-ciphers -p 443 192.168.1.1  # Ciphers TLS
nmap --script ldap-rootdse -p 389 192.168.1.1      # LDAP root DSE

# EternalBlue (MS17-010)
nmap --script smb-vuln-ms17-010 -p 445 192.168.1.1

# Heartbleed (CVE-2014-0160)
nmap --script ssl-heartbleed -p 443 192.168.1.1
```

### Timing et évasion

```bash
# Templates de timing (T0=paranoid à T5=insane)
nmap -T0 192.168.1.1    # Très lent, maximum évasion IDS
nmap -T1 192.168.1.1    # Sneaky
nmap -T2 192.168.1.1    # Poli (pour éviter surcharge cible)
nmap -T3 192.168.1.1    # Défaut
nmap -T4 192.168.1.1    # Aggressif (rapide, LAN)
nmap -T5 192.168.1.1    # Insane (très rapide, perd des paquets)

# Fragmentation (contourner certains firewalls)
nmap -f 192.168.1.1              # Fragments 8 bytes
nmap -ff 192.168.1.1             # Fragments 16 bytes

# Decoy (masquer l'IP source)
nmap -D RND:10 192.168.1.1       # 10 IPs aléatoires en decoy
nmap -D 1.2.3.4,5.6.7.8 192.168.1.1  # Decoys spécifiques

# Spoofer l'adresse source
nmap -S 10.0.0.5 192.168.1.1

# Changer le port source
nmap --source-port 53 192.168.1.1  # Sembler être du DNS

# Via proxy Tor
nmap --proxies socks4://127.0.0.1:9050 192.168.1.1

# Délais entre sondes
nmap --scan-delay 5s 192.168.1.1
nmap --max-scan-delay 10s 192.168.1.1
```

### Sorties

```bash
# Format normal
nmap -oN output.txt 192.168.1.1

# XML (pour importation dans Metasploit)
nmap -oX output.xml 192.168.1.1

# Greppable
nmap -oG output.grep 192.168.1.1

# Tous les formats
nmap -oA output 192.168.1.1

# Importer dans Metasploit
msf> db_import output.xml
msf> hosts
msf> services
```

### Scan de réseau complet

```bash
# Scan recommandé pour audit
nmap -sV -sC -p- -T4 --open -oA scan_complet 192.168.1.0/24

# Découverte rapide d'abord, puis scan détaillé
nmap -sn 192.168.1.0/24 | grep "Nmap scan" | awk '{print $5}' > hosts.txt
nmap -sV -sC -p- -iL hosts.txt -oA detail_scan
```

## Masscan — Scan Internet-scale

```bash
# Scan très rapide (rate = paquets/seconde)
masscan -p 80,443 192.168.1.0/24 --rate 1000

# Scan de tout Internet (pas en prod !)
# masscan -p 80 0.0.0.0/0 --rate 10000 --exclude 255.255.255.255

# Avec interface
masscan -p 22,80,443 192.168.1.0/24 -e eth0 --rate 5000

# Output
masscan -p 80 192.168.1.0/24 -oX masscan.xml
```

## RustScan — Découverte de ports rapide

```bash
# Scan ultra-rapide puis passe à Nmap automatiquement
rustscan -a 192.168.1.1

# Avec paramètres Nmap
rustscan -a 192.168.1.1 -- -sV -sC

# Réseau entier
rustscan -a 192.168.1.0/24 --range 1-65535 --ulimit 5000
```

## Découverte web

### Gobuster — Brute force de répertoires/fichiers

```bash
# Mode dir (répertoires et fichiers)
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt

# Avec extensions
gobuster dir -u http://target.com -w wordlist.txt -x php,html,txt,bak

# DNS (sous-domaines)
gobuster dns -d target.com -w subdomains.txt

# VHost
gobuster vhost -u http://target.com -w subdomains.txt --append-domain

# Avec proxy (Burp Suite)
gobuster dir -u http://target.com -w wordlist.txt -p http://127.0.0.1:8080

# Authentification basique
gobuster dir -u http://target.com -w wordlist.txt -U admin -P password

# Threads (défaut 10)
gobuster dir -u http://target.com -w wordlist.txt -t 50
```

### Feroxbuster — Scan web récursif

```bash
# Scan récursif
feroxbuster --url http://target.com

# Avec extensions
feroxbuster --url http://target.com -x php,html,txt

# Profondeur de récursion
feroxbuster --url http://target.com --depth 3

# Filtrer les codes de réponse
feroxbuster --url http://target.com --filter-status 404,500
```

### Nikto — Scanner de vulnérabilités web

```bash
# Scan basique
nikto -h http://target.com

# Avec proxy
nikto -h http://target.com -useproxy http://127.0.0.1:8080

# Scan HTTPS
nikto -h https://target.com -ssl

# Plugins spécifiques
nikto -h http://target.com -Tuning 4   # SQL injection
nikto -h http://target.com -Tuning 2   # Fichiers intéressants
```

## Découverte d'énumération par protocole

### SMB (445)

```bash
enum4linux -a 192.168.1.1
enum4linux-ng -A 192.168.1.1

crackmapexec smb 192.168.1.1
crackmapexec smb 192.168.1.1 --shares
crackmapexec smb 192.168.1.0/24 --users
```

### SNMP (161 UDP)

```bash
snmpwalk -v2c -c public 192.168.1.1
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.1  # Infos système

# Brute force community string
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt 192.168.1.1
```

### LDAP (389)

```bash
ldapsearch -x -h 192.168.1.1 -b "dc=domain,dc=local"
ldapsearch -x -h 192.168.1.1 -b "dc=domain,dc=local" "(objectClass=user)"
```

## Nuclei — Scanner de vulnérabilités template-based

```bash
# Scanner une cible avec tous les templates
nuclei -u http://target.com

# Sévérité spécifique
nuclei -u http://target.com -severity critical,high

# Catégorie de templates
nuclei -u http://target.com -tags cve,misconfig

# CVE spécifique
nuclei -u http://target.com -templates cves/2021/CVE-2021-44228.yaml  # Log4Shell

# Réseau entier
nuclei -l hosts.txt -severity high,critical -o results.txt
```

## Tableau récapitulatif des outils

| Outil | Usage principal | Vitesse | Précision |
|-------|----------------|---------|-----------|
| Nmap | Port/service/OS/vuln | Moyen | Très haute |
| Masscan | Découverte ports large échelle | Très rapide | Ports seulement |
| RustScan | Découverte ports + Nmap | Rapide | Haute |
| Gobuster | Découverte répertoires web | Rapide | Haute |
| Feroxbuster | Découverte web récursive | Rapide | Haute |
| ffuf | Fuzzing web polyvalent | Très rapide | Haute |
| Nikto | Vulnérabilités web connues | Lent | Moyenne |
| Nuclei | Vulnérabilités template-based | Rapide | Haute |
| enum4linux | Énumération SMB/Samba | Moyen | Haute |
| crackmapexec | Active Directory / SMB | Rapide | Haute |

## Considérations légales

Le scanning actif sans autorisation explicite est **illégal** dans la plupart des pays (France : Article 323-1 CP). Toujours obtenir une autorisation écrite (ROE — Rules of Engagement) avant tout scan sur des systèmes tiers.
