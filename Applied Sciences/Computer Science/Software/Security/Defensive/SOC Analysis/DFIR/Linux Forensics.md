---
title: Linux Forensics
domain: sciences-appliquées
subdomain: informatique / sécurité / dfir
tags: [forensics, linux, dfir, investigation, artefacts, sécurité]
date: 2026-03-22
---

# Linux Forensics

## Ordre de volatilité et collecte initiale

```bash
# 1. Mémoire vive — capturer avant tout
avml /tmp/memory.lime                     # AVML (Azure Volatile Memory Library)
# ou insmod lime-$(uname -r).ko "path=/tmp/mem.lime format=lime"

# 2. Processus et connexions réseau (avant extinction)
ps auxww > /tmp/processes.txt
ss -tulnp > /tmp/network.txt
netstat -anp > /tmp/netstat.txt
lsof -nP > /tmp/open_files.txt
lsof -nPi > /tmp/network_files.txt

# 3. Modules kernel chargés
lsmod > /tmp/modules.txt
cat /proc/modules > /tmp/proc_modules.txt

# 4. Tâches planifiées
crontab -l > /tmp/crontab_user.txt
cat /etc/crontab > /tmp/crontab_system.txt
ls -la /etc/cron.* >> /tmp/crontab_system.txt

# 5. Utilisateurs connectés / historique connexions
who > /tmp/who.txt
w > /tmp/w.txt
last > /tmp/last.txt
lastlog > /tmp/lastlog.txt
```

### Acquisition disque

```bash
# Créer une image bit-à-bit
dd if=/dev/sda of=/mnt/evidence/disk.dd bs=4096 conv=noerror,sync status=progress

# Avec dc3dd (log + hash intégré)
dc3dd if=/dev/sda of=/mnt/evidence/disk.dd hash=sha256 log=/mnt/evidence/disk.log

# Compressé
dd if=/dev/sda | gzip -c > /mnt/evidence/disk.dd.gz

# Vérification d'intégrité
sha256sum /dev/sda
sha256sum /mnt/evidence/disk.dd
# Les deux hashes doivent correspondre

# Montage en lecture seule pour l'analyse
mount -o ro,noatime /dev/sdb1 /mnt/analysis
# ou : mount -o ro,loop /mnt/evidence/disk.dd /mnt/analysis
```

## Journaux système

### Fichiers de logs importants

```bash
# Authentification
/var/log/auth.log        # Debian/Ubuntu
/var/log/secure          # RHEL/CentOS

# Syslog et kernel
/var/log/syslog          # Debian/Ubuntu
/var/log/messages        # RHEL/CentOS
/var/log/kern.log        # Messages kernel
dmesg                    # Buffer kernel en mémoire

# Journald (systemd)
journalctl                                # Tous les logs
journalctl -u sshd                        # Logs d'un service
journalctl --since "2026-01-01" --until "2026-01-02"
journalctl -p err                         # Niveau erreur et au-dessus

# Apache/Nginx
/var/log/apache2/access.log
/var/log/apache2/error.log
/var/log/nginx/access.log

# Base de données
/var/log/mysql/mysql.log
/var/log/postgresql/postgresql-*.log

# Connexions SSH
grep "Accepted\|Failed\|Invalid" /var/log/auth.log
grep "sshd" /var/log/auth.log | grep -v "pam\|closed"
```

### Analyse des connexions SSH

```bash
# Connexions réussies
grep "Accepted password\|Accepted publickey" /var/log/auth.log |
    awk '{print $1, $2, $3, $9, $11}'

# Tentatives de brute-force
grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn | head

# Clés SSH autorisées
cat /root/.ssh/authorized_keys
cat /home/*/.ssh/authorized_keys 2>/dev/null

# Clés SSH générées récemment
find / -name "id_rsa" -o -name "id_ed25519" 2>/dev/null -newer /tmp/reference_time
```

## Persistance — artefacts courants

### Cron et tâches planifiées

```bash
# Toutes les crons
for user in $(cat /etc/passwd | cut -d: -f1); do
    cron=$(crontab -u $user -l 2>/dev/null)
    if [ -n "$cron" ]; then
        echo "=== $user ==="; echo "$cron"
    fi
done

cat /etc/crontab
ls -la /etc/cron.d/ /etc/cron.daily/ /etc/cron.weekly/ /etc/cron.monthly/
cat /etc/cron.d/*

# Timers systemd (alternative aux crons)
systemctl list-timers --all
find /etc/systemd/ /usr/lib/systemd/ -name "*.timer" | xargs cat
```

### Services et démons

```bash
# Services systemd
systemctl list-units --type=service --all
find /etc/systemd/system/ -name "*.service" | xargs grep -l "ExecStart" | head
# Inspecter les services suspects
systemctl cat nom-service-suspect

# Init.d (système SysV héritage)
ls -la /etc/init.d/
ls -la /etc/rc*.d/

# Modules kernel (rootkits potentiels)
lsmod | grep -v "$(lsmod | awk '{print $1}' | sort)" 2>/dev/null
# Comparer avec un système de référence sain
```

### Fichiers de démarrage

```bash
# Fichiers exécutés au démarrage de session
cat /etc/profile
cat /etc/environment
cat /etc/profile.d/*
cat ~/.bashrc ~/.bash_profile ~/.profile ~/.zshrc 2>/dev/null

# rc.local (exécuté au boot)
cat /etc/rc.local

# PAM (Pluggable Authentication Modules) — possibilité d'injecter un module malveillant
cat /etc/pam.d/sshd
ls -la /lib/security/*.so      # Modules PAM — vérifier les dates
```

## Système de fichiers — artefacts

### Fichiers modifiés récemment

```bash
# Fichiers modifiés dans les 24 dernières heures
find / -mtime -1 -type f 2>/dev/null | grep -v "/proc\|/sys\|/dev"

# Fichiers SUID/SGID récents (indicateur de backdoor)
find / -perm -u=s -type f -newer /bin/ls 2>/dev/null
find / -perm -g=s -type f -newer /bin/ls 2>/dev/null

# Fichiers cachés dans des répertoires inhabituels
find /tmp /var/tmp /dev/shm -name ".*" 2>/dev/null
find / -name ".*" -path "*/tmp/*" 2>/dev/null

# Fichiers sans propriétaire (UID/GID supprimé)
find / -nouser -o -nogroup 2>/dev/null

# Fichiers exécutables dans /tmp, /var/tmp, /dev/shm (suspects)
find /tmp /var/tmp /dev/shm -executable -type f 2>/dev/null
```

### Analyse du système de fichiers ext4

```bash
# Inode information — MAC times précis
stat /suspicious/file

# Fichiers supprimés récupérables
# Avec Autopsy ou The Sleuth Kit
fls -r -d /dev/sda1 | grep "^r/r \*"  # Fichiers supprimés
icat /dev/sda1 <numéro_inode> > recovered_file

# Journal du filesystem (ext4 journal — ext3grep, extundelete)
extundelete /dev/sda1 --restore-all

# Métadonnées de fichiers
debugfs /dev/sda1
debugfs> stat <file>      # Tous les timestamps
debugfs> lsdel            # Fichiers supprimés
```

### Historique des commandes

```bash
# Historique bash
cat /root/.bash_history
cat /home/*/.bash_history 2>/dev/null

# Historique zsh
cat /root/.zsh_history
cat /home/*/.zsh_history 2>/dev/null

# Attention : l'historique peut être désactivé (HISTFILE=/dev/null)
# ou effacé (history -c)

# Alternative — chercher des commandes dans les logs
grep "sudo" /var/log/auth.log
grep "CMD" /var/log/auth.log  # Commandes sudo

# .viminfo — fichiers ouverts avec vim
cat /root/.viminfo
cat /home/*/.viminfo 2>/dev/null
```

## Analyse mémoire (Volatility 3)

```bash
# Profil Linux — nécessite un profil correspondant à la version du kernel
vol -f memory.lime linux.pslist          # Processus
vol -f memory.lime linux.pstree         # Arbre de processus
vol -f memory.lime linux.bash           # Historique bash en mémoire
vol -f memory.lime linux.netstat        # Connexions réseau
vol -f memory.lime linux.lsof           # Fichiers ouverts
vol -f memory.lime linux.malfind        # Pages mémoire exécutables injectées
vol -f memory.lime linux.check_syscall  # Table des syscalls (rootkit détection)
vol -f memory.lime linux.check_modules  # Modules kernel (rootkit)

# Dump d'un processus suspect
vol -f memory.lime linux.proc.Maps --pid 1234
vol -f memory.lime linux.memmap --pid 1234 --dump
```

## Rootkits

```bash
# Chkrootkit — détection basique
chkrootkit

# Rkhunter
rkhunter --check --sk

# Comparaison avec des hashes connus (Tripwire, AIDE)
aide --check

# Vérifier les syscall hooks (processus cachés par rootkit)
ps aux > /tmp/ps_output.txt
# Comparer avec la liste /proc
ls /proc | grep -E "^[0-9]+$" > /tmp/proc_pids.txt
# Si des PIDs dans /proc n'apparaissent pas dans ps → rootkit probable

# Vérifier les fichiers cachés par un rootkit
# Les rootkits hookent getdents() → les fichiers sont invisibles pour ls
# Mais /proc/PID/exe et /proc/PID/maps révèlent le binaire
for pid in $(ls /proc | grep -E "^[0-9]+$"); do
    if ! ps -p $pid > /dev/null 2>&1; then
        echo "Processus caché: $pid"
        ls -la /proc/$pid/exe 2>/dev/null
    fi
done
```

## Timeline et corrélation

```bash
# Mactime (Sleuth Kit) — timeline à partir du système de fichiers
fls -r -m / /dev/sda1 > body_file.txt
mactime -b body_file.txt -d > timeline.csv

# Combiner avec les logs
# Importer dans un outil comme Timeline Explorer ou Kibana pour la corrélation

# log2timeline/plaso
log2timeline.py --parsers linux timeline.plaso /dev/sda1
psort.py -o l2tcsv timeline.plaso > supertimeline.csv
```
