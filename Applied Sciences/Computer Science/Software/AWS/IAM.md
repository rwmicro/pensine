---
title: "IAM — Identity and Access Management"
domain: "Applied Sciences"
subdomain: "Computer Science > AWS"
tags: [sciences-appliquées, informatique, aws]
date: "2026-02-25"
---

# IAM — Identity and Access Management

IAM est le service AWS de gestion des identités et des accès. Il définit qui peut faire quoi sur quelles ressources AWS.

## Concepts fondamentaux

### Principe du moindre privilège

N'accorder que les permissions strictement nécessaires pour accomplir une tâche. Pas de wildcards `*` en production sauf si réellement nécessaire.

### Principe du zero trust

Ne jamais faire confiance implicitement, même à l'intérieur du réseau. Vérifier chaque accès.

## Entités IAM

### Utilisateurs (Users)

Représentent des personnes ou des applications ayant besoin d'un accès à long terme. Chaque utilisateur a des credentials permanents (mot de passe + clés d'accès).

```bash
# Créer un utilisateur
aws iam create-user --user-name alice

# Créer des clés d'accès (accès programmatique)
aws iam create-access-key --user-name alice

# Lister les utilisateurs
aws iam list-users
```

**Bonne pratique** : ne pas utiliser le compte root AWS pour le travail quotidien. Créer un utilisateur IAM avec les permissions nécessaires. Activer MFA sur le compte root.

### Groupes (Groups)

Regroupent des utilisateurs pour leur attribuer des permissions communes.

```bash
aws iam create-group --group-name Developpeurs
aws iam add-user-to-group --user-name alice --group-name Developpeurs
aws iam attach-group-policy \
    --group-name Developpeurs \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

### Rôles (Roles)

Les rôles sont des identités IAM sans credentials permanents. Une entité (service AWS, utilisateur, compte externe) assume temporairement un rôle et reçoit des credentials éphémères (15 min à 12h).

**Cas d'usage principaux** :
- EC2 accède à S3 sans stocker de clés dans l'instance
- Lambda accède à DynamoDB
- Un compte AWS assume un rôle dans un autre compte (cross-account)
- Fédération d'identité (SAML, OIDC pour SSO)

```bash
# Assumer un rôle (cross-account ou élévation de privilèges)
aws sts assume-role \
    --role-arn arn:aws:iam::123456789012:role/MonRole \
    --role-session-name ma-session

# Résultat : credentials temporaires (AccessKeyId + SecretAccessKey + SessionToken)
```

### Service Accounts

Identités utilisées par des services AWS (EC2, Lambda, ECS) pour interagir avec d'autres services AWS. Implémentés via des rôles attachés à la ressource.

## Politiques IAM (Policies)

Une politique est un document JSON définissant les permissions.

### Structure d'une politique

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "IdentifiantOptionnelDeLaRegle",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::mon-bucket/*",
      "Condition": {
        "StringEquals": {
          "s3:prefix": ["uploads/"]
        }
      }
    },
    {
      "Effect": "Deny",
      "Action": "s3:DeleteObject",
      "Resource": "*"
    }
  ]
}
```

**Effect** : `Allow` ou `Deny`. Un `Deny` explicite l'emporte toujours sur un `Allow`.

**Action** : opérations AWS au format `service:operation`. Wildcards possibles : `s3:*`, `ec2:Describe*`.

**Resource** : ARN (Amazon Resource Name) de la ressource. Format : `arn:partition:service:region:account-id:resource`.

**Condition** : restreindre selon le contexte (IP source, heure, tags, MFA requis, etc.).

### Exemples de politiques commentées

**Accès S3 à un bucket spécifique avec condition** :

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::mon-bucket-prod",
        "arn:aws:s3:::mon-bucket-prod/*"
      ]
    },
    {
      "Effect": "Deny",
      "Action": "s3:*",
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

**Politique de rôle EC2 pour accès DynamoDB** :

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:eu-west-1:123456789012:table/MaTable"
    }
  ]
}
```

**Trust Policy d'un rôle** (qui peut assumer ce rôle) :

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Types de politiques

| Type | Attaché à | Usage |
|---|---|---|
| Politiques gérées AWS | Utilisateur, groupe, rôle | Politiques standard AWS (ex: AdministratorAccess) |
| Politiques gérées client | Utilisateur, groupe, rôle | Politiques personnalisées réutilisables |
| Politiques inline | Une entité spécifique | Permission très spécifique à une entité |
| Politiques de ressource | La ressource (S3, SQS, KMS) | Contrôle depuis la ressource |
| SCPs (Service Control Policies) | Comptes AWS Organizations | Garde-fous au niveau organisation |

## STS — Security Token Service

AWS STS génère des credentials temporaires.

```bash
# Obtenir l'identité courante
aws sts get-caller-identity

# Assumer un rôle
CREDS=$(aws sts assume-role \
    --role-arn arn:aws:iam::COMPTE:role/ROLE \
    --role-session-name session-$(date +%s) \
    --duration-seconds 3600)

export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r .Credentials.AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r .Credentials.SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r .Credentials.SessionToken)
```

## MFA — Multi-Factor Authentication

```bash
# Activer MFA virtuel pour un utilisateur
aws iam create-virtual-mfa-device \
    --virtual-mfa-device-name mon-mfa \
    --outfile /tmp/qrcode.png \
    --bootstrap-method QRCodePNG

aws iam enable-mfa-device \
    --user-name alice \
    --serial-number arn:aws:iam::COMPTE:mfa/mon-mfa \
    --authentication-code1 123456 \
    --authentication-code2 654321
```

## IAM Access Analyzer

Identifie les ressources accessibles depuis l'extérieur du compte (S3 publics, rôles cross-account, politiques trop permissives).

```bash
aws accessanalyzer list-analyzers
aws accessanalyzer list-findings --analyzer-arn arn:aws:...
```

## Politiques de mots de passe

```bash
aws iam update-account-password-policy \
    --minimum-password-length 14 \
    --require-symbols \
    --require-numbers \
    --require-uppercase-characters \
    --require-lowercase-characters \
    --allow-users-to-change-password \
    --max-password-age 90 \
    --password-reuse-prevention 5
```

## Bonnes pratiques

| Pratique | Raison |
|---|---|
| Ne jamais utiliser le root pour le travail | Accès illimité, intraçable |
| MFA sur tous les comptes humains | Protection contre la compromission |
| Rôles plutôt que clés d'accès pour les services | Pas de credentials long terme à gérer |
| Rotation régulière des clés d'accès | Limiter l'impact en cas de fuite |
| Politiques restrictives avec conditions | Principe du moindre privilège |
| CloudTrail activé | Audit de toutes les actions IAM |
| Utiliser AWS Organizations + SCPs | Garde-fous multi-comptes |
| Tagger les ressources IAM | Faciliter l'audit et la gestion |
