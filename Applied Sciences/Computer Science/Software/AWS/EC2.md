---
title: "EC2 — Elastic Compute Cloud"
domain: "Applied Sciences"
subdomain: "Computer Science > AWS"
tags: [sciences-appliquées, informatique, aws]
date: "2026-02-25"
---

# EC2 — Elastic Compute Cloud

EC2 est le service de machines virtuelles d'AWS. Il fournit des serveurs à la demande avec une grande variété de configurations matérielles.

## Types d'instances

Les instances sont organisées en familles selon leur usage.

| Famille | Optimisation | Exemples | Cas d'usage |
|---|---|---|---|
| t (Burstable) | Généraliste, crédit CPU | t3.micro, t3.medium | Dev, sites à trafic variable |
| m (General Purpose) | Équilibre CPU/RAM | m6i.large, m7g.xlarge | Applications web, BDD légères |
| c (Compute) | CPU haute performance | c6i.4xlarge, c7g.2xlarge | Encodage vidéo, calcul scientifique |
| r (Memory) | RAM importante | r6i.8xlarge, r7g.16xlarge | BDD in-memory, caches, Elasticsearch |
| g/p (GPU) | GPU NVIDIA | g4dn.xlarge, p4d.24xlarge | Machine Learning, rendu 3D |
| i (Storage) | I/O NVMe local | i3.large, i4i.8xlarge | BDD haute performance, Cassandra |
| d (Dense Storage) | HDD dense | d3.8xlarge | Data warehouses, Hadoop |
| x (Extended Memory) | RAM extrême | x2idn.32xlarge (4 To RAM) | SAP HANA, bases en mémoire |
| inf (Inferentia) | Inférence ML | inf2.xlarge | Déploiement de modèles ML |

**Notation** : `type.taille` ex: `m6i.xlarge`
- `m` : famille
- `6` : génération
- `i` : processeur Intel (a=AMD, g=Graviton/ARM, n=NVMe)
- `xlarge` : taille (nano < micro < small < medium < large < xlarge < 2xlarge...)

## AMI — Amazon Machine Image

Une AMI est un modèle contenant le système d'exploitation, les logiciels, les configurations et les données de démarrage nécessaires à une instance EC2.

```bash
# Lister les AMIs Ubuntu 24.04 officielles
aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-noble-24.04-amd64-server-*" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text

# Créer une AMI depuis une instance existante
aws ec2 create-image \
    --instance-id i-1234567890abcdef0 \
    --name "Mon-App-v2.1" \
    --description "AMI de production avec app v2.1"
```

## Cycle de vie d'une instance

```
launch
  │
  ▼
pending → running → stopping → stopped → starting → running
              │
              └── shutting-down → terminated
```

**stopped** : instance arrêtée, RAM effacée, CPU libéré. Le stockage EBS persiste. Facturation EBS seule (pas CPU/RAM). Peut être redémarrée.

**terminated** : instance supprimée définitivement. Volume EBS root supprimé par défaut.

```bash
# Lancer une instance
aws ec2 run-instances \
    --image-id ami-0123456789abcdef0 \
    --instance-type t3.medium \
    --key-name ma-cle-ssh \
    --security-group-ids sg-12345 \
    --subnet-id subnet-12345 \
    --iam-instance-profile Name=MonProfil \
    --user-data file://script-init.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=mon-serveur}]'

# Arrêter / Démarrer / Terminer
aws ec2 stop-instances --instance-ids i-1234567890
aws ec2 start-instances --instance-ids i-1234567890
aws ec2 terminate-instances --instance-ids i-1234567890

# Lister les instances
aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
    --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,PublicIpAddress,Tags[?Key==`Name`].Value|[0]]' \
    --output table
```

## EBS — Elastic Block Store

Volumes de stockage persistants attachés aux instances EC2.

| Type | Usage | IOPS max | Débit max |
|---|---|---|---|
| gp3 (SSD généraliste) | Défaut recommandé | 16 000 | 1 000 Mo/s |
| gp2 (SSD généraliste) | Ancien standard | 16 000 | 250 Mo/s |
| io2 Block Express | BDD critiques | 256 000 | 4 000 Mo/s |
| st1 (HDD séquentiel) | Logs, Kafka | 500 | 500 Mo/s |
| sc1 (HDD froid) | Archives | 250 | 250 Mo/s |

```bash
# Créer un volume EBS
aws ec2 create-volume \
    --volume-type gp3 \
    --size 100 \
    --availability-zone eu-west-1a \
    --iops 6000 \
    --throughput 500

# Attacher à une instance
aws ec2 attach-volume \
    --volume-id vol-1234567890 \
    --instance-id i-1234567890 \
    --device /dev/sdf

# Snapshot (sauvegarde ponctuelle)
aws ec2 create-snapshot \
    --volume-id vol-1234567890 \
    --description "Backup avant migration"
```

## Security Groups

Les Security Groups sont des firewalls virtuels stateful associés aux instances.

**Stateful** : si une connexion sortante est autorisée, la réponse entrante est automatiquement autorisée (et vice versa). Différent des NACLs (stateless).

```bash
# Créer un Security Group
aws ec2 create-security-group \
    --group-name sg-app-web \
    --description "SG pour serveurs web" \
    --vpc-id vpc-12345

# Autoriser le trafic entrant
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345 \
    --protocol tcp --port 443 --cidr 0.0.0.0/0  # HTTPS depuis partout

aws ec2 authorize-security-group-ingress \
    --group-id sg-12345 \
    --protocol tcp --port 22 --cidr 10.0.0.0/8  # SSH depuis réseau privé seulement

aws ec2 authorize-security-group-ingress \
    --group-id sg-app \
    --protocol tcp --port 8080 \
    --source-group sg-alb    # Autoriser uniquement depuis l'ALB (par SG)
```

## Auto Scaling Groups (ASG)

Ajuste automatiquement le nombre d'instances selon la charge.

```bash
# Créer un Launch Template (modèle de configuration)
aws ec2 create-launch-template \
    --launch-template-name mon-template \
    --version-description "v1" \
    --launch-template-data '{
        "ImageId": "ami-12345",
        "InstanceType": "t3.medium",
        "SecurityGroupIds": ["sg-12345"],
        "IamInstanceProfile": {"Name": "MonProfil"}
    }'

# Créer l'ASG
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name mon-asg \
    --launch-template "LaunchTemplateName=mon-template,Version=$Latest" \
    --min-size 2 \
    --max-size 10 \
    --desired-capacity 3 \
    --vpc-zone-identifier "subnet-abc,subnet-def" \
    --target-group-arns arn:aws:elasticloadbalancing:...
```

**Scaling Policies** :
- **Target Tracking** : maintenir une métrique (ex: CPU à 70%)
- **Step Scaling** : ajouter/supprimer N instances selon des seuils
- **Scheduled** : scaling à heures fixes (ex: augmenter la nuit pour les jobs batch)

## Load Balancers

| Type | Couche OSI | Usage |
|---|---|---|
| ALB (Application LB) | 7 (HTTP/HTTPS) | Routing par chemin/host, WebSockets |
| NLB (Network LB) | 4 (TCP/UDP) | Haute performance, IP fixe, gaming |
| CLB (Classic LB) | 4 et 7 | Legacy, ne plus utiliser |
| GWLB (Gateway LB) | 3 | Appliances réseau (firewall, IDS) |

```bash
# Créer un ALB
aws elbv2 create-load-balancer \
    --name mon-alb \
    --subnets subnet-abc subnet-def \
    --security-groups sg-alb \
    --scheme internet-facing \
    --type application

# Créer un Target Group
aws elbv2 create-target-group \
    --name mes-instances \
    --protocol HTTP \
    --port 8080 \
    --vpc-id vpc-12345 \
    --health-check-path /health \
    --health-check-interval-seconds 30

# Créer un listener
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:... \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=arn:aws:acm:... \
    --default-actions Type=forward,TargetGroupArn=arn:aws:...
```

## User Data

Script exécuté au premier démarrage de l'instance.

```bash
#!/bin/bash
# /etc/user-data.sh — Installation automatique au démarrage
set -euo pipefail

# Mise à jour
apt-get update -y
apt-get upgrade -y

# Installation de dépendances
apt-get install -y python3 python3-pip nginx

# Récupération du code depuis S3
aws s3 cp s3://mon-bucket/app.tar.gz /tmp/
tar -xzf /tmp/app.tar.gz -C /opt/

# Démarrage du service
systemctl enable --now mon-app
systemctl enable --now nginx
```

## Metadata Service (IMDS)

Chaque instance peut interroger ses propres métadonnées sans credentials.

```bash
# IMDSv2 (recommandé — protège contre les attaques SSRF)
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Récupérer l'ID de l'instance
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/instance-id

# Récupérer les credentials IAM du rôle attaché
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/iam/security-credentials/MON_ROLE
```

## Modèles de tarification

| Modèle | Description | Économie vs On-Demand |
|---|---|---|
| On-Demand | Payer à l'heure, aucun engagement | 0% |
| Reserved (1 an) | Engagement 1 an | ~40% |
| Reserved (3 ans) | Engagement 3 ans | ~60% |
| Savings Plans | Engagement en $/h, flexible | ~40-60% |
| Spot | Instances disponibles à la demande du marché | ~60-90% mais interruptibles |
| Dedicated Host | Serveur physique dédié | Variable |

**Spot Instances** : instances interruptibles avec 2 minutes de préavis. Idéales pour les workloads tolérants aux interruptions : calcul scientifique, rendering, Big Data, CI/CD.
