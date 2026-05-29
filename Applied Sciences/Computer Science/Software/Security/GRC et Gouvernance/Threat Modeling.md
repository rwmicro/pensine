---
title: Threat Modeling
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [threat-modeling, stride, dread, attack-trees, secure-design, sécurité, architecture]
date: 2026-03-23
---

# Threat Modeling

Le threat modeling est un processus structuré d'identification des menaces pesant sur un système, de leur évaluation, et de définition des contre-mesures appropriées. Il intervient idéalement en phase de conception (shift left) mais peut aussi s'appliquer à des systèmes existants.

## Processus général

```
4 questions fondamentales (Adam Shostack) :

  1. Sur quoi travaille-t-on ?
     → Définir le périmètre : application, infrastructure, processus métier
     → Produire un diagramme de flux de données (DFD)

  2. Qu'est-ce qui peut mal se passer ?
     → Identifier les menaces (STRIDE, PASTA, arbres d'attaque...)

  3. Que fait-on à ce sujet ?
     → Définir les contre-mesures, les risques acceptés, les transferts

  4. Avons-nous bien travaillé ?
     → Revue, validation, intégration dans le cycle de développement
```

## DFD — Diagramme de Flux de Données

```
Éléments d'un DFD :

  Processus (cercle/rond)
    → Entité qui traite ou transforme des données
    → Exemples : application web, API, service backend

  Entité externe (rectangle)
    → Source ou destination de données hors du périmètre
    → Exemples : utilisateur, système tiers, partenaire

  Flux de données (flèche)
    → Communication entre éléments
    → Annoter avec : protocole, authentification, chiffrement

  Datastore (double trait horizontal)
    → Stockage de données
    → Exemples : base de données, fichiers, cache Redis

  Limite de confiance (pointillés)
    → Frontière entre zones de confiance différentes
    → Chaque traversée = vecteur d'attaque potentiel
```

```
Exemple — Application web de e-commerce :

  [Navigateur] ──HTTPS──> [Load Balancer] ──HTTP──> [App Server]
                                                           |
                                              ┌────────────┼────────────┐
                                           [Cache]    [DB MySQL]   [API Paiement]
                                          (Redis)   [Datastore]   [Entité externe]

  Limites de confiance :
    Internet / DMZ : entre navigateur et load balancer
    DMZ / Backend   : entre load balancer et app server
    Backend / DB    : entre app server et base de données
```

## STRIDE

STRIDE est le framework de threat modeling développé par Microsoft. Chaque lettre correspond à une catégorie de menaces.

| Menace | Description | Propriété violée | Contre-mesures |
|---|---|---|---|
| **S**poofing | Usurpation d'identité | Authentification | MFA, certificats, OAuth |
| **T**ampering | Modification de données | Intégrité | Signatures, HMAC, checksums |
| **R**epudiation | Nier avoir effectué une action | Non-répudiation | Logs, audit trails, signatures |
| **I**nformation Disclosure | Fuite de données | Confidentialité | Chiffrement, ACLs, masquage |
| **D**enial of Service | Rendre le service indisponible | Disponibilité | Rate limiting, WAF, redondance |
| **E**levation of Privilege | Obtenir plus de droits | Autorisation | Moindre privilège, sandboxing |

```
Application de STRIDE — pour chaque élément du DFD :

Flux de données [Navigateur → App Server] :
  S → Spoofing : le serveur peut-il vérifier l'identité du client ? (→ TLS, JWT)
  T → Tampering : le flux peut-il être modifié en transit ? (→ TLS, HSTS)
  R → Repudiation : les actions sont-elles loggées avec l'identité ? (→ audit log)
  I → Information Disclosure : les données sont-elles chiffrées ? (→ HTTPS)
  D → DoS : le serveur peut-il être saturé ? (→ rate limiting, CDN)
  E → EoP : le client peut-il accéder à des ressources d'autres users ? (→ IDOR checks)

Datastore [DB MySQL] :
  S → Spoofing : qui peut se connecter ? (→ auth MySQL, SSL)
  T → Tampering : qui peut modifier ? (→ permissions, transactions)
  I → Information Disclosure : chiffrement au repos ? (→ TDE, chiffrement colonnes)
  D → DoS : protection contre les requêtes lourdes ? (→ quotas, query timeout)
  E → EoP : un utilisateur peut-il accéder aux données d'un autre ? (→ Row-level security)
```

## MITRE ATT&CK

ATT&CK ne remplace pas STRIDE mais le complète : là où STRIDE catégorise les menaces de façon abstraite, ATT&CK fournit un catalogue de **TTP réellement observés** chez les attaquants. Trois matrices selon l'environnement :

- **Enterprise** — réseaux d'entreprise (Windows, Linux, macOS, cloud, conteneurs)
- **Mobile** — iOS, Android
- **ICS** — systèmes industriels (SCADA, automates)

Chaque technique documente : description, exemples de procédures (quels groupes APT l'ont utilisée), mitigations et indicateurs de détection. L'**ATT&CK Navigator** (`mitre-attack.github.io/attack-navigator/`) visualise les techniques en heatmap — utile pour cartographier la couverture de détection d'un SOC ou le profil d'un acteur de menace. Voir `[[Threat Modeling pour la détection (SOC)]]` pour cet usage défensif.

## DREAD — Scoring des menaces

DREAD permet de prioriser les menaces identifiées avec STRIDE.

| Critère | Description | Score 1-3 |
|---|---|---|
| **D**amage | Ampleur des dégâts si exploité | 1=faible, 3=critique |
| **R**eproducibility | Facilité à reproduire | 1=difficile, 3=toujours reproductible |
| **E**xploitability | Niveau de compétence requis | 1=expert, 3=script kiddie |
| **A**ffected users | Nombre d'utilisateurs impactés | 1=quelques-uns, 3=tous |
| **D**iscoverability | Facilité à découvrir la vulnérabilité | 1=très difficile, 3=évident |

```
Score DREAD = (D + R + E + A + D) / 5

Exemple — Injection SQL dans le formulaire de login :
  Damage        : 3 (accès à toute la base de données)
  Reproducibility : 3 (toujours reproductible)
  Exploitability  : 2 (sqlmap accessible à tous)
  Affected users  : 3 (tous les utilisateurs)
  Discoverability : 2 (tests automatisés le trouvent)
  Score : (3+3+2+3+2)/5 = 2.6 — CRITIQUE

Seuils :
  2.5 - 3.0 : Critique → corriger immédiatement
  2.0 - 2.4 : Élevé → corriger dans le sprint en cours
  1.5 - 1.9 : Moyen → backlog prioritaire
  < 1.5     : Faible → backlog standard
```

### CVSS et matrice de risque

DREAD est subjectif (et Microsoft l'a abandonné en interne au profit de CVSS et de la SDL). En pratique on s'appuie aussi sur :

- **CVSS** (FIRST.org) — standard industriel de notation des vulnérabilités de 0 à 10, en trois métriques : **Base** (caractéristiques intrinsèques : vecteur, complexité, impact CIA), **Temporal** (maturité de l'exploit, disponibilité du patch), **Environmental** (criticité pour l'organisation).
- **Matrice probabilité × impact** — la plus simple et la plus utilisée par les équipes :

|  | Impact faible | Impact moyen | Impact critique |
|---|---|---|---|
| **Probabilité haute** | Moyen | Haut | Critique |
| **Probabilité moyenne** | Faible | Moyen | Haut |
| **Probabilité basse** | Accepté | Faible | Moyen |

## Arbres d'attaque

Les arbres d'attaque modélisent les chemins qu'un attaquant peut emprunter pour atteindre un objectif.

```
Structure :
  Racine = objectif de l'attaquant
  Nœuds = sous-objectifs ou conditions
  Feuilles = actions atomiques

Opérateurs logiques :
  AND : toutes les conditions doivent être vraies
  OR  : au moins une condition suffit

Exemple — Objectif : Exfiltrer les données clients

Exfiltrer données clients
├── OR
│   ├── [AND] Compromis du compte admin
│   │         ├── Obtenir credentials admin
│   │         │   ├── OR
│   │         │   │   ├── Phishing ciblé (CEO)
│   │         │   │   ├── Brute force sur VPN
│   │         │   │   └── Acheter sur le dark web
│   │         └── Bypasser le MFA
│   │               ├── OR
│   │               │   ├── SIM swapping
│   │               │   └── MFA fatigue attack
│   ├── SQL Injection dans l'application
│   │   ├── Identifier les endpoints vulnérables
│   │   └── Extraire les données via UNION SELECT
│   └── [AND] Accès physique au serveur
│             ├── Tailgating dans les bureaux
│             └── Accès à la salle serveur
```

```python
# Quantification des arbres d'attaque
# Annoter chaque feuille avec : probabilité, coût, impact

threats = {
    "phishing": {"prob": 0.3, "cost_attacker": 100, "impact": 9},
    "brute_force_vpn": {"prob": 0.1, "cost_attacker": 500, "impact": 9},
    "sql_injection": {"prob": 0.2, "cost_attacker": 50, "impact": 8},
}

# Calculer le risque par chemin
for threat, params in threats.items():
    risk = params["prob"] * params["impact"]
    print(f"{threat}: risque = {risk:.1f}, coût attaquant = ${params['cost_attacker']}")
```

## PASTA — Process for Attack Simulation and Threat Analysis

PASTA est un framework orienté risque métier, en 7 étapes.

```
Étape 1 : Définir les objectifs métier
  → Quelles données, quels processus, quels actifs sont critiques ?
  → Impacts métier : financier, réputationnel, légal, opérationnel

Étape 2 : Définir la portée technique
  → Architecture, composants, technologies, dépendances

Étape 3 : Décomposition de l'application
  → DFD, flux de données, limites de confiance

Étape 4 : Analyse des menaces
  → Identifier les acteurs (script kiddies, APT, insiders...)
  → Identifier les TTP (MITRE ATT&CK)

Étape 5 : Analyse des vulnérabilités
  → Scan de vulnérabilités, revue de code, SAST/DAST
  → Mapper les vulnérabilités aux menaces

Étape 6 : Modélisation des attaques
  → Arbres d'attaque, scénarios d'attaque réalistes
  → Simulation (purple team)

Étape 7 : Analyse du risque et contre-mesures
  → Scoring des risques, priorisation
  → Plan de remédiation avec ROI (coût de la contre-mesure vs coût de l'incident)
```

## Stratégies de traitement du risque

Pour chaque menace priorisée, quatre réponses possibles — chaque contre-mesure doit être tracée jusqu'à la menace qu'elle adresse, afin de vérifier qu'aucune menace critique ne reste sans réponse :

1. **Mitigate** — réduire le risque (chiffrement, input validation, WAF)
2. **Transfer** — transférer le risque (assurance cyber, externalisation)
3. **Accept** — accepter le risque (documenté, validé par le management)
4. **Avoid** — supprimer la fonctionnalité qui crée le risque

## Quand faire du threat modeling

- **À la conception** d'un nouveau système ou d'une fonctionnalité (shift left)
- **Lors d'un changement d'architecture** significatif (migration cloud, ajout d'un partenaire externe)
- **Régulièrement** sur les systèmes critiques (annuellement au minimum)
- **Après un incident**, pour vérifier si le modèle de menace était incomplet

## Intégration dans le SDLC

```
Threat modeling dans le cycle de développement :

Phase de conception :
  → Créer le DFD initial, appliquer STRIDE, prioriser avec DREAD
  → Définir les exigences de sécurité (security requirements)
  → Livrable : rapport de threat modeling

Phase de développement :
  → Code review orienté menaces identifiées
  → SAST (Static Application Security Testing) : Semgrep, SonarQube, Checkmarx
  → Tests unitaires de sécurité

Phase de test :
  → DAST (Dynamic Application Security Testing) : OWASP ZAP, Burp Suite
  → Pentest ciblé sur les menaces identifiées
  → Vérification que les contre-mesures sont en place

Phase de déploiement :
  → Infrastructure as Code security scan (Checkov, tfsec)
  → Container security scan (Trivy, Grype)

Phase de maintenance :
  → Mettre à jour le threat model à chaque changement majeur
  → Bug bounty, divulgation responsable
  → Veille CVE sur les composants utilisés

Outils de threat modeling :
  → Microsoft Threat Modeling Tool (TMT) — basé sur STRIDE, gratuit
  → OWASP Threat Dragon — open-source, web-based
  → IriusRisk — commercial, intégration CI/CD
  → draw.io — DFD manuels avec templates
```
