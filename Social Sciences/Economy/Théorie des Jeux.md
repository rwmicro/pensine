---
title: "Théorie des Jeux"
domain: "Social Sciences"
subdomain: "Economy"
tags: [sciences-sociales, économie]
date: "2026-02-27"
---

# Théorie des Jeux

La théorie des jeux est la branche des mathématiques et de l'économie qui étudie les situations de décision stratégique : des situations où le résultat obtenu par un agent dépend non seulement de ses propres choix, mais aussi des choix effectués par d'autres agents.

Formalisée par John von Neumann et Oskar Morgenstern dans *Theory of Games and Economic Behavior* (1944), puis développée par John Nash dans les années 1950, elle est devenue un outil central de l'économie, de la biologie évolutive, de la science politique et de la philosophie.

## Concepts fondamentaux

**Les éléments d'un jeu**

| Élément | Définition | Exemple (dilemme du prisonnier) |
|---|---|---|
| Joueurs | Agents qui prennent des décisions | Les deux suspects |
| Stratégies | Actions disponibles pour chaque joueur | Coopérer ou Trahir |
| Gains (payoffs) | Résultats selon les stratégies jouées | Années de prison |
| Information | Ce que chaque joueur sait | Interrogés séparément |
| Règles | Structure et ordre des décisions | Choix simultané |

**Anatomie d'un jeu**

```
          ┌─────────────┐
          │   Joueur A  │  ← a ses propres stratégies
          └──────┬──────┘
                 │ choisit une stratégie
                 ▼
          ┌─────────────────────────────┐
          │     Résultat du jeu         │  ← dépend des DEUX choix
          └─────────────────────────────┘
                 ▲
                 │ choisit une stratégie
          ┌──────┴──────┐
          │   Joueur B  │  ← a ses propres stratégies
          └─────────────┘
```

**Stratégie dominante**
Une stratégie est *dominante* si elle est la meilleure réponse possible, quel que soit le comportement des autres joueurs. Lorsque chaque joueur a une stratégie dominante, le résultat est prévisible sans coordination.

**Stratégie dominée**
Une stratégie est *dominée* s'il en existe toujours une meilleure, quelle que soit la décision adverse. Un joueur rationnel ne jouera jamais une stratégie strictement dominée.

## Taxonomie des jeux

```
Les jeux se classifient selon quatre axes indépendants :

  Intérêts   ──┬── Somme nulle       gain A = −gain B        ex : échecs, poker
               └── Somme non nulle   coopération possible    ex : commerce, DP

  Temporalité ─┬── Simultané         matrice de gains        ex : DP, Chicken
               └── Séquentiel        arbre de décision       ex : ultimatum

  Information ─┬── Complète / Incomplète   (les gains sont-ils connus de tous ?)
               └── Parfaite / Imparfaite   (les actions passées sont-elles visibles ?)

  Coordination ┬── Coopératif         coalitions contraignantes possibles
               └── Non coopératif     décisions indépendantes
```

**Jeux à somme nulle**
Le gain d'un joueur est exactement la perte de l'autre. Les intérêts sont parfaitement opposés.
- Exemples : échecs, poker, négociations de partage fixe
- Résolution : théorème minimax (von Neumann) — chaque joueur minimise le gain maximum de l'adversaire

**Jeux à somme non nulle**
Les joueurs peuvent simultanément gagner ou perdre. La coopération peut créer de la valeur.
- Exemples : commerce, alliances, dilemme du prisonnier
- Ces jeux sont au cœur de l'économie moderne

**Jeux simultanés (forme normale)**
Les joueurs choisissent leurs stratégies en même temps, sans voir le choix adverse. Représentés par une matrice de gains.

**Jeux séquentiels (forme extensive)**
Les joueurs agissent l'un après l'autre. Représentés par un arbre de décision. La notion d'engagement et de menace crédible y est centrale.

**Information complète vs. incomplète**
En information complète, tous les joueurs connaissent la structure du jeu (les gains de chacun). En information incomplète, certains joueurs ignorent le type ou les gains des autres — c'est le cas des enchères ou des négociations asymétriques.

**Information parfaite vs. imparfaite**
En information parfaite, chaque joueur observe l'intégralité des actions passées (échecs). En information imparfaite, certaines actions sont cachées (poker).

## L'équilibre de Nash

Un **équilibre de Nash** est un profil de stratégies tel qu'aucun joueur n'a d'intérêt à dévier unilatéralement de sa stratégie, étant donnée celle des autres.

Formellement : les stratégies (s₁*, s₂*, ..., sₙ*) forment un équilibre de Nash si pour chaque joueur i :

```
uᵢ(sᵢ*, s₋ᵢ*) ≥ uᵢ(sᵢ, s₋ᵢ*)   pour toute stratégie sᵢ alternative
```

Autrement dit : je joue ma meilleure réponse à ce que tu joues, et tu joues ta meilleure réponse à ce que je joue. Ni toi ni moi n'avons envie de changer.

**Théorème de Nash (1950)** : tout jeu fini à n joueurs possède au moins un équilibre de Nash, possiblement en stratégies mixtes.

**Stratégies mixtes**
Un joueur peut randomiser sur ses stratégies pures selon une distribution de probabilité. L'intuition est simple : si tu joues toujours la même stratégie, ton adversaire peut l'apprendre et l'exploiter. Au pierre-feuille-ciseaux, toujours jouer "pierre" garantit la défaite dès que l'adversaire le remarque. La seule protection est l'imprévisibilité — randomiser.

```
Pierre-feuille-ciseaux : pourquoi randomiser ?

  Si tu joues toujours Pierre  →  l'adversaire joue Feuille  →  tu perds
  Si tu joues toujours Feuille →  l'adversaire joue Ciseaux  →  tu perds
  Si tu joues toujours Ciseaux →  l'adversaire joue Pierre   →  tu perds

  Solution : jouer chaque option avec probabilité 1/3
  → l'adversaire est indifférent entre ses trois choix
  → il ne peut pas t'exploiter
```

La distribution d'équilibre est celle qui rend l'adversaire *indifférent* entre ses propres stratégies : si l'adversaire préférait nettement l'une d'elles, tu aurais intérêt à jouer une stratégie pure (la meilleure réponse), et il ne randomiserait plus.

**Efficacité au sens de Pareto**
Un résultat est **Pareto-optimal** s'il est impossible d'améliorer la situation d'un joueur sans détériorer celle d'un autre. Un résultat est **Pareto-dominé** s'il en existe un autre où au moins un joueur est strictement mieux loti et personne n'est moins bien loti.

```
Tension fondamentale Nash / Pareto (dilemme du prisonnier) :

   Gain de B
      │
  −1  ●  ← (Coopère, Coopère) : Pareto-optimal, instable
      │
  −5  │             ★ ← (Trahit, Trahit) : Nash, mais Pareto-dominé !
      │
      └──────────────────── Gain de A
         −5        −1

  ★ = équilibre de Nash    ● = optimum de Pareto
  Les deux ne coïncident pas → c'est le drame du dilemme du prisonnier.
```

L'équilibre de Nash n'est pas nécessairement Pareto-optimal. C'est précisément le drame du dilemme du prisonnier : l'équilibre (Trahit, Trahit) est Pareto-dominé par (Coopère, Coopère), que chacun préférerait — mais la logique individuelle rend ce dernier instable.

**Limites de l'équilibre de Nash**
- Un jeu peut avoir plusieurs équilibres (problème de sélection)
- L'équilibre peut être Pareto-inefficace — rationnel individuellement, mauvais collectivement
- Requiert une rationalité commune et des connaissances mutuelles fortes

## Lire et résoudre un jeu

### Lire une matrice de gains

Un jeu simultané à deux joueurs se représente par une **matrice de gains**. Par convention :

```
                      ← Stratégies de B →
                   Gauche          Droite
                ┌───────────────┬───────────────┐
   Stratégies   │               │               │
      de A      │    (gA, gB)   │    (gA, gB)   │
      Haut       │               │               │
                ├───────────────┼───────────────┤
                │               │               │
      Bas        │    (gA, gB)   │    (gA, gB)   │
                │               │               │
                └───────────────┴───────────────┘
         ↑
    A choisit la LIGNE          B choisit la COLONNE
    Le premier chiffre = gain de A    Le second = gain de B
```

### Trouver les équilibres de Nash : méthode des meilleures réponses

Règle : souligner le gain maximal de A pour chaque colonne, et le gain maximal de B pour chaque ligne. Toute case où les **deux** gains sont soulignés est un équilibre de Nash.

**Exemple pas à pas :**

|  | B : Gauche | B : Droite |
|---|---|---|
| **A : Haut** | (3, 1) | (0, 2) |
| **A : Bas** | (1, 0) | (2, 3) |

```
Étape 1 — Meilleures réponses de A (on fixe B, on cherche le max pour A) :

  B joue Gauche → A compare 3 (Haut) vs 1 (Bas)  → A préfère Haut  → souligner 3
  B joue Droite → A compare 0 (Haut) vs 2 (Bas)  → A préfère Bas   → souligner 2

Étape 2 — Meilleures réponses de B (on fixe A, on cherche le max pour B) :

  A joue Haut → B compare 1 (Gauche) vs 2 (Droite)  → B préfère Droite → souligner 2
  A joue Bas  → B compare 0 (Gauche) vs 3 (Droite)  → B préfère Droite → souligner 3

Étape 3 — Cases où les DEUX gains sont soulignés :
```

|  | B : Gauche | B : Droite |
|---|---|---|
| **A : Haut** | (**3**, 1) | (0, **2**) |
| **A : Bas** | (1, 0) | (**2**, **3**) ★ |

Seule la case (Bas, Droite) a ses deux gains soulignés → **équilibre de Nash unique : (Bas, Droite)**.

### Identifier une stratégie dominante

Avant même d'appliquer la méthode ci-dessus, vérifier s'il existe une **stratégie dominante** : une stratégie meilleure que toutes les autres quelle que soit l'action adverse.

Dans l'exemple ci-dessus, B joue toujours Droite (2 > 1 si A joue Haut, 3 > 0 si A joue Bas). Droite est une stratégie dominante pour B. Sachant cela, A choisit Bas (2 > 0). L'équilibre se trouve sans même construire le tableau des meilleures réponses.

```
Élimination itérative des stratégies dominées :

  1. Éliminer toutes les stratégies strictement dominées
  2. Recommencer sur le jeu réduit
  3. Répéter jusqu'à convergence (ou blocage)

  Si le processus converge vers un unique profil → équilibre dominant
  Si le processus se bloque → appliquer la méthode des meilleures réponses
```

## Jeux classiques

### Le dilemme du prisonnier

Deux suspects sont interrogés séparément. Chacun peut coopérer (se taire) ou trahir.

|  | B coopère | B trahit |
|---|---|---|
| **A coopère** | (−1, −1) | (−10, **0**) |
| **A trahit** | (**0**, −10) | (**−5**, **−5**) ★ |

```
Analyse :
  Meilleures réponses de A : Trahir domine (0 > −1 et −5 > −10)
  Meilleures réponses de B : Trahir domine (0 > −1 et −5 > −10)

  Nash ★ = (Trahit, Trahit) = (−5, −5)
  Optimum de Pareto = (Coopère, Coopère) = (−1, −1)

  → La logique individuelle mène à un résultat collectivement sous-optimal.
    C'est le paradoxe central de ce jeu.
```

Ce jeu modélise : course aux armements, pollution, évasion fiscale, tragédie des communs.

### Le jeu de la poule mouillée (Chicken)

Deux conducteurs foncent l'un vers l'autre. Celui qui dévie en premier perd la face.

|  | B continue | B dévie |
|---|---|---|
| **A continue** | (−100, −100) | (**1**, **−1**) ★ |
| **A dévie** | (**−1**, **1**) ★ | (0, 0) |

```
Analyse :
  Aucune stratégie dominante.
  Deux équilibres en stratégies pures, asymétriques :
    ★ (Continue, Dévie) = (1, −1)   → A gagne la face, B capitule
    ★ (Dévie, Continue) = (−1, 1)   → B gagne la face, A capitule
  + un équilibre en stratégies mixtes

  Question clé : qui va céder ? La réponse dépend des engagements crédibles.
  Stratégie : s'engager publiquement à ne jamais dévier (rendre la menace crédible).
```

Ce jeu modélise : crise des missiles de Cuba, négociations de dernière minute, bras de fer budgétaires.

### La bataille des sexes

Deux partenaires veulent passer la soirée ensemble mais ont des préférences différentes.

|  | B : opéra | B : match |
|---|---|---|
| **A : opéra** | (**2**, **1**) ★ | (0, 0) |
| **A : match** | (0, 0) | (**1**, **2**) ★ |

```
Analyse :
  Deux équilibres en stratégies pures (chacun préfère être ensemble,
  même sur l'activité de l'autre) + un équilibre en stratégies mixtes.

  Problème de coordination : comment choisir entre les deux équilibres ?
  Solutions : communication préalable, convention, point focal (Schelling),
              équilibre de corrélation (arbitre externe).
```

Ce jeu modélise : standardisation technologique, normes, conventions sociales.

### Le jeu du cerf (Stag Hunt)

Un chasseur peut chasser le cerf (coopération nécessaire, gain élevé) ou le lièvre (solo, gain faible mais sûr).

|  | B : cerf | B : lièvre |
|---|---|---|
| **A : cerf** | (**4**, **4**) ★ | (0, **1**) |
| **A : lièvre** | (**1**, 0) | (**1**, **1**) ★ |

```
Analyse :
  Deux équilibres en stratégies pures :
    ★ (Cerf, Cerf) = (4, 4)     → Pareto-optimal, mais requiert la confiance
    ★ (Lièvre, Lièvre) = (1, 1) → Pareto-inférieur, mais sûr sans coordination

  Différence avec le dilemme du prisonnier :
    Ici, si tu es sûr que l'autre coopère, tu veux coopérer aussi.
    Le problème est la confiance, pas la tentation de trahir.
```

Ce jeu modélise : coopération internationale, projets collectifs, confiance institutionnelle.

### Le jeu Hawk-Dove (biologie évolutive)

Utilisé par John Maynard Smith pour modéliser les conflits entre animaux. Un individu peut adopter un comportement agressif (faucon) ou pacifique (colombe) pour accéder à une ressource de valeur V, avec un coût de blessure C si deux faucons se rencontrent.

|  | B : Faucon | B : Colombe |
|---|---|---|
| **A : Faucon** | ((V−C)/2, (V−C)/2) | (V, 0) |
| **A : Colombe** | (0, V) | (V/2, V/2) |

```
Cas V > C (ressource très précieuse, blessure faible) :
  → Faucon domine → tout le monde devient faucon (équilibre en stratégies pures)

Cas V < C (blessure coûteuse) :
  → Pas d'équilibre en stratégies pures
  → Équilibre mixte : proportion p = V/C de faucons dans la population

Ce modèle explique pourquoi les comportements ritualisés (menaces sans combat)
sont évolutivement stables : la sélection naturelle maintient un mélange des deux
stratégies, pas une domination totale d'une seule.
```

## Jeux séquentiels et induction à rebours

Dans un jeu séquentiel, les joueurs agissent l'un après l'autre en observant les actions précédentes. On les représente par un **arbre de décision** et on résout par **induction à rebours** : partir des feuilles (fins) et remonter vers la racine.

**Exemple : la menace d'entrée (entry deterrence)**

Un entrant potentiel décide d'entrer sur un marché. Le monopole en place peut alors faire la guerre des prix ou accommoder le nouvel entrant.

```
                         ┌─────────────────┐
                         │    ENTRANT      │
                         └────────┬────────┘
                    ┌─────────────┴─────────────┐
                 Entre                     N'entre pas
                    │                           │
          ┌─────────┴──────────┐           (0, +100)
          │     MONOPOLE       │         (entrant, mono)
          └─────────┬──────────┘
          ┌─────────┴──────────┐
       Guerre              Accommode
     des prix                  │
          │               (+40, +60)
      (−10, −10)
```

```
Résolution par induction à rebours :

  Étape 1 — Au nœud du Monopole :
    Guerre des prix → (−10) pour le monopole
    Accommode       → (+60) pour le monopole
    → Le monopole choisit Accommoder  (60 > −10) ✓

  Étape 2 — Au nœud de l'Entrant (sachant que le monopole accommodera) :
    Entre        → +40 pour l'entrant
    N'entre pas  →   0 pour l'entrant
    → L'entrant choisit Entrer  (40 > 0) ✓

  Résultat d'équilibre : (Entre, Accommode) → (40, 60)
```

**La menace non crédible**
Le monopole peut annoncer à l'avance : *"Si tu entres, je ferai la guerre des prix."* Mais l'entrant rationnel sait que cette menace est vide : une fois entré, le monopole perdrait lui aussi à faire la guerre. La menace n'est **pas crédible**.

Pour rendre une menace crédible, il faut un engagement préalable qui la rende coûteuse à ne pas exécuter : investissements en capacité de production, contrats publics, réputation sur plusieurs marchés.

**Équilibre parfait en sous-jeux**
Raffinement de l'équilibre de Nash pour les jeux extensifs : les stratégies doivent constituer un équilibre de Nash dans *chaque* sous-jeu, y compris hors du chemin d'équilibre. Cela élimine automatiquement les menaces non crédibles.

## Jeux répétés et coopération

Quand des joueurs interagissent de manière répétée, la coopération peut émerger même sans communication, grâce aux mécanismes de réputation et de représailles.

**Théorème du Folk**
Dans un jeu répété à l'infini (ou avec probabilité de continuation suffisante), tout résultat mutuellement avantageux par rapport à l'équilibre de Nash peut être maintenu comme équilibre, si les joueurs sont suffisamment patients.

**Stratégie Tit-for-Tat**
Développée par Anatol Rapoport et popularisée par Robert Axelrod (tournois de simulation, années 1980) :
- Coopérer au premier tour
- Reproduire ensuite le comportement de l'adversaire au tour précédent

```
Simulation sur le dilemme du prisonnier répété :

Scénario 1 — TfT vs Coopérateur permanent

  Tour │ TfT joue │ Adverse joue │ Gain TfT
  ─────┼──────────┼──────────────┼──────────
    1  │ Coopère  │   Coopère    │   −1
    2  │ Coopère  │   Coopère    │   −1
    3  │ Coopère  │   Coopère    │   −1
       │   ...    │     ...      │   ...
  → Coopération stable, gains mutuels élevés

Scénario 2 — TfT vs Traitre systématique

  Tour │ TfT joue │ Adverse joue │ Gain TfT
  ─────┼──────────┼──────────────┼──────────
    1  │ Coopère  │   Trahit     │  −10
    2  │ Trahit   │   Trahit     │   −5
    3  │ Trahit   │   Trahit     │   −5
       │   ...    │     ...      │   ...
  → TfT limite les pertes dès le 2e tour, punit sans escalade infinie

Scénario 3 — TfT vs TfT

  Tour │ TfT-A   │ TfT-B   │ Gains
  ─────┼─────────┼─────────┼──────────
    1  │ Coopère │ Coopère │ (−1, −1)
    2  │ Coopère │ Coopère │ (−1, −1)
    3  │ Coopère │ Coopère │ (−1, −1)
  → Coopération permanente dès le premier contact
```

TfT est simple, robuste, et performante car elle combine trois propriétés : bienveillance (commence par coopérer), représailles (punit immédiatement), clémence (pardonne dès que l'adversaire coopère).

**Conditions favorisant la coopération**
- Horizon temporel long (pas de "coup final" certain)
- Faible taux d'actualisation (le futur compte autant que le présent)
- Interactions répétées entre les mêmes agents (réputation)
- Transparence des comportements passés

## Jeu de l'ultimatum et remise en cause de la rationalité

Deux joueurs se partagent une somme fixe (100€). A propose un partage, B accepte ou refuse. Si B refuse, les deux repartent avec rien.

```
Structure du jeu (arbre de décision) :

                    ┌──────────────────────────┐
                    │  A propose un partage x% │
                    └─────────────┬────────────┘
                                  │
                        ┌─────────┴─────────┐
                     Accepte             Refuse
                        │                   │
                   (x, 100−x)            (0, 0)
                        ↑
                   B décide ici
```

```
Prédiction théorique (induction à rebours) :
  B accepte toute offre > 0  (car 1€ > 0€)
  → A offre le minimum possible (ex : 1€)
  → Résultat : (99, 1)

Résultats expérimentaux (Güth et al., 1982 ; centaines de réplications) :
  Offre moyenne        : 40–50% de la somme
  Seuil de rejet       : offres < ~25–30% rejetées majoritairement
  Stabilité            : le rejet persiste même avec des sommes élevées
  Universalité         : observé dans toutes les cultures (variations sur le seuil)
```

Les participants sacrifient un gain réel pour punir ce qu'ils perçoivent comme injuste. Ceci révèle des préférences sociales — équité, réciprocité, aversion à l'inégalité — absentes du modèle de l'homo economicus.

**Jeu du dictateur** — variante sans droit de refus pour B. A "dicte" le partage. La théorie prédit que A garde tout. En pratique, la plupart donnent entre 20 % et 30 %. La seule présence d'un autre être humain active un sens de l'équité.

Ces expériences ont fondé l'économie comportementale moderne.

## Jeux de signalement

Dans de nombreuses situations, un agent possède une information privée sur lui-même (sa compétence, sa qualité) et cherche à la communiquer de manière crédible. Un simple message ne suffit pas — il faut un signal *coûteux*, dont le coût est suffisamment différent entre les types pour que l'imitation ne soit pas rentable.

```
Structure d'un jeu de signalement :

  Nature (tirage aléatoire)
       │
       ├── Type productif (prob. p)        ← l'employeur ne sait pas qui est qui
       │        │
       │   Travailleur choisit un signal
       │        ├── Éducation élevée  ──┐
       │        └── Éducation basse   ──┤
       │                                 │
       └── Type peu productif (prob. 1−p) │
                │                        │
           Travailleur choisit un signal  │
                ├── Éducation élevée  ──┤
                └── Éducation basse   ──┤
                                        │
                              Employeur observe
                            le signal, mais PAS le type
                                        │
                              ┌─────────┴─────────┐
                         Salaire haut        Salaire bas
```

**Le modèle de Spence (1973)**
Sur le marché du travail, les travailleurs ont des productivités différentes, inobservables par les employeurs. Un travailleur très productif peut investir dans l'éducation *non pas parce qu'elle le rend plus productif*, mais parce que cet investissement lui coûte moins (en effort, en temps) qu'à un travailleur peu productif.

L'équilibre de signalement : les travailleurs très productifs obtiennent suffisamment d'éducation pour que l'imitation par les peu productifs soit non rentable. Les employeurs interprètent le diplôme comme signal de productivité et rémunèrent en conséquence.

```
Condition d'équilibre séparateur :

  Pour les très productifs    : bénéfice du signal > coût du signal  ✓
  Pour les peu productifs     : bénéfice du signal < coût du signal  ✗
                                         ↑
                       Le coût doit être différentiel entre les types
```

Le résultat est troublant : l'éducation peut avoir une valeur économique individuelle élevée *sans aucune valeur productive directe*. Ce qui crée de la valeur, c'est la *séparation* des types, pas la formation elle-même.

**Conditions d'un signal crédible**
- Coûteux à produire (sinon tout le monde imite)
- Différentiellement coûteux selon les types (condition de séparation)
- Observable par celui à qui il s'adresse

**Autres exemples de signalement**

| Signal | Émetteur | Récepteur | Logique |
|---|---|---|---|
| Diplôme coûteux | Travailleur productif | Employeur | Le peu productif ne peut pas se permettre les mêmes études |
| Publicité ostentatoire | Entreprise de qualité | Consommateur | Seule une bonne entreprise peut rentabiliser cette dépense |
| Garantie longue | Fabricant fiable | Acheteur | Une mauvaise qualité génèrerait trop de remboursements |
| Dividende élevé | Entreprise saine | Investisseur | Coûteux à simuler pour une entreprise en difficulté |
| Rituel d'initiation coûteux | Membre sincère | Groupe | Filtre les opportunistes |

Michael Spence a reçu le Nobel d'économie en 2001, avec George Akerlof et Joseph Stiglitz.

## Théorie des enchères

Les enchères constituent un domaine d'application majeur de la théorie des jeux en information asymétrique.

| Type | Mécanisme | Stratégie optimale | Intuition |
|---|---|---|---|
| Anglaise | Montée successive, plus offrant remporte | Enchérir jusqu'à sa valeur vraie | On s'arrête quand le coût dépasse la valeur |
| Hollandaise | Descente du prix, premier preneur remporte | Sous-enchérir (arbitrage prix/probabilité) | Attendre baisse le prix mais risque de perdre |
| Premier prix (scellée) | Plus offrant paie son offre | Sous-enchérir par rapport à sa valeur | Payer sa valeur vraie = profit nul |
| Deuxième prix (Vickrey) | Plus offrant paie la 2e offre | Enchérir sa valeur vraie (dominant) | Ce qu'on paie ne dépend pas de notre offre |

```
Pourquoi l'enchère de Vickrey incite à révéler sa vraie valeur ?

  Soit v = ta vraie valeur, b = ton enchère, m = la meilleure offre adverse.

  Si b > v et m ∈ [v, b] → tu gagnes mais paies m > v  → perte !
  Si b < v et m ∈ [b, v] → tu perds alors que tu aurais dû gagner → manque à gagner
  Si b = v → tu gagnes si et seulement si v > m, et paies m < v  → optimal

  → Enchérir sa valeur vraie est une stratégie dominante.
```

**Théorème d'équivalence des revenus** : sous certaines conditions (symétrie, neutralité au risque, distribution connue des valeurs), tous ces formats génèrent le même revenu espéré pour le vendeur.

## Critique comportementale

La théorie classique repose sur des hypothèses fortes : rationalité parfaite, maximisation de l'utilité propre, connaissances mutuelles des règles et de la rationalité des autres. Les expériences en laboratoire et sur le terrain ont documenté des déviations systématiques.

**Rationalité limitée (Simon, 1955)**
Les agents ne maximisent pas — ils *satisficent* : ils s'arrêtent à la première solution jugée suffisamment bonne, compte tenu de leurs capacités cognitives et du coût de traitement de l'information. La rationalité est procédurale, pas substantive.

**Biais documentés en théorie des jeux**

| Biais | Description | Impact sur les prédictions |
|---|---|---|
| Aversion aux pertes | Une perte de 10€ pèse plus qu'un gain de 10€ | Modifie les seuils d'acceptation dans les négociations |
| Réciprocité et équité | On punit les comportements injustes même à coût personnel | Explique les rejets dans le jeu de l'ultimatum |
| Biais de présent | Sous-pondération des gains futurs (au-delà de l'actualisation) | Problèmes de cohérence temporelle, procrastination |
| Points focaux (Schelling) | Convergence sur des solutions "saillantes" culturellement | Les équilibres Nash prédits ne sont pas toujours atteints |

**Points focaux de Schelling**
Sans communication, deux agents doivent se retrouver à New York sans avoir fixé de lieu. Où vont-ils ? La plupart répondent : *Grand Central Station, à midi*. Pas parce que c'est l'équilibre de Nash (il en existe des milliers), mais parce que c'est *saillant*. Les normes sociales, les nombres ronds, les lieux symboliques sont des points focaux qui sélectionnent des équilibres dans la vie réelle.

**Théorie des jeux comportementale**
Intègre ces déviations dans des modèles formels. Les modèles d'utilité sociale (Fehr & Schmidt, 1999) ajoutent une aversion à l'inégalité dans la fonction d'utilité et permettent de prédire les résultats du jeu de l'ultimatum.

**Limites de la critique comportementale**
La théorie classique reste un outil normatif puissant : elle dit ce que des agents *rationnels* feraient. Les déviations comportementales sont souvent rationnellement explicables dans un modèle élargi (réputation, préférences sociales). Le débat porte sur le bon niveau de modélisation, pas sur un remplacement complet.

## Équilibre de corrélation

Introduit par Robert Aumann (1974), l'équilibre de corrélation est une généralisation de l'équilibre de Nash qui permet d'obtenir de meilleurs résultats collectifs grâce à une corrélation des stratégies.

```
Mécanisme :

  ┌─────────────────────────────────────────────┐
  │              ARBITRE EXTERNE                │
  │   Tire un profil (sA, sB) selon prob. π     │
  └──────────────────┬──────────────────────────┘
                     │
          ┌──────────┴──────────┐
     Recommande sA         Recommande sB
     à Joueur A            à Joueur B
          │                    │
     A ne voit que sA     B ne voit que sB
          │                    │
     A suit sA ?          B suit sB ?
     (si déviation → perte)    (idem)
```

L'équilibre est atteint quand aucun joueur n'a intérêt à dévier de sa recommandation, sachant que l'autre suit la sienne.

**Exemple : la bataille des sexes**

```
  Nash pur (opéra, opéra) → espérance (2, 1)
  Nash pur (match, match) → espérance (1, 2)
  Nash mixte             → espérance (2/3, 2/3)  ← le pire !

  Équilibre de corrélation : arbitre recommande (opéra, opéra) avec prob. 1/2
                             et (match, match) avec prob. 1/2
  → espérance (3/2, 3/2)  ← meilleur que tous les Nash !

  Ni A ni B n'ont intérêt à dévier : si l'arbitre dit "opéra", A sait que
  B va aussi au match (ou à l'opéra) et ne peut pas faire mieux qu'obéir.
```

**Propriétés**
- Tout équilibre de Nash est un équilibre de corrélation (cas particulier sans corrélation)
- L'ensemble des équilibres de corrélation est convexe et plus facile à calculer
- Il peut obtenir des résultats inatteignables par tout équilibre de Nash

**Interprétations concrètes**
L'arbitre peut être un feu de circulation, une convention sociale, une autorité régulatrice ou simplement une norme culturelle partagée. La corrélation est omniprésente dans la coordination sociale réelle — ce qui explique pourquoi les équilibres de Nash purs sont souvent moins prédictifs que les équilibres de corrélation.

## Théorie des mécanismes

Branche de la théorie des jeux qui s'intéresse à la *conception* des règles du jeu plutôt qu'à leur analyse. Problème inverse : étant donné un objectif social, quelle règle incite les agents à se comporter de manière à l'atteindre ?

```
Théorie des jeux classique :   Règles données → Analyser les comportements
Théorie des mécanismes     :   Objectif donné → Concevoir les règles
```

**Révélation directe** : un mécanisme est dit *incitatif-compatible* si chaque agent a intérêt à révéler ses vraies préférences. L'enchère de Vickrey en est un exemple.

**Principe de révélation** (Myerson) : tout équilibre d'un mécanisme quelconque peut être reproduit par un mécanisme à révélation directe et incitatif-compatible.

Applications : enchères pour les spectres radio, algorithmes d'allocation d'organes (Roth), affectation scolaire (algorithme de Gale-Shapley).

## Applications

**Économie industrielle**
Modèles de Cournot (concurrence en quantités), Bertrand (concurrence en prix), Stackelberg (leader-suiveur). Analyse des cartels, de la dissuasion à l'entrée, de la différenciation des produits.

**Relations internationales**
Négociations commerciales, dissuasion nucléaire, formation d'alliances, crises diplomatiques. La doctrine de la destruction mutuelle assurée (MAD) est directement fondée sur l'équilibre de Nash : ni les États-Unis ni l'URSS n'avaient intérêt à frapper en premier si une riposte dévastatrice était garantie.

**Biologie évolutive**
Les stratégies évolutivement stables (ESS) de Maynard Smith. La sélection naturelle sélectionne les stratégies qui résistent aux mutants — analogie directe avec l'équilibre de Nash. Les comportements ritualisés chez les animaux, les rapports de sex-ratio, les niveaux d'agressivité intra-spécifique s'expliquent par ces modèles.

**Droit et régulation**
Conception des règles juridiques pour inciter les agents à adopter des comportements socialement souhaitables. Analyse des négociations pré-procès, des amendes optimales, des règles de responsabilité.

**Informatique et réseaux**
Routage Internet, protocoles distribués, algorithmes de consensus, conception de mécanismes d'enchères en ligne. Le paradoxe de Braess montre qu'ajouter une route à un réseau peut augmenter les temps de trajet de tous — équilibre de Nash inefficace pour la collectivité.

**Médecine et santé publique**
Vaccination : chaque individu a intérêt à ne pas se vacciner si les autres le font (passager clandestin). La couverture vaccinale optimale ne s'atteint pas spontanément — elle relève d'un problème de coordination ou d'incitation publique.

## Grandes figures

**John von Neumann (1903–1957)** — Mathématicien hongrois-américain, co-fondateur avec Morgenstern. Démontre le théorème minimax pour les jeux à somme nulle (1928). Co-auteur de *Theory of Games and Economic Behavior* (1944).

**Oskar Morgenstern (1902–1977)** — Économiste, co-auteur de l'ouvrage fondateur (1944). Introduit la théorie de l'utilité espérée dans le cadre des jeux.

**John Nash (1928–2015)** — Mathématicien américain. Formalise l'équilibre portant son nom (1950), prouve son existence par un argument topologique (théorème du point fixe de Brouwer). Nobel 1994. Sa vie est retracée dans *A Beautiful Mind*.

**Reinhard Selten (1930–2016)** — Introduit les raffinements de l'équilibre de Nash : équilibre parfait en sous-jeux (1965) et équilibre trembling hand (1975). Nobel 1994 avec Nash et Harsanyi.

**John Harsanyi (1920–2000)** — Formalise les jeux à information incomplète via les types bayésiens : chaque joueur est un "type" tiré par la nature, avec une distribution de probabilité connue de tous. Nobel 1994.

**Thomas Schelling (1921–2016)** — Économiste américain. Théorie des points focaux, de l'engagement, de la menace crédible. Applications à la guerre froide, à la ségrégation, aux négociations. Nobel 2005 avec Aumann.

**Robert Aumann (1930–)** — Développe la théorie des jeux répétés, le concept de connaissance commune, l'équilibre de corrélation. Nobel 2005.

**Roger Myerson (1951–)** — Théorie des mécanismes, principe de révélation, théorie des enchères optimales. Nobel 2007 avec Maskin et Hurwicz.

**Jean Tirole (1953–)** — Applications à l'économie industrielle, à la régulation des monopoles, aux plateformes numériques. Nobel 2014.
