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
- Diagrammes mermaid pour les sujets visuels — voir « Diagrammes et animations » pour le choix du type
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

## Diagrammes et animations

### Choisir le type de diagramme

Un `flowchart` est le réflexe par défaut, et c'est un défaut : sur les 297 diagrammes du vault, 282 en sont encore. Un flux ne convient qu'à ce qui *s'enchaîne*. Le reste a son type.

| Contenu | Type |
|---|---|
| Étapes, causalité, hiérarchie | `flowchart` |
| Échange entre deux parties, protocole | `sequenceDiagram` |
| Automate, cycle de vie, transitions | `stateDiagram-v2` |
| Format binaire, en-tête de protocole | `packet-beta` |
| Couches, plan mémoire, blocs alignés | `block-beta` |
| Chronologie datée | `timeline` |
| Carte d'un sujet, arborescence libre | `mindmap` |
| Proportions d'un tout | `pie` |
| Positionnement sur deux axes | `quadrantChart` |

`graph` est l'ancien nom de `flowchart` — les deux coexistent dans le vault, `flowchart` pour les nouveaux.

Un schéma fait à la main en caractères semi-graphiques est presque toujours un de ces types qui s'ignore.

### Pièges de syntaxe

Quatre causes ont cassé 14 diagrammes, qui s'affichaient en boîte d'erreur :

- **Libellés non quotés.** Parenthèses, apostrophes et crochets cassent le parseur. Règle simple : tout libellé qui n'est pas purement lettres, chiffres et espaces se met entre guillemets — `A["Cache L1 (32 Ko)"]`.
- **Saut de ligne.** `\n` dans un libellé quoté, pas `<br>`.
- **Mots réservés en identifiant de nœud.** Un nœud nommé `graph` suffit à tout faire échouer. Préfixer en cas de doute.
- **Arêtes.** `-.->|label|` prend sa barre fermante, et on ne mélange pas deux syntaxes d'arête (`--` avec `-.->`) sur la même ligne.

Le pré-rendu mermaid de learn-nebula est un gate de build : un diagramme qui ne parse pas fait échouer la CI du site. Une coquille ne passe donc pas inaperçue, mais elle bloque la mise en ligne.

### Animations manim

Un bloc ` ```manim ` porte une scène **manimgl** (`from manimlib import *`), précédée en commentaire de la commande qui la rend.

````
```manim
# Rendu : manimgl charge_rc.py ChargeDechargeRC
from manimlib import *


class ChargeDechargeRC(Scene):
    def construct(self):
        ...
```
````

**Le rendu est retrouvé par empreinte du code.** `rehypeManim` calcule le SHA-256 de la source détourée, garde les 16 premiers caractères hexadécimaux et cherche `_manim/<empreinte>.mp4` (aussi `.gif`, `.png`, `.webm`). Sans fichier correspondant, le bloc retombe en source repliée « (no cached render) ».

Conséquence à garder en tête : **modifier un seul caractère de la scène change l'empreinte**. L'ancienne vidéo devient orpheline et la note perd sa figure en silence. Toute retouche impose donc de regénérer, puis de supprimer le `.mp4` devenu orphelin.

État actuel : 39 animations, 39 rendus, 21 Mo, aucun orphelin.

#### Regénérer

```
xvfb-run -a manimgl scene.py NomDeLaScene -w --video_dir <dossier>
```

`xvfb-run` n'est pas optionnel : manimgl ouvre un contexte OpenGL à l'import et échoue sans serveur X, même en écriture de fichier.

Quatre préalables, à refaire sur toute machine neuve :

- en-têtes de développement **pango** et **cairo**, sans quoi `manimpango` ne se construit pas ;
- collections TeX Live `dsfont`, `tipa`, `calligra`, `wasysym`, `pifont`, `ctex` ;
- `mktexlsr` après toute installation TeX — un paquet présent sur le disque reste invisible à `kpsewhich` tant que l'index kpathsea n'est pas régénéré ;
- **`\usepackage[safe]{tipa}`** dans `manimlib/tex_templates.yml` (les deux occurrences). Sans l'option `safe`, tipa détourne `\|`, `\;` et `\!`, ce qui fait échouer toute scène qui s'en sert — six d'un coup ici.

## Widgets interactifs (feature du site learn-nebula)

Certaines notes embarquent des widgets manipulables, rendus sur learn-nebula et laissés en bloc de code lisible dans Obsidian.

### Syntaxe

Un bloc de code dont le langage est `widget:<nom>`, avec un corps en `clé: valeur` :

````
```widget:ieee754
value: 0.1
bits: 32
```
````

### Widgets disponibles

| Nom | Paramètres | Ce qu'il montre |
|---|---|---|
| `ieee754` | `value`, `bits` (32 ou 64) | Décomposition signe/exposant/mantisse, valeur exacte stockée. Bits cliquables |
| `complement2` | `value`, `bits` (4 à 32) | Même motif lu comme signé et non signé, recette « inverser puis +1 » |
| `cache-locality` | `size`, `line`, `capacity` | Parcours en lignes ou en colonnes, défauts de cache avec éviction LRU |
| `subnet` | `value`, `prefix` | Frontière réseau/hôte sur les 32 bits, masque, diffusion, plage utilisable |
| `hash-avalanche` | `value`, `algo` | Effet d'avalanche : un caractère change, la moitié des bits de l'empreinte bascule |
| `encodage` | `value` | Un texte en UTF-8, hexadécimal, base64, URL, double URL et entités HTML |
| `boutisme` | `value`, `bits` (16, 32, 64) | Disposition des octets en petit et grand boutiste, avec les décalages |
| `regex` | `pattern`, `flags`, `text` | Correspondances surlignées et groupes capturés. `\n` dans `text` = saut de ligne |
| `seuil` | `threshold` | Seuil de décision, matrice de confusion, précision, rappel, F1 |
| `complexite` | `exp` (n = 2^exp) | Opérations et temps par classe de complexité, effet des constantes |
| `table-verite` | `expr`, `compare` | Table de vérité et test d'équivalence. Opérateurs `! & | ^` et parenthèses |
| `cadre-pile` | — | Cadre de pile pas à pas au fil d'un appel, `rsp` et `rbp` suivis |
| `pipeline` | `forwarding` | Pipeline à 5 étages, aléa charge-utilisation, effet du renvoi de résultat |
| `intervalle` | `interval`, `base` | Gamme juste contre tempérament égal, **à l'écoute** : battements, cents |
| `echiquier` | `fen`, `moves` | Position d'échecs, coups en notation de cases (e2e4), avance pas à pas |
| `trapeze-vocalique` | `vowels` (`sym:antériorité,aperture,arrondie`) | Espace vocalique continu et traits articulatoires |
| `punnett` | `parent1`, `parent2`, `dominant` | Croisement mendélien ou lié à l'X, proportions génotypiques |
| `matrice-2d` | `a`, `b`, `c`, `d` | Matrice 2×2 comme transformation du plan : déterminant, directions propres |
| `logistique` | `r` | Suite logistique, orbite et diagramme de bifurcation |
| `theorie-jeux` | `payoffs` (`3,3 \| 0,5 \| 5,0 \| 1,1`), `r1`, `r2`, `c1`, `c2` | Matrice de gains, équilibres de Nash, optimalité de Pareto |
| `harmonie-vocalique` | `stem` | Harmonie vocalique turque : un suffixe prend sa voyelle du radical |
| `ton` | `syllables` (`ni3 hao3`) | Contours de hauteur et sandhi tonal du mandarin |
| `racine-arabe` | `root`, `translit` | Famille de mots dérivés d'une racine trilitère par les schèmes |
| `abugida` | — | Composition devanagari : consonne + signe vocalique → syllabe |
| `ordre-des-mots` | — | Ordre des constituants SVO / SOV / VSO selon la langue |
| `depistage` | `prevalence`, `sensibilite`, `specificite` | Valeur prédictive d'un test : pourquoi un bon test dépiste mal une maladie rare |
| `pharmacocinetique` | `dose`, `intervalle`, `demiVie` | Concentration plasmatique, accumulation, délai jusqu'au plateau |
| `cadrage` | — | Fait subir l'effet de cadrage au lecteur avant de le nommer |
| `tcl` | `loi`, `n` | Théorème central limite : distribution des moyennes, erreur-type en 1/√n |

### Fonctionnement

`rehypeWidgets` (learn-nebula, `lib/markdown.ts`) transforme le bloc en point de montage, que `public/js/widgets.js` hydrate. Un nom inconnu reste affiché comme un bloc de code — une coquille est donc visible, jamais silencieuse. Sans JavaScript, une ligne de repli remplace le widget.

Ajouter un widget = une entrée dans `WIDGETS` et `WIDGET_FALLBACK` (`lib/markdown.ts`), un constructeur dans `BUILDERS` (`public/js/widgets.js`), et les styles `.w-*` dans `assets/css/main.css`.

## Fichiers à ne jamais supprimer

- `Social Sciences/Languages - Dialects/Indonésien/.claude/` — configuration Claude
- `Social Sciences/Languages - Dialects/Kabyle/tmp.md` — fichier de travail

## Workflow git

Format des commits suivant l'historique : `save: DD/MM/YYYY — description (N fichiers)`.

Exemples récents :
- `save: 28/04/2026 — ajout langue Mandarin (11 fichiers)`
- `save: 23/04/2026 — ajout langue Spanish (9 fichiers)`
