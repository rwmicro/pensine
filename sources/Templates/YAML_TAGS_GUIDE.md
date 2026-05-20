---
title: "Guide du système de tags et frontmatter YAML"
domain: "sources"
subdomain: "Templates"
date: "2026-02-04"
---

# Guide du système de tags et frontmatter YAML

## Qu'est-ce que le frontmatter YAML ?

Le **frontmatter YAML** est un bloc de métadonnées situé au début d'une note Markdown, encadré par `---`. Il permet d'ajouter des informations structurées à vos notes pour faciliter l'organisation, la recherche et l'analyse.

### Exemple basique

```yaml
type: concept
tags: [philosophy, stoicism]
author: Marc Aurèle
created: 2026-01-01
modified: 2026-01-01

# Stoïcisme

Contenu de la note...
```


## Champs recommandés

### Champs essentiels

**type** : Type de note
- `person` : Biographie, personnage
- `concept` : Idée, théorie, concept abstrait
- `technology` : Outil, langage, framework
- `book` : Livre, ouvrage
- `project` : Projet personnel ou professionnel
- `meeting` : Compte-rendu de réunion
- `daily` : Note quotidienne
- `moc` : Map of Content (carte de contenu)

**tags** : Liste de tags pour catégoriser
```yaml
tags: [philosophy, stoicism, ancient-rome]
```

**created** : Date de création
```yaml
created: 2026-01-01
```

**modified** : Date de dernière modification
```yaml
modified: 2026-01-01
```

### Champs spécifiques par type

#### Pour les personnes (type: person)

```yaml
type: person
tags: [person, philosophy, ancient-greece]
birth: -470
death: -399
nationality: Grec
occupation: Philosophe
domain: Philosophie
movement: Philosophie antique
created: 2026-01-01
modified: 2026-01-01
```

#### Pour les concepts (type: concept)

```yaml
type: concept
tags: [concept, philosophy, ethics]
domain: Philosophie morale
difficulty: intermediate
status: complete
created: 2026-01-01
modified: 2026-01-01
```

#### Pour les technologies (type: technology)

```yaml
type: technology
tags: [technology, programming, version-control]
category: DevTools
status: stable
license: GPL-2.0
language: C
created: 2026-01-01
modified: 2026-01-01
```

#### Pour les livres (type: book)

```yaml
type: book
tags: [book, philosophy, existentialism]
author: Jean-Paul Sartre
year: 1943
isbn: 978-2070329137
status: completed
rating: 4/5
genre: Philosophie
language: Français
pages: 722
created: 2026-01-01
modified: 2026-01-01
```

#### Pour les projets (type: project)

```yaml
type: project
tags: [project, programming, web-dev]
status: in-progress
priority: high
start-date: 2026-01-01
end-date: 2026-06-01
team: [Alice, Bob, Charlie]
budget: 50000
created: 2026-01-01
modified: 2026-01-01
```


## Système de tags

### Taxonomie recommandée

#### Tags par domaine (niveau 1)

**Sciences humaines et sociales**
- `philosophy` : Philosophie
- `psychology` : Psychologie
- `history` : Histoire
- `sociology` : Sociologie
- `anthropology` : Anthropologie
- `language` : Linguistique, langues
- `literature` : Littérature
- `religion` : Religion, spiritualité

**Sciences appliquées**
- `science` : Sciences en général
- `mathematics` : Mathématiques
- `physics` : Physique
- `chemistry` : Chimie
- `biology` : Biologie
- `medicine` : Médecine
- `technology` : Technologie
- `engineering` : Ingénierie
- `computer-science` : Informatique

**Arts et culture**
- `art` : Arts visuels
- `music` : Musique
- `cinema` : Cinéma
- `architecture` : Architecture
- `theater` : Théâtre

**Autres**
- `economy` : Économie
- `politics` : Politique
- `law` : Droit
- `education` : Éducation
- `sport` : Sport
- `health` : Santé

#### Tags par sous-domaine (niveau 2)

**Philosophie**
- `ethics` : Éthique
- `metaphysics` : Métaphysique
- `epistemology` : Épistémologie
- `logic` : Logique
- `aesthetics` : Esthétique
- `political-philosophy` : Philosophie politique

**Histoire**
- `ancient-history` : Antiquité
- `medieval-history` : Moyen Âge
- `modern-history` : Époque moderne
- `contemporary-history` : Époque contemporaine

**Informatique**
- `programming` : Programmation
- `web-dev` : Développement web
- `data-science` : Science des données
- `ai-ml` : IA et Machine Learning
- `cybersecurity` : Cybersécurité
- `devops` : DevOps

#### Tags par période/mouvement

**Philosophie**
- `ancient-greece` : Grèce antique
- `stoicism` : Stoïcisme
- `existentialism` : Existentialisme
- `phenomenology` : Phénoménologie
- `pragmatism` : Pragmatisme

**Histoire**
- `renaissance` : Renaissance
- `enlightenment` : Lumières
- `industrial-revolution` : Révolution industrielle
- `ww1` : Première Guerre mondiale
- `ww2` : Seconde Guerre mondiale
- `cold-war` : Guerre froide

**Art**
- `baroque` : Baroque
- `romanticism` : Romantisme
- `impressionism` : Impressionnisme
- `modernism` : Modernisme
- `postmodernism` : Postmodernisme

#### Tags par région géographique

- `europe` : Europe
- `asia` : Asie
- `africa` : Afrique
- `americas` : Amériques
- `oceania` : Océanie
- `france` : France
- `china` : Chine
- `india` : Inde
- `japan` : Japon

#### Tags par statut

- `wip` : Work in progress (en cours)
- `draft` : Brouillon
- `review` : À réviser
- `complete` : Complet
- `archived` : Archivé

#### Tags par difficulté

- `beginner` : Débutant
- `intermediate` : Intermédiaire
- `advanced` : Avancé
- `expert` : Expert


## Bonnes pratiques

### 1. Cohérence

- Utilisez toujours les mêmes tags pour les mêmes concepts
- Préférez l'anglais pour les tags (meilleure portabilité)
- Utilisez des tirets (-) plutôt que des espaces ou underscores

✅ Bon :
```yaml
tags: [ancient-greece, philosophy, stoicism]
```

❌ Mauvais :
```yaml
tags: [Ancient Greece, philosophie, Stoïcism]
```

### 2. Nombre de tags

- **2-5 tags maximum** par note
- Tags trop nombreux = perte de sens
- Tags trop peu = difficile à retrouver

### 3. Hiérarchie

Organisez vos tags du général au spécifique :

```yaml
tags: [philosophy, ethics, stoicism]
# Domaine → Sous-domaine → Mouvement
```

### 4. Évitez les redondances

Si le type est `person`, pas besoin du tag `person` :

❌ Redondant :
```yaml
type: person
tags: [person, philosophy]
```

✅ Mieux :
```yaml
type: person
tags: [philosophy, ancient-greece]
```

### 5. Tags composés

Pour les concepts complexes, utilisez des tags composés :

```yaml
tags: [computer-science, data-science, machine-learning]
```


## Utilisation avancée avec Dataview

Avec le plugin **Dataview** d'Obsidian, vous pouvez interroger vos notes via le frontmatter.

### Exemples de requêtes

**Lister tous les philosophes**

```dataview
TABLE birth, death, nationality
FROM #person
WHERE contains(tags, "philosophy")
SORT birth ASC
```

**Livres lus avec note ≥ 4/5**

```dataview
TABLE author, year, rating
FROM #book
WHERE status = "completed" AND rating >= 4
SORT rating DESC
```

**Projets en cours**

```dataview
TABLE priority, start-date, end-date
FROM #project
WHERE status = "in-progress"
SORT priority DESC, end-date ASC
```

**Notes modifiées récemment**

```dataview
TABLE type, tags, modified
WHERE modified >= date(today) - dur(7 days)
SORT modified DESC
```


## Migration progressive

Si vous avez déjà des notes sans frontmatter :

### Étape 1 : Commencez par les nouvelles notes

Utilisez les templates du dossier `Templates/` qui incluent déjà le frontmatter.

### Étape 2 : Ajoutez progressivement aux notes importantes

Ne migrez pas tout d'un coup. Priorisez :
1. Notes MOC et index
2. Notes fréquemment consultées
3. Fiches de personnes et concepts clés

### Étape 3 : Utilisez un script (optionnel)

Pour ajouter automatiquement du frontmatter :

```bash
# Ajouter un frontmatter basique aux .md sans frontmatter
find . -name "*.md" -exec sed -i '1i---\ntags: []\ncreated: 2026-01-01\n---\n' {} \;
```

**Attention** : Sauvegardez avant !


## Exemples réels

### Exemple 1 : Note sur Socrate

```yaml
type: person
tags: [person, philosophy, ancient-greece]
birth: -470
death: -399
nationality: Grec
occupation: Philosophe
domain: Philosophie morale
created: 2026-01-01
modified: 2026-01-01

# Socrate

Philosophe grec de l'Antiquité...
```

### Exemple 2 : Note sur le Stoïcisme

```yaml
type: concept
tags: [concept, philosophy, ethics, stoicism]
domain: Philosophie morale
period: Antiquité → Aujourd'hui
founders: [Zénon de Cition]
created: 2026-01-01
modified: 2026-01-01

# Stoïcisme

École philosophique fondée à Athènes...
```

### Exemple 3 : Note sur Git

```yaml
type: technology
tags: [technology, programming, version-control, devops]
category: DevTools
status: stable
license: GPL-2.0
language: C
first-release: 2005-04-07
creator: Linus Torvalds
website: https://git-scm.com
created: 2026-01-01
modified: 2026-01-01

# Git - Système de contrôle de version

Git est un système de contrôle de version distribué...
```


## Outils et plugins recommandés

### Plugins Obsidian

1. **Dataview** : Requêter vos notes via le frontmatter
2. **Templater** : Créer des templates avec variables
3. **Tag Wrangler** : Gérer et renommer les tags en masse
4. **Metadata Menu** : Interface visuelle pour les métadonnées
5. **Frontmatter Tag Suggest** : Autocomplétion des tags

### Installation

1. Ouvrir Obsidian Settings
2. Community Plugins → Browse
3. Rechercher et installer les plugins
4. Activer les plugins


## Ressources

### Documentation

- [Obsidian - YAML frontmatter](https://help.obsidian.md/Advanced+topics/YAML+front+matter)
- [Dataview Plugin](https://blacksmithgu.github.io/obsidian-dataview/)
- [Templater Plugin](https://silentvoid13.github.io/Templater/)

### Inspirations

- [Zettelkasten Method](https://zettelkasten.de/)
- [PARA Method](https://fortelabs.co/blog/para/) (Projects, Areas, Resources, Archives)
- [Johnny Decimal System](https://johnnydecimal.com/)


## Cheat Sheet rapide

```yaml
# Type de note
type: [person|concept|technology|book|project|meeting|daily|moc]

# Tags (2-5 recommandés)
tags: [domaine, sous-domaine, spécifique]

# Dates
created: YYYY-MM-DD
modified: YYYY-MM-DD

# Statut (optionnel)
status: [draft|wip|review|complete|archived]

# Autres champs selon le type
# Person: birth, death, nationality, occupation
# Book: author, year, isbn, rating, status
# Project: priority, start-date, end-date, team
# Technology: category, license, language
```


*Créé le : 2026-01-01*  
*Version : 1.0*
