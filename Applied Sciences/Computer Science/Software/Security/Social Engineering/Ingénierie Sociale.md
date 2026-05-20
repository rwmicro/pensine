---
title: "Ingénierie Sociale"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2026-02-25"
---

# Ingénierie Sociale

L'ingénierie sociale est la manipulation psychologique de personnes pour les amener à divulguer des informations confidentielles ou à effectuer des actions compromettantes. C'est le vecteur d'entrée numéro un des compromissions : les attaquants ciblent l'humain plutôt que les systèmes, car l'humain est souvent le maillon le plus faible.

## Principes psychologiques exploités

Robert Cialdini (Influence, 1984) identifie les leviers de persuasion utilisés en ingénierie sociale :

| Principe | Description | Exemple d'exploitation |
|---|---|---|
| **Autorité** | Obéir à quelqu'un qui semble légitime | Se faire passer pour le DSI ou la police |
| **Urgence** | Pression temporelle qui court-circuite la réflexion | "Votre compte sera suspendu dans 24h" |
| **Peur** | Menace qui pousse à agir sans réfléchir | "Votre ordinateur est infecté" |
| **Réciprocité** | Rendre service pour en obtenir un | Envoyer un cadeau avant de demander un accès |
| **Preuve sociale** | Faire référence à ce que font les autres | "Tous vos collègues ont déjà mis à jour leur accès" |
| **Sympathie** | Cible plus coopérative envers quelqu'un qu'elle apprécie | Usurper l'identité d'un ami ou collègue |
| **Engagement** | Obtenir un petit oui pour en obtenir un grand | Foot-in-the-door technique |

## Phishing

Le phishing est l'envoi massif d'emails frauduleux imitant des entités légitimes.

### Anatomie d'un email de phishing

```
From: security-noreply@arnazon.com              ← domaine typosquat
To: alice@company.com
Subject: [URGENT] Votre compte Amazon sera suspendu dans 24h

Corps :
- Logos et mise en page imitant Amazon
- Message alarmiste créant l'urgence
- Lien hypertexte masqué :
  [Vérifier mon compte](https://arnazon-secure.com/verify?token=xxx)
                                                 ← redirect vers page de phishing
Pied de page :
- Coordonnées légitimes copiées depuis le vrai site
- Lien de désinscription (souvent non fonctionnel)
```

### Techniques de contournement des filtres

```
Homoglyphes : аmazon.com (а cyrillique ≠ a latin)
Typosquatting : amazon.corn, arnazon.com, amazoon.com
Sous-domaine : amazon.com.malveillant.fr
IDN Homograph : аррӏе.com (caractères Unicode similaires)
URL shortener : bit.ly/3xKz91a → masque la destination
Redirect légitime : google.com/url?q=https://evil.com
HTML encoding : &#x61;&#x6D;&#x61;&#x7A;&#x6F;&#x6E;.com
```

### Indicateurs de phishing

- Expéditeur ne correspond pas au domaine de l'organisation affichée
- URL de destination ≠ domaine légitime (vérifier avant de cliquer)
- Fautes d'orthographe, traduction maladroite
- Demande urgente d'action (mot de passe, paiement, clics)
- Pièce jointe inattendue (`.docm`, `.xlsm`, `.lnk`, `.iso`, `.zip`)
- Lien vers une page de connexion sans HTTPS valide
- Requête inhabituelle hors des processus normaux

## Spear Phishing

Attaque ciblée et personnalisée contre un individu spécifique, après recherche OSINT approfondie.

```
Reconaissance :
- LinkedIn → titre, responsabilités, projets en cours, manager
- Site corporate → organigramme, actualités, partenaires
- Réseaux sociaux → centres d'intérêt, déplacements, relations
- GitHub → projets, technologies utilisées

Email ciblé :
From: jean.martin@fournisseur-partenaire.com   ← domaine similaire au vrai fournisseur
Subject: Devis révisé — Projet Lyon Q1 2025

"Bonjour Alice, suite à notre réunion du 12 janvier avec votre équipe,
je vous envoie la version révisée du devis pour le projet Lyon.
Merci de le valider avant vendredi pour respecter le planning.

→ Devis_Lyon_v3.pdf.exe   (double extension)
→ Ou lien OneDrive malveillant"
```

## Whaling

Spear phishing ciblant les dirigeants (C-level) à fort pouvoir de décision.

```
Cible : PDG, CFO, directeurs
Exemples :
- Usurpation du PDG vers le CFO : "Virement urgent confidentiel"
  (Business Email Compromise — BEC)
- Faux huissier, faux avocat demandant un paiement discret
- Invitation à une conférence avec formulaire d'inscription malveillant
```

## Business Email Compromise (BEC)

Fraude ciblant les entreprises via compromission ou usurpation d'emails professionnels.

Types de BEC :
- **CEO Fraud** : email du "PDG" au DAF demandant un virement urgent
- **Invoice Fraud** : faux fournisseur modifie les coordonnées bancaires
- **Payroll Diversion** : "RH" demande de changer les informations de virement salaire
- **Lawyer Impersonation** : faux avocat demandant confidentialité et urgence

```
BEC - CEO Fraud typique :

From: pdg@company-corp.com  (vrai domaine compromis, ou domaine similaire)
To: daf@company.com
Subject: Opération confidentielle — Action requise aujourd'hui

"Bonjour Pierre, je suis en réunion externe. J'ai besoin que tu effectues
un virement de 85 000€ vers ce nouveau partenaire avant 17h.
C'est confidentiel pour l'instant. Je t'expliquerai demain.
IBAN : FR76 xxxx xxxx xxxx"

Statistiques : pertes mondiales BEC > 50 milliards $ (FBI IC3)
```

## Vishing (Voice Phishing)

Manipulation par téléphone.

```
Scénarios courants :
- Support technique (Microsoft, Apple) : "Votre ordinateur envoie des virus"
  → Faire installer AnyDesk/TeamViewer → accès complet
- Fausse banque : "Activité suspecte sur votre compte"
  → Demande du numéro de carte, code OTP
- Faux collègue IT : "Je dois réinitialiser votre compte"
  → Demande du mot de passe temporaire ou des credentials
- Faux fournisseur : mise à jour des coordonnées bancaires par téléphone
```

Techniques de vishing :
- **Caller ID spoofing** : afficher un numéro légitime (banque, employeur)
- **Accent coaching** : accent natif pour crédibilité
- **Background noise** : sons de call center pour paraître authentique

## Smishing (SMS Phishing)

```
Exemples :
"CHRONOPOST : Votre colis est bloqué. Payez 2,99€ de frais : bit.ly/xxx"
"[La Banque Postale] Connexion inhabituelle. Confirmez : labanquepostale-secure.com"
"[CPF] 4500€ de droits à la formation expirent vendredi. Accédez à : moncompteformation-gouv.fr.xxx"
```

Les SMS ont un taux d'ouverture de ~98% vs ~20% pour les emails.

## Pretexting

Fabrication d'un scénario crédible (prétexte) pour obtenir des informations.

```
Scénario 1 — Audit interne :
"Bonjour, je suis de la direction des systèmes d'information à Paris.
Nous effectuons un audit de conformité. J'aurais besoin de vos identifiants
pour vérifier votre accès dans notre système."

Scénario 2 — Nouveau employé :
"Bonjour, je viens de rejoindre l'équipe RH. Mon accès n'est pas encore
configuré, pourriez-vous me prêter votre badge pour aller en salle serveur ?"

Scénario 3 — Fournisseur :
"Je suis technicien Orange, j'ai un ticket pour vérifier la fibre
dans vos locaux. Pouvez-vous me laisser accès à la baie réseau ?"
```

## Baiting et Quid Pro Quo

**Baiting** : laisser une clé USB infectée dans un parking, couloir, ou salle de réunion. La curiosité de la victime la pousse à la brancher.

```
Étiquettes efficaces sur la clé USB :
"Salaires 2025 — Confidentiel"
"Vidéos fête de Noël"
"Résultats évaluation performance Q3"
```

**Quid Pro Quo** : proposer un service en échange d'informations (ex : support informatique gratuit contre des credentials).

## Indicateurs de compromission (côté victime)

- Email d'un expéditeur connu mais ton inhabituel
- Demande sortant des processus normaux (virement sans bon de commande)
- Pression temporelle anormale
- Demande de confidentialité excessive
- Coordonnées bancaires modifiées "à la dernière minute"
- Lien ou pièce jointe inattendu

## Contre-mesures organisationnelles

### Formation et sensibilisation

```
Simulations de phishing :
- Campagnes régulières (GoPhish, KnowBe4, Proofpoint)
- Taux de clic mesuré et suivi dans le temps
- Formation immédiate pour les cliqueurs

Procédures de vérification :
- Tout virement > X€ nécessite une validation téléphonique sur un numéro connu
- Changement de coordonnées bancaires → vérification via canal distinct
- Principe : "si vous avez un doute, raccrochez et rappelez sur le numéro officiel"
```

### Contrôles techniques

| Contrôle | Objectif |
|---|---|
| SPF, DKIM, DMARC | Authentifier les emails légitimes, rejeter les usurpations |
| Filtres anti-phishing | Microsoft Defender, Proofpoint, Mimecast |
| MFA sur tous les comptes | Limiter l'impact d'un vol de credentials |
| Navigation sécurisée | DNS filtering (Cisco Umbrella), proxy web |
| Désactiver les macros Office | Empêcher l'exécution de code via les pièces jointes |
| DMARC en mode reject | Empêcher l'usurpation du domaine de l'entreprise |

### Vérification des emails (DMARC/SPF/DKIM)

```bash
# Vérifier les enregistrements DNS anti-phishing d'un domaine
dig TXT company.com | grep spf          # SPF
dig TXT _dmarc.company.com             # DMARC
dig TXT selector._domainkey.company.com # DKIM

# SPF sécurisé
v=spf1 include:_spf.google.com ip4:1.2.3.4 -all   # -all = reject

# DMARC en mode reject
v=DMARC1; p=reject; rua=mailto:dmarc@company.com; pct=100
```
