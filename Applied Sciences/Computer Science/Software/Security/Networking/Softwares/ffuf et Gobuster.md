---
title: ffuf et Gobuster
domain: sciences-appliquées
subdomain: informatique / sécurité / outils
tags: [ffuf, gobuster, fuzzing, directory-bruteforce, sécurité, outils, pentest]
date: 2026-03-22
---
# ffuf et Gobuster

Outils de découverte de ressources web par force brute : répertoires, fichiers, sous-domaines, paramètres.

## ffuf (Fuzz Faster U Fool)

ffuf est plus flexible et performant que Gobuster. Le mot-clé `FUZZ` marque l'emplacement d'injection.

### Découverte de répertoires et fichiers

```bash
# Répertoires
ffuf -u https://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt

# Fichiers avec extensions
ffuf -u https://target.com/FUZZ -w wordlist.txt -e .php,.html,.txt,.bak,.zip

# Ignorer les codes HTTP non pertinents
ffuf -u https://target.com/FUZZ -w wordlist.txt -fc 404,403

# Filtrer par taille de réponse
ffuf -u https://target.com/FUZZ -w wordlist.txt -fs 1234  # Ignorer les réponses de 1234 octets

# Filtrer par nombre de mots ou de lignes
ffuf -u https://target.com/FUZZ -w wordlist.txt -fw 12    # Ignorer les 12 mots
ffuf -u https://target.com/FUZZ -w wordlist.txt -fl 5     # Ignorer les 5 lignes

# Afficher uniquement les codes spécifiques
ffuf -u https://target.com/FUZZ -w wordlist.txt -mc 200,301,302,403
```

### Sous-domaines (vhost fuzzing)

```bash
# Fuzzing de sous-domaines via l'en-tête Host
ffuf -u https://target.com/ -H "Host: FUZZ.target.com" \
    -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
    -fs 1234  # Filtrer la réponse par défaut (taille de la page principale)

# DNS bruteforce (nécessite la résolution DNS)
ffuf -u https://FUZZ.target.com/ \
    -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
    -mc 200,301
```

### Fuzzing de paramètres et valeurs

```bash
# Découverte de paramètres GET
ffuf -u "https://target.com/page?FUZZ=value" \
    -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
    -fs <taille_réponse_normale>

# Fuzzing de valeurs d'un paramètre connu
ffuf -u "https://target.com/api/user?id=FUZZ" \
    -w /usr/share/seclists/Fuzzing/Integers/Integers.txt \
    -mc 200

# Fuzzing POST (formulaire de connexion)
ffuf -u https://target.com/login \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=FUZZ" \
    -w /usr/share/seclists/Passwords/Leaked-Databases/rockyou-50.txt \
    -fc 200  # Le succès répond peut-être différemment

# Fuzzing JSON
ffuf -u https://target.com/api/login \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"FUZZ"}' \
    -w passwords.txt \
    -fs <taille_échec>
```

### Fuzzing multi-positions

```bash
# Deux positions simultanées (FUZZ et W2) — Pitchfork
ffuf -u "https://target.com/FUZZ/W2" \
    -w wordlist1.txt:FUZZ \
    -w wordlist2.txt:W2 \
    -mode pitchfork

# Cluster bomb (produit cartésien)
ffuf -u "https://target.com/api?user=FUZZ&role=W2" \
    -w users.txt:FUZZ \
    -w roles.txt:W2 \
    -mode clusterbomb
```

### Options avancées

```bash
# Authentification HTTP
ffuf -u https://target.com/FUZZ -w wordlist.txt \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..."

# Cookie de session
ffuf -u https://target.com/FUZZ -w wordlist.txt \
    -H "Cookie: session=abc123"

# Avec un proxy (Burp Suite)
ffuf -u https://target.com/FUZZ -w wordlist.txt \
    -x http://127.0.0.1:8080

# Délai entre requêtes (eviter le rate limiting)
ffuf -u https://target.com/FUZZ -w wordlist.txt \
    -p 0.1  # 100ms entre chaque requête

# Threads (concurrence)
ffuf -u https://target.com/FUZZ -w wordlist.txt \
    -t 50   # 50 threads (défaut : 40)

# Sortie
ffuf -u https://target.com/FUZZ -w wordlist.txt \
    -o results.json -of json  # JSON, CSV, HTML, MD

# Recursif — descendre dans les sous-répertoires trouvés
ffuf -u https://target.com/FUZZ -w wordlist.txt \
    -recursion -recursion-depth 2
```

## Gobuster

Outil plus simple, spécialisé dans trois modes : dir, dns, vhost.

### Mode dir — répertoires et fichiers

```bash
# Basique
gobuster dir -u https://target.com -w /usr/share/seclists/Discovery/Web-Content/common.txt

# Avec extensions
gobuster dir -u https://target.com \
    -w /usr/share/seclists/Discovery/Web-Content/common.txt \
    -x php,html,txt,bak,zip

# Ignorer les codes de statut
gobuster dir -u https://target.com -w wordlist.txt \
    -b 404,403,500  # Blacklist

# Avec authentification
gobuster dir -u https://target.com -w wordlist.txt \
    -U admin -P password  # Basic auth
gobuster dir -u https://target.com -w wordlist.txt \
    -H "Authorization: Bearer TOKEN"
gobuster dir -u https://target.com -w wordlist.txt \
    -c "session=abc123"   # Cookie

# Via proxy Burp
gobuster dir -u https://target.com -w wordlist.txt \
    --proxy http://127.0.0.1:8080

# Afficher la longueur des réponses
gobuster dir -u https://target.com -w wordlist.txt -l

# Threads
gobuster dir -u https://target.com -w wordlist.txt -t 50
```

### Mode dns — sous-domaines

```bash
# Enumération de sous-domaines
gobuster dns -d target.com \
    -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# Résoudre les IPs
gobuster dns -d target.com -w wordlist.txt -i

# Résolveur DNS spécifique
gobuster dns -d target.com -w wordlist.txt -r 8.8.8.8
```

### Mode vhost — virtual hosts

```bash
gobuster vhost -u https://target.com \
    -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
    --append-domain  # Ajoute .target.com automatiquement
```

## Wordlists recommandées

```bash
# SecLists — la référence (apt install seclists)
/usr/share/seclists/Discovery/Web-Content/

  common.txt                        # 4 800 entrées — rapide
  directory-list-2.3-medium.txt     # 220 000 entrées — équilibré
  directory-list-2.3-big.txt        # 1 270 000 entrées — exhaustif
  raft-large-directories.txt        # Répertoires courants
  raft-large-files.txt              # Fichiers courants
  burp-parameter-names.txt          # Noms de paramètres
  api/api-endpoints.txt             # Endpoints API REST

/usr/share/seclists/Discovery/DNS/
  subdomains-top1million-5000.txt   # Top sous-domaines (rapide)
  subdomains-top1million-20000.txt  # Plus exhaustif

/usr/share/seclists/Passwords/
  Leaked-Databases/rockyou-50.txt   # Top 50 000 mots de passe
  Common-Credentials/top-passwords-shortlist.txt

# Générer des wordlists personnalisées
cewl https://target.com -d 3 -m 5 -w wordlist.txt  # À partir du site lui-même
```

## Comparaison

| Critère | ffuf | Gobuster |
|---|---|---|
| Vitesse | Très rapide | Rapide |
| Flexibilité | Élevée (FUZZ partout) | Modérée (modes dédiés) |
| Multi-positions | Oui (FUZZ, W2, W3...) | Non |
| Filtres | Nombreux (code, taille, mots, lignes, temps) | Basiques |
| Syntaxe | Légèrement plus complexe | Plus simple |
| Récursion | Oui | Non (dir uniquement) |
| Formats de sortie | JSON, CSV, HTML, MD | Stdout, JSON |

ffuf est généralement préféré pour sa flexibilité. Gobuster reste utile pour des cas simples grâce à sa syntaxe claire.
