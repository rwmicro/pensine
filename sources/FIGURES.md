---
title: "Guide des figures de données"
domain: "Méta"
subdomain: "Configuration"
tags: [conventions, figures, données, widgets, owid, insee]
date: "2026-10-11"
---
# Guide des figures de données

Comment mettre un chiffre, une courbe ou une carte dans une note du jardin. Les données sont lues **à la construction du site** (pas dans le navigateur) et la source s'affiche sous chaque figure. Inspiré des règles d'Our World in Data et de l'Insee : un titre qui dit ce qu'il faut voir, une source toujours citée, un tableau derrière chaque graphique.

## Les six règles

1. **Le titre est la conclusion**, pas le sujet. « La France a gagné 38 ans d'espérance de vie depuis 1900 », pas « Espérance de vie en France ». Le `sous-titre:` dit ce qui est mesuré et dans quelle unité.
2. **Un chiffre dans un titre se vérifie dans les données** de la figure : relis la dernière valeur et l'année avant d'écrire « deux fois plus ».
3. **Cinq séries au plus** sur une courbe. Au-delà, deux figures, ou un `classer`.
4. **Des pays qui se comparent** : le pays dont parle la note, un pays proche, un pays très différent, et `Monde` comme repère.
5. **Échelle logarithmique** (`echelle: log`) seulement quand les valeurs vont du simple au centuple (PIB par habitant sur trois siècles, émissions par pays). Le lecteur peut toujours basculer.
6. **Pas de figure décorative** : une figure doit montrer quelque chose que le texte autour dit en une phrase.

## Les blocs

Chaque figure est un bloc de code `widget:<nom>` avec des lignes `clé: valeur`. Une clé répétée écrase la précédente, d'où `etape1`, `etape2`… pour les récits.

### Courbe (`owid`)

````markdown
```widget:owid
graphe: life-expectancy
pays: France, Papouasie-Nouvelle-Guinée, Monde
depuis: 1900
titre: La France a gagné 38 ans d'espérance de vie depuis 1900
sous-titre: Espérance de vie à la naissance, en années
unite: ans
```
````

- `graphe:` le nom du graphique dans l'adresse d'Our World in Data (`ourworldindata.org/grapher/life-expectancy`).
- `pays:` noms français, codes ISO (`PNG`, `FRA`) ou agrégats (`Monde`, `Afrique`, `Union européenne`).
- `depuis:`, `jusqua:` bornes en années ; `zero: non` pour ne pas partir de zéro ; `echelle: log` ; `colonne: 2` si le graphique a plusieurs colonnes.
- Le lecteur a trois onglets (Graphe, Tableau, Sources) et peut télécharger le CSV et le SVG.

### Devine la courbe (`owid`, `type: devine`)

Le lecteur dessine la suite de la courbe après `devine:` puis compare avec la réalité. À réserver aux tendances qui surprennent.

```
type: devine
devine: 1970
```

### Pyramide des âges (`owid`, `type: pyramide`)

`graphe: population-by-five-year-age-group`, un seul pays, `comparer: 1950` pour le contour d'une année de référence. Un curseur fait défiler les années.

### Récit (`owid`, `type: recit`)

La courbe reste à l'écran pendant que le texte défile ; chaque étape zoome sur une période et met un pays en avant.

```
type: recit
etape1: 1700-1800 | Royaume-Uni | Avant 1800, le niveau de vie progresse à peine.
etape2: 1800-1913 | Royaume-Uni | Le Royaume-Uni décolle le premier.
```

### Bulles (`owid`, `type: bulles`)

Le nuage de Gapminder : un point par pays, PIB par habitant en abscisse (échelle log), espérance de vie en ordonnée, taille selon la population, couleur selon le continent. Un bouton anime les années.

```
type: bulles
pays: France, Chine, Inde, Nigeria, États-Unis
depuis: 1900
pas: 10
trace: Chine
```

- `x:`, `y:`, `taille:` d'autres graphiques OWID que les trois par défaut, avec `x-titre:`, `y-titre:`, `x-unite:`, `y-unite:`, `x-echelle: lineaire`.
- `trace:` laisse la piste d'un pays derrière sa bulle.

### Pente (`owid`, `type: pente`)

Deux années face à face, une ligne par pays : qui monte, qui descend, qui double qui. `annees: 1990, 2023`, `mettre-en-avant: Inde, France` (les autres restent en gris).

### Petits multiples (`owid`, `type: multiples`)

Un petit graphique par pays sur la même échelle, `reference: Monde` en gris dans chacun. Ou plusieurs graphiques pour un seul pays, avec `panneaux:` (survoler un panneau montre la même année dans les autres) :

```
type: multiples
panneaux: life-expectancy | Espérance de vie | ans ; annual-working-hours-per-worker | Heures travaillées par an | heures
pays: France
```

### Deux mesures d'un même sujet (`graphe2`)

Sur une courbe, `graphe2:` ajoute un bouton pour basculer vers un second graphique (total contre par habitant), avec `onglet:` / `onglet2:` pour les libellés des boutons et `titre2:`, `sous-titre2:`, `unite2:` pour le second.

### Variantes, doublement, projections

- `vue:` choisit une variante d'un graphique qui en a plusieurs, comme dans l'adresse OWID : `graphe: incomes-of-the-richest` + `vue: quantile=_10&welfare_type=before_tax` (part des 10 % les plus riches).
- `doublement: 2` trace en pointillés la courbe qui doublerait tous les 2 ans (loi de Moore), à lire avec `echelle: log`.
- `projection: oui` sur une pyramide ajoute la part des 65 ans et plus jusqu'en 2100, projection moyenne de l'ONU en pointillés.

### Autres figures de données

| Bloc | Clés | Usage |
|------|------|-------|
| `fiche-pays` | `pays`, `depuis` | Population, espérance de vie, PIB par habitant, avec leur évolution |
| `vrai-faux` | `affirmation`, `reponse` (vrai/faux), `explication`, et facultativement `graphe`, `pays`… | Une idée reçue vérifiée par les données |
| `classer` | `consigne`, `graphe` + `pays` + `annee`, ou `elements: A = 1; B = 2`, `ordre`, `unite` | Le lecteur ordonne, puis vérifie |
| `convertisseur` | `montant`, `monnaie` (AF, NF, EUR), `annee` | Francs ou euros d'une année en euros d'aujourd'hui (Insee) |
| `interets` | `capital`, `taux`, `duree` | Placement contre inflation |
| `ouverture` | `coups` (UCI, comme `moves:` de l'échiquier) | Résultats Lichess de l'ouverture par niveau |
| `fiche-langue` | `wikidata` (ex. `Q9240`) | Locuteurs, écriture, famille, code ISO |
| `durees` | `ligne1: Empire romain \| -27 \| 476 \| note`, …, `mettre-en-avant`, `source` | Durées comparées (empires, dynasties) ; années négatives avant J.-C. ; tri par date ou par durée |
| `partie` | `coups` (UCI), `san` (notation française), `commentaire12:` (affiché après le 12ᵉ demi-coup), `fin`, `titre` | Une partie d'échecs rejouée coup par coup |
| `paires` | `paire1: audio/a.mp3 = mot (sens) \| audio/b.mp3 = mot (sens)`, `consigne` | Paires minimales : le lecteur entend un des deux mots et choisit |
| `conjugaison` | `langue` (Allemand, Espagnol, Turc, Roumain, Indonésien), `verbe` | Tableau de conjugaison, terminaisons en couleur |
| `faux-amis` | `langue`, `mot1: mot \| bon sens \| piège ; autre piège \| explication` | Quiz de faux amis |
| `arbre-langues` | aucune | Arbre des familles de langues, les langues du jardin cliquables |

## Dans le texte

- **Prix d'époque** : `` `prix: 300 francs 1950` `` affiche « 300 francs » avec un bouton qui donne la valeur en euros d'aujourd'hui. « francs » seul veut dire anciens francs avant 1960, nouveaux francs ensuite ; on peut écrire `AF`, `NF`, `euros`.
- **Encadré chiffres** : un callout `> [!chiffres]` dont chaque ligne commence par le chiffre en gras.

```markdown
> [!chiffres]
> - **×2,8** : le PIB par habitant du Royaume-Uni entre 1760 et 1913
> - **1 milliard** d'humains vers 1800, **2** en 1927
```

## En-tête

- `pays: France, Japon` place la note sur la carte du monde du site (`/carte/`), en plus de son dossier.
- `wikidata: Q9312` date la note sur la frise à partir de Wikidata (naissance et mort, début et fin) quand elle n'a pas de `year:`.
- `format: graphique` : une note courte bâtie autour d'une figure (« un graphique, trois paragraphes »), listée sur l'accueil et dans le flux `/graphiques.xml`. Trois paragraphes : ce qu'on voit, pourquoi, ce qu'il faut garder en tête en le lisant.

## Couleurs et accessibilité

Les couleurs des séries sont fixes et dans le même ordre partout ; elles ont été vérifiées pour les daltonismes courants, en clair comme en sombre. Ne compte jamais sur la couleur seule : chaque courbe a son nom au bout de la ligne et dans la légende, et l'onglet Tableau donne tous les chiffres.
