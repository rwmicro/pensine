---
title: "Structure d'un SOC"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc]
date: "2025-02-15"
---

# Structure d'un SOC

Un Security Operations Center (SOC) est une cellule centralisée dédiée à la surveillance, la détection, la réponse et la mitigation des menaces cyber. Son organisation, ses processus et ses outils déterminent directement sa capacité à protéger l'organisation.

## Modèles d'organisation

### SOC interne (In-house)

L'organisation maintient son propre SOC avec des équipes dédiées.

| Avantages | Inconvénients |
|-----------|---------------|
| Connaissance approfondie du contexte métier | Coût élevé (personnel, outils, formation continue) |
| Réactivité maximale | Difficulté à trouver et retenir les talents |
| Contrôle total sur les données | Risque d'angle mort (même équipe, même biais) |
| Pas de dépendance externe | Disponibilité 24/7 coûteuse |

### SOC externalisé (MSSP — Managed Security Service Provider)

Un prestataire tiers assure tout ou partie de la fonction SOC.

| Avantages | Inconvénients |
|-----------|---------------|
| Coût maîtrisé, pas de CAPEX | Connaissance métier limitée |
| Expertise et outils mutualisés | Temps de réponse potentiellement plus longs |
| 24/7 inclus | Dépendance contractuelle |
| Montée en charge rapide | Accès partagé aux experts |

### SOC hybride

Combinaison : équipe interne pour le contexte et la réponse, MSSP pour la surveillance 24/7.

### SOC virtuel (vSOC)

Équipe distribuée géographiquement, sans site physique dédié. Courant dans les entreprises cloud-first.

## Tiers et rôles

### Tier 1 — Alert Triage

**Mission** : Premier filtre. Reçoit toutes les alertes SIEM, trie et qualifie.

Tâches quotidiennes :
- Monitoring de la file d'alertes
- Qualification initiale (vrai positif / faux positif)
- Analyse de premier niveau (log, context, timeline)
- Escalade vers Tier 2 si incident confirmé
- Clôture des faux positifs documentés

Outils : SIEM (Splunk, Sentinel), ticketing (ServiceNow, TheHive), threat intel feeds.

Métriques : MTTA (Mean Time To Acknowledge), taux de FP, volume alertes traitées/heure.

### Tier 2 — Incident Investigation

**Mission** : Investigation approfondie des incidents escaladés.

Tâches :
- Déterminer la portée (scope) de l'incident
- Collecter et analyser les preuves (forensics, logs)
- Identifier le vecteur d'attaque initial
- Détecter les compromissions latérales
- Coordonner les actions de containment
- Rédiger les rapports d'incident

Outils : EDR, SOAR, Velociraptor, Volatility, Wireshark, CyberChef.

### Tier 3 — Threat Hunting & Advanced Analysis

**Mission** : Chasse proactive aux menaces non détectées.

Tâches :
- Threat hunting (hypothèses basées sur TI ou anomalies)
- Analyse de malware avancée
- Reverse engineering
- Forensics digital approfondi
- Développement de nouvelles signatures et règles de détection
- Veille sur les nouvelles menaces et TTPs

Outils : Ghidra, IDA, CAPE, MITRE ATT&CK Navigator, Atomic Red Team.

### Threat Intelligence Analyst

**Mission** : Collecter, analyser et diffuser le renseignement sur les menaces.

Tâches :
- Suivi des acteurs menaçants pertinents pour l'organisation
- Production de rapports tactiques et stratégiques
- Alimentation des outils (MISP, blocklists) en IOCs
- Briefings pour la direction et les équipes techniques
- Participation aux ISACs (Information Sharing and Analysis Centers)

### Detection Engineer

**Mission** : Concevoir et maintenir le contenu de détection (règles SIEM, EDR, IDS).

Tâches :
- Écriture de règles Sigma, SPL, KQL, EQL
- Tests et validation des détections (Atomic Red Team)
- Réduction des faux positifs
- Mapping sur MITRE ATT&CK
- Gestion du backlog de détection

### DFIR (Digital Forensics & Incident Response) Analyst

**Mission** : Investigation forensique lors d'incidents majeurs.

Tâches :
- Collecte légale de preuves (acquisition disque/mémoire)
- Analyse forensique (timeline, artefacts)
- Analyse de malware
- Reconstitution de l'attaque
- Rédaction de rapports légaux/judiciaires

### Security Engineer / Architect

**Mission** : Concevoir, déployer et maintenir l'infrastructure du SOC.

Tâches :
- Administration SIEM (parsers, indexation, performances)
- Intégration des sources de logs
- Déploiement et configuration EDR, IDS, honeypots
- Automatisation SOAR (playbooks)
- Maintien de la plateforme de Threat Intelligence

## Équipes complémentaires

### Blue Team (Défense)

Regroupe SOC + équipe vulnérabilités + équipe hardening. Objectif : réduire la surface d'attaque et détecter les compromissions.

### Red Team (Offensif)

Simule des attaquants réels (APT) avec des TTPs sophistiquées sur une durée prolongée (weeks/months). Objectif : évaluer l'efficacité des défenses réelles.

Différence avec pentest :
- Pentest : liste de vulnérabilités techniques, durée courte
- Red Team : scénario réaliste (objectif business), discret, pas de notification préalable

### Purple Team

Collaboration structurée entre Red et Blue pour maximiser l'amélioration :
1. Red Team exécute une TTP (ex: Kerberoasting)
2. Blue Team observe et analyse sa capacité à détecter
3. Ajustement des détections si angle mort
4. Documentation dans la base de connaissances

### Vulnerability Management Team

- Scans de vulnérabilités réguliers (Nessus, Qualys)
- Priorisation selon CVSS + EPSS + contexte business
- Suivi de la remédiation avec les équipes IT
- Gestion du programme bug bounty

## Processus fondamentaux

### Cycle de vie d'un incident

```
Détection (SIEM, EDR, utilisateur)
        ↓
Qualification / Triage (Tier 1)
        ↓
Investigation (Tier 2)
        ├─ Incident confirmé → Containment
        └─ Faux positif → Clôture + tuning règle
        ↓
Containment (isolation, blocage)
        ↓
Eradication (suppression malware, patches)
        ↓
Recovery (restauration services)
        ↓
Post-Incident Review (lessons learned)
```

### Classification des incidents

| Niveau | Définition | Exemples | SLA réponse |
|--------|-----------|---------|------------|
| P1 — Critique | Impact business majeur, compromission active | Ransomware actif, exfiltration en cours | < 15 min |
| P2 — Élevé | Compromission probable, données sensibles exposées | Compte admin compromis, C2 actif | < 1h |
| P3 — Moyen | Activité suspecte, pas de compromission confirmée | Brute force, scan interne | < 4h |
| P4 — Faible | Violations de politique, anomalies mineures | Accès hors heures, port scan externe | < 24h |

### Runbooks et playbooks

Procédures documentées pour les scénarios courants :

- **Phishing reçu** : extraire IOCs, bloquer sender/URL, vérifier clics d'autres utilisateurs
- **Malware détecté par EDR** : isoler la machine, collecter artefacts, analyser
- **Brute force SSH** : vérifier si IP bloquée, examiner les logs, bloquer si nécessaire
- **Data exfiltration suspectée** : quantifier le volume, identifier la destination, containment
- **Compte compromis** : réinitialiser password, révoquer sessions, MFA forcé

## Métriques SOC

| Métrique | Description | Cible |
|---------|-------------|-------|
| MTTD (Mean Time To Detect) | Délai entre compromission et détection | < 24h |
| MTTA (Mean Time To Acknowledge) | Délai avant prise en charge de l'alerte | < 15 min (P1) |
| MTTR (Mean Time To Respond) | Délai de résolution de l'incident | < 4h (P1) |
| False Positive Rate | % d'alertes non pertinentes | < 10% |
| Alert Backlog | Alertes non traitées en file d'attente | < 24h de volume |
| Coverage | % des TTPs ATT&CK couverts par des détections | Croissant |
| Incidents per Analyst | Volume d'incidents traités par analyste/jour | Varie selon contexte |

## Stack technologique typique

| Catégorie | Solutions courantes |
|-----------|-------------------|
| SIEM | Splunk, Microsoft Sentinel, IBM QRadar, Elastic |
| EDR | CrowdStrike Falcon, SentinelOne, Microsoft Defender |
| SOAR | Splunk SOAR, Palo Alto XSOAR, TheHive+Cortex |
| Threat Intelligence | MISP, OpenCTI, Recorded Future, ThreatConnect |
| Vulnerability Scanner | Nessus Professional, Qualys VMDR |
| Network Detection | Darktrace, ExtraHop, Zeek |
| Forensics | Velociraptor, Volatility, KAPE, Autopsy |
| Case Management | TheHive, ServiceNow SecOps, IBM Resilient |
| Log Management | Graylog, Splunk, Elastic Stack |

## SOC 24/7 — Organisation humaine

Pour couvrir 24h/24 et 7j/7 avec 3 équipes de 8h :
- **Shift matin** (6h-14h)
- **Shift après-midi** (14h-22h)
- **Shift nuit** (22h-6h)

Chaque shift comporte :
- Handover meeting (30 min de passation) avec les incidents en cours
- Rapport de shift documenté dans le système de ticketing
- Au minimum 2 analystes par shift (couverture mutuelle)

La nuit, le volume d'alertes est généralement plus faible mais les attaques nocturnes sont fréquentes (exploitation des fuseaux horaires différents).
