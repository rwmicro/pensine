---
title: Steganographie
domain: sciences-appliquées
subdomain: informatique / sécurité / cryptographie
tags: [steganographie, ctf, stegano, image, audio, sécurité]
date: 2026-03-22
---

# Steganographie

La stéganographie consiste à dissimuler des informations à l'intérieur d'un fichier "innocent" (image, audio, texte) de façon à ce que la présence du message caché ne soit pas détectable. Elle se distingue de la cryptographie qui rend le message illisible sans empêcher de savoir qu'il existe.

## Concepts fondamentaux

```
LSB (Least Significant Bit) :
  Technique la plus courante — remplacer le bit de poids faible de chaque octet
  Valeur pixel : 10110110 → 1011011[0]
  Bit caché :                         [1]
  → L'œil humain ne voit pas la différence (1/256 de différence)

  Pour une image RGB 24-bit de 1920×1080 :
  Capacité = (1920 × 1080 × 3 bits) / 8 = 777 600 octets ≈ 760 Ko

Autres méthodes :
  DCT (JPEG) : modifier les coefficients de transformée cosinus discrète
  Métadonnées : cacher des données dans EXIF, commentaires
  Espaces blancs : espaces de fin de ligne, caractères Unicode invisibles
  Fréquences audio : insérer des sons hors spectre audible
```

## Analyse d'images — CTF

### Métadonnées

```bash
# ExifTool — extraire toutes les métadonnées
exiftool image.png
exiftool -a -u image.jpg  # Tous les tags, y compris inconnus
exiftool *.jpg            # Sur plusieurs fichiers

# Informations à chercher :
# Comment → souvent utilisé pour cacher un message
# GPS coordinates → coordonnées cachées
# Date/Time → dates significatives
# Makernote → données propriétaires constructeur

# file — identifier le type réel
file image.png
# Si "image.png: JPEG image data" → extension trompeuse

# strings — extraire les chaînes imprimables
strings image.png | grep -E "[a-zA-Z0-9+/]{20,}=*"  # Rechercher du base64
strings image.png | grep -i "password\|flag\|CTF\|secret"
```

### LSB et stéganographie d'images

```bash
# steghide — cacher/extraire des données (JPEG, BMP)
# Extraire
steghide extract -sf image.jpg          # Demande le mot de passe
steghide extract -sf image.jpg -p ""    # Mot de passe vide
steghide extract -sf image.jpg -p password -xf output.txt

# Cacher
steghide embed -cf cover.jpg -sf secret.txt -p password
steghide info image.jpg  # Informations sur le contenu caché

# zsteg — PNG et BMP (ruby)
gem install zsteg
zsteg image.png               # Scan automatique de toutes les méthodes LSB
zsteg -a image.png            # Toutes les combinaisons
zsteg image.png --lsb         # LSB seulement
zsteg image.png -b 1 -o xy -p rgb  # 1 bit, ordre xy, canaux RGB

# stegsolve — outil graphique (Java)
java -jar stegsolve.jar
# → Parcourir les plans de bits, inverser les canaux, XOR entre images

# openstego — stéganographie visuelle (watermarking)
# GUI : java -jar OpenStego.jar

# Outguess
outguess -r image.jpg output.txt     # Extraire
outguess -d secret.txt cover.jpg stego.jpg  # Cacher
```

### Analyse spectrale d'images

```bash
# Chercher des patterns dans les plans de bits
python3 << 'EOF'
from PIL import Image
import numpy as np

img = Image.open("image.png").convert("RGB")
pixels = np.array(img)

# Extraire les bits LSB du canal rouge
lsb_bits = pixels[:,:,0] & 1

# Visualiser le plan LSB
lsb_img = Image.fromarray((lsb_bits * 255).astype(np.uint8))
lsb_img.save("lsb_plane.png")

# Extraire les données cachées
flat = lsb_bits.flatten()
message_bits = flat[:1000*8]  # Extraire les premiers 1000 octets
message = bytes([int(''.join(map(str, message_bits[i:i+8])), 2) for i in range(0, len(message_bits), 8)])
print(message[:100])
EOF
```

## Analyse audio

```bash
# Audacity — visualisation du spectrogramme
# Analyser le spectrogramme (View → Show Spectrogram)
# Les messages peuvent être cachés en fréquences non audibles
# ou en morse visible dans la représentation temporelle

# SoX — traitement audio en ligne de commande
sox audio.wav -n spectrogram -o spectrogram.png
# → Examiner l'image PNG du spectrogramme

# Visualisation avec Python
python3 << 'EOF'
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav

rate, data = wav.read("audio.wav")
plt.specgram(data, Fs=rate, cmap='hot')
plt.colorbar()
plt.savefig("spectrogram.png", dpi=150)
EOF

# Extraire le canal sous-auditif
# Certains messages sont cachés à >20kHz (hors plage humaine)

# Steghide fonctionne aussi avec les WAV et AU
steghide extract -sf audio.wav -p password
```

## Analyse de fichiers divers

```bash
# binwalk — extraire des fichiers embarqués dans d'autres fichiers
binwalk image.png           # Chercher des fichiers concaténés
binwalk -e image.png        # Extraire automatiquement
binwalk --dd='.*' image.png # Extraire tout

# foremost — récupération par magic bytes
foremost -i image.png -o extracted/

# Un fichier PNG peut en contenir un autre (concaténation)
# cat secret.zip >> image.png → image.png est valide ET contient le ZIP
# binwalk -e image.png → extrait le ZIP
xxd image.png | grep "PK\|7z\|Rar\|%PDF"  # Chercher d'autres signatures

# Chunks PNG cachés (PNG a une structure en "chunks")
pngcheck image.png             # Vérifier les chunks
pngcheck -v image.png          # Verbeux — chunks inhabituels
# Un chunk "tEXt" ou "zTXt" peut contenir du texte caché

# Analyse JPEG
jpeg-archive image.jpg         # Informations JPEG
identify -verbose image.jpg    # ImageMagick — toutes les infos
```

## Texte et Unicode

```bash
# Caractères Unicode invisibles cachés dans du texte
# U+200B (Zero Width Space), U+200C, U+200D, U+FEFF (BOM)
python3 -c "
text = open('suspicious.txt').read()
invisible = [c for c in text if ord(c) > 127 or ord(c) == 0]
print('Caractères non-ASCII:', len(invisible))
print(invisible[:20])
"

# Espaces de fin de ligne (trailing whitespace steganography)
# SNOW — encode dans les espaces/tabs en fin de ligne
snow -C message.txt  # Extraire
snow -C -m 'message caché' cover.txt stego.txt  # Cacher

# Base64 dans des textes d'apparence normale
strings suspicious.txt | grep -E "^[A-Za-z0-9+/]{4,}={0,2}$" | base64 -d 2>/dev/null
```

## Outils de détection (steganalyse)

```bash
# StegDetect — détecter la présence de steganographie
stegdetect image.jpg
# → Indique DCT, JSteg, F5, Outguess...

# StegoVeritas — scan automatique
pip install stegoveritas
stegoveritas image.png         # Analyse complète automatique

# Aperisolve (en ligne) — agrège plusieurs outils
# https://www.aperisolve.com

# Stegseek — bruteforce steghide (ultra-rapide)
stegseek image.jpg rockyou.txt  # Cracker le mot de passe steghide
```

## Workflow CTF

```
1. file image.xxx → identifier le vrai type
2. exiftool image.xxx → métadonnées
3. strings image.xxx | grep -i flag → chaînes
4. binwalk -e image.xxx → fichiers embarqués
5. zsteg image.png → LSB automatique (PNG)
6. steghide info image.jpg → présence de données (JPEG)
7. stegsolve → plans de bits visuels
8. Regarder le spectrogramme (audio)
9. stegseek image.jpg rockyou.txt → bruteforce mot de passe
10. aperisolve.com → scan en ligne complet
```
