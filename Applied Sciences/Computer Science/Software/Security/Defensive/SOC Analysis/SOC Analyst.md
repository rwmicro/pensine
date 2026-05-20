---
title: "Analyste SOC"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc]
date: "2025-12-31"
---

# Analyste SOC

Un **analyste SOC** (Security Operations Center) est un professionnel de la cybersécurité qui surveille, détecte et répond aux incidents de sécurité en temps réel. Il opère dans un centre dédié qui monitore les systèmes d'une organisation 24h/24, 7j/7.


## Responsabilités

| Tâche | Description |
|-------|-------------|
| **Surveillance** | Analyser en continu les logs et alertes réseau |
| **Détection** | Identifier les comportements suspects ou malveillants |
| **Réponse** | Traiter les incidents, escalader si nécessaire |
| **Ticketing** | Ouvrir et suivre des tickets pour chaque incident |
| **Reporting** | Documenter les incidents et les actions effectuées |
| **Threat Intelligence** | Se tenir informé des nouvelles menaces et IOCs |
| **SIEM** | Utiliser des outils de corrélation de logs (Splunk, Elastic...) |


## Sources de données analysées

- **IDS/IPS** (Intrusion Detection/Prevention System) : alertes réseau en temps réel
- **Logs système** : journaux des serveurs, pare-feux, endpoints, applications
- **Emails suspects** : détection de phishing, pièces jointes malveillantes
- **Trafic réseau** : captures de paquets, anomalies de flux
- **Données forensiques** : artefacts sur des systèmes potentiellement compromis


## Terminologie de la menace

### Les acteurs

- **Adversary Operator** : la personne qui conduit techniquement l'attaque (le "hacker")
- **Adversary Customer** : l'entité qui bénéficie de l'attaque — peut être la même personne que l'opérateur ou un commanditaire distinct

### L'infrastructure d'attaque

**Type 1** — Infrastructure contrôlée directement par l'attaquant : ses propres serveurs, ses propres machines.

**Type 2** — Infrastructure intermédiaire : des machines compromises ou louées via des tiers, dans le but de **masquer l'origine réelle de l'attaque**. Exemples : serveurs de staging, domaines enregistrés sous faux noms, comptes email piratés.

**Fournisseurs de services** : organisations comme les hébergeurs, registrars ou webmail providers qui soutiennent involontairement l'infrastructure Type 1 ou Type 2.


## Niveaux dans un SOC (Tiers)

| Niveau | Rôle |
|--------|------|
| **Tier 1** | Triage des alertes, surveillance de premier niveau |
| **Tier 2** | Investigation approfondie des incidents escaladés |
| **Tier 3** | Threat hunting proactif, forensique avancée, corrélation |


## Outils courants

- **SIEM** : Splunk, IBM QRadar, Microsoft Sentinel, Elastic SIEM
- **Threat Intelligence** : VirusTotal, MISP, OpenCTI
- **Forensique** : Autopsy, Volatility (mémoire), Wireshark (réseau)
- **Ticketing** : TheHive, Jira, ServiceNow


## Plateformes d'entraînement

- [TryHackMe](https://tryhackme.com) — parcours SOC L1 dédié
- [LetsDefend](https://letsdefend.io) — simulation d'environnement SOC réel
- [BlueTeamLabs](https://blueteamlabs.online) — exercices défensifs
