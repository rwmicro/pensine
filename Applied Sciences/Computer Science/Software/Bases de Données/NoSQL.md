---
title: "NoSQL"
domain: "Applied Sciences"
subdomain: "Computer Science > Bases de Données"
tags: [sciences-appliquées, informatique]
date: "2026-02-24"
---

# NoSQL

## Motivations

Les bases relationnelles ont dominé pendant des décennies, mais vers 2006-2010, des contraintes nouvelles ont émergé :

**Scalabilité horizontale** : un SGBDR classique scale difficilement sur des centaines de nœuds. Les jointures distribuées sont prohibitives.

**Volume (Big Data)** : des pétaoctets de données ne tiennent pas sur un seul serveur relationnel.

**Schéma flexible** : les startups et les systèmes agiles changent fréquemment leur modèle de données. Modifier le schéma d'une table avec des milliards de lignes peut prendre des heures.

**Cohérence éventuelle** : le théorème CAP impose de choisir entre cohérence et disponibilité en cas de partition réseau. Pour certains cas d'usage (réseaux sociaux, compteurs de vues), la cohérence éventuelle est acceptable.

NoSQL signifie "Not Only SQL" — pas "pas de SQL". Beaucoup de ces bases proposent maintenant un langage de requête similaire à SQL.

## Bases clé-valeur

Le modèle le plus simple : une clé (identifiant unique) associée à une valeur opaque.

### Redis

Redis (Remote Dictionary Server) est une base de données clé-valeur en mémoire avec persistance optionnelle.

**Types de données Redis** :

```bash
# Strings
SET utilisateur:1:nom "Alice"
GET utilisateur:1:nom          # "Alice"
INCR compteur:visites          # incrément atomique
EXPIRE session:abc123 3600     # expiration dans 1h

# Listes (LIFO ou FIFO)
RPUSH file:emails "email1" "email2"
LPUSH file:emails "email0"
LRANGE file:emails 0 -1        # lister tous les éléments
LPOP file:emails               # retirer et retourner le premier

# Sets (sans doublons, sans ordre)
SADD tags:article1 "python" "algo" "database"
SMEMBERS tags:article1
SINTER tags:article1 tags:article2  # intersection

# Sorted Sets (avec score)
ZADD classement 1500 "Alice"
ZADD classement 2300 "Bob"
ZRANGE classement 0 -1 WITHSCORES  # tri par score croissant
ZREVRANK classement "Bob"          # rang (décroissant)

# Hashes (objets)
HSET utilisateur:1 nom "Alice" age 30 email "alice@x.com"
HGET utilisateur:1 nom
HGETALL utilisateur:1
HINCRBY utilisateur:1 age 1    # incrémenter un champ

# Streams (log d'événements)
XADD evenements * action "login" utilisateur "alice"
XREAD COUNT 10 STREAMS evenements 0
```

**Persistance Redis** :
- RDB (Redis Database) : snapshots périodiques sur disque
- AOF (Append Only File) : log de toutes les opérations d'écriture
- Hybride : RDB + AOF

**Cas d'usage Redis** :
- Cache (diminuer la charge sur la BDD principale)
- Gestion des sessions utilisateur
- Files de tâches (Celery utilise Redis comme broker)
- Pub/Sub pour les notifications temps réel
- Compteurs, classements, rate limiting
- Verrous distribués (Redlock)

**Gestion du cache** :

| Concept | Description |
|---------|-------------|
| Cache invalidation | Processus qui déclare une entrée invalide et la supprime ou remplace, pour assurer la fraîcheur des données |
| Cache eviction | Suppression d'entrées quand le cache est plein, selon une politique (LRU, LFU, TTL, Random) |
| LRU (Least Recently Used) | Supprime les entrées les moins récemment accédées |
| TTL (Time To Live) | Expiration automatique après une durée définie (`EXPIRE`) |

```bash
# Redis avec ioredis (Node.js)
const Redis = require("ioredis");
const redis = new Redis({ host: "127.0.0.1", port: 6379 });

# Mise en cache avec TTL de 10 secondes
await redis.set("user:1", JSON.stringify(userData), "EX", 10);

# Récupérer depuis le cache
const cached = await redis.get("user:1");
if (cached) return JSON.parse(cached);
```

### DynamoDB (AWS)

Base clé-valeur/document entièrement managée par AWS. Scaling automatique, SLA 99.999%, latence < 10 ms. Modèle de tarification à la requête.

## Bases document

Stockent des documents semi-structurés (JSON, BSON, XML). Chaque document est auto-décrit et peut avoir des champs différents.

### MongoDB

```javascript
// Connexion et sélection de base
use ecommerce

// Insérer
db.produits.insertOne({
    nom: "Laptop Pro",
    prix: 1299.99,
    categorie: "informatique",
    tags: ["laptop", "professionnel"],
    specs: { ram: 16, stockage: 512, ecran: 15.6 },
    date_ajout: new Date()
})

db.produits.insertMany([
    { nom: "Souris", prix: 29.99, categorie: "peripheriques" },
    { nom: "Clavier", prix: 89.99, categorie: "peripheriques" }
])

// Lire — find() retourne un curseur
db.produits.find({ categorie: "informatique" })
db.produits.findOne({ nom: "Laptop Pro" })

// Opérateurs de comparaison
db.produits.find({ prix: { $gt: 100, $lt: 2000 } })
db.produits.find({ tags: "laptop" })           // dans un tableau
db.produits.find({ "specs.ram": { $gte: 16 } }) // champ imbriqué

// Projection (sélectionner les champs)
db.produits.find({}, { nom: 1, prix: 1, _id: 0 })

// Tri, limite, skip
db.produits.find().sort({ prix: -1 }).limit(10).skip(20)

// Mettre à jour
db.produits.updateOne(
    { nom: "Laptop Pro" },
    { $set: { prix: 1199.99 }, $push: { tags: "solde" } }
)

db.produits.updateMany(
    { categorie: "peripheriques" },
    { $inc: { prix: 5 } }  // augmenter le prix de 5
)

// Supprimer
db.produits.deleteOne({ nom: "Souris" })
db.produits.deleteMany({ prix: { $lt: 10 } })

// Index
db.produits.createIndex({ categorie: 1 })
db.produits.createIndex({ nom: "text" })  // index full-text
db.produits.createIndex({ prix: 1, categorie: 1 })  // index composé

// Pipeline d'agrégation
db.produits.aggregate([
    { $match: { categorie: "informatique" } },
    { $group: {
        _id: "$categorie",
        prix_moyen: { $avg: "$prix" },
        nb_produits: { $sum: 1 },
        prix_max: { $max: "$prix" }
    }},
    { $sort: { prix_moyen: -1 } }
])
```

**Schéma MongoDB** : bien que MongoDB soit "sans schéma", en pratique on définit un schéma via des validateurs JSON Schema ou des bibliothèques ODM (Mongoose pour Node.js, MongoEngine pour Python).

**Quand utiliser MongoDB** : schéma qui évolue fréquemment, documents avec des structures variables, applications web avec des lectures rapides par document, CMS, catalogues produits, profils utilisateur.

## Bases colonnes larges (Wide Column)

### Apache Cassandra

Conçu pour gérer des volumes massifs de données distribuées sans point de défaillance unique. Créé par Facebook pour la recherche dans les messages.

**Modèle de données** : organisé en keyspaces (équivalent bases de données), tables, rows. Les colonnes peuvent varier par ligne. Les données sont partitionnées sur les nœuds via un consistent hashing.

```sql
-- CQL (Cassandra Query Language) — similaire à SQL
CREATE KEYSPACE ecommerce
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};

USE ecommerce;

CREATE TABLE evenements_utilisateur (
    utilisateur_id UUID,
    horodatage     TIMESTAMP,
    action         TEXT,
    details        MAP<TEXT, TEXT>,
    PRIMARY KEY (utilisateur_id, horodatage)
) WITH CLUSTERING ORDER BY (horodatage DESC);

-- La partition key (utilisateur_id) détermine le nœud
-- La clustering key (horodatage) détermine l'ordre au sein de la partition

INSERT INTO evenements_utilisateur
(utilisateur_id, horodatage, action)
VALUES (uuid(), toTimestamp(now()), 'login');

-- Requête efficace : filtre sur la partition key
SELECT * FROM evenements_utilisateur
WHERE utilisateur_id = 550e8400-e29b-41d4-a716-446655440000
AND horodatage > '2024-01-01 00:00:00'
LIMIT 100;
```

**Règles de conception Cassandra** :
- Modéliser selon les requêtes, pas selon les entités (l'inverse de SQL)
- Pas de jointures, pas de transactions multi-tables
- Une table = une requête
- La partition key doit distribuer les données uniformément

**Cas d'usage** : IoT (milliards de mesures), logs, historique d'événements, messagerie, métriques de monitoring.

## Bases graphe

### Neo4j

```cypher
// Cypher — langage de requête de Neo4j

// Créer des nœuds
CREATE (alice:Personne {nom: 'Alice', age: 30})
CREATE (bob:Personne {nom: 'Bob', age: 25})
CREATE (python:Competence {nom: 'Python'})

// Créer des relations
MATCH (alice:Personne {nom: 'Alice'}), (bob:Personne {nom: 'Bob'})
CREATE (alice)-[:CONNAIT {depuis: 2020}]->(bob)

MATCH (alice:Personne {nom: 'Alice'}), (python:Competence {nom: 'Python'})
CREATE (alice)-[:MAITRISE {niveau: 'expert'}]->(python)

// Requêtes de traversée
MATCH (p:Personne)-[:CONNAIT]->(ami)
WHERE p.nom = 'Alice'
RETURN ami.nom

// Chemin le plus court
MATCH path = shortestPath(
    (alice:Personne {nom: 'Alice'})-[:CONNAIT*]-(cible:Personne {nom: 'Charlie'})
)
RETURN path

// Recommandation (amis d'amis)
MATCH (alice:Personne {nom: 'Alice'})-[:CONNAIT]->(ami)-[:CONNAIT]->(suggestion)
WHERE NOT (alice)-[:CONNAIT]->(suggestion) AND alice <> suggestion
RETURN suggestion.nom, COUNT(ami) AS amis_en_commun
ORDER BY amis_en_commun DESC
LIMIT 10
```

**Cas d'usage** : réseaux sociaux, moteurs de recommandation, détection de fraudes (graphes de transactions), gestion des autorisations (RBAC/ABAC), knowledge graphs, cartographie des dépendances logicielles.

## Elasticsearch

Moteur de recherche distribué basé sur Apache Lucene. Optimisé pour la recherche full-text et l'analyse de logs.

```bash
# Indexer un document
curl -X POST "localhost:9200/articles/_doc" -H 'Content-Type: application/json' -d '{
  "titre": "Introduction à Python",
  "contenu": "Python est un langage de programmation...",
  "auteur": "Alice",
  "date": "2024-01-15",
  "tags": ["python", "programmation"]
}'

# Recherche full-text
curl -X GET "localhost:9200/articles/_search" -H 'Content-Type: application/json' -d '{
  "query": {
    "multi_match": {
      "query": "python programmation",
      "fields": ["titre^2", "contenu"],
      "type": "best_fields",
      "fuzziness": "AUTO"
    }
  },
  "highlight": { "fields": { "contenu": {} } },
  "from": 0, "size": 10
}'
```

**Cas d'usage** : recherche dans une application (e-commerce, documentation), centralisation des logs (stack ELK), analytics temps réel.

## Comparaison SQL vs NoSQL

| Critère | SQL (Relationnel) | NoSQL |
|---|---|---|
| Schéma | Rigide, défini à l'avance | Flexible, évolue facilement |
| Transactions | ACID complètes | Éventuellement cohérent (souvent) |
| Jointures | Natives et efficaces | Inexistantes ou très limitées |
| Scalabilité | Verticale principalement | Horizontale nativement |
| Maturité | 50 ans, très stable | 15-20 ans, en évolution |
| Langage | SQL standard | Propre à chaque base |
| Cas d'usage | Transactions, ERP, finance | Web scale, Big Data, temps réel |

## Quand utiliser NoSQL

- Les données n'ont pas de schéma fixe ou évoluent rapidement
- Le volume est trop grand pour un seul serveur relationnel
- La latence doit être sub-milliseconde (Redis)
- On modélise des relations complexes (Neo4j)
- On fait de la recherche full-text (Elasticsearch)
- On ingère des millions d'événements par seconde (Cassandra, Kafka)
- La disponibilité prime sur la cohérence stricte
