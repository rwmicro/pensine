---
title: "Gestion des Vulnérabilités"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-25"
---

# Gestion des Vulnérabilités

La gestion des vulnérabilités est le processus continu d'identification, d'évaluation, de priorisation et de remédiation des failles de sécurité dans les systèmes d'information. C'est une fonction fondamentale de la sécurité défensive.

## Cycle de vie d'une vulnérabilité

```
Découverte → CVE assignée → Publication → Exploitation → Patch disponible → Remédiation
     ↑                                        ↑
  Chercheur                              Zero-day (avant patch)
  Bug bounty
  Scan interne
```

**Zero-day** : vulnérabilité exploitée avant qu'un patch soit disponible. Délai médian entre découverte et exploitation dans la wild : quelques jours à quelques semaines pour les vulnérabilités critiques (Log4Shell exploité < 24h après publication).

## CVE, CWE et NVD

### CVE (Common Vulnerabilities and Exposures)

Identifiant unique pour chaque vulnérabilité : `CVE-ANNÉE-NUMÉRO`

```
CVE-2021-44228 : Log4Shell (Apache Log4j — CVSS 10.0)
CVE-2022-30190 : Follina (Microsoft Support Diagnostic Tool — CVSS 7.8)
CVE-2023-23397 : Outlook Zero-Click (Microsoft Outlook — CVSS 9.8)
CVE-2024-3400 : PAN-OS Command Injection (Palo Alto — CVSS 10.0)
```

### CWE (Common Weakness Enumeration)

Classification des types de faiblesses à l'origine des vulnérabilités.

| CWE | Weakness | Exemple |
|---|---|---|
| CWE-79 | Cross-site Scripting (XSS) | Sortie non encodée dans HTML |
| CWE-89 | SQL Injection | Requête non paramétrée |
| CWE-22 | Path Traversal | `../../../etc/passwd` |
| CWE-78 | OS Command Injection | `os.system(user_input)` |
| CWE-434 | Unrestricted File Upload | Upload de `.php` exécutable |
| CWE-502 | Deserialization of Untrusted Data | `pickle.loads(user_data)` |
| CWE-287 | Improper Authentication | |
| CWE-611 | XXE Injection | |

### NVD (National Vulnerability Database)

Base de données NIST qui enrichit les CVEs avec les scores CVSS, les références, et les CPE (Common Platform Enumeration — identifiant des logiciels affectés).

## CVSS (Common Vulnerability Scoring System)

CVSS v3.1 est le standard de scoring des vulnérabilités. Il produit un score de 0 à 10.

### Métriques de base (Base Score)

**Exploitability Metrics :**

| Métrique | Valeurs | Description |
|---|---|---|
| Attack Vector (AV) | Network(N), Adjacent(A), Local(L), Physical(P) | Comment l'attaquant accède |
| Attack Complexity (AC) | Low(L), High(H) | Conditions requises |
| Privileges Required (PR) | None(N), Low(L), High(H) | Niveau d'accès préalable |
| User Interaction (UI) | None(N), Required(R) | Interaction humaine nécessaire |

**Impact Metrics :**

| Métrique | Valeurs | Description |
|---|---|---|
| Confidentiality (C) | None(N), Low(L), High(H) | Impact sur la confidentialité |
| Integrity (I) | None(N), Low(L), High(H) | Impact sur l'intégrité |
| Availability (A) | None(N), Low(L), High(H) | Impact sur la disponibilité |

**Scope (S)** : Unchanged(U) / Changed(C) — l'exploit peut-il impacter des composants hors du composant vulnérable ?

### Vecteur CVSS et scores

```
CVE-2021-44228 (Log4Shell) :
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H = 10.0 CRITICAL

Lecture :
- AV:N = exploitable via le réseau
- AC:L = complexité faible (pas de conditions spéciales)
- PR:N = pas de privilèges requis
- UI:N = pas d'interaction utilisateur
- S:C = scope changé (impact hors du composant)
- C:H/I:H/A:H = impact total sur CIA
```

| Score | Sévérité |
|---|---|
| 0.0 | None |
| 0.1 – 3.9 | Low |
| 4.0 – 6.9 | Medium |
| 7.0 – 8.9 | High |
| 9.0 – 10.0 | Critical |

### EPSS (Exploit Prediction Scoring System)

Complément au CVSS : probabilité (0-100%) qu'une vulnérabilité soit exploitée dans les 30 prochains jours dans la wild. Une CVE Critical avec EPSS de 0.1% est moins urgente qu'une CVE Medium avec EPSS de 85%.

## Processus de gestion des vulnérabilités

### 1. Inventaire des assets

Impossible de sécuriser ce qu'on ne connaît pas.

```bash
# Scan réseau pour découvrir les assets
nmap -sn 192.168.0.0/16 -oG hosts.txt         # ping sweep
nmap -sV -O 192.168.1.0/24 --open -oX scan.xml # services et OS

# Interroger un CMDB ou un outil de découverte (Nessus, Qualys, Tenable)
# Intégrer avec Active Directory pour les assets Windows
```

### 2. Scan de vulnérabilités

```bash
# OpenVAS (Greenbone) — scanner open source
gvm-start
gvm-cli socket --xml "<authenticate><credentials><username>admin</username>..."

# Nessus — scanner commercial de référence
# Interface web : https://localhost:8834

# Nuclei — scanner basé sur templates YAML
nuclei -u https://target.com -t cves/ -severity critical,high
nuclei -l urls.txt -t exposures/ -o results.txt

# Nikto — serveurs web
nikto -h https://target.com -o rapport.html -Format html
```

### 3. Priorisation

La priorisation empêche de traiter 10 000 CVEs de façon aléatoire.

```
Priorité = f(CVSS Score, EPSS, Criticité de l'asset, Exposition, Exploitabilité)

Matrice de décision :
┌─────────────────────────────────────────────────┐
│            Criticité de l'asset                 │
│        Haute          │        Faible           │
├──────────┬────────────┼──────────┬──────────────┤
│ CVSS     │ Patch      │ CVSS     │ Surveiller,  │
│ Critical │ immédiat   │ Critical │ planifier    │
├──────────┼────────────┼──────────┼──────────────┤
│ CVSS     │ Patch      │ CVSS     │ Cycle normal │
│ High     │ < 7 jours  │ High     │ de patch     │
├──────────┼────────────┼──────────┼──────────────┤
│ CVSS     │ Cycle      │ CVSS     │ Accepter     │
│ Medium   │ normal     │ Medium   │ le risque    │
└──────────┴────────────┴──────────┴──────────────┘
```

**SLA typiques selon la sévérité :**

| Sévérité | Asset critique | Asset normal |
|---|---|---|
| Critical | 24-48h | 7 jours |
| High | 7 jours | 30 jours |
| Medium | 30 jours | 90 jours |
| Low | 90 jours | Prochain cycle |

### 4. Remédiation

Options par ordre de préférence :

1. **Patch** : appliquer le correctif officiel
2. **Mise à jour** : passer à une version non vulnérable
3. **Workaround** : configuration alternative (ex: désactiver le feature vulnérable)
4. **Compensating control** : WAF, segmentation réseau, monitoring renforcé
5. **Acceptation du risque** : documentée et approuvée par la direction

### 5. Vérification

```bash
# Rescanner après patch pour vérifier la remédiation
nuclei -u https://target.com -tags cve -id CVE-2021-44228

# Vérifier la version du package
dpkg -l log4j*
apt-cache show liblog4j2-java
```

## Vulnerability Intelligence

```bash
# Suivre les nouvelles vulnérabilités
# - NVD RSS feed
# - CISA KEV (Known Exploited Vulnerabilities) : https://www.cisa.gov/known-exploited-vulnerabilities-catalog
# - Vendor security advisories
# - Full Disclosure, oss-security

# CISA KEV — liste des CVEs avec exploitation active confirmée
curl https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | \
    jq '.vulnerabilities[] | select(.vendorProject=="Apache") | .cveID, .vulnerabilityName'
```

## Bug Bounty et Disclosure Responsable

### Responsible Disclosure (Coordinated Vulnerability Disclosure)

```
1. Chercheur découvre une vulnérabilité
2. Signalement privé au vendor (security@vendor.com, HackerOne, Bugcrowd)
3. Acknowledgement dans 5 jours ouvrés
4. Période de remédiation : 90 jours (standard Google Project Zero)
5. Publication coordonnée après patch (ou après 90 jours si pas de réponse)
```

### Bug Bounty

| Plateforme | Programmes | Récompenses |
|---|---|---|
| HackerOne | 3000+ programmes | $100 – $1M+ |
| Bugcrowd | 1000+ programmes | $50 – $500k |
| Intigriti | 600+ programmes | €50 – €100k |
| YesWeHack | 400+ programmes (Europe) | €50 – €50k |

Fourchettes de récompenses typiques :

| Sévérité | Récompense typique |
|---|---|
| Critical (RCE, auth bypass) | $5k – $50k+ |
| High (SQLi, IDOR sur données sensibles) | $1k – $10k |
| Medium (XSS persistant, CSRF) | $200 – $2k |
| Low | $50 – $500 |

## Outils de gestion des vulnérabilités

| Outil | Type | Usage |
|---|---|---|
| **Tenable Nessus / io** | Commercial | Scan entreprise, reporting |
| **Qualys VMDR** | Cloud | Scan continu, patch management |
| **Greenbone / OpenVAS** | Open source | Scanner autonome |
| **Nuclei** | Open source | Templates CVE, très rapide |
| **Trivy** | Open source | Conteneurs, filesystem, IaC |
| **OWASP DefectDojo** | Open source | Agrégation et suivi des vulnérabilités |
| **Faraday** | Open source | Collaboration équipe pentest |
