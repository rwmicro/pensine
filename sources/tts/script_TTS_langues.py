"""
script_TTS_langues.py
=====================
Scanne un vault Obsidian, repère les termes surlignés (==texte==), génère un
audio via ElevenLabs, puis REMPLACE le surlignage par une image markdown audio
compatible avec la feature de prononciation du site learn-nebula.

Syntaxe dans tes notes :
    ==hola==              -> langue auto-détectée (peu fiable sur les mots courts)
    ==hola::es==          -> langue forcée (recommandé)
    ==keefak::ar-lb==     -> dialecte forcé (libanais)
    ==hola::es:female==   -> langue + voix (male / female)

Après traitement, le surlignage devient une image markdown audio :
    ![hola](audio/es_male_ab12cd34ef56.mp3)
Sur learn-nebula, rehypeVaultAssets (lib/markdown.ts) transforme toute image
markdown à extension audio en lecteur ▶ « .pron », avec le alt (« hola ») comme
label. Le .mp3 est rangé dans un sous-dossier `audio/` À CÔTÉ de la note (chemin
note-relative), donc résolu par resolveVaultAsset au build (content/posts/…).

⚠ Pense à COMMITTER les dossiers `audio/` + les .mp3 dans le repo du vault : le
  site clone ce repo dans content/posts/ (scripts/fetch-notes.mjs). Un .mp3 non
  commité = lecteur cassé en ligne.

Modèle : eleven_v3 (74 langues). Non gérés quel que soit le modèle :
  ouïghour, kabyle, hakka, tok pisin. (Sambas -> forcer ::ms, Darija -> ::ar.)

Installation :
    pip install elevenlabs langdetect --break-system-packages

Utilisation :
    export ELEVENLABS_API_KEY="..."
    python script_TTS_langues.py "/chemin/vers/ton/vault"
"""

import os
import re
import sys
import shutil
import hashlib
from pathlib import Path

from elevenlabs import ElevenLabs
from langdetect import detect, DetectorFactory, LangDetectException

DetectorFactory.seed = 0  # résultats reproductibles

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Voix ElevenLabs par langue.
#   • La clé = le code que tu écris dans tes notes : ==mot::CODE==
#     (ISO 639-1, ou code perso comme "ar-lb" pour un dialecte).
#   • Colle tes voice IDs (onglet « Voices » de ton compte ElevenLabs).
#   • eleven_v3 est multilingue : UNE bonne voix sait lire plusieurs langues.
#     Réutilise le même ID partout, ou mets une voix par langue. Ce qui reste à
#     None retombe sur FALLBACK_VOICE ; si lui aussi est None, la langue est
#     ignorée (avec un avertissement).
LANGUAGES = {
    # --- déjà configurées ---
    # IDs d'origine BIDONS (404 voice_not_found) -> None => voix de secours réelle.
    # Remplace par de vrais voice IDs si tu en as de dédiés (puis relance la langue).
    "fr":    {"male": "ohItIVrXTBI80RrUECOD", "female": "FvmvwvObRqIHojkEGh5N"},  # (aucune note française dans le vault)
    "es":    {"male": "Nh2zY9kknu6z4pZy6FhD", "female": "KHCvMklQZZo0O30ERnVn"},  # Espagnol -> FALLBACK
    "id":    {"male": "RWiGLY9uXI70QL540WNd", "female": "iWydkXKoiVtvdn4vLKp9"},  # Indonésien -> FALLBACK
    "ar-lb": {"male": "x2bzUhGNyEnNbV8lRrVX", "female": "a1KZUXKFVFDOb33I1uqr"},  # Libanais -> FALLBACK (::ar-lb)
    "en": {"male": "7cOBG34AiHrAzs842Rdi", "female": "BAdH0bMfq6VleQGLXj38"},  # Anglais
    "de": {"male": "muSxG4dqYjBCkbpXqbEl", "female": "uvysWDLbKpA4XvpD3GI6"},  # Allemand
    "tr": {"male": "mF7tIc9VLrznhGooGjaT", "female": "axtmxCPnqPghs9C5SjJ8"},  # Turc
    "az": {"male": "mF7tIc9VLrznhGooGjaT", "female": "axtmxCPnqPghs9C5SjJ8"},  # Azéri  (débloqué par eleven_v3)
    "ro": {"male": "OlBp4oyr3FBAGEAtJOnU", "female": "3z9q8Y7plHbvhDZehEII"},  # Roumain
    "hi": {"male": "zgqefOY5FPQ3bB7OZTVR", "female": "1qEiC6qsybMkmnNdVMbK"},  # Hindi
    "ta": {"male": "ZhJ5LanYnCmLKQUXvsV7", "female": "gCr8TeSJgJaeaIoV4RWH"},  # Tamoul
    "ms": {"male": "NpVSXJvYSdIbjOaMbShj", "female": "qAJVXEQ6QgjOQ25KuoU8"},  # Malais (et approx. Sambas via ::ms)
    "zh": {"male": "DowyQ68vDpgFYdWVGjc3", "female": "bhJUNIXWQQ94l8eI2VUf"},  # Mandarin
    "ar": {"male": "JjTirzdD7T3GMLkwdd3a", "female": "u0TsaWvt0v8migutHM3M"},  # Arabe standard (Darija approx. via ::ar)
}

# Voix de secours multilingue : utilisée dès qu'une langue n'a pas de voix
# dédiée. Colle-y un seul ID et la plupart des langues ci-dessus marchent tout
# de suite (le modèle gère la prononciation selon le texte).
FALLBACK_VOICE = {"male": "7cOBG34AiHrAzs842Rdi", "female": "BAdH0bMfq6VleQGLXj38"}

DEFAULT_GENDER = "male"
MODEL_ID = "eleven_v3"           # 74 langues
OUTPUT_FORMAT = "mp3_44100_128"  # format valide pour l'API (pas un nom de fichier)

# Sous-dossier créé À CÔTÉ de chaque note pour ses clips (chemin note-relative,
# résolu par le site). Ne pas confondre avec le cache maître ci-dessous.
AUDIO_SUBFOLDER = "audio"
# Cache maître (à la racine du scan) : une seule copie par mot/langue/voix, pour
# ne pas rappeler l'API quand le même terme réapparaît dans une autre note.
MASTER_CACHE_DIR = ".tts_audio_cache"

# Surlignage à traiter : ==texte== ou ==texte::langue==.
# [^=\n] empêche le match de traverser un autre ==...== (pas de débordement) et
# le limite à une ligne. Pas besoin de garde d'idempotence : une fois converti
# en ![mot](audio/…), il n'y a plus de == à re-matcher.
PATTERN = re.compile(r"==([^=\n]+?)==")

def load_api_key() -> str | None:
    """Clé API ElevenLabs. Priorité à la variable d'env ELEVENLABS_API_KEY ;
    sinon on lit un fichier `.env` (ligne « ELEVENLABS_API_KEY=... ») à côté du
    script. Pratique ici : chaque commande shell repart d'un environnement neuf,
    donc un `export` d'une session précédente n'est pas conservé."""
    key = os.getenv("ELEVENLABS_API_KEY")
    if key:
        return key
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "ELEVENLABS_API_KEY":
                return value.strip().strip('"').strip("'")
    return None


API_KEY = load_api_key()
client = ElevenLabs(api_key=API_KEY)


# ---------------------------------------------------------------------------
# Détection de langue + synthèse vocale
# ---------------------------------------------------------------------------

def cache_key(text: str, lang: str, gender: str) -> str:
    # le genre fait partie de la clé : deux voix = deux audios distincts
    return hashlib.sha1(f"{lang}:{gender}:{text}".encode("utf-8")).hexdigest()[:12]


def detect_language(text: str) -> str | None:
    """Retourne un code langue supporté, ou None si non détectable/non supporté."""
    try:
        code = detect(text)
    except LangDetectException:
        return None
    return code if code in LANGUAGES else None


def parse_override(raw: str) -> tuple[str, str | None, str]:
    """Découpe le contenu d'un ==...==.

    Renvoie (text, lang, gender) où :
        - lang = None  -> détection automatique
        - gender in {"male", "female"} (DEFAULT_GENDER si non précisé/invalide)

    Formats reconnus : "texte", "texte::lang", "texte::lang:gender".
    """
    if "::" not in raw:
        return raw.strip(), None, DEFAULT_GENDER

    text, spec = raw.rsplit("::", 1)
    text = text.strip()
    spec = spec.strip()

    gender = DEFAULT_GENDER
    if ":" in spec:  # "lang:gender"
        lang, gender = (part.strip() for part in spec.split(":", 1))
        if gender.lower() not in ("male", "female"):
            gender = DEFAULT_GENDER
        gender = gender.lower()
    else:
        lang = spec

    return text, (lang or None), gender


def resolve_voice(lang: str, gender: str = DEFAULT_GENDER) -> str | None:
    """Voice ID pour (lang, gender). Repli : genre demandé -> autre genre de la
    même langue -> FALLBACK_VOICE. Renvoie None si rien n'est configuré."""
    for source in (LANGUAGES.get(lang, {}), FALLBACK_VOICE):
        vid = source.get(gender) or source.get("male") or source.get("female")
        if vid:
            return vid
    return None


def synthesize(text: str, lang: str, gender: str = DEFAULT_GENDER) -> bytes:
    voice_id = resolve_voice(lang, gender)
    if voice_id is None:
        raise RuntimeError(f"aucune voix configurée pour « {lang} »")
    audio_chunks = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=MODEL_ID,
        output_format=OUTPUT_FORMAT,
    )
    return b"".join(audio_chunks)  # convert() renvoie un générateur de bytes


def escape_alt(text: str) -> str:
    """Neutralise ce qui casserait la syntaxe ![alt](...) (crochets)."""
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def list_voices() -> None:
    """Liste les voix du compte avec leur catégorie. Les voix « premade » (voix
    par défaut d'ElevenLabs) sont utilisables via l'API même en plan gratuit ;
    les voix « library » (Voice Library) exigent un plan payant -> erreur 402."""
    try:
        resp = client.voices.get_all()
    except Exception:
        resp = client.voices.search()  # nom de méthode selon la version du SDK
    voices = getattr(resp, "voices", resp)
    rows = [
        (getattr(v, "category", "?") or "?",
         getattr(v, "name", "") or "",
         getattr(v, "voice_id", "") or "")
        for v in voices
    ]
    rows.sort(key=lambda r: (r[0] != "premade", r[1].lower()))  # premade d'abord
    print(f"{len(rows)} voix sur ton compte :\n")
    for cat, name, vid in rows:
        free = "✅ API gratuite" if cat == "premade" else "💳 plan payant"
        print(f"  {vid:24}  {cat:12}  {free}  {name}")


# ---------------------------------------------------------------------------
# Traitement d'une note
# ---------------------------------------------------------------------------

def process_file(md_path: Path, master_dir: Path) -> bool:
    content = md_path.read_text(encoding="utf-8")
    note_audio_dir = md_path.parent / AUDIO_SUBFOLDER
    changed = False

    def replace(match: re.Match) -> str:
        nonlocal changed
        text, lang, gender = parse_override(match.group(1))

        if lang is None:
            # auto-détection : peu fiable sur les mots courts (ex. "Hola"->tr),
            # donc restreinte aux langues explicitement configurées.
            lang = detect_language(text)
            if not lang:
                print(f"  ⚠ Langue non détectée pour « {text} » — précise-la avec ::lang. Ignoré.")
                return match.group(0)  # inchangé

        if resolve_voice(lang, gender) is None:
            print(f"  ⚠ Aucune voix configurée pour « {lang} » (« {text} »), ignoré.")
            return match.group(0)  # inchangé

        key = cache_key(text, lang, gender)
        filename = f"{lang}_{gender}_{key}.mp3"
        master = master_dir / filename
        note_clip = note_audio_dir / filename

        # 1) master : généré une seule fois par (mot, langue, voix). Écrit tout
        #    de suite sur le disque -> rien à perdre si le script plante ensuite.
        if not master.exists():
            print(f"  🎙 Génération audio [{lang}/{gender}] « {text} »")
            try:
                audio_bytes = synthesize(text, lang, gender)
            except Exception as exc:  # réseau, quota, timeout ElevenLabs...
                print(f"  ✗ Échec de la génération pour « {text} » : {exc}")
                return match.group(0)  # inchangé, on réessaiera au prochain run
            master.write_bytes(audio_bytes)

        # 2) copie note-relative : le site la résout en <noteDir>/audio/<fichier>.
        if not note_clip.exists():
            note_audio_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(master, note_clip)

        changed = True
        # image markdown audio -> lecteur .pron sur le site, « text » en label.
        return f"![{escape_alt(text)}]({AUDIO_SUBFOLDER}/{filename})"

    new_content = PATTERN.sub(replace, content)
    if changed:
        md_path.write_text(new_content, encoding="utf-8")
    return changed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]

    if not API_KEY:
        env_file = Path(__file__).resolve().parent / ".env"
        print("⚠ Clé API manquante. Deux options :\n"
              "   • export ELEVENLABS_API_KEY=\"ta_clé\"  (même ligne que la commande), ou\n"
              f"   • crée le fichier {env_file} contenant :\n"
              "        ELEVENLABS_API_KEY=ta_clé")
        sys.exit(1)

    if args == ["--list-voices"]:
        list_voices()
        return

    if len(args) != 1:
        print("Usage: python script_TTS_langues.py /chemin/vers/vault\n"
              "       python script_TTS_langues.py --list-voices")
        sys.exit(1)

    vault = Path(args[0]).expanduser().resolve()
    if not vault.is_dir():
        print(f"Dossier introuvable : {vault}")
        sys.exit(1)

    master_dir = vault / MASTER_CACHE_DIR
    master_dir.mkdir(exist_ok=True)

    md_files = [
        p for p in vault.rglob("*.md")
        if ".obsidian" not in p.parts
    ]

    any_changed = False
    for md_path in md_files:
        rel = md_path.relative_to(vault)
        if process_file(md_path, master_dir):
            print(f"✔ Mis à jour : {rel}")
            any_changed = True

    if not any_changed:
        print("Rien à faire : aucun nouveau ==texte== trouvé.")


if __name__ == "__main__":
    main()
