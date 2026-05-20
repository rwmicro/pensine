---
title: "EBIOS Risk Manager (EBIOS RM)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Risk Analysis"
tags: [sciences-appliquées, informatique, sécurité]
date: "2025-12-31"
---

# EBIOS Risk Manager (EBIOS RM)

**EBIOS RM** (*Expression des Besoins et Identification des Objectifs de Sécurité — Risk Manager*) est la méthode française de référence pour l'analyse et le traitement du risque en cybersécurité. Elle est développée et maintenue par l'**ANSSI** (Agence Nationale de la Sécurité des Systèmes d'Information), publiée en 2018.

Elle remplace l'ancienne EBIOS 2010 et s'aligne sur les normes internationales **ISO 27001/27005**.


## Philosophie

EBIOS RM part des **scénarios de menaces réalistes** plutôt que d'une liste exhaustive de vulnérabilités. Elle place les **attaquants** (sources de risque) au centre de l'analyse.

L'objectif : identifier ce que des adversaires concrets pourraient faire contre un système précis, et décider comment s'en protéger.


## Les 5 ateliers

La méthode est structurée en **5 ateliers** progressifs :

### Atelier 1 — Cadrage et socle de sécurité
- Définir le périmètre de l'étude (l'objet analysé)
- Identifier les **biens essentiels** (données, processus critiques)
- Appliquer un **socle de sécurité** de base (bonnes pratiques, normes)
- Identifier les écarts par rapport à ce socle

### Atelier 2 — Sources de risque
- Identifier les **sources de risque** (SR) : qui pourrait attaquer ?
  - État, cybercriminels, concurrent, initié malveillant, hacktiviste...
- Définir leurs **objectifs visés** (OV) : pourquoi attaqueraient-ils ?
- Prioriser les couples SR/OV les plus pertinents

### Atelier 3 — Scénarios stratégiques
- Pour chaque SR/OV prioritaire, construire des **chemins d'attaque** à haut niveau
- Identifier les **parties prenantes** (fournisseurs, partenaires) comme vecteurs d'attaque
- Évaluer la vraisemblance de chaque scénario stratégique
- Déduire les **mesures sur l'écosystème** à prendre

### Atelier 4 — Scénarios opérationnels
- Décomposer les scénarios stratégiques en **scénarios techniques détaillés**
- Utiliser des arbres d'attaque (MITRE ATT&CK, kill chain...)
- Évaluer la vraisemblance à chaque étape
- Identifier les **mesures techniques** à mettre en place

### Atelier 5 — Traitement du risque
- Croiser **vraisemblance × gravité** pour évaluer chaque risque résiduel
- Décider du traitement :
  - **Réduire** (mesures de sécurité)
  - **Accepter** (le risque est tolérable)
  - **Transférer** (assurance, sous-traitance)
  - **Refuser** (ne pas faire l'activité)
- Produire un **plan de traitement** et un **résumé dirigeant**


## Schéma global

```
Atelier 1 : Cadrage
     ↓
Atelier 2 : Qui peut attaquer ? Pourquoi ?
     ↓
Atelier 3 : Comment (vision macro) ?
     ↓
Atelier 4 : Comment (vision technique) ?
     ↓
Atelier 5 : Que décide-t-on de faire ?
```


## Utilisation

EBIOS RM est recommandée (voire obligatoire) pour :
- Les **Opérateurs d'Importance Vitale (OIV)** — secteurs critiques en France
- Les **Opérateurs de Services Essentiels (OSE)** — directive NIS
- Les homologations **SecNumCloud**
- Tout projet soumis aux exigences de l'ANSSI


## Livrables typiques

- Cartographie des biens essentiels
- Liste des sources de risque priorisées
- Scénarios de risque documentés
- Plan de traitement des risques
- Tableau de bord sécurité pour la direction

## Exemple pratique — Application e-commerce

### Atelier 1 : Cadrage

```
Périmètre : Application web de vente en ligne "MaBottique.fr"
Biens essentiels :
  BE1 — Données clients (coordonnées, historique d'achat)
  BE2 — Données de paiement (numéros de carte, tokens PSP)
  BE3 — Catalogue et stocks (propriété intellectuelle)
  BE4 — Disponibilité du service (CA en temps réel)

Socle de sécurité appliqué :
  ✓ HTTPS partout (TLS 1.2+)
  ✓ Authentification admin avec MFA
  ✗ Pas de WAF (écart identifié)
  ✗ Logs insuffisants (écart identifié)
  ✗ Dépendances npm non auditées (écart identifié)
```

### Atelier 2 : Sources de risque

```
Sources de risque identifiées :

SR1 — Cybercriminel organisé
  Objectif visé OV1 : Voler les données de paiement (revente Dark Web)
  Priorité : HAUTE (cible classique, fort ROI pour l'attaquant)

SR2 — Concurrent malveillant
  Objectif visé OV2 : Perturber le service (DDoS avant les soldes)
  Priorité : MOYENNE

SR3 — Développeur prestataire mécontent
  Objectif visé OV3 : Saboter ou exfiltrer le catalogue
  Priorité : MOYENNE (accès légitime, motivé par rancune)

SR4 — Script kiddie
  Objectif visé OV4 : Défacement ou SQLi opportuniste
  Priorité : FAIBLE (peu ciblé, défenses basiques suffisent)

Couples SR/OV retenus pour la suite : SR1/OV1 et SR3/OV3
```

### Atelier 3 : Scénarios stratégiques

```
Scénario stratégique SS1 (SR1 — Cybercriminel / OV1 — Données paiement)

Chemin d'attaque :
  [Internet] → Exploitation SQL Injection sur le formulaire de recherche
             → Accès à la base de données clients + tokens PSP
  OU
  [Internet] → Compromission du prestataire de maintenance (accès VPN)
             → Accès direct au serveur de production

Parties prenantes exposées :
  - Prestataire hébergement (accès infra)
  - PSP (processeur de paiement) — interface API
  - Prestataire maintenance développement — accès source code + BDD de recette

Mesures sur l'écosystème :
  → Exiger le MFA chez le prestataire maintenance
  → Audit du contrat et des accès du PSP
  → Segmentation réseau : les prestataires n'accèdent qu'aux ressources nécessaires

Vraisemblance : 4/4 (cybercriminel bien équipé, SQLi commune, pas de WAF)
Gravité : 4/4 (données paiement = sanction CNIL + PCI DSS + perte de confiance)
```

### Atelier 4 : Scénarios opérationnels

```
Scénario opérationnel SO1.1 (décomposition de SS1 — voie SQLi)

Étape 1 : Reconnaissance
  Technique : T1595 Active Scanning, T1596 Search Open Datasets (Shodan)
  Vraisemblance : 4/4 (trivial)
  Mesure : Pas de headers révélateurs (Server:, X-Powered-By:)

Étape 2 : SQLi sur formulaire de recherche
  Technique : T1190 Exploit Public-Facing Application
  Vraisemblance : 3/4 (paramètre non filtré identifié dans le code)
  Mesure : Requêtes préparées (parameterized queries) + WAF

Étape 3 : Extraction de la base de données
  Technique : T1005 Data from Local System (via sqlmap OUT_FILE)
  Vraisemblance : 3/4 (utilisateur DB avec trop de droits)
  Mesure : Principe du moindre privilège sur l'utilisateur BDD

Étape 4 : Exfiltration
  Technique : T1048 Exfiltration Over Alternative Protocol (DNS)
  Vraisemblance : 2/4 (nécessite un outil custom)
  Mesure : Filtrage DNS sortant, DLP
```

### Atelier 5 : Traitement du risque

```
Risque résiduel R1 (SS1) :
  Vraisemblance × Gravité = 3 × 4 = Risque CRITIQUE avant traitement

Plan de traitement :
  Action 1 : Déployer un WAF (ModSecurity / Cloudflare WAF)
    Responsable : Équipe infra | Délai : 1 mois | Impact : -1 vraisemblance
    Coût estimé : 2 000€/an

  Action 2 : Audit de code (toutes les requêtes BDD) + migration ORM
    Responsable : Lead dev | Délai : 2 mois | Impact : -1 vraisemblance
    Coût estimé : 5 jours/homme

  Action 3 : Segmenter l'accès BDD (user applicatif = SELECT/INSERT seulement)
    Responsable : DBA | Délai : 1 semaine | Impact : réduit la gravité
    Coût estimé : Faible (configuration)

  Action 4 : Tokenisation des données de paiement (déléguer au PSP)
    Responsable : Architecte | Délai : 3 mois | Impact : -2 gravité
    Coût estimé : Voir contrat PSP

Risque résiduel après traitement : 2 × 2 = Risque MODÉRÉ → ACCEPTÉ

Décision : Réduire (actions 1-4) + Transférer (assurance cyber)
```

## Intégration avec MITRE ATT&CK

EBIOS RM s'interface naturellement avec MITRE ATT&CK pour les ateliers 3 et 4 :

```
Atelier 3 (Scénarios stratégiques) ↔ Tactiques ATT&CK
  Initial Access, Execution, Persistence, Lateral Movement...

Atelier 4 (Scénarios opérationnels) ↔ Techniques ATT&CK
  T1190 Exploit Public-Facing Application
  T1078 Valid Accounts
  T1059 Command and Scripting Interpreter
  ...

Bénéfice :
→ Vocabulaire commun avec les équipes SOC
→ Mapping direct vers les règles de détection SIGMA
→ Évaluation de la couverture défensive sur chaque technique
```

## Outils et ressources

```
Outils officiels :
→ EBIOS RM Tool (ANSSI) : logiciel officiel gratuit pour conduire la méthode
→ Club EBIOS : communauté de praticiens, retours d'expérience
→ Guide ANSSI "La méthode EBIOS Risk Manager" (2018, mis à jour régulièrement)

Normes complémentaires :
→ ISO 27005 : gestion des risques de la sécurité de l'information
→ ISO 31000 : management du risque (générique)
→ NIST SP 800-30 : guide d'évaluation des risques (US)
```
