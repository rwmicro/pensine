---
title: "Splunk"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc]
date: "2025-02-15"
---

# Splunk

Splunk est la plateforme SIEM/SODA (Security Operations and Data Analytics) la plus déployée en entreprise. Elle collecte, indexe, corrèle et visualise les données de journalisation. La maîtrise du SPL (Splunk Processing Language) est une compétence fondamentale pour les analystes SOC.

## Architecture Splunk

```
Sources de données
    ↓
Forwarders (Universal Forwarder / Heavy Forwarder)
    ↓
Indexers (stockage + indexation)
    ↓
Search Head (interface utilisateur + SPL)
    ↓
Deployment Server (gestion de config)
```

| Composant | Rôle |
|-----------|------|
| Universal Forwarder (UF) | Agent léger installé sur les hôtes, transmet les logs bruts |
| Heavy Forwarder (HF) | Forwarder avec capacité de parsing et filtrage local |
| Indexer | Reçoit, parse, indexe et stocke les données |
| Search Head | Interface web, exécution des recherches SPL |
| Deployment Server | Distribution centralisée des configurations aux forwarders |
| License Master | Gestion des licences (volume de données indexées/jour) |

## Concepts fondamentaux

### Index et sourcetype

- **Index** : espace de stockage logique (ex: `index=windows`, `index=linux`, `index=proxy`)
- **Sourcetype** : type de données qui détermine comment parser (ex: `WinEventLog:Security`, `syslog`, `json`)
- **Source** : chemin ou origine du fichier log
- **Host** : machine qui a généré l'événement

```
index=windows sourcetype=WinEventLog:Security EventCode=4625
```

### Champs automatiques

Splunk extrait automatiquement :
- `_time` : timestamp de l'événement
- `_raw` : ligne brute originale
- `host`, `source`, `sourcetype`, `index`
- Champs parsés selon le sourcetype (ex: `EventCode`, `Account_Name`, `src_ip`)

## SPL — Splunk Processing Language

### Structure d'une recherche

```
[index/source] [filtres] | commande1 | commande2 | ...
```

Le pipe `|` passe les résultats d'une commande à la suivante.

### Opérateurs de recherche

```spl
-- Égalité
EventCode=4625

-- Wildcard
source="*windows*"

-- NOT
NOT EventCode=4624

-- AND (implicite entre termes)
EventCode=4625 Account_Name=*admin*

-- OR
EventCode=4625 OR EventCode=4648

-- Comparaisons
bytes > 1000000
duration >= 60

-- IN
EventCode IN (4624, 4625, 4648, 4720)

-- LIKE (moins performant que wildcard)
Account_Name LIKE "%admin%"
```

### Commandes essentielles

#### stats — Agrégation

```spl
-- Compter les événements par champ
index=windows EventCode=4625
| stats count by Account_Name

-- Plusieurs agrégations
index=proxy
| stats count, sum(bytes), avg(duration) by src_ip

-- Valeurs distinctes
index=windows
| stats dc(Account_Name) as unique_accounts by host

-- Premier et dernier événement
index=windows EventCode=4624
| stats earliest(_time) as first_seen, latest(_time) as last_seen, count by Account_Name

-- Valeurs uniques listées
| stats values(dest_ip) as destinations by src_ip
```

#### table, fields, rename

```spl
-- Afficher seulement certains champs
| table _time, Account_Name, EventCode, host, src_ip

-- Supprimer des champs
| fields - _raw, _serial

-- Renommer
| rename Account_Name as username, EventCode as event_id
```

#### eval — Calculs et transformations

```spl
-- Créer un champ calculé
| eval size_mb = bytes / 1024 / 1024

-- Condition
| eval risk = if(EventCode=4625, "high", "low")

-- Cas multiples
| eval category = case(
    EventCode=4624, "Login Success",
    EventCode=4625, "Login Failure",
    EventCode=4648, "Explicit Credentials",
    true(), "Other"
  )

-- Concaténation
| eval full_path = host + "\\" + Account_Name

-- Conversion de temps
| eval hour = strftime(_time, "%H")
| eval readable_time = strftime(_time, "%Y-%m-%d %H:%M:%S")

-- Champ booléen
| eval is_admin = if(match(Account_Name, "(?i)admin"), 1, 0)
```

#### where — Filtrage post-agrégation

```spl
-- Après stats, filtrer sur le résultat
| stats count by src_ip
| where count > 100

-- Conditions complexes
| where duration > 300 AND bytes > 1000000

-- Avec like
| where like(Account_Name, "%$")  -- comptes machine AD
```

#### sort, head, tail

```spl
-- Trier par nombre décroissant
| sort -count

-- Top 10
| sort -count | head 10

-- 10 derniers événements
| tail 10

-- Tri multi-champ
| sort -bytes, +_time
```

#### timechart — Séries temporelles

```spl
-- Événements par heure
index=windows EventCode=4625
| timechart count

-- Par champ
index=proxy
| timechart sum(bytes) by dest_domain

-- Avec span personnalisé
| timechart span=15m count by EventCode

-- Limiter le nombre de séries
| timechart count by Account_Name limit=5
```

#### rex — Extraction par regex

```spl
-- Extraire un champ
| rex field=_raw "Failed password for (?<username>\S+) from (?<src_ip>\d+\.\d+\.\d+\.\d+)"

-- Avec mode sed (remplacement)
| rex mode=sed field=_raw "s/password=\S+/password=REDACTED/g"
```

#### transaction — Grouper des événements liés

```spl
-- Regrouper les événements d'une session
index=web
| transaction session_id
| where duration > 300

-- Avec limites
| transaction src_ip maxspan=5m maxpause=30s
```

#### join — Jointure entre recherches

```spl
-- Inner join
| join src_ip [search index=threat_intel | fields ip, threat_score | rename ip as src_ip]

-- Left join
| join type=left Account_Name [search index=hr_data | fields username, department | rename username as Account_Name]
```

#### lookup — Enrichissement depuis une table

```spl
-- Enrichir avec une table CSV (uploadée dans Splunk)
| lookup threat_intel.csv ip as src_ip OUTPUT threat_level, campaign

-- Lookup géographique (iplocation)
| iplocation src_ip
| table src_ip, Country, City, lat, lon
```

#### dedup — Déduplication

```spl
-- Une seule occurrence par Account_Name
| dedup Account_Name

-- Garder le dernier
| dedup Account_Name sortby -_time
```

## Recherches SOC — Cas d'usage Security

### Brute force / Credential stuffing

```spl
index=windows EventCode=4625
| stats count by Account_Name, src_ip
| where count > 10
| sort -count
```

### Comptes compromis (login depuis plusieurs pays)

```spl
index=windows EventCode=4624
| iplocation src_ip
| stats dc(Country) as countries, values(Country) as country_list by Account_Name
| where countries > 1
```

### Lateral movement (accès inhabituels)

```spl
index=windows EventCode=4624 Logon_Type=3
| stats dc(dest) as targets by src_ip
| where targets > 5
| sort -targets
```

### Process suspects (LOLBins)

```spl
index=windows EventCode=4688
| where Process_Name IN ("*certutil*", "*bitsadmin*", "*mshta*", "*wscript*", "*cscript*", "*regsvr32*", "*rundll32*")
| table _time, host, Creator_Process_Name, Process_Name, Process_Command_Line
```

### PowerShell encodé

```spl
index=windows EventCode=4688
| where like(Process_Command_Line, "%-EncodedCommand%") OR like(Process_Command_Line, "%-enc %")
| table _time, host, Account_Name, Process_Command_Line
```

### Connexions réseau suspectes (C2 beaconing)

```spl
index=proxy
| bucket _time span=1h
| stats count by src_ip, dest_ip, _time
| stats stdev(count) as variance, avg(count) as mean, count as observations by src_ip, dest_ip
| where observations > 24 AND variance < 2
| sort variance
```

### Exfiltration de données

```spl
index=proxy
| stats sum(bytes_out) as total_bytes by src_ip, dest_domain
| eval MB = round(total_bytes/1024/1024, 2)
| where MB > 100
| sort -MB
| table src_ip, dest_domain, MB
```

### Nouveaux comptes créés

```spl
index=windows EventCode=4720
| table _time, host, Account_Name, Subject_Account_Name
| sort -_time
```

### Escalade de privilèges

```spl
index=windows EventCode=4672
| stats count by Account_Name
| sort -count
```

### Détection MITRE T1059 (Command and Scripting)

```spl
index=windows EventCode=4688
(Process_Name="*cmd.exe" OR Process_Name="*powershell.exe" OR Process_Name="*wscript.exe")
| stats count by host, Account_Name, Process_Name
| sort -count
```

## Alertes et rapports

### Créer une alerte (via UI ou config)

```
Paramètres d'une alerte Splunk :
- Schedule : Cron (ex: */15 * * * * pour toutes les 15 min)
- Condition de déclenchement : Number of results > 0
- Actions : Send email, Run script, Webhook (SOAR)
- Throttle : éviter les alertes répétitives (ex: 1h par src_ip)
```

### Saved Search (rapport planifié)

```spl
-- Exemple : rapport quotidien des logins échoués
index=windows earliest=-24h EventCode=4625
| stats count by Account_Name, src_ip
| where count > 5
| sort -count
| table Account_Name, src_ip, count
```

## Tableaux de bord (Dashboards)

Les dashboards utilisent le Simple XML ou le Dashboard Studio (JSON/CSS). Composants courants :

| Visualisation | SPL type | Usage |
|---------------|----------|-------|
| Single Value | `| stats count` | KPI (nb alertes, incidents) |
| Line Chart | `| timechart count` | Tendances temporelles |
| Bar Chart | `| stats count by field` | Comparaisons catégories |
| Pie Chart | `| stats count by field` | Répartition |
| Map | `| iplocation ip | geostats` | Géolocalisation |
| Table | `| table field1, field2` | Détail événements |
| Heatmap | `| timechart by field` | Densité temporelle |

## SIEM — Corrélation et Use Cases

### Notable Events (Splunk ES)

Dans Splunk Enterprise Security, les **Notable Events** correspondent aux alertes corrélées. Structure :

```
Correlation Search → Notable Event → Review Queue → Investigation
```

```spl
-- Correlation search example : Excessive Failed Logins
index=windows EventCode=4625
| bucket span=5m _time
| stats count by _time, Account_Name, src_ip
| where count >= 10
| eval rule_name="Excessive Failed Logins", severity="high"
| sendalert notable
```

### Risk Framework (Splunk ES)

Le Risk-Based Alerting (RBA) attribue des scores de risque aux entités :

```spl
-- Attribuer du risque à un utilisateur
| eval risk_score=70, risk_message="Login depuis pays inhabituel"
| eval risk_object=Account_Name, risk_object_type="user"
| sendalert risk_notifier
```

## Administration

```bash
# Redémarrer Splunk
/opt/splunk/bin/splunk restart

# Vérifier le statut
/opt/splunk/bin/splunk status

# Chercher dans les logs internes
index=_internal sourcetype=splunkd log_level=ERROR

# Vérifier l'usage de licence
index=_internal sourcetype=splunkd component=LicenseUsage type=RolloverSummary

# Forcer l'indexation d'un fichier
/opt/splunk/bin/splunk add oneshot /var/log/auth.log -index linux
```

## Comparaison SPL vs SQL

| SPL | SQL équivalent |
|-----|---------------|
| `stats count by field` | `SELECT field, COUNT(*) GROUP BY field` |
| `where count > 10` | `HAVING COUNT(*) > 10` |
| `sort -count` | `ORDER BY count DESC` |
| `head 10` | `LIMIT 10` |
| `eval x=y+z` | `SELECT y+z AS x` |
| `timechart count` | `SELECT DATE_TRUNC(interval, time), COUNT(*) GROUP BY 1` |
| `rex field=f "pattern"` | `REGEXP_EXTRACT(f, pattern)` |
| `lookup table.csv field` | `JOIN table ON field` |
