---
title: Encodages
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [encodage, base64, hex, ascii, unicode, url-encoding, sécurité]
date: 2026-03-22
---

# Encodages

La maîtrise des encodages est indispensable en sécurité : les payloads sont souvent encodés pour contourner des filtres, les données binaires transitent encodées, et la confusion entre encodage et chiffrement est une source fréquente de vulnérabilités.

## ASCII et représentations de base

ASCII code 128 caractères sur 7 bits (0–127). La table étendue (Latin-1, ISO-8859-1) ajoute 128 caractères de 128 à 255.

```
Caractère  Décimal  Hex   Binaire
A          65       0x41  0100 0001
a          97       0x61  0110 0001
0          48       0x30  0011 0000
\n         10       0x0A  0000 1010
\0 (null)  0        0x00  0000 0000
espace     32       0x20  0010 0000
```

```bash
# Conversions rapides
printf '%d\n' "'A"          # → 65 (décimal)
printf '%x\n' 65            # → 41 (hex)
printf '%o\n' 65            # → 101 (octal)
echo -n 'A' | xxd           # → 0000000: 41                    A
python3 -c "print(ord('A'))" # → 65
python3 -c "print(chr(65))"  # → A
```

## Hexadécimal

Représentation en base 16 (0-9, A-F). Chaque octet = 2 chiffres hex.

```bash
# Encoder en hex
echo -n "hello" | xxd -p          # → 68656c6c6f
echo -n "hello" | od -A x -t x1z  # Format alternatif
python3 -c "print('hello'.encode().hex())"  # → 68656c6c6f

# Décoder depuis hex
echo "68656c6c6f" | xxd -r -p     # → hello
python3 -c "print(bytes.fromhex('68656c6c6f').decode())"

# Bytes magiques courants (identification de fichiers)
FF D8 FF      → JPEG
89 50 4E 47   → PNG
50 4B 03 04   → ZIP (et Office XML, JAR)
AC ED 00 05   → Java serialisé
25 50 44 46   → PDF (%PDF)
7F 45 4C 46   → ELF (binaire Linux)
4D 5A         → PE (exécutable Windows, MZ)
```

## Base64

Encode des données binaires en ASCII printable en utilisant 64 caractères (A-Z, a-z, 0-9, +, /). Chaque groupe de 3 octets → 4 caractères. Le padding `=` complète si nécessaire.

```bash
# Encoder
echo -n "Hello, World!" | base64   # → SGVsbG8sIFdvcmxkIQ==
echo -n "admin:password" | base64  # → YWRtaW46cGFzc3dvcmQ=

# Décoder
echo "SGVsbG8sIFdvcmxkIQ==" | base64 -d   # → Hello, World!

# Fichier binaire
base64 shell.exe > shell_b64.txt
base64 -d shell_b64.txt > shell_restored.exe

# En Python
import base64
base64.b64encode(b"Hello")          # → b'SGVsbG8='
base64.b64decode(b"SGVsbG8=")      # → b'Hello'
```

### Variantes de Base64

| Variante | Différences | Usage |
|---|---|---|
| Base64 standard | `+` `/` `=` | MIME, HTTP |
| Base64 URL-safe | `-` `_` sans `=` | JWT, URLs |
| Base32 | A-Z, 2-7, padding `=` | TOTP, codes de sauvegarde |
| Base58 | Pas de 0, O, l, I | Bitcoin, IPFS |

```python
import base64

# URL-safe
base64.urlsafe_b64encode(b"Hello+World")
base64.urlsafe_b64decode("SGVsbG8rV29ybGQ=")

# Reconnaître du Base64 : longueur multiple de 4, caractères [A-Za-z0-9+/=]
# JWT = trois blocs base64url séparés par des points
# eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWxpY2UifQ.signature
```

## URL Encoding (Percent Encoding)

Encode les caractères non-ASCII ou réservés dans les URLs sous la forme `%XX`.

```
Espace  → %20
!       → %21
"       → %22
#       → %23
%       → %25
&       → %26
'       → %27
/       → %2F
:       → %3A
=       → %3D
?       → %3F
@       → %40
<       → %3C
>       → %3E

# Double encodage
%       → %25
%25     → %2525 (double encodé)
```

```python
from urllib.parse import quote, unquote, quote_plus

quote("Hello World!")         # → 'Hello%20World%21'
quote_plus("Hello World!")    # → 'Hello+World%21' (+ pour les espaces)
unquote("%48%65%6C%6C%6F")   # → 'Hello'

# Bypass de filtres par encodage
# Si le filtre cherche "script" mais pas "%73%63%72%69%70%74"
quote("script")  # → '%73%63%72%69%70%74'
```

## Unicode et UTF-8

UTF-8 encode les caractères Unicode sur 1 à 4 octets :

```
U+0000 à U+007F  → 1 octet  (compatibilité ASCII)
U+0080 à U+07FF  → 2 octets
U+0800 à U+FFFF  → 3 octets  (CJK, etc.)
U+10000 à U+10FFFF → 4 octets  (emojis, etc.)

Exemples :
'A'  → 0x41          (1 octet)
'é'  → 0xC3 0xA9     (2 octets, U+00E9)
'€'  → 0xE2 0x82 0xAC (3 octets, U+20AC)
'😀' → 0xF0 0x9F 0x98 0x80 (4 octets, U+1F600)
```

### Confusions Unicode en sécurité

```python
# Homoglyphes — caractères visuellement identiques
'а' != 'a'  # 'а' est le cyrillique U+0430, 'a' est U+0061
# Utilisé en phishing (paypa1.com avec chiffre 1, ou pаypal.com avec cyrillique)

# Normalisation Unicode (NFC, NFD, NFKC, NFKD)
# Deux représentations Unicode du même caractère peuvent passer différemment
# à travers des filtres de sécurité

# Exemple : 'ﬁ' (ligature fi, U+FB01) → normalisé en 'fi' par NFKC
import unicodedata
unicodedata.normalize('NFKC', 'ﬁle')  # → 'file'

# Overlong UTF-8 (obsolète mais historique)
# '/' → 0x2F (normal) ou 0xC0 0xAF (overlong invalide)
# CVE-2000-0884 : IIS acceptait les encodages overlong → traversée de répertoire
```

## HTML Encoding

Encode les caractères spéciaux HTML pour les afficher comme texte :

```
&  → &amp;
<  → &lt;
>  → &gt;
"  → &quot;
'  → &#x27; ou &apos;

# Encodage numérique (décimal ou hex)
<  → &#60;  ou &#x3C;
>  → &#62;  ou &#x3E;
A  → &#65;  ou &#x41;

# Payloads XSS bypassing des filtres
<script>alert(1)</script>
# Si < et > sont filtrés mais pas les entités HTML dans les attributs :
<img onerror="&#x61;&#x6C;&#x65;&#x72;&#x74;&#x28;&#x31;&#x29;" src=x>
```

## Chaînes multi-encodages

```
Payload XSS après différents encodages :

1. Clair           : <script>alert(1)</script>
2. URL encode      : %3Cscript%3Ealert%281%29%3C%2Fscript%3E
3. Double URL      : %253Cscript%253E...
4. HTML entities   : &#x3C;script&#x3E;alert(1)&#x3C;/script&#x3E;
5. Base64          : PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
6. Unicode         : \u003cscript\u003e...
```

## Outils en ligne de commande

```bash
# Décoder rapidement n'importe quoi
echo "SGVsbG8=" | base64 -d             # base64
echo "48 65 6c 6c 6f" | xxd -r -p      # hex vers ASCII
python3 -c "import urllib.parse; print(urllib.parse.unquote('%48%65%6c%6c%6f'))"

# CyberChef (outil web) — "Magic" détecte et décode automatiquement
# https://gchq.github.io/CyberChef/

# Identifier l'encodage d'un texte inconnu
python3 -c "
data = 'SGVsbG8gV29ybGQ='
# Tenter base64
try:
    import base64
    print('Base64:', base64.b64decode(data))
except: pass
# Tenter hex
try:
    print('Hex:', bytes.fromhex(data))
except: pass
"

# Hachage (one-way, pas un encodage)
echo -n "password" | md5sum        # → 5f4dcc3b5aa765d61d8327deb882cf99
echo -n "password" | sha256sum     # → 5e884898da28...
echo -n "password" | sha512sum

# Identifier un hash par sa longueur
# MD5    → 32 hex chars
# SHA-1  → 40 hex chars
# SHA-256 → 64 hex chars
# SHA-512 → 128 hex chars
# bcrypt  → commence par $2a$ ou $2b$, 60 chars
```

## Erreurs courantes en sécurité

```
Encodage ≠ chiffrement — Base64 est réversible sans clé
→ Stocker des secrets en Base64 ne les protège pas

ROT13 / César — chiffrement de substitution trivial
→ Jamais utiliser pour des données sensibles

Encodage insuffisant contre les injections
→ Le contexte d'injection détermine l'encodage nécessaire :
   HTML body : &lt; &gt; &amp;
   Attribut HTML : + encodage des guillemets
   URL : percent-encoding
   JavaScript : \uXXXX ou \xXX
   SQL : paramètres préparés (pas d'encodage)

Double encodage pour bypasser des filtres
→ Si le serveur décode une fois puis le WAF une fois → race condition d'encodage
→ Toujours décoder complètement avant de filtrer
```
