---
title: "AWS (Amazon Web Services)"
domain: "Applied Sciences"
subdomain: "Computer Science > AWS"
tags: [sciences-appliquées, informatique, aws]
date: "2026-02-16"
---

# AWS (Amazon Web Services)

## Vue d'ensemble

Amazon Web Services est la plateforme cloud la plus complète et largement adoptée, offrant plus de 200 services couvrant calcul, stockage, bases de données, networking, ML, et plus encore.

## Services fondamentaux

### Compute

**EC2 (Elastic Compute Cloud)**
- Serveurs virtuels dans le cloud
- Instances variées (t2, m5, c5, r5, etc.)
- Auto Scaling Groups
- Elastic Load Balancing

**Lambda**
- Fonctions serverless
- Pay per execution
- Event-driven
- Pas de gestion serveur

**ECS (Elastic Container Service)**
- Orchestration de conteneurs
- Fargate (serverless) ou EC2

**EKS (Elastic Kubernetes Service)**
- Kubernetes managé
- Voir aussi: [[Kubernetes]]

### Storage

**S3 (Simple Storage Service)**
- Stockage d'objets
- Durabilité 99.999999999% (11 9s)
- Storage classes: Standard, IA, Glacier
- Versioning et lifecycle policies

**EBS (Elastic Block Store)**
- Volumes pour EC2
- SSD (gp3, io2) ou HDD (st1, sc1)
- Snapshots

**EFS (Elastic File System)**
- NFS managé
- Auto-scaling
- Multi-AZ

### Database

**RDS (Relational Database Service)**
- MySQL, PostgreSQL, MariaDB, Oracle, SQL Server
- Multi-AZ pour haute disponibilité
- Read replicas
- Automated backups

**DynamoDB**
- NoSQL managé
- Millisecond latency
- Auto-scaling
- DynamoDB Streams

**Aurora**
- Compatible MySQL/PostgreSQL
- 5x plus rapide que MySQL
- Serverless option

**ElastiCache**
- Redis ou Memcached managé
- In-memory caching

### Networking

**VPC (Virtual Private Cloud)**
- Réseau isolé
- Subnets publics/privés
- Internet Gateway
- NAT Gateway

**Route 53**
- DNS managé
- Health checks
- Routing policies

**CloudFront**
- CDN global
- Edge locations worldwide
- Integration avec S3, EC2

**API Gateway**
- Création et gestion d'APIs
- REST, HTTP, WebSocket
- Throttling et caching

## Sécurité et identité

**IAM (Identity and Access Management)**
- Users, Groups, Roles
- Policies (JSON)
- MFA
- Principe du moindre privilège

**Cognito**
- Authentication et autorisation
- User pools
- Identity pools

**KMS (Key Management Service)**
- Gestion des clés de chiffrement
- Encryption at rest

**Secrets Manager**
- Rotation automatique des secrets
- Integration avec RDS, autres services

**WAF (Web Application Firewall)**
- Protection contre attaques web
- Rules pour bloquer trafic malveillant

## DevOps et CI/CD

**CodeCommit**
- Git repository managé

**CodeBuild**
- Build et test automatisés
- Pay per build minute

**CodeDeploy**
- Automated deployment
- EC2, Lambda, ECS

**CodePipeline**
- CI/CD pipeline
- Orchestration des étapes

**CloudFormation**
- Infrastructure as Code
- Templates YAML/JSON

**CDK (Cloud Development Kit)**
- IaC avec code (TypeScript, Python, etc.)

## Monitoring et logging

**CloudWatch**
- Métriques et logs
- Alarms
- Dashboards
- Events/EventBridge

**X-Ray**
- Distributed tracing
- Analyse de performance
- Service map

**CloudTrail**
- Audit logs
- API calls tracking
- Compliance

## Architecture patterns

### High Availability
- Multi-AZ deployment
- Auto Scaling
- Elastic Load Balancing
- Route 53 health checks

### Disaster Recovery
- Backup and Restore
- Pilot Light
- Warm Standby
- Multi-Region Active-Active

### Microservices
- ECS/EKS pour containers
- API Gateway
- Lambda pour services
- SQS/SNS pour messaging

## Serverless

**Core Services**
- Lambda - Compute
- API Gateway - APIs
- DynamoDB - Database
- S3 - Storage
- EventBridge - Events
- SQS/SNS - Messaging

**Framework**
```yaml
# serverless.yml
service: my-service
provider:
  name: aws
  runtime: nodejs18.x
functions:
  hello:
    handler: handler.hello
    events:
      - http:
          path: hello
          method: get
```

## Machine Learning

**SageMaker**
- Build, train, deploy ML models
- Jupyter notebooks
- Built-in algorithms

**Rekognition**
- Image et video analysis

**Comprehend**
- NLP (Natural Language Processing)

**Translate**
- Translation service

## Messaging

**SQS (Simple Queue Service)**
- Message queue
- Standard ou FIFO
- Dead Letter Queue

**SNS (Simple Notification Service)**
- Pub/Sub messaging
- Push notifications
- Email, SMS, HTTP

**EventBridge**
- Event bus serverless
- Event-driven architecture

## Best Practices

### Coûts
- Right-sizing instances
- Reserved Instances / Savings Plans
- S3 Lifecycle policies
- Auto Scaling
- Monitoring avec Cost Explorer

### Sécurité
- Least privilege IAM
- MFA activé
- Encryption at rest et in transit
- VPC isolés
- Security Groups restrictifs

### Performance
- CloudFront pour CDN
- ElastiCache pour caching
- RDS Read Replicas
- Auto Scaling basé sur métriques

### Reliability
- Multi-AZ deployments
- Automated backups
- Health checks
- Disaster recovery plan

## Certification paths

- **Cloud Practitioner** - Fondamentaux
- **Solutions Architect Associate** - Architecture
- **Developer Associate** - Développement
- **SysOps Administrator Associate** - Opérations
- **Professional** - Expert level
- **Specialty** - Security, ML, etc.

## Ressources

- [Documentation AWS](https://docs.aws.amazon.com)
- AWS Well-Architected Framework
- AWS Free Tier
- AWS Training and Certification
- re:Invent conferences

## Comparaison Cloud Providers

| Feature | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Compute | EC2, Lambda | VMs, Functions | Compute Engine, Cloud Functions |
| Storage | S3, EBS | Blob, Disks | Cloud Storage, Persistent Disks |
| Database | RDS, DynamoDB | SQL Database, Cosmos DB | Cloud SQL, Firestore |
| Kubernetes | EKS | AKS | GKE |

## Sujets à approfondir

- [ ] Well-Architected Framework
- [ ] SAM (Serverless Application Model)
- [ ] Step Functions
- [ ] AppSync (GraphQL)
- [ ] Amplify
- [ ] Organizations et multi-account
