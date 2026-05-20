---
title: "Threat Intelligence (Renseignement sur les Menaces)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis"
tags: [sciences-appliquées, informatique, sécurité, soc]
date: "2026-02-25"
---

# Threat Intelligence (Renseignement sur les Menaces)

La Threat Intelligence (TI) est la collecte, l'analyse et la contextualisation d'informations sur les menaces cybernétiques pour permettre des décisions défensives éclairées. Ce n'est pas une simple liste d'IOCs — c'est de la connaissance exploitable sur les adversaires.

## Niveaux de Threat Intelligence

| Niveau | Audience | Horizon | Contenu |
|---|---|---|---|
| **Stratégique** | RSSI, direction | Mois/années | Tendances, acteurs étatiques, impact business |
| **Opérationnel** | Managers sécurité | Semaines | Campagnes actives, TTPs d'adversaires ciblant le secteur |
| **Tactique** | Analystes SOC | Jours | TTPs (MITRE ATT&CK), techniques spécifiques |
| **Technique** | Outils automatisés | Heures | IOCs : IPs, domaines, hashes, URLs malveillantes |

## IOCs (Indicators of Compromise)

Les IOCs sont des artefacts observables indiquant une compromission probable.

### Types d'IOCs

| Type | Exemples | Volatilité |
|---|---|---|
| Hash de fichier | MD5, SHA1, SHA256 d'un malware | Faible (trivial à changer) |
| Adresse IP | IP d'un C2 | Moyenne |
| Domaine | `malware-c2.xyz` | Moyenne |
| URL | `https://evil.com/payload.bin` | Haute |
| User-agent | Chaîne UA de Cobalt Strike | Haute |
| Mutex | Nom créé par un malware au démarrage | Haute |
| Clé de registre | Persistence via `Run` key spécifique | Haute |
| Pattern réseau | Signature Snort/Yara | Variable |

### Pyramide de la douleur (Pyramid of Pain)

Concept de David Bianco : plus un IOC est difficile à modifier pour l'attaquant, plus son blocage lui est douloureux.

```
TTPs          ←← Très difficile à changer (comportements fondamentaux)
Outils        ←← Difficile
Artefacts réseau / hôte
Noms de domaine
Adresses IP
Hashes de fichiers ←← Trivial à changer
```

Bloquer un hash est inutile (l'attaquant recompile). Détecter les TTPs (techniques de l'adversaire) est beaucoup plus efficace.

## MITRE ATT&CK

ATT&CK (Adversarial Tactics, Techniques & Common Knowledge) est une base de connaissances des comportements d'attaquants observés dans des environnements réels.

Structure :
- **Tactiques** (14) : l'objectif de l'attaquant (Initial Access, Execution, Persistence...)
- **Techniques** (~200) : comment atteindre l'objectif
- **Sous-techniques** (~400) : variations spécifiques
- **Procédures** : exemples d'utilisation par des groupes réels

### Tactiques Enterprise (ordre chronologique d'une intrusion)

| ID | Tactique | Exemples de techniques |
|---|---|---|
| TA0043 | Reconnaissance | Scanning actif (T1595), OSINT (T1593) |
| TA0042 | Resource Development | Compromettre une infrastructure (T1584) |
| TA0001 | Initial Access | Spearphishing (T1566), Exploit public (T1190) |
| TA0002 | Execution | PowerShell (T1059.001), WMI (T1047) |
| TA0003 | Persistence | RunKeys (T1547.001), Scheduled Task (T1053) |
| TA0004 | Privilege Escalation | Token Impersonation (T1134), Sudo (T1548) |
| TA0005 | Defense Evasion | Obfuscation (T1027), Masquerading (T1036) |
| TA0006 | Credential Access | Mimikatz/LSASS (T1003), Brute Force (T1110) |
| TA0007 | Discovery | Network Scan (T1046), Account Discovery (T1087) |
| TA0008 | Lateral Movement | Pass-the-Hash (T1550.002), RDP (T1021.001) |
| TA0009 | Collection | Keylogging (T1056), Screen Capture (T1113) |
| TA0011 | Command & Control | DNS Tunneling (T1071.004), HTTPS C2 (T1071.001) |
| TA0010 | Exfiltration | Exfil via C2 (T1041), Cloud Storage (T1567) |
| TA0040 | Impact | Ransomware (T1486), Wiper (T1485) |

### Utilisation d'ATT&CK en défense

```
1. Cartographier sa couverture de détection
   → Pour chaque technique, quelle règle/outil détecte ?
   → Visualiser avec ATT&CK Navigator (https://mitre-attack.github.io/attack-navigator/)

2. Prioritiser les lacunes
   → Quelles techniques sont utilisées par les groupes ciblant votre secteur ?
   → Mapper les TTPs des groupes APT à votre surface d'attaque

3. Valider les contrôles
   → Atomic Red Team : tests unitaires de détection par technique ATT&CK
   → Caldera : simulation d'adversaires automatisée
```

## Sources de Threat Intelligence

### Open Source (OSINT-TI)

| Source | Type | URL |
|---|---|---|
| VirusTotal | Hashes, IPs, domaines, sandbox | virustotal.com |
| Shodan | IPs, services exposés, infra C2 | shodan.io |
| AlienVault OTX | Pulses, IOCs communautaires | otx.alienvault.com |
| MalwareBazaar | Samples malware | bazaar.abuse.ch |
| URLhaus | URLs malveillantes | urlhaus.abuse.ch |
| Threatfox | IOCs (domaines, IPs, hashes) | threatfox.abuse.ch |
| MISP | Plateforme de partage d'IOCs | misp-project.org |
| OpenCTI | Plateforme CTI graphe de connaissances | opencti.io |
| Feodo Tracker | IPs de botnets (Emotet, TrickBot) | feodotracker.abuse.ch |
| AbuseIPDB | Réputation IPs | abuseipdb.com |

### Commerciales

- **Recorded Future** — intelligence en temps réel sur le dark web
- **CrowdStrike Falcon Intel** — profils d'acteurs APT
- **Mandiant Advantage** — rapports d'incidents et profils de groupes
- **ESET Threat Intelligence** — malware research

## Acteurs de menace (Threat Actors)

### Classification

| Type | Motivations | Sophistication |
|---|---|---|
| APT (Advanced Persistent Threat) | Espionnage étatique | Très haute |
| Cybercriminels | Gain financier (ransomware, fraude) | Variable |
| Hacktivistes | Idéologie, impact symbolique | Faible à moyenne |
| Insider threats | Gain, vengeance, idéologie | Variable |
| Script kiddies | Curiosité, notoriété | Faible |

### Groupes notables (nomenclature Mandiant / MITRE)

| Groupe | Origine supposée | Spécialité |
|---|---|---|
| APT28 (Fancy Bear) | Russie (GRU) | Spearphishing, élections |
| APT29 (Cozy Bear) | Russie (SVR) | Supply chain (SolarWinds) |
| Lazarus Group | Corée du Nord | Vol de cryptomonnaies, SWIFT |
| APT41 | Chine | Espionnage + cybercriminalité |
| FIN7 | Russie (criminel) | Retail, hôtellerie, PoS |
| REvil / LockBit | Russie (criminel) | Ransomware-as-a-Service |

## Formats et partage de TI

### STIX 2.1 (Structured Threat Information Expression)

Format JSON standardisé pour représenter des objets TI :

```json
{
  "type": "indicator",
  "spec_version": "2.1",
  "id": "indicator--8e2e2d2b-17d4-4cbf-938f-98129880a42c",
  "name": "Malicious URL",
  "pattern": "[url:value = 'https://evil.com/payload']",
  "pattern_type": "stix",
  "valid_from": "2024-01-15T00:00:00Z",
  "labels": ["malicious-activity"],
  "kill_chain_phases": [{
    "kill_chain_name": "mitre-attack",
    "phase_name": "command-and-control"
  }]
}
```

### TAXII (Trusted Automated eXchange of Intelligence Information)

Protocole HTTP pour échanger des collections STIX entre plateformes TI.

### MISP (Malware Information Sharing Platform)

Plateforme open source de partage d'IOCs. Les événements MISP contiennent des attributs (IOCs), des tags (taxonomies TLP), et des corrélations automatiques.

**TLP (Traffic Light Protocol)** — niveau de diffusion :

| Couleur | Diffusion |
|---|---|
| TLP:RED | Uniquement les destinataires directs |
| TLP:AMBER+STRICT | Organisation + besoin explicite |
| TLP:AMBER | Organisation et partenaires directs |
| TLP:GREEN | Communauté de sécurité |
| TLP:CLEAR | Public |

## Cycle de vie du renseignement

```
1. Direction  → définir les besoins (Key Intelligence Requirements)
2. Collecte   → sources OSINT, HUMINT, SIGINT, dark web
3. Traitement → normalisation, déduplication, enrichissement
4. Analyse    → contextualisation, attribution, prédiction
5. Diffusion  → rapport, feed SIEM, IOCs dans les outils
6. Feedback   → évaluation de la pertinence, ajustement
```
