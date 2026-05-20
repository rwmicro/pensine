---
title: "AWS S3 — Buckets"
domain: "Applied Sciences"
subdomain: "Computer Science > AWS"
tags: [sciences-appliquées, informatique, aws]
date: "2024-09-13"
---

# AWS S3 — Buckets

Amazon S3 (Simple Storage Service) est un service de stockage d'objets dans le cloud. Un **bucket** est le conteneur de base dans S3 — comme un dossier racine dans lequel on met des fichiers (appelés "objets").


## Concepts de base

| Terme | Description |
|-------|-------------|
| **Bucket** | Conteneur de stockage (nom unique mondial) |
| **Object** | Fichier stocké dans S3 (jusqu'à 5 TB par objet) |
| **Key** | Chemin/nom de l'objet dans le bucket |
| **Region** | Zone géographique où est stocké le bucket |


## Créer un bucket (Console AWS)

1. AWS Console → S3 → "Create bucket"
2. Choisir un nom unique (minuscules, pas d'espaces)
3. Choisir une région
4. Configurer l'accès (par défaut : tout bloqué)
5. Créer


## Opérations avec AWS CLI

```bash
# Configurer les credentials
aws configure

# Lister les buckets
aws s3 ls

# Créer un bucket
aws s3 mb s3://mon-bucket-nom

# Uploader un fichier
aws s3 cp fichier.txt s3://mon-bucket/
aws s3 cp fichier.txt s3://mon-bucket/dossier/fichier.txt

# Uploader un dossier entier
aws s3 sync ./dossier/ s3://mon-bucket/dossier/

# Télécharger
aws s3 cp s3://mon-bucket/fichier.txt ./

# Lister le contenu d'un bucket
aws s3 ls s3://mon-bucket/

# Supprimer un objet
aws s3 rm s3://mon-bucket/fichier.txt

# Supprimer un bucket (doit être vide)
aws s3 rb s3://mon-bucket
aws s3 rb s3://mon-bucket --force   # Force la suppression avec contenu
```


## Avec le SDK JavaScript (v3)

```javascript
import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3"

const client = new S3Client({ region: "eu-west-1" })

// Upload
const upload = await client.send(new PutObjectCommand({
  Bucket: "mon-bucket",
  Key: "dossier/fichier.txt",
  Body: "contenu du fichier",
  ContentType: "text/plain"
}))

// Download
const response = await client.send(new GetObjectCommand({
  Bucket: "mon-bucket",
  Key: "dossier/fichier.txt"
}))
const content = await response.Body.transformToString()
```

Documentation complète : [AWS SDK JS v3 S3](https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/javascript_s3_code_examples.html)


## Gestion des accès

### Bucket Policy (JSON)
Contrôle qui peut accéder au bucket.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::mon-bucket/*"
  }]
}
```
→ Rend tous les objets publics en lecture.

### IAM Roles
Méthode recommandée pour les applications AWS — pas de clés dans le code.


## Fonctionnalités utiles

| Fonctionnalité | Description |
|----------------|-------------|
| **Versioning** | Garde toutes les versions d'un objet |
| **Lifecycle Rules** | Archive ou supprime auto les objets anciens |
| **Replication** | Copie vers un autre bucket/région |
| **Static Website** | Héberger un site statique directement depuis S3 |
| **Presigned URLs** | URL temporaire pour accès privé sans auth |
| **Transfer Acceleration** | Upload plus rapide via CloudFront |
