---
title: "SQL"
domain: "Applied Sciences"
subdomain: "Computer Science > Bases de Données"
tags: [sciences-appliquées, informatique]
date: "2026-02-24"
---

# SQL

SQL (Structured Query Language) est le langage standard pour interagir avec les bases de données relationnelles. Il comprend plusieurs sous-langages selon le type d'opération.

## Sous-langages SQL

| Sous-langage | Signification | Commandes |
|---|---|---|
| DDL | Data Definition Language | CREATE, ALTER, DROP, TRUNCATE |
| DML | Data Manipulation Language | SELECT, INSERT, UPDATE, DELETE |
| DCL | Data Control Language | GRANT, REVOKE |
| TCL | Transaction Control Language | BEGIN, COMMIT, ROLLBACK, SAVEPOINT |

## DDL — Définition des structures

```sql
-- Créer une table
CREATE TABLE clients (
    id          SERIAL PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    date_naissance DATE,
    solde       DECIMAL(10, 2) DEFAULT 0.00,
    cree_le     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer une table avec clé étrangère
CREATE TABLE commandes (
    id          SERIAL PRIMARY KEY,
    client_id   INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    total       DECIMAL(10, 2) NOT NULL,
    statut      VARCHAR(20) DEFAULT 'en_attente',
    cree_le     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Modifier une table
ALTER TABLE clients ADD COLUMN telephone VARCHAR(20);
ALTER TABLE clients ALTER COLUMN nom TYPE VARCHAR(200);
ALTER TABLE clients DROP COLUMN telephone;

-- Supprimer une table
DROP TABLE commandes;         -- Erreur si des données existent
DROP TABLE commandes CASCADE; -- Supprime aussi les tables dépendantes

-- Vider une table (plus rapide que DELETE sans WHERE)
TRUNCATE TABLE commandes;
```

## DML — Manipulation des données

### INSERT

```sql
-- Insertion simple
INSERT INTO clients (nom, email) VALUES ('Alice Martin', 'alice@example.com');

-- Insertion multiple
INSERT INTO clients (nom, email) VALUES
    ('Bob Dupont', 'bob@example.com'),
    ('Claire Petit', 'claire@example.com');

-- Insertion avec retour (PostgreSQL)
INSERT INTO clients (nom, email)
VALUES ('David', 'david@example.com')
RETURNING id, cree_le;

-- Upsert — insérer ou mettre à jour si conflit
INSERT INTO clients (email, nom)
VALUES ('alice@example.com', 'Alice Nouvelle')
ON CONFLICT (email) DO UPDATE SET nom = EXCLUDED.nom;
```

### SELECT de base

```sql
-- Sélection complète
SELECT * FROM clients;

-- Sélection de colonnes spécifiques
SELECT nom, email FROM clients;

-- Avec alias
SELECT nom AS "Nom du client", email AS "Adresse email" FROM clients;

-- Filtrage avec WHERE
SELECT * FROM clients WHERE solde > 1000;
SELECT * FROM clients WHERE nom LIKE 'A%';     -- commence par A
SELECT * FROM clients WHERE nom ILIKE 'alice%'; -- insensible à la casse (PostgreSQL)
SELECT * FROM clients WHERE solde BETWEEN 500 AND 2000;
SELECT * FROM clients WHERE email IN ('a@x.com', 'b@x.com');
SELECT * FROM clients WHERE date_naissance IS NOT NULL;

-- Tri
SELECT * FROM clients ORDER BY nom ASC, cree_le DESC;

-- Limiter les résultats
SELECT * FROM clients ORDER BY solde DESC LIMIT 10;
SELECT * FROM clients ORDER BY solde DESC LIMIT 10 OFFSET 20; -- page 3

-- Valeurs distinctes
SELECT DISTINCT statut FROM commandes;
```

### SELECT avancé

```sql
-- Fonctions d'agrégation
SELECT COUNT(*) AS nb_clients FROM clients;
SELECT SUM(total) AS revenu_total FROM commandes;
SELECT AVG(total) AS commande_moyenne FROM commandes;
SELECT MAX(total), MIN(total) FROM commandes;

-- GROUP BY
SELECT client_id, COUNT(*) AS nb_commandes, SUM(total) AS total_achats
FROM commandes
GROUP BY client_id;

-- HAVING — filtrer sur les agrégats (après GROUP BY)
SELECT client_id, SUM(total) AS total_achats
FROM commandes
GROUP BY client_id
HAVING SUM(total) > 500
ORDER BY total_achats DESC;

-- Fonctions de fenêtrage (Window Functions)
SELECT
    nom,
    solde,
    RANK() OVER (ORDER BY solde DESC) AS rang,
    ROW_NUMBER() OVER (ORDER BY cree_le) AS numero_inscription,
    AVG(solde) OVER () AS moyenne_globale,
    SUM(solde) OVER (ORDER BY cree_le) AS solde_cumulatif
FROM clients;

-- PARTITION BY — calculer par groupe sans réduire les lignes
SELECT
    client_id,
    total,
    SUM(total) OVER (PARTITION BY client_id) AS total_par_client,
    RANK() OVER (PARTITION BY client_id ORDER BY total DESC) AS rang_commande
FROM commandes;
```

## Jointures

Les jointures combinent des données de plusieurs tables.

```sql
-- Table de référence pour les exemples
-- clients : id, nom, email
-- commandes : id, client_id, total
-- produits : id, nom, prix
-- lignes_commande : commande_id, produit_id, quantite

-- INNER JOIN — uniquement les lignes qui correspondent dans les deux tables
SELECT c.nom, co.total
FROM clients c
INNER JOIN commandes co ON c.id = co.client_id;

-- LEFT JOIN (LEFT OUTER JOIN) — tous les clients, même sans commande
SELECT c.nom, co.total
FROM clients c
LEFT JOIN commandes co ON c.id = co.client_id;
-- Les clients sans commande auront co.total = NULL

-- RIGHT JOIN — toutes les commandes, même sans client correspondant
SELECT c.nom, co.total
FROM clients c
RIGHT JOIN commandes co ON c.id = co.client_id;

-- FULL OUTER JOIN — toutes les lignes des deux tables
SELECT c.nom, co.total
FROM clients c
FULL OUTER JOIN commandes co ON c.id = co.client_id;

-- CROSS JOIN — produit cartésien (toutes les combinaisons)
SELECT c.nom, p.nom
FROM clients c
CROSS JOIN produits p;

-- Auto-jointure — joindre une table avec elle-même
SELECT e1.nom AS employe, e2.nom AS manager
FROM employes e1
LEFT JOIN employes e2 ON e1.manager_id = e2.id;

-- Jointure multi-tables
SELECT c.nom, co.id AS commande, p.nom AS produit, lc.quantite
FROM clients c
JOIN commandes co ON c.id = co.client_id
JOIN lignes_commande lc ON co.id = lc.commande_id
JOIN produits p ON lc.produit_id = p.id
WHERE co.statut = 'livree'
ORDER BY c.nom, co.id;
```

## Sous-requêtes

```sql
-- Sous-requête dans WHERE
SELECT nom FROM clients
WHERE id IN (
    SELECT client_id FROM commandes WHERE total > 1000
);

-- Sous-requête corrélée (référence à la requête externe)
SELECT c.nom,
    (SELECT COUNT(*) FROM commandes co WHERE co.client_id = c.id) AS nb_commandes
FROM clients c;

-- Sous-requête dans FROM (table dérivée)
SELECT client_id, AVG(total) AS moy
FROM (
    SELECT client_id, total
    FROM commandes
    WHERE cree_le > '2024-01-01'
) AS commandes_recentes
GROUP BY client_id;

-- EXISTS / NOT EXISTS
SELECT * FROM clients c
WHERE EXISTS (
    SELECT 1 FROM commandes co
    WHERE co.client_id = c.id AND co.total > 500
);
```

## CTE — Common Table Expressions (WITH)

```sql
-- CTE simple — améliore la lisibilité
WITH clients_actifs AS (
    SELECT DISTINCT client_id
    FROM commandes
    WHERE cree_le > CURRENT_DATE - INTERVAL '30 days'
),
totaux AS (
    SELECT client_id, SUM(total) AS total_30j
    FROM commandes
    WHERE cree_le > CURRENT_DATE - INTERVAL '30 days'
    GROUP BY client_id
)
SELECT c.nom, t.total_30j
FROM clients c
JOIN clients_actifs ca ON c.id = ca.client_id
JOIN totaux t ON c.id = t.client_id
ORDER BY t.total_30j DESC;

-- CTE récursive — pour les hiérarchies (organigramme, catégories imbriquées)
WITH RECURSIVE hierarchie AS (
    -- Cas de base : employés sans manager
    SELECT id, nom, manager_id, 0 AS niveau
    FROM employes
    WHERE manager_id IS NULL

    UNION ALL

    -- Cas récursif : employés avec manager
    SELECT e.id, e.nom, e.manager_id, h.niveau + 1
    FROM employes e
    JOIN hierarchie h ON e.manager_id = h.id
)
SELECT * FROM hierarchie ORDER BY niveau, nom;
```

## UPDATE et DELETE

```sql
-- UPDATE simple
UPDATE clients SET solde = solde + 100 WHERE id = 5;

-- UPDATE avec JOIN (PostgreSQL)
UPDATE commandes co
SET statut = 'traite'
FROM clients c
WHERE co.client_id = c.id
  AND c.email LIKE '%@vip.com'
  AND co.statut = 'en_attente';

-- UPDATE avec RETURNING
UPDATE clients SET solde = 0 WHERE id = 3 RETURNING id, nom, solde;

-- DELETE
DELETE FROM commandes WHERE cree_le < '2020-01-01';

-- DELETE avec sous-requête
DELETE FROM commandes
WHERE client_id IN (
    SELECT id FROM clients WHERE statut = 'inactif'
);
```

## Transactions

```sql
BEGIN;

UPDATE comptes SET solde = solde - 500 WHERE id = 1;
UPDATE comptes SET solde = solde + 500 WHERE id = 2;

-- Vérification
SELECT id, solde FROM comptes WHERE id IN (1, 2);

COMMIT;  -- Valider
-- ou ROLLBACK; -- Annuler

-- SAVEPOINT pour rollback partiel
BEGIN;
INSERT INTO clients (nom, email) VALUES ('Test', 'test@x.com');
SAVEPOINT point_a;
DELETE FROM clients WHERE nom = 'Test';
ROLLBACK TO SAVEPOINT point_a;  -- Annule seulement le DELETE
COMMIT;  -- Le INSERT est conservé
```

## Contraintes

```sql
-- Contraintes sur les colonnes
email VARCHAR(255) UNIQUE NOT NULL
age   INTEGER CHECK (age >= 0 AND age <= 150)
statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif', 'inactif', 'suspendu'))

-- Contrainte de table
CONSTRAINT pk_commande PRIMARY KEY (commande_id, produit_id)  -- clé composite
CONSTRAINT fk_client FOREIGN KEY (client_id) REFERENCES clients(id)
    ON DELETE RESTRICT    -- interdire la suppression si des commandes existent
    ON UPDATE CASCADE     -- propager les changements d'id

-- Ajouter/supprimer une contrainte
ALTER TABLE clients ADD CONSTRAINT chk_solde CHECK (solde >= 0);
ALTER TABLE clients DROP CONSTRAINT chk_solde;
```

## Fonctions utiles

```sql
-- Chaînes
SELECT UPPER(nom), LOWER(email), LENGTH(nom) FROM clients;
SELECT SUBSTRING(email FROM 1 FOR 5), POSITION('@' IN email) FROM clients;
SELECT CONCAT(nom, ' <', email, '>') FROM clients;
SELECT TRIM('  bonjour  '), LPAD('5', 3, '0');  -- '005'
SELECT REPLACE(nom, 'Martin', 'Dupont') FROM clients;

-- Dates
SELECT NOW(), CURRENT_DATE, CURRENT_TIME;
SELECT DATE_TRUNC('month', cree_le) AS mois FROM commandes;
SELECT EXTRACT(YEAR FROM cree_le) AS annee FROM commandes;
SELECT cree_le + INTERVAL '30 days' AS expiration FROM commandes;
SELECT AGE(CURRENT_DATE, date_naissance) FROM clients;

-- Numériques
SELECT ROUND(3.14159, 2), CEIL(3.2), FLOOR(3.8), ABS(-5);
SELECT RANDOM();  -- nombre aléatoire entre 0 et 1

-- Conditionnelles
SELECT nom,
    CASE
        WHEN solde > 1000 THEN 'premium'
        WHEN solde > 100  THEN 'standard'
        ELSE 'basic'
    END AS categorie
FROM clients;

SELECT COALESCE(telephone, email, 'inconnu') AS contact FROM clients;
SELECT NULLIF(quantite, 0) FROM lignes_commande;  -- NULL si 0
```

## Vues (Views)

Une vue est une requête SELECT sauvegardée sous forme de table virtuelle. Elle simplifie les requêtes complexes et peut contrôler l'accès aux données.

```sql
-- Créer une vue
CREATE VIEW clients_actifs AS
SELECT c.id, c.nom, c.email, COUNT(co.id) AS nb_commandes
FROM clients c
LEFT JOIN commandes co ON c.id = co.client_id
WHERE c.statut = 'actif'
GROUP BY c.id, c.nom, c.email;

-- Utiliser la vue comme une table ordinaire
SELECT * FROM clients_actifs WHERE nb_commandes > 5;

-- Recréer ou remplacer une vue
CREATE OR REPLACE VIEW clients_actifs AS
SELECT ...;  -- nouvelle définition

-- Supprimer une vue
DROP VIEW clients_actifs;

-- Vue matérialisée (PostgreSQL) — résultat stocké physiquement
CREATE MATERIALIZED VIEW stats_journalieres AS
SELECT DATE_TRUNC('day', cree_le) AS jour,
       COUNT(*) AS nb_commandes,
       SUM(total) AS chiffre_affaires
FROM commandes
GROUP BY DATE_TRUNC('day', cree_le);

-- Rafraîchir une vue matérialisée
REFRESH MATERIALIZED VIEW stats_journalieres;
REFRESH MATERIALIZED VIEW CONCURRENTLY stats_journalieres;  -- sans verrouiller
```

**Avantages des vues** :
- Simplification de requêtes complexes réutilisées
- Couche d'abstraction (changer la table sous-jacente sans impacter les clients)
- Sécurité : accorder l'accès à une vue plutôt qu'à la table entière
- Les vues matérialisées améliorent les performances des requêtes analytiques lentes

## Index

Les index accélèrent les requêtes SELECT au détriment des INSERT/UPDATE/DELETE.

```sql
-- Index simple
CREATE INDEX idx_clients_email ON clients(email);

-- Index unique
CREATE UNIQUE INDEX idx_clients_email_unique ON clients(email);

-- Index composite (ordre des colonnes important)
CREATE INDEX idx_commandes_client_statut ON commandes(client_id, statut);

-- Index partiel (uniquement sur un sous-ensemble)
CREATE INDEX idx_commandes_actives ON commandes(client_id)
WHERE statut = 'en_attente';

-- Index d'expression
CREATE INDEX idx_clients_email_lower ON clients(LOWER(email));

-- Voir les index d'une table
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'commandes';

-- Supprimer un index
DROP INDEX idx_clients_email;
```

**Quand créer un index** :
- Colonnes fréquemment utilisées dans WHERE, JOIN ON, ORDER BY
- Colonnes avec haute cardinalité (beaucoup de valeurs distinctes)
- **Éviter** : petites tables, colonnes rarement filtrées, tables avec beaucoup d'INSERT/UPDATE

## Requêtes avancées

### UNION, INTERSECT, EXCEPT

```sql
-- UNION : union sans doublons
SELECT nom, email FROM clients
UNION
SELECT nom, email FROM prospects;

-- UNION ALL : union avec doublons (plus rapide)
SELECT nom FROM clients_fr
UNION ALL
SELECT nom FROM clients_be;

-- INTERSECT : uniquement les lignes présentes dans les deux
SELECT email FROM clients
INTERSECT
SELECT email FROM newsletter;

-- EXCEPT : lignes de la première absentes de la seconde
SELECT email FROM clients
EXCEPT
SELECT email FROM desabonnes;
```

### Requêtes de pivot

```sql
-- Transformer des lignes en colonnes (CASE + GROUP BY)
SELECT
    client_id,
    SUM(CASE WHEN EXTRACT(MONTH FROM cree_le) = 1 THEN total ELSE 0 END) AS jan,
    SUM(CASE WHEN EXTRACT(MONTH FROM cree_le) = 2 THEN total ELSE 0 END) AS fev,
    SUM(CASE WHEN EXTRACT(MONTH FROM cree_le) = 3 THEN total ELSE 0 END) AS mar
FROM commandes
WHERE EXTRACT(YEAR FROM cree_le) = 2024
GROUP BY client_id;
```

### Expressions régulières

```sql
-- PostgreSQL : SIMILAR TO (SQL standard) et ~ (POSIX)
SELECT * FROM clients WHERE email SIMILAR TO '%@(gmail|yahoo)\.com';
SELECT * FROM clients WHERE nom ~ '^[A-Z][a-z]+$';  -- commence par majuscule
SELECT * FROM clients WHERE nom !~ '[0-9]';           -- pas de chiffre

-- REGEXP_REPLACE
SELECT REGEXP_REPLACE(telephone, '[^0-9]', '', 'g') AS tel_propre FROM clients;
```

## Ordre d'exécution d'une requête SELECT

```
1. FROM / JOIN  — identifier les tables sources
2. WHERE        — filtrer les lignes
3. GROUP BY     — regrouper
4. HAVING       — filtrer les groupes
5. SELECT       — calculer les colonnes à retourner
6. DISTINCT     — supprimer les doublons
7. ORDER BY     — trier
8. LIMIT/OFFSET — paginer
```

Comprendre cet ordre explique pourquoi on ne peut pas utiliser un alias de SELECT dans un WHERE (l'alias n'est pas encore calculé à ce stade).
