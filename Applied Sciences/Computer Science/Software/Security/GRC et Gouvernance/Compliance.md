---
title: "Compliance et Réglementations en Sécurité"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-25"
---

# Compliance et Réglementations en Sécurité

La conformité réglementaire encadre les pratiques de sécurité informatique via des normes et lois contraignantes. Les principaux référentiels sont ISO 27001, GDPR, PCI DSS et SOC 2.

## ISO 27001:2022

### Présentation

ISO/IEC 27001 est la norme internationale pour les Systèmes de Management de la Sécurité de l'Information (SMSI). Elle spécifie les exigences pour établir, implémenter, maintenir et améliorer un SMSI. La version 2022 remplace la version 2013 et réorganise les contrôles d'Annex A.

### Structure de la norme

**Corps principal (clauses 4 à 10) :**

| Clause | Titre | Contenu |
|--------|-------|---------|
| 4 | Contexte | Parties prenantes, périmètre, SMSI |
| 5 | Leadership | Engagement direction, politique SSI |
| 6 | Planification | Risques, objectifs, traitement |
| 7 | Support | Ressources, compétences, communication |
| 8 | Opération | Implémentation des contrôles |
| 9 | Évaluation | Audits internes, revue de direction |
| 10 | Amélioration | Non-conformités, amélioration continue |

**Annex A (93 contrôles en 4 thèmes) :**

| Thème | Nombre | Exemples |
|-------|--------|---------|
| Organisationnel | 37 | Politique SSI, gestion des risques, relations fournisseurs |
| Personnes | 8 | Sensibilisation, télétravail, accords de confidentialité |
| Physique | 14 | Contrôle d'accès physique, protection équipements, clear desk |
| Technologique | 34 | Contrôle d'accès logique, chiffrement, journalisation |

### Cycle PDCA

```
Plan  → Définir périmètre, politique, évaluation des risques, SOA
Do    → Implémenter contrôles, formation, procédures opérationnelles
Check → Audits internes, métriques, revue de direction
Act   → Actions correctives, amélioration continue
```

### Processus de certification

1. **Gap analysis** — Évaluation de l'écart entre l'existant et les exigences
2. **Traitement des risques** — Identifier, évaluer, traiter (accepter/réduire/transférer/éviter)
3. **Statement of Applicability (SOA)** — Documenter l'applicabilité de chacun des 93 contrôles
4. **Implémentation** — Déploiement des contrôles retenus
5. **Audit interne** — Vérification indépendante de la conformité
6. **Revue de direction** — Validation par le top management
7. **Audit de certification (Stage 1)** — Revue documentaire par l'organisme certificateur
8. **Audit de certification (Stage 2)** — Audit sur site, tests des contrôles
9. **Certification** — Délivrance du certificat (validité 3 ans avec audits de surveillance annuels)

### Documents obligatoires

- Politique de sécurité de l'information
- Procédure d'évaluation et de traitement des risques
- SOA (Statement of Applicability)
- Objectifs de sécurité
- Preuves de compétences (formations)
- Résultats de surveillance
- Programme d'audit interne
- Résultats des revues de direction
- Non-conformités et actions correctives

## RGPD (GDPR)

### Champ d'application

Le Règlement Général sur la Protection des Données (UE 2016/679) s'applique à tout traitement de données personnelles concernant des résidents de l'UE, quel que soit le lieu d'établissement du responsable de traitement.

**Données personnelles** : toute information permettant d'identifier directement ou indirectement une personne physique (nom, IP, cookie, données biométriques, etc.).

**Données sensibles (Article 9)** : origine raciale/ethnique, opinions politiques, convictions religieuses, données syndicales, données génétiques, biométriques, de santé, sexualité. Traitement interdit sauf exceptions listées.

### Bases légales du traitement (Article 6)

| Base légale | Description | Exemple |
|-------------|-------------|---------|
| Consentement | Libre, éclairé, spécifique, univoque | Newsletter marketing |
| Contrat | Nécessaire à l'exécution | Livraison d'une commande |
| Obligation légale | Imposée par la loi | Déclaration fiscale |
| Intérêts vitaux | Protéger une vie | Urgence médicale |
| Mission d'intérêt public | Service public | Recensement |
| Intérêts légitimes | Balance intérêts | Sécurité réseau interne |

### Droits des personnes concernées

| Droit | Article | Description | Délai réponse |
|-------|---------|-------------|---------------|
| Information | 13-14 | Transparence sur les traitements | Au moment de la collecte |
| Accès | 15 | Obtenir une copie des données | 1 mois (extensible à 3) |
| Rectification | 16 | Corriger des données inexactes | 1 mois |
| Effacement (droit à l'oubli) | 17 | Supprimer les données | 1 mois |
| Limitation | 18 | Geler le traitement | 1 mois |
| Portabilité | 20 | Recevoir ses données en format structuré | 1 mois |
| Opposition | 21 | S'opposer au traitement | Immédiat |
| Décision automatisée | 22 | Refuser le profilage automatisé | 1 mois |

### Obligations techniques et organisationnelles

**Privacy by Design (Article 25)** : intégrer la protection des données dès la conception du système, pas en post-traitement.

**Privacy by Default** : paramètres les plus protecteurs par défaut (ex: pas de pré-cochage des cases de consentement).

**Mesures de sécurité (Article 32)** :

```
- Pseudonymisation et chiffrement des données
- Confidentialité, intégrité, disponibilité et résilience
- Restauration rapide en cas d'incident
- Tests réguliers d'efficacité des mesures
```

**Accountability** : documenter et prouver la conformité (registre des traitements, PIA, politiques).

### Acteurs clés

| Rôle | Définition | Responsabilité |
|------|------------|----------------|
| Responsable de traitement | Détermine les finalités et moyens | Responsabilité principale |
| Sous-traitant | Traite pour le compte du RT | Responsabilité déléguée |
| DPO (Délégué à la Protection des Données) | Conseil et contrôle interne | Obligatoire dans certains cas |
| Autorité de contrôle (CNIL en France) | Régulateur national | Sanctions jusqu'à 4% CA mondial |

**DPO obligatoire si :**
- Organisme public (hors juridictions)
- Traitements à grande échelle de données sensibles
- Surveillance systématique à grande échelle

### Notification de violation (Article 33-34)

```
Découverte violation
        ↓
    72 heures
        ↓
Notification à l'autorité de contrôle (CNIL)
        ↓
Risque élevé pour les personnes ?
  ↓ Oui              ↓ Non
Notifier les       Documenter
personnes          en interne
concernées
```

Contenu de la notification :
- Nature de la violation
- Catégories et nombre de personnes concernées
- Conséquences probables
- Mesures prises ou envisagées

### DPIA (Data Protection Impact Assessment) — Article 35

Obligatoire pour les traitements à risque élevé :
- Profilage à grande échelle
- Traitement de données sensibles à grande échelle
- Surveillance systématique d'une zone accessible au public
- Nouvelles technologies (IA, biométrie)

Structure d'une DPIA :
1. Description du traitement et des finalités
2. Évaluation de la nécessité et proportionnalité
3. Évaluation des risques pour les personnes
4. Mesures de traitement des risques

### Sanctions

| Niveau | Montant maximum | Exemples d'infractions |
|--------|----------------|----------------------|
| Niveau 1 | 10 M€ ou 2% CA mondial | DPO non nommé, sous-traitant non conforme |
| Niveau 2 | 20 M€ ou 4% CA mondial | Violation des bases légales, droits des personnes |

Exemples : Meta (1,2 Md€, 2023), Amazon (746 M€, 2021), WhatsApp (225 M€, 2021).

## PCI DSS v4.0

### Présentation

Payment Card Industry Data Security Standard. Norme applicable à toute entité qui stocke, traite ou transmet des données de titulaires de cartes de paiement (CHD — Cardholder Data).

**Données protégées :**

| Type | Description | Stockage autorisé |
|------|-------------|-------------------|
| PAN | Primary Account Number (numéro de carte) | Oui (masqué/chiffré) |
| Nom du titulaire | Nom sur la carte | Oui |
| Code de service | 3 chiffres sur bande magnétique | Oui |
| Date d'expiration | MM/AA | Oui |
| Données piste complète | Bande magnétique, puce | Non |
| CAV2/CVC2/CVV2/CID | Code de sécurité 3-4 chiffres | Non |
| PIN/PIN block | Code secret | Non |

### Les 12 exigences

**Objectif 1 : Construire et maintenir un réseau sécurisé**
1. Installer et maintenir des contrôles de sécurité réseau (firewall)
2. Appliquer des configurations sécurisées (changer les mots de passe par défaut)

**Objectif 2 : Protéger les données des titulaires de cartes**
3. Protéger les données stockées (chiffrement, tokenisation, troncature)
4. Protéger les données en transit (TLS 1.2+ minimum, TLS 1.3 recommandé)

**Objectif 3 : Maintenir un programme de gestion des vulnérabilités**
5. Protéger tous les systèmes contre les malwares (antivirus, EDR)
6. Développer et maintenir des systèmes sécurisés (patching, SSDLC)

**Objectif 4 : Implémenter des mesures de contrôle d'accès robustes**
7. Restreindre l'accès aux données sur la base du besoin (least privilege)
8. Identifier les utilisateurs et authentifier l'accès (MFA obligatoire pour accès admin)
9. Restreindre l'accès physique aux données

**Objectif 5 : Surveiller et tester régulièrement les réseaux**
10. Journaliser et surveiller tous les accès aux composants réseau et données
11. Tester régulièrement la sécurité (scans ASV trimestriels, pentests annuels)

**Objectif 6 : Maintenir une politique de sécurité de l'information**
12. Soutenir la sécurité de l'information avec des politiques et programmes

### Niveaux de conformité et SAQ

| Niveau | Critère | Validation |
|--------|---------|-----------|
| Niveau 1 | > 6 millions transactions/an | QSA on-site audit + ASV scan |
| Niveau 2 | 1-6 millions transactions/an | SAQ + ASV scan |
| Niveau 3 | 20K-1M transactions e-commerce | SAQ + ASV scan |
| Niveau 4 | < 20K transactions e-commerce | SAQ recommandé |

**Types de SAQ (Self-Assessment Questionnaire) :**

| SAQ | Applicable à |
|-----|-------------|
| SAQ A | Redirection totale vers page de paiement tierce, aucune donnée CHD |
| SAQ A-EP | Site e-commerce avec scripts tiers, pas de stockage CHD |
| SAQ B | Terminaux de paiement standalone, pas de stockage électronique |
| SAQ C | Applications de paiement connectées à Internet |
| SAQ D | Toutes les autres situations |
| SAQ P2PE | Terminaux certifiés P2PE |

### Changements PCI DSS v4.0 (mars 2024)

- Approche personnalisée (Customized Approach) : démontrer la conformité autrement que par les contrôles définis
- MFA obligatoire pour tout accès à l'environnement de données cartes (plus seulement admin)
- Exigences renforcées sur les scripts de pages de paiement e-commerce (protection Magecart)
- Gestion des clés cryptographiques et inventaire des certificats obligatoires
- Évaluations de sécurité des applications web obligatoires

### Périmètre (Scope)

Le périmètre PCI DSS inclut tout composant qui :
- Stocke, traite ou transmet des CHD
- Est connecté à ou peut impacter la sécurité de tels composants

**Réduction du périmètre :**
- Tokenisation : remplacer le PAN par un token non sensible
- Segmentation réseau : isoler l'environnement de données cartes (CDE) via VLANs, firewalls
- P2PE (Point-to-Point Encryption) : chiffrement dès le terminal physique

## SOC 2

### Présentation

SOC 2 (System and Organization Controls 2) est un standard d'audit développé par l'AICPA (American Institute of CPAs). Il s'applique aux prestataires de services qui stockent, traitent ou transmettent des données clients dans le cloud.

Non contraignant légalement (contrairement au RGPD ou PCI DSS), mais souvent exigé contractuellement par les clients B2B américains.

### Les 5 Trust Service Criteria (TSC)

| Critère | Obligatoire | Description |
|---------|------------|-------------|
| Security | Oui | Protection contre l'accès non autorisé (physique et logique) |
| Availability | Non | Système disponible selon les engagements contractuels |
| Processing Integrity | Non | Traitement complet, valide, précis, en temps voulu |
| Confidentiality | Non | Protection des informations désignées comme confidentielles |
| Privacy | Non | Collecte, utilisation, rétention, divulgation des données personnelles |

### Type I vs Type II

| | SOC 2 Type I | SOC 2 Type II |
|--|-------------|---------------|
| Objet | Conception des contrôles | Efficacité opérationnelle |
| Période | À un instant T | Sur une période (6-12 mois minimum) |
| Valeur | Faible (état à un moment) | Élevée (preuve de fonctionnement continu) |
| Délai | 3-6 mois | 9-18 mois |

### Processus d'audit

1. **Readiness Assessment** — Évaluation de la maturité actuelle
2. **Remédiation** — Correction des lacunes identifiées
3. **Sélection des TSC** — Choisir les critères pertinents pour l'activité
4. **Sélection de l'auditeur CPA** — Firme d'audit accréditée AICPA
5. **Période d'observation** (Type II) — 6-12 mois de collecte de preuves
6. **Audit** — Tests des contrôles par l'auditeur
7. **Rapport** — Opinion de l'auditeur (avec ou sans réserves)

### Différences SOC 1 / SOC 2 / SOC 3

| | SOC 1 | SOC 2 | SOC 3 |
|--|-------|-------|-------|
| Focus | Contrôles financiers | Contrôles opérationnels | Résumé public SOC 2 |
| Audience | Auditeurs financiers des clients | Direction, prospects, clients | Public général |
| Distribution | Restreinte | Restreinte (NDA) | Publique |

## Comparaison des référentiels

| Critère | ISO 27001 | RGPD | PCI DSS | SOC 2 |
|---------|-----------|------|---------|-------|
| Origine | ISO/IEC | Union Européenne | PCI SSC (Visa/Mastercard) | AICPA |
| Obligatoire | Non (contractuel) | Oui (légal UE) | Oui (contractuel acquéreur) | Non (contractuel) |
| Périmètre | SMSI global | Données personnelles | Données cartes de paiement | Services cloud/SaaS |
| Reconnaissance | Internationale | UE et mondiale | Secteur paiement | Marché US/B2B |
| Durée certification | 3 ans | Continue | Annuelle | 12 mois (Type II) |
| Sanctions | Perte certification | Jusqu'à 4% CA mondial | Amendes, révocation acceptation | Perte contrats |

## Synergies et chevauchements

**ISO 27001 + SOC 2** : forte complémentarité. ISO 27001 couvre l'ISMS global, SOC 2 démontre l'efficacité des contrôles aux clients. Beaucoup de contrôles se recoupent (access control, logging, incident response).

**ISO 27001 + RGPD** : ISO 27001 Annexe A inclut des contrôles sur la vie privée (5.34 Privacy and PII protection). La conformité ISO 27001 n'implique pas la conformité RGPD mais facilite grandement celle-ci.

**PCI DSS + RGPD** : un incident sur données de cartes peut simultanément déclencher une obligation PCI DSS (notification acquéreur) et RGPD (notification CNIL sous 72h si données personnelles affectées).

**Approche intégrée** :

```
SMSI ISO 27001
    ├── Contrôles organisationnels
    ├── Contrôles techniques
    │       ├── Satisfait PCI DSS req. 2, 6, 7, 8, 10
    │       └── Satisfait RGPD Art. 32 (mesures techniques)
    └── Contrôles de monitoring
            └── Satisfait SOC 2 Security TSC
```

## Outils et ressources

| Outil | Usage |
|-------|-------|
| OneTrust / TrustArc | Gestion RGPD, registre des traitements, DPIA |
| Vanta / Drata / Thoropass | Automatisation conformité SOC 2, ISO 27001 |
| SecurityScorecard | Évaluation continue du niveau de sécurité |
| CNIL (cnil.fr) | Ressources RGPD françaises, modèles registre |
| PCI SSC (pcisecuritystandards.org) | Normes PCI DSS, SAQ, outils officiels |
| ISO Store (iso.org) | Textes officiels ISO (payants) |
| ANSSI | Guides et recommandations pour ISO 27001 en France |
