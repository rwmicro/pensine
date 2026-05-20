---
title: Windows Forensics
domain: sciences-appliquées
subdomain: informatique / sécurité / dfir
tags: [forensics, windows, dfir, investigation, artefacts, sécurité]
date: 2026-03-22
---

# Windows Forensics

L'investigation numérique Windows vise à reconstituer les actions passées sur un système en analysant les artefacts laissés dans le registre, les journaux d'événements, le système de fichiers et la mémoire.

## Collecte et triage initial

### Ordre de volatilité

```
1. Mémoire vive (RAM)              ← Perdu à l'extinction
2. Processus en cours, connexions réseau
3. Données dans la swap/pagefile
4. Registre (partiellement en RAM)
5. Fichiers temporaires
6. Journaux d'événements
7. Système de fichiers (disque)    ← Persiste après extinction
8. Médias de sauvegarde
```

### Acquisition mémoire

```powershell
# WinPmem — acquisition de la RAM (gratuit)
winpmem_mini_x64_rc2.exe -o memory.raw

# DumpIt (Comae Technologies)
DumpIt.exe /O memory.dmp

# Volatility 3 — analyse de la RAM acquise
vol -f memory.raw windows.pslist
vol -f memory.raw windows.netscan
vol -f memory.raw windows.cmdline
```

### Acquisition du disque

```bash
# FTK Imager (GUI) — créer une image forensique
# File → Create Disk Image → Physical Drive → E01 format

# En ligne de commande (si FTK CLI disponible)
ftkimager.exe \\.\PHYSICALDRIVE0 D:\evidence\disk.E01 --e01

# Linux (si le disque est monté sur un système Linux)
sudo dc3dd if=/dev/sdb of=/evidence/disk.dd bs=512 log=/evidence/disk.log

# Calcul de hash pour l'intégrité de la chaîne de preuves
certutil -hashfile disk.E01 SHA256
```

## Registre Windows

Le registre contient une quantité massive d'artefacts forensiques.

### Ruches principales

```
HKEY_LOCAL_MACHINE (HKLM)
  \SYSTEM     → Configuration système, services, drivers
  \SOFTWARE   → Applications installées, configuration
  \SAM        → Comptes locaux et hashes NTLM (chiffrés, nécessite SYSTEM)
  \SECURITY   → Politique de sécurité, LSA secrets

HKEY_CURRENT_USER (HKCU)
  \SOFTWARE   → Configuration par utilisateur
  Fichier sur disque : C:\Users\<user>\NTUSER.DAT

HKEY_USERS (HKU)
  Toutes les ruches utilisateurs chargées

Fichiers sur disque (C:\Windows\System32\config\) :
  SYSTEM, SOFTWARE, SAM, SECURITY, DEFAULT
  C:\Users\<user>\NTUSER.DAT
  C:\Users\<user>\AppData\Local\Microsoft\Windows\UsrClass.dat
```

### Artefacts forensiques clés

```powershell
# Programmes au démarrage (persistance)
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
reg query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run

# Services installés
reg query HKLM\SYSTEM\CurrentControlSet\Services

# Derniers fichiers ouverts (RecentDocs)
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"

# Programmes récemment exécutés (UserAssist — obfusqué en ROT13)
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist"

# Connexions réseau récentes
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections"

# Clés USB connectées (identification des périphériques)
reg query "HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR"

# Shellbags — dossiers parcourus même si le dossier n'existe plus
# HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\BagMRU
# Outil : ShellBags Explorer (Eric Zimmermann)

# MuiCache — binaires exécutés
reg query "HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache"
```

### Extraction de ruches avec RegRipper

```bash
# RegRipper — analyse automatisée des ruches
rip.pl -r NTUSER.DAT -f ntuser    # Tous les plugins pour NTUSER
rip.pl -r SYSTEM -f system        # Services, USB, etc.
rip.pl -r SAM -f sam              # Comptes locaux

# Plugin spécifique
rip.pl -r SOFTWARE -f recentdocs  # Documents récents
rip.pl -r SYSTEM -f usbstor       # Périphériques USB
```

## Journaux d'événements Windows (Event Logs)

```
Emplacement : C:\Windows\System32\winevt\Logs\
Fichiers .evtx analysables avec Event Viewer, PowerShell, ou outils forensiques
```

### Event IDs critiques

| Event ID | Canal | Signification |
|---|---|---|
| 4624 | Security | Connexion réussie |
| 4625 | Security | Connexion échouée |
| 4634/4647 | Security | Déconnexion |
| 4648 | Security | Connexion avec des credentials explicites (runas) |
| 4672 | Security | Droits spéciaux à la connexion (SeDebugPrivilege…) |
| 4688 | Security | Création d'un processus (si audit activé) |
| 4698/4702 | Security | Tâche planifiée créée/modifiée |
| 4720/4726 | Security | Compte créé/supprimé |
| 4732/4733 | Security | Ajout/suppression d'un groupe |
| 4768/4769 | Security | Kerberos TGT/TGS demandé |
| 4776 | Security | Authentification NTLM |
| 7045 | System | Service installé |
| 1102 | Security | Journaux d'événements effacés |
| 4104 | PowerShell | Exécution de script PowerShell (ScriptBlock logging) |

```powershell
# Requêter les journaux
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4624]]" |
    Select-Object TimeCreated, Message | Format-List

# Détecter les connexions à distance (logon type 3 = réseau, 10 = remote interactive)
Get-WinEvent -LogName Security |
    Where-Object {$_.Id -eq 4624} |
    Where-Object {$_.Message -match "Logon Type:\s+3"} |
    Select-Object TimeCreated, Message

# Connexions PowerShell Remoting
Get-WinEvent -LogName "Microsoft-Windows-WinRM/Operational"

# Script PowerShell encodé exécuté
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" |
    Where-Object {$_.Id -eq 4104} |
    Select-Object TimeCreated, Message
```

## Artefacts système de fichiers

### Prefetch

```powershell
# Préfetch : liste des programmes exécutés avec horodatage
# C:\Windows\Prefetch\*.pf
# Outil : WinPrefetchView (NirSoft)

# PowerShell
Get-ChildItem C:\Windows\Prefetch | Sort-Object LastWriteTime -Descending | Select -First 20
# Chaque .pf = nom de l'exécutable + jusqu'à 8 horodatages d'exécution
```

### Shimcache / AppCompatCache

```
Registre : HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache
Contient tous les exécutables avec date de dernière modification
(même si exécutés ou non — seulement les fichiers qui ont été sur le disque)

Outil : AppCompatCacheParser.exe (Eric Zimmermann)
AppCompatCacheParser.exe -f SYSTEM --csv .
```

### Amcache

```
C:\Windows\AppCompat\Programs\Amcache.hve
Contient le hash SHA1 des exécutables lancés, chemin, date de première exécution

AmcacheParser.exe -f Amcache.hve --csv .
```

### LNK et Jump Lists

```
Raccourcis créés automatiquement à l'ouverture de fichiers :
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\*.lnk
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations\

Contenu : chemin du fichier, volume, taille, MAC times au moment de l'accès
Outil : LECmd.exe (Eric Zimmermann)
LECmd.exe -d "C:\Users\User\AppData\Roaming\Microsoft\Windows\Recent" --csv .
```

### $MFT — Master File Table

```bash
# La MFT NTFS contient des métadonnées sur chaque fichier :
# MAC times (Modified, Accessed, Changed, Born/Created)
# Taille, permissions, attributs

# Extraire la MFT
# FTK Imager : File > Add Evidence > Physical Drive > naviguer vers [\NONAME\[root]\$MFT]

# Analyser avec MFTECmd
MFTECmd.exe -f $MFT --csv . --csvf mft_output.csv

# Timeline avec MAC times
MFTECmd.exe -f $MFT --csv . --csvf mft_timeline.csv
# Importer dans Timeline Explorer (Eric Zimmermann)
```

### Volume Shadow Copies

```powershell
# Copies d'ombre — snapshots du système à différents moments
vssadmin list shadows

# Monter une shadow copy
mklink /d C:\shadow1 \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\
# Examiner les fichiers tels qu'ils étaient au moment du snapshot

# Récupérer un fichier depuis une shadow copy
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SAM C:\evidence\
```

## Timeline et corrélation

```bash
# Plaso / log2timeline — créer une super-timeline multi-sources
log2timeline.py --parsers win7 timeline.plaso /dev/sdb1
psort.py -o l2tcsv timeline.plaso > supertimeline.csv

# Sources incluses : MFT, registre, journaux événements, prefetch, LNK, shellbags...

# Filtrer par fenêtre temporelle
psort.py timeline.plaso "date > '2026-01-01' AND date < '2026-01-02'" > jan1.csv
```

## Outils de référence

| Outil | Éditeur | Fonction |
|---|---|---|
| Volatility 3 | Open source | Analyse mémoire |
| Eric Zimmermann Tools (EZTools) | Gratuit | MFT, LNK, Amcache, Prefetch |
| RegRipper | Open source | Analyse registre |
| Autopsy | Open source | Suite forensique GUI |
| FTK Imager | Gratuit | Acquisition d'image |
| Plaso/log2timeline | Open source | Super-timeline |
| KAPE | Kroll | Collecte et triage rapide |
| Arsenal Image Mounter | Gratuit/payant | Montage d'images forensiques |
