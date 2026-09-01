---
title: "Syntaxe"
domain: "Social Sciences"
subdomain: "Linguistics > Branches"
tags: [sciences-sociales, linguistique]
date: "2026-02-22"
---
# Syntaxe

La **syntaxe** est la branche de la linguistique qui étudie comment les mots se combinent pour former des phrases grammaticalement correctes. Elle répond à la question : quelles règles régissent l'ordre et la structure des mots dans une langue ?

Par exemple, "Le chat mange la souris" est grammatical en français (ordre SVO), mais "Chat le souris mange la" ne l'est pas — même si chaque mot est reconnaissable individuellement.


## Structure de la Phrase

**Constituants:**
- Groupes de mots fonctionnant comme unités
- Tests: déplacement, substitution, coordination

**Syntagmes (phrases):**
- **SN (Syntagme Nominal):** Le chat noir
- **SV (Syntagme Verbal):** mange la souris
- **SP (Syntagme Prépositionnel):** dans le jardin
- **SA (Syntagme Adjectival):** très content
- **SAdv (Syntagme Adverbial):** très rapidement

**Arbre syntaxique:**
```
        P (Phrase)
       / \
      SN  SV
     /  \  / \
   Det  N V  SN
    |   |  |  /\
   Le chat mange Det N
              |   |
             la souris
```

**Tête et dépendants:**
- **Tête:** Élément central (N dans SN, V dans SV)
- **Spécifieur:** Avant la tête (Det)
- **Complément:** Après la tête (objet)
- Théorie X-barre (Chomsky)

### Fonctions Grammaticales

**Sujet:**
- Agent de l'action (souvent)
- Accord avec verbe
- Position généralement fixe

**Objet:**
- **Direct (COD):** "Marie mange une pomme"
- **Indirect (COI):** "Marie parle à Jean"
- **Oblique:** Avec préposition obligatoire

**Attribut:**
- Du sujet: "Marie est contente"
- De l'objet: "Je trouve Marie contente"

**Complément circonstanciel:**
- Temps, lieu, manière, cause, but
- Généralement facultatif, mobile

### Ordre des Mots (Typologie)

**Six ordres possibles:**
- **SVO:** Sujet-Verbe-Objet (français, anglais, mandarin, espagnol)
  - ~42% des langues
- **SOV:** Sujet-Objet-Verbe (japonais, coréen, turc, hindi, latin dans certains cas)
  - ~45% des langues
- **VSO:** Verbe-Sujet-Objet (gallois, arabe classique, tagalog)
  - ~9%
- **VOS, OVS, OSV:** Rares

**Corrélations typologiques (Greenberg):**
- SVO/VSO → Prépositions (avant le nom)
- SOV → Postpositions (après le nom)
- SVO → Auxiliaire avant verbe
- SOV → Auxiliaire après verbe

### Grammaire Générative

**Transformations (ancien modèle):**
- Structure profonde → Transformations → Structure de surface
- Passivation: "Le chat mange la souris" → "La souris est mangée par le chat"
- Interrogation: "Tu viens" → "Viens-tu?"
- Relativisation, négation, etc.

**Principes et Paramètres (années 1980):**
- Principes universels (UG)
- Paramètres variant entre langues
  - **Pro-drop:** Peut-on omettre le pronom sujet?
    - Espagnol: "Hablo" (Je parle) - pro-drop
    - Français: *"Parle" - non pro-drop
  - **Head directionality:** Tête avant/après complément

**Programme Minimaliste (1990s-):**
- Économie, minimalisation
- Merge (fusion), Move (déplacement)
- Interface syntaxe-sémantique

### Grammaires de Dépendance

**Alternative à grammaires de constituants:**
- Relations directes entre mots (pas d'arbres abstraits)
- Tête → Dépendants
- Utilisé en TAL (analyse syntaxique automatique)

