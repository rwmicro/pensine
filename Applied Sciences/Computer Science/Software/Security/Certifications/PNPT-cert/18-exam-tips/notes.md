---
title: "PNPT Exam Tips & Stratégie (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, certification, pnpt]
date: "2026-05-18"
---

# PNPT — Exam Tips & Stratégie

La PNPT (Practical Network Penetration Tester, TCM Security) se distingue des autres certifications par son format : 5 jours de pentest réel, pas de QCM, pas de flags artificiels, et un débrief oral comme dans la vie professionnelle. La technique seule ne suffit pas — c'est aussi un test de gestion du temps, de rigueur de documentation, et de communication.

## Format en bref

| Élément              | Détail                                             |
|----------------------|----------------------------------------------------|
| Durée pentest        | **5 jours** (120 heures), non supervisé           |
| Durée rapport        | **2 jours** supplémentaires                       |
| Débrief              | **15 minutes** en visio                            |
| Outils               | **Tous autorisés** (Metasploit inclus, scripts...) |
| Flags / QCM          | **Aucun** — c'est un vrai pentest                  |
| Retake               | **1 gratuit** inclus avec le voucher               |
| Expiration           | La certification **n'expire jamais**               |

## L'objectif

Compromettre le **Domain Controller** en partant d'un accès externe limité.

```
   Internet                                  Active Directory cible
   (toi)                                         (DC à compromettre)
     │                                                  ▲
     │                                                  │
     ▼                                                  │
   OSINT ──► Premier accès ──► Énum interne ──► Privesc ──► Domain Admin
                              (BloodHound)    (Kerberos,
                                               relay, etc.)
```

Ce n'est pas un CTF — c'est une simulation réaliste d'environnement d'entreprise.

## Gestion du temps (7 jours)

### Jour 1 — Recon & OSINT

- Lire **attentivement la lettre d'engagement** (scope, règles)
- OSINT complet (employés, emails, breaches, infrastructure)
- Scan externe du périmètre
- Identifier les premiers points d'entrée potentiels

### Jours 2–3 — Exploitation & AD

- Obtenir un accès initial
- Énumération AD complète (BloodHound)
- Attaques AD (Responder, Kerberoasting, AS-REP)
- Mouvement latéral

### Jour 4 — Compromission & vérification

- Compromettre le Domain Controller
- **Documenter et vérifier toute la chaîne d'attaque**
- Tenter des chemins alternatifs (utile pour le rapport)
- Prendre les derniers screenshots manquants

### Jour 5 — Début du rapport

- Commencer la rédaction du rapport
- Organiser les preuves, classer les screenshots

### Jours 6–7 — Rapport & débrief

- Finaliser le rapport, relire pour fautes
- Préparer les slides du débrief
- S'entraîner à l'oral (timing)

## Stratégie pendant le pentest

```
   Règle 1 : DOCUMENTER en temps réel
              (commandes, outputs, screenshots — à chaque étape)
                                │
                                ▼
   Règle 2 : Lire le scope AVANT de scanner
              (sortir du périmètre = échec)
                                │
                                ▼
   Règle 3 : Ne pas s'acharner > 2-3h sur une piste
              (si c'est bloqué, explorer ailleurs et revenir)
                                │
                                ▼
   Règle 4 : Énumérer, énumérer, énumérer
              (80% du résultat vient d'une recon profonde)
                                │
                                ▼
   Règle 5 : Tester les payloads AVANT l'envoi
              (AV evasion validée en local d'abord)
```

## Conseils critiques

### Pendant le pentest

- **Lecture du scope** : ne pas attaquer ce qui n'est pas dans le périmètre — risque d'échec immédiat.
- **Documentation continue** : utiliser Obsidian/CherryTree/Markdown avec une note par cible. La mémoire ne suffira pas.
- **Ne pas s'enliser** : si une vuln semble trop tordue à exploiter, vérifier qu'il n'y a pas un chemin plus simple.
- **Tester les payloads localement** : avoir une VM Windows avec Defender à jour pour valider l'évasion AV avant d'envoyer.
- **JAMAIS uploader sur VirusTotal** : VT partage les samples avec les éditeurs AV, ton payload est grillé en quelques heures.

### Pour le rapport

- Screenshots **avant ET après** chaque exploitation (état initial vs résultat)
- Montrer le **chemin d'attaque complet** sous forme de diagramme
- **Executive summary non technique** — relire en pensant à un DG
- **Remédiations actionnables** : étapes concrètes, pas "appliquer les bonnes pratiques"
- Faire une **relecture à froid** (24h après si possible)

### Pour le débrief

- **15 minutes max** — chronométrer en s'entraînant
- Présenter comme à un **client non technique**, mais avec assez de profondeur pour les pentesters assesseurs
- Connaître son rapport **par cœur**
- Avoir des **remédiations solides** pour chaque finding majeur
- Voir `16-client-debrief` pour la structure détaillée

## Erreurs classiques qui font échouer

- Mauvaise lecture du scope (attaquer hors périmètre)
- Trop de temps sur une seule piste, abandonner les autres
- Screenshots manquants à des étapes critiques
- Rapport trop technique sans executive summary
- Oubli des remédiations ou remédiations vagues
- Dépasser le temps du débrief
- Payloads non évadés détectés par Defender → blocage de l'attaque

## Préparation : labs recommandés

### TryHackMe

- Parcours **Attacking Active Directory**
- **Wreath** (pivoting, excellent pour préparer l'examen)
- **Blue / Ice / Alfred / Steel Mountain** (rooms Windows)

### HackTheBox

- Machines AD débutantes : **Forest, Sauna, Cascade, Resolute**
- Machines AD intermédiaires : **Monteverde, Blackfield, Search**
- **Active, Mantis** (Kerberos)
- **Pro Labs : Offshore, RastaLabs** (si budget — environnement quasi identique à l'examen)

### TCM Security Labs

- Les labs du cours **Practical Ethical Hacking (PEH)** sont **directement alignés** avec l'examen
- **Refaire les labs AD** plusieurs fois — c'est la base la plus proche

### Web (utile mais pas central)

- **PortSwigger Web Security Academy** — gratuit, complet
- **DVWA, bWAPP** pour la pratique basique

## Checklist avant l'examen

```
   [ ] Cours PEH terminé, tous les labs faits
   [ ] À l'aise avec Responder, ntlmrelayx, mitm6
   [ ] Maîtrise Kerberoasting, AS-REP, DCSync
   [ ] BloodHound : analyse de chemins d'attaque
   [ ] Pivoting fonctionnel (Chisel OU Ligolo testé)
   [ ] AV evasion : un loader custom testé qui marche
   [ ] Template de rapport prêt, screenshots organisés
   [ ] Présentation orale entraînée chronométrée
   [ ] Cheatsheets PNPT consultables rapidement
   [ ] VM Kali à jour, snapshot pris avant l'examen
   [ ] Setup visio testé (micro, caméra, partage d'écran)
```

## Pièges courants à l'examen

- **Mauvaise gestion du jour 1** : passer toute la journée sur OSINT sans scanner → on rate des fenêtres pour énumérer.
- **Croire que le DC est facile** : il faut passer par plusieurs machines intermédiaires. Pas de raccourci magique.
- **Trop compter sur Metasploit** : utile, mais beaucoup d'attaques AD se font avec impacket, mimikatz, BloodHound. MSF ne couvre pas tout.
- **AV evasion bâclée** : un payload msfvenom brut + encoder ne passe plus Defender. Préparer un loader custom **avant** l'examen.
- **Documentation tardive** : "je documenterai à la fin" → screenshots oubliés, étapes floues. La rédaction est infernale si la doc n'est pas faite en temps réel.
- **Sous-estimer le débrief** : la technique passe, mais l'oral plante. Préparer ses slides au plus tard le matin du débrief.
