---
title: "Bases de Données"
domain: "Applied Sciences"
subdomain: "Computer Science > Bases de Données"
tags: [sciences-appliquées, informatique]
date: "2026-02-24"
---

# Bases de Données

Une base de données est un ensemble organisé d'informations structurées, stockées électroniquement et accessibles via un Système de Gestion de Bases de Données (SGBD). Les SGBD permettent de créer, lire, mettre à jour et supprimer des données de façon sûre, cohérente et efficace.

## Historique

| Période | Évolution |
|---|---|
| Années 1960 | Fichiers plats — chaque programme gère ses propres fichiers |
| 1970 | Edgar Codd (IBM) formalise le modèle relationnel |
| 1974 | SQL développé chez IBM (SEQUEL → SQL) |
| 1979 | Oracle commercialise le premier SGBDR |
| 1985 | PostgreSQL (Ingres → Postgres) démarre à Berkeley |
| 1995 | MySQL open source |
| 2004-2010 | Émergence du NoSQL (Google BigTable, Amazon Dynamo, MongoDB) |
| 2012+ | NewSQL — bases relationnelles distribuées (CockroachDB, Spanner) |

## Types de bases de données

### Relationnelles (SGBDR)

Données organisées en tables reliées par des clés. Langage SQL. Garanties ACID.

Exemples : PostgreSQL, MySQL, SQLite, Oracle, Microsoft SQL Server, MariaDB.

### NoSQL — clé-valeur

Associe une clé à une valeur opaque. Lecture et écriture ultra-rapides. Pas de schéma.

Exemples : Redis, DynamoDB, Memcached, Riak.

### NoSQL — document

Stocke des documents structurés (JSON/BSON). Chaque document est auto-décrit.

Exemples : MongoDB, CouchDB, Firestore, Elasticsearch.

### NoSQL — colonnes larges (Wide Column)

Données stockées par colonne plutôt que par ligne. Efficace pour les grandes quantités de données avec des lectures de colonnes spécifiques.

Exemples : Apache Cassandra, HBase, Google Bigtable.

### NoSQL — graphe

Modélise des entités (nœuds) et leurs relations (arêtes) avec des propriétés.

Exemples : Neo4j, ArangoDB, Amazon Neptune, TigerGraph.

### Temporelles et séries temporelles

Optimisées pour les données horodatées (métriques, logs, IoT).

Exemples : InfluxDB, TimescaleDB, Prometheus.

### Spatiales

Stockent et interrogent des données géographiques (points, polygones, trajets).

Exemples : PostGIS (extension PostgreSQL), MongoDB (index géospatiaux).

## ACID

Les propriétés ACID garantissent la fiabilité des transactions dans les SGBDR.

**Atomicité** : une transaction est tout ou rien. Si une étape échoue, toutes les modifications sont annulées (rollback). Exemple : un virement bancaire débite A et crédite B dans la même transaction — si le crédit échoue, le débit est annulé.

**Cohérence** : une transaction amène la base d'un état valide à un autre état valide. Les contraintes d'intégrité sont toujours respectées (clés étrangères, contraintes CHECK, unicité).

**Isolation** : les transactions concurrentes n'interfèrent pas les unes avec les autres. Chaque transaction voit la base comme si elle s'exécutait seule. Le niveau d'isolation est configurable (voir ci-dessous).

**Durabilité** : une fois une transaction committée, ses modifications persistent même en cas de panne système (écriture dans les logs WAL avant de confirmer).

### Niveaux d'isolation

| Niveau | Dirty Read | Non-Repeatable Read | Phantom Read |
|---|---|---|---|
| READ UNCOMMITTED | Possible | Possible | Possible |
| READ COMMITTED | Impossible | Possible | Possible |
| REPEATABLE READ | Impossible | Impossible | Possible |
| SERIALIZABLE | Impossible | Impossible | Impossible |

Plus le niveau est élevé, plus l'isolation est forte mais plus les performances diminuent.

## Théorème CAP

Pour une base de données distribuée, il est impossible de garantir simultanément les trois propriétés suivantes :

**Cohérence (Consistency)** : tous les nœuds voient les mêmes données au même moment.

**Disponibilité (Availability)** : chaque requête reçoit une réponse (pas forcément la plus récente).

**Tolérance aux partitions (Partition Tolerance)** : le système continue de fonctionner malgré des pannes de communication entre nœuds.

En pratique, les partitions réseau sont inévitables → il faut choisir entre C et A en cas de partition :

- **CP** (cohérence + partition) : MongoDB, HBase, Zookeeper — préfèrent l'indisponibilité à l'incohérence
- **AP** (disponibilité + partition) : Cassandra, DynamoDB, CouchDB — acceptent une cohérence éventuelle
- **CA** (cohérence + disponibilité) : impossible en vrai distribué

## Extension PACELC

Complète CAP : même sans partition, il existe un compromis entre **Latence** et **Cohérence**.

## Principaux acteurs du marché

| SGBD | Type | Licence | Points forts |
|---|---|---|---|
| PostgreSQL | Relationnel | Open Source | Extensible, SQL avancé, JSONB, performance |
| MySQL | Relationnel | Open Source / Oracle | Très répandu, MySQL 8 très amélioré |
| SQLite | Relationnel | Open Source | Embarqué, zéro configuration |
| Oracle | Relationnel | Propriétaire | Entreprise, très riche en fonctionnalités |
| Microsoft SQL Server | Relationnel | Propriétaire | Écosystème .NET/Windows |
| MongoDB | Document | SSPL | Schéma flexible, développement rapide |
| Redis | Clé-valeur | BSD | Ultra-rapide, structures de données riches |
| Cassandra | Colonnes larges | Apache | Scalabilité linéaire, haute disponibilité |
| Neo4j | Graphe | GPL / Enterprise | Requêtes de graphes (Cypher), performant |
| Elasticsearch | Document/Search | Elastic License | Recherche full-text, analytics, logs |
| InfluxDB | Série temporelle | MIT / Enterprise | IoT, métriques, haute fréquence |

## Quand choisir quel type

| Besoin | Type recommandé | Exemple de SGBD |
|---|---|---|
| Transactions complexes, intégrité forte | Relationnel | PostgreSQL, MySQL |
| Cache rapide, sessions | Clé-valeur | Redis |
| Données semi-structurées, schéma flexible | Document | MongoDB |
| Logs, métriques, IoT | Série temporelle | InfluxDB, TimescaleDB |
| Réseaux sociaux, recommandations | Graphe | Neo4j |
| Big Data, analytics en colonnes | Colonnes larges | Cassandra, HBase |
| Recherche full-text | Search engine | Elasticsearch |
| Application mobile embarquée | Relationnel léger | SQLite |
