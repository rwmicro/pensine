# sources/tts — Génération audio de prononciation

Outils pour ajouter des clips de prononciation aux notes de langues
(`Social Sciences/Languages - Dialects/`), rendus en lecteurs audio sur le site
learn-nebula. Voir aussi la section « Prononciation audio » de
[`sources/CLAUDE.md`](../CLAUDE.md).

## Prérequis

```
pip install elevenlabs langdetect
```

Clé API ElevenLabs, dans l'ordre de priorité :
1. variable d'environnement `ELEVENLABS_API_KEY` (à utiliser en **Claude Code
   online** : la définir comme secret d'environnement) ;
2. sinon un fichier `.env` à côté des scripts (ligne `ELEVENLABS_API_KEY=...`).

Le `.env` est **gitignoré** — ne jamais committer la clé.

## Workflow (2 étapes)

### 1. Surligner les termes — `highlighter.py`
Ajoute `==terme::code==` dans les tableaux (colonne nommée par la langue pour les
langues latines ; extraction par script Unicode pour arabe/mandarin/hindi/tamoul).
Pointe-le sur le dossier des langues :

```
python highlighter.py "../../Social Sciences/Languages - Dialects"           # dry-run
python highlighter.py "../../Social Sciences/Languages - Dialects" --apply   # écrit
```

Idempotent : les cellules déjà surlignées ou déjà converties (`![...]`) sont
ignorées — on peut donc le relancer après avoir ajouté une nouvelle langue.

Tableaux à en-tête sémantique (idiomes, `Formule`, conjugaisons…) : non captés,
à surligner à la main si besoin. Ajouter une langue = une ligne dans `CONFIG`.

### 2. Générer l'audio — `script_TTS_langues.py`
Remplace chaque `==terme::code==` par `![terme](audio/xxx.mp3)` et écrit le mp3
dans un sous-dossier `audio/` à côté de la note (chemin note-relative).

```
python script_TTS_langues.py "../../Social Sciences/Languages - Dialects/Arabe-Standard"
python script_TTS_langues.py --list-voices     # lister les voix du compte
```

- Modèle : `eleven_v3`. Voix par langue dans le dict `LANGUAGES` du script.
- Idempotent (un terme déjà converti n'est pas regénéré).
- Cache maître local `.tts_audio_cache/` (gitignoré).
- **Attention** : le `cache_key` n'inclut pas le voice_id — si tu changes une
  voix, purge le `.tts_audio_cache/` **et** les `audio/` de la langue avant de
  relancer, sinon les anciens clips (mauvaise voix) sont réutilisés.

## Mise en ligne
mp3 stockés en git-lfs (`*.mp3` dans `.gitattributes`), à committer. Le build
learn-nebula fait `git lfs pull --include=*.mp3` (déjà sur `main`), donc pousser
pensine publie les audios.
