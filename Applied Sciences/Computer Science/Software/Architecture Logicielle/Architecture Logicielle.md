---
title: "Architecture Logicielle"
domain: "Applied Sciences"
subdomain: "Computer Science > Architecture Logicielle"
tags: [sciences-appliquées, informatique]
date: "2026-02-24"
---
# Architecture Logicielle

L'architecture logicielle désigne la structure de haut niveau d'un système : ses composants, leurs responsabilités, leurs interactions, et les décisions structurantes qui guident tout le développement.

## Architecture vs Design

| Dimension | Architecture | Design |
|---|---|---|
| Niveau | Macro — système entier | Micro — module, classe, fonction |
| Décisions | Structurelles, difficilement réversibles | Locales, plus facilement modifiables |
| Portée | Toutes les équipes | Un ou quelques développeurs |
| Exemples | Microservices vs monolithique | Pattern Factory dans un module |

## Attributs de qualité

Une architecture est évaluée selon des critères non fonctionnels :

- **Disponibilité** : pourcentage de temps opérationnel (SLA 99.9% = 8.7h de downtime/an)
- **Scalabilité** : horizontale (plus de machines) vs verticale (machines plus puissantes)
- **Maintenabilité** : facilité à modifier, corriger, faire évoluer
- **Sécurité** : résistance aux attaques, confidentialité, intégrité
- **Performance** : temps de réponse, débit, latence
- **Testabilité** : facilité à écrire des tests automatisés
- **Déployabilité** : fréquence et facilité des déploiements

Ces attributs sont souvent en tension. Augmenter la disponibilité via la redondance augmente la complexité.

## Styles architecturaux

### Monolithique

Toute l'application est déployée comme une seule unité.

Avantages : simple à développer au départ, facile à tester end-to-end, pas de latence réseau entre composants.

Inconvénients : scaling difficile (tout ou rien), couplage fort, déploiements risqués, temps de build qui croît.

Quand l'utiliser : équipe petite, produit en phase de découverte, faible charge prévisible.

### En couches (N-tiers)

```
Couche Présentation   — UI, API REST
Couche Application    — Use cases, orchestration
Couche Domaine        — Logique métier, entités
Couche Infrastructure — BDD, cache, services externes
```

Chaque couche ne communique qu'avec la couche immédiatement inférieure ou supérieure.

Avantages : séparation claire, facile à comprendre. Inconvénients : tendance au "sinkhole" (données qui traversent sans transformation).

### MVC — Model View Controller

Sépare les données (Model), l'affichage (View) et la logique de contrôle (Controller). Très utilisé dans les frameworks web (Django, Rails, Laravel).

Variantes : MVP pour le mobile, MVVM pour les SPA réactives.

### Event-Driven (Orienté événements)

Les composants communiquent via des événements asynchrones. Un producteur émet un événement ; des consommateurs y réagissent de façon découplée.

```
Producteur A → [Bus d'événements] → Consommateur X
Producteur B →                    → Consommateur Y
```

Avantages : couplage très faible, extensibilité, résilience. Inconvénients : flux difficile à tracer, cohérence éventuelle, gestion des messages perdus.

### Hexagonale (Ports et Adaptateurs)

La logique métier est au centre, isolée de l'infrastructure. Les "ports" sont des interfaces définies par le domaine ; les "adaptateurs" sont les implémentations concrètes.

```
[REST] [CLI]
   │      │
Port Entrant ── DOMAINE MÉTIER ── Port Sortant
                                       │      │
                                     [BDD] [Email]
```

Avantage clé : le domaine ne dépend de rien d'externe. On peut tester toute la logique métier sans base de données ni HTTP.

### CQRS — Command Query Responsibility Segregation

Le modèle de lecture et le modèle d'écriture sont séparés. Les commandes modifient l'état ; les requêtes retournent des données.

Avantage : optimiser indépendamment lecture (dénormalisée, rapide) et écriture (normalisée, cohérente). Souvent combiné avec Event Sourcing.

### Event Sourcing

L'état est reconstruit à partir d'une séquence d'événements immuables. Au lieu de `UPDATE compte SET solde = 1000`, on stocke `DépôtEffectué(500)`, `RetraitEffectué(200)`.

Avantages : audit complet, capacité de rejouer l'historique. Inconvénients : complexité importante, snapshots nécessaires pour les performances.

### Serverless (FaaS)

La logique est décomposée en fonctions stateless déclenchées par des événements. L'infrastructure est gérée par le cloud (AWS Lambda, Google Cloud Functions).

Avantages : scaling automatique à zéro, facturation à l'usage, pas de gestion de serveur. Inconvénients : cold starts, durée limitée, vendor lock-in.

### Microservices

Voir le fichier dédié `Microservices.md`.

## Critères de choix

| Critère | Question à se poser |
|---|---|
| Taille de l'équipe | Une équipe de 3 n'a pas besoin de microservices |
| Complexité du domaine | DDD si le domaine est riche et évolue |
| Besoin de scaling | Faut-il scaler une partie indépendamment ? |
| Time to market | Un monolithe se développe plus vite au départ |
| Budget infrastructure | Les microservices coûtent plus cher à opérer |

## Couplage et cohésion

**Couplage** : degré de dépendance entre deux modules. Un couplage fort signifie qu'un changement dans A force un changement dans B. On cherche un couplage faible.

**Cohésion** : degré auquel les éléments d'un module appartiennent ensemble. Une forte cohésion signifie que tout ce qui est dans un module a une raison d'être là.

Règle : forte cohésion interne, faible couplage externe.

La loi de Conway : les systèmes produits par une organisation tendent à reproduire la structure de communication de cette organisation.

## Documentation : le modèle C4

Quatre niveaux de diagrammes emboîtés (Simon Brown) :

| Niveau | Public | Contenu |
|---|---|---|
| Contexte (C1) | Tous | Le système dans son environnement |
| Conteneurs (C2) | Développeurs | Applications, BDD, services en production |
| Composants (C3) | Développeurs | Composants internes d'un conteneur |
| Code (C4) | Développeurs | Classes, fonctions — rarement nécessaire |

## Patterns d'intégration

| Mode | Couplage temporel | Complexité | Cas d'usage |
|---|---|---|---|
| Appel direct | Fort | Faible | Même processus |
| API REST/gRPC | Fort | Moyenne | Réponse immédiate nécessaire |
| Message Queue | Faible | Moyenne | Tâches asynchrones |
| Event Bus | Très faible | Élevée | Extensibilité maximale |

## Architecture Decision Records (ADR)

Document court capturant une décision architecturale : contexte, décision, alternatives, conséquences. Les ADR vivent dans le dépôt (`docs/adr/`) et constituent la mémoire du projet.

```
# ADR-001 : PostgreSQL comme base de données principale

Statut : Accepté

Contexte : Besoin d'une base relationnelle pour des transactions complexes.

Décision : PostgreSQL plutôt que MySQL.

Conséquences :
- Accès à JSONB, Full-text search, extensions
- Équipe déjà familière avec PostgreSQL
```
