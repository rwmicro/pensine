---
title: Hash Cracking
domain: sciences-appliquées
subdomain: informatique / sécurité / cryptographie
tags: [hashcat, john, hash, cracking, ntlm, bcrypt, sécurité]
date: 2026-03-22
---

# Hash Cracking

Le cassage de hash consiste à retrouver une valeur en clair à partir d'un hash, en testant des candidats jusqu'à trouver celui qui produit le même hash. C'est une étape centrale en pentest (mots de passe, hashes NTLM, tickets Kerberos).

## Identifier un hash

```bash
# Reconnaître un type de hash par sa forme
# MD5         → 32 hex    : 5f4dcc3b5aa765d61d8327deb882cf99
# SHA-1       → 40 hex    : 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8
# SHA-256     → 64 hex    : 8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
# SHA-512     → 128 hex   : b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86
# NTLM        → 32 hex    : 8846f7eaee8fb117ad06bdd830b7586c
# bcrypt      → 60 chars  : $2a$12$R9h/cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jWMUW
# MD5crypt    →            : $1$salt$hash
# SHA-512crypt→            : $6$salt$hash (Linux /etc/shadow)
# WPA         →            : hashcat -m 22000
# Kerberos TGS→            : $krb5tgs$23$...
# Kerberos TGT→            : $krb5asrep$23$...
# DPAPI       →            : $DPAPImk$...

# Outils d'identification
hashid hash.txt          # Python : pip install hashid
hash-identifier          # Outil interactif
name-that-hash -t "hash" # pip install name-that-hash

# Hashcat — identifier avec le mode auto
hashcat hash.txt --identify
```

## Hashcat

Hashcat est le craqueur de hashes GPU le plus performant.

### Modes d'attaque (-a)

```
0 → Dictionary    : tester chaque ligne d'une wordlist
1 → Combination   : concaténer deux wordlists
3 → Brute-Force   : toutes les combinaisons d'un charset
6 → Hybrid Wordlist + Mask : mot + suffixe (password2024)
7 → Hybrid Mask + Wordlist : préfixe + mot (2024password)
```

### Modes de hash (-m) courants

| Mode | Type | Usage |
|---|---|---|
| 0 | MD5 | |
| 100 | SHA-1 | |
| 1000 | NTLM | Active Directory |
| 1800 | sha512crypt ($6$) | Linux /etc/shadow |
| 3200 | bcrypt ($2*$) | Applications web |
| 5500 | NTLMv1 | Captures réseau |
| 5600 | NTLMv2 | Captures réseau |
| 13100 | Kerberos TGS-REP | Kerberoasting |
| 18200 | Kerberos AS-REP | AS-REP Roasting |
| 22000 | WPA-PBKDF2-PMKID | WiFi |
| 7300 | IPMI2 RAKP HMAC-SHA1 | IPMI |
| 11300 | Bitcoin/Litecoin wallet | Crypto |

### Attaque dictionnaire (mode 0)

```bash
# Basique — wordlist contre des hashes NTLM
hashcat -m 1000 -a 0 ntlm_hashes.txt /usr/share/wordlists/rockyou.txt

# Avec output des trouvés
hashcat -m 1000 -a 0 ntlm_hashes.txt rockyou.txt -o cracked.txt

# Reprendre une session interrompue
hashcat -m 1000 -a 0 ntlm_hashes.txt rockyou.txt --session mysession
hashcat --session mysession --restore

# Afficher les résultats déjà trouvés
hashcat -m 1000 ntlm_hashes.txt --show
```

### Règles — transformer les mots de la wordlist

Les règles appliquent des transformations (capitalisation, ajout de chiffres, substitution) à chaque mot de la wordlist.

```bash
# Appliquer des règles
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -r rules/dive.rule  # Plus exhaustif

# Règles courantes :
# /usr/share/hashcat/rules/best64.rule    → 64 règles efficaces
# /usr/share/hashcat/rules/rockyou-30000.rule → très exhaustif
# /usr/share/hashcat/rules/OneRuleToRuleThemAll.rule → règle unique très puissante

# Plusieurs règles simultanément
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -r rules/best64.rule -r rules/toggles1.rule
```

### Attaque brute-force avec masque (mode 3)

```bash
# Charset prédéfinis
# ?l = abcdefghijklmnopqrstuvwxyz
# ?u = ABCDEFGHIJKLMNOPQRSTUVWXYZ
# ?d = 0123456789
# ?s = !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
# ?a = ?l?u?d?s (tout)
# ?b = 0x00 - 0xff (tous les octets)

# 8 chiffres (PIN numérique)
hashcat -m 1000 -a 3 hashes.txt ?d?d?d?d?d?d?d?d

# 8 caractères alphanumériques (estimation : quelques heures avec GPU)
hashcat -m 1000 -a 3 hashes.txt ?a?a?a?a?a?a?a?a

# Mot de passe typique : Majuscule + minuscules + chiffres + 1 symbole, 8-12 chars
hashcat -m 1000 -a 3 hashes.txt -i --increment-min=8 --increment-max=12 ?a?a?a?a?a?a?a?a

# Patterns courants de mots de passe d'entreprise :
# Mot + année : ?u?l?l?l?l?l?d?d?d?d
hashcat -m 1000 -a 6 hashes.txt rockyou.txt ?d?d?d?d  # Mot + 4 chiffres (hybrid)
hashcat -m 1000 -a 7 hashes.txt ?u rockyou.txt         # Majuscule + mot (hybrid)
```

### Kerberoasting

```bash
# Hashes obtenus via impacket-GetUserSPNs ou Rubeus
hashcat -m 13100 -a 0 kerberoast_hashes.txt rockyou.txt
hashcat -m 13100 -a 0 kerberoast_hashes.txt rockyou.txt -r rules/best64.rule

# AS-REP Roasting
hashcat -m 18200 -a 0 asrep_hashes.txt rockyou.txt
```

### Performances et optimisation GPU

```bash
# Utiliser tous les GPU disponibles
hashcat -m 1000 hashes.txt rockyou.txt -d 1,2  # GPU 0 et 1

# Mode optimisé (plus rapide mais limite la longueur max)
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -O

# Workload (W1=faible, W2=défaut, W3=élevé, W4=max)
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -w 3

# Benchmark — connaître les performances
hashcat -b -m 1000  # NTLM
hashcat -b -m 3200  # bcrypt (beaucoup plus lent)

# Performances typiques (RTX 4090) :
# MD5       → 164 GH/s
# SHA-1     → 50 GH/s
# NTLM      → 200 GH/s
# bcrypt    → 184 kH/s  (intentionnellement lent)
# SHA-512   → 8 GH/s
```

## John the Ripper

Alternative à Hashcat, avec détection automatique du type de hash.

```bash
# Détection automatique et cassage
john hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt

# Format explicite
john hashes.txt --format=NT --wordlist=rockyou.txt        # NTLM
john hashes.txt --format=sha512crypt --wordlist=rockyou.txt  # Linux shadow

# Règles
john hashes.txt --wordlist=rockyou.txt --rules=All

# Afficher les trouvés
john --show hashes.txt

# Formats de fichiers courants (extraction auto)
# /etc/shadow
john /etc/shadow --wordlist=rockyou.txt

# Hashes ZIP
zip2john archive.zip > zip_hash.txt
john zip_hash.txt --wordlist=rockyou.txt

# PDF
pdf2john document.pdf > pdf_hash.txt
john pdf_hash.txt --wordlist=rockyou.txt

# KeePass
keepass2john database.kdbx > kp_hash.txt
john kp_hash.txt --wordlist=rockyou.txt

# SSH key avec passphrase
ssh2john id_rsa > ssh_hash.txt
john ssh_hash.txt --wordlist=rockyou.txt
```

## Wordlists

```bash
# Emplacement des wordlists
/usr/share/wordlists/rockyou.txt           # 14 millions de mots — incontournable
/usr/share/seclists/Passwords/             # Collection SecLists

# Télécharger rockyou (si pas disponible)
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

# Wordlists spécialisées
/usr/share/seclists/Passwords/Leaked-Databases/rockyou-75.txt  # Top 75k
/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt

# Générer une wordlist ciblée avec CeWL (mots du site web de la cible)
cewl https://target.com -d 3 -m 5 -w target_wordlist.txt

# Générer avec mentalist (wordlist basée sur des informations personnelles)
# Nom, prénom, date de naissance, ville → permutations
```

## Rainbow Tables

```
Précalcul de couples (texte clair → hash) stockés dans une table
→ Recherche très rapide (trade-off espace/temps vs brute-force)

Limites :
- Ne fonctionnent pas contre les hashes salés (bcrypt, sha512crypt)
- Le salt rend chaque hash unique même pour des mots de passe identiques
- Très peu utile en pratique contre les systèmes modernes

Cas d'usage résiduel :
- NTLM sans salt → les rainbow tables NTLM fonctionnent encore
- MD5 non salé (applications anciennes)

RainbowCrack (si disponible) :
rcrack . -h NTLM_HASH        # Chercher dans les tables
```

## Bonnes pratiques défensives

```
Pour résister au cassage :
✓ bcrypt (coût 12+), Argon2id, ou scrypt — fonctions de hachage à coût paramétrable
✓ JAMAIS MD5, SHA-1, SHA-256 seuls pour les mots de passe (trop rapides)
✓ Salt unique par utilisateur (généré aléatoirement, min 16 octets)
✓ Politique de mots de passe forts (min 12 chars, complexité)
✓ Vérifier les mots de passe contre des listes de compromis (HaveIBeenPwned API)
✓ MFA pour limiter l'impact d'un mot de passe compromis
```
