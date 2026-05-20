---
title: "AWS Lambda"
domain: "Applied Sciences"
subdomain: "Computer Science > AWS"
tags: [sciences-appliquées, informatique, aws]
date: "2026-02-25"
---

# AWS Lambda

Lambda est le service de calcul serverless d'AWS. On déploie du code (fonctions) sans provisionner ni gérer de serveurs. Lambda alloue les ressources automatiquement et facture uniquement le temps d'exécution.

## Principe serverless

**Serverless ne signifie pas "pas de serveurs"** — les serveurs existent, mais AWS les gère entièrement. Le développeur se concentre uniquement sur le code métier.

**Modèle d'exécution** : chaque invocation de Lambda peut s'exécuter sur une instance fraîche (cold start) ou réutiliser une instance déjà initialisée (warm start). Lambda gère automatiquement le scaling de 0 à des milliers d'instances simultanées.

## Déclencheurs (Triggers)

Lambda peut être invoqué par de nombreux services AWS :

| Source | Mode | Cas d'usage |
|---|---|---|
| API Gateway | Synchrone | API REST, webhooks |
| Application Load Balancer | Synchrone | Endpoints HTTP |
| S3 | Asynchrone | Traitement de fichiers uploadés |
| DynamoDB Streams | Par lot | Réagir aux changements BDD |
| SQS | Par lot | Traitement de messages en queue |
| SNS | Asynchrone | Notifications, fan-out |
| EventBridge | Asynchrone | Événements planifiés (cron), règles |
| CloudWatch Events | Asynchrone | Monitoring, alarmes |
| Cognito | Synchrone | Hooks d'authentification |
| Kinesis | Par lot | Traitement de flux temps réel |

## Exemple complet — Lambda HTTP via API Gateway

```python
import json
import boto3
from datetime import datetime

# Le client DynamoDB est créé en dehors du handler
# pour être réutilisé entre les warm invocations
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('commandes')

def handler(event, context):
    """
    Endpoint : POST /commandes
    event : contient les informations de la requête HTTP
    context : informations sur l'invocation Lambda
    """
    try:
        # Parser le corps de la requête
        body = json.loads(event.get('body', '{}'))

        client_id = body.get('client_id')
        montant = body.get('montant')

        if not client_id or not montant:
            return reponse(400, {"erreur": "client_id et montant requis"})

        # Créer la commande en DynamoDB
        commande = {
            'id': context.aws_request_id,  # ID unique de l'invocation
            'client_id': client_id,
            'montant': str(montant),  # DynamoDB stocke les Decimal en string
            'statut': 'en_attente',
            'cree_le': datetime.utcnow().isoformat()
        }

        table.put_item(Item=commande)

        return reponse(201, {"commande_id": commande['id']})

    except json.JSONDecodeError:
        return reponse(400, {"erreur": "Corps JSON invalide"})
    except Exception as e:
        print(f"Erreur : {e}")  # CloudWatch Logs
        return reponse(500, {"erreur": "Erreur interne"})

def reponse(code: int, corps: dict) -> dict:
    return {
        'statusCode': code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(corps)
    }
```

## Configuration

```yaml
# template SAM (Serverless Application Model)
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: python3.12
    Timeout: 30
    MemorySize: 256
    Environment:
      Variables:
        ENV: production

Resources:
  ApiCommandes:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: commandes.handler
      MemorySize: 512        # 128 Mo à 10 Go (par pas de 1 Mo)
      Timeout: 10            # 1 à 900 secondes (15 minutes max)
      ReservedConcurrencyLimit: 100  # Concurrence réservée
      Policies:
        - DynamoDBCrudPolicy:
            TableName: commandes
      Events:
        ApiPost:
          Type: Api
          Properties:
            Path: /commandes
            Method: POST
```

### Paramètres clés

**Mémoire** : de 128 Mo à 10 Go. La puissance CPU allouée est proportionnelle à la mémoire. Doubler la mémoire double le CPU mais double aussi le coût par milliseconde. À tester pour trouver le bon compromis.

**Timeout** : maximum 15 minutes (900 s). Pour les traitements longs, préférer une architecture asynchrone (SQS + Lambda + Step Functions).

**Stockage temporaire /tmp** : jusqu'à 10 Go. Persistant pendant la durée de vie de l'instance Lambda (warm invocations). Réinitialisé sur les cold starts.

## Lifecycle — Cold start vs Warm start

```
Première invocation (cold start) :
  1. Télécharger le package de code
  2. Démarrer l'environnement d'exécution
  3. Initialiser le runtime (JVM, Node.js, Python interpreter)
  4. Exécuter le code d'initialisation (code en dehors du handler)
  5. Appeler le handler
  Total : 100ms à quelques secondes selon le langage et la taille

Invocation suivante dans la même instance (warm start) :
  1. Appeler le handler directement
  Total : latence du code uniquement
```

**Optimiser les cold starts** :
- Utiliser des langages à démarrage rapide (Python, Node.js > Java, .NET)
- Minimiser la taille du package (dépendances minimales)
- Utiliser les Lambda Layers pour les dépendances communes
- Concurrence provisionnée (Provisioned Concurrency) : maintient X instances pré-initialisées (coût supplémentaire)
- `INIT_TYPE=provisioned` pour la concurrence provisionnée

## Layers (couches)

Les Lambda Layers permettent de partager du code et des dépendances entre fonctions.

```bash
# Créer un layer avec des dépendances Python
mkdir python
pip install requests boto3 -t python/
zip -r layer.zip python/
aws lambda publish-layer-version \
    --layer-name dependances-communes \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.11 python3.12
```

## Concurrence

**Concurrence** : nombre d'instances Lambda s'exécutant simultanément.

**Concurrence par défaut** : 1000 par région (soft limit, augmentable).

**Concurrence réservée** (Reserved Concurrency) : garantit un nombre max d'instances pour une fonction, ET plafonne cette fonction à ce nombre.

**Concurrence provisionnée** (Provisioned Concurrency) : maintient X instances initialisées et prêtes. Élimine les cold starts pour ces instances.

```bash
# Configurer la concurrence réservée
aws lambda put-function-concurrency \
    --function-name ma-fonction \
    --reserved-concurrent-executions 50

# Configurer la concurrence provisionnée
aws lambda put-provisioned-concurrency-config \
    --function-name ma-fonction \
    --qualifier mon-alias \
    --provisioned-concurrent-executions 10
```

## Gestion des erreurs et Destinations

```python
# Retry automatique pour les invocations asynchrones
# Lambda réessaie 2 fois en cas d'erreur par défaut

# Dead Letter Queue — messages non traités après les retries
# À configurer dans la console ou via IaC

# Destinations — pour les invocations asynchrones
# On Success → autre Lambda, SQS, SNS, EventBridge
# On Failure → même options (DLQ recommandée)
```

```yaml
# SAM : configurer les destinations
EventInvokeConfig:
  DestinationConfig:
    OnSuccess:
      Type: SQS
      Destination: !GetAtt FileSucces.Arn
    OnFailure:
      Type: SQS
      Destination: !GetAtt DLQ.Arn
  MaximumRetryAttempts: 2
  MaximumEventAgeInSeconds: 3600
```

## Bonnes pratiques

**Idempotence** : concevoir les fonctions pour qu'elles produisent le même résultat si invoquées plusieurs fois avec les mêmes données. Lambda peut invoquer une fonction plus d'une fois dans certains cas (retry asynchrone).

**Stateless** : ne pas stocker d'état dans la mémoire de la fonction. Utiliser DynamoDB, S3, ElastiCache pour la persistance.

**Garder le handler court** : déléguer la logique à des fonctions auxiliaires. Le code en dehors du handler est exécuté une seule fois par instance (warm cache).

**Variables d'environnement** : pour la configuration. Ne jamais hardcoder les secrets — utiliser SSM Parameter Store ou Secrets Manager.

```python
import os
import boto3
import json

# Récupération de secrets depuis Secrets Manager (à l'init, pas dans le handler)
def obtenir_secret(nom: str) -> dict:
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=nom)
    return json.loads(response['SecretString'])

# Mise en cache au niveau de l'instance
SECRET = obtenir_secret(os.environ['SECRET_NAME'])

def handler(event, context):
    mot_de_passe_bdd = SECRET['password']
    # ...
```

## Pricing

- **Requêtes** : 0.20 $ par million d'invocations (1 million gratuit/mois)
- **Durée** : 0.0000166667 $ par Go-seconde (400 000 Go-secondes gratuites/mois)

Exemple : 1 million d'invocations de 512 Mo pendant 200 ms = 0.20$ + 1M × 0.5Go × 0.2s × 0.0000166667$/Go-s ≈ 1.87$
