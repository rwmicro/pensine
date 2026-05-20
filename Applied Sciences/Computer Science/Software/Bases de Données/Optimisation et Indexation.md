---
title: "Optimisation et Indexation"
domain: "Applied Sciences"
subdomain: "Computer Science > Bases de Données"
tags: [sciences-appliquées, informatique]
date: "2026-02-25"
---

# Optimisation et Indexation

L'optimisation des bases de données est l'art d'accélérer les requêtes et d'améliorer les performances globales du système. La compréhension des index est centrale.

## Comprendre les plans d'exécution

Avant d'optimiser, comprendre comment la base exécute la requête.

```sql
-- PostgreSQL
EXPLAIN SELECT * FROM clients WHERE email = 'alice@example.com';

-- Avec statistiques réelles d'exécution
EXPLAIN ANALYZE SELECT * FROM clients WHERE email = 'alice@example.com';

-- Format JSON plus lisible pour les requêtes complexes
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT c.nom, SUM(co.total)
FROM clients c JOIN commandes co ON c.id = co.client_id
GROUP BY c.id
ORDER BY SUM(co.total) DESC
LIMIT 10;
```

**Éléments clés d'un plan** :

| Nœud | Description |
|---|---|
| Seq Scan | Lecture séquentielle de toute la table — à éviter sur grandes tables |
| Index Scan | Utilise un index pour localiser les lignes |
| Index Only Scan | Toutes les données viennent de l'index (le plus rapide) |
| Bitmap Heap Scan | Combine plusieurs index, puis accède au heap |
| Hash Join | Jointure par table de hachage — efficace pour l'égalité |
| Nested Loop Join | Pour chaque ligne de T1, recherche dans T2 — bien avec index |
| Merge Join | Jointure de tables triées — bon pour les grandes tables triées |
| Sort | Tri explicite en mémoire ou sur disque |
| Hash Aggregate | GROUP BY via table de hachage |

**Coût** : `cost=0.00..45.23 rows=10 width=124` — `0.00` = coût de démarrage, `45.23` = coût total, `rows` = lignes estimées.

`Actual time=0.041..1.234` : temps réel de démarrage et total.

Si `rows` estimé est très différent de `rows` réel, les statistiques sont obsolètes → lancer `ANALYZE`.

## Index

Un index est une structure de données supplémentaire qui accélère les recherches au prix d'espace disque et d'un coût à l'insertion/mise à jour.

### Index B-tree

Structure arborescente équilibrée. L'index par défaut dans PostgreSQL/MySQL. Supporte les comparaisons `=`, `<`, `<=`, `>`, `>=`, `BETWEEN`, `IN`, `LIKE 'abc%'` (mais pas `LIKE '%abc'`).

```sql
-- Index simple
CREATE INDEX idx_clients_email ON clients(email);

-- Index unique (implique aussi une contrainte)
CREATE UNIQUE INDEX idx_clients_email ON clients(email);

-- Index composé — l'ordre des colonnes compte !
-- Efficace pour : WHERE nom = 'Alice' AND age > 25
-- Efficace pour : WHERE nom = 'Alice' (préfixe gauche)
-- Inefficace pour : WHERE age > 25 (pas le préfixe gauche)
CREATE INDEX idx_clients_nom_age ON clients(nom, age);

-- Index partiel — index uniquement les lignes actives
CREATE INDEX idx_commandes_actives ON commandes(client_id)
WHERE statut != 'annulee';

-- Index couvrant — inclure des colonnes supplémentaires (Index Only Scan possible)
CREATE INDEX idx_clients_email_covering ON clients(email) INCLUDE (nom, solde);
```

**Choisir les colonnes à indexer** :
- Colonnes très utilisées dans les clauses WHERE, JOIN ON, ORDER BY
- Colonnes avec haute cardinalité (beaucoup de valeurs distinctes)
- Clés étrangères (toujours indexer les FK)

**Ne pas indexer** :
- Tables très petites (< quelques milliers de lignes)
- Colonnes avec très peu de valeurs distinctes (boolean, enum à 2-3 valeurs)
- Tables à très haute fréquence d'écriture si les lectures ne nécessitent pas l'index

### Index Hash

```sql
CREATE INDEX idx_hash_email ON clients USING HASH (email);
```

Uniquement pour les comparaisons d'égalité `=`. Plus rapide qu'un B-tree pour les lookups exacts mais ne supporte pas ORDER BY, RANGE, LIKE.

### Index GIN et GiST (PostgreSQL)

**GIN (Generalized Inverted Index)** : pour les types complexes comme les tableaux, JSONB, la recherche full-text.

```sql
-- Index sur un champ JSONB
CREATE INDEX idx_metadata ON produits USING GIN (metadata);

-- Index full-text
CREATE INDEX idx_contenu_fts ON articles USING GIN (to_tsvector('french', contenu));

-- Requête full-text
SELECT * FROM articles
WHERE to_tsvector('french', contenu) @@ to_tsquery('french', 'python & programmation');
```

**GiST (Generalized Search Tree)** : pour les données géométriques, les intervalles (tsrange, daterange), la similarité de chaînes.

```sql
-- Index géospatial (avec PostGIS)
CREATE INDEX idx_geo ON lieux USING GIST (position);

-- Requête géospatiale
SELECT * FROM lieux WHERE ST_DWithin(position, ST_MakePoint(2.35, 48.85), 10000);
```

## Optimisation des requêtes

### Éviter SELECT *

```sql
-- Mauvais : charge toutes les colonnes, empêche l'Index Only Scan
SELECT * FROM clients WHERE email = 'alice@x.com';

-- Bon : ne charger que ce dont on a besoin
SELECT id, nom, solde FROM clients WHERE email = 'alice@x.com';
```

### Éviter les fonctions sur les colonnes indexées

```sql
-- Mauvais : l'index sur date_naissance n'est pas utilisé
SELECT * FROM clients WHERE YEAR(date_naissance) = 1990;

-- Bon : transformer le prédicat pour utiliser l'index
SELECT * FROM clients
WHERE date_naissance BETWEEN '1990-01-01' AND '1990-12-31';

-- Mauvais : l'index sur email n'est pas utilisé
SELECT * FROM clients WHERE LOWER(email) = 'alice@x.com';

-- Bon : index fonctionnel (PostgreSQL)
CREATE INDEX idx_email_lower ON clients (LOWER(email));
SELECT * FROM clients WHERE LOWER(email) = 'alice@x.com';
```

### Pagination efficace

```sql
-- Mauvais pour les grandes pages : OFFSET lit et ignore toutes les lignes précédentes
-- O(offset + limit) → très lent pour offset = 1 000 000
SELECT * FROM produits ORDER BY id LIMIT 20 OFFSET 1000000;

-- Bon : keyset pagination (cursor-based)
-- Après avoir récupéré la dernière ligne avec id = 12345 :
SELECT * FROM produits WHERE id > 12345 ORDER BY id LIMIT 20;
-- O(log n) grâce à l'index sur id
```

### Jointures et sous-requêtes

```sql
-- Souvent plus lent : sous-requête corrélée (recalculée pour chaque ligne)
SELECT c.nom,
    (SELECT COUNT(*) FROM commandes co WHERE co.client_id = c.id) AS nb
FROM clients c;

-- Souvent plus rapide : LEFT JOIN avec GROUP BY
SELECT c.nom, COUNT(co.id) AS nb
FROM clients c
LEFT JOIN commandes co ON c.id = co.client_id
GROUP BY c.id, c.nom;

-- Utiliser EXISTS plutôt que IN pour les grandes sous-requêtes
-- IN : évalue toute la sous-requête, compare chaque valeur
SELECT * FROM clients WHERE id IN (SELECT DISTINCT client_id FROM commandes);
-- EXISTS : s'arrête au premier match trouvé
SELECT * FROM clients c WHERE EXISTS (SELECT 1 FROM commandes WHERE client_id = c.id);
```

### Statistiques et maintenance (PostgreSQL)

```sql
-- Mettre à jour les statistiques (utilisées par le planificateur)
ANALYZE clients;
ANALYZE;  -- toute la base

-- VACUUM : récupérer l'espace des lignes mortes (supprimées/mises à jour)
VACUUM clients;
VACUUM ANALYZE clients;  -- vacuum + analyze en une passe
VACUUM FULL clients;     -- récupère l'espace disque (bloque la table)

-- Autovacuum : daemon PostgreSQL qui fait ça automatiquement
-- Voir la configuration :
SHOW autovacuum;
SELECT * FROM pg_stat_user_tables WHERE relname = 'clients';
```

## Partitionnement

Le partitionnement divise une grande table en plusieurs sous-tables (partitions) physiquement séparées.

```sql
-- Partitionnement par plage de dates
CREATE TABLE commandes (
    id        BIGSERIAL,
    client_id INTEGER,
    total     DECIMAL(10,2),
    cree_le   TIMESTAMP NOT NULL
) PARTITION BY RANGE (cree_le);

CREATE TABLE commandes_2024 PARTITION OF commandes
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE commandes_2025 PARTITION OF commandes
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- PostgreSQL route automatiquement les requêtes vers la bonne partition
-- "Partition pruning" : une requête WHERE cree_le > '2025-01-01' n'accède qu'à commandes_2025
```

**Avantages** : partition pruning (ignorer les partitions non pertinentes), archivage facile (détacher une partition ancienne), maintenance par partition (VACUUM, ANALYZE).

**Partitionnement par liste** : pour les valeurs catégorielles (région, statut).

**Partitionnement par hash** : distribuer uniformément les données.

## Pool de connexions

Créer une connexion BDD est coûteux (~50ms). Le connection pooling maintient un pool de connexions réutilisables.

```python
# SQLAlchemy connection pool (Python)
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost/mabase",
    pool_size=10,          # connexions permanentes
    max_overflow=20,       # connexions supplémentaires en cas de pic
    pool_timeout=30,       # attente max avant erreur
    pool_pre_ping=True     # vérifier les connexions avant utilisation
)
```

Outils dédiés : **PgBouncer** (PostgreSQL), **ProxySQL** (MySQL). Essentiels en production pour absorber les pics de trafic.

## Cache applicatif

Éviter les requêtes répétées en mettant en cache les résultats fréquents.

```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379)

def obtenir_produit(id: int) -> dict:
    cle = f"produit:{id}"

    # Tenter le cache
    donnees = cache.get(cle)
    if donnees:
        return json.loads(donnees)

    # Cache miss → aller en BDD
    produit = db.query("SELECT * FROM produits WHERE id = %s", id)

    # Stocker en cache pour 10 minutes
    cache.setex(cle, 600, json.dumps(produit))
    return produit
```

## Verrous et transactions

```sql
-- Vérifier les verrous actifs (PostgreSQL)
SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE wait_event_type = 'Lock';

-- Voir les verrous
SELECT * FROM pg_locks WHERE NOT granted;

-- Terminer une transaction qui bloque
SELECT pg_terminate_backend(pid);

-- Niveaux d'isolation pour les transactions longues
BEGIN ISOLATION LEVEL READ COMMITTED;
BEGIN ISOLATION LEVEL REPEATABLE READ;
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

**Verrouillage explicite** :

```sql
-- Verrouiller des lignes pour mise à jour (évite les conflits)
SELECT * FROM comptes WHERE id = 5 FOR UPDATE;
UPDATE comptes SET solde = solde - 100 WHERE id = 5;
COMMIT;

-- Verrouillage partagé (plusieurs lectures, bloque les écritures)
SELECT * FROM produits WHERE id = 10 FOR SHARE;
```
