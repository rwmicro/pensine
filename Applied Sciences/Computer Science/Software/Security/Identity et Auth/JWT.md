---
title: "JWT (JSON Web Token)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-25"
---

# JWT (JSON Web Token)

Un JWT (RFC 7519) est un token auto-porteur : il contient lui-même les informations nécessaires à sa vérification, sans consulter de base de données. Il est utilisé pour l'authentification stateless et l'échange d'informations entre services.

## Flux d'utilisation typique

```
   Client (navigateur, mobile)        Auth Server                 Resource Server (API)
   ─────────────────────────          ───────────                  ──────────────────
            │                              │                              │
            │  1. login(user, password)    │                              │
            │ ──────────────────────────►  │                              │
            │                              │                              │
            │  2. JWT (header.payload.sig) │                              │
            │ ◄──────────────────────────  │                              │
            │                              │                              │
            │  Stocke le JWT côté client                                  │
            │  (mémoire, cookie HttpOnly...)                              │
            │                                                             │
            │  3. GET /api/resource                                       │
            │     Authorization: Bearer eyJ...                            │
            │ ─────────────────────────────────────────────────────────►  │
            │                                                             │
            │                                            4. Vérifie       │
            │                                            la signature     │
            │                                            (clé pub /       │
            │                                            secret partagé)  │
            │                                                             │
            │  5. Données protégées                                       │
            │ ◄─────────────────────────────────────────────────────────  │
```

**Pourquoi c'est stateless** : le Resource Server n'a pas besoin de consulter l'Auth Server à chaque requête. Il vérifie la signature avec la clé publique (RS256) ou le secret partagé (HS256) et fait confiance au contenu du JWT. Avantage : scalabilité. Inconvénient : impossible de révoquer un JWT côté serveur sans infrastructure additionnelle.

## Structure

Un JWT est composé de trois parties séparées par des points, chacune encodée en Base64URL (pas de padding, URL-safe) :

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIiwicm9sZSI6InVzZXIiLCJleHAiOjE3MzU2ODk2MDB9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
│─────────────────────────────────────────────│ │────────────────────────────────────────────────────────────────────────────────────────│ │─────────────────────────────────────────────│
              Header                                                 Payload                                                    Signature
```

### Header

```json
{
  "alg": "HS256",   // algorithme de signature
  "typ": "JWT"
}
```

### Payload (claims)

```json
{
  // Claims réservés (RFC 7519)
  "iss": "https://auth.example.com",   // Issuer
  "sub": "user_42",                    // Subject (identifiant de l'utilisateur)
  "aud": "https://api.example.com",    // Audience
  "exp": 1735689600,                   // Expiration (Unix timestamp)
  "nbf": 1735686000,                   // Not Before
  "iat": 1735686000,                   // Issued At
  "jti": "unique_id_123",             // JWT ID (prévenir le replay)

  // Claims publics / privés
  "name": "Alice Dupont",
  "email": "alice@example.com",
  "role": "user",
  "permissions": ["read:profile", "write:posts"]
}
```

### Signature

```
HMAC-SHA256(
  base64url(header) + "." + base64url(payload),
  secret_key
)
```

Pour RS256, la signature utilise la clé privée RSA et se vérifie avec la clé publique.

## Algorithmes

| Algorithme | Type | Clé | Usage |
|---|---|---|---|
| `HS256` / `HS384` / `HS512` | HMAC | Symétrique (secret partagé) | Services internes |
| `RS256` / `RS384` / `RS512` | RSA | Asymétrique (priv/pub) | Systèmes distribués |
| `ES256` / `ES384` / `ES512` | ECDSA | Asymétrique (priv/pub) | Performances, IoT |
| `PS256` | RSA-PSS | Asymétrique | Recommandé sur RS256 |
| `none` | Aucun | Aucune | À désactiver absolument |

## Vérification d'un JWT

```python
import jwt
from jwt import PyJWKClient

# HS256 — clé symétrique
payload = jwt.decode(
    token,
    key="secret",
    algorithms=["HS256"],
    audience="https://api.example.com"
)

# RS256 — récupérer la clé publique depuis le JWKS endpoint
jwks_client = PyJWKClient("https://auth.example.com/.well-known/jwks.json")
signing_key = jwks_client.get_signing_key_from_jwt(token)
payload = jwt.decode(
    token,
    key=signing_key.key,
    algorithms=["RS256"],
    audience="https://api.example.com"
)

# Points de vérification obligatoires :
# - Signature valide
# - exp non dépassé
# - iss correspond à l'émetteur attendu
# - aud correspond à votre application
# - alg est dans la liste blanche (jamais ["*"])
```

## Vulnérabilités et attaques

### 1. Algorithm None (`alg: none`)

Si le serveur accepte des JWT sans signature, un attaquant peut forger un token arbitraire.

```python
# JWT forgé avec alg=none
import base64, json

header  = base64.b64encode(json.dumps({"alg":"none","typ":"JWT"}).encode()).rstrip(b'=')
payload = base64.b64encode(json.dumps({"sub":"admin","role":"admin","exp":9999999999}).encode()).rstrip(b'=')

token = f"{header.decode()}.{payload.decode()}."  # signature vide

# Contre-mesure : spécifier explicitement les algorithmes autorisés
# jwt.decode(token, key, algorithms=["RS256"])  # jamais ["none"] ni ["*"]
```

### 2. Algorithm Confusion (RS256 → HS256)

Si un serveur vérifie RS256 avec sa clé publique, un attaquant peut signer un JWT en HS256 en utilisant cette même clé publique comme secret HMAC.

```python
# Attaquant : récupère la clé publique RSA du serveur
public_key = requests.get("https://api.example.com/.well-known/jwks.json")

# Forge un JWT HS256 signé avec la clé publique RSA
token = jwt.encode(
    {"sub": "admin", "role": "admin"},
    key=rsa_public_key_pem,    # clé publique RSA utilisée comme secret HMAC
    algorithm="HS256"
)
# Si le serveur accepte indifféremment RS256 et HS256, il vérifie avec sa clé publique → succès

# Contre-mesure : vérifier l'algorithme avant la vérification de signature
if jwt.get_unverified_header(token)["alg"] not in ALLOWED_ALGORITHMS:
    raise ValueError("Algorithm not allowed")
```

### 3. Weak Secret (HS256)

Un secret HMAC court ou prévisible peut être cracké offline.

```bash
# Cracker un JWT HS256 avec hashcat
hashcat -a 0 -m 16500 jwt_token.txt wordlist.txt

# Ou avec jwt_tool
python3 jwt_tool.py <token> -C -d wordlist.txt
```

### 4. `kid` (Key ID) Injection

Le header `kid` indique quelle clé utiliser pour vérifier la signature. S'il est utilisé dans une requête SQL ou un chemin de fichier sans validation :

```json
// Injection SQL dans kid
{"alg": "HS256", "kid": "' UNION SELECT 'attacker_secret' --"}
// Si le serveur exécute : SELECT key FROM keys WHERE kid = '...'
// Il récupère la valeur contrôlée par l'attaquant

// Path traversal dans kid
{"alg": "HS256", "kid": "../../dev/null"}
// /dev/null est vide → HMAC avec une clé vide → facile à forger
```

### 5. Expiration non vérifiée

```python
# Mauvais : decode sans vérifier exp
jwt.decode(token, key, algorithms=["HS256"], options={"verify_exp": False})

# Bon : toujours vérifier l'expiration (comportement par défaut de PyJWT)
jwt.decode(token, key, algorithms=["HS256"])
```

### 6. Sensitive Data in Payload

Le payload JWT est encodé en Base64URL, pas chiffré. Toute donnée dans le payload est lisible par quiconque possède le token.

```python
# Décoder sans vérifier (lecture du payload)
import base64, json

payload_b64 = token.split(".")[1]
payload_b64 += "=" * (4 - len(payload_b64) % 4)  # padding
payload = json.loads(base64.b64decode(payload_b64))
# Tout ce qui est là est lisible !
```

Ne jamais stocker d'informations sensibles (mots de passe, secrets) dans le payload.

## JWE — JWT chiffré

JWE (JSON Web Encryption) chiffre le payload, contrairement à JWS (JWT signé) qui le laisse lisible.

```
BASE64URL(Header).BASE64URL(Encrypted Key).BASE64URL(IV).BASE64URL(Ciphertext).BASE64URL(Tag)
```

Utiliser JWE quand le payload contient des données confidentielles qui doivent rester opaques même pour les parties tierces.

## Stockage et transmission

| Stockage | Risque | Recommandation |
|---|---|---|
| `localStorage` | XSS peut lire le token | Déconseillé pour les tokens sensibles |
| `sessionStorage` | XSS peut lire le token, perdu à la fermeture de l'onglet | Déconseillé |
| Cookie `HttpOnly; Secure; SameSite=Strict` | CSRF (atténué par SameSite) | Recommandé |
| Mémoire (variable JS) | Perdu au rechargement | Recommandé si SPA sans rechargement |

```javascript
// Transmission : header Authorization (Bearer)
fetch("/api/resource", {
    headers: { "Authorization": `Bearer ${accessToken}` }
});

// Ou cookie HttpOnly (géré automatiquement par le navigateur)
// Set-Cookie: access_token=eyJ...; HttpOnly; Secure; SameSite=Strict; Path=/api
```

## Révocation

Le JWT est stateless — une fois émis, impossible de l'invalider sans infrastructure supplémentaire.

Stratégies de révocation :
- **Short-lived tokens** (5-15 minutes) + refresh tokens rotatifs
- **Blocklist (denylist)** : stocker les JTI révoqués en cache (Redis)
- **Version claim** : incrémenter un compteur côté serveur, invalider les tokens avec version < courante

## Bonnes pratiques

```python
# Exemple de validation correcte en Python
import jwt
from datetime import datetime, timezone

def validate_jwt(token: str, expected_audience: str) -> dict:
    try:
        header = jwt.get_unverified_header(token)

        # 1. Vérifier l'algorithme avant tout
        if header.get("alg") not in {"RS256", "ES256"}:
            raise ValueError(f"Algorithme non autorisé : {header.get('alg')}")

        # 2. Récupérer la clé publique depuis JWKS
        jwks_client = PyJWKClient(JWKS_URI)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # 3. Décoder avec toutes les vérifications
        payload = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=["RS256", "ES256"],
            audience=expected_audience,
            issuer=EXPECTED_ISSUER,
            options={"require": ["exp", "iat", "iss", "aud", "sub"]}
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise ValueError("Token expiré")
    except jwt.InvalidAudienceError:
        raise ValueError("Audience invalide")
    except jwt.InvalidIssuerError:
        raise ValueError("Issuer invalide")
    except jwt.InvalidSignatureError:
        raise ValueError("Signature invalide")
```

## Pièges courants

- **`alg: none` accepté par défaut** : beaucoup de vieilles bibliothèques JWT acceptent les tokens non signés si l'algorithme est `none`. Toujours passer `algorithms=["RS256"]` explicitement (jamais `["*"]` ni `["none"]`).
- **RS256 ↔ HS256 confusion** : si le serveur appelle `decode(token, public_key)` sans spécifier l'algorithme, un attaquant peut signer un JWT en HS256 en utilisant la clé publique RSA comme secret HMAC. Le serveur vérifie avec sa propre clé publique et accepte. Toujours valider l'algorithme **avant** la signature.
- **Payload visible** : base64url n'est PAS du chiffrement. Tout ce qui est dans le payload est lisible (`echo PAYLOAD | base64 -d`). Ne jamais y stocker mots de passe, tokens, ou données sensibles.
- **Expiration jamais vérifiée** : sur certaines libs, `verify=False` ou `verify_exp=False` désactive la vérification d'expiration. Un token volé hier est toujours valide. Toujours vérifier `exp`.
- **Secret HS256 faible** : `secret`, `your-256-bit-secret`, des clés courtes ou prévisibles sont crackables en quelques secondes avec hashcat. Pour HS256, utiliser au minimum 32 octets aléatoires (idéalement passer à RS256/ES256).
- **`kid` non sanitisé** : si le `kid` est utilisé tel quel pour résoudre une clé (SQL query, file path), c'est une injection SQL ou path traversal. Toujours valider contre une whitelist.
- **localStorage pour stocker le JWT** : exposé à toute XSS. Une seule faille XSS = compromission de tous les tokens de l'application. Préférer cookie `HttpOnly; Secure; SameSite=Strict`, ou variable en mémoire dans une SPA.
- **Pas de révocation possible** : si un JWT est volé, il reste valide jusqu'à `exp`. Garder des tokens courts (5-15 min) + refresh tokens, ou maintenir une blocklist par `jti`.
- **JWT en query string** : `?token=eyJ...` apparaît dans les logs serveur, le Referer, l'historique navigateur. Toujours passer en header `Authorization`.
