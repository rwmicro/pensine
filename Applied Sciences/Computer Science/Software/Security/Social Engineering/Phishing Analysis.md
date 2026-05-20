---
title: "Phishing Analysis"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité, soc, phishing, email]
date: "2026-04-16"
---

# Phishing Analysis

L'analyse de phishing est une compétence quotidienne en SOC. Chaque email signalé comme suspect par un utilisateur doit être trié rapidement : est-ce du spam inoffensif, une tentative de credential harvesting, ou le vecteur initial d'un ransomware ? Cette note couvre le processus d'analyse de bout en bout.

## Types de phishing

| Type | Description | Cible |
|---|---|---|
| **Mass phishing** | Email générique envoyé à des milliers de destinataires (fausse facture, faux colis) | Tout le monde |
| **Spear phishing** | Email personnalisé ciblant un individu ou un service précis | Employé spécifique |
| **Whaling** | Spear phishing visant un dirigeant (CEO, CFO) | C-level |
| **BEC** (*Business Email Compromise*) | L'attaquant se fait passer pour un collègue/fournisseur pour déclencher un virement | Finance, direction |
| **Vishing** | Phishing par téléphone (voice) | Support IT, helpdesk |
| **Smishing** | Phishing par SMS | Grand public |
| **QR phishing (Quishing)** | QR code redirigeant vers un site malveillant | Employés (posters, emails) |

## Processus d'analyse

### 1. Collecter les artefacts

**En-têtes email** : indispensables. Le corps peut être trompeur, les en-têtes sont beaucoup plus difficiles à falsifier.

Artefacts à extraire :

| Artefact | Où le trouver | Pourquoi |
|---|---|---|
| **From:** (affiché) | En-tête | Nom et adresse affichés — souvent usurpés |
| **Return-Path / Envelope-From** | En-tête | Vrai expéditeur SMTP |
| **Reply-To:** | En-tête | Si différent du From:, suspect |
| **Received:** (chaîne) | En-têtes | Trace des serveurs traversés (lire du bas vers le haut) |
| **X-Originating-IP** | En-tête (pas toujours) | IP du client qui a soumis le mail |
| **Authentication-Results** | En-tête | SPF/DKIM/DMARC pass ou fail |
| **URLs dans le corps** | Corps HTML | Hyperlien affiché ≠ href réel |
| **Pièces jointes** | Corps MIME | Nom, extension, hash |
| **Message-ID** | En-tête | Identifiant unique, utile pour pivoter |

### 2. Analyser les en-têtes

```
Received: from mail-attacker.evil.com (203.0.113.66)
    by mx.company.com with ESMTPS id xyz123
    for <victime@company.com>;
    Wed, 15 Jan 2025 09:12:33 +0100

Authentication-Results: mx.company.com;
    spf=fail (sender IP is 203.0.113.66);
    dkim=none;
    dmarc=fail (p=NONE)
```

**Red flags dans les en-têtes** :
- SPF/DKIM/DMARC en `fail` ou `none`
- Serveur d'origine (`Received:`) sans rapport avec le domaine affiché
- **Reply-To** différent du **From:**
- Timestamps incohérents
- `X-Mailer` ou `User-Agent` inhabituel

Outils : **MXToolbox Header Analyzer**, **Google Admin Toolbox**, `msgconvert` (pour `.msg` → `.eml`).

### 3. Analyser les URLs

**Ne jamais cliquer directement.** Extraire les URLs du code source HTML.

```html
<!-- Affichage trompeur -->
<a href="https://evil-site.com/login">https://microsoft.com/login</a>
```

Techniques de masquage courantes :
- **Typosquatting** : `micros0ft.com`, `rnicrosoft.com` (rn → m)
- **Homoglyphes** : `miсrosoft.com` (le 'с' est un caractère cyrillique)
- **Sous-domaine trompeur** : `microsoft.com.evil.site.com`
- **URL shortener** : `bit.ly/xyz123`
- **Data URI** : `data:text/html;base64,...`
- **Redirections chaînées** : Google redirect, LinkedIn redirect

**Analyse safe** :

| Outil | Usage |
|---|---|
| **URLScan.io** | Soumet l'URL et capture une screenshot + arborescence réseau |
| **VirusTotal** | Score de détection multi-moteurs |
| **AbuseIPDB** | Réputation de l'IP d'hébergement |
| **Whois** / `whois` CLI | Date de création du domaine (domaine de < 30 jours = suspect) |
| **URL2PNG** / **Browserling** | Preview sans exécuter le JS |
| **CyberChef** | Décoder base64, défuser des URLs |

### 4. Analyser les pièces jointes

**Ne jamais ouvrir sur un poste de production.** Utiliser un environnement sandbox.

Types de pièces jointes à risque :

| Extension | Risque | Pourquoi |
|---|---|---|
| `.exe`, `.scr`, `.bat`, `.cmd`, `.ps1` | Critique | Exécutable direct |
| `.docm`, `.xlsm`, `.pptm` | Élevé | Macros VBA |
| `.doc`, `.xls` (format ancien) | Élevé | Macros activées par défaut sur anciennes versions |
| `.html`, `.htm` | Élevé | Credential harvesting local, JS obfusqué |
| `.iso`, `.img`, `.vhd` | Élevé | Contournement de Mark-of-the-Web (pas de warning Windows) |
| `.zip`, `.rar`, `.7z` protégé par mot de passe | Élevé | Le mot de passe dans le corps empêche le scan AV |
| `.lnk` | Élevé | Raccourci Windows qui peut exécuter du code |
| `.pdf` | Moyen | JS embarqué, liens masqués |

**Analyse sandbox** :

| Outil | Type |
|---|---|
| **ANY.RUN** | Sandbox interactive (gratuit pour les samples publics) |
| **Hybrid Analysis** (Falcon Sandbox) | Analyse automatique + rapport |
| **Joe Sandbox** | Analyse comportementale détaillée |
| **VirusTotal** | Hash lookup + analyse multi-moteurs |
| **oletools** (`olevba`, `oleid`) | Extraction macros VBA d'un document Office |
| **pdfid** / **pdf-parser** (Didier Stevens) | Analyse statique PDF |

```bash
# Extraire le hash sans ouvrir le fichier
sha256sum piece_jointe.docm

# Chercher le hash sur VirusTotal
vt file <hash>

# Extraire les macros VBA
olevba piece_jointe.docm

# Analyser un PDF
pdfid document.pdf
pdf-parser --search /JS document.pdf
```

### 5. Pivoter sur les IOCs

Chaque artefact trouvé (IP, domaine, hash, email) peut être pivoté pour trouver d'autres campagnes liées :

- **IP source** → AbuseIPDB, Shodan, GreyNoise, VirusTotal
- **Domaine** → Whois (registrar, date de création), PassiveTotal, RiskIQ
- **Hash de fichier** → VirusTotal, Hybrid Analysis, MalwareBazaar
- **Adresse email** → Hunter.io, haveibeenpwned, search dans le SIEM
- **Techniques MITRE** → ATT&CK Navigator pour cartographier la campagne

### 6. Qualifier et répondre

| Verdict | Action |
|---|---|
| **Faux positif** | Rassurer l'utilisateur, fermer le ticket |
| **Spam** | Bloquer l'expéditeur, pas d'escalade |
| **Phishing (credential harvesting)** | Bloquer l'URL, reset du mot de passe si cliqué, rechercher d'autres destinataires |
| **Phishing avec payload** | Isoler le poste si ouvert, analyse forensique, bloquer IOCs, escalade |
| **BEC** | Contacter la finance, vérifier si un virement a été initié, escalade direction |

## Indicateurs d'un email de phishing

### Dans le contenu
- Urgence artificielle ("votre compte sera bloqué dans 24h")
- Fautes d'orthographe ou de grammaire inhabituelles
- Demande d'information sensible (mot de passe, numéro de carte)
- Lien qui ne correspond pas au domaine affiché
- Pièce jointe inattendue
- Ton inhabituel pour l'expéditeur supposé

### Dans les métadonnées
- Domaine expéditeur de moins de 30 jours
- SPF/DKIM/DMARC fail
- Serveur d'origine dans un pays inattendu
- En-tête `X-Mailer` d'un outil d'envoi de masse (PHPMailer, SendGrid si l'entreprise ne l'utilise pas)

## Automatisation

### Règles SIEM

```
# Pseudo-règle : email avec pièce jointe Office + macro depuis un domaine externe
source=email_gateway
| where attachment_extension IN ("docm","xlsm","pptm")
| where sender_domain NOT IN (internal_domains)
| alert "Macro-enabled attachment from external sender"
```

### SOAR Playbook

Un playbook phishing typique :
1. **Trigger** : email signalé par un utilisateur (bouton "Report Phishing")
2. **Enrichissement automatique** : extraire URLs/attachments, soumettre à VirusTotal/URLScan
3. **Décision** : si score VirusTotal > 3 détections → malveillant
4. **Réponse** : bloquer le domaine dans le proxy, purger l'email de toutes les boîtes, notifier l'utilisateur
5. **Clôture** : créer un IOC dans la plateforme CTI, fermer le ticket

## Références

- **MITRE ATT&CK T1566** — Phishing (technique d'Initial Access)
- **MITRE ATT&CK T1566.001** — Spearphishing Attachment
- **MITRE ATT&CK T1566.002** — Spearphishing Link
- **MITRE ATT&CK T1534** — Internal Spearphishing
