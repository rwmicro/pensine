---
title: "CLAUDE.md — Conventions du vault Pensine"
domain: "Méta"
subdomain: "Configuration"
tags: [claude, conventions, vault, configuration, audio]
date: "2026-07-31"
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
└── sources/            # Templates, conventions et images
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

## Prononciation audio (feature du site learn-nebula)

Les notes de langues peuvent embarquer des clips de prononciation, rendus en lecteurs audio sur le site learn-nebula.

### Ajouter un audio

Surligne le terme à prononcer avec la syntaxe :

```
==terme::code==            ex. ==Hola::es==   ==keefak::ar-lb==   ==你好::zh==
==terme::code:female==     pour la voix féminine (male par défaut)
```

Puis lance le script de génération (ci-dessous). Le surlignage devient une image markdown audio :

```
![terme](audio/xxx.mp3)
```

Sur learn-nebula, `rehypeVaultAssets` (lib/markdown.ts) transforme toute image markdown à extension audio en lecteur audio « .pron », avec le `alt` comme label. Ne pas utiliser l'embed Obsidian `![[...]]` : le site ne le convertit pas en lecteur.

### Où vivent les clips

- Un sous-dossier `audio/` à côté de chaque note (chemin note-relative).
- Stockés en git-lfs (`*.mp3` dans `.gitattributes`) — à committer (le site clone ce repo dans `content/posts/`).
- `.tts_audio_cache/` est le cache maître local, gitignoré (ne pas committer).

### Codes de langue

| Code | Langue | | Code | Langue |
|------|--------|-|------|--------|
| `fr` | Français | | `ms` | Malais (+ Sambas via `::ms`) |
| `es` | Espagnol | | `zh` | Mandarin |
| `en` | Anglais | | `ar` | Arabe standard (+ Darija via `::ar`) |
| `de` | Allemand | | `ar-lb` | Arabe libanais |
| `tr` | Turc | | `hi` | Hindi |
| `az` | Azéri | | `ta` | Tamoul |
| `ro` | Roumain | | `id` | Indonésien |

Non gérées par ElevenLabs, aucun audio possible : ouïghour, kabyle, hakka, tok pisin.

### Générer

Le tooling est dans **`sources/tts/`** : `highlighter.py` (surligne les tableaux) puis `script_TTS_langues.py` (génère l'audio, ElevenLabs, modèle `eleven_v3`). Détails : `sources/tts/README.md`.

```
cd sources/tts
python highlighter.py "../../Social Sciences/Languages - Dialects" --apply   # surligne
python script_TTS_langues.py "../../Social Sciences/Languages - Dialects/<Langue>"  # génère
```

- Ajouter une langue = une ligne dans le `CONFIG` de `highlighter.py` et le `LANGUAGES` du script.
- Clé API : variable `ELEVENLABS_API_KEY`, ou fichier `sources/tts/.env` (gitignoré).
- Idempotent : une fois converti en `![...](audio/…)`, un terme n'est pas regénéré.
- Attention : le `cache_key` n'inclut pas le voice_id. Si tu changes une voix, purge le `.tts_audio_cache/` et les dossiers `audio/` de la langue avant de relancer, sinon les anciens clips (mauvaise voix) sont réutilisés.

### Mise en ligne

Le build learn-nebula clone ce repo et fait `git lfs pull --include=*.mp3`. La feature audio est sur learn-nebula `main` (depuis la PR #26), donc pousser pensine publie directement les audios.

## Fichiers à ne jamais supprimer

- `Social Sciences/Languages - Dialects/Indonésien/.claude/` — configuration Claude
- `Social Sciences/Languages - Dialects/Kabyle/tmp.md` — fichier de travail

## Workflow git

Format des commits suivant l'historique : `save: DD/MM/YYYY — description (N fichiers)`.

Exemples récents :
- `save: 28/04/2026 — ajout langue Mandarin (11 fichiers)`
- `save: 23/04/2026 — ajout langue Spanish (9 fichiers)`
