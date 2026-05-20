---
title: Firmware Analysis
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [firmware, iot, binwalk, ghidra, analyse-binaire, sécurité, reverse-engineering]
date: 2026-03-22
---

# Firmware Analysis

L'analyse de firmware consiste à extraire et examiner le code embarqué dans des équipements IoT, routeurs, caméras IP, automates industriels. C'est une discipline de reverse engineering appliquée au hardware.

## Acquisition du firmware

### Sources en ligne

```bash
# 1. Site du fabricant — la méthode la plus simple
# Chercher "download firmware <modèle>"
# Exemples : Netgear, TP-Link, Cisco publient leurs firmwares

# 2. OpenWrt (routeurs)
# Firmwares open-source disponibles

# 3. Wayback Machine / archive.org
# Anciennes versions de firmware supprimées du site officiel

# 4. Binwalk — téléchargement direct depuis GitHub
# La base de données Firmwalker inclut des firmwares extraits
```

### Extraction directe du hardware

```bash
# UART — port série souvent accessible physiquement
# 1. Repérer les pins UART (TX, RX, GND, VCC) avec un multimètre
# 2. Connecter un adaptateur USB-UART (FTDI, CP2102)
# 3. minicom -b 115200 /dev/ttyUSB0
# → Souvent donne un shell root ou des logs de démarrage

# JTAG — interface de debug hardware
# Permet de : lire la mémoire flash, débugger l'exécution
# Outils : OpenOCD, JLinkExe

# Extraction de flash SPI/NAND
# 1. Désolidariser la puce flash (désoldering)
# 2. Lire avec un programmateur (CH341A, Raspberry Pi)
flashrom -p ch341a_spi -r firmware.bin     # Lire la puce flash SPI

# Bus Pirate — interface polyvalente (UART, SPI, I2C, JTAG)
# Bus Pirate → SPI flash → dump du firmware
```

## Extraction et analyse avec Binwalk

```bash
# Installation
pip install binwalk
# Ou : apt install binwalk

# Analyser un firmware
binwalk firmware.bin
# → Liste les signatures trouvées :
# DECIMAL  HEX      DESCRIPTION
# 0        0x0      U-Boot legacy uImage header
# 128      0x80     LZMA compressed data
# 2097152  0x200000 Squashfs filesystem

# Extraire automatiquement
binwalk -e firmware.bin              # Extraction dans _firmware.bin.extracted/
binwalk --dd='.*' firmware.bin      # Forcer l'extraction de tout
binwalk -Me firmware.bin            # Extraction récursive (-M = matryoshka)

# Entropie — détecter les zones chiffrées ou compressées
binwalk -E firmware.bin             # Graphe d'entropie
# Entropie haute et uniforme (≈0.99) → chiffré ou compressé
# Entropie moyenne → code/données

# Firmware chiffré → chercher les clés ou les routines de déchiffrement
# Parfois une version antérieure (non chiffrée) permet de comprendre le mécanisme
```

## Analyse du filesystem extrait

```bash
# Après extraction de binwalk
ls _firmware.bin.extracted/
# squashfs-root/   bin/  etc/  usr/  var/  ...

# Chercher des credentials en clair
grep -r "password\|passwd\|secret\|admin\|root" _firmware.bin.extracted/etc/ 2>/dev/null
grep -r "password" _firmware.bin.extracted/ --include="*.conf" 2>/dev/null

# Credentials hardcodés fréquents
cat _firmware.bin.extracted/etc/passwd
cat _firmware.bin.extracted/etc/shadow
cat _firmware.bin.extracted/etc/config/system  # OpenWrt

# Clés privées et certificats
find _firmware.bin.extracted/ -name "*.key" -o -name "*.pem" -o -name "*.p12" 2>/dev/null

# URLs et endpoints en clair
strings _firmware.bin.extracted/usr/sbin/httpd | grep -E "https?://[^ ]+"

# Binaires SUID (escalade de privilèges potentielle dans l'émulation)
find _firmware.bin.extracted/ -perm -u=s -type f 2>/dev/null

# Scripts de démarrage
cat _firmware.bin.extracted/etc/init.d/*
cat _firmware.bin.extracted/etc/inittab

# Clés API / tokens
grep -r "token\|api_key\|apikey" _firmware.bin.extracted/ 2>/dev/null | grep -v ".pyc"
```

## Émulation avec QEMU / Firmadyne

```bash
# Firmadyne — émulation automatique de firmware Linux embarqué
git clone https://github.com/firmadyne/firmadyne
# Voir la documentation pour la configuration de la base de données

# QEMU — émulation manuelle (ARM, MIPS, PowerPC)
# Identifier l'architecture
file _firmware.bin.extracted/bin/busybox
# → ELF 32-bit MSB executable, MIPS, MIPS32 rel2 → MIPS big-endian

# Installer les packages QEMU pour cette architecture
apt install qemu-user-static qemu-system-mips

# Émuler un binaire directement (user-mode)
copy $(which qemu-mipsel-static) _firmware.bin.extracted/
chroot _firmware.bin.extracted/ /qemu-mipsel-static /bin/busybox

# Émuler le système complet (system-mode — plus complexe)
# Nécessite un kernel MIPS compatible et une configuration réseau
qemu-system-mipsel -M malta -kernel vmlinux -hda firmware.img \
    -append "root=/dev/hda" -nographic
```

## Analyse des binaires

```bash
# Identifier l'architecture et l'ABI
file suspicious_binary
readelf -h suspicious_binary    # En-tête ELF
objdump -d suspicious_binary    # Désassemblage (si binutils pour cette archi)

# Strings — credentials, URLs, clés
strings suspicious_binary | grep -E "password|admin|http|key"
strings -el suspicious_binary   # Strings encodées little-endian (Windows)
strings -eb suspicious_binary   # Strings encodées big-endian

# Bibliothèques dynamiques utilisées
readelf -d suspicious_binary | grep NEEDED

# Symbols (si non strippé)
nm suspicious_binary
readelf -s suspicious_binary
```

### Ghidra pour le reverse engineering

```bash
# Ghidra (NSA) — décompilateur multiarchitecture gratuit
# Supporte : ARM, MIPS, PowerPC, x86, RISC-V, ...

# Démarrer Ghidra
ghidraRun

# Workflow :
# 1. New Project → Import File → firmware binary
# 2. Ghidra détecte l'architecture automatiquement
# 3. Analyser (AutoAnalyze)
# 4. Explorer le Code Browser
#    Functions → naviguer entre les fonctions
#    Decompiler → vue C pseudo-code
#    Search → chercher des strings, références

# Renommer les variables et fonctions pour améliorer la lisibilité
# Suivre les références croisées (Xrefs) pour comprendre les flux

# Astuce : chercher les fonctions qui lisent les configurations
# → Souvent contiennent des noms de clés de configuration ou des valeurs par défaut
```

### Radare2 / rizin

```bash
# r2 — analyse en ligne de commande
r2 -A suspicious_binary      # Analyser automatiquement
r2 firmware_extracted_binary

# Commandes utiles
[0x00000000]> afl             # Lister toutes les fonctions
[0x00000000]> pdf @ main      # Désassembler la fonction main
[0x00000000]> iz              # Lister les strings dans .data
[0x00000000]> iz~password     # Filtrer les strings contenant "password"
[0x00000000]> axt @ 0x1234    # Cross-références vers une adresse
```

## Vulnérabilités courantes en firmware

```
1. Credentials hardcodés
   → Compte admin avec mot de passe fixe "admin"/"1234"
   → Clé privée SSH identique dans tous les appareils du même modèle

2. Buffer overflow dans les handlers HTTP
   → L'interface web du routeur analyse les requêtes avec strcpy() sans vérifier la taille
   → Overflow → RCE sans authentification

3. Command injection dans les paramètres de configuration
   → Paramètre "ping_host" passé directement à system("ping " + host)
   → Payload : "8.8.8.8; /bin/ash -i > /dev/ttyS0"

4. Backdoors délibérées
   → Compte "tech-support" avec mot de passe caché dans le binaire
   → Port UDP en écoute répondant à un magic packet

5. Mise à jour non signée
   → Firmware sans vérification de signature → flash d'un firmware malveillant

6. Interfaces non documentées
   → /cgi-bin/debug_tool → RCE direct
   → Port TCP/UDP caché en écoute
```

## Outils de l'écosystème

| Outil | Rôle |
|---|---|
| binwalk | Extraction et analyse de firmware |
| firmwalker | Audit automatique du filesystem extrait |
| Ghidra | Reverse engineering / décompilation |
| Radare2 / rizin | Analyse binaire CLI |
| QEMU | Émulation d'architectures |
| Firmadyne | Émulation automatique de firmware Linux |
| flashrom | Lecture/écriture de puces flash |
| OpenOCD | Interface JTAG |
| checksec | Protections d'un binaire ELF |
| pwntools | Exploitation (si vuln identifiée) |
