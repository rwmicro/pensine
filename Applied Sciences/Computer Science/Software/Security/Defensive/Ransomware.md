---
title: "Ransomware — analyse et réponse"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité, ransomware, incident-response]
date: "2026-04-16"
---

# Ransomware — analyse et réponse

Le ransomware est la menace la plus destructrice en cybersécurité actuelle. Un ransomware chiffre les données d'une victime et exige une rançon (généralement en crypto-monnaie) pour fournir la clé de déchiffrement. Depuis 2019, les groupes majeurs pratiquent la **double extorsion** : chiffrement + exfiltration des données avec menace de publication.

## Chaîne d'attaque typique

La plupart des opérations ransomware suivent un schéma prévisible, souvent étalé sur **plusieurs jours à plusieurs semaines** entre l'accès initial et le chiffrement :

```
Accès initial (phishing, RDP, vuln)
    │
    ▼
Exécution de code (loader, dropper)
    │
    ▼
Persistence (tâches planifiées, clés registre, service)
    │
    ▼
Reconnaissance interne (AD, BloodHound, net commands)
    │
    ▼
Mouvement latéral (PsExec, WMI, RDP, SMB)
    │
    ▼
Élévation de privilèges (Kerberoasting, DCSync, exploits)
    │
    ▼
Exfiltration de données (rclone, MEGASync, FTP custom)
    │
    ▼
Désactivation des défenses (kill AV, delete shadow copies)
    │
    ▼
Chiffrement massif + note de rançon
```

## Vecteurs d'accès initial

| Vecteur | Fréquence | Exemples |
|---|---|---|
| **Phishing** | ~40 % | Pièce jointe macro, lien vers loader (Emotet, QakBot, IcedID) |
| **RDP exposé** | ~20 % | Brute-force ou credentials achetées sur le dark web |
| **Exploitation de vulnérabilités** | ~20 % | VPN (Fortinet CVE-2023-27997, Citrix CVE-2023-4966), Exchange (ProxyShell) |
| **Access brokers** | ~15 % | Achat d'accès initial déjà établi sur un marché underground |
| **Supply chain** | ~5 % | Compromission d'un fournisseur logiciel (Kaseya, SolarWinds) |

## Modèle économique : Ransomware-as-a-Service (RaaS)

Les groupes ransomware modernes fonctionnent comme des **franchises** :

- **Développeurs** : créent et maintiennent le ransomware (chiffreur, infrastructure, site de paiement, leak site)
- **Affiliés** : des opérateurs indépendants qui achètent l'accès au ransomware et mènent les opérations. Ils gardent 70-80 % de la rançon, le reste va aux développeurs.
- **Access brokers** : vendent des accès initiaux aux affiliés
- **Négociateurs** : certains groupes ont des équipes dédiées à la négociation avec les victimes

### Groupes majeurs (2023-2025)

| Groupe | Chiffreur | Particularité |
|---|---|---|
| **LockBit** | LockBit 3.0 (Black) | Le plus actif par volume, bug bounty pour son propre malware |
| **ALPHV / BlackCat** | Rust-based | Premier ransomware en Rust, cross-platform (Linux/Windows/ESXi) |
| **Cl0p** | Cl0p | Spécialisé en exploitation de vulnérabilités zero-day (MOVEit, GoAnywhere) |
| **Royal / BlackSuit** | Évolution de Conti | Cible les infrastructures critiques |
| **Akira** | C++ et Rust variants | Cible les VPN Cisco, réseaux VMware ESXi |
| **Play** | Play | Double extorsion, pas de négociation publique |

## Techniques de chiffrement

### Chiffrement hybride

Le ransomware utilise un schéma hybride pour la performance :

1. **Clé RSA publique de l'attaquant** embarquée dans le malware
2. Pour chaque fichier : génération d'une **clé AES-256 aléatoire** (symétrique, rapide)
3. Le fichier est chiffré avec la clé AES
4. La clé AES est chiffrée avec la **clé RSA publique** et stockée avec le fichier
5. Seule la **clé RSA privée** (que seul l'attaquant possède) peut déchiffrer les clés AES

### Optimisations courantes

- **Chiffrement partiel** : seuls les premiers Mo de chaque fichier sont chiffrés (plus rapide, suffisant pour rendre le fichier inutilisable)
- **Chiffrement intermittent** : chiffrer un bloc sur deux (détection plus difficile, impact identique)
- **Multi-threading** : paralléliser le chiffrement sur tous les cœurs pour maximiser la vitesse
- **Ciblage des extensions** : prioriser `.docx`, `.xlsx`, `.pdf`, `.sql`, `.vmdk`, `.bak` — ignorer les exécutables système

### Suppression des sauvegardes

Avant le chiffrement, le ransomware neutralise les options de récupération :

```cmd
vssadmin delete shadows /all /quiet
wmic shadowcopy delete
bcdedit /set {default} recoveryenabled no
wbadmin delete catalog -quiet
```

## Indicateurs de compromission (IOCs)

### Phase pré-chiffrement (détection précoce)

| Indicateur | Source de détection |
|---|---|
| Création massive de tâches planifiées | Event ID 4698 (Windows) |
| Exécution de `nltest`, `net group "Domain Admins"` | EDR, Sysmon Event ID 1 |
| BloodHound / SharpHound collecte AD | Trafic LDAP inhabituel, fichiers `.zip` de collecte |
| Désactivation de l'antivirus | Event ID 7045 (nouveau service), EDR tamper alerts |
| Rclone, MEGASync, WinSCP installés | AppLocker, SIEM |
| Trafic sortant massif vers des services cloud inhabituels | Proxy, NDR |
| PsExec, WMIC remote vers de multiples machines | Event ID 4648 (logon explicite), Sysmon Event ID 1 |

### Phase de chiffrement

| Indicateur | Source de détection |
|---|---|
| Renommage massif de fichiers (nouvelle extension) | EDR file monitoring, honeypot files |
| `vssadmin delete shadows` | Sysmon Event ID 1, Sigma rule |
| Note de rançon déposée dans chaque dossier | EDR, pattern matching sur nom de fichier |
| CPU à 100 % sur de multiples machines simultanément | Monitoring infrastructure |

## Réponse à incident

### Premières 30 minutes

1. **Contenir** — isoler les machines touchées du réseau (pas les éteindre, la RAM contient des artefacts)
2. **Évaluer l'étendue** — combien de machines, quels segments, le DC est-il compromis ?
3. **Préserver les preuves** — dump RAM des machines clés avant toute action destructive
4. **Activer le plan de crise** — escalade direction, juridique, communication, assurance cyber

### Investigation

- **Identifier le vecteur d'accès initial** (logs VPN, logs email, EDR timeline)
- **Identifier le patient zéro** (première machine chiffrée, timeline des fichiers modifiés)
- **Cartographier le mouvement latéral** (logs AD, Event ID 4624 type 3, PsExec traces)
- **Évaluer l'exfiltration** (logs proxy, DNS, NDR — volume sortant anormal)
- **Identifier le groupe** (extension des fichiers chiffrés, note de rançon, leak site)

### Récupération

| Priorité | Action |
|---|---|
| 1 | Vérifier l'intégrité des sauvegardes (sont-elles chiffrées aussi ?) |
| 2 | Reconstruire l'AD si compromis (KRBTGT reset double, nouveaux DC) |
| 3 | Restaurer depuis des sauvegardes offline/immutables |
| 4 | Réinstaller les machines compromises (ne pas simplement déchiffrer) |
| 5 | Changer tous les mots de passe (y compris comptes de service) |
| 6 | Durcir les accès avant de remettre en production |

### Payer ou ne pas payer ?

Arguments contre :
- Aucune garantie de déchiffrement
- Finance les opérations criminelles
- Signal que l'organisation est une cible rentable
- Potentiellement illégal (sanctions OFAC si le groupe est sanctionné)

Arguments pour (dans certains cas) :
- Données critiques sans sauvegarde (hôpital, infrastructure critique)
- Coût de la reconstruction > rançon
- Délai de reconstruction inacceptable

La décision est toujours un choix de gestion de crise, pas un choix technique.

## Prévention

### Contrôles prioritaires

| Contrôle | Impact | Effort |
|---|---|---|
| **Sauvegardes offline / immutables** | Critique | Moyen |
| **MFA sur tous les accès distants** (VPN, RDP, email) | Critique | Faible |
| **Patch management** (VPN, Exchange, Citrix en priorité) | Critique | Moyen |
| **Segmentation réseau** (isoler l'AD, les backups) | Élevé | Élevé |
| **EDR sur tous les endpoints** | Élevé | Moyen |
| **Désactiver SMBv1, restreindre RDP** | Élevé | Faible |
| **AppLocker / WDAC** (bloquer les exécutables non autorisés) | Élevé | Élevé |
| **Honeypot files / canary tokens** sur les partages | Moyen | Faible |
| **Exercices de phishing** réguliers | Moyen | Faible |
| **Plan de réponse à incident testé** (tabletop exercise) | Critique | Moyen |

### Stratégie de sauvegarde 3-2-1

- **3** copies des données
- **2** types de supports différents (disque local + cloud / bande)
- **1** copie hors site et **offline** (air-gapped ou immutable)

Tester la restauration régulièrement — une sauvegarde non testée n'est pas une sauvegarde.

## Ressources

- **ID Ransomware** (`id-ransomware.malwarehunterteam.com`) — identifier la famille à partir de la note de rançon ou d'un fichier chiffré
- **No More Ransom** (`nomoreransom.org`) — déchiffreurs gratuits pour les anciennes familles
- **Ransomwatch** (`ransomwatch.telemetry.ltd`) — suivi des leak sites actifs
- **MITRE ATT&CK** — T1486 (Data Encrypted for Impact), T1490 (Inhibit System Recovery)
- **CISA StopRansomware** (`stopransomware.gov`) — guides de prévention et réponse
