---
title: Cloud Security
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [cloud, aws, azure, gcp, iam, sécurité, pentest, misconfiguration]
date: 2026-03-22
---

# Cloud Security

La sécurité cloud regroupe les pratiques, outils et architectures pour protéger les données, applications et infrastructures hébergées sur des plateformes cloud (AWS, Azure, GCP). Les erreurs de configuration sont la première cause de compromission cloud.

## Modèle de responsabilité partagée

```mermaid
graph TD
    subgraph "Responsabilité du fournisseur"
        physical[Infrastructure physique\ndatacenters, réseau, hardware]
        hypervisor[Hyperviseur\nvirtualisation]
    end

    subgraph "Zone partagée"
        os[Système d'exploitation\nIaaS = client / PaaS = partagé]
        network_ctrl[Contrôles réseau]
    end

    subgraph "Responsabilité du client"
        data[Données\net leur chiffrement]
        iam[Gestion des identités\net accès (IAM)]
        app[Applications]
        config[Configuration\ndes services]
    end

    physical --> hypervisor --> os --> data
```

**Règle clé** : le cloud provider sécurise le cloud, le client sécurise ce qu'il y met.

## Les 12 risques cloud majeurs (CSA)

| # | Risque | Description |
|---|---|---|
| 1 | Insuffisant Identity & Access Management | Credentials volés, permissions excessives |
| 2 | Interfaces et APIs non sécurisées | APIs exposées sans auth |
| 3 | Mauvaises configurations | S3 public, SG trop ouverts |
| 4 | Manque de visibilité | Pas de logs, pas de monitoring |
| 5 | Vol de compte | Phishing, credential stuffing |
| 6 | Menaces internes | Admin malveillant ou négligent |
| 7 | Surfaces d'attaque changeantes | Shadow IT, ressources oubliées |
| 8 | Manque d'architecture de sécurité | Pas de segmentation, flat network |
| 9 | Défaillances de la chaîne d'approvisionnement | Dépendances compromises |
| 10 | Problèmes de conformité | Données dans mauvaise région |
| 11 | Attaques avancées | APT ciblant le cloud |
| 12 | Abus de services cloud | Cryptomining, spam depuis des ressources volées |

## IAM — Gestion des identités et accès

### Principe du moindre privilège

```bash
# AWS — Créer une politique restrictive
aws iam create-policy --policy-name ReadOnlyS3Specific --policy-document '{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::my-bucket",
      "arn:aws:s3:::my-bucket/*"
    ]
  }]
}'

# Mauvais : AdministratorAccess pour une Lambda
# Bien : rôle avec uniquement les permissions nécessaires
```

### Erreurs IAM communes

**Clés AWS exposées dans le code source**
```bash
# Scanner les repos avec git-secrets ou trufflehog
trufflehog github --org=myorg --only-verified
git-secrets --scan-history

# Vérifier si une clé est valide
aws sts get-caller-identity --profile suspect-key
```

**IMDSv1 — Instance Metadata Service (SSRF risk)**
```bash
# Depuis une instance EC2 compromise ou via SSRF :
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
# Retourne les credentials temporaires du rôle attaché

# Solution : forcer IMDSv2 (token requis)
aws ec2 modify-instance-metadata-options \
  --http-tokens required \
  --instance-id i-1234567890abcdef0
```

**Rôles avec trust policy trop larges**
```json
// MAUVAIS — n'importe qui dans le compte peut assumer ce rôle
{
  "Principal": {"AWS": "arn:aws:iam::123456789:root"},
  "Action": "sts:AssumeRole"
}

// BIEN — restreindre au service et condition précise
{
  "Principal": {"Service": "lambda.amazonaws.com"},
  "Action": "sts:AssumeRole",
  "Condition": {
    "StringEquals": {"aws:SourceAccount": "123456789012"}
  }
}
```

## Mauvaises configurations courantes

### S3 — Buckets exposés

```bash
# Découverte de buckets publics
aws s3 ls s3://nom-du-bucket --no-sign-request
# Si succès → bucket public en lecture

# Outils de découverte
s3scanner scan --buckets-file wordlist.txt

# Vérifier la politique d'un bucket
aws s3api get-bucket-policy --bucket mon-bucket
aws s3api get-bucket-acl --bucket mon-bucket

# Bloquer l'accès public (à faire pour tous les buckets)
aws s3api put-public-access-block --bucket mon-bucket \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,\
   BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### Security Groups trop permissifs

```bash
# Trouver les SG avec SSH ouvert à Internet
aws ec2 describe-security-groups \
  --filters "Name=ip-permission.from-port,Values=22" \
             "Name=ip-permission.cidr,Values=0.0.0.0/0" \
  --query 'SecurityGroups[*].[GroupId,GroupName]'

# Idem pour RDP
aws ec2 describe-security-groups \
  --filters "Name=ip-permission.from-port,Values=3389" \
             "Name=ip-permission.cidr,Values=0.0.0.0/0"
```

## Outils d'audit cloud

| Outil | Cloud | Description |
|---|---|---|
| **ScoutSuite** | AWS/Azure/GCP | Audit multi-cloud, dashboard HTML |
| **Prowler** | AWS/Azure/GCP | Vérifications CIS benchmarks, remédiation |
| **Pacu** | AWS | Framework pentest AWS (type Metasploit) |
| **CloudSploit** | Multi | CSPM open source |
| **Checkov** | IaC | Scan Terraform/CloudFormation pour mauvaises configs |
| **SteamPipe** | Multi | SQL sur l'inventaire cloud |
| **CloudMapper** | AWS | Visualisation du réseau AWS |

```bash
# ScoutSuite
scout aws --profile audit-profile --report-dir ./rapport

# Prowler
prowler aws --profile audit-profile --compliance cis_aws_3.0

# Pacu — pentest AWS
python3 pacu.py
> import_keys --profile compromised-profile
> run iam__enum_permissions
> run s3__bucket_finder
```

## Container Security (Docker + Kubernetes)

### Images Docker

```bash
# Scanner les vulnérabilités d'une image
trivy image nginx:latest
grype ubuntu:22.04

# Vérifier la configuration Docker
docker bench for security

# Dockerfile sécurisé
FROM node:18-alpine           # Image minimale
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app
COPY --chown=app:app . .
USER app                      # Ne pas tourner en root
RUN npm ci --only=production
HEALTHCHECK CMD wget -q -O- http://localhost:3000/health
```

### Kubernetes

```bash
# Audit avec kube-bench (CIS Kubernetes Benchmark)
kube-bench run --targets node,master

# Trouver les pods tournant en root
kubectl get pods --all-namespaces -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext.runAsUser}{"\n"}{end}'

# Service Account avec trop de permissions
kubectl auth can-i --list --as=system:serviceaccount:default:my-sa

# Network Policy — isoler les pods
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

## Cloud Pentest — Scénarios types

### Scénario 1 : SSRF → IMDSv1 → Credentials

```
1. XSS/SSRF dans une application web sur EC2
2. curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
3. Récupérer AccessKeyId, SecretAccessKey, Token temporaire
4. aws iam list-attached-role-policies → énumérer les permissions
5. Pivoter vers d'autres services (S3, Lambda, RDS...)
```

### Scénario 2 : Lambda avec variable d'environnement

```bash
# Lister les fonctions Lambda
aws lambda list-functions

# Voir les variables d'environnement (credentials hardcodés ?)
aws lambda get-function-configuration --function-name my-function
# Chercher: DATABASE_PASSWORD, API_KEY, AWS_SECRET_ACCESS_KEY
```

### Scénario 3 : Role chaining (escalade de privilèges IAM)

```bash
# Pacu - énumérer les possibilités d'escalade de privilèges
run iam__privesc_scan

# Manuellement : si AssumeRole est permis
aws sts assume-role \
  --role-arn arn:aws:iam::123456789:role/AdminRole \
  --role-session-name pentest
```

## Détection et surveillance

### CloudTrail — logs API AWS

```bash
# Activer CloudTrail sur toutes les régions
aws cloudtrail create-trail \
  --name global-trail \
  --s3-bucket-name my-cloudtrail-bucket \
  --is-multi-region-trail \
  --include-global-service-events

# Requêtes CloudWatch Logs Insights pour détecter des anomalies
fields @timestamp, eventName, userIdentity.arn, sourceIPAddress
| filter errorCode = "AccessDenied"
| stats count(*) by userIdentity.arn
| sort count desc
```

### GuardDuty (AWS)

Détection d'anomalies managée : accès inhabituels, mining de crypto, reconnaissance.

```bash
aws guardduty create-detector --enable --finding-publishing-frequency FIFTEEN_MINUTES
```

### Alertes critiques à configurer

```
- Root account utilisé
- Console login sans MFA
- CreateAccessKey sur un compte IAM
- S3 public access block désactivé
- Security Group 0.0.0.0/0 sur port 22/3389
- Appel API depuis une IP suspecte (Tor, VPN)
- Pic de coûts (cryptomining)
```

## Chiffrement au repos et en transit

```bash
# S3 — chiffrement serveur obligatoire
aws s3api put-bucket-encryption --bucket mon-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:..."
      },
      "BucketKeyEnabled": true
    }]
  }'

# RDS — chiffrement activé à la création uniquement
aws rds create-db-instance \
  --db-instance-identifier mydb \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:...

# EBS — chiffrement par défaut pour tous les volumes
aws ec2 enable-ebs-encryption-by-default
```
