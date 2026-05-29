---
title: "Volatility 3 — Analyse de Mémoire"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis > DFIR"
tags: [sciences-appliquées, informatique, sécurité, soc, dfir]
date: "2025-02-15"
---

# Volatility 3 — Analyse de Mémoire

Volatility 3 est le framework open source de référence pour l'analyse de dumps mémoire (RAM). Il permet d'extraire des artefacts du système tels que les processus, connexions réseau, registre, fichiers et de détecter des injections malveillantes.

## Installation et prérequis

```bash
# Installation
git clone https://github.com/volatilityfoundation/volatility3
cd volatility3
pip3 install -r requirements.txt

# Vérifier l'installation
python3 vol.py -h

# Alias utile
alias vol="python3 /opt/volatility3/vol.py"
```

**Contrairement à Volatility 2, Volatility 3 ne nécessite pas de profil OS.** Il détecte automatiquement le système d'exploitation depuis le dump.

## Syntaxe générale

```bash
python3 vol.py -f <dump.mem> <plugin>
python3 vol.py -f <dump.mem> <plugin> [options]
```

## Plugins Windows

### Informations système

```bash
# Infos OS (version, build, machine)
vol -f dump.mem windows.info

# Exemple de sortie :
# Variable    Value
# Kernel Base 0xf8047e600000
# DTB         0x1ad000
# Symbols     file:///volatility3/symbols/windows/ntkrnlmp.pdb/...
# Is64Bit     True
# IsPAE       False
# primary     0 WindowsIntel32e
# memory_layer 1 FileLayer
# KdVersionBlock 0xf8047f015490
# Major/Minor 15.19041
# MachineType 34404
# ...
```

### Processus

```bash
# Liste des processus (depuis la doubly-linked list EPROCESS)
vol -f dump.mem windows.pslist

# Scan de processus (inclut les processus cachés par rootkits)
vol -f dump.mem windows.psscan

# Arborescence parent/enfant
vol -f dump.mem windows.pstree

# Ligne de commande de chaque processus
vol -f dump.mem windows.cmdline

# Arguments de processus spécifique
vol -f dump.mem windows.cmdline --pid 1234

# Variables d'environnement
vol -f dump.mem windows.envars --pid 1234

# Handles ouverts par un processus (fichiers, clés registre, etc.)
vol -f dump.mem windows.handles --pid 1234

# Modules chargés dans un processus
vol -f dump.mem windows.dlllist
vol -f dump.mem windows.dlllist --pid 1234
```

**Comparaison pslist / psscan / pstree :**

| Plugin | Source | Avantage | Cas d'usage |
|--------|--------|---------|------------|
| pslist | Doubly-linked list EPROCESS | Rapide, exhaustif pour processus normaux | Vue d'ensemble |
| psscan | Scan de structures _EPROCESS | Détecte les processus délinkés (rootkits DKOM) | Détection rootkits |
| pstree | pslist + relations parent/enfant | Visualisation hiérarchie | Lateral movement, injections |

**Anomalies à rechercher :**
- `svchost.exe` avec parent ≠ `services.exe`
- `explorer.exe` lancé par `cmd.exe` ou `powershell.exe`
- Processus systèmes avec chemin inhabituel (`C:\Temp\svchost.exe`)
- Processus avec nom légèrement différent du légitime (`svch0st.exe`, `lsasss.exe`)

### Réseau

```bash
# Connexions TCP actives (similaire à netstat)
vol -f dump.mem windows.netstat

# Scan des structures réseau (inclut connexions fermées)
vol -f dump.mem windows.netscan

# Filtrer par protocole ou état
vol -f dump.mem windows.netscan | grep ESTABLISHED
vol -f dump.mem windows.netscan | grep -v "0.0.0.0"
```

**IOCs réseau à analyser :**
- Connexions vers des IPs/ports inhabituels
- Processus légitimes (notepad, calc) avec connexions réseau
- Beaucoup de connexions depuis un seul processus
- Connexions vers des pays inhabituels

### DLLs et modules

```bash
# Lister les DLLs chargées dans tous les processus
vol -f dump.mem windows.dlllist

# DLLs pour un processus spécifique
vol -f dump.mem windows.dlllist --pid 1234

# Modules kernel
vol -f dump.mem windows.modules

# Scan de modules kernel (inclut modules cachés)
vol -f dump.mem windows.driverscan

# Vérifier l'intégrité des DLLs (comparaison avec fichiers sur disque)
vol -f dump.mem windows.dlllist | grep -v "C:\Windows"
```

### Registre

```bash
# Lister les hives chargées
vol -f dump.mem windows.registry.hivelist

# Lire une clé
vol -f dump.mem windows.registry.printkey --key "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# Chercher une valeur spécifique
vol -f dump.mem windows.registry.printkey \
    --key "SOFTWARE\Microsoft\Windows\CurrentVersion\Run" \
    --recurse

# Hive complète d'un utilisateur (NTUSER.DAT)
vol -f dump.mem windows.registry.hivelist | grep NTUSER
```

### Extraction de fichiers

```bash
# Scanner les fichiers en mémoire
vol -f dump.mem windows.filescan

# Filtrer par extension
vol -f dump.mem windows.filescan | grep -i ".exe\|.dll\|.ps1"

# Extraire un fichier (par adresse virtuelle depuis filescan)
vol -f dump.mem windows.dumpfiles --virtaddr 0xe48f2be2a020

# Extraire tous les fichiers d'un processus
vol -f dump.mem windows.dumpfiles --pid 1234

# Extraire l'exécutable d'un processus
vol -f dump.mem windows.procdump --pid 1234
```

### Détection d'injection (malfind)

`malfind` est le plugin principal pour détecter du code injecté. Il recherche les régions mémoire avec permissions exécutables (RWX ou RX) sans fichier sur disque associé.

```bash
# Détecter les injections
vol -f dump.mem windows.malfind

# Filtrer par PID
vol -f dump.mem windows.malfind --pid 1234

# Exemple de sortie malfind :
# PID    Process   Start            End              Tag   Protection
# 1234   explorer  0x00400000       0x00500000       VadS  PAGE_EXECUTE_READWRITE
# Disassembly:
# 0x00400000  4d 5a 90 00 03 00 00 00   MZ......  ← MZ header = PE injecté !
```

**Interpréter malfind :**
- `MZ` header = Portable Executable injecté (process hollowing ou DLL injection)
- Shellcode : instructions x86/x64 sans MZ header (souvent du code de stager)
- `PAGE_EXECUTE_READWRITE` = mémoire RWX (suspect, sauf JIT)

### Secrets et credentials

```bash
# Extraire les hashes NTLM (SAM)
vol -f dump.mem windows.hashdump

# Extraire les hashes depuis le domaine (NTDS)
vol -f dump.mem windows.hashdump --sam <sam_offset> --sys <system_offset>

# LSA secrets
vol -f dump.mem windows.lsadump

# Chercher des strings de mots de passe en mémoire
vol -f dump.mem windows.strings | grep -i "password\|passwd\|credentials"

# Ou extraire les strings directement
strings -el dump.mem | grep -i "http\|ftp\|password\|token" | head -100
```

### Rootkits et évasion

```bash
# SSDT hooks (System Service Descriptor Table)
vol -f dump.mem windows.ssdt

# Callbacks kernel (notification routines)
vol -f dump.mem windows.callbacks

# Vérifier IDT (Interrupt Descriptor Table)
vol -f dump.mem windows.idt

# Comparer modules pslist vs psscan (processus cachés !)
vol -f dump.mem windows.pslist > pslist.txt
vol -f dump.mem windows.psscan > psscan.txt
diff pslist.txt psscan.txt
# Les PIDs dans psscan mais pas pslist = processus cachés par rootkit
```

### YARA scanning

```bash
# Scanner avec règle YARA
vol -f dump.mem windows.yarascan.YaraScan --yara-file malware.yar

# Avec règle inline
vol -f dump.mem windows.yarascan.YaraScan \
    --yara-rules 'rule test { strings: $s = "malware" condition: $s }'

# Dans un processus spécifique
vol -f dump.mem windows.yarascan.YaraScan \
    --yara-file malware.yar --pid 1234
```

## Plugins Linux

```bash
# Infos Linux
vol -f dump.mem linux.bash

# Processus Linux
vol -f dump.mem linux.pslist
vol -f dump.mem linux.pstree

# Connexions réseau
vol -f dump.mem linux.netstat

# Modules kernel chargés
vol -f dump.mem linux.lsmod

# Fichiers ouverts
vol -f dump.mem linux.lsof

# Malfind Linux
vol -f dump.mem linux.malfind

# Check rootkit (comparer les syscall table entries)
vol -f dump.mem linux.check_syscall
```

## Workflow d'investigation complet

### Étape 1 : Orientation

```bash
# Identifier l'OS
vol -f dump.mem windows.info

# Vue d'ensemble des processus
vol -f dump.mem windows.pstree > pstree.txt
cat pstree.txt
```

### Étape 2 : Processus suspects

```bash
# Identifier les anomalies
vol -f dump.mem windows.psscan > psscan.txt
vol -f dump.mem windows.pslist > pslist.txt

# Processus avec connexions réseau
vol -f dump.mem windows.netscan | grep ESTABLISHED

# Lignes de commande complètes
vol -f dump.mem windows.cmdline
```

### Étape 3 : Injection et code malveillant

```bash
# Rechercher les injections
vol -f dump.mem windows.malfind

# Pour chaque PID suspect, extraire l'image
vol -f dump.mem windows.procdump --pid $SUSPICIOUS_PID

# Analyser les DLLs hors \Windows\
vol -f dump.mem windows.dlllist --pid $SUSPICIOUS_PID | grep -v "C:\\Windows"
```

### Étape 4 : Réseau et C2

```bash
# Connexions actives
vol -f dump.mem windows.netstat

# Toutes les connexions (inclus fermées)
vol -f dump.mem windows.netscan | tee netconn.txt
grep ESTABLISHED netconn.txt
grep -v "0.0.0.0" netconn.txt
```

### Étape 5 : Persistence

```bash
# Run Keys
vol -f dump.mem windows.registry.printkey \
    --key "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# Services
vol -f dump.mem windows.svcscan

# Tâches planifiées (via filescan)
vol -f dump.mem windows.filescan | grep -i "\\tasks\\"
```

### Étape 6 : Extraction et analyse

```bash
# Extraire les exécutables suspects
vol -f dump.mem windows.procdump --pid $PID

# Analyser avec YARA
yara malware_rules.yar pid.$PID.*.exe

# Hash pour VirusTotal
sha256sum pid.*.exe
```

## Référence rapide des plugins

| Plugin | Description |
|--------|-------------|
| `windows.info` | Informations OS |
| `windows.pslist` | Liste processus |
| `windows.psscan` | Scan processus (rootkits) |
| `windows.pstree` | Arborescence processus |
| `windows.cmdline` | Lignes de commande |
| `windows.dlllist` | DLLs par processus |
| `windows.netscan` | Connexions réseau (inclus fermées) |
| `windows.netstat` | Connexions actives |
| `windows.filescan` | Fichiers en mémoire |
| `windows.dumpfiles` | Extraire fichiers |
| `windows.procdump` | Extraire exécutable |
| `windows.malfind` | Détecter injections |
| `windows.hashdump` | Extraire hashes NTLM |
| `windows.lsadump` | LSA secrets |
| `windows.ssdt` | SSDT hooks |
| `windows.modules` | Modules kernel |
| `windows.driverscan` | Scan drivers |
| `windows.registry.hivelist` | Hives registre |
| `windows.registry.printkey` | Lire clé registre |
| `windows.svcscan` | Services Windows |
| `windows.yarascan.YaraScan` | Scanner avec YARA |
| `windows.callbacks` | Kernel callbacks |
| `windows.handles` | Handles ouverts |
| `windows.envars` | Variables d'environnement |
| `windows.memmap` | Mapping mémoire processus |
