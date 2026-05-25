---
title: "Client Debrief / Presentation (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, debrief, communication, pnpt]
date: "2026-05-18"
---

# Client Debrief / Presentation

Le débrief client est la partie la plus négligée à la préparation, et la plus discriminante à l'examen PNPT. Tu as fait 5 jours d'exploitation et 2 jours de rapport, et c'est 15 minutes d'oral qui déterminent ton image professionnelle. Beaucoup de candidats techniques compétents échouent au débrief parce qu'ils ne savent pas vulgariser.

## Le piège : parler à deux audiences à la fois

Un débrief réussi navigue entre deux registres sans choisir un seul.

```
   Audience du débrief
            │
   ┌────────┴────────┐
   ▼                 ▼
   Direction         Équipe technique
   (DSI, RSSI,       (sysadmin, dev,
   parfois DG)       sécu)
   │                 │
   ▼                 ▼
   "Quel risque ?"   "Comment c'est arrivé ?"
   "Coûts ?"         "Comment corriger ?"
   "Priorités ?"     "Reproductibilité ?"
   │                 │
   └─── doivent tous deux comprendre ───┘
```

**Règle d'or** : commencer business, descendre dans la technique progressivement, remonter en business pour les remédiations.

## Format de l'examen PNPT

Après les 5 jours de pentest + 2 jours de rédaction :

- **Débrief de 15 minutes** en visio avec les assesseurs de TCM Security
- Les assesseurs sont des **pentesters seniors** qui ont déjà lu ton rapport
- Ils peuvent poser des **questions techniques et stratégiques**

## Structure type (15 min)

### 1. Introduction (1–2 min)

- Se présenter brièvement (qui tu es)
- Rappeler le scope de l'engagement (ce qu'on t'a demandé)
- Annoncer ton plan de présentation

### 2. Résumé exécutif (2–3 min)

- Posture globale du client (en une phrase verdict)
- 3 risques principaux, en **impact métier** (pas en CVE)
- Niveau de sévérité global

**Exemple de phrasing** : "L'environnement présente une vulnérabilité critique : un attaquant interne, même sans privilège initial, peut prendre le contrôle complet du domaine Windows en moins de deux heures."

### 3. Chemin d'attaque (5–7 min)

C'est le cœur de la présentation. Montrer l'enchaînement complet en 5–6 étapes clés.

```
   Recon (OSINT)
        │
        ▼
   Premier accès (vuln web ou phishing)
        │
        ▼
   Énumération interne (BloodHound)
        │
        ▼
   Élévation latérale (Kerberoasting)
        │
        ▼
   Domain Admin (DCSync)
```

Pour chaque étape : une slide, un screenshot clé, et l'impact ("à ce stade, l'attaquant pourrait déjà...").

**Langage** : vulgariser sans simplifier à l'excès. Pas "j'ai DCSync le hash du krbtgt", mais "j'ai extrait l'équivalent du trousseau maître du domaine, ce qui permet de générer des identifiants pour n'importe quel utilisateur".

### 4. Remédiations (3–4 min)

Présenter par priorité, avec distinction quick win vs effort long terme.

| Priorité | Délai indicatif | Exemple                                          |
|----------|----------------|--------------------------------------------------|
| Immédiat | Jour 1         | Désactiver LLMNR, durcir mots de passe service   |
| Court terme | Semaine    | Activer SMB Signing, MFA sur OWA                 |
| Moyen terme | Mois       | Tiering AD, séparation des admin/users          |
| Long terme | Trimestre   | Adoption d'un PAM, refonte des comptes de service|

Montrer que tu comprends les **contraintes business** : on ne demande pas à une banque d'arrêter les services SMB.

### 5. Questions (2–3 min)

Être prêt à justifier des choix techniques, des sévérités, et des alternatives de remédiation.

## Préparer ses slides

- **PowerPoint, Slides, ou même PDF de ton rapport** — peu importe l'outil
- **Slides épurées** : peu de texte, beaucoup de visuel
- **Screenshots des moments-clés** uniquement (pas tous les `nmap`)
- **Schéma du chemin d'attaque** : c'est ce qui marque le plus
- **Une slide = une idée**

## Ce qui est évalué

- Capacité à communiquer clairement à deux audiences
- Compréhension réelle des trouvailles (pas du copier-coller)
- Qualité et réalisme des remédiations
- Professionnalisme (langage, ton, gestion du temps)

## Questions classiques à anticiper

```
   "Quelle est la vulnérabilité la plus critique ?"
   → Avoir une réponse claire + justification métier

   "Par où commenceriez-vous la remédiation ?"
   → Hiérarchiser, expliquer pourquoi

   "Combien de temps un vrai attaquant mettrait-il ?"
   → Donner une fourchette + facteurs (compétence, OSINT préalable, etc.)

   "Comment avez-vous contourné l'antivirus ?"
   → Expliquer la technique sans rentrer dans le détail du shellcode

   "Si on n'avait qu'un budget limité, on fait quoi ?"
   → Identifier les 1-2 actions à impact maximum
```

## Entraînement

- **Mini exec summary après chaque lab** — habituer à formaliser
- **S'enregistrer** en présentant : timing, tics de langage, hésitations
- **Présenter à un proche non technique** — s'il comprend, c'est gagné
- **Préparer des cartes mentales** pour le chemin d'attaque (pas du texte écrit à lire)

## Pièges courants

- **Dépasser les 15 minutes** : élimination quasi assurée. Pratiquer avec un chrono.
- **Lire ses slides** : décrédibilise immédiatement. Connaître son rapport.
- **Trop technique trop vite** : si tu lances "Kerberoasting" à la slide 2, tu as perdu la moitié de la salle.
- **Trop business sans démonstration** : à l'inverse, si tu ne montres jamais une preuve technique, les pentesters assesseurs doutent que tu aies vraiment compris.
- **Ne pas avoir de remédiations** : un débrief sans recommandations = livrable incomplet.
- **Mauvaise gestion des questions** : si tu ne sais pas, dis-le. "Je n'ai pas testé ce vecteur faute de temps" est mieux que de bluffer.
- **Setup technique défaillant** : tester son micro, sa webcam, sa connexion AVANT le débrief. Avoir une slide PDF en backup au cas où.
