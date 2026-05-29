---
title: "curl — Référence complète"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2025-02-15"
---

# curl — Référence complète

`curl` est l'outil en ligne de commande de référence pour transférer des données via des URLs. Indispensable pour les APIs, les tests web, le debug HTTP, et la sécurité.

## Syntaxe de base

```bash
curl [options] <URL>
```

## Requêtes HTTP de base

```bash
# GET (défaut)
curl https://api.example.com/users

# Afficher les headers de réponse
curl -i https://example.com          # Headers + body
curl -I https://example.com          # Headers seulement (HEAD request)
curl -v https://example.com          # Mode verbose (headers req + resp + corps)
curl -s https://example.com          # Silent (pas de barre de progression)
curl -o /dev/null https://example.com  # Ignorer le body

# POST avec données form
curl -X POST -d "username=admin&password=test" https://example.com/login

# POST avec JSON
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "test"}' \
     https://api.example.com/login

# PUT
curl -X PUT \
     -H "Content-Type: application/json" \
     -d '{"name": "John"}' \
     https://api.example.com/users/1

# DELETE
curl -X DELETE https://api.example.com/users/1

# PATCH
curl -X PATCH \
     -H "Content-Type: application/json" \
     -d '{"email": "new@example.com"}' \
     https://api.example.com/users/1
```

## Headers

```bash
# Ajouter des headers personnalisés
curl -H "Authorization: Bearer eyJhbGci..." https://api.example.com/data
curl -H "X-API-Key: abc123" https://api.example.com/data
curl -H "Accept: application/json" https://api.example.com/data

# Plusieurs headers
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer token123" \
     -H "X-Custom-Header: value" \
     https://api.example.com/endpoint

# User-Agent personnalisé
curl -A "Mozilla/5.0 (compatible; MyBot/1.0)" https://example.com

# Referer
curl -e "https://google.com" https://example.com

# Cookie
curl -b "session=abc123; csrf=xyz" https://example.com
curl -b cookies.txt https://example.com    # Depuis un fichier
curl -c cookies.txt https://example.com    # Sauvegarder les cookies
curl -b cookies.txt -c cookies.txt https://example.com  # Les deux
```

## Authentification

```bash
# Basic auth
curl -u admin:password https://example.com
curl http://admin:password@example.com     # Dans l'URL

# Digest auth
curl --digest -u admin:password https://example.com

# Bearer token
curl -H "Authorization: Bearer eyJhbGci..." https://api.example.com

# API Key dans le header
curl -H "X-API-Key: your_api_key" https://api.example.com

# API Key dans l'URL (moins sécurisé)
curl "https://api.example.com/data?api_key=your_key"

# Client certificate (mutual TLS)
curl --cert client.crt --key client.key https://example.com

# Kerberos
curl --negotiate -u : https://kerberos-protected.example.com
```

## Téléchargement et upload

```bash
# Télécharger avec le nom original
curl -O https://example.com/file.zip

# Avec nom personnalisé
curl -o myfile.zip https://example.com/file.zip

# Reprendre un téléchargement interrompu
curl -C - -O https://example.com/large_file.iso

# Téléchargements parallèles (plusieurs URLs)
curl -O https://example.com/file1.zip -O https://example.com/file2.zip

# Upload de fichier (multipart form)
curl -F "file=@/path/to/file.pdf" https://example.com/upload
curl -F "file=@/path/to/image.jpg;type=image/jpeg" \
     -F "title=My Image" \
     https://example.com/upload

# Upload raw (binary)
curl -X POST \
     -H "Content-Type: application/octet-stream" \
     --data-binary @/path/to/file.bin \
     https://api.example.com/files

# Téléchargement en streaming (stdin vers command)
curl -s https://example.com/script.sh | bash  # Dangereux ! Vérifier avant d'exécuter
```

## TLS / SSL

```bash
# Désactiver la vérification du certificat (non sécurisé — labs uniquement)
curl -k https://self-signed.example.com
curl --insecure https://self-signed.example.com

# Utiliser une CA bundle personnalisée
curl --cacert /path/to/ca-bundle.crt https://example.com

# Spécifier la version TLS
curl --tls-max 1.2 https://example.com    # TLS 1.2 max
curl --tlsv1.3 https://example.com        # TLS 1.3 minimum

# Voir les détails du certificat
curl -v https://example.com 2>&1 | grep -A 30 "SSL connection"

# Pinning de certificat
curl --pinnedpubkey sha256//base64hash https://example.com
```

## Proxy et tunneling

```bash
# Via proxy HTTP
curl -x http://proxy.example.com:8080 https://target.com
curl --proxy http://proxy.example.com:8080 https://target.com

# Via proxy SOCKS5 (Tor)
curl --socks5 127.0.0.1:9050 https://example.com
curl --socks5-hostname 127.0.0.1:9050 https://onion.address.onion  # Résolution DNS via Tor

# Via Burp Suite (intercept)
curl -x http://127.0.0.1:8080 -k https://example.com

# Variables d'environnement pour proxy global
export http_proxy=http://proxy:8080
export https_proxy=http://proxy:8080
curl https://example.com   # Utilisera le proxy automatiquement
```

## Redirections

```bash
# Suivre les redirections HTTP 301/302 (jusqu'à 30 par défaut)
curl -L https://short.url/xyz

# Limiter le nombre de redirections
curl -L --max-redirs 5 https://example.com

# Ne pas suivre mais voir la redirection
curl -v https://example.com  # Voir le Location header
```

## Debug et diagnostic

```bash
# Verbose (voir la requête et réponse complètes)
curl -v https://example.com

# Trace complète (ASCII)
curl --trace-ascii /tmp/trace.txt https://example.com

# Tempo des opérations réseau
curl -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" \
     -o /dev/null -s https://example.com

# Résultat structuré (JSON)
curl -w '{"dns":"%{time_namelookup}","connect":"%{time_connect}","total":"%{time_total}","http_code":"%{http_code}"}' \
     -o /dev/null -s https://example.com | python3 -m json.tool

# Code HTTP seulement
curl -o /dev/null -s -w "%{http_code}" https://example.com

# IP résolue
curl -v https://example.com 2>&1 | grep "Connected to"

# Forcer une IP (résoudre un hostname vers une IP spécifique)
curl --resolve example.com:443:1.2.3.4 https://example.com
```

## Usage pour la sécurité

### Test d'endpoints API

```bash
# Tester une API REST
curl -s -X GET \
     -H "Authorization: Bearer $TOKEN" \
     -H "Accept: application/json" \
     https://api.example.com/v1/users | python3 -m json.tool

# Tester les méthodes HTTP disponibles
curl -X OPTIONS -v https://example.com/api/ 2>&1 | grep -i allow

# Tester les en-têtes de sécurité
curl -I https://example.com | grep -i "strict-transport\|content-security\|x-frame\|x-content-type"

# Injection SQL dans un paramètre
curl "https://example.com/search?q=test'--"

# SSRF test
curl -X POST -d '{"url":"http://169.254.169.254/latest/meta-data/"}' \
     https://example.com/api/fetch
```

### Tester des headers de sécurité

```bash
# Vérifier HSTS
curl -sI https://example.com | grep -i strict

# Vérifier CSP
curl -sI https://example.com | grep -i content-security

# Vérifier X-Frame-Options
curl -sI https://example.com | grep -i frame

# Tester si HTTP redirige vers HTTPS
curl -v http://example.com 2>&1 | grep -i location
```

### Brute force et énumération

```bash
# Tester des mots de passe (basique)
while IFS= read -r pass; do
    code=$(curl -o /dev/null -s -w "%{http_code}" \
                -X POST -d "username=admin&password=$pass" \
                https://example.com/login)
    if [ "$code" = "302" ] || [ "$code" = "200" ]; then
        echo "Password found: $pass"
        break
    fi
done < passwords.txt

# Tester des chemins web
for path in admin login panel wp-admin .git config.php; do
    code=$(curl -o /dev/null -s -w "%{http_code}" "https://example.com/$path")
    [ "$code" != "404" ] && echo "$path: $code"
done
```

### APIs de sécurité

```bash
# VirusTotal — analyser un hash
curl -s --request GET \
     --url "https://www.virustotal.com/api/v3/files/$SHA256" \
     --header "x-apikey: $VT_API_KEY" | python3 -m json.tool

# Shodan
curl -s "https://api.shodan.io/shodan/host/8.8.8.8?key=$SHODAN_KEY" | python3 -m json.tool

# Have I Been Pwned — vérifier si un email est dans une fuite
curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/test@example.com" \
     -H "hibp-api-key: $HIBP_KEY"

# Rechercher des informations de domaine
curl -s "https://api.certspotter.com/v1/issuances?domain=example.com&include_subdomains=true&expand=dns_names"

# Certificate Transparency (crt.sh)
curl -s "https://crt.sh/?q=%25.example.com&output=json" | python3 -m json.tool | grep name_value
```

## Formats de données

```bash
# Envoyer du JSON
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"key": "value", "array": [1, 2, 3]}' \
     https://api.example.com

# Envoyer du JSON depuis un fichier
curl -X POST \
     -H "Content-Type: application/json" \
     -d @data.json \
     https://api.example.com

# Form data (application/x-www-form-urlencoded)
curl -d "key1=value1&key2=value2" https://example.com

# Multipart
curl -F "name=John" -F "file=@photo.jpg" https://example.com/upload

# XML
curl -X POST \
     -H "Content-Type: application/xml" \
     -d '<root><element>value</element></root>' \
     https://api.example.com
```

## Options pratiques

| Option | Raccourci | Description |
|--------|-----------|-------------|
| `--verbose` | `-v` | Afficher le détail de la requête/réponse |
| `--head` | `-I` | Requête HEAD (headers seulement) |
| `--include` | `-i` | Inclure les headers dans la sortie |
| `--silent` | `-s` | Pas de barre de progression |
| `--output FILE` | `-o` | Sauvegarder dans un fichier |
| `--remote-name` | `-O` | Sauvegarder avec le nom distant |
| `--location` | `-L` | Suivre les redirections |
| `--request METHOD` | `-X` | Méthode HTTP |
| `--header HEADER` | `-H` | Ajouter un header |
| `--data DATA` | `-d` | Corps de la requête |
| `--form FIELD` | `-F` | Champ multipart |
| `--user USER:PASS` | `-u` | Authentification |
| `--cookie COOKIES` | `-b` | Envoyer des cookies |
| `--cookie-jar FILE` | `-c` | Sauvegarder les cookies |
| `--insecure` | `-k` | Désactiver vérif. TLS |
| `--proxy URL` | `-x` | Utiliser un proxy |
| `--max-time SECS` | `-m` | Timeout global |
| `--connect-timeout` | | Timeout de connexion |
| `--retry N` | | Réessayer N fois |
| `--parallel` | `-Z` | Requêtes en parallèle |

## Exemples pratiques composés

```bash
# API REST complète : créer, lire, mettre à jour, supprimer
BASE="https://api.example.com/v1"
TOKEN="eyJhbGci..."

# Créer
curl -s -X POST "$BASE/items" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "item1"}' | jq .id

# Lire
curl -s -X GET "$BASE/items/123" \
     -H "Authorization: Bearer $TOKEN" | jq .

# Mettre à jour
curl -s -X PUT "$BASE/items/123" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "updated_item1"}' | jq .

# Supprimer
curl -s -X DELETE "$BASE/items/123" \
     -H "Authorization: Bearer $TOKEN" -w "%{http_code}"

# Health check en boucle
while true; do
    code=$(curl -o /dev/null -s -w "%{http_code}" --max-time 5 https://example.com/health)
    echo "$(date): $code"
    sleep 30
done
```
