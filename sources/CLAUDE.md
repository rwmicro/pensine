---
title: "CLAUDE.md — Conventions du vault Pensine"
domain: "Méta"
subdomain: "Configuration"
tags: [claude, conventions, vault, configuration]
date: "2026-04-28"
---
# CLAUDE.md — Conventions du vault Pensine

Instructions à destination de Claude Code pour tout travail dans ce vault Obsidian.

## Langue

- **Toujours produire le contenu en français** — c'est un vault francophone
- Style soutenu mais accessible, vulgarisation de qualité

## Frontmatter YAML obligatoire

Tout fichier `.md` créé doit commencer par :

```yaml
---
title: "Titre de la note"
domain: "Applied Sciences" | "Social Sciences" | autre
subdomain: "Sous-domaine > Catégorie"
tags: [tag1, tag2, tag3]
date: "YYYY-MM-DD"
---
```

## Règles de formatage

- `---` autorisé **uniquement** pour le frontmatter — jamais comme séparateur dans le corps
- Titre `# Titre` (H1) en début de fichier après le frontmatter
- **Pas d'emojis** dans le contenu
- Tables markdown pour les comparaisons
- Blocs de code pour les exemples
- Diagrammes mermaid pour les sujets visuels (cycles, flux, hiérarchies, proportions)
- **Pas de section "Voir aussi"** — ces sections ont été supprimées en masse

## Structure du vault

```
pensine/
├── Applied Sciences/   # Sciences appliquées (Bio, Chem, CS, Math, Physics, Sport, Echecs...)
├── Social Sciences/    # Sciences sociales (Anthropo, Arts, Histoire, Langues, Philo...)
└── sources/            # Templates et images
```

## Dossier `Languages - Dialects/`

Les langues suivent une structure standard 01-06 :
- `01-Phonologie/` — alphabet, prononciation, tons
- `02-Grammaire/`
- `03-Communication/` — Phrases-Essentielles, Salutations, Registres, Situations
- `04-Vocabulaire/`
- `05-Culture/`
- `06-Ressources/` — Anki, apps, livres, films

Nommage des dossiers : **français** (Espagnol, Mandarin, Azerbaïdjanais, Turc, Roumain...).

## Fichiers à ne jamais supprimer

- `Social Sciences/Languages - Dialects/Indonésien/.claude/` — configuration Claude
- `Social Sciences/Languages - Dialects/Kabyle/tmp.md` — fichier de travail

## Workflow git

Format des commits suivant l'historique : `save: DD/MM/YYYY — description (N fichiers)`.

Exemples récents :
- `save: 28/04/2026 — ajout langue Mandarin (11 fichiers)`
- `save: 23/04/2026 — ajout langue Spanish (9 fichiers)`
