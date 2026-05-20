---
title: "REST et API Design"
domain: "Applied Sciences"
subdomain: "Computer Science > Web"
tags: [sciences-appliquées, informatique, web]
date: "2026-02-25"
---

# REST et API Design

## Qu'est-ce que REST

REST (Representational State Transfer) est un style architectural défini par Roy Fielding dans sa thèse de 2000. Ce n'est pas un protocole ni un standard, mais un ensemble de contraintes qui guident la conception d'API sur le web.

## Modèle de maturité de Richardson

Hiérarchise les API HTTP selon leur respect de REST.

| Niveau | Description | Exemple |
|---|---|---|
| 0 — POX | HTTP comme tunnel, une seule URL, tout en POST | RPC via HTTP |
| 1 — Ressources | URLs distinctes par ressource | `/clients`, `/commandes` |
| 2 — Verbes HTTP | Utilisation correcte de GET/POST/PUT/DELETE | REST courant |
| 3 — HATEOAS | Liens dans les réponses (hypermedia) | REST "pur" |

La plupart des APIs modernes sont au niveau 2. Le niveau 3 est rare mais offre une découverte automatique des capacités.

## Les 6 contraintes REST

**Client-serveur** : séparation claire entre client (UI) et serveur (données/logique). Permet l'évolution indépendante de chaque côté.

**Stateless** : chaque requête contient toutes les informations nécessaires. Le serveur ne stocke aucun état de session entre deux requêtes. L'état est côté client (token JWT, cookies) ou dans la base de données.

**Cacheable** : les réponses doivent indiquer si elles peuvent être mises en cache (`Cache-Control`, `ETag`).

**Interface uniforme** : identification des ressources via des URIs, manipulation des ressources via des représentations, messages auto-descriptifs.

**Système en couches** : le client ne sait pas s'il parle directement au serveur ou à un intermédiaire (load balancer, cache, API Gateway).

**Code on demand** (optionnel) : le serveur peut envoyer du code exécutable au client (JavaScript).

## Conventions d'URL

```
# Noms au pluriel pour les collections
GET    /api/v1/clients            # Lister les clients
POST   /api/v1/clients            # Créer un client

GET    /api/v1/clients/{id}       # Obtenir un client spécifique
PUT    /api/v1/clients/{id}       # Remplacer entièrement un client
PATCH  /api/v1/clients/{id}       # Mettre à jour partiellement un client
DELETE /api/v1/clients/{id}       # Supprimer un client

# Relations imbriquées
GET    /api/v1/clients/{id}/commandes    # Commandes d'un client
POST   /api/v1/clients/{id}/commandes   # Créer une commande pour ce client

# Filtrage, tri, pagination via query parameters
GET /api/v1/clients?statut=actif&sort=nom&order=asc&page=2&limit=20
GET /api/v1/produits?categorie=informatique&prix_min=100&prix_max=500
```

**Bonnes pratiques pour les URLs** :
- Kebab-case pour les mots composés : `/commandes-clients`
- Pas de verbes dans les URLs : `/api/clients` pas `/api/getClients`
- Pas d'extensions (`.json`, `.xml`) — utiliser les headers `Accept`
- Minuscules uniquement

## Méthodes HTTP et sémantique

| Méthode | Sémantique | Idempotente | Sûre | Cache |
|---|---|---|---|---|
| GET | Lire une ressource | Oui | Oui | Oui |
| POST | Créer une ressource | Non | Non | Non |
| PUT | Remplacer entièrement | Oui | Non | Non |
| PATCH | Modifier partiellement | Non | Non | Non |
| DELETE | Supprimer | Oui | Non | Non |
| HEAD | Comme GET sans corps | Oui | Oui | Oui |
| OPTIONS | Lister les méthodes supportées | Oui | Oui | Non |

**Idempotente** : appeler N fois produit le même résultat que l'appeler une fois. Important pour les retries.

**Sûre** : n'a aucun effet de bord. Une opération GET ne doit pas modifier l'état du serveur.

**PUT vs PATCH** : PUT remplace entièrement la ressource (les champs absents sont supprimés/remis à défaut). PATCH ne modifie que les champs fournis.

## Codes de réponse HTTP

### 2xx — Succès

| Code | Nom | Usage |
|---|---|---|
| 200 OK | Succès général | GET, PUT, PATCH réussis |
| 201 Created | Ressource créée | POST réussi, inclure `Location` header |
| 202 Accepted | Traitement asynchrone | Job soumis, pas encore terminé |
| 204 No Content | Succès sans corps | DELETE réussi |

### 3xx — Redirections

| Code | Nom | Usage |
|---|---|---|
| 301 Moved Permanently | Redirection permanente | URL changée définitivement |
| 302 Found | Redirection temporaire | Rare en API REST |
| 304 Not Modified | Cache valide | Avec ETag/Last-Modified |

### 4xx — Erreurs client

| Code | Nom | Usage |
|---|---|---|
| 400 Bad Request | Requête invalide | JSON malformé, paramètre manquant |
| 401 Unauthorized | Non authentifié | Token absent ou invalide |
| 403 Forbidden | Non autorisé | Authentifié mais pas de permission |
| 404 Not Found | Ressource introuvable | ID inexistant |
| 405 Method Not Allowed | Méthode non supportée | DELETE sur une collection read-only |
| 409 Conflict | Conflit d'état | Email déjà existant |
| 422 Unprocessable Entity | Validation échouée | Données invalides sémantiquement |
| 429 Too Many Requests | Rate limit dépassé | |

### 5xx — Erreurs serveur

| Code | Nom | Usage |
|---|---|---|
| 500 Internal Server Error | Erreur inattendue | Bug, exception non gérée |
| 502 Bad Gateway | Erreur upstream | Service en aval indisponible |
| 503 Service Unavailable | Service indisponible | Maintenance, surcharge |
| 504 Gateway Timeout | Timeout upstream | |

## Format des réponses

### Corps de réponse standardisé

```json
// Succès — liste
{
  "data": [
    {"id": 1, "nom": "Alice", "email": "alice@example.com"},
    {"id": 2, "nom": "Bob", "email": "bob@example.com"}
  ],
  "meta": {
    "total": 156,
    "page": 1,
    "per_page": 20,
    "total_pages": 8
  }
}

// Succès — objet unique
{
  "data": {
    "id": 1,
    "nom": "Alice",
    "email": "alice@example.com",
    "cree_le": "2024-01-15T10:30:00Z"
  }
}

// Erreur
{
  "erreur": {
    "code": "VALIDATION_ERROR",
    "message": "Les données fournies sont invalides",
    "details": [
      {"champ": "email", "message": "Format d'email invalide"},
      {"champ": "age", "message": "L'âge doit être entre 0 et 150"}
    ]
  }
}
```

## Versioning

| Stratégie | Exemple | Avantages | Inconvénients |
|---|---|---|---|
| URL path | `/api/v1/clients` | Visible, facile | Change les URLs |
| Header | `API-Version: 2024-01-01` | URLs propres | Moins visible |
| Query param | `/clients?version=2` | Simple | Pollue les URLs |
| Content negotiation | `Accept: application/vnd.api.v2+json` | Standard HTTP | Complexe |

La stratégie URL path (`/v1/`, `/v2/`) est la plus courante et la plus claire.

## Pagination

### Offset/Limit

```
GET /api/clients?offset=40&limit=20  # Page 3 de 20
```

Simple à comprendre mais inefficace pour les grandes tables (SQL `OFFSET 1000000` lit et ignore 1 million de lignes).

### Keyset Pagination (Cursor-based)

```
# Première page
GET /api/clients?limit=20

# Réponse inclut le curseur
{
  "data": [...],
  "next_cursor": "eyJpZCI6IDIwfQ=="  # base64({"id": 20})
}

# Page suivante
GET /api/clients?after=eyJpZCI6IDIwfQ==&limit=20
```

Très efficace (utilise un index), mais ne permet pas de sauter à une page arbitraire.

## Authentification

| Méthode | Description | Usage |
|---|---|---|
| API Keys | Clé secrète dans un header (`X-API-Key`) | Services machine-à-machine |
| Bearer Token (JWT) | Token signé dans `Authorization: Bearer <token>` | Applications web/mobile |
| OAuth 2.0 | Délégation d'accès, tokens d'accès + refresh | Accès pour des tiers |
| mTLS | Certificats client + serveur | Microservices, sécurité maximale |

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-API-Key: ak_live_abc123def456
```

## Rate Limiting

Limiter le nombre de requêtes par client pour protéger l'API.

Headers de réponse standard :
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 750
X-RateLimit-Reset: 1705316400
Retry-After: 120  # en cas de 429
```

Algorithmes : Token Bucket, Leaky Bucket, Fixed Window, Sliding Window.

## HATEOAS — Niveau 3

Les réponses incluent des liens vers les actions possibles.

```json
{
  "id": 1,
  "nom": "Alice",
  "solde": 1500.00,
  "_links": {
    "self": { "href": "/api/clients/1" },
    "commandes": { "href": "/api/clients/1/commandes" },
    "modifier": { "href": "/api/clients/1", "method": "PATCH" },
    "supprimer": { "href": "/api/clients/1", "method": "DELETE" }
  }
}
```

Le client n'a pas besoin de connaître les URLs à l'avance — il les découvre dans les réponses.

## Documentation — OpenAPI/Swagger

```yaml
openapi: 3.0.3
info:
  title: API Clients
  version: 1.0.0

paths:
  /clients:
    get:
      summary: Lister les clients
      parameters:
        - name: statut
          in: query
          schema:
            type: string
            enum: [actif, inactif]
      responses:
        '200':
          description: Liste des clients
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Client'

components:
  schemas:
    Client:
      type: object
      properties:
        id:
          type: integer
        nom:
          type: string
        email:
          type: string
          format: email
```

## Bon vs mauvais design

| Pratique | Mauvais | Bon |
|---|---|---|
| Noms d'URL | `/getClients`, `/deleteUser` | `/clients`, `/users/{id}` |
| Méthodes HTTP | POST pour tout | GET/POST/PUT/DELETE appropriés |
| Codes de statut | Toujours 200, erreur dans le corps | Codes HTTP sémantiques |
| Versioning | Changer l'API sans version | `/v1/`, `/v2/` |
| Réponses d'erreur | Message vague "Erreur" | Code + message + détails |
| Filtrage | `/getClientsByStatus?s=actif` | `/clients?statut=actif` |
| Pagination | Retourner 10 000 objets | `?page=1&limit=20` |

## Postman — Test et exploration d'API

Postman est un outil graphique et programmatique pour tester, documenter et automatiser des requêtes API HTTP/REST.

### Concepts Postman

**Collection** : groupe de requêtes organisées par dossier. Peut être partagée avec une équipe ou exportée en JSON.

**Environnement** : ensemble de variables (URL de base, token, identifiants) permettant de basculer entre dev, staging et production sans modifier les requêtes.

**Variables** :

| Portée | Déclaration | Exemple |
|--------|-------------|---------|
| Global | Settings → Globals | `{{baseUrl}}` |
| Environnement | Environments | `{{apiToken}}` |
| Collection | Collection → Variables | `{{timeout}}` |
| Local | Scripts | Visible dans la requête uniquement |

```
# Utilisation des variables dans les URLs, headers, corps
{{baseUrl}}/api/v1/clients
Authorization: Bearer {{apiToken}}
```

### Requêtes

```http
# GET avec paramètres de requête
GET {{baseUrl}}/api/v1/clients?statut=actif&limit=10

# POST avec corps JSON
POST {{baseUrl}}/api/v1/clients
Content-Type: application/json

{
    "nom": "Alice Martin",
    "email": "alice@example.com"
}

# PUT (remplacement complet)
PUT {{baseUrl}}/api/v1/clients/1
Authorization: Bearer {{token}}
Content-Type: application/json

{
    "nom": "Alice Dupont",
    "email": "alice.dupont@example.com"
}

# DELETE
DELETE {{baseUrl}}/api/v1/clients/1
Authorization: Bearer {{token}}
```

### Scripts de test (JavaScript)

Postman permet d'écrire des tests en JavaScript dans les onglets **Pre-request Script** et **Tests**.

```javascript
// Tests de réponse basiques
pm.test("Status 200", () => {
    pm.response.to.have.status(200);
});

pm.test("Corps JSON valide", () => {
    const body = pm.response.json();
    pm.expect(body).to.have.property("data");
    pm.expect(body.data).to.be.an("array");
});

pm.test("Temps de réponse < 500ms", () => {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Extraire et stocker une valeur (ex: token d'auth)
const body = pm.response.json();
pm.environment.set("token", body.token);
pm.environment.set("userId", body.data.id);

// Pre-request : générer un timestamp
pm.environment.set("timestamp", new Date().toISOString());
```

### Flux d'authentification — Login automatique

```javascript
// Pre-request Script sur les requêtes protégées :
// Vérifier si le token est expiré avant chaque requête

const tokenExpiry = pm.environment.get("tokenExpiry");
const now = Date.now();

if (!tokenExpiry || now > parseInt(tokenExpiry)) {
    // Obtenir un nouveau token
    pm.sendRequest({
        url: pm.environment.get("baseUrl") + "/auth/login",
        method: "POST",
        header: { "Content-Type": "application/json" },
        body: {
            mode: "raw",
            raw: JSON.stringify({
                username: pm.environment.get("username"),
                password: pm.environment.get("password")
            })
        }
    }, (err, response) => {
        const data = response.json();
        pm.environment.set("token", data.token);
        pm.environment.set("tokenExpiry", now + 3600000); // 1h
    });
}
```

### Collection Runner et automatisation

Le **Collection Runner** exécute toutes les requêtes d'une collection en séquence. Utile pour les tests de régression.

**Newman** est la version CLI de Postman, permettant l'intégration en CI/CD :

```bash
# Installer Newman
npm install -g newman

# Exécuter une collection
newman run collection.json -e environment.json

# Générer un rapport HTML
newman run collection.json -e prod.json \
    --reporters html \
    --reporter-html-export rapport.html

# Intégration CI (exemple GitLab CI)
# newman run collection.json -e ci-env.json --bail
```

### Mock servers

Postman peut simuler une API avant qu'elle soit développée. Un mock server renvoie des réponses prédéfinies basées sur les exemples sauvegardés dans la collection.

Utile pour le développement frontend découplé du backend.

### Alternatives à Postman

| Outil | Type | Points forts |
|-------|------|-------------|
| Insomnia | Desktop | Léger, open source (Kong) |
| Thunder Client | VSCode extension | Intégré à l'éditeur |
| HTTPie | CLI | Syntaxe humaine |
| curl | CLI | Universel, scriptable |
| Bruno | Desktop | Stockage en fichiers Git |
