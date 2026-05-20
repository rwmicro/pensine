---
title: "Threat Modeling"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc, threat-modeling]
date: "2025-03-14"
---

# Threat Modeling

Le threat modeling est un processus structuré pour identifier **quelles menaces** pèsent sur un système, **quels actifs** sont en jeu, et **quelles mesures** sont prioritaires. L'objectif est de réfléchir aux attaques *avant* qu'elles ne se produisent, au moment de la conception ou de l'évolution d'une architecture.

## Quatre questions fondamentales

Tout exercice de threat modeling revient à répondre à ces quatre questions (Adam Shostack, *Threat Modeling: Designing for Security*) :

1. **Qu'est-ce qu'on construit ?** → diagramme de l'architecture, flux de données, limites de confiance
2. **Qu'est-ce qui peut mal tourner ?** → identification des menaces (STRIDE, kill chain, brainstorm)
3. **Qu'est-ce qu'on fait à ce sujet ?** → priorisation et contre-mesures
4. **Est-ce qu'on a bien fait le travail ?** → validation, revue, itération

## Étape 1 — Modéliser le système

### Data Flow Diagram (DFD)

Le DFD est le support visuel standard du threat modeling :

| Élément | Symbole | Exemples |
|---|---|---|
| **Processus** | Cercle | Serveur web, API, microservice |
| **Data store** | Lignes parallèles | Base de données, fichier, cache |
| **External entity** | Rectangle | Utilisateur, API tierce, partenaire |
| **Data flow** | Flèche | Requête HTTP, appel gRPC, lecture SQL |
| **Trust boundary** | Ligne pointillée | Frontière réseau, frontière cloud, frontière d'authentification |

Les **trust boundaries** sont les zones les plus intéressantes pour un attaquant : c'est là que les données changent de niveau de confiance (entrée utilisateur → backend, internet → DMZ, client → serveur).

## Étape 2 — Identifier les menaces

### STRIDE (Microsoft, 1999)

Le modèle STRIDE catégorise les menaces en six types, chacun violant une propriété de sécurité :

| Catégorie | Menace | Propriété violée | Exemple |
|---|---|---|---|
| **S**poofing | Usurpation d'identité | Authentification | Session hijacking, IP spoofing |
| **T**ampering | Modification non autorisée | Intégrité | Injection SQL, modification de fichier |
| **R**epudiation | Nier une action | Non-répudiation | Supprimer les logs, transaction sans trace |
| **I**nformation Disclosure | Fuite d'information | Confidentialité | Exfiltration, erreurs verbose, IDOR |
| **D**enial of Service | Déni de service | Disponibilité | DDoS, resource exhaustion |
| **E**levation of Privilege | Élévation de privilèges | Autorisation | Exploitation kernel, IDOR vers admin |

**Comment l'utiliser** : pour chaque élément du DFD traversé par un trust boundary, passer en revue les 6 catégories STRIDE et se demander si la menace s'applique.

### MITRE ATT&CK

Le framework MITRE ATT&CK ne remplace pas STRIDE mais le complète en fournissant un catalogue de **TTPs réels observés** chez des attaquants.

Trois matrices selon l'environnement :
- **Enterprise** — réseaux d'entreprise (Windows, Linux, macOS, cloud, conteneurs)
- **Mobile** — iOS, Android
- **ICS** — systèmes industriels (SCADA, automates)

Chaque technique a :
- **Description** : ce que fait la technique
- **Procedure examples** : quels groupes APT l'ont utilisée et comment
- **Mitigations** : mesures défensives recommandées
- **Detection** : indicateurs à surveiller dans les logs

**ATT&CK Navigator** (`mitre-attack.github.io/attack-navigator/`) permet de visualiser les techniques sous forme de heatmap — utile pour cartographier la couverture de détection du SOC ou le profil d'un acteur de menace.

### Arbres d'attaque (Attack Trees)

Méthode formelle (Bruce Schneier, 1999) : on place l'objectif de l'attaquant à la racine, puis on décompose en sous-objectifs (ET/OU) jusqu'aux actions concrètes. Permet de raisonner sur les chemins d'attaque et de comparer leur coût/difficulté.

## Étape 3 — Évaluer et prioriser les risques

### DREAD (Microsoft)

Score de 1 à 10 sur cinq critères, le total permet de classer les risques :

| Critère | Question |
|---|---|
| **D**amage | Quel est l'impact si l'attaque réussit ? |
| **R**eproducibility | L'attaque est-elle facile à reproduire ? |
| **E**xploitability | Quel niveau de compétence faut-il ? |
| **A**ffected users | Combien d'utilisateurs sont impactés ? |
| **D**iscoverability | La vulnérabilité est-elle facile à trouver ? |

Limites : la subjectivité des scores et le fait que Discoverability encourage le *security through obscurity*. Microsoft a d'ailleurs abandonné DREAD en interne au profit de CVSS et de la SDL.

### CVSS (Common Vulnerability Scoring System)

Standard industriel (FIRST.org) pour noter la sévérité des vulnérabilités de 0 à 10. Trois métriques :
- **Base** : caractéristiques intrinsèques (vecteur d'attaque, complexité, impact CIA)
- **Temporal** : maturité de l'exploit, disponibilité du patch
- **Environmental** : criticité pour l'organisation spécifique

### Matrice risque = probabilité x impact

En pratique, les équipes utilisent souvent une matrice simple :

|  | Impact faible | Impact moyen | Impact critique |
|---|---|---|---|
| **Probabilité haute** | Moyen | Haut | Critique |
| **Probabilité moyenne** | Faible | Moyen | Haut |
| **Probabilité basse** | Accepté | Faible | Moyen |

## Étape 4 — Définir les contre-mesures

Pour chaque menace identifiée et priorisée, quatre stratégies possibles :

1. **Mitigate** — réduire le risque (chiffrement, input validation, WAF)
2. **Transfer** — transférer le risque (assurance cyber, externalisation)
3. **Accept** — accepter le risque (documenté, validé par le management)
4. **Avoid** — supprimer la fonctionnalité qui crée le risque

Les contre-mesures doivent être tracées jusqu'aux menaces qu'elles adressent — c'est ce qui permet de vérifier qu'aucune menace critique n'est laissée sans réponse.

## Quand faire du threat modeling

- **Lors de la conception** d'un nouveau système ou d'une nouvelle fonctionnalité (shift left)
- **Lors d'un changement d'architecture** significatif (migration cloud, ajout d'un partenaire externe)
- **Régulièrement** sur les systèmes critiques (annuellement minimum)
- **Après un incident** pour comprendre si le modèle de menace était incomplet

## Outils

| Outil | Usage |
|---|---|
| **Microsoft Threat Modeling Tool** | Génère automatiquement des menaces STRIDE à partir d'un DFD |
| **OWASP Threat Dragon** | Open source, éditeur de DFD avec identification de menaces |
| **IriusRisk** | Plateforme commerciale, intégration CI/CD |
| **draw.io / Excalidraw** | Pour dessiner les DFD manuellement |
| **ATT&CK Navigator** | Visualisation des couvertures de techniques |
