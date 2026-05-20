---
title: "Modèle Relationnel"
domain: "Applied Sciences"
subdomain: "Computer Science > Bases de Données"
tags: [sciences-appliquées, informatique]
date: "2026-02-25"
---

# Modèle Relationnel

Proposé par Edgar F. Codd en 1970 dans son article fondateur "A Relational Model of Data for Large Shared Data Banks", le modèle relationnel est la base théorique de tous les SGBDR. Il repose sur la théorie des ensembles et la logique du premier ordre.

## Concepts fondamentaux

**Relation** : une table. Une relation est un ensemble de tuples, sans ordre et sans doublons. Le nom d'une relation est unique dans la base.

**Attribut** : une colonne. Chaque attribut a un nom et un domaine (type de données).

**Domaine** : l'ensemble des valeurs possibles pour un attribut. Ex : entiers entre 0 et 150, chaînes de 1 à 100 caractères.

**Tuple** : une ligne. Un tuple est une combinaison de valeurs, une par attribut.

**Schéma** : la définition de la structure d'une relation. Ex : `CLIENTS(id: INTEGER, nom: VARCHAR, email: VARCHAR)`

**Instance** : le contenu actuel d'une relation (l'ensemble des tuples à un instant donné).

## Clés

### Superclé

Tout ensemble d'attributs qui identifie de façon unique chaque tuple. Par exemple, dans CLIENTS, {id}, {email}, {id, nom}, {id, email, nom} sont toutes des superclés.

### Clé candidate

Une superclé minimale — on ne peut supprimer aucun attribut sans perdre l'unicité. {id} et {email} sont des clés candidates pour CLIENTS (si email est unique).

### Clé primaire

La clé candidate choisie comme identifiant principal. Une seule clé primaire par table. Ne peut pas être NULL.

```sql
CREATE TABLE clients (
    id    SERIAL PRIMARY KEY,   -- clé primaire
    email VARCHAR UNIQUE        -- clé candidate alternative
);
```

### Clé étrangère

Un attribut qui référence la clé primaire d'une autre table. Assure l'intégrité référentielle.

```sql
CREATE TABLE commandes (
    id        SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id)  -- clé étrangère
);
```

### Clé composite

Clé primaire composée de plusieurs attributs.

```sql
CREATE TABLE inscriptions (
    etudiant_id INTEGER REFERENCES etudiants(id),
    cours_id    INTEGER REFERENCES cours(id),
    date_inscription DATE,
    PRIMARY KEY (etudiant_id, cours_id)  -- clé composite
);
```

### Clé naturelle vs clé surrogate

| Type | Description | Exemples | Avantages | Inconvénients |
|---|---|---|---|---|
| Naturelle | Donnée du domaine | numéro_secu, ISBN, email | Signifiante | Peut changer, longue |
| Surrogate | Générée artificiellement | id SERIAL, UUID | Stable, courte, simple | Pas de signification métier |

Recommandation : utiliser des clés surrogates (SERIAL/UUID) comme clé primaire, et des contraintes UNIQUE sur les clés naturelles.

## Intégrité

### Intégrité de domaine

Chaque valeur doit appartenir au domaine de son attribut.

```sql
age  INTEGER CHECK (age BETWEEN 0 AND 150)
sexe CHAR(1)  CHECK (sexe IN ('M', 'F', 'N'))
```

### Intégrité d'entité

La clé primaire ne peut pas être NULL — sinon on ne pourrait pas identifier le tuple.

### Intégrité référentielle

Une valeur de clé étrangère doit correspondre à une valeur existante dans la table référencée (ou être NULL si autorisé).

```sql
-- Comportements sur suppression/mise à jour de la clé référencée
FOREIGN KEY (client_id) REFERENCES clients(id)
    ON DELETE CASCADE     -- supprimer les commandes si le client est supprimé
    ON DELETE RESTRICT    -- interdire la suppression du client s'il a des commandes
    ON DELETE SET NULL    -- mettre client_id à NULL
    ON DELETE SET DEFAULT -- mettre la valeur par défaut
    ON UPDATE CASCADE     -- propager les changements d'id
```

## Normalisation

La normalisation est le processus d'organisation du schéma pour réduire la redondance et éviter les anomalies de mise à jour.

### Anomalies

**Anomalie d'insertion** : impossible d'insérer des données sans en insérer d'autres. Ex : dans une table ETUDIANT_COURS_PROF où l'attribut PROF dépend de COURS, on ne peut pas enregistrer un prof sans inscriptions.

**Anomalie de mise à jour** : changer un fait nécessite de modifier plusieurs lignes. Ex : si le prof d'un cours change, il faut mettre à jour toutes les lignes de ce cours.

**Anomalie de suppression** : supprimer un fait en fait perdre un autre. Ex : supprimer le dernier étudiant inscrit à un cours efface aussi le prof de ce cours.

### 1NF — Première forme normale

Chaque cellule contient une valeur atomique (pas de listes, pas de groupes répétitifs), et chaque ligne est unique.

```
Violée :
COMMANDE(id, articles)
1, "laptop, souris, clavier"  ← articles non atomique

Respectée :
LIGNE_COMMANDE(commande_id, produit_id, quantite)
1, 101, 1
1, 102, 2
1, 103, 1
```

### 2NF — Deuxième forme normale

En 1NF ET aucun attribut non-clé ne dépend partiellement de la clé primaire (s'applique uniquement aux clés composites).

```
Violée (clé composite = etudiant_id + cours_id) :
INSCRIPTION(etudiant_id, cours_id, nom_etudiant, nom_cours, note)
   └── nom_etudiant dépend seulement de etudiant_id (dépendance partielle)
   └── nom_cours dépend seulement de cours_id (dépendance partielle)

Respectée : décomposer en
ETUDIANT(etudiant_id, nom_etudiant)
COURS(cours_id, nom_cours)
INSCRIPTION(etudiant_id, cours_id, note)
```

### 3NF — Troisième forme normale

En 2NF ET aucun attribut non-clé ne dépend d'un autre attribut non-clé (pas de dépendance transitive).

```
Violée :
EMPLOYE(emp_id, nom, dept_id, dept_nom, dept_ville)
   └── dept_nom dépend de dept_id (qui n'est pas la clé) → transitive

Respectée :
EMPLOYE(emp_id, nom, dept_id)
DEPARTEMENT(dept_id, dept_nom, dept_ville)
```

### BCNF — Forme Normale de Boyce-Codd

Variante plus stricte de la 3NF. Pour chaque dépendance fonctionnelle X → Y, X doit être une superclé.

```
Violée :
ENSEIGNEMENT(etudiant_id, matiere, prof)
   Si un prof n'enseigne qu'une matière : prof → matiere
   Mais prof n'est pas une superclé.

Respectée : décomposer en
PROF_MATIERE(prof, matiere)
INSCRIPTION(etudiant_id, prof)
```

### 4NF et 5NF

**4NF** : pas de dépendances multivaluées non triviales. S'applique quand un attribut peut avoir plusieurs valeurs indépendantes pour chaque valeur d'un autre attribut.

**5NF** : pas de dépendances de jointure. Cas très rares en pratique.

### Dénormalisation

En pratique, on dénormalise parfois pour des raisons de performance : on accepte de la redondance contrôlée pour éviter des jointures coûteuses. Les data warehouses sont généralement fortement dénormalisés (schéma en étoile ou en flocon).

## Algèbre relationnelle

L'algèbre relationnelle est le fondement mathématique du SQL. Chaque opération prend une ou deux relations en entrée et retourne une relation.

### Opérations de base

**Sélection σ** : filtre les tuples selon un prédicat.

```
σ_{salaire > 50000}(EMPLOYES) ≡ SELECT * FROM EMPLOYES WHERE salaire > 50000
```

**Projection π** : sélectionne des colonnes (élimine les doublons).

```
π_{nom, email}(CLIENTS) ≡ SELECT DISTINCT nom, email FROM CLIENTS
```

**Produit cartésien ×** : toutes les combinaisons de tuples des deux relations.

```
CLIENTS × COMMANDES ≡ SELECT * FROM CLIENTS CROSS JOIN COMMANDES
```

**Union ∪** : les tuples appartenant à l'une ou l'autre relation (mêmes attributs requis).

```
EMPLOYES_FR ∪ EMPLOYES_ES ≡ SELECT * FROM EMPLOYES_FR UNION SELECT * FROM EMPLOYES_ES
```

**Différence −** : tuples de la première relation non présents dans la seconde.

```
CLIENTS − CLIENTS_ACTIFS ≡ SELECT * FROM CLIENTS EXCEPT SELECT * FROM CLIENTS_ACTIFS
```

### Opérations dérivées

**Jointure naturelle ⋈** : combine les tuples ayant les mêmes valeurs sur les attributs communs.

```
CLIENTS ⋈ COMMANDES ≡ SELECT * FROM CLIENTS NATURAL JOIN COMMANDES
```

**Theta-jointure** : produit cartésien filtré par une condition.

```
CLIENTS ⋈_{CLIENTS.id = COMMANDES.client_id} COMMANDES ≡ INNER JOIN
```

**Division ÷** : A ÷ B retourne les tuples de A qui sont associés à tous les tuples de B. Utile pour les requêtes "pour tous".

```
-- "Clients ayant commandé TOUS les produits"
COMMANDES ÷ PRODUITS
```

## Diagramme Entité-Relation (ER)

Le diagramme ER est utilisé pour modéliser le domaine avant de créer le schéma relationnel.

Composants :
- **Entité** : objet du monde réel (CLIENT, PRODUIT, COMMANDE)
- **Attribut** : propriété d'une entité (nom, prix, date)
- **Association** : relation entre entités (CLIENT passe COMMANDE)
- **Cardinalité** : nombre de participations (1:1, 1:N, M:N)

```
CLIENT ──┤├── passe ──○├── COMMANDE ──┤├── contient ──○├── PRODUIT

1:N (un client passe plusieurs commandes)
M:N (une commande contient plusieurs produits, un produit est dans plusieurs commandes)
```

Une association M:N se traduit par une table de jonction :

```sql
-- Association M:N entre COMMANDES et PRODUITS
CREATE TABLE lignes_commande (
    commande_id INTEGER REFERENCES commandes(id),
    produit_id  INTEGER REFERENCES produits(id),
    quantite    INTEGER NOT NULL DEFAULT 1,
    prix_unitaire DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (commande_id, produit_id)
);
```
