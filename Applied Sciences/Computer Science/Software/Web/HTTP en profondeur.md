---
title: "HTTP en profondeur"
domain: "Applied Sciences"
subdomain: "Computer Science > Web"
tags: [sciences-appliquées, informatique, web]
date: "2026-02-25"
---

# HTTP en profondeur

HTTP (HyperText Transfer Protocol) est le protocole applicatif qui structure les échanges sur le Web. Texte brut à l'origine, il a évolué en 35 ans vers un protocole binaire multiplexé reposant sur UDP.

## Historique des versions

| Version | Année | Transport | Connexions | Particularité |
|---|---|---|---|---|
| HTTP/0.9 | 1991 | TCP | 1 requête → fermeture | GET uniquement, pas d'en-têtes |
| HTTP/1.0 | 1996 | TCP | 1 requête par connexion | En-têtes, méthodes multiples |
| HTTP/1.1 | 1997 | TCP | Keep-alive, pipeline | Chunked encoding, Host obligatoire |
| HTTP/2 | 2015 | TCP + TLS | Multiplexage | Binaire, HPACK, server push |
| HTTP/3 | 2022 | QUIC (UDP) | Multiplexage sans HOL | 0-RTT, migration de connexion |

### Head-of-Line Blocking

HTTP/1.1 souffre du blocage de tête de ligne : en mode pipeline, si la première réponse est lente, toutes les suivantes attendent. HTTP/2 résout ce problème au niveau applicatif avec le multiplexage sur un seul flux TCP — mais TCP lui-même crée un HOL au niveau transport si un paquet est perdu. HTTP/3 sur QUIC résout également le HOL au niveau transport (chaque flux est indépendant).

## Structure d'une requête HTTP

```
POST /api/utilisateurs HTTP/1.1
Host: api.exemple.fr
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Accept: application/json
User-Agent: Mozilla/5.0
Content-Length: 42
Connection: keep-alive

{"nom": "Dupont", "email": "dupont@exemple.fr"}
```

Structure : ligne de requête (méthode + chemin + version), en-têtes (un par ligne), ligne vide, corps optionnel.

## Structure d'une réponse HTTP

```
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/utilisateurs/42
Cache-Control: no-store
X-Request-Id: 9a8b7c6d

{"id": 42, "nom": "Dupont"}
```

Structure : ligne de statut (version + code + message), en-têtes, ligne vide, corps.

## Méthodes HTTP

| Méthode | Sémantique | Idempotente | Sûre | Corps |
|---|---|---|---|---|
| GET | Lire une ressource | Oui | Oui | Non |
| HEAD | Métadonnées seulement | Oui | Oui | Non |
| POST | Créer / action | Non | Non | Oui |
| PUT | Remplacer entièrement | Oui | Non | Oui |
| PATCH | Modifier partiellement | Non* | Non | Oui |
| DELETE | Supprimer | Oui | Non | Optionnel |
| OPTIONS | Capacités du serveur | Oui | Oui | Non |

*PATCH peut être rendu idempotent via des documents diff JSON Patch.

**Idempotente** : appeler N fois produit le même effet qu'une fois. **Sûre** : ne modifie pas l'état du serveur.

## Codes de statut

### 1xx — Informatifs
- `100 Continue` : le client peut envoyer le corps de la requête
- `101 Switching Protocols` : changement de protocole (WebSocket upgrade)

### 2xx — Succès
- `200 OK` : succès standard
- `201 Created` : ressource créée (avec `Location`)
- `204 No Content` : succès sans corps (DELETE, PUT)
- `206 Partial Content` : réponse partielle (Range requests)

### 3xx — Redirections
- `301 Moved Permanently` : redirection permanente (cachée)
- `302 Found` : redirection temporaire
- `304 Not Modified` : le cache local est à jour
- `307 Temporary Redirect` : comme 302 mais conserve la méthode
- `308 Permanent Redirect` : comme 301 mais conserve la méthode

### 4xx — Erreurs client
- `400 Bad Request` : requête malformée
- `401 Unauthorized` : authentification requise (nom trompeur : c'est de l'authentification)
- `403 Forbidden` : authentifié mais non autorisé
- `404 Not Found` : ressource inexistante
- `405 Method Not Allowed` : méthode non supportée sur cette route
- `409 Conflict` : conflit d'état (version concurrente)
- `410 Gone` : ressource définitivement supprimée
- `422 Unprocessable Entity` : validation échouée (corps syntaxiquement correct mais sémantiquement invalide)
- `429 Too Many Requests` : rate limiting

### 5xx — Erreurs serveur
- `500 Internal Server Error` : erreur générique serveur
- `502 Bad Gateway` : le proxy n'a pas reçu de réponse valide
- `503 Service Unavailable` : serveur temporairement indisponible
- `504 Gateway Timeout` : délai dépassé vers le backend

## En-têtes importants

### En-têtes de requête courants

| En-tête | Rôle | Exemple |
|---|---|---|
| `Host` | Domaine cible (obligatoire HTTP/1.1+) | `api.exemple.fr` |
| `Authorization` | Credentials | `Bearer <token>` |
| `Accept` | Types MIME acceptés | `application/json, text/html` |
| `Accept-Encoding` | Compressions acceptées | `gzip, br, zstd` |
| `Content-Type` | Type du corps envoyé | `application/json` |
| `Content-Length` | Taille du corps en octets | `42` |
| `If-None-Match` | ETag conditionnel | `"abc123"` |
| `If-Modified-Since` | Date conditionnelle | `Wed, 21 Oct 2023 07:28:00 GMT` |
| `Range` | Requête partielle | `bytes=0-1023` |
| `Cookie` | Cookies envoyés | `session=xyz; lang=fr` |

### En-têtes de réponse courants

| En-tête | Rôle | Exemple |
|---|---|---|
| `Content-Type` | Type du corps | `application/json; charset=utf-8` |
| `Cache-Control` | Directives de cache | `max-age=3600, public` |
| `ETag` | Identifiant de version | `"d41d8cd98f00b204"` |
| `Last-Modified` | Date de dernière modif | `Wed, 21 Oct 2023 07:28:00 GMT` |
| `Location` | Redirection / URL créée | `/api/ressources/42` |
| `Set-Cookie` | Définir un cookie | `session=abc; HttpOnly; Secure` |
| `Strict-Transport-Security` | Forcer HTTPS | `max-age=31536000; includeSubDomains` |
| `X-Content-Type-Options` | Bloquer le MIME sniffing | `nosniff` |
| `X-Frame-Options` | Protéger contre le clickjacking | `DENY` |
| `Content-Security-Policy` | Politique de chargement | `default-src 'self'` |

## Cache HTTP

### Directives Cache-Control

```
# Réponse cacheable publiquement pendant 1h, revalidation possible
Cache-Control: public, max-age=3600, stale-while-revalidate=60

# Réponse privée (navigateur uniquement), durée 10 min
Cache-Control: private, max-age=600

# Ne jamais cacher
Cache-Control: no-store

# Cacher mais revalider à chaque fois (ETag)
Cache-Control: no-cache

# Indiquer que le contenu ne change jamais (assets versionnés)
Cache-Control: public, max-age=31536000, immutable
```

### Revalidation avec ETag

```
# 1. Première requête
GET /api/produits/1
→ 200 OK | ETag: "v3" | Cache-Control: max-age=0, must-revalidate

# 2. Requête suivante avec revalidation
GET /api/produits/1
If-None-Match: "v3"
→ 304 Not Modified  (le cache local est toujours valide, corps vide)
```

Le mécanisme `Last-Modified` / `If-Modified-Since` est analogue mais basé sur les dates (moins précis).

### Hiérarchie des caches

```
Client → Service Worker → Cache navigateur → Proxy (CDN) → Serveur d'origine
```

Un CDN (Content Delivery Network) est un proxy de cache géographiquement distribué. Le serveur définit les règles via `Cache-Control: public` ; le CDN respecte `Surrogate-Control` (Varnish) ou `CDN-Cache-Control`.

## Cookies

```
# Serveur envoie un cookie
Set-Cookie: session=abc123; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=3600

# Navigateur le renvoie automatiquement
Cookie: session=abc123
```

| Attribut | Rôle |
|---|---|
| `HttpOnly` | Inaccessible à JavaScript (protège contre XSS) |
| `Secure` | Transmis uniquement en HTTPS |
| `SameSite=Strict` | Non envoyé lors des requêtes cross-site (protège contre CSRF) |
| `SameSite=Lax` | Envoyé pour les navigations GET cross-site |
| `SameSite=None; Secure` | Envoyé pour toutes les requêtes (pour les iframes, OAuth) |
| `Max-Age` | Durée de vie en secondes (0 = suppression) |
| `Expires` | Date d'expiration absolue |
| `Domain` | Domaine et sous-domaines autorisés |
| `Path` | Chemin sur lequel le cookie s'applique |

## HTTPS et TLS

HTTPS = HTTP dans un tunnel TLS. TLS (Transport Layer Security) assure la confidentialité, l'intégrité et l'authentification du serveur.

### Handshake TLS 1.3 (simplifié)

```
Client                          Serveur
  |  ClientHello                   |
  |  (versions, cipher suites,     |
  |   clé publique ECDHE)          |
  |-----------------------------→  |
  |                                |
  |  ServerHello                   |
  |  (cipher suite retenu,         |
  |   clé publique ECDHE,          |
  |   certificat, Finished)        |
  |  ←-----------------------------|
  |                                |
  |  Finished (chiffré)            |
  |-----------------------------→  |
  |                                |
  |  Données applicatives (HTTP)   |
  |  ↔ ↔ ↔ ↔ ↔ ↔ ↔ ↔ ↔ ↔ ↔     |
```

TLS 1.3 réduit le handshake à **1-RTT** (ou 0-RTT pour les reconnexions, avec des risques de replay à gérer).

### Certificats X.509

Un certificat lie une clé publique à un nom de domaine, signé par une Autorité de Certification (CA). La chaîne de confiance : Root CA → CA intermédiaire → certificat du serveur. Les navigateurs embarquent un magasin de certificats racines de confiance.

Let's Encrypt fournit des certificats gratuits via le protocole ACME (défi DNS ou HTTP pour prouver la possession du domaine).

## HTTP/2

### Multiplexage

HTTP/1.1 : une requête à la fois par connexion TCP (ou besoin de plusieurs connexions parallèles, typiquement 6 par domaine). HTTP/2 : de nombreux **flux** (streams) dans une même connexion TCP, chaque flux ayant un identifiant numérique.

```
Connexion TCP unique
├── Flux 1 : GET /style.css     → 200 (stream 1 frames)
├── Flux 3 : GET /script.js     → 200 (stream 3 frames)
├── Flux 5 : GET /image.png     → 200 (stream 5 frames)
└── Flux 7 : POST /api/log      → 201 (stream 7 frames)
```

### HPACK (compression des en-têtes)

HTTP/2 compresse les en-têtes avec HPACK : une table statique (62 en-têtes courants prédéfinis) et une table dynamique (en-têtes vus dans la session). Au lieu de répéter `Content-Type: application/json` sur chaque requête, on envoie un index entier.

### Server Push

Le serveur peut envoyer des ressources proactivement via `PUSH_PROMISE` avant que le client ne les demande. En pratique peu utilisé car difficile à invalider côté cache — `103 Early Hints` est une alternative plus simple.

## HTTP/3 et QUIC

QUIC est un protocole de transport multiplexé basé sur UDP, développé par Google, standardisé en RFC 9000 (2021). Il intègre nativement le chiffrement TLS 1.3.

| Fonctionnalité | TCP+TLS | QUIC |
|---|---|---|
| Établissement connexion | 3-RTT (TCP) + 1-RTT (TLS) | 1-RTT (ou 0-RTT) |
| HOL blocking transport | Oui | Non (flux indépendants) |
| Migration de connexion | Non | Oui (Connection ID) |
| Chiffrement | Optionnel (TLS ajouté) | Intégré |

La **migration de connexion** permet à un client mobile de passer du WiFi à 4G sans recréer la connexion (la session est identifiée par un Connection ID plutôt que par le 4-tuple IP:port).

## WebSockets

WebSocket établit une connexion bidirectionnelle et persistante sur TCP. La connexion commence par un upgrade HTTP :

```
GET /ws HTTP/1.1
Host: exemple.fr
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

→ 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

Après l'upgrade, le protocole WebSocket prend la main : les deux parties envoient des **frames** (données texte ou binaires) sans overhead HTTP.

### SSE (Server-Sent Events)

SSE est plus simple : le serveur envoie des événements en streaming sur une connexion HTTP ordinaire (unidirectionnel serveur → client).

```
GET /events HTTP/1.1
Accept: text/event-stream

→ 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

data: {"temperature": 22.5}

data: {"temperature": 22.7}

event: alerte
data: {"message": "Seuil dépassé"}
id: 42
```

| Critère | WebSocket | SSE |
|---|---|---|
| Direction | Bidirectionnel | Serveur → client uniquement |
| Protocole | Propre (WS://) | HTTP standard |
| Reconnexion auto | Non (à coder) | Oui (native) |
| Binaire | Oui | Non (texte) |
| Cas d'usage | Chat, jeux, collaboration | Flux temps réel, notifications |

## CORS (Cross-Origin Resource Sharing)

Les navigateurs bloquent les requêtes cross-origin par défaut (Same-Origin Policy). CORS permet au serveur d'autoriser des origines externes.

### Requête simple (no preflight)

```
GET /api/data HTTP/1.1
Origin: https://app.exemple.fr

→ 200 OK
Access-Control-Allow-Origin: https://app.exemple.fr
```

### Requête prévalidée (preflight)

Pour les méthodes non-simple (PUT, DELETE, PATCH) ou en-têtes personnalisés, le navigateur envoie d'abord une requête OPTIONS :

```
OPTIONS /api/ressources HTTP/1.1
Origin: https://app.exemple.fr
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: Authorization

→ 204 No Content
Access-Control-Allow-Origin: https://app.exemple.fr
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
```

`Access-Control-Max-Age` met en cache la réponse preflight pendant 24h pour éviter de répéter l'OPTIONS.

## Authentification HTTP

| Mécanisme | En-tête | Sécurité | Usage |
|---|---|---|---|
| Basic Auth | `Authorization: Basic base64(user:pass)` | Faible (base64) | APIs simples en HTTPS |
| Bearer Token | `Authorization: Bearer <jwt>` | Bonne | APIs REST modernes |
| API Key | `X-API-Key: <clé>` | Moyenne | APIs publiques |
| OAuth 2.0 | Flow complexe | Haute | Délégation d'accès |
| Digest Auth | `Authorization: Digest ...` | Moyenne | Obsolète |

## Outils de débogage

### curl

```bash
# Requête GET avec en-têtes détaillés
curl -v https://api.exemple.fr/produits/1

# POST JSON avec authentification
curl -X POST https://api.exemple.fr/produits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"nom": "Widget", "prix": 9.99}'

# Suivre les redirections, limiter le temps
curl -L --max-time 5 https://exemple.fr

# Télécharger un fichier en affichant la progression
curl -O --progress-bar https://exemple.fr/fichier.zip

# Inspecter seulement les en-têtes de réponse
curl -I https://api.exemple.fr/produits
```

### httpie (outil convivial)

```bash
# GET avec affichage coloré
http GET api.exemple.fr/produits/1

# POST JSON (syntaxe simplifiée)
http POST api.exemple.fr/produits \
  Authorization:"Bearer $TOKEN" \
  nom="Widget" prix:=9.99

# Afficher seulement le corps
http --body GET api.exemple.fr/produits
```

### Wireshark / tcpdump

```bash
# Capturer le trafic HTTP sur le port 80
tcpdump -i eth0 -A port 80

# Capturer vers un fichier pour analyse Wireshark
tcpdump -i eth0 -w capture.pcap port 443
```

Pour HTTPS/TLS, il faut fournir les clés de session à Wireshark via la variable `SSLKEYLOGFILE` (Firefox/Chrome la supportent) pour déchiffrer les échanges.
