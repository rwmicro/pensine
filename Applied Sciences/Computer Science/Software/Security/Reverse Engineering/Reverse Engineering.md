---
title: "Reverse Engineering"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-25"
---

# Reverse Engineering

Le reverse engineering (rétro-ingénierie) est l'analyse d'un binaire compilé pour comprendre son fonctionnement sans accès au code source. En sécurité, il sert à analyser des malwares, trouver des vulnérabilités, casser des protections, et valider le comportement d'un logiciel.

## Format des exécutables

### PE (Portable Executable) — Windows

```
┌──────────────────────────────────┐
│  DOS Header (MZ)                 │ ← Magic "MZ" (0x4D5A)
├──────────────────────────────────┤
│  DOS Stub                        │ ← "This program cannot be run in DOS mode"
├──────────────────────────────────┤
│  PE Header (PE\0\0)              │ ← Magic "PE" (0x5045 0000)
├──────────────────────────────────┤
│  COFF File Header                │ ← Machine, nb sections, timestamps
├──────────────────────────────────┤
│  Optional Header                 │ ← EntryPoint, ImageBase, taille
├──────────────────────────────────┤
│  Section Table                   │
│  ├── .text (code)                │ ← RX (Read/Execute)
│  ├── .data (données initialisées)│ ← RW (Read/Write)
│  ├── .rdata (données en lecture) │ ← R  (imports, strings)
│  ├── .rsrc (ressources)          │ ← icônes, manifests
│  └── .reloc (relocations)        │
├──────────────────────────────────┤
│  Sections (contenu)              │
└──────────────────────────────────┘
```

```bash
# Inspecter un PE avec pe-bear, CFF Explorer, ou en ligne de commande
python3 -c "
import pefile
pe = pefile.PE('malware.exe')
print('EntryPoint :', hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint))
print('ImageBase  :', hex(pe.OPTIONAL_HEADER.ImageBase))
for section in pe.sections:
    print(section.Name.decode().strip(), hex(section.VirtualAddress), section.SizeOfRawData)
"

# Extraire les imports (DLLs et fonctions appelées)
python3 -c "
import pefile
pe = pefile.PE('malware.exe')
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    print(entry.dll.decode())
    for imp in entry.imports:
        print('  ', imp.name.decode() if imp.name else hex(imp.ordinal))
"
```

### ELF (Executable and Linkable Format) — Linux

```bash
# Informations générales
file binaire
readelf -h binaire           # en-tête ELF
readelf -S binaire           # sections
readelf -d binaire           # dynamic section (dépendances)
objdump -d binaire           # désassemblage
strings binaire | head -50   # chaînes de caractères
nm binaire                   # symboles
ldd binaire                  # bibliothèques dynamiques
```

## Analyse statique

L'analyse statique examine le binaire sans l'exécuter.

### strings — extraction des chaînes

```bash
# Chaînes ASCII et Unicode
strings malware.exe
strings -el malware.exe    # Unicode 16-bit little-endian (Windows)
strings -eb malware.exe    # Unicode 16-bit big-endian

# Filtrer ce qui est intéressant
strings malware.exe | grep -iE "http|https|cmd|powershell|registry|password|token|key"
strings malware.exe | grep -E "^[A-Za-z0-9+/]{20,}={0,2}$"  # base64
```

### Ghidra (NSA — open source)

Ghidra est le décompilateur open source de référence. Il reconstitue du pseudo-code C à partir du binaire.

```
1. Créer un projet → importer le binaire
2. Auto-analyse (accepter les paramètres par défaut)
3. Navigation :
   - Symbol Tree → fonctions, imports, exports
   - Listing → vue assembleur
   - Decompiler → pseudo-code C (panneau droit)
4. Renommer les variables et fonctions pour clarifier (touche L)
5. Chercher les références croisées (clic droit → References)
```

```
Exemple de décompilation Ghidra :

Assembleur :
push ebp
mov ebp, esp
sub esp, 8
mov eax, [ebp+arg_0]
test eax, eax
jz short exit
...

Pseudo-code C :
void fonction(char *param) {
    if (param == NULL) return;
    ...
}
```

### IDA Free / IDA Pro

IDA est le standard industriel (payant), IDA Free est disponible pour les binaires x86/x64 jusqu'à une certaine taille.

```
Raccourcis essentiels :
G   : aller à une adresse
N   : renommer un symbole
:   : ajouter un commentaire
X   : références croisées (xrefs)
F5  : décompilateur Hex-Rays (IDA Pro) / pseudo-code
Space : basculer entre vue graphe et listing
```

### radare2 / Cutter

```bash
# Analyse en ligne de commande
r2 -A malware.exe      # ouvrir et analyser automatiquement
[0x00401000]> afl      # lister les fonctions
[0x00401000]> pdf @ main   # désassembler main
[0x00401000]> iz       # lister les chaînes de caractères
[0x00401000]> ii       # imports
[0x00401000]> s 0x401234 ; pdf  # aller à une adresse et désassembler

# Cutter = interface graphique de radare2
```

### Entropie et packing

Les packers (UPX, Themida, MPRESS) compressent/chiffrent le code pour contrer l'analyse.

```bash
# Détecter le packing via l'entropie (>7.0 = suspect)
python3 -c "
import math, pefile
pe = pefile.PE('malware.exe')
for section in pe.sections:
    data = section.get_data()
    freq = [data.count(bytes([i])) for i in range(256)]
    entropy = -sum(f/len(data) * math.log2(f/len(data)) for f in freq if f)
    print(f'{section.Name.decode().strip():10} entropy: {entropy:.2f}')
"

# Détecter le packer
die malware.exe        # Detect-it-Easy
exeinfope malware.exe

# Décompresser UPX
upx -d malware_upx.exe -o malware_unpacked.exe
```

## Analyse dynamique

L'analyse dynamique exécute le binaire dans un environnement contrôlé pour observer son comportement.

### Sandbox

Environnement isolé qui capture le comportement sans risquer l'hôte.

| Sandbox | Type | URL |
|---|---|---|
| Any.run | En ligne, interactif | any.run |
| Joe Sandbox | En ligne | joesandbox.com |
| Cuckoo Sandbox | Self-hosted | github.com/cuckoosandbox |
| Hybrid Analysis | En ligne | hybrid-analysis.com |

```bash
# Cuckoo — soumettre un sample
cuckoo submit malware.exe
cuckoo submit --timeout 120 --package doc malware.docm
# Rapport disponible dans l'interface web : http://localhost:8080
```

### x64dbg / x32dbg — débogage dynamique

x64dbg est le débogueur open source de référence pour Windows.

```
Actions essentielles :
F2    : poser/supprimer un breakpoint sur la ligne courante
F7    : step into (entrer dans la fonction appelée)
F8    : step over (exécuter l'appel sans y entrer)
F9    : run (jusqu'au prochain breakpoint)
Ctrl+G : aller à une adresse

Stratégie d'analyse :
1. Poser un breakpoint sur les APIs suspectes
   (CreateFile, WriteFile, RegSetValue, CreateProcess, URLDownloadToFile)
   → Run → Observer les arguments au moment de l'appel
2. Identifier le OEP (Original Entry Point) après unpacking en mémoire
3. Dumper le binaire unpacké depuis la mémoire
```

### API Monitor

Capture tous les appels d'API Windows d'un processus en temps réel : fichiers créés, clés de registre modifiées, connexions réseau, processus enfants.

### Procmon (Process Monitor — Sysinternals)

```
Filtres recommandés pour l'analyse malware :
- Process Name is malware.exe
- Operation contains : CreateFile, WriteFile, RegSetValue, RegDeleteValue,
  TCP Connect, TCP Send, CreateProcess
```

## Assembleur x86-64 — bases

```nasm
; Registres généraux x86-64
; 64 bits : RAX, RBX, RCX, RDX, RSI, RDI, RSP, RBP, R8-R15
; 32 bits : EAX, EBX, ECX, EDX...
; 16 bits :  AX,  BX,  CX,  DX...
; 8  bits :  AL/AH, BL/BH...

; Convention d'appel System V AMD64 (Linux)
; Paramètres : RDI, RSI, RDX, RCX, R8, R9, puis stack
; Retour : RAX

; Convention d'appel Windows x64
; Paramètres : RCX, RDX, R8, R9, puis stack
; Retour : RAX

; Instructions essentielles
mov rax, 42          ; rax ← 42
mov rax, [rbp-8]     ; rax ← valeur à l'adresse rbp-8 (mémoire)
push rax             ; empiler rax sur la pile (RSP -= 8)
pop rbx              ; dépiler dans rbx (RSP += 8)
call fonction        ; push RIP, jmp fonction
ret                  ; pop RIP (retour)
lea rax, [rbp-0x10]  ; rax ← adresse de rbp-0x10 (load effective address)

; Arithmétique
add rax, rbx         ; rax += rbx
sub rax, 4           ; rax -= 4
xor rax, rax         ; rax = 0 (idiome courant)
test rax, rax        ; AND sans écriture (positionne les flags)
cmp rax, 5           ; soustraction sans écriture (positionne les flags)

; Branchements
je  adresse          ; jump if equal (ZF=1)
jne adresse          ; jump if not equal
jg  adresse          ; jump if greater (signé)
jl  adresse          ; jump if less (signé)
jmp adresse          ; saut inconditionnel
```

## Techniques anti-reversing

```
Anti-debugging :
- IsDebuggerPresent() API
- CheckRemoteDebuggerPresent()
- NtQueryInformationProcess (ProcessDebugPort)
- Timing checks : RDTSC, GetTickCount
- TLS callbacks (exécutés avant le point d'entrée)

Anti-VM :
- Détecter VMware/VirtualBox via registre, drivers, CPUID
- Vérifier la présence d'outils d'analyse (procmon.exe, wireshark.exe)
- Nombre de CPUs (VM souvent à 1-2)
- Température des capteurs (absente en VM)

Obfuscation :
- Chaînes chiffrées (XOR, RC4, AES) déchiffrées à l'exécution
- Import hashing : calculer le hash des noms d'API pour les résoudre dynamiquement
- Code polymorphique : le code se réécrit à chaque exécution
- Packing : compression + chiffrement du code
- Control flow flattening : remplacer les if/while par un switch géant
```

## Workflow d'analyse malware

```
1. Analyse statique initiale (5 min)
   strings, imports, entropie, signature AV (VirusTotal)

2. Analyse comportementale en sandbox (15 min)
   Any.run ou Cuckoo : IOCs automatiques (IPs, domaines, fichiers, registry)

3. Analyse statique approfondie (variable)
   Ghidra/IDA : décompiler, identifier les fonctions principales

4. Analyse dynamique ciblée (variable)
   x64dbg : déboguer les fonctions suspectes identifiées à l'étape 3
   Se concentrer sur le déchiffrement des C2, les mécanismes de persistance

5. Extraction des IOCs
   - Hashes (MD5, SHA1, SHA256)
   - IPs et domaines C2
   - User-agents réseau
   - Chemins de fichiers créés
   - Clés de registre
   - Mutex
   → Documenter dans MISP ou un rapport
```

## Techniques Anti-Analyse et leur Contournement

Les malwares modernes implémentent des défenses contre l'analyse. Comprendre ces techniques est essentiel pour les contourner.

### Anti-débogage

**Détection du débogueur :**

```c
// IsDebuggerPresent (Windows API)
if (IsDebuggerPresent()) ExitProcess(0);

// PEB.BeingDebugged (accès direct)
// Contournement : patcher le byte BeingDebugged à 0 dans x64dbg
// Options → Preferences → Engine → "Skip IsDebuggerPresent checks"

// CheckRemoteDebuggerPresent
BOOL isDebug;
CheckRemoteDebuggerPresent(GetCurrentProcess(), &isDebug);

// NtQueryInformationProcess
NTSTATUS status = NtQueryInformationProcess(
    GetCurrentProcess(),
    ProcessDebugPort,  // 0x7
    &debugPort,
    sizeof(debugPort), NULL
);
// debugPort != 0 → débogueur présent
```

**Contournement dans x64dbg :**
```
Options → Preferences → Engine :
✓ Skip "IsDebuggerPresent"
✓ Skip "CheckRemoteDebuggerPresent"

Plugin ScyllaHide → patch transparent de toutes les vérifications
```

**Timing attacks (détection par mesure du temps) :**
```c
// RDTSC : mesure le temps entre deux instructions
// Si trop long → présence d'un débogueur

LARGE_INTEGER t1, t2;
QueryPerformanceCounter(&t1);
// code court
QueryPerformanceCounter(&t2);
if ((t2.QuadPart - t1.QuadPart) > THRESHOLD) ExitProcess(0);

// Contournement : patcher les appels RDTSC pour retourner une valeur fixe
// x64dbg → Options → "Fix RDTSC"
```

**Exception-based anti-debug :**
```c
// Les débogueurs gèrent les exceptions différemment
__try {
    __asm int 3  // Breakpoint
} __except(EXCEPTION_EXECUTE_HANDLER) {
    // Si on arrive ici → pas de débogueur (l'exception est gérée normalement)
    // Si le débogueur intercepte → le code ne passe pas ici
}
```

### Anti-VM et Anti-Sandbox

```c
// Vérification de la présence d'une VM (VMware, VirtualBox)

// CPUID instruction
__asm {
    push eax
    push ecx
    mov eax, 1
    cpuid
    // ECX bit 31 = hypervisor présent
    test ecx, 0x80000000
    jnz in_vm
    pop ecx
    pop eax
}

// Recherche d'artefacts VMware dans le registre
RegOpenKey(HKLM, "SOFTWARE\\VMware, Inc.\\VMware Tools", &key)
// Si clé existe → VM

// Recherche de processus sandbox courants
const char* sandbox_processes[] = {
    "vmsrvc.exe",    // VMware
    "vboxservice.exe", // VirtualBox
    "sandboxie.exe",
    "wireshark.exe",   // Monitoring
    "processhacker.exe",
    "x64dbg.exe"
};
```

**Contournement :**
- Utiliser des sandboxes "renforcées" avec artefacts mimant un vrai PC (FlareVM, CAPE)
- Modifier les chaînes de caractères identifiables dans la VM
- Utiliser une vraie machine physique (bare-metal) pour l'analyse

**Comportements sandbox-aware :**
```c
// Attendre avant d'agir (éviter le timeout sandbox)
Sleep(300000);  // 5 minutes → sandbox s'arrête souvent avant

// Vérifier l'interaction humaine (sandbox = pas de souris)
POINT cursor;
GetCursorPos(&cursor);
Sleep(10000);
GetCursorPos(&cursor2);
if (cursor.x == cursor2.x && cursor.y == cursor2.y) {
    // Pas de mouvement de souris → probablement une sandbox
}

// Vérifier le nombre de processus (sandbox en a moins)
// Vérifier la RAM (sandbox souvent < 2GB)
// Vérifier la résolution écran (sandbox souvent 800×600)
```

### Obfuscation et Unpacking

**Packing détection :**
```bash
# Entropy élevée (>7.0) → probablement packé
die application.exe        # Detect It Easy
exeinfo pe application.exe

# Entrée unique, peu de sections, section d'entrée exécutable + writable
# → indicateurs de packer
```

**Unpacking manuel (x64dbg) :**
```
Stratégie "OEP hunting" :
1. Poser un hardware breakpoint sur le point d'entrée (EP)
2. F9 (Run) → le packer se décompresse en mémoire
3. Observer les sauts vers une nouvelle région mémoire (OEP = Original Entry Point)
4. Dumper la mémoire une fois à l'OEP (Scylla → Dump)
5. Reconstruire l'IAT (Import Address Table) → Scylla → Fix Dump
```

**Self-modifying code :**
```
Le malware modifie ses propres instructions à l'exécution.
Contournement :
- Utiliser des hardware breakpoints (pas affectés par les modifications du code)
- Poser des watchpoints sur les sections modifiées
- Breakpoint sur VirtualProtect (rend une section exécutable)
```

### Code Injection et Process Hollowing

Techniques pour exécuter du code malveillant dans le contexte d'un processus légitime.

```c
// Process Hollowing — détecter en dynamique
// 1. CreateProcess en mode suspendu
CreateProcess("svchost.exe", ..., CREATE_SUSPENDED, ...);
// 2. Unmapper l'image légitime
NtUnmapViewOfSection(hProcess, baseAddr);
// 3. Allouer et écrire le malware
VirtualAllocEx(hProcess, ...);
WriteProcessMemory(hProcess, ...);
// 4. Reprendre l'exécution
ResumeThread(hThread);

// Détection dans Procmon :
// CreateProcess → NtUnmapViewOfSection → VirtualAllocEx → WriteProcessMemory
// Séquence anormale pour un processus légitime
```

**Process Injection variantes à connaître :**
```
DLL Injection : CreateRemoteThread → LoadLibrary
Thread Hijacking : suspendre un thread, modifier son contexte (RIP), reprendre
APC Injection : QueueUserAPC → exécuté au prochain appel alertable
Atom Bombing : GlobalAddAtom + APCs (contourne certaines protections)
Process Doppelgänging : NTFS transactions + process hollowing
Ghostwriting : injection via sections mappées
```

### Chiffrement du C2 et DGA

```python
# DGA (Domain Generation Algorithm) — détection
# Le malware génère des centaines de domaines quotidiennement
# Il essaie chacun jusqu'à trouver celui que l'attaquant a enregistré

def dga_example(seed, date):
    import hashlib
    domains = []
    for i in range(1000):
        h = hashlib.md5(f"{seed}{date}{i}".encode()).hexdigest()
        domain = h[:16] + ".com"
        domains.append(domain)
    return domains

# Détection DGA :
# - Requêtes DNS vers des domaines à entropie élevée
# - Domaines avec NXDOMAIN en masse
# - Modèles de nommage algorithmiques (pas de mots lisibles)
```

**Chiffrement des communications C2 :**
```bash
# Identifier les algorithmes de chiffrement dans le binaire
# Chercher des constantes connues dans Ghidra/IDA
# AES S-box : 0x63, 0x7c, 0x77, 0x7b, 0xf2...
# RC4 : algorithme de permutation simple → repérable à l'analyse

# Décrypter les communications : poser un BP sur les fonctions de déchiffrement
# intercepter les paramètres → obtenir le plaintext avant le chiffrement
```
