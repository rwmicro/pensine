---
title: "Microservices"
domain: "Applied Sciences"
subdomain: "Computer Science > Architecture Logicielle"
tags: [sciences-appliquées, informatique]
date: "2026-02-25"
---

# Microservices

## Historique et contexte

**Monolithique** : toute l'application est un seul déployable. Simple à démarrer, difficile à scaler et maintenir à grande échelle.

**SOA (Service-Oriented Architecture)** : années 2000 — décomposition en services via des bus d'entreprise (ESB). Souvent lourd et couplé.

**Microservices** : 2012-2014 — popularisé par Netflix, Amazon, Martin Fowler. Services petits, indépendants, déployables séparément, organisés autour des capacités métier.

## Caractéristiques

**Faiblement couplés** : un service peut être modifié, déployé ou redémarré sans affecter les autres.

**Déployables indépendamment** : chaque service a son propre pipeline CI/CD. Netflix déploie des milliers de fois par jour.

**Organisés autour des capacités métier** (Domain-Driven Design) : un service correspond à un bounded context — ex : Service Commandes, Service Inventaire, Service Paiement.

**Chacun possède ses données** : pas de base de données partagée entre services. Chaque service est propriétaire de son schéma. La cohérence est éventuelle.

**Petite équipe** : la règle des "deux pizzas" d'Amazon — une équipe qui se nourrit avec deux pizzas peut développer et maintenir un service.

## Communication

### Synchrone (requête-réponse)

**REST/HTTP** : simple, universel, mais couplage temporel fort (le service appelé doit être disponible).

```python
# Service A appelle Service B via HTTP
import httpx

async def obtenir_prix_produit(produit_id: int) -> float:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://service-inventaire/api/produits/{produit_id}"
        )
        response.raise_for_status()
        return response.json()["prix"]
```

**gRPC** : protocole binaire basé sur HTTP/2. Plus rapide que REST (Protocol Buffers vs JSON), typage fort via IDL (Interface Definition Language), streaming bidirectionnel.

```protobuf
// inventaire.proto
service Inventaire {
  rpc ObtenirProduit (RequeteProduit) returns (Produit);
  rpc ListeProduits (FiltresProduit) returns (stream Produit);
}

message Produit {
  int32 id = 1;
  string nom = 2;
  float prix = 3;
  int32 stock = 4;
}
```

### Asynchrone (messagerie)

Les services communiquent via des messages, sans attendre de réponse directe. Couplage très faible — le producteur et le consommateur ne doivent pas être disponibles en même temps.

**RabbitMQ** : broker de messages avec queues, exchanges (direct, topic, fanout, headers), routing.

```python
import pika

# Publier un message
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='commandes', durable=True)

channel.basic_publish(
    exchange='',
    routing_key='commandes',
    body='{"commande_id": 123, "montant": 99.99}',
    properties=pika.BasicProperties(delivery_mode=2)  # message persistant
)
```

**Apache Kafka** : log distribué, rétention des messages (replay possible), haute performance (millions de messages/s), partitionnement, consumer groups.

```python
from kafka import KafkaProducer, KafkaConsumer
import json

# Producteur
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode()
)
producer.send('commandes', {"commande_id": 123, "statut": "creee"})

# Consommateur
consumer = KafkaConsumer(
    'commandes',
    bootstrap_servers=['localhost:9092'],
    group_id='service-paiement',
    value_deserializer=lambda m: json.loads(m.decode())
)
for message in consumer:
    print(f"Reçu : {message.value}")
```

## Patterns microservices

### API Gateway

Point d'entrée unique pour les clients. Gère l'authentification, le rate limiting, le routage, l'agrégation de réponses, la transformation de protocoles.

```
Client → [API Gateway] → Service A
                      → Service B
                      → Service C

Outils : Kong, AWS API Gateway, NGINX, Traefik, Envoy
```

### Service Discovery

Les services doivent se trouver dynamiquement (les IPs changent avec les déploiements).

**Client-side** : le service interroge un registre (Consul, etcd, Eureka) et choisit l'instance.

**Server-side** : le load balancer interroge le registre et fait le routage (Kubernetes Service, AWS ALB).

```yaml
# Kubernetes Service — Service Discovery automatique
apiVersion: v1
kind: Service
metadata:
  name: service-inventaire
spec:
  selector:
    app: inventaire
  ports:
    - port: 80
      targetPort: 8080
# Les autres pods accèdent via http://service-inventaire
```

### Circuit Breaker

Protège contre les défaillances en cascade. Après N échecs consécutifs, le circuit s'ouvre et les appels vers le service défaillant sont court-circuités (retour immédiat d'une erreur ou d'une valeur de fallback).

```python
# Pattern Circuit Breaker simplifié
class CircuitBreaker:
    def __init__(self, seuil_echecs=5, timeout=60):
        self.seuil = seuil_echecs
        self.timeout = timeout
        self.echecs = 0
        self.etat = "FERME"  # FERME, OUVERT, SEMI-OUVERT
        self.derniere_ouverture = None

    def appeler(self, fonction, *args, **kwargs):
        if self.etat == "OUVERT":
            if time.time() - self.derniere_ouverture > self.timeout:
                self.etat = "SEMI-OUVERT"
            else:
                raise Exception("Circuit ouvert")

        try:
            resultat = fonction(*args, **kwargs)
            if self.etat == "SEMI-OUVERT":
                self.etat = "FERME"
                self.echecs = 0
            return resultat
        except Exception as e:
            self.echecs += 1
            if self.echecs >= self.seuil:
                self.etat = "OUVERT"
                self.derniere_ouverture = time.time()
            raise
```

Bibliothèques : `resilience4j` (Java), `pybreaker` (Python), `polly` (.NET).

### Saga Pattern

Gère les transactions distribuées sans verrou global. Une saga est une séquence de transactions locales coordonnées.

**Chorégraphie** : chaque service réagit aux événements et publie les suivants. Pas de coordonnateur central.

```
Commande créée →
  Service Paiement (débite) → Paiement effectué →
    Service Inventaire (réserve) → Stock réservé →
      Service Livraison (planifie)

En cas d'erreur :
Service Livraison échoue → Stock libéré → Remboursement
```

**Orchestration** : un orchestrateur central coordonne les étapes et gère les compensations.

### Strangler Fig Pattern

Migration progressive d'un monolithe vers des microservices. On ajoute un proxy devant le monolithe, puis on extrait progressivement des fonctionnalités vers de nouveaux services. Le monolithe est "étranglé" progressivement jusqu'à disparaître.

### Sidecar Pattern

Déployer un conteneur secondaire aux côtés du service principal pour gérer des préoccupations transversales (logging, monitoring, proxy réseau). Utilisé par les service meshes (Istio injecte automatiquement un proxy Envoy).

## Observabilité

Les microservices rendent le débogage difficile. Les trois piliers :

**Logs** : chaque service écrit des logs structurés (JSON). Centralisés via ELK (Elasticsearch + Logstash + Kibana) ou Loki + Grafana.

**Métriques** : compteurs, jauges, histogrammes. Collectés par Prometheus, visualisés avec Grafana. RED method : Rate, Errors, Duration.

**Traces distribuées** : suivre une requête à travers plusieurs services. OpenTelemetry + Jaeger ou Zipkin. Chaque requête a un trace ID propagé dans les headers.

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = trace.get_tracer(__name__)

@app.get("/commandes/{id}")
async def obtenir_commande(id: int):
    with tracer.start_as_current_span("obtenir-commande") as span:
        span.set_attribute("commande.id", id)
        # ...
```

## Comparaison Microservices vs Monolithique

| Critère | Monolithique | Microservices |
|---|---|---|
| Complexité initiale | Faible | Élevée |
| Déploiement | Simple | Complexe (orchestration) |
| Scalabilité | Tout ou rien | Granulaire par service |
| Indépendance des équipes | Faible | Forte |
| Latence inter-composants | Nulle (appels en mémoire) | Réseau (~1-10ms) |
| Débogage | Simple | Complexe (traces distribuées) |
| Cohérence des données | Transactions ACID | Cohérence éventuelle |
| Infrastructure | Serveur(s) | Docker + K8s + registre |

## Quand ne PAS utiliser les microservices

- Petite équipe (< 10 développeurs) — la complexité opérationnelle dépasse le bénéfice
- Application simple ou incertitude sur le domaine métier — impossible de définir de bons bounded contexts avant de comprendre le domaine
- Faible charge — le scaling granulaire n'apporte rien
- Pas de culture DevOps — les microservices nécessitent CI/CD mature, monitoring, déploiements automatisés

Conseil : commencer avec un monolithe bien structuré (modulaire), puis extraire des services quand des besoins de scaling indépendant ou d'organisation en équipes séparées émergent.
