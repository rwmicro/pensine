---
title: "Purple Teaming"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Methodology"
tags: [sciences-appliquées, informatique, sécurité, purple-team, red-team, blue-team, detection-engineering]
date: "2026-04-16"
---

# Purple Teaming

Le Purple Teaming est une approche collaborative de la sécurité offensive et défensive. Contrairement au modèle classique où la Red Team attaque en secret et la Blue Team défend sans savoir, le Purple Teaming fait travailler les deux équipes **ensemble** pour maximiser l'amélioration des défenses.

## Red, Blue, Purple

| Equipe | Role | Objectif |
|---|---|---|
| **Red Team** | Simuler un adversaire réaliste | Trouver des chemins d'attaque exploitables |
| **Blue Team** | Détecter, contenir, répondre | Protéger l'organisation contre les menaces |
| **Purple Team** | Coordination Red + Blue | Maximiser la couverture de détection |

Le Purple Team n'est pas une troisième équipe permanente : c'est un **mode de fonctionnement** où Red et Blue collaborent en temps réel. La Red Team exécute une technique, la Blue Team vérifie si elle la détecte, et les deux ajustent ensemble.

## Pourquoi le Purple Teaming existe

Le modèle traditionnel Red vs Blue souffre de plusieurs problèmes :

- La Red Team trouve des vulnérabilités, rédige un rapport, puis passe à autre chose. La Blue Team reçoit le rapport des semaines plus tard et doit deviner comment reproduire les attaques.
- Les résultats du pentest ne se traduisent pas toujours en **améliorations de détection concrètes**.
- La Red Team optimise pour "réussir l'attaque", pas pour "améliorer la défense". Elle évite les techniques bruyantes, alors que la Blue Team a justement besoin de les voir pour calibrer ses alertes.
- Sans feedback loop, les mêmes failles réapparaissent d'un exercice à l'autre.

Le Purple Teaming résout ces problèmes en créant une **boucle de feedback immédiate** : attaque, observation, correction, re-test.

## Déroulement d'un exercice Purple Team

### 1. Planification

Choisir les techniques à tester, typiquement à partir de :

- **MITRE ATT&CK** : sélectionner des techniques par tactique (Initial Access, Execution, Persistence, etc.)
- **Threat intelligence** : quelles techniques utilisent les groupes qui ciblent notre secteur ?
- **Résultats du dernier pentest** : les techniques qui ont fonctionné sans être détectées
- **Nouveaux outils déployés** : valider qu'un nouvel EDR détecte bien ce qu'il promet

### 2. Exécution (cycle par technique)

Pour chaque technique MITRE ATT&CK sélectionnée :

```
Red Team exécute la technique
        |
        v
Blue Team observe en temps réel (SIEM, EDR, logs)
        |
        v
   Détecté ?
   /        \
  OUI        NON
  |           |
  v           v
Valider    Analyser pourquoi :
la règle   - Logs absents ?
           - Règle manquante ?
           - Seuil trop haut ?
           |
           v
        Créer ou corriger
        la détection
           |
           v
        Red Team re-exécute
        pour valider
```

### 3. Documentation

Chaque technique testée produit une fiche :

| Champ | Contenu |
|---|---|
| Technique MITRE | ID + nom (ex: T1059.001 — PowerShell) |
| Outil utilisé | Atomic Red Team, Cobalt Strike, manuel |
| Commande exécutée | Commande exacte ou procédure |
| Résultat initial | Détecté / Partiellement / Non détecté |
| Source de logs | Sysmon Event ID, EDR, etc. |
| Règle créée/modifiée | Sigma rule, requête SIEM |
| Résultat après correction | Détecté avec la nouvelle règle |

## Frameworks et outils

### MITRE ATT&CK comme base

ATT&CK est le langage commun du Purple Teaming. La matrice permet de :

- **Cartographier la couverture** : pour chaque technique, est-ce qu'on a une détection ?
- **Prioriser** : couvrir d'abord les techniques les plus utilisées par les adversaires de notre secteur
- **Mesurer la progression** : comparer la couverture avant/après l'exercice

L'outil **ATT&CK Navigator** permet de visualiser la couverture sous forme de heatmap colorée.

### Atomic Red Team

Framework open-source de Red Canary. Fournit des **tests unitaires d'attaque** pour chaque technique MITRE ATT&CK :

```bash
# Installer
git clone https://github.com/redcanaryco/atomic-red-team.git

# Avec le module PowerShell Invoke-AtomicRedTeam
Install-Module -Name invoke-atomicredteam

# Lister les tests pour une technique
Invoke-AtomicTest T1059.001 -ShowDetailsBrief

# Exécuter un test spécifique
Invoke-AtomicTest T1059.001 -TestNumbers 1

# Nettoyer après le test
Invoke-AtomicTest T1059.001 -TestNumbers 1 -Cleanup
```

Chaque test atomique contient : la commande d'attaque, les prérequis, la procédure de nettoyage, et les IOCs attendus.

### Autres outils de simulation

| Outil | Type | Usage |
|---|---|---|
| **Atomic Red Team** | Open-source | Tests unitaires par technique ATT&CK |
| **Caldera** (MITRE) | Open-source | Plateforme d'émulation d'adversaire automatisée |
| **Infection Monkey** (Akamai) | Open-source | Simulation de mouvement latéral automatique |
| **Cobalt Strike** | Commercial | C2 framework complet (utilisé aussi par les vrais attaquants) |
| **Sliver** | Open-source | C2 framework alternatif à Cobalt Strike |
| **SafeBreach** | Commercial (BAS) | Breach and Attack Simulation continue |
| **AttackIQ** | Commercial (BAS) | Validation de sécurité automatisée |

### Du côté défensif

| Outil | Role |
|---|---|
| **Sigma** | Règles de détection portables (SIEM-agnostic) |
| **Elastic Detection Rules** | Règles prêtes à l'emploi pour Elastic SIEM |
| **Splunk Security Content** | Détections pour Splunk |
| **ATT&CK Navigator** | Visualisation de la couverture |
| **DeTT&CT** | Framework pour mapper données + détections sur ATT&CK |

## Detection Engineering dans le Purple Team

Le résultat principal d'un exercice Purple Team est la **création ou amélioration de règles de détection**. C'est le pont entre l'attaque observée et la défense opérationnelle.

### Processus par technique

1. **Identifier les artefacts** : quels logs, événements, ou traces l'attaque produit-elle ?
2. **Vérifier la collecte** : ces logs sont-ils collectés dans le SIEM ? Avec le bon niveau de détail ?
3. **Ecrire la règle** : en Sigma (portable) ou directement dans le SIEM
4. **Tester** : la Red Team re-exécute, la règle se déclenche-t-elle ?
5. **Réduire les faux positifs** : ajuster les seuils et exclusions sur l'environnement réel

### Exemple : détecter un DCSync

La Red Team exécute un DCSync (T1003.006) avec Mimikatz :

```
mimikatz # lsadump::dcsync /domain:corp.local /user:krbtgt
```

Artefacts générés :
- Event ID 4662 : accès à l'objet AD avec droits de réplication (DS-Replication-Get-Changes)
- Trafic DRS (Directory Replication Service) depuis une machine qui n'est pas un DC

Règle Sigma :

```yaml
title: DCSync Activity
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4662
        Properties|contains:
            - '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2'  # DS-Replication-Get-Changes
            - '1131f6ad-9c07-11d1-f79f-00c04fc2dcd2'  # DS-Replication-Get-Changes-All
    filter:
        SubjectUserName|endswith: '$'
        SubjectUserName|contains: 'DC'
    condition: selection and not filter
level: critical
```

## Mesurer la couverture

### Métriques utiles

| Métrique | Description |
|---|---|
| **Couverture ATT&CK** | % de techniques avec au moins une détection |
| **Taux de détection initial** | % de techniques détectées avant correction |
| **Taux de détection final** | % de techniques détectées après correction |
| **MTTD** (Mean Time To Detect) | Temps moyen entre l'exécution et l'alerte |
| **Visibilité par data source** | Quelles sources de logs couvrent quelles techniques |
| **Gap analysis** | Techniques sans aucune visibilité (pas de log collecté) |

### Niveaux de maturité de détection

Pour chaque technique, évaluer le niveau :

| Niveau | Description |
|---|---|
| 0 — Aucun | Pas de visibilité, pas de log |
| 1 — Minimal | Logs collectés mais pas de règle |
| 2 — Procédural | Règle qui détecte un outil spécifique (ex: Mimikatz par hash) |
| 3 — Comportemental | Règle qui détecte le comportement sous-jacent (ex: DRS request depuis un non-DC) |
| 4 — Avancé | Détection résistante à l'évasion, corrélation multi-sources, ML |

L'objectif est de monter au niveau 3 minimum sur les techniques prioritaires. Le niveau 2 (signature d'outil) est fragile : l'attaquant change d'outil et la détection saute.

## Fréquence et intégration

Le Purple Teaming est plus efficace en **continu** qu'en exercice ponctuel :

- **Mensuel** : tester 5-10 techniques ciblées (rotation par tactique ATT&CK)
- **Après chaque changement** : nouveau SIEM, nouvel EDR, migration cloud — re-valider les détections
- **Après chaque incident** : les techniques utilisées par l'attaquant réel deviennent prioritaires
- **BAS continu** : les plateformes comme SafeBreach ou AttackIQ exécutent des simulations en permanence et alertent si une détection régresse

## Références

- **MITRE ATT&CK** (`attack.mitre.org`) — matrice des techniques adverses
- **Atomic Red Team** (`github.com/redcanaryco/atomic-red-team`) — tests d'attaque par technique
- **MITRE Caldera** (`caldera.mitre.org`) — émulation d'adversaire automatisée
- **Sigma** (`github.com/SigmaHQ/sigma`) — règles de détection portables
- **DeTT&CT** (`github.com/rabobank-cdc/DeTTECT`) — cartographie données/détections sur ATT&CK
