---
title: "Detection Engineering"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc]
date: "2025-03-08"
---

# Detection Engineering

L'ingénierie de la détection (Detection Engineering, DE) est la discipline qui consiste à concevoir, implémenter, tester et maintenir des règles de détection pour identifier des comportements malveillants dans les systèmes d'information. Elle s'oppose à une approche réactive en professionnalisant la création de détections.

## Philosophie et approche

### Detection-as-Code (DaC)

Les détections sont traitées comme du code source, avec les mêmes pratiques d'ingénierie logicielle :

- **Versioning** : Git, historique des modifications, blame
- **Peer review** : pull requests, validation avant déploiement
- **Tests automatisés** : CI/CD pipeline pour valider les règles
- **Documentation** : contexte, playbook, faux positifs connus
- **Réutilisabilité** : composants partagés, abstractions

### Threat-Informed Defense

Aligner les détections sur les menaces réelles ciblant l'organisation :

1. Identifier les acteurs menaçants pertinents (APT, cybercriminels, insiders)
2. Cartographier leurs TTPs sur MITRE ATT&CK
3. Prioriser les détections sur les TTPs les plus probables
4. Valider via des simulations (Red Team, Atomic Red Team)

### Pyramide de la douleur (Pyramid of Pain)

Indicateurs classés par difficulté pour l'attaquant de les changer :

```
[TTPs]          ← Difficile à changer (comportement fondamental)
[Outils]        ← Coûteux à modifier
[Artefacts réseau/host] ← Modifiable
[Domaines]      ← Facile à changer
[IPs]           ← Très facile à changer
[Hashes]        ← Trivial à changer
```

Cibler les TTPs offre la meilleure durabilité des détections.

## Cycle de vie d'une détection

```
Threat Intel / Hypothèse
        ↓
Recherche (query exploration)
        ↓
Prototype de règle
        ↓
Test sur données historiques (false positives, true positives)
        ↓
Tuning (ajustement seuils, exclusions)
        ↓
Review (pair, architecte)
        ↓
Déploiement en production (alert ou observe)
        ↓
Monitoring (performances, FP rate)
        ↓
Maintenance (mise à jour si TP rate chute)
```

## Frameworks de référence

### MITRE ATT&CK

14 tactiques, 200+ techniques, 400+ sous-techniques. Chaque technique documente :
- Description de la technique
- Procédures observées dans la nature
- Détections recommandées
- Mitigations

Usage pratique :
```
ATT&CK Navigator → visualiser la couverture de détection
Atomic Red Team  → tester une technique spécifique
ATT&CK Evaluations → benchmarker les outils EDR
```

### Cyber Kill Chain (Lockheed Martin)

| Phase | Description | Détections types |
|-------|-------------|-----------------|
| Reconnaissance | OSINT, scanning | DNS queries inhabituelles, scans nmap |
| Weaponization | Création du payload | Hors périmètre défensif |
| Delivery | Email, Web, USB | Email gateway, proxy, AV |
| Exploitation | Exécution du payload | EDR, process monitoring |
| Installation | Persistence | Registry, scheduled tasks, cron |
| C2 | Communication attaquant | Netflow, DNS beaconing |
| Actions on Objectives | Exfiltration, mouvement latéral | DLP, auth logs, file access |

### Unified Kill Chain

Extension de la Kill Chain avec 18 phases organisées en 3 epochs :
- **In (Initial Foothold)** : recon → delivery → exploitation → persistence
- **Through (Network Propagation)** : discovery → lateral movement → privilege escalation
- **Out (Action on Objectives)** : collection → exfiltration → impact

### MITRE D3FEND

Contre-partie défensive d'ATT&CK : catalogue de techniques de défense mappées aux techniques offensives.

## Sources de données pour la détection

| Source | Contenu | Couverture ATT&CK |
|--------|---------|------------------|
| Windows Event Logs | Auth, process, network, registry | Initial Access, Execution, Persistence, Lateral Movement |
| Sysmon | Process creation/injection, file, network, registry | Execution, Defense Evasion, Discovery |
| EDR (CrowdStrike, SentinelOne) | Comportements process, mémoire, réseau | Très large |
| Netflow / proxy logs | Connexions réseau, DNS | C2, Exfiltration |
| Email gateway | Headers, attachments, URLs | Phishing, Initial Access |
| Cloud trail (AWS/Azure/GCP) | API calls, IAM changes | Cloud-specific tactics |
| Firewall / IDS | Connexions bloquées, signatures | Network-based attacks |

### Event IDs Windows critiques

| Event ID | Description | Tactique ATT&CK |
|----------|-------------|----------------|
| 4624 | Login réussi | Lateral Movement |
| 4625 | Login échoué | Credential Access |
| 4648 | Login avec credentials explicites | Lateral Movement |
| 4688 | Création de processus | Execution |
| 4698 | Tâche planifiée créée | Persistence |
| 4702 | Tâche planifiée modifiée | Persistence |
| 4720 | Compte créé | Persistence |
| 4732 | Membre ajouté au groupe local | Privilege Escalation |
| 4768 | Demande ticket Kerberos (AS-REQ) | Credential Access |
| 4769 | Demande service ticket (TGS-REQ) | Lateral Movement |
| 4771 | Échec Kerberos pré-auth | Credential Access |
| 7045 | Service installé | Persistence |

### Sysmon Event IDs

| Event ID | Description |
|----------|-------------|
| 1 | Process Create |
| 2 | File creation time changed |
| 3 | Network connection |
| 5 | Process terminated |
| 6 | Driver loaded |
| 7 | Image loaded (DLL) |
| 8 | CreateRemoteThread |
| 10 | ProcessAccess (LSASS dump) |
| 11 | FileCreate |
| 12/13/14 | Registry events |
| 15 | FileCreateStreamHash (Alternate Data Stream) |
| 22 | DNS query |
| 23 | File delete |
| 25 | Process tampering |

## Écriture de règles Sigma

Sigma est un format de règles de détection générique, convertible vers n'importe quel SIEM (Splunk, Elastic, QRadar, Azure Sentinel, etc.).

### Structure d'une règle Sigma

```yaml
title: Suspicious PowerShell Encoded Command
id: a2e06f9b-8a74-4e3a-b88f-1234567890ab
status: production
description: Détecte l'utilisation de PowerShell avec des commandes encodées base64
references:
    - https://attack.mitre.org/techniques/T1059/001/
author: SOC Team
date: 2024/01/15
tags:
    - attack.execution
    - attack.t1059.001
    - attack.defense_evasion
    - attack.t1027
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains|all:
            - '-EncodedCommand'
    selection_alt:
        Image|endswith: '\powershell.exe'
        CommandLine|contains:
            - ' -enc '
            - ' -ec '
    condition: selection or selection_alt
falsepositives:
    - Certains outils légitimes d'administration utilisent des commandes encodées
    - SCCM, Ansible, certains scripts de déploiement
fields:
    - Image
    - CommandLine
    - ParentImage
    - User
level: medium
```

### Modificateurs de condition Sigma

| Modificateur | Description |
|-------------|-------------|
| `contains` | La valeur contient la chaîne |
| `startswith` | La valeur commence par |
| `endswith` | La valeur se termine par |
| `re` | Expression régulière |
| `contains|all` | Contient toutes les valeurs de la liste |
| `contains|any` | Contient au moins une valeur |
| `lt`, `lte`, `gt`, `gte` | Comparaisons numériques |
| `cidr` | Plage CIDR |
| `base64` | Valeur encodée en Base64 |
| `base64offset` | Avec offset de padding |
| `windash` | Wildcards `-` ou `/` pour les flags Windows |

### Niveaux de sévérité

| Niveau | Description |
|--------|-------------|
| informational | Pas directement malveillant, contexte |
| low | Comportement suspect, faible certitude |
| medium | Activité anormale, investigation recommandée |
| high | Très probablement malveillant |
| critical | Compromission confirmée ou imminente |

### Conversion avec sigma-cli

```bash
# Installer
pip install sigma-cli

# Convertir vers Splunk SPL
sigma convert -t splunk rule.yml

# Vers Elastic EQL
sigma convert -t elasticsearch-eql rule.yml

# Vers Azure KQL
sigma convert -t microsoft365defender rule.yml

# Depuis un dossier
sigma convert -t splunk rules/

# Avec pipeline de mapping
sigma convert -t splunk -p splunk_windows rule.yml
```

## Techniques de détection par TTP

### Execution (TA0002)

**T1059.001 — PowerShell**
```yaml
detection:
    selection:
        Image|endswith: '\powershell.exe'
        CommandLine|contains:
            - 'IEX'
            - 'Invoke-Expression'
            - 'DownloadString'
            - 'WebClient'
            - '-nop'
            - 'bypass'
            - '-w hidden'
```

**T1059.003 — cmd.exe chaînes suspectes**
```yaml
detection:
    selection:
        Image|endswith: '\cmd.exe'
        CommandLine|contains:
            - 'echo %COMSPEC%'
            - '/c certutil'
            - 'bitsadmin /transfer'
```

### Persistence (TA0003)

**T1053.005 — Scheduled Tasks**
```yaml
logsource:
    product: windows
    category: process_creation
detection:
    selection:
        Image|endswith: '\schtasks.exe'
        CommandLine|contains: '/create'
    condition: selection
```

**T1547.001 — Registry Run Keys**
```yaml
logsource:
    category: registry_set
    product: windows
detection:
    selection:
        TargetObject|contains:
            - '\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
            - '\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'
    condition: selection
```

### Credential Access (TA0006)

**T1003.001 — LSASS Memory Dump**
```yaml
logsource:
    category: process_access
    product: windows
detection:
    selection:
        TargetImage|endswith: '\lsass.exe'
        GrantedAccess|contains:
            - '0x1010'
            - '0x1410'
            - '0x147a'
            - '0x143a'
    condition: selection
```

### Defense Evasion (TA0005)

**T1055 — Process Injection (CreateRemoteThread)**
```yaml
logsource:
    category: create_remote_thread
    product: windows
detection:
    selection:
        TargetImage|endswith:
            - '\svchost.exe'
            - '\explorer.exe'
            - '\notepad.exe'
    filter:
        SourceImage|endswith:
            - '\csrss.exe'
            - '\werfault.exe'
    condition: selection and not filter
```

## Tests et validation

### Atomic Red Team

Bibliothèque de tests atomiques mappés sur ATT&CK pour valider les détections :

```powershell
# Installer
Install-Module -Name invoke-atomicredteam

# Lister les tests pour une technique
Invoke-AtomicTest T1059.001 -ShowDetails

# Exécuter un test
Invoke-AtomicTest T1059.001

# Avec cleanup
Invoke-AtomicTest T1059.001 -Cleanup

# Tester une liste de techniques
"T1059.001", "T1053.005", "T1547.001" | ForEach-Object {
    Invoke-AtomicTest $_ -TimeoutSeconds 60
}
```

### Valkeyrie / DetectionLab

DetectionLab : lab Vagrant/Terraform pré-configuré avec Splunk, Sysmon, Fleet, Velociraptor pour tester les détections dans un environnement réaliste.

```bash
# Déployer DetectionLab
git clone https://github.com/clong/DetectionLab
cd DetectionLab/Vagrant
vagrant up
```

### Métriques de qualité d'une détection

| Métrique | Définition | Cible |
|---------|-----------|-------|
| True Positive Rate (TPR) | Détections correctes / Total malveillant | > 90% |
| False Positive Rate (FPR) | Fausses alertes / Total bénin | < 5% |
| Precision | TP / (TP + FP) | > 80% |
| Latency | Délai entre événement et alerte | < 5 min |
| Coverage | % TTPs ATT&CK couverts | Croissant |

## Gestion du backlog de détection

### Priorisation

```
Score priorité = Impact × Probabilité × Facilité détection
```

| Critère | Poids |
|---------|-------|
| Pertinence métier (Crown Jewels menacés) | Élevé |
| Fréquence d'utilisation par les acteurs | Élevé |
| Absence de détection existante | Moyen |
| Facilité de tuning (peu de FP) | Moyen |
| Données disponibles | Bloquant |

### Registre des détections

Chaque règle en production doit documenter :

```markdown
## Règle : [Nom]

### Objectif
[Quoi détecter et pourquoi]

### Sources de données requises
[Logs, agents, configurations nécessaires]

### ATT&CK Coverage
Technique: T1234 — Nom de la technique

### Taux de faux positifs connu
[Cas de FP documentés + filtres appliqués]

### Actions recommandées (Playbook)
[Que faire quand cette alerte se déclenche]

### Date de dernière validation
[Date du dernier test avec Atomic Red Team]
```

## Outils

| Outil | Usage |
|-------|-------|
| Sigma | Format de règles universel |
| sigma-cli | Conversion Sigma vers SIEM |
| Atomic Red Team | Tests de validation TTPs |
| DetectionLab | Lab de test complet |
| MITRE ATT&CK Navigator | Visualisation couverture |
| Caldera | Simulation adversariale automatisée |
| Velociraptor | Collecte de forensics à grande échelle |
| Uncoder.IO | Convertisseur Sigma en ligne |
| Panther | SIEM cloud-native avec DaC |
