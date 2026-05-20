---
title: "Logique"
domain: "Social Sciences"
subdomain: "Philosophy"
tags: [sciences-sociales, philosophie]
date: "2026-02-27"
---

# Logique

La logique est l'étude des formes valides de raisonnement. Elle répond à la question : dans quelles conditions une conclusion suit-elle nécessairement de prémisses données ? C'est une discipline à la fois philosophique et mathématique, fondamentale pour les sciences, l'informatique et la pensée critique.

## Branches de la logique

```
  LOGIQUE
    │
    ├── Formelle (symbolique)    Étudie la forme des arguments,
    │                            indépendamment de leur contenu
    │   ├── Logique des propositions  (connecteurs : ∧, ∨, →, ¬)
    │   ├── Logique des prédicats     (quantificateurs : ∀, ∃)
    │   └── Logique modale            (nécessité, possibilité : □, ◇)
    │
    ├── Informelle               Étudie les arguments en langage naturel
    │                            Sophismes, rhétorique, pensée critique
    │
    └── Non-classique            Logique intuitionniste, floue,
                                 paraconsistante...
```

## Propositions et valeurs de vérité

Une **proposition** est un énoncé qui peut être vrai ou faux (pas les deux, pas ni l'un ni l'autre — en logique classique).

```
  Propositions valides :
    "Il pleut."              → vrai ou faux
    "2 + 2 = 4"              → vrai
    "Tous les chats volent." → faux

  Non-propositions :
    "Ferme la porte !"       → ordre
    "Quelle heure est-il ?" → question
    "Vive la liberté !"     → exclamation
```

## Connecteurs logiques

Les connecteurs permettent de construire des propositions complexes à partir de propositions simples.

| Connecteur | Symbole | Nom | Description |
|---|---|---|---|
| NON | ¬p | Négation | Inverse la valeur de vérité |
| ET | p ∧ q | Conjonction | Vrai si les deux sont vrais |
| OU | p ∨ q | Disjonction | Vrai si au moins un est vrai |
| SI...ALORS | p → q | Implication | Faux seulement si p vrai et q faux |
| SI ET SEULEMENT SI | p ↔ q | Équivalence | Vrai si même valeur de vérité |

**Table de vérité complète**

| p | q | ¬p | p ∧ q | p ∨ q | p → q | p ↔ q |
|---|---|----|-------|-------|-------|-------|
| V | V | F | V | V | V | V |
| V | F | F | F | V | F | F |
| F | V | V | F | V | V | F |
| F | F | V | F | F | V | V |

**Le cas délicat : l'implication (p → q)**
L'implication est fausse *uniquement* quand la prémisse est vraie et la conclusion fausse. Si la prémisse est fausse, l'implication est vraie par convention — "ex falso quodlibet" (du faux, tout suit).

```
  "Si je suis roi de France, alors la lune est en fromage."
  Prémisse fausse → implication vraie (triviale, pas informative)

  C'est pourquoi on distingue :
    Implication matérielle (logique)  : p → q
    Implication causale (langage)     : "parce que", "donc"
```

## Syllogismes (Aristote)

Le syllogisme est la forme d'argument déductif fondamentale, formalisée par Aristote dans l'*Organon*.

```
  Structure :

  Majeure   : Tous les M sont P     (règle générale)
  Mineure   : Tout S est M          (cas particulier)
  ────────────────────────────────
  Conclusion: Tout S est P          (résultat)

  Exemple classique :

  Majeure   : Tous les hommes sont mortels.
  Mineure   : Socrate est un homme.
  ────────────────────────────────────────
  Conclusion: Socrate est mortel.
```

**Les 4 types de propositions catégoriques**

| Type | Forme | Exemple |
|---|---|---|
| A (universelle affirmative) | Tous les S sont P | "Tous les chiens sont des mammifères" |
| E (universelle négative) | Aucun S n'est P | "Aucun poisson n'est un mammifère" |
| I (particulière affirmative) | Certains S sont P | "Certains animaux sont des chiens" |
| O (particulière négative) | Certains S ne sont pas P | "Certains animaux ne sont pas des chiens" |

**Erreurs syllogistiques fréquentes**

```
  Terme moyen non distribué :
    "Tous les chats sont des animaux.
     Tous les chiens sont des animaux.
     Donc tous les chats sont des chiens." ← FAUX (M non distribué)

  Affirmation du conséquent :
    "Si P alors Q. Q. Donc P." ← INVALIDE
    Ex : "Si je suis en Australie, je suis dans l'hémisphère Sud.
         Je suis dans l'hémisphère Sud. Donc je suis en Australie."
         → Faux : je pourrais être en Argentine.

  Négation de l'antécédent :
    "Si P alors Q. ¬P. Donc ¬Q." ← INVALIDE
    Ex : "Si je travaille, je réussis.
         Je ne travaille pas. Donc je ne réussis pas."
         → Faux : je pourrais réussir autrement.
```

## Formes d'arguments valides

Ces formes sont valides : si les prémisses sont vraies, la conclusion l'est nécessairement.

```
  Modus Ponens (MP)          Modus Tollens (MT)
  ─────────────────          ──────────────────
  Si P alors Q               Si P alors Q
  P                          ¬Q (Q est faux)
  ────────────               ────────────
  Q                          ¬P (P est faux)

  Ex : "Si il pleut, la rue est mouillée.     Ex : "Si il pleut, la rue est mouillée.
        Il pleut.                                   La rue n'est pas mouillée.
        Donc la rue est mouillée." ✓               Donc il ne pleut pas." ✓


  Syllogisme hypothétique     Disjonction exclusive
  ──────────────────────      ─────────────────────
  Si P alors Q                P ou Q (exclusif)
  Si Q alors R                P
  ────────────                ─────────────────
  Si P alors R                Donc ¬Q

  Ex : "Si A alors B.         (fonctionne si le "ou" est exclusif)
        Si B alors C.
        Donc si A alors C." ✓
```

## Validité et solidité (soundness)

Distinction fondamentale que le langage courant confond souvent.

```
  ARGUMENT VALIDE  : si les prémisses sont vraies,
                     la conclusion DOIT être vraie
                     (la forme logique est correcte)

  ARGUMENT SOLIDE  : valide ET toutes les prémisses sont vraies
  (sound)

  ┌─────────────────────────────────────────────────────┐
  │             Tous les arguments possibles            │
  │                                                     │
  │   ┌─────────────────────────────────────────┐       │
  │   │           Arguments valides             │       │
  │   │                                         │       │
  │   │   ┌─────────────────────────────────┐   │       │
  │   │   │       Arguments SOLIDES         │   │       │
  │   │   │ (valides + prémisses vraies)    │   │       │
  │   │   └─────────────────────────────────┘   │       │
  │   └─────────────────────────────────────────┘       │
  └─────────────────────────────────────────────────────┘

  Exemple valide mais non solide :
    "Tous les chats sont des robots.   ← prémisse fausse
     Mon chat est un chat.
     Donc mon chat est un robot."
     Forme valide ✓, mais non solide ✗

  Exemple ni valide ni solide :
    "J'ai gagné à la loterie.
     Donc les licornes existent."
     Aucun lien logique entre les deux.
```

## Raisonnement déductif, inductif et abductif

Trois modes de raisonnement fondamentalement différents dans leur rapport à la certitude.

```
  DÉDUCTION              INDUCTION              ABDUCTION
  (top-down)             (bottom-up)            (inference to best explanation)

  Du général             Du particulier         De l'observation
  au particulier         au général             à la meilleure cause

  Règle :                Observations :         Observation :
  Tous les M sont P.     Ce M₁ est P.           R est observé (surprenant).
  Cas :                  Ce M₂ est P.
  Ce S est M.            Ce M₃ est P.           Hypothèse :
  ────────────           ────────────           Si H, alors R serait attendu.
  Résultat :             Règle probable :
  Ce S est P.            Tous les M sont P ?    Conclusion :
                                                H est probablement vraie.
  CERTAIN                PROBABLE               PLAUSIBLE
  (si prémisses          (pas garanti)          (pas prouvé)
   vraies et             Problème de            "Inference to the best
   forme valide)         l'induction (Hume)     explanation" (Peirce)

  Ex : "Tous les         Ex : "J'ai vu          Ex : "Le sol est mouillé.
  humains meurent.       100 cygnes blancs.     Probablement, il a plu."
  Socrate est humain.    Donc tous les          (autres exp. possibles :
  → Socrate mourra."     cygnes sont           tuyau crevé, arrosage)
                         blancs."
                         (réfuté en 1697)
```

## Logique des prédicats

La logique des prédicats (ou du premier ordre) enrichit la logique propositionnelle en permettant d'exprimer des propriétés et des relations.

**Quantificateurs**

```
  ∀x P(x)   : "Pour tout x, P(x) est vrai"   (quantificateur universel)
  ∃x P(x)   : "Il existe un x tel que P(x)"  (quantificateur existentiel)

  Exemples :
    ∀x (Homme(x) → Mortel(x))          "Tous les hommes sont mortels"
    ∃x (Chat(x) ∧ Vole(x))             "Il existe un chat qui vole"
    ¬∃x (Dragon(x) ∧ Humain(x))        "Aucun dragon n'est humain"

  Dualité des quantificateurs :
    ¬∀x P(x)  ≡  ∃x ¬P(x)   ("pas tous" = "il en existe au moins un qui n'est pas")
    ¬∃x P(x)  ≡  ∀x ¬P(x)   ("il n'en existe aucun" = "tous ne sont pas")
```

**Relations**

```
  Prédicat binaire : R(x, y) = "x est en relation R avec y"
  Ex : AimeMieux(x, y) = "x préfère y"

  ∀x ∀y (AimeMieux(x, y) → ¬AimeMieux(y, x))   → irréflexivité (si asymétrique)
  ∀x ∃y AimeMieux(x, y)                          → tout le monde préfère quelque chose
```

## Sophismes et erreurs de raisonnement

Un sophisme est un argument qui *semble* valide mais ne l'est pas. Les repérer est une compétence centrale de la pensée critique.

**Sophismes informels — tableau de référence**

| Sophisme | Description | Exemple |
|---|---|---|
| Ad hominem | Attaquer la personne, pas l'argument | "Tu ne peux pas parler de diététique, tu es en surpoids." |
| Homme de paille | Déformer l'argument adverse pour le réfuter | "Il veut réduire l'armée → il veut laisser le pays sans défense." |
| Appel à l'autorité | Citer une autorité hors de son domaine | "Ce médecin dit que les vaccins sont inutiles." |
| Appel à la popularité | Ce qui est répandu est vrai | "Des millions de gens y croient, ça ne peut pas être faux." |
| Faux dilemme | Réduire à deux options quand il en existe plus | "Tu es avec nous ou contre nous." |
| Pente glissante | Enchaîner des conséquences sans justification | "Si on autorise X, on finira forcément par autoriser Y et Z." |
| Post hoc ergo propter hoc | Confondre succession et causalité | "J'ai pris cette pilule, ma migraine est partie, donc ça a guéri." |
| Généralisation hâtive | Conclure du particulier au général sans justification | "J'ai été arnaqué par un vendeur, tous les vendeurs sont malhonnêtes." |
| Appel à l'ignorance | "Ce n'est pas prouvé faux, donc c'est vrai" | "On n'a jamais prouvé que les fantômes n'existent pas." |
| Équivoque | Utiliser un mot dans deux sens différents | "La fin justifie les moyens. La mort est la fin de la souffrance. Donc la mort justifie les moyens." |
| Cause unique | Réduire un phénomène complexe à une seule cause | "La violence vient des jeux vidéo." |
| Tu quoque | "Tu fais pareil" comme réponse à une critique | "Tu me reproches de mentir ? Et toi, tu mens aussi !" |

## Paradoxes logiques

**Le paradoxe du menteur**
```
  "Cette phrase est fausse."

  Si elle est vraie  → son contenu dit qu'elle est fausse → contradiction
  Si elle est fausse → son contenu est donc vrai         → contradiction

  → Aucune valeur de vérité classique possible
  → Motiva le développement de la logique formelle moderne
    et la distinction entre objet-langage et méta-langage (Tarski)
```

**Le paradoxe de Russell**
```
  Soit R l'ensemble de tous les ensembles qui ne se contiennent pas eux-mêmes.
  R ∈ R ?

  Si R ∈ R  → R se contient → R ne devrait pas être dans R
  Si R ∉ R  → R ne se contient pas → R devrait être dans R

  → Crise des fondements des mathématiques (fin XIXe)
  → Mène à la théorie des types (Russell) et à la théorie des ensembles axiomatique (ZFC)
```

## Logique formelle moderne

**Frege (1848–1925)** — *Begriffsschrift* (1879) : premier système de logique des prédicats, formalisation rigoureuse du raisonnement mathématique. Inventeur de la logique moderne.

**Russell et Whitehead** — *Principia Mathematica* (1910–1913) : tentative de fonder toutes les mathématiques sur la logique. Réponse au paradoxe de Russell par la théorie des types.

**Gödel (1906–1978)**

```
  Théorèmes d'incomplétude (1931) :

  1er théorème : Tout système formel cohérent suffisamment expressif
                 (contenant l'arithmétique) est INCOMPLET :
                 il contient des propositions vraies mais indémontrables.

  2e théorème  : Un tel système ne peut pas prouver sa propre cohérence.

  Construction : Gödel encode "Cette proposition est indémontrable dans ce système."
    → Si elle est fausse : le système prouve une fausseté → incohérent
    → Si elle est vraie  : le système ne peut pas la prouver → incomplet

  Conséquence philosophique : il n'existera jamais de système formel
  complet et cohérent capable de capturer toute la vérité mathématique.
```

**Turing (1912–1954)** — Le problème de la halte : on ne peut pas construire un programme général qui détermine si n'importe quel programme terminera ou tournera indéfiniment. Lien direct avec le 1er théorème de Gödel.

## Applications de la logique

**Mathématiques** — La logique est le fondement de la démonstration mathématique. Les preuves mathématiques sont des arguments déductifs formellement valides.

**Informatique** — Les circuits logiques (portes ET, OU, NON) sont des implémentations physiques des connecteurs logiques. Les langages de programmation, les bases de données (SQL), l'intelligence artificielle symbolique reposent sur la logique formelle.

**Droit** — L'interprétation des textes juridiques, le raisonnement par analogie, la construction des contrats requièrent une logique rigoureuse.

**Philosophie** — L'analyse des arguments philosophiques, la construction de théories cohérentes, l'épistémologie formelle.

**Pensée critique** — Identifier les sophismes dans les discours politiques, publicitaires et médiatiques. Évaluer la solidité des arguments scientifiques.
