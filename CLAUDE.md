# CLAUDE.md — Conventions du vault *pensine*

## 🔊 Prononciation audio (feature du site learn-nebula)

Les notes de langues (`Social Sciences/Languages - Dialects/`) peuvent embarquer
des clips de prononciation, rendus en lecteurs ▶ sur learn-nebula.

### Ajouter un audio
Surligne le terme à prononcer avec la syntaxe :

    ==terme::code==            ex. ==Hola::es==   ==keefak::ar-lb==   ==你好::zh==
    ==terme::code:female==     pour la voix féminine (male par défaut)

Puis lance le script de génération (ci-dessous). Le surlignage devient une
**image markdown audio** :

    ![terme](audio/xxx.mp3)

Sur learn-nebula, `rehypeVaultAssets` (lib/markdown.ts) transforme toute image
markdown à extension audio en lecteur ▶ « .pron », avec le `alt` comme label.
⚠️ **Ne pas** utiliser l'embed Obsidian `![[...]]` : le site ne le convertit pas
en lecteur.

### Où vivent les clips
- Un sous-dossier **`audio/` à côté de chaque note** (chemin note-relative).
- Stockés en **git-lfs** (`*.mp3` dans `.gitattributes`) — **à committer** (le
  site clone ce repo dans `content/posts/`).
- `.tts_audio_cache/` = cache maître local, **gitignoré** (ne pas committer).

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

**Non gérées par ElevenLabs — aucun audio possible** : ouïghour, kabyle, hakka,
tok pisin.

### Générer
Script : `~/Desktop/script_lang_pensine/script_TTS_langues.py` (ElevenLabs,
modèle `eleven_v3`).

    python script_TTS_langues.py "<dossier du vault, ou d'une langue>"

- Clé API : variable `ELEVENLABS_API_KEY`, ou fichier `.env` à côté du script.
- **Idempotent** : une fois converti en `![...](audio/…)`, un terme n'est pas
  regénéré.
- ⚠️ Le `cache_key` n'inclut pas le voice_id : si tu **changes une voix**, purge
  le `.tts_audio_cache/` **et** les `audio/` de la langue avant de relancer,
  sinon les anciens clips (mauvaise voix) sont réutilisés.

### Mise en ligne
Le build learn-nebula clone ce repo et fait `git lfs pull --include=*.mp3`.
Ne pousse les mp3 en prod **qu'après** que la feature audio soit sur
learn-nebula `main`, sinon les `![](mp3)` s'affichent en images cassées.
