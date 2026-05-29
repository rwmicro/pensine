---
title: "Analyse de mémoire"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis > DFIR"
tags: [sciences-appliquées, informatique, sécurité, soc, dfir]
date: "2025-02-15"
---

# Analyse de mémoire

La mémoire vive (RAM) est l'une des sources d'information les plus précieuses en forensique numérique. Elle contient des artefacts éphémères invisibles sur le disque : processus en cours, connexions réseau actives, clés de chiffrement, mots de passe en clair, code malveillant injecté, et fragments de documents ouverts.

## Acquisition de la mémoire

### Windows

```powershell
# FTK Imager (GUI + ligne de commande)
# File > Capture Memory → sélectionner le chemin de sortie
# Produit un fichier .mem ou .raw

# WinPmem (open source)
winpmem_mini_x64_rc2.exe memdump.raw

# DumpIt (Comae / Magnet)
DumpIt.exe /OUTPUT memdump.raw

# Vérifier le hash après acquisition
Get-FileHash memdump.raw -Algorithm SHA256
```

### Linux — LiME (Loadable Kernel Module)

LiME permet d'acquérir la mémoire vive sur Linux et Android sans altérer l'état du système cible.

```bash
# Compiler LiME sur la machine cible (ou cross-compiler)
cd LiME/src
make

# Charger le module — dump vers un fichier local
sudo insmod lime.ko "path=/tmp/memdump.raw format=raw"

# Dump vers réseau (pour minimiser l'impact sur le disque de la machine compromise)
sudo insmod lime.ko "path=tcp:4444 format=raw"

# Sur la machine d'analyse, recevoir le dump
nc -l -p 4444 > memdump.raw

# Vérification d'intégrité
sha256sum memdump.raw
```

Formats supportés : `raw` (dump brut), `lime` (format LiME avec en-têtes de segment), `padded`.

## Structure de la mémoire virtuelle

Chaque processus possède son propre espace d'adressage virtuel. L'OS maintient une structure (EPROCESS sur Windows, task_struct sur Linux) qui décrit chaque processus. Volatility navigue ces structures pour reconstruire l'état du système.

```
Mémoire physique
├── Noyau OS (kernel space)
│   ├── Structures de processus (EPROCESS, task_struct)
│   ├── Listes chaînées des processus actifs
│   └── Listes des objets (handles, tokens, connexions)
└── Espace utilisateur (user space)
    ├── Code de l'exécutable
    ├── Bibliothèques (DLL, .so)
    ├── Heap
    └── Stack
```

## Volatility 3

Volatility 3 est le standard de l'analyse de mémoire. Il utilise des profils de symboles (ISF) pour interpréter les structures noyau.

```bash
# Installation
pip install volatility3

# Identifier le profil (OS, version, architecture)
vol.py -f memdump.raw windows.info
vol.py -f memdump.raw banners.Banners   # Linux/macOS
```

### Analyse des processus

```bash
# Liste des processus (via EPROCESS doubly-linked list)
vol.py -f memdump.raw windows.pslist

# Liste via PEB (Process Environment Block) — peut révéler des processus cachés
vol.py -f memdump.raw windows.pstree

# Processus cachés (non listés dans EPROCESS — rootkit)
vol.py -f memdump.raw windows.psscan     # scan brut de la mémoire pour trouver des EPROCESS
# Comparer pslist et psscan : tout processus dans psscan mais pas dans pslist est suspect

# Ligne de commande de chaque processus
vol.py -f memdump.raw windows.cmdline

# Variables d'environnement
vol.py -f memdump.raw windows.envars --pid 1234

# DLLs chargées par un processus
vol.py -f memdump.raw windows.dlllist --pid 1234
```

### Réseau

```bash
# Connexions réseau actives et récentes
vol.py -f memdump.raw windows.netstat
# TCP/UDP, sockets en écoute, connexions établies, adresses distantes

vol.py -f memdump.raw windows.netscan    # scan plus complet
```

### Registre Windows en mémoire

```bash
# Lister les ruches chargées
vol.py -f memdump.raw windows.registry.hivelist

# Afficher les clés d'une ruche (par offset)
vol.py -f memdump.raw windows.registry.printkey \
  --offset 0xe1e5c000 \
  --key "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# Extraire une ruche complète
vol.py -f memdump.raw windows.registry.hivescan
```

### Fichiers et handles

```bash
# Fichiers ouverts par les processus
vol.py -f memdump.raw windows.filescan

# Extraire un fichier de la mémoire
vol.py -f memdump.raw windows.dumpfiles --pid 1234
vol.py -f memdump.raw windows.dumpfiles --virtaddr 0xoffset
```

### Analyse de code malveillant

```bash
# Détecter les sections mémoire injections (droits RWX inhabituels, sans fichier associé)
vol.py -f memdump.raw windows.malfind

# malfind cherche des régions mémoire :
# - exécutables (PAGE_EXECUTE_*)
# - sans mapping vers un fichier disque
# - commençant par des en-têtes PE (MZ ou 0x4D 0x5A)

# Extraire le code suspect pour analyse statique
vol.py -f memdump.raw windows.malfind --dump
```

### Dump de processus

```bash
# Extraire l'espace mémoire d'un processus (pour analyse avec IDA, Ghidra, strings)
vol.py -f memdump.raw windows.memmap --pid 1234 --dump

# Dump de l'exécutable (PE reconstruit)
vol.py -f memdump.raw windows.procdump --pid 1234
```

## Techniques de malware en mémoire

| Technique | Description | Détection |
|---|---|---|
| Process Injection | Injection de shellcode dans un processus légitime | `malfind`, anomalies `dlllist` |
| Process Hollowing | Création d'un processus suspendu dont le code est remplacé | PID orphelin, chemin ne correspondant pas |
| DLL Injection | Chargement d'une DLL malveillante via `LoadLibrary` | DLL non signée dans `dlllist` |
| Reflective DLL Injection | DLL se charge elle-même sans passer par le loader Windows | Région MZ sans fichier disque (`malfind`) |
| DKOM (Direct Kernel Object Manipulation) | Déconnexion d'EPROCESS de la liste — processus invisible | `pslist` vs `psscan` divergent |
| Fileless Malware | Code uniquement en mémoire (PowerShell, WMI) | `cmdline`, `malfind`, logs PowerShell |

## Analyse Linux avec Volatility 3

```bash
# Profil Linux (nécessite les symboles du kernel)
vol.py -f memdump.lime linux.bash      # historique bash en mémoire
vol.py -f memdump.lime linux.pslist
vol.py -f memdump.lime linux.netstat
vol.py -f memdump.lime linux.malfind
vol.py -f memdump.lime linux.lsof      # fichiers ouverts
```

## Extraction de secrets

```bash
# Hashes NTLM (Windows — pour Pass-the-Hash ou crackage)
vol.py -f memdump.raw windows.hashdump

# Clés de chiffrement Bitlocker, TrueCrypt
vol.py -f memdump.raw windows.bitlocker

# Mots de passe en mémoire (strings bruts)
strings -el memdump.raw | grep -i "password"   # unicode 16-bit little-endian

# Analyse des artefacts de navigateur en mémoire
vol.py -f memdump.raw windows.filescan | grep -i "chrome\|firefox"
```

## Workflow typique d'analyse

```
1. Identifier l'OS et la version
   → vol.py windows.info

2. Lister les processus et chercher les anomalies
   → pslist + pstree (hiérarchie) + psscan (processus cachés)
   → Vérifier : noms inhabituels, parents inattendus (svchost sous explorer.exe), PID 0/4 suspects

3. Analyser les connexions réseau
   → netstat / netscan
   → Vérifier : connexions vers des IPs externes inconnues, ports inhabituels

4. Examiner les processus suspects
   → cmdline (arguments)
   → dlllist (DLLs chargées)
   → malfind (injections)

5. Chercher la persistance
   → registre (RunKeys), services (svcscan), tâches planifiées

6. Extraire et analyser les artefacts
   → procdump + analyse statique (Ghidra, strings)
   → dumpfiles pour les fichiers suspects
```
