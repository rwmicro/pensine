---
title: "AWS (Amazon Web Services)"
domain: "Applied Sciences"
subdomain: "Computer Science > AWS"
tags: [sciences-appliquées, informatique, aws]
date: "2026-02-16"
parcours: "AWS : fondations, réseau, calcul et serverless"
parcours-description: "De la vue d'ensemble AWS à IAM, S3 et VPC, puis EC2 et Lambda."
---

# AWS (Amazon Web Services)

Au début des années 2000, Amazon découvre que ses équipes passent plus de temps à monter des serveurs, des bases de données et du stockage qu'à développer des fonctionnalités. L'entreprise transforme alors ses briques d'infrastructure en services internes, accessibles par une API. En 2006, elle les ouvre au public : S3 pour stocker des fichiers, puis EC2 pour louer des serveurs à l'heure. Plus besoin d'acheter des machines des mois à l'avance : on loue ce qu'il faut, quand il le faut, et on paie à l'usage. C'est la naissance du **cloud computing** moderne, et Amazon Web Services reste le premier fournisseur du marché, avec plus de deux cents services.

> [!important] Repère pour s'orienter
> Ce fichier est une carte du territoire AWS, pas un manuel : chaque service listé ici a (ou devrait avoir) sa propre note détaillée — voir [[EC2]], [[Bucket S3]], [[IAM]], [[Lambda]], [[VPC]]. Utile pour retrouver rapidement le nom du bon service selon le besoin, pas pour apprendre à le configurer.

## Régions, zones et responsabilité partagée

L'infrastructure d'AWS est découpée en **régions** (Paris, Francfort, Virginie du Nord…), chacune composée de plusieurs **zones de disponibilité** (*Availability Zones*, AZ) : des centres de données séparés physiquement, avec leur propre alimentation et leur propre réseau, mais reliés par des liaisons rapides. Répartir une application sur plusieurs AZ la protège de la panne d'un bâtiment ; la répartir sur plusieurs régions la protège d'une catastrophe régionale. Le choix de la région compte aussi pour la latence, les prix et la localisation légale des données.

La sécurité suit un **modèle de responsabilité partagée** : AWS sécurise le cloud lui-même (bâtiments, matériel, hyperviseurs), le client sécurise ce qu'il y met (données, configurations, droits d'accès, mises à jour de ses serveurs). La plupart des incidents de sécurité dans le cloud viennent de ce second côté, comme un bucket S3 laissé public.

## Calculer : serveurs, conteneurs et fonctions

Il existe trois façons de faire tourner du code sur AWS, de la plus maîtrisée à la plus abstraite. **EC2** (*Elastic Compute Cloud*) loue des machines virtuelles, dans des dizaines de familles d'instances optimisées pour le calcul, la mémoire ou le stockage. On y gère soi-même le système d'exploitation, et on assure la montée en charge avec des *Auto Scaling Groups*, qui ajoutent ou retirent des instances selon la charge, derrière un *Elastic Load Balancer* qui répartit le trafic.

Pour les conteneurs, **ECS** est l'orchestrateur maison d'AWS et **EKS** un [[Kubernetes]] managé ; dans les deux cas, les conteneurs peuvent tourner sur des instances EC2 qu'on gère, ou sur **Fargate**, où AWS fournit la capacité sans qu'on voie de serveur.

**Lambda**, enfin, exécute des fonctions en réaction à des événements, une requête HTTP, un fichier déposé dans S3, un message dans une file. On ne gère aucun serveur, on paie à la milliseconde d'exécution, et la fonction passe automatiquement de zéro à des milliers d'exécutions simultanées. Elle convient aux traitements courts et irréguliers, moins aux calculs longs ou à charge constante.

## Stocker : objets, blocs et fichiers

**S3** (*Simple Storage Service*) stocke des objets, c'est-à-dire des fichiers identifiés par une clé dans un *bucket*, accessibles par HTTP. Il est conçu pour une durabilité de 99,999999999 % (« onze neuf ») : les données sont répliquées sur plusieurs AZ. Des classes de stockage moins chères (Standard-IA pour les accès peu fréquents, Glacier pour l'archivage) et des règles de cycle de vie déplacent automatiquement les objets vieillissants, et le versioning protège des suppressions accidentelles.

**EBS** (*Elastic Block Store*) fournit des disques virtuels attachés à une instance EC2, en SSD (gp3, io2) ou en disque dur (st1, sc1), avec des instantanés pour la sauvegarde. **EFS** (*Elastic File System*) est un système de fichiers réseau NFS partagé entre plusieurs machines, qui grandit automatiquement.

## Les bases de données

**RDS** gère pour vous une base relationnelle classique, MySQL, PostgreSQL, MariaDB, Oracle ou SQL Server : sauvegardes automatiques, correctifs, réplica de secours dans une autre AZ (*Multi-AZ*) et réplicas en lecture pour soulager la base principale. **Aurora** est la base relationnelle conçue par AWS, compatible MySQL et PostgreSQL, avec un stockage distribué qui la rend plus performante et plus résistante, et une option *serverless*.

**DynamoDB** est une base NoSQL clé-valeur et documents, avec une latence de quelques millisecondes à n'importe quelle échelle ; elle impose en revanche de concevoir le modèle de données à partir des requêtes qu'on fera. **ElastiCache** fournit un cache en mémoire (Redis, Valkey ou Memcached) pour soulager une base.

## Le réseau

Tout commence par un **VPC** (*Virtual Private Cloud*), un réseau privé isolé dans lequel on découpe des sous-réseaux. Un sous-réseau public dispose d'une route vers une *Internet Gateway* ; un sous-réseau privé n'en a pas, et ne sort vers Internet, si besoin, que par une *NAT Gateway*. Une architecture classique place les load balancers en public et les serveurs et bases de données en privé. Les *Security Groups*, des pare-feu attachés à chaque instance, filtrent ensuite le trafic.

Autour du VPC, **Route 53** gère le DNS, avec des tests de santé et des politiques de routage (par latence, par géographie, de bascule) ; **CloudFront** est le CDN qui met en cache les contenus au plus près des utilisateurs ; **API Gateway** crée et protège des API REST, HTTP ou WebSocket, avec limitation de débit et cache.

## Identité et sécurité

**IAM** (*Identity and Access Management*) est le service le plus important à maîtriser. Il gère des utilisateurs, des groupes et surtout des **rôles**, des identités temporaires qu'endossent des services ou des personnes, et leur attribue des droits par des politiques JSON. Le principe du moindre privilège, l'authentification multifacteur et l'abandon des clés d'accès permanentes au profit de rôles sont les bases de la sécurité d'un compte AWS. La note [[IAM]] détaille ces mécanismes.

Les autres briques de sécurité répondent à des besoins précis : **KMS** gère les clés de chiffrement des données au repos, **Secrets Manager** stocke les secrets et peut les faire tourner automatiquement, **Cognito** gère l'inscription et la connexion des utilisateurs d'une application, et **WAF** filtre les requêtes web malveillantes devant CloudFront, un load balancer ou API Gateway.

## Surveiller et auditer

**CloudWatch** collecte les métriques et les journaux de tous les services, déclenche des alarmes et affiche des tableaux de bord. **X-Ray** suit une requête à travers les différents services qu'elle traverse, pour trouver où le temps se perd. **CloudTrail** enregistre chaque appel à l'API AWS, qui a fait quoi et quand, et constitue la source essentielle pour l'audit et l'investigation d'un incident.

## Faire communiquer les services

Une architecture moderne découple ses composants par des messages. **SQS** est une file d'attente : un producteur y dépose des messages qu'un consommateur traite à son rythme, avec une *dead letter queue* pour les messages qui échouent sans cesse (en mode standard, au moins une livraison, ou en mode FIFO, ordre strict). **SNS** diffuse un message à de nombreux abonnés (*pub/sub*), files, fonctions, e-mails ou SMS. **EventBridge** est un bus d'événements qui route les événements des services AWS ou des applications selon des règles.

## Automatiser : infrastructure as code et CI/CD

Plutôt que de cliquer dans la console, on décrit l'infrastructure dans du code versionné. **CloudFormation** le fait en YAML ou JSON, **CDK** en langages de programmation (TypeScript, Python…) qui génèrent du CloudFormation ; beaucoup d'équipes utilisent aussi Terraform, indépendant du fournisseur. Pour l'intégration et le déploiement continus, **CodeBuild**, **CodeDeploy** et **CodePipeline** couvrent la construction, le déploiement et l'enchaînement des étapes. CodeCommit, le dépôt Git d'AWS, n'accepte plus de nouveaux clients depuis 2024 : les équipes hébergent leur code sur GitHub ou GitLab.

Les applications *serverless* ont leurs propres frameworks, comme AWS SAM ou le Serverless Framework, qui décrivent fonctions et événements dans un seul fichier :

```yaml
# serverless.yml
service: my-service
provider:
  name: aws
  runtime: nodejs22.x
functions:
  hello:
    handler: handler.hello
    events:
      - http:
          path: hello
          method: get
```

## L'intelligence artificielle

**SageMaker** couvre tout le cycle d'un modèle d'apprentissage automatique, des notebooks à l'entraînement et au déploiement. **Bedrock** donne accès par API à des grands modèles de langage de plusieurs éditeurs. Des services prêts à l'emploi traitent des tâches courantes : **Rekognition** pour l'analyse d'images et de vidéos, **Comprehend** pour l'analyse de texte, **Translate** pour la traduction.

## Concevoir une bonne architecture

AWS résume ses recommandations dans le **Well-Architected Framework**, organisé en piliers : excellence opérationnelle, sécurité, fiabilité, performance, optimisation des coûts et durabilité.

Pour la **fiabilité**, on répartit l'application sur plusieurs AZ, avec de l'auto scaling, des load balancers et des tests de santé, et on prévoit un plan de reprise après sinistre. Quatre stratégies existent : restaurer des sauvegardes, garder une « veilleuse » (*pilot light*, l'essentiel des données répliquées et une infrastructure minimale prête à démarrer), maintenir une copie réduite qui tourne en permanence (*warm standby*), ou faire tourner l'application à plein dans plusieurs régions (*multi-region active-active*).

> [!tip] Choisir sa stratégie de DR
> Ces quatre options sont classées par RTO/coût croissant : Backup and Restore est le moins cher mais le plus lent à restaurer, Multi-Region Active-Active est quasi instantané mais double l'infrastructure et son coût en continu. Le bon choix dépend du RTO/RPO exigé par le métier, pas d'une préférence technique.

Pour la **sécurité**, on applique le moindre privilège, l'authentification multifacteur, le chiffrement au repos et en transit, et des Security Groups restrictifs. Pour la **performance**, on rapproche les contenus des utilisateurs avec CloudFront, on met en cache avec ElastiCache et on répartit les lectures sur des réplicas. Pour les **coûts**, enfin, on dimensionne les instances au plus juste, on s'engage sur la durée avec des *Savings Plans* ou des instances réservées pour la charge stable, on éteint ce qui ne sert pas, et on surveille les dépenses avec Cost Explorer et des alertes budgétaires. Le cloud est facturé à l'usage, ce qui veut aussi dire qu'une ressource oubliée coûte chaque mois.

## Comparaison avec les autres clouds

Les deux grands concurrents d'AWS, Microsoft Azure et Google Cloud, proposent des services équivalents sous d'autres noms.

| Feature | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Compute | EC2, Lambda | VMs, Functions | Compute Engine, Cloud Functions |
| Storage | S3, EBS | Blob, Disks | Cloud Storage, Persistent Disks |
| Database | RDS, DynamoDB | SQL Database, Cosmos DB | Cloud SQL, Firestore |
| Kubernetes | EKS | AKS | GKE |

## Se former et se certifier

AWS propose un parcours de certifications : Cloud Practitioner pour les fondamentaux, puis les niveaux Associate (Solutions Architect, Developer, SysOps Administrator), Professional, et des spécialités comme la sécurité ou le machine learning. Le niveau gratuit (*Free Tier*) permet de s'exercer sans dépenser, à condition de surveiller ce qu'on laisse allumé.

## Ressources

- [Documentation AWS](https://docs.aws.amazon.com) et le guide du Well-Architected Framework.
- AWS Skill Builder pour les formations officielles, et les vidéos de la conférence annuelle re:Invent.
- Pour aller plus loin : Step Functions, AWS Organizations et la gestion multi-comptes.
