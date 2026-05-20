---
title: "Report Writing (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, reporting, pnpt]
date: "2026-05-18"
---

# Report Writing

Le rapport, c'est le livrable réel d'un pentest. Le client ne voit ni ton shell ni ton terminal — il voit un PDF. Un test brillant mal rapporté vaut moins qu'un test moyen bien rapporté. À l'examen PNPT, le rapport représente une grande partie de l'évaluation : si le rapport est mauvais, on peut techniquement réussir l'exploit et rater l'examen.

## L'audience à deux niveaux

Un rapport de pentest a deux lectorats distincts qui ne lisent pas les mêmes sections.

```
   Lecteur                    Section                  Ce qu'il cherche
   ─────────────────          ───────────────────      ───────────────────────
   Direction, DSI       ───►  Executive Summary   ───► "On est exposés ou pas ?"
   (non technique)                                     "Combien ça coûte ?"
                                                       "Priorités ?"

   Équipe sécu, sysadmin ──►  Findings techniques ───► "Comment exploiter ?"
   (technique)                                         "Comment corriger ?"
                                                       "Reproduire ?"
```

**Conséquence pratique** : l'Executive Summary ne doit JAMAIS contenir de jargon technique. Si le DG voit "CVE-2024-1234" ou "NTLM relay", il ferme le PDF. Les findings techniques, eux, peuvent et doivent être précis.

## Structure type d'un rapport

### 1. Page de garde

```
   Nom du client + logo
   Type de pentest (externe / interne / web / AD)
   Dates du test
   Auteur(s) du rapport
   Classification : CONFIDENTIEL — Diffusion restreinte
   Version + date du document
```

### 2. Resume exécutif (Executive Summary)

Une à deux pages. Ce que le DG va lire, et probablement la seule partie qu'il va lire en entier.

À inclure :
- Objectifs du test (rappel)
- Posture globale (verdict en une phrase)
- 3 à 5 risques principaux, formulés en impact métier
- Recommandations prioritaires
- Schéma synthétique (souvent : score global, comparaison avant/après si test précédent)

**Ce qu'il ne faut pas faire** : commencer par "Nous avons exploité une vulnérabilité Kerberoasting...". Le DG ne sait pas ce qu'est Kerberos.

**Formulation correcte** : "Nous avons démontré qu'un attaquant interne pouvait compromettre l'ensemble du domaine Windows en moins de deux heures, en exploitant des mots de passe faibles sur des comptes de service."

### 3. Méthodologie

- Cadre suivi (PTES, OWASP, OSSTMM, etc.)
- Périmètre exact (IPs, domaines, applications)
- Limitations connues (hors-périmètre, contraintes horaires, etc.)
- Outils utilisés

Ce chapitre montre la rigueur. Court mais précis.

### 4. Trouvailles (Findings)

Le cœur du rapport. Une fiche par vulnérabilité significative.

| Élément       | Description                                              |
|---------------|----------------------------------------------------------|
| **Titre**     | Nom clair, court (ex. "Kerberoasting sur compte SQL")    |
| **Sévérité**  | Critique / Haute / Moyenne / Basse / Info                |
| **CVSS**      | Score numérique (v3.1) si applicable                     |
| **Description** | La vulnérabilité, en termes techniques                  |
| **Impact**    | Conséquence concrète (en termes métier !)                |
| **Systèmes**  | IPs/services affectés                                    |
| **Preuve**    | Screenshots + commandes + outputs                        |
| **Remédiation** | Étapes concrètes pour corriger                         |
| **Références** | CVE, MITRE ATT&CK, articles                            |

### 5. Annexes

- Liste complète des cibles testées (IPs, URLs)
- Outputs bruts de scans
- Liste exhaustive des outils + versions
- Chaîne d'attaque détaillée (de l'OSINT au Domain Admin)

## Échelle de sévérité

| Sévérité | Critères                                                | Exemples                                          |
|----------|---------------------------------------------------------|---------------------------------------------------|
| Critique | RCE sans auth, compromission du domaine, données massives | EternalBlue exposé, DA via Kerberoast, SQLi auth bypass |
| Haute    | RCE auth, privesc, credentials sensibles                | SQLi standard, default creds admin, ACL abuse AD  |
| Moyenne  | XSS stocké, info disclosure sensible, MFA absent        | XSS persistent, énumération de users, no rate limit |
| Basse    | XSS reflété, headers sécurité absents, info versions    | X-Frame-Options manquant, version Apache exposée  |
| Info     | Bonnes pratiques non suivies, hardening léger           | TLS 1.0 supporté, suite de chiffrement faible     |

**Le CVSS n'est pas suffisant** : un CVSS de 9.8 sur une CVE non exploitable dans le contexte = sévérité ajustée à la baisse. Toujours expliquer pourquoi tu rates différemment du score brut.

## Une fiche de finding bien rédigée

```
   Titre : Kerberoasting permettant la compromission du domaine

   Sévérité : Critique         CVSS v3.1 : 9.1 (AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)

   Description :
     Le compte de service "svc_sql" utilise un mot de passe court ("Sql2020")
     et possède un Service Principal Name (SPN). Tout utilisateur du domaine
     peut donc demander un TGS pour ce compte, et extraire un hash crackable
     hors ligne (Kerberoasting). Le hash a été cracké en 4 minutes avec une
     wordlist standard.

   Impact :
     L'attaquant obtient les credentials du compte svc_sql, membre du groupe
     "Server Operators". Cela permet une élévation jusqu'à Domain Admin via
     une chaîne d'ACL identifiée par BloodHound (voir annexe A).

   Systèmes affectés :
     DC01 (10.10.10.5) — Active Directory cible.local

   Preuve :
     [Screenshot 1] GetUserSPNs.py extrayant le hash
     [Screenshot 2] hashcat crackant le mot de passe
     [Screenshot 3] Connexion psexec.py en tant que svc_sql

   Remédiation :
     1. Renforcer le mot de passe (16+ caractères, généré aléatoirement) ou
        utiliser un Managed Service Account (MSA / gMSA).
     2. Auditer tous les comptes avec SPN (Get-ADUser -Filter
        {ServicePrincipalName -like "*"}).
     3. Implémenter une politique de mots de passe spécifique aux comptes
        de service via Fine-Grained Password Policies.

   Références :
     - MITRE ATT&CK : T1558.003 Kerberoasting
     - https://attack.mitre.org/techniques/T1558/003/
```

## Conseils spécifiques à l'examen PNPT

- **Le rapport pèse lourd** dans la note finale. Beaucoup de candidats échouent à cause du rapport, pas de la technique.
- **Screenshots dès la première commande**. Mieux vaut en avoir trop que pas assez. Sans preuve, un finding n'existe pas.
- **Documenter en temps réel** dans Obsidian ou CherryTree pendant le test — pas le soir, pas après. La mémoire ne suffit pas pour 5 jours d'engagement.
- **Chaîne d'attaque illustrée** : montrer le parcours OSINT → foothold → privesc → mouvement latéral → Domain Admin. Diagramme appréciable.
- **Remédiations actionnables** : ne pas se contenter de "mettre à jour le système". Donner les étapes concrètes, et si possible, le coût/effort estimé.
- **Relire** : fautes d'orthographe et incohérences décrédibilisent. Faire relire par quelqu'un d'autre si possible.
- **Format PDF, présentation soignée** : police lisible, screenshots non écrasés, mise en page cohérente.

## Outils

```
   Rédaction :
     - Markdown (Obsidian, Typora) puis export PDF
     - Word / LibreOffice avec template
     - Pwndoc (générateur dédié pentest, en self-hosted)
     - SysReptor (équivalent open-source moderne)

   Screenshots :
     - Flameshot (Linux, recommandé — annotations rapides)
     - Greenshot (Windows)
     - ShareX (Windows, plus avancé)

   Notes pendant le test :
     - Obsidian (note par cible, lien entre findings)
     - CherryTree (arborescence + screenshots intégrés)
     - GhostWriter (collaboration équipe pentest)
```

## Pièges courants

- **Executive Summary trop technique** : si la première phrase contient un acronyme, le DG ferme.
- **Findings sans screenshot** : "j'ai fait X" sans preuve = pas crédible.
- **Sévérité incohérente** : marquer en "Critique" une vuln sans démontrer d'impact = perte de crédibilité sur tout le rapport.
- **Remédiation vague** : "appliquer les bonnes pratiques" n'est pas une remédiation. Toujours donner les étapes.
- **Mélanger les langues** : si le rapport est en français, garder le français partout (sauf termes techniques sans équivalent comme "Pass-the-Hash").
- **Oublier l'annexe Chaîne d'attaque** : c'est la section que les pentesters apprécient le plus dans les rapports qu'ils lisent. Souvent omise par flemme.
- **Rapport rendu sans relecture** : 24 heures de pause avant de relire change tout. À l'examen PNPT, le délai post-test est court mais existe — l'utiliser.
