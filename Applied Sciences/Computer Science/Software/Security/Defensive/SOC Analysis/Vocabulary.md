---
title: "Vocabulaire SOC et réponse à incident"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc]
date: "2025-12-31"
---

# Vocabulaire SOC et réponse à incident

Glossaire de référence des acronymes et termes rencontrés dans le quotidien d'un analyste SOC.

## Structures et acteurs

**SOC** (*Security Operations Center*) — équipe dédiée à la détection, l'analyse et la réponse aux incidents de sécurité, 24/7 dans les grandes organisations.

**CERT** (*Computer Emergency Response Team*) — équipe de réponse aux urgences informatiques. Terme historique (CERT/CC créé à Carnegie Mellon en 1988 après le ver Morris).

**CSIRT** (*Computer Security Incident Response Team*) — synonyme pratique de CERT, plus utilisé en Europe. La différence est largement sémantique.

**DFIR** (*Digital Forensics and Incident Response*) — discipline et équipe combinant l'analyse forensique numérique et la réponse à incident. Intervient typiquement après qu'un incident a été confirmé.

**MSSP** (*Managed Security Service Provider*) — prestataire externe qui opère tout ou partie du SOC d'un client.

**MDR** (*Managed Detection and Response*) — service externalisé de détection et réponse, plus actif qu'un MSSP classique (chasse proactive, réponse déléguée).

## Outils et technologies

**SIEM** (*Security Information and Event Management*) — plateforme qui centralise, corrèle et alerte sur les logs de sécurité. Exemples : Splunk, Elastic Security, QRadar, Sentinel.

**SOAR** (*Security Orchestration, Automation and Response*) — automatise les réponses aux alertes via des playbooks. Exemples : Cortex XSOAR, Splunk SOAR, Tines.

**EDR** (*Endpoint Detection and Response*) — agent sur les postes et serveurs qui collecte la télémétrie (processus, réseau, fichiers) et permet la détection comportementale. Exemples : CrowdStrike Falcon, SentinelOne, Microsoft Defender for Endpoint.

**XDR** (*Extended Detection and Response*) — généralisation de l'EDR à plusieurs sources (endpoint + réseau + cloud + identité) avec corrélation unifiée.

**NDR** (*Network Detection and Response*) — détection centrée sur le trafic réseau (analyse NetFlow, PCAP, DNS).

**IDS / IPS** (*Intrusion Detection / Prevention System*) — détecte (IDS) ou bloque (IPS) des signatures d'attaque dans le trafic. Exemples : Suricata, Snort, Zeek.

**WAF** (*Web Application Firewall*) — filtre HTTP applicatif qui bloque les attaques web (injections SQL, XSS, path traversal). Exemples : ModSecurity, Cloudflare, AWS WAF.

## Renseignement et méthode

**TTPs** (*Tactics, Techniques, and Procedures*) — vocabulaire du framework **MITRE ATT&CK** pour décrire le comportement d'un attaquant. Tactique = objectif, technique = moyen, procédure = implémentation spécifique.

**IOC** (*Indicator of Compromise*) — donnée observable indiquant une compromission : hash de fichier, IP, domaine, clé de registre. Périssable : l'attaquant peut changer d'infrastructure rapidement.

**IOA** (*Indicator of Attack*) — indicateur comportemental plus résilient qu'un IOC (ex. "processus Word qui lance PowerShell avec encoded command"). Reste pertinent même si les binaires changent.

**CTI** (*Cyber Threat Intelligence*) — renseignement sur les menaces, décliné en trois niveaux :
- **Stratégique** : tendances, acteurs, géopolitique (pour direction)
- **Tactique** : TTPs, campagnes (pour SOC et chasse)
- **Opérationnel / technique** : IOCs, signatures (pour outils)

**TI sharing** — partage de renseignement via **STIX** (format) et **TAXII** (protocole), ou plateformes comme MISP.

## Types de menaces

**APT** (*Advanced Persistent Threat*) — groupe d'attaquants sophistiqué, souvent étatique, qui vise une persistance longue sur une cible précise. Exemples : APT28 (Russie, GRU), APT29 (Russie, SVR), Lazarus (Corée du Nord), APT41 (Chine).

**Ransomware** — chiffrement malveillant des données avec demande de rançon. Variantes modernes ajoutent la **double extorsion** (exfiltration + publication).

**Malware** — terme générique. Sous-types : virus, ver, trojan, rootkit, dropper, loader, stealer, wiper.

**Webshell** — script malveillant (PHP, ASP, JSP, ASPX) déposé sur un serveur web compromis. Permet à l'attaquant de conserver un accès et d'exécuter des commandes sans backdoor classique. Sa ressemblance avec du code légitime complique la détection.

**LOLBins / LOLBAS** (*Living Off the Land Binaries*) — usage de binaires légitimes du système (PowerShell, certutil, rundll32, wmic) pour des actions malveillantes, sans déployer de nouveau binaire. Base de référence : `lolbas-project.github.io`.

**C2** (*Command and Control*) — serveur de contrôle d'un attaquant qui pilote ses implants. Canaux fréquents : HTTPS, DNS tunneling, services cloud légitimes (Slack, Telegram, GitHub).

## Analyse technique

**Hash** — empreinte cryptographique (MD5, SHA-1, SHA-256) d'un fichier. Identifiant unique pour IOC.

**Fuzzy hashing** — hachage qui mesure la **similarité** entre deux fichiers au lieu de l'identité. Utile pour détecter des variantes d'un même malware. Algorithmes courants : **ssdeep**, **TLSH**, **imphash** (spécifique aux imports PE).

**YARA** — langage de règles pour identifier des familles de malwares par patterns (chaînes, octets, conditions). Standard de fait pour la détection statique.

**Sigma** — équivalent de YARA pour les logs : règles de détection portables entre SIEM.

**PCAP** (*Packet Capture*) — fichier de capture réseau (Wireshark, tcpdump) utilisé pour l'analyse forensique réseau.

**Triage** — première analyse rapide d'une alerte pour décider si c'est un vrai incident ou un faux positif.

## Cycle de vie d'un incident

**NIST SP 800-61** décrit 4 phases :
1. **Preparation** — outillage, procédures, exercices
2. **Detection & Analysis** — identification et qualification
3. **Containment, Eradication & Recovery** — confinement, éradication, restauration
4. **Post-Incident Activity** — retour d'expérience, leçons apprises

**MTTD** (*Mean Time To Detect*) — délai moyen entre le début d'une attaque et sa détection.

**MTTR** (*Mean Time To Respond* / *Recover*) — délai moyen entre la détection et la résolution / restauration.

**Dwell time** — temps passé par l'attaquant dans le système avant détection. Benchmark Mandiant 2023 : 10 jours en moyenne.

## Normes et cadres

**ISO/IEC 27035** — norme internationale pour la gestion des incidents de sécurité de l'information. Fournit un cadre processus en plusieurs parties (planification, détection, réponse, leçons apprises).

**ISO/IEC 27001** — norme de management de la sécurité de l'information (SMSI).

**MITRE ATT&CK** — base de connaissance des TTPs d'attaquants, structurée par tactiques (Initial Access, Execution, Persistence, Lateral Movement, Exfiltration…).

**Kill Chain (Lockheed Martin)** — modèle en 7 étapes : Reconnaissance → Weaponization → Delivery → Exploitation → Installation → C2 → Actions on Objectives.

**Pyramid of Pain (David Bianco)** — hiérarchie des IOCs selon le coût pour l'attaquant de les changer : hash (trivial) < IP < domaine < artefact réseau/hôte < outils < **TTPs** (très coûteux).
