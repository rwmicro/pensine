---
title: API Security
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [api, rest, graphql, oauth, sécurité, owasp, pentest]
date: 2026-03-22
---

# API Security

Les APIs (REST, GraphQL, gRPC) constituent la colonne vertébrale des applications modernes. Elles représentent une surface d'attaque critique car elles exposent directement la logique métier et les données.

## OWASP API Security Top 10 (2023)

| # | Vulnérabilité | Description |
|---|---|---|
| API1 | Broken Object Level Authorization | Accéder aux objets d'un autre utilisateur via leur ID |
| API2 | Broken Authentication | Tokens faibles, sessions non invalidées |
| API3 | Broken Object Property Level Authorization | Retourner des champs sensibles non nécessaires |
| API4 | Unrestricted Resource Consumption | Pas de rate limiting → DoS, coût excessif |
| API5 | Broken Function Level Authorization | Accéder à des endpoints admin sans les droits |
| API6 | Unrestricted Access to Sensitive Business Flows | Achat en masse, exploitation de workflows |
| API7 | Server-Side Request Forgery | SSRF via des paramètres d'URL dans l'API |
| API8 | Security Misconfiguration | CORS trop permissif, méthodes inutiles actives |
| API9 | Improper Inventory Management | Versions obsolètes exposées (/v1 encore actif) |
| API10 | Unsafe Consumption of APIs | Faire confiance aveuglément aux APIs tierces |

## API1 — Broken Object Level Authorization (BOLA/IDOR)

La vulnérabilité la plus fréquente. L'API n'vérifie pas que l'utilisateur est propriétaire de la ressource demandée.

```
GET /api/v1/users/1337/orders/9876
Authorization: Bearer <token_user_42>

→ Si le serveur retourne les commandes de l'user 1337 sans vérifier
  que le token appartient à cet utilisateur → BOLA
```

**Exploitation :**
```python
# Itérer sur les IDs pour accéder aux données d'autres utilisateurs
for user_id in range(1, 10000):
    r = requests.get(f"https://api.exemple.com/users/{user_id}/data",
                     headers={"Authorization": f"Bearer {my_token}"})
    if r.status_code == 200:
        print(f"User {user_id}: {r.json()}")
```

**Défense :**
```python
# Toujours vérifier côté serveur
@app.route("/api/orders/<order_id>")
@require_auth
def get_order(order_id):
    order = Order.query.get(order_id)
    if order.user_id != current_user.id:  # Vérification obligatoire
        return {"error": "Forbidden"}, 403
    return order.to_dict()

# Utiliser des UUIDs plutôt que des IDs séquentiels
# → rend l'énumération difficile mais ne remplace pas la vérification
```

## API5 — Broken Function Level Authorization

Accès à des fonctions réservées aux admins depuis un compte normal.

```
# Utilisateur normal essaie des endpoints admin
DELETE /api/v1/admin/users/42
PUT /api/v1/users/42/role {"role": "admin"}
GET /api/v1/admin/logs
POST /api/v1/internal/migrate-db
```

**Outils de découverte d'endpoints :**
```bash
# Fuzzing d'endpoints
ffuf -u https://api.exemple.com/FUZZ \
     -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt \
     -H "Authorization: Bearer $TOKEN"

# Chercher les specs OpenAPI/Swagger
GET /swagger.json
GET /api-docs
GET /openapi.yaml
GET /v1/spec
```

## API4 — Rate Limiting et Resource Consumption

```python
# Flask — Rate limiting avec Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")  # Max 5 tentatives/min par IP
def login():
    ...

@app.route("/api/search")
@limiter.limit("100 per hour")
def search():
    ...
```

**GraphQL — Prévention des attaques par complexité de requête :**
```python
# Limiter la profondeur et la complexité des requêtes
from graphql import build_schema
from graphql_depth_limit import depth_limit_validator

schema = build_schema(...)
# Limiter à 5 niveaux de profondeur
validation_rules = [depth_limit_validator(5)]
```

## Sécurité GraphQL

GraphQL présente des risques spécifiques par rapport à REST.

### Introspection

Par défaut, GraphQL expose son schéma complet via l'introspection.

```bash
# Récupérer le schéma entier
curl -X POST https://api.exemple.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{__schema{types{name fields{name type{name}}}}}"}'
```

**Désactiver en production :**
```python
# Python graphene
schema = graphene.Schema(query=Query, auto_camelcase=False)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    introspection=False  # Désactivé en production
))
```

### Injection GraphQL

```graphql
# Injection dans un argument GraphQL
query {
  user(name: "admin' OR '1'='1") {  # SQLi si mal géré
    email
    password
  }
}
```

### Batching d'attaques

GraphQL permet plusieurs requêtes en une seule requête HTTP, contournant le rate limiting par IP.

```json
[
  {"query": "mutation { login(user: \"admin\", pass: \"pass1\") { token } }"},
  {"query": "mutation { login(user: \"admin\", pass: \"pass2\") { token } }"},
  {"query": "mutation { login(user: \"admin\", pass: \"pass3\") { token } }"}
]
```

**Défense :** limiter à une requête par batch, ou implémenter un rate limiting par utilisateur (pas seulement IP).

## Authentification et autorisation API

### Bearer Tokens — Bonnes pratiques

```python
# Génération sécurisée
import secrets
token = secrets.token_urlsafe(32)  # 256 bits d'entropie

# Validation
def validate_token(token: str) -> Optional[User]:
    # Utiliser une comparaison en temps constant (anti-timing attack)
    stored_token = db.get_token(token[:8])  # Lookup partiel
    if not stored_token:
        return None
    if not secrets.compare_digest(stored_token.value, token):
        return None
    if stored_token.expires_at < datetime.utcnow():
        return None
    return stored_token.user
```

### API Keys — Stockage et rotation

```bash
# Format recommandé pour API keys
prefix_randompart
# ex: sk_live_kJ8mPqR9xN2vL5wE3fD7hA4cB6nM0pZ1
# Le préfixe permet d'identifier le type de clé dans les logs

# Hacher les API keys en base (comme des mots de passe)
import hashlib
key_hash = hashlib.sha256(api_key.encode()).hexdigest()
```

### CORS — Configuration sécurisée

```python
# Flask-CORS
from flask_cors import CORS

# MAUVAIS
CORS(app, origins="*")  # Toutes les origines

# BIEN — liste blanche explicite
CORS(app, origins=[
    "https://app.mondomaine.com",
    "https://dashboard.mondomaine.com"
], supports_credentials=True)
```

```javascript
// Node.js Express
app.use(cors({
  origin: (origin, callback) => {
    const whitelist = ['https://app.mondomaine.com'];
    if (!origin || whitelist.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 3600
}));
```

## Pentest d'API — Méthodologie

### Découverte et cartographie

```bash
# 1. Trouver la documentation
GET /swagger.json
GET /openapi.yaml
GET /api/v1/docs
GET /.well-known/openapi

# 2. Spider les endpoints depuis les apps mobiles
# Intercepter le trafic avec BurpSuite + appareil mobile/émulateur

# 3. Analyser les specs OpenAPI avec OWASP ZAP
zap-cli openapi-import --target https://api.exemple.com swagger.json

# 4. Générer des requêtes depuis la spec
docker run --rm -v $PWD:/tmp willbryant/openapi-fuzzer:latest \
  -s /tmp/swagger.json -t https://api.exemple.com
```

### Tests manuels essentiels

```bash
# Tester BOLA : accéder aux ressources d'un autre user
# Créer 2 comptes, noter les IDs, tester croisements

# Tester l'énumération d'objets
GET /api/users/1 → 200
GET /api/users/2 → 200
GET /api/users/3 → 404  # Vide
GET /api/users/4 → 200

# Tester les méthodes HTTP
OPTIONS /api/users/1 → lister les méthodes permises
PATCH /api/users/1 {"role": "admin"}  # Mass assignment ?
DELETE /api/users/1  # Droit sur d'autres users ?

# Tester les paramètres cachés
POST /api/users
{"username": "test", "email": "test@exemple.com", "role": "admin"}  # Ignoré ?
```

### Outils spécialisés API

| Outil | Usage |
|---|---|
| **Postman** | Tests manuels, collections |
| **Insomnia** | Alternative Postman, REST/GraphQL |
| **BurpSuite** | Proxy, scanner, répéteur |
| **OWASP ZAP** | Scanner automatique API |
| **Arjun** | Découverte de paramètres cachés |
| **ffuf** | Fuzzing d'endpoints et paramètres |
| **GraphQL Voyager** | Visualisation du schéma GraphQL |
| **InQL** | BurpSuite plugin pour GraphQL |

```bash
# Arjun — découverte de paramètres cachés
arjun -u https://api.exemple.com/search -m GET

# ffuf — fuzzing de paramètres
ffuf -u "https://api.exemple.com/users?FUZZ=test" \
     -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
     -fs 0  # Filtrer les réponses vides
```

## Gestion des erreurs et information leakage

```python
# MAUVAIS — expose les détails internes
@app.errorhandler(Exception)
def handle_error(e):
    return {
        "error": str(e),
        "traceback": traceback.format_exc(),  # Stack trace visible
        "query": current_query                 # Requête SQL visible
    }, 500

# BIEN — erreurs génériques en production
@app.errorhandler(Exception)
def handle_error(e):
    error_id = str(uuid.uuid4())
    logger.error(f"Error {error_id}: {e}", exc_info=True)  # Log interne
    return {
        "error": "Internal server error",
        "error_id": error_id  # Pour corrélation avec les logs
    }, 500
```
