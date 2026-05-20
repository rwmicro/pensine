---
title: "SOAR (Security Orchestration, Automation and Response)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc]
date: "2025-03-08"
---

# SOAR (Security Orchestration, Automation and Response)

Le SOAR orchestre des workflows de sécurité entre outils hétérogènes et automatise les tâches répétitives de réponse aux incidents. Là où le SIEM détecte, le SOAR agit. L'objectif est de réduire le MTTR (Mean Time to Respond) et de libérer les analystes des tâches à faible valeur ajoutée.

## SIEM vs SOAR

| Dimension | SIEM | SOAR |
|---|---|---|
| Rôle principal | Collecte, corrélation, détection | Orchestration, automatisation, réponse |
| Entrée | Logs bruts | Alertes (dont du SIEM) |
| Sortie | Alertes | Actions sur les outils, tickets, rapports |
| Interaction | Passive (visualisation) | Active (exécute des actions) |
| Valeur ajoutée | Visibilité | Vitesse de réponse, cohérence |

En pratique, SIEM et SOAR sont complémentaires et souvent couplés (Splunk SOAR, Microsoft Sentinel + Logic Apps, IBM QRadar + SOAR).

## Composants d'un SOAR

### Playbooks (Runbooks automatisés)

Un playbook est un workflow décisionnel qui orchestre les actions à effectuer en réponse à un type d'incident.

```
Alerte SIEM : "Login depuis une IP de réputation faible"
        ↓
[Enrichissement automatique]
  → Vérifier réputation IP (VirusTotal, AbuseIPDB)
  → Vérifier l'historique de l'utilisateur (AD)
  → Chercher d'autres alertes liées au même utilisateur (30 dernières minutes)
        ↓
[Décision automatique]
  SI score de réputation IP > 80 ET utilisateur VIP
    → Bloquer IP (firewall)
    → Révoquer session (AD)
    → Créer ticket P1 (ServiceNow)
    → Notifier RSSI (email/Slack)
  SINON SI score > 50
    → Créer ticket P2 pour review analyste
    → Ajouter IP en watchlist SIEM
  SINON
    → Fermer l'alerte (FP probable)
    → Ajouter à la whitelist
```

### Intégrations (Connectors)

Le SOAR s'intègre avec l'ensemble de l'écosystème de sécurité via des APIs :

| Catégorie | Outils intégrés typiques |
|---|---|
| SIEM | Splunk, Elastic, Sentinel, QRadar |
| EDR | CrowdStrike, SentinelOne, Carbon Black |
| Threat Intelligence | VirusTotal, MISP, Recorded Future, Shodan |
| Firewall / NAC | Palo Alto, Cisco ASA, FortiGate |
| Identité | Active Directory, Okta, Azure AD |
| Ticketing | ServiceNow, Jira, PagerDuty |
| Communication | Slack, Teams, email |
| Cloud | AWS GuardDuty, Azure Defender, GCP SCC |
| Sandbox | Any.run, Cuckoo, Joe Sandbox |

### Case Management

Le SOAR centralise la gestion des incidents : timeline des événements, pièces jointes, actions effectuées, statut, assignation. Les analystes travaillent depuis une interface unifiée plutôt que de jongler entre outils.

## Playbooks courants

### Phishing

```
1. Réception d'un signalement (email forwarded, alerte proxy)
2. Extraire les IOCs : URLs, pièces jointes, expéditeur, IPs
3. Analyser les URLs (VirusTotal, urlscan.io)
4. Analyser les pièces jointes (sandbox)
5. Chercher si d'autres utilisateurs ont reçu le même email
6. Si malveillant :
   → Supprimer l'email de toutes les boîtes (Exchange API / M365)
   → Bloquer le domaine expéditeur (email gateway)
   → Bloquer les URLs/IPs (proxy/firewall)
   → Créer ticket + notifier les utilisateurs concernés
7. Documenter les IOCs dans MISP
```

### Alerte malware (EDR)

```
1. Réception de l'alerte EDR
2. Enrichir le hash (VirusTotal, MalwareBazaar)
3. Chercher le hash sur tous les endpoints (EDR query)
4. Isoler la machine compromise (EDR isolation)
5. Collecter les artefacts forensiques (EDR live response)
6. Vérifier les mouvements latéraux (logs AD, NetFlow)
7. Si spread détecté → isoler les autres machines
8. Créer ticket d'incident, notifier IR team
```

### Accès suspect (brute force / credential stuffing)

```
1. SIEM alerte : X échecs + 1 succès
2. Enrichir IP (géolocalisation, réputation, ASN)
3. Vérifier si l'IP a tenté d'autres comptes (lateral spread)
4. Vérifier si le compte ciblé est VIP / privilégié
5. Si compte compromis suspect :
   → Reset du mot de passe (AD)
   → Révoquer les sessions actives (AAD / Okta)
   → Bloquer IP source (firewall)
   → Notifier l'utilisateur
6. Documenter l'incident
```

## Métriques SOAR

| Métrique | Description | Objectif |
|---|---|---|
| Taux d'automatisation | % d'alertes traitées sans intervention humaine | > 70% |
| MTTR (automatisé) | Temps de résolution des incidents auto | < 5 min |
| MTTR (manuel) | Temps de résolution avec analyste | < 2h |
| Réduction de charge | Heures analyste économisées / mois | Mesurer la tendance |
| Taux de faux positifs | % d'alertes auto-fermées comme FP incorrectement | < 5% |

## Solutions SOAR

| Produit | Type | Notes |
|---|---|---|
| **Splunk SOAR** (ex-Phantom) | Commercial | Très riche en intégrations, Python |
| **Microsoft Sentinel** | Cloud | Logic Apps + Playbooks, intégration M365 |
| **IBM QRadar SOAR** (ex-Resilient) | Commercial | Gestion de cas avancée |
| **Palo Alto XSOAR** (ex-Demisto) | Commercial | Marketplace de contenus |
| **TheHive + Cortex** | Open source | TheHive = case management, Cortex = analyseurs |
| **Shuffle** | Open source | Low-code, docker-based |

## TheHive + Cortex (stack open source)

```
SIEM/EDR → Alerte → TheHive (case management)
                         ↓
                    Cortex (analyseurs)
                    ├── VirusTotal
                    ├── Shodan
                    ├── MISP
                    └── AbuseIPDB
                         ↓
                    Résultats enrichis dans le case
```

```python
# Créer un case TheHive via API
import requests

case = {
    "title": "Phishing Campaign - 2024-01-15",
    "description": "Multiple users received phishing emails",
    "severity": 2,       # 1=Low, 2=Medium, 3=High, 4=Critical
    "tlp": 2,            # TLP:AMBER
    "tags": ["phishing", "initial-access"],
    "tasks": [
        {"title": "Analyze phishing email"},
        {"title": "Identify affected users"},
        {"title": "Block IOCs"}
    ]
}

response = requests.post(
    "http://thehive:9000/api/case",
    headers={"Authorization": "Bearer API_KEY"},
    json=case
)
```

## Bonnes pratiques

- **Commencer simple** : automatiser d'abord les enrichissements avant les actions bloquantes
- **Toujours avoir un mode manuel** : une action automatique peut être overridée par un analyste
- **Tester les playbooks** en environnement de staging avant production
- **Versionner** les playbooks dans git
- **Audit trail** : chaque action automatique doit être tracée (qui, quoi, quand)
- **Escalade claire** : définir les seuils au-delà desquels un humain doit prendre la main
