---
title: "Threat Hunting (Chasse aux Menaces)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc]
date: "2026-02-25"
---

# Threat Hunting (Chasse aux Menaces)

Le Threat Hunting est une démarche **proactive** de recherche des menaces qui ont contourné les défenses automatisées. À l'inverse de la réponse à incident (réactive) ou de la détection SIEM (basée sur des règles connues), le hunter part d'une hypothèse et explore les données pour la confirmer ou l'infirmer — sans attendre une alerte.

## Pourquoi la chasse est nécessaire

Les outils de détection automatique (EDR, SIEM) sont efficaces contre les menaces connues, mais des études (Mandiant M-Trends) montrent que le délai médian entre la compromission initiale et la détection est de plusieurs dizaines de jours. Pendant ce temps, un attaquant évolue discrètement dans le réseau.

Le threat hunter cherche des signaux faibles : comportements anormaux qui ne déclenchent pas d'alerte mais indiquent une présence malveillante.

## Modèles de maturité

| Niveau | Caractéristiques |
|---|---|
| 0 — Réactif | Dépend totalement des alertes automatiques |
| 1 — Procédures | Quelques chasses périodiques sur des IOCs connus |
| 2 — Hypothèses | Chasses structurées basées sur TTPs (ATT&CK) |
| 3 — Instrumenté | Données de haute qualité, métriques, amélioration continue |
| 4 — Automatisé | Intégration des résultats dans les règles de détection |

## Cycle de chasse

```
1. Formuler une hypothèse
   → "Des attaquants peuvent utiliser des tâches planifiées pour la persistance"
   → Basée sur ATT&CK (T1053), Threat Intel, incidents récents du secteur

2. Collecter et filtrer les données
   → Définir les sources pertinentes (logs Sysmon, EDR, NetFlow)
   → Délimiter le périmètre (tous les serveurs Windows, derniers 30 jours)

3. Analyser et détecter
   → Chercher les patterns anormaux
   → Baseline du comportement normal, identifier les outliers

4. Investiguer les anomalies
   → Chaque anomalie n'est pas une menace — triage et contextualisation

5. Répondre si besoin
   → Escalader à l'équipe IR si compromission confirmée

6. Améliorer la détection
   → Transformer la chasse en règle SIEM/EDR pour automatiser
```

## Formuler une hypothèse

Une bonne hypothèse est spécifique, testable et ancrée dans une source de TI ou un TTP connu.

Modèles pour générer des hypothèses :
- **ATT&CK** : "Des attaquants utilisant PowerShell (T1059.001) génèrent des processus enfants anormaux depuis office.exe"
- **Threat Intel** : "Le groupe APT29 utilise WMI pour l'exécution latérale — cherchons des enfants inhabituels de WmiPrvSE.exe"
- **Observations terrain** : "On a des pics réseau inexpliqués la nuit — DGA ou tunneling DNS ?"
- **Crown Jewel Analysis** : "Qui accède à nos données les plus sensibles en dehors des heures normales ?"

## Sources de données

| Source | Données | Couvre |
|---|---|---|
| Sysmon | Processus, réseau, registre, fichiers | Endpoint Windows |
| EDR (CrowdStrike, SentinelOne) | Comportements, télémétrie enrichie | Endpoint |
| NetFlow / IPFIX | Flux réseau (IP, ports, volumes, durées) | Réseau |
| Proxy logs | URLs, user-agents, domaines | Web |
| DNS logs | Requêtes, réponses, NXDOMAIN | Réseau |
| Active Directory | Connexions Kerberos, changements comptes | Identité |
| Cloud logs | AWS CloudTrail, Azure Activity Log | Cloud |

## Techniques d'analyse

### Analyse des fréquences (Long Tail Analysis)

Identifier les événements rares qui sortent de la norme. La majorité des processus légitimes apparaissent souvent ; le malware tend à être rare.

```sql
-- Splunk : processus les moins fréquents lancés depuis cmd.exe
index=windows EventCode=4688 ParentProcessName="cmd.exe"
| stats count by ProcessName
| sort count asc
| head 20
```

### Stacking

Regrouper des événements similaires pour faire ressortir les valeurs uniques ou rares.

```sql
-- Processus lancés depuis Office (potentiel macros malveillantes)
index=windows EventCode=4688
    (ParentProcessName="WINWORD.EXE" OR ParentProcessName="EXCEL.EXE")
| stats count by ProcessName, ParentProcessName
| sort count asc
```

### Clustering / Baseline

Établir le comportement normal sur une période de référence, puis chercher les écarts.

```
Baseline : les 4 serveurs de prod font en moyenne 500 connexions DNS/heure
Anomalie : un serveur fait 15 000 requêtes DNS/heure vers des domaines inconnus
→ Hypothèse : DGA (Domain Generation Algorithm) ou DNS tunneling
```

### Analyse des relations

Graphe des connexions entre entités (IP, utilisateurs, machines) pour détecter les mouvements latéraux.

```
Machine A → PsExec → Machine B → Machine C
(utilisateur de service rarement connecté → accès inhabituels)
```

## Chasses courantes par catégorie

### Persistance (ATT&CK TA0003)

```powershell
# Chercher des RunKeys inhabituels
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run

# Tâches planifiées créées récemment
Get-ScheduledTask | Where-Object {$_.Date -gt (Get-Date).AddDays(-7)}

# Services créés récemment
Get-WinEvent -FilterHashtable @{LogName='System'; Id=7045} |
    Select-Object TimeCreated, Message | Sort-Object TimeCreated -Descending
```

### Living off the Land (LOLBins)

Les attaquants utilisent des binaires Windows légitimes pour évader la détection.

Binaires suspects à surveiller : `certutil.exe`, `mshta.exe`, `regsvr32.exe`, `rundll32.exe`, `wscript.exe`, `cscript.exe`, `bitsadmin.exe`, `forfiles.exe`

```sql
-- Splunk : usage de certutil pour télécharger
index=windows EventCode=4688 ProcessName="certutil.exe" CommandLine="*urlcache*"
| table _time, ComputerName, UserName, CommandLine
```

### Command and Control (TA0011)

```sql
-- Requêtes DNS vers des domaines à entropie élevée (potentiel DGA)
-- Calculer l'entropie de Shannon des noms de domaine
index=dns
| eval domain_length=len(query)
| where domain_length > 20
| stats count by query
| sort count asc

-- Connexions longues vers des IPs externes (potentiel C2 beaconing)
index=network
| stats sum(bytes) as total_bytes, count as nb_connexions, avg(duration) as duree_moy
  by src_ip, dest_ip
| where nb_connexions > 100 AND duree_moy < 5
-- Pattern de beaconing : nombreuses connexions courtes à intervalles réguliers
```

### Credential Access (TA0006)

```sql
-- Accès LSASS (Mimikatz typique)
-- Sysmon Event ID 10 : ProcessAccess sur lsass.exe
index=windows EventCode=10 TargetImage="*lsass.exe"
    NOT (SourceImage="*svchost.exe" OR SourceImage="*csrss.exe")
| table _time, SourceImage, GrantedAccess

-- Spraying de mots de passe : un compte tentant de s'authentifier sur beaucoup de cibles
index=windows EventCode=4648
| stats dc(TargetServerName) as targets by SubjectUserName
| where targets > 10
```

### Lateral Movement (TA0008)

```sql
-- PsExec / SMB admin shares
index=windows EventCode=7045
    ServiceFileName="*ADMIN$*" OR ServiceFileName="*C$*"

-- WMI remote execution
index=windows EventCode=4688 ParentProcessName="WmiPrvSE.exe"
    NOT ProcessName="WmiPrvSE.exe"
| table _time, ComputerName, ParentProcessName, ProcessName, CommandLine
```

## De la chasse à la détection

Le résultat d'une chasse réussie doit être transformé en règle automatique pour éviter de rechasser le même pattern manuellement.

```
Chasse (manuel) → Pattern identifié → Règle Sigma → Intégration SIEM → Alerte automatique
```

```yaml
# Règle Sigma issue d'une chasse sur certutil
title: CertUtil Used to Download File
status: stable
description: Detects certutil.exe being used to download a file (Living off the Land)
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    Image|endswith: '\certutil.exe'
    CommandLine|contains:
      - 'urlcache'
      - 'verifyctl'
      - '-decode'
  condition: selection
level: high
tags:
  - attack.defense_evasion
  - attack.t1105
  - attack.t1140
```

## Outils

| Outil | Usage |
|---|---|
| **Velociraptor** | Collecte et chasse à grande échelle (VQL) |
| **Elastic / Kibana** | Analyse de logs, dashboards |
| **Splunk** | Requêtes SPL, dashboards, alertes |
| **Humio / Falcon LogScale** | Haute vélocité, streaming |
| **MITRE Caldera** | Simulation d'adversaires pour tester les détections |
| **Atomic Red Team** | Tests unitaires par technique ATT&CK |
| **Sigma** | Format portable de règles de détection |
| **YARA** | Détection de patterns dans les fichiers et la mémoire |
