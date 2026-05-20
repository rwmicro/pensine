---
title: "Sigma"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc]
date: "2025-03-08"
---

# Sigma

Sigma est un langage de détection de menaces open-source conçu pour décrire des règles de détection de manière indépendante du fournisseur. Il permet de définir des règles de détection basées sur des logs de manière générique, ce qui les rend compatibles avec divers systèmes de gestion des informations et des événements de sécurité (SIEM). 

1. **Langage Générique** :
   - Sigma permet de décrire des règles de détection sans se soucier du format spécifique des logs ou du SIEM utilisé. Cela facilite le partage et la réutilisation des règles entre différentes plateformes.

2. **Compatibilité Multi-SIEM** :
   - Les règles Sigma peuvent être converties en requêtes spécifiques pour différents SIEM, comme Elasticsearch, Splunk, IBM QRadar, et bien d'autres, grâce à des outils de conversion.

3. **Communauté Active** :
   - Sigma bénéficie d'une communauté active qui contribue régulièrement à l'amélioration du langage et au développement de nouvelles règles de détection. Cela permet de rester à jour avec les dernières menaces et techniques d'attaque.

4. **Flexibilité et Extensibilité** :
   - Le langage est conçu pour être flexible et extensible, permettant aux utilisateurs de créer des règles complexes adaptées à leurs besoins spécifiques.

5. **Facilité de Partage** :
   - Les règles Sigma peuvent être facilement partagées entre les équipes de sécurité, les organisations et les communautés, ce qui favorise la collaboration et l'amélioration continue des capacités de détection.

## Créer un fichier Sigma
Pour créer des règles dans un fichier Sigma, plusieurs éléments clés doivent être inclus. 
Voici une liste plus détaillée des options possibles pour une règle Sigma, en incluant des exemples et des explications pour chaque champ :

1. `title`:
   - **Description** : Un titre descriptif pour la règle.
   - **Exemple** : "Détection de l'exécution de PowerShell à partir d'un emplacement inhabituel"

2. `id` :
   - **Description** : Un identifiant unique pour la règle, souvent sous la forme d'un UUID.
   - **Exemple** : "123e4567-e89b-12d3-a456-426614174000"
   - https://www.uuidgenerator.net/

3. `status` :
   - **Description** : Le statut de la règle, indiquant son niveau de maturité.
   - **Options possibles** :
     - `experimental` : La règle est en phase de test et peut ne pas être fiable.
     - `stable` : La règle a été testée et est considérée comme fiable.
     - `deprecated` : La règle est obsolète et ne doit plus être utilisée.
   - **Exemple** : "stable"

4. `description` :
   - **Description** : Une description détaillée de ce que la règle est censée détecter.
   - **Exemple** : "Cette règle détecte l'exécution de PowerShell à partir de répertoires non standard, ce qui peut indiquer une activité malveillante."

5. `author` :
   - **Description** : Le nom de l'auteur de la règle.
   - **Exemple** : "Jean Dupont"

6. `date` :
   - **Description** : La date de création de la règle.
   - **Format** : AAAA-MM-JJ
   - **Exemple** : "2023-10-01"

7. `tags` :
   - **Description** : Des étiquettes pour catégoriser la règle, souvent basées sur des frameworks comme MITRE ATT&CK.
   - **Exemples** :
     - `attack.execution`
     - `attack.t1059` (pour PowerShell)
     - `attack.persistence`
   - **Exemple** :
     ```yaml
     tags:
       - attack.execution
       - attack.t1059
     ```

8. `logsource` :
   - **Description** : Spécifie la source des logs à analyser.
   - **Champs possibles** :
     - `product` : Le produit générant les logs (par exemple, Windows, Linux).
     - `category` : La catégorie de logs (par exemple, process_creation, file_event).
     - `service` : Le service spécifique (par exemple, sysmon, powershell).
   - **Exemple** :
     ```yaml
     logsource:
       product: windows
       category: process_creation
       service: sysmon
     ```

9. `detection` :
   - **Description** : La section principale où les conditions de détection sont définies.
   - **Sous-sections possibles** :
     - **Selection** : Les critères principaux pour la détection.
     - **Condition** : Les conditions logiques appliquées aux critères de sélection.
   - **Exemple** :
     ```yaml
     detection:
       selection:
         EventID: 4689
         ParentImage: 'C:\Windows\System32\svchost.exe'
         Image: '*\powershell.exe'
       condition: selection
     ```

10. `falsepositives` :
    - **Description** : Les cas possibles de faux positifs.
    - **Exemple** : "Des administrateurs légitimes peuvent exécuter PowerShell à partir de répertoires non standard pour des tâches d'administration."

11. `level` :
    - **Description** : Le niveau de criticité de la règle.
    - **Options possibles** :
      - `low` : Faible criticité.
      - `medium` : Criticité moyenne.
      - `high` : Haute criticité.
      - `critical` : Criticité élevée.
    - **Exemple** : "high"

### Exemple complet de règle Sigma

```yaml
title: Détection de lexécution de PowerShell à partir d'un emplacement inhabituel
id: 123e4567-e89b-12d3-a456-426614174000
status: stable
description: Cette règle détecte lexécution de PowerShell à partir de répertoires non standard, ce qui peut indiquer une activité malveillante.
author: Jean Dupont
date: 2023-10-01
tags:
  - attack.execution
  - attack.t1059
logsource:
  product: windows
  category: process_creation
  service: sysmon
detection:
  selection:
    EventID: 4689
    ParentImage: 'C:\Windows\System32\svchost.exe'
    Image: '*\powershell.exe'
  condition: selection
falsepositives:
  - Des administrateurs légitimes peuvent exécuter PowerShell à partir de répertoires non standard pour des tâches dadministration.
level: high
```

### Convertir un format Sigma

```bash
# sigma-cli (outil officiel moderne)
pip install sigma-cli

# Convertir vers Splunk SPL
sigma convert -t splunk rule.yml

# Vers Elastic EQL
sigma convert -t elasticsearch rule.yml

# Vers KQL (Microsoft Defender / Sentinel)
sigma convert -t microsoft365defender rule.yml

# Vers QRadar AQL
sigma convert -t qradar rule.yml

# Depuis un dossier entier
sigma convert -t splunk rules/windows/

# Avec pipeline de mapping (spécifier le schéma de champs)
sigma convert -t splunk -p splunk_windows rule.yml
```

Outil en ligne : https://uncoder.io/

## Référence des logsources

| Catégorie | Produit | Événements couverts |
|-----------|---------|-------------------|
| `process_creation` | windows | Event ID 4688 (Sysmon 1) |
| `network_connection` | windows | Sysmon 3 |
| `file_event` | windows | Sysmon 11 |
| `registry_set` | windows | Sysmon 13 |
| `registry_add` | windows | Sysmon 12 |
| `image_load` | windows | Sysmon 7 |
| `create_remote_thread` | windows | Sysmon 8 |
| `raw_access_read` | windows | Sysmon 9 |
| `driver_load` | windows | Sysmon 6 |
| `dns_query` | windows | Sysmon 22 |
| `authentication` | linux | /var/log/auth.log |
| `webserver` | apache | access.log |

## Exemples de règles complètes

### Détection LSASS dump

```yaml
title: LSASS Memory Access by Non-System Process
id: a2d6b9e4-2c5f-4f1a-8e3b-1234567890ab
status: stable
description: Détecte un accès mémoire à LSASS depuis un processus non légitime (Mimikatz, etc.)
references:
    - https://attack.mitre.org/techniques/T1003/001/
author: Detection Team
date: 2024/01/15
tags:
    - attack.credential_access
    - attack.t1003.001
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
            - '0x1438'
    filter_legit:
        SourceImage|startswith:
            - 'C:\Windows\System32\'
            - 'C:\Windows\SysWOW64\'
            - 'C:\Program Files\Windows Defender\'
    condition: selection and not filter_legit
falsepositives:
    - Logiciels de sauvegarde ou antivirus
    - Outils d'administration Microsoft (Task Manager en mode debug)
fields:
    - SourceImage
    - GrantedAccess
    - TargetImage
level: high
```

### Détection de persistence via tâche planifiée

```yaml
title: Scheduled Task Creation via Schtasks
id: 92c1a18a-8e3d-4a5f-9c2b-0987654321cd
status: production
description: Détecte la création de tâches planifiées via schtasks.exe
references:
    - https://attack.mitre.org/techniques/T1053/005/
author: Detection Team
date: 2024/01/15
tags:
    - attack.persistence
    - attack.t1053.005
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\schtasks.exe'
        CommandLine|contains: '/create'
    filter_known_good:
        CommandLine|contains:
            - 'MicrosoftEdge'
            - 'GoogleUpdate'
            - 'Windows Defender'
    condition: selection and not filter_known_good
falsepositives:
    - Outils de déploiement légitimes (SCCM, Ansible, etc.)
    - Administrateurs créant des tâches planifiées manuellement
fields:
    - Image
    - CommandLine
    - ParentImage
    - User
level: medium
```

### Détection DNS inhabituel

```yaml
title: DNS Query to Suspicious TLD
id: f3a2b1c4-7e8d-4a5f-9c2b-abcdef123456
status: experimental
description: Détecte des requêtes DNS vers des TLDs rarement légitimes, souvent utilisés pour C2
author: Detection Team
date: 2024/01/15
tags:
    - attack.command_and_control
    - attack.t1071.004
logsource:
    category: dns_query
    product: windows
detection:
    selection:
        QueryName|endswith:
            - '.ru'
            - '.cn'
            - '.tk'
            - '.xyz'
            - '.onion'
            - '.bit'
    filter_corporate:
        # Exclure les domaines légitimes de votre organisation
        QueryName|contains:
            - 'windows.net'
            - 'microsoft.com'
    condition: selection and not filter_corporate
falsepositives:
    - Utilisateurs visitant des sites légitimes avec ces TLDs
    - Certaines applications avec des dépendances vers ces TLDs
level: low
```

## Opérateurs logiques et conditions

```yaml
# AND (sélection et filtre)
condition: selection and not filter

# OR (plusieurs sélections)
condition: selection1 or selection2

# Conditions combinées
condition: (selection1 or selection2) and not filter

# Compter (aggregate)
condition: selection | count() > 10

# Par champ
condition: selection | count(account_name) by workstation > 5

# Proximité temporelle (near, dans même événement)
condition: selection1 | near selection2

# Toutes les sélections
condition: all of selection*

# Au moins N parmi M
condition: 2 of (selection1, selection2, selection3)
```

## Dépôt de règles communautaires

Le dépôt officiel SigmaHQ contient plus de 3000 règles :

```bash
# Cloner le dépôt
git clone https://github.com/SigmaHQ/sigma

# Structure du dépôt
sigma/rules/
├── windows/
│   ├── process_creation/
│   ├── network_connection/
│   ├── registry_event/
│   └── ...
├── linux/
│   ├── auditd/
│   └── syslog/
├── cloud/
│   ├── aws/
│   └── azure/
└── web/

# Utiliser les règles communautaires
sigma convert -t splunk rules/windows/process_creation/ > splunk_all_rules.spl
```
