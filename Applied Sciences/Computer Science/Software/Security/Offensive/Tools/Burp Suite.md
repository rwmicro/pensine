---
title: Burp Suite
domain: sciences-appliquées
subdomain: informatique / sécurité / offensive / outils
tags: [burp-suite, proxy, web, pentest, sécurité, outils]
date: 2026-03-22
---

# Burp Suite

Burp Suite est la référence pour le test de sécurité des applications web. Il intercepte le trafic HTTP/S entre le navigateur et le serveur pour analyser et modifier les requêtes.

## Architecture et composants

```
Navigateur → Proxy Burp (127.0.0.1:8080) → Serveur web

Burp intercepte, analyse et peut modifier chaque requête et réponse.
```

### Modules principaux

| Module | Fonction |
|---|---|
| Proxy | Intercepte et modifie le trafic HTTP/S |
| Repeater | Rejoue et modifie des requêtes manuellement |
| Intruder | Attaques automatisées (brute-force, fuzzing) |
| Scanner | Scan automatique de vulnérabilités (Pro) |
| Decoder | Encode/décode (base64, URL, HTML, hex...) |
| Comparer | Compare deux requêtes ou réponses |
| Sequencer | Analyse l'entropie des tokens de session |
| Collaborator | Serveur OOB (out-of-band) pour SSRF, XXE, blind SQLi |
| Logger | Historique de tout le trafic |
| Extensions | Plugins via l'API Burp (BApp Store) |

## Configuration

### Proxy et certificat

```
1. Proxy → Options → Proxy Listeners
   Interface : 127.0.0.1, Port : 8080

2. Configurer le navigateur
   Firefox : Préférences → Réseau → Paramètres → Proxy manuel
   HTTP Proxy : 127.0.0.1, Port : 8080
   Utiliser pour tous les protocoles

3. Installer le certificat CA Burp
   Naviguer vers http://burpsuite (dans le navigateur proxifié)
   Télécharger le certificat → Importer dans le navigateur comme CA de confiance
   Firefox : Préférences → Vie privée → Certificats → Autorités → Importer

4. FoxyProxy (extension Firefox) — switch rapide de proxy
   Créer un profil "Burp" pointant vers 127.0.0.1:8080
```

### Scope

```
Target → Scope → Add (définir les cibles)
   Include : https://target.com
   Exclude : https://target.com/logout (éviter de se déconnecter)

Proxy → Options → "Intercept only in-scope items" ← Pour ne pas intercepter tout le trafic
```

## Proxy — Interception

```
Proxy → Intercept → ON
→ Chaque requête est mise en pause pour inspection/modification

Actions :
  Forward  : envoyer la requête telle quelle
  Drop     : abandonner la requête
  Action   : envoyer vers Repeater, Intruder, Scanner...

Raccourcis clavier :
  Ctrl+F    : Forward
  Ctrl+A    : Action menu
  Ctrl+R    : Envoyer vers Repeater
  Ctrl+I    : Envoyer vers Intruder
```

## Repeater

Le module central pour le test manuel.

```
Clic droit sur une requête → Send to Repeater

Onglet Repeater :
  - Modifier la requête à gauche
  - Cliquer "Send"
  - Voir la réponse à droite
  - Historique des requêtes (flèches ← →)

Utilisation :
  - Tester des payloads SQL, XSS, SSTI manuellement
  - Modifier des paramètres (prix, ID, rôle)
  - Changer des en-têtes (Host, Origin, Cookie)
  - Tester les WebSockets (onglet WebSockets dans Repeater)
```

## Intruder — Attaques automatisées

```
Clic droit → Send to Intruder

1. Positions — marquage des emplacements d'injection
   §payload§  → l'Intruder remplace chaque §...§ par les payloads

2. Types d'attaques
   Sniper      : un seul payload position, itère sur la liste
   Battering ram : même payload sur toutes les positions simultanément
   Pitchfork   : listes différentes sur des positions différentes (colonne par colonne)
   Cluster bomb : produit cartésien de toutes les listes (le plus exhaustif)

3. Payloads — liste des valeurs à tester
   Simple list : liste de mots importée ou saisie
   Runtime file : fichier chargé à l'exécution
   Brute forcer : génère toutes les combinaisons
   Dates       : génère des dates
   Numbers     : séquences numériques

Exemple — brute-force de formulaire de connexion :
  POST /login
  username=admin&password=§mot_de_passe§

  Payload : liste de mots de passe courants
  Grep Match : "Invalid password" → identifier la réponse différente (succès)
```

### Comparaison des résultats Intruder

```
Colonnes utiles à analyser :
  Status     → code HTTP différent = candidat
  Length     → taille de réponse différente = candidat
  Time       → délai anormal = SQLi time-based ou logique différente
  Grep Match → présence d'un pattern dans la réponse

Filtrer sur Length ≠ longueur habituelle → identifier les requêtes qui se comportent différemment
```

## Scanner (Burp Pro)

```
Clic droit → Scan (sur une requête ou un site entier)

Types de scan :
  Passive : analyse le trafic existant sans envoyer de nouvelles requêtes
  Active  : envoie des payloads de test (XSS, SQLi, SSRF...)

Configuration :
  Scanner → Scan configuration → Audit checks to include
  → Sélectionner les types de vulnérabilités à tester

Issues panel :
  Target → Site map → Issues (vulnérabilités trouvées avec sévérité)
```

## Collaborator (OOB — Out-Of-Band)

```
Burp Collaborator = serveur externe contrôlé par Burp pour détecter les interactions réseau.
Utile pour : SSRF, XXE, Blind SQLi, Blind XSS, Log4Shell, SSTI sans output.

Burp → Collaborator → Copy to clipboard
→ Utiliser l'URL/domaine Collaborator dans les payloads

Exemple SSRF :
  {"url": "https://xyz.oastify.com/test"}
  → Si le serveur fait une requête → interaction visible dans Collaborator

Exemple XXE :
  <!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://xyz.oastify.com/xxe">]>
  <root>&xxe;</root>
```

## Extensions utiles (BApp Store)

```
Autorize       → Tester l'autorisation (rejouer les requêtes avec un token moins privilégié)
Param Miner    → Découvrir des paramètres cachés (cache poisoning, host header)
Logger++       → Logging avancé avec filtres et expressions régulières
J2EEScan       → Vulnérabilités Java EE spécifiques
Active Scan++  → Améliore le scanner avec des checks supplémentaires
Turbo Intruder → Intruder haute performance pour race conditions
SQLMap        → Intégration SQLmap dans Burp
JWT Editor    → Analyse et modification de JWT
Retire.js     → Détection de bibliothèques JS vulnérables
```

## Raccourcis et astuces

```
Ctrl+Shift+B    → Basculer l'interception ON/OFF
Ctrl+R          → Envoyer vers Repeater (dans Proxy, Logger)
Ctrl+I          → Envoyer vers Intruder
Ctrl+S          → Envoyer vers Scanner (Pro)
Ctrl+G          → Go (Forward dans Repeater)

Clic droit sur une requête dans n'importe quel module :
  → "Copy as curl command" → reproduire la requête en ligne de commande
  → "Save item" → exporter la requête/réponse

Dashboard :
  Tâches actives, événements, vulnérabilités récentes

Scope → "Use advanced scope control"
  → Regex pour inclure/exclure avec précision
```

## Workflow typique de pentest web

```
1. Configurer le proxy, installer le certificat, définir le scope

2. Proxy ON → Parcourir l'application manuellement (spider passif)
   → L'arbre des URLs se construit dans Target → Site Map

3. Scanner passif → Vulnérabilités évidentes sans action offensive

4. Tests manuels dans Repeater :
   → Modifier des paramètres (IDOR, SQLi, XSS)
   → Tester les en-têtes (Host, Origin, X-Forwarded-For)
   → Tester les WebSockets si présents

5. Intruder → Tests semi-automatisés (fuzzing de paramètres, brute-force)

6. Scanner actif (Pro) → Couverture automatique

7. Collaborator → Tester les interactions OOB (SSRF, XXE, blind injections)

8. Extensions → Autorize (test d'autorisation), Param Miner (découverte de paramètres)
```
