---
title: "Scanning & Enumeration (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, enumeration, pnpt]
date: "2026-05-18"
---

# Scanning & Enumeration

L'énumération, c'est l'étape la plus rentable d'un pentest. Une heure de plus passée à interroger un service mal compris peut éviter trois heures d'exploitation à l'aveugle. Chaque protocole a son outil, ses commandes anonymes, ses misconfig classiques — c'est ça qu'il faut savoir.

## Méthode mentale par service

Pour chaque port ouvert, se poser systématiquement :

```
1. Quel service tourne ? (version exacte → CVE potentielles)
2. Accepte-t-il une connexion anonyme ? (souvent oui en interne)
3. Quelles infos divulgue-t-il sans authentification ? (users, shares, version)
4. Quels comptes par défaut existent ? (admin/admin, sa/sa, root sans mdp)
5. Y a-t-il des misconfig connues ? (anonymous access, null session, default creds)
```

C'est cette routine qui distingue une énumération sérieuse d'un scan automatisé qui passe à côté.

## Nmap : recap rapide

```bash
nmap -sC -sV -oN scan.txt IP        # standard : scripts par défaut + version
nmap -T4 -p- IP                      # tous les ports TCP
nmap -sU --top-ports 50 IP           # UDP (lent)
nmap -A IP                           # tout (OS, scripts, traceroute)
nmap --script=vuln IP                # scripts de détection de vulns
nmap --script=auth IP                # scripts d'authentification (anonymous, default creds)
```

Voir aussi `05-reconnaissance` pour les flags détaillés.

## SMB (445) — souvent le jackpot en interne

SMB partage des fichiers Windows. Sur un AD, c'est la voie royale : shares mal configurés, null sessions, relay NTLM.

```
Énumération SMB — l'arbre de décision

         smbclient -L //IP/ -N
              │
       ┌──────┴───────┐
       ▼              ▼
   ça liste         accès refusé
       │              │
       ▼              ▼
 énumérer shares   tester avec creds
       │           (CrackMapExec)
       ▼
 chercher fichiers
 sensibles
```

```bash
smbclient -L //IP/ -N                              # lister shares anonymement
smbclient //IP/share -N                            # se connecter à un share
smbmap -H IP                                       # permissions par share
smbmap -H IP -u user -p pass                       # avec creds
enum4linux -a IP                                   # énumération exhaustive (legacy mais utile)
enum4linux-ng IP                                   # version moderne

crackmapexec smb IP --shares                       # lister shares
crackmapexec smb IP -u '' -p '' --shares           # acces anonyme
crackmapexec smb IP -u user -p pass --shares       # avec creds
nxc smb IP -u user -p pass --shares                # nxc = nouveau nom de cme
```

**Null session** : `smbclient -U "" -N //IP/IPC$` — sur des Windows pas patchés, on récupère users, groupes, politique de mots de passe.

## HTTP/HTTPS (80, 443)

```bash
whatweb http://IP                                  # technos web (CMS, frameworks)
nikto -h http://IP                                 # vulns classiques (mauvaise config)
gobuster dir -u http://IP -w wordlist              # brute force chemins
feroxbuster -u http://IP -w wordlist -d 3         # récursif
ffuf -u http://IP/FUZZ -w wordlist                # alternative rapide

# Détection vhost (Host header)
ffuf -u http://IP -H "Host: FUZZ.cible.com" -w hostnames.txt -fs SIZE_BASELINE
```

**À tester systématiquement** : `/robots.txt`, `/.git/`, `/.env`, `/backup/`, `/admin/`, `/api/`. Un `.git` exposé donne tout le code source.

## FTP (21)

```bash
ftp IP                              # essayer anonymous:anonymous
nmap --script=ftp-anon IP
nmap --script=ftp-vsftpd-backdoor IP
```

FTP transmet en clair. Sur un réseau interne, un sniff peut révéler des credentials FTP utilisés ailleurs (réutilisation).

## SSH (22)

```bash
ssh user@IP                         # connexion classique
ssh-audit IP                        # audit config SSH (algos faibles)
hydra -l user -P wordlist.txt ssh://IP    # brute force (bruyant, lockout possible)

# Énumération d'utilisateurs sur OpenSSH < 7.7 (CVE-2018-15473)
python3 ssh-user-enum.py -U users.txt IP
```

**Brute force SSH = risqué** : fail2ban et alerting le détectent. Préférer des credentials trouvés ailleurs.

## DNS (53)

```bash
dig axfr @IP domaine.com            # zone transfer
dnsrecon -d domaine.com -t axfr
dnsrecon -d domaine.com -D wordlist.txt -t brt   # brute force sous-domaines
```

## SMTP (25)

```bash
smtp-user-enum -M VRFY -U users.txt -t IP        # énumération via VRFY
nmap --script=smtp-enum-users IP
nmap --script=smtp-commands IP                   # commandes acceptées
```

**Commandes VRFY/EXPN** : sur de vieux serveurs mail, elles confirment l'existence d'un utilisateur sans authentification. Donne une liste valide pour phishing ou brute force ailleurs.

## SNMP (161 UDP)

SNMP est souvent négligé. Avec la "community string" par défaut (`public` ou `private`), on récupère TOUT l'état du device.

```bash
snmpwalk -v2c -c public IP                       # dump complet (verbeux)
snmpwalk -v2c -c public IP 1.3.6.1.2.1.1         # infos système seulement
onesixtyone -c communities.txt IP                # brute force community strings

# OIDs intéressants sur Windows
snmpwalk -v2c -c public IP 1.3.6.1.4.1.77.1.2.25  # liste users
snmpwalk -v2c -c public IP 1.3.6.1.2.1.25.4.2.1.2 # processus en cours
```

## LDAP (389) / LDAPS (636)

LDAP = annuaire AD. Souvent énumérable anonymement.

```bash
ldapsearch -x -H ldap://IP -b "dc=domaine,dc=com"           # dump complet
ldapsearch -x -H ldap://IP -s base -b "" namingContexts     # trouver la base DN
nmap --script=ldap-search IP

# Avec creds
ldapsearch -x -H ldap://IP -D "user@domaine.com" -w 'pass' -b "dc=domaine,dc=com"

# Énumération AD via LDAP (sans creds parfois possible)
windapsearch -d domaine.com --dc-ip IP -U
```

## RPC (135)

```bash
rpcclient -U "" -N IP                   # null session
  > enumdomusers                        # liste users
  > enumdomgroups
  > queryuser 0x1f4                     # info user (RID 500 = admin)
  > lookupnames Administrator
  > getdompwinfo                        # politique de mots de passe
```

## MSSQL (1433)

```bash
nmap -p 1433 --script ms-sql-info,ms-sql-empty-password,ms-sql-config IP

# Connexion avec creds
mssqlclient.py domaine/user:pass@IP -windows-auth
crackmapexec mssql IP -u user -p pass -q "SELECT @@version"

# Une fois connecté
> enable_xp_cmdshell                    # activer exécution de commandes OS
> xp_cmdshell whoami
> enum_links                            # liens vers d'autres bases (pivot)
> enum_impersonate                      # users qu'on peut impersonner
```

**`xp_cmdshell` = RCE Windows** si on est sysadmin sur le SQL Server.

## MySQL (3306)

```bash
nmap -p 3306 --script mysql-empty-password,mysql-users,mysql-databases IP
mysql -h IP -u root -p
mysql -h IP -u root --skip-ssl          # parfois nécessaire
```

## WinRM (5985 / 5986)

WinRM = PowerShell distant. Si on a des creds, c'est shell direct.

```bash
crackmapexec winrm IP -u user -p pass            # tester
evil-winrm -i IP -u user -p pass                 # shell interactif
evil-winrm -i IP -u user -H NTLM_HASH            # pass-the-hash
```

## NFS (2049)

```bash
showmount -e IP                                  # lister les exports
mkdir /mnt/nfs && mount -t nfs IP:/share /mnt/nfs
```

**`no_root_squash`** dans `/etc/exports` côté serveur = on monte le share en tant que root local et on a droits root sur les fichiers. Privesc classique : créer un binaire SUID-root et l'exécuter.

## Redis (6379)

```bash
redis-cli -h IP
  > info
  > config get *
  > keys *
```

**RCE Redis** : si Redis tourne en root sans auth, écrire une clé SSH dans `/root/.ssh/authorized_keys` via `CONFIG SET dir + SAVE`.

## NTP (123) et IPMI (623)

```bash
ntpq -c rv IP
nmap -sU -p 123 --script=ntp-info IP

# IPMI — protocole d'admin matérielle, souvent vulnérable
nmap -sU -p 623 --script=ipmi-version,ipmi-cipher-zero IP
```

**Cipher zero IPMI** = auth bypass complet, dump des hashes possibles. Bug ancien mais encore présent sur des serveurs oubliés.

## Pièges courants

- **Ne pas prendre "anonymous=non" comme final** : tester avec un compte trivial (guest, anonymous, admin/admin) avant de conclure.
- **Les outils CrackMapExec/nxc sont parfois renommés** : `crackmapexec` est devenu `nxc` (NetExec). Garder les deux en tête.
- **Le rate-limiting peut fausser l'énumération** : un service avec rate-limit fait passer pour fermé un port en réalité ouvert. Toujours scanner deux fois si doute.
- **null sessions** sont désactivées sur Windows récents (>= Server 2008 par défaut). Mais on les voit encore sur du legacy.
- **SNMP v3** est chiffré et nécessite auth — `snmpwalk -v2c` échoue alors. Tester `v3` séparément.
- **Toujours noter les versions exactes** : "Apache 2.4.41" ≠ "Apache 2.4.49". Une seule version a Path Traversal critique (CVE-2021-41773). Sans la version exacte on rate les CVE.
