---
title: "Bug Bounty — Méthodologie"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité, bug-bounty, pentest, web-security, recon]
date: "2026-04-16"
---

# Bug Bounty — Méthodologie

Le bug bounty est un programme par lequel une organisation invite des chercheurs en sécurité externes à trouver et signaler des vulnérabilités dans ses systèmes, en échange d'une récompense financière. Cette note couvre la méthodologie de chasse, de la reconnaissance au rapport.

## Plateformes

| Plateforme | Modèle | Particularité |
|---|---|---|
| **HackerOne** | Public + privé | La plus grande, programmes majeurs (US DoD, GitHub, Shopify) |
| **Bugcrowd** | Public + privé | Forte présence enterprise, programmes VDP |
| **Intigriti** | Public + privé | Basée en Europe, conforme GDPR |
| **YesWeHack** | Public + privé | Française, programmes gouvernementaux FR |
| **Synack** | Privé (Red Team) | Sélection stricte des chercheurs, accès contrôlé |

### Programmes publics vs privés

- **Public** : tout le monde peut participer. Plus de concurrence, vulnérabilités faciles déjà trouvées.
- **Privé** : sur invitation. Moins de concurrence, surface d'attaque souvent plus large, meilleurs payouts.
- **VDP** (Vulnerability Disclosure Program) : pas de récompense financière, mais cadre légal pour signaler.

## Comprendre le scope

Avant toute chose, lire intégralement le **programme policy** :

| Element | Pourquoi |
|---|---|
| **Scope** (in-scope / out-of-scope) | Quels domaines, apps, APIs sont autorisés |
| **Vulnérabilités exclues** | Self-XSS, rate limiting, SPF/DKIM manquant sont souvent exclus |
| **Règles d'engagement** | Pas de DoS, pas de données utilisateur réelles, pas d'ingénierie sociale |
| **Safe harbor** | Protection légale pour les chercheurs qui respectent les règles |
| **Récompenses** | Grille par sévérité (Critical, High, Medium, Low) |

Tester hors scope ou ignorer les règles = ban de la plateforme et potentiellement des poursuites légales.

## Phase 1 — Reconnaissance

La recon est la phase la plus importante. Plus la surface d'attaque est cartographiée, plus les chances de trouver une vulnérabilité sur un asset oublié sont élevées.

### Enumération de sous-domaines

```bash
# Sources passives (DNS historique, Certificate Transparency)
subfinder -d target.com -o subs.txt
amass enum -passive -d target.com -o amass.txt
assetfinder --subs-only target.com >> subs.txt

# Brute-force DNS
puredns bruteforce wordlist.txt target.com -r resolvers.txt -w brute.txt

# Fusionner et dédupliquer
cat subs.txt amass.txt brute.txt | sort -u > all_subs.txt

# Vérifier lesquels sont vivants
httpx -l all_subs.txt -o alive.txt -status-code -title -tech-detect
```

### Sources de reconnaissance passive

| Source | Outil / Méthode |
|---|---|
| **Certificate Transparency** | crt.sh (`%.target.com`), certspotter |
| **DNS historique** | SecurityTrails, DNSDumpster, VirusTotal |
| **Wayback Machine** | `waybackurls target.com` — URLs historiques |
| **Google Dorking** | `site:target.com filetype:pdf`, `inurl:admin`, `intitle:login` |
| **GitHub** | Recherche de secrets, configs, endpoints dans les repos publics |
| **Shodan / Censys** | Services exposés, ports ouverts, technologies |
| **ASN lookup** | Identifier toutes les plages IP de l'organisation |

### Enumération technologique

```bash
# Identifier les technologies (CMS, framework, serveur)
whatweb https://target.com
wappalyzer # (extension navigateur)

# Scanner les ports des IP en scope
nmap -sV -sC -p- target.com -oA nmap_results

# Découvrir les endpoints et fichiers
ffuf -u https://target.com/FUZZ -w /path/to/wordlist.txt -mc 200,301,302,403
feroxbuster -u https://target.com -w wordlist.txt

# Fichiers intéressants à chercher
/.env, /.git/config, /robots.txt, /sitemap.xml
/.well-known/, /swagger.json, /api/docs
/backup.zip, /debug, /phpinfo.php, /server-status
```

### Cartographie de l'application

- **Spider** l'application (Burp Suite, ZAP) — parcourir tous les liens
- **Identifier les fonctionnalités** : login, inscription, upload, recherche, export, API, websocket
- **Identifier les rôles** : utilisateur, admin, API key — tester les transitions de privilèges
- **Lire le JavaScript** : endpoints API, tokens, logique métier côté client

## Phase 2 — Vulnérabilités à chercher

### Par fonctionnalité

| Fonctionnalité | Vulnérabilités à tester |
|---|---|
| **Login** | Brute-force, credential stuffing, bypass MFA, enumération d'utilisateurs |
| **Inscription** | Account takeover via email manipulation, injection dans les champs |
| **Reset mot de passe** | Token prédictible, host header injection, race condition |
| **Upload de fichier** | RCE via webshell, bypass d'extension, SSRF via SVG/PDF |
| **Recherche** | XSS réfléchi, injection SQL, LDAP injection |
| **Export / PDF** | SSRF (HTML to PDF), injection de formules (CSV injection) |
| **API** | IDOR, mass assignment, broken authentication, rate limiting absent |
| **Paramètres de profil** | Stored XSS, CSRF, IDOR sur l'ID utilisateur |
| **Paiement** | Manipulation de prix, race condition, bypass de validation |

### OWASP Top 10 comme checklist

| # | Catégorie | Exemple de test |
|---|---|---|
| A01 | **Broken Access Control** | IDOR : changer l'ID dans `/api/users/123` pour accéder au profil d'un autre |
| A02 | **Cryptographic Failures** | Données sensibles en clair, tokens JWT avec `alg: none` |
| A03 | **Injection** | SQLi, XSS, command injection, template injection (SSTI) |
| A04 | **Insecure Design** | Logique métier contournable, absence de rate limiting |
| A05 | **Security Misconfiguration** | Headers manquants, debug mode en production, CORS `*` |
| A06 | **Vulnerable Components** | CVE connues dans les dépendances (retire.js, Snyk) |
| A07 | **Auth Failures** | Session fixation, tokens faibles, MFA contournable |
| A08 | **Data Integrity Failures** | Désérialisation non sécurisée, CI/CD compromise |
| A09 | **Logging Failures** | Pas directement exploitable mais aggrave l'impact |
| A10 | **SSRF** | Requête côté serveur vers des services internes (metadata cloud, Redis) |

### Vulnérabilités à fort impact

Les vulnérabilités les mieux payées sont celles qui donnent un accès critique :

| Classe | Impact | Payout typique |
|---|---|---|
| **RCE** (Remote Code Execution) | Contrôle total du serveur | 5 000 - 100 000+ USD |
| **SQLi avec exfiltration** | Accès à la base de données | 3 000 - 50 000 USD |
| **SSRF vers cloud metadata** | Accès aux credentials AWS/GCP | 3 000 - 30 000 USD |
| **Account takeover** | Prise de contrôle de n'importe quel compte | 2 000 - 20 000 USD |
| **IDOR sur données sensibles** | Accès aux données d'autres utilisateurs | 1 000 - 10 000 USD |
| **Stored XSS** | Exécution de JS dans le navigateur d'autres utilisateurs | 500 - 5 000 USD |

## Phase 3 — Exploitation et validation

### Principes

- **Prouver l'impact** sans causer de dommage. Ne jamais exfiltrer de vraies données utilisateur.
- Utiliser ses propres comptes de test.
- Documenter chaque étape avec des screenshots ou des enregistrements.
- S'arrêter dès que l'impact est démontré (pas besoin de pivoter ou d'escalader dans un bug bounty).

### Outils principaux

| Outil | Usage |
|---|---|
| **Burp Suite** (Pro) | Proxy HTTP, scanner, repeater, intruder — outil central |
| **ffuf** / **feroxbuster** | Fuzzing de répertoires et paramètres |
| **sqlmap** | Exploitation automatique d'injections SQL |
| **nuclei** | Scanner de vulnérabilités basé sur des templates |
| **XSS Hunter** | Détecter les blind XSS (callback quand le payload s'exécute) |
| **Collaborator** (Burp) | Détecter les SSRF et injections out-of-band |
| **jwt_tool** | Tester les faiblesses JWT (none algorithm, key confusion) |
| **Postman** / **curl** | Tester les API manuellement |

### Exemple : tester un IDOR

```
1. Créer deux comptes : attacker@test.com et victim@test.com
2. Se connecter en tant que victim, naviguer vers /api/profile/456
3. Se connecter en tant que attacker, changer la requête vers /api/profile/456
4. Si les données de victim sont retournées → IDOR confirmé
5. Tester aussi avec les méthodes PUT/DELETE pour mesurer l'impact
```

## Phase 4 — Rédiger le rapport

Un bon rapport est aussi important que la vulnérabilité elle-même. Un rapport mal rédigé sera sous-évalué, renvoyé pour clarification, ou fermé comme "informative".

### Structure d'un rapport

```
Titre : [Type] Description concise avec localisation
  Ex: "IDOR on /api/v2/orders/{id} allows reading any user's order history"

Sévérité : Critical / High / Medium / Low (justifier avec CVSS si possible)

Description : 
  - Ce que fait la vulnérabilité
  - Pourquoi c'est un problème (impact concret)

Etapes de reproduction :
  1. Aller sur https://target.com/endpoint
  2. Intercepter la requête avec Burp
  3. Modifier le paramètre X en Y
  4. Observer que...
  (Chaque étape doit être reproductible par un triager qui ne connaît pas l'application)

Preuve :
  - Screenshots annotés
  - Requêtes/réponses HTTP (depuis Burp)
  - Vidéo si le flux est complexe

Impact :
  - Quelles données sont exposées
  - Combien d'utilisateurs sont affectés
  - Quel est le pire scénario réaliste

Recommandation de correction :
  - Vérification d'autorisation côté serveur
  - Utiliser des identifiants non prédictibles (UUID)
```

### Erreurs courantes

- Titre vague ("XSS found") au lieu de spécifique ("Stored XSS in comment field via `<img onerror>` on /blog/post/{id}")
- Pas d'étapes de reproduction claires
- Surestimer la sévérité (Self-XSS n'est pas un Critical)
- Envoyer un scan automatique brut (nuclei output) sans validation manuelle
- Soumettre un duplicata sans vérifier les rapports existants (disclosed)

## Workflow quotidien

```
Choisir un programme
       |
       v
Recon (sous-domaines, endpoints, technologies)
       |
       v
Sélectionner une surface d'attaque
(fonctionnalité précise, API endpoint, asset oublié)
       |
       v
Tester manuellement (Burp Suite)
       |
       v
Vulnérabilité trouvée ?
  /          \
 NON         OUI
  |            |
  v            v
Changer      Valider l'impact
de cible     Rédiger le rapport
             Soumettre
```

## Conseils stratégiques

- **Eviter les programmes saturés** : les programmes avec 1000+ hackers et des récompenses faibles sont très compétitifs. Préférer les programmes récents ou de niche.
- **Spécialisation** : devenir expert d'une classe de vulnérabilités (SSRF, IDOR, race conditions) plutôt que de tout tester superficiellement.
- **Automatiser la recon, pas l'exploitation** : les scanners trouvent les fruits bas, les findings manuels sont mieux payés et moins dupliqués.
- **Lire les rapports disclosed** : HackerOne et Bugcrowd publient des rapports résolus (Hacktivity). Etudier ce qui a été accepté et bien payé.
- **Tester la logique métier** : les scanners ne trouvent pas les failles de logique. Comprendre comment l'application fonctionne et chercher les cas limites.
- **Etre patient** : le triage peut prendre des semaines. Ne pas harceler l'équipe de sécurité.

## Légalité

Le bug bounty est légal **uniquement dans le cadre du programme** :

- Tester seulement les assets in-scope
- Respecter les règles d'engagement
- Ne pas accéder aux données d'utilisateurs réels
- Ne pas faire de déni de service
- Ne pas divulguer publiquement avant la correction (responsible disclosure)
- Le safe harbor du programme protège le chercheur **s'il respecte les règles**

En France, l'article 323-1 du Code pénal punit l'accès frauduleux à un système informatique. Le cadre du bug bounty avec safe harbor constitue une autorisation explicite.

## Références

- **HackerOne Hacktivity** (`hackerone.com/hacktivity`) — rapports disclosed publiquement
- **PortSwigger Web Security Academy** (`portswigger.net/web-security`) — labs gratuits par catégorie
- **OWASP Testing Guide** (`owasp.org/www-project-web-security-testing-guide`) — méthodologie de test complète
- **Nahamsec** — ressources et streams sur le bug bounty
- **Bug Bounty Bootcamp** (Vickie Li) — livre de référence pour débuter
