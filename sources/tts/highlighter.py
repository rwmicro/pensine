"""
highlighter.py — ajoute des surlignages ==terme::lang== dans les notes de langue
pour que script_TTS_langues.py les convertisse ensuite en audio.

Stratégie (deux signaux fiables) :
  • Langues à écriture propre (arabe/han/devanagari/tamoul) : on repère la cible
    par son SCRIPT Unicode dans chaque cellule de tableau. Fiable et auto-exclut
    translittérations (latines), gloses françaises et IPA.
  • Langues latines : on ne touche QUE la colonne dont l'en-tête nomme la langue
    (ex. « Espagnol », « Sambas »). Les colonnes Sens/Prononciation/IPA sont donc
    ignorées. Si aucune colonne ne correspond, le tableau est laissé intact.

Ne traite QUE les tableaux markdown (le corps en prose est laissé tel quel).
Idempotent : une cellule contenant déjà == ou ![ est ignorée.

Usage : pointe-le sur le dossier « Languages - Dialects » (il déduit la langue
du nom du dossier de 1er niveau). Dry-run par défaut ; --apply pour écrire.

    python highlighter.py "/.../Languages - Dialects"           # dry-run
    python highlighter.py "/.../Languages - Dialects" --apply   # écrit
"""
import re
import sys
from pathlib import Path

# dossier -> (code langue, [mots-clés d'en-tête | None si script], type de script)
CONFIG = {
    "Allemand":       ("de",    ["allemand", "deutsch"],              "latin"),
    "Anglais":        ("en",    ["anglais", "english"],               "latin"),
    "Azéri":          ("az",    ["azéri", "azeri", "azerbaïdjanais"], "latin"),
    "Espagnol":       ("es",    ["espagnol"],                          "latin"),
    "Indonésien":     ("id",    ["indonésien", "indonesien"],          "latin"),
    "Malais":         ("ms",    ["malais"],                            "latin"),
    "Roumain":        ("ro",    ["roumain"],                           "latin"),
    "Sambas":         ("ms",    ["sambas"],                            "latin"),
    "Turc":           ("tr",    ["turc", "türkçe", "turkce"],          "latin"),
    "Arabe-Libanais": ("ar-lb", None,                                  "arabic"),
    "Arabe-Standard": ("ar",    None,                                  "arabic"),
    "Darija":         ("ar",    None,                                  "arabic"),
    "Mandarin":       ("zh",    None,                                  "han"),
    "Hindi":          ("hi",    None,                                  "deva"),
    "Tamoul":         ("ta",    None,                                  "tamil"),
    # NON traitées (TTS impossible) : Hakka-Khek, Kabyle, Ouighour, Tok Pisin
}

SCRIPT_RANGES = {
    "arabic": "؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿",
    "han":    "㐀-䶿一-鿿",
    "deva":   "ऀ-ॿ",
    "tamil":  "஀-௿",
}

PAREN = re.compile(r"\([^)]*\)")           # translittérations / notes entre ()
HAS_LETTER = re.compile(r"[^\W\d_]", re.UNICODE)
ROW = re.compile(r"^\s*\|.*\|\s*$")
SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def already(cell: str) -> bool:
    return "==" in cell or "![" in cell


def highlight_latin(cell: str, lang: str) -> str:
    if already(cell):
        return cell
    clean = PAREN.sub("", cell).strip()
    if not clean or not HAS_LETTER.search(clean):
        return cell
    parts = [p.strip() for p in re.split(r"\s*/\s*", clean)]
    out = [f"=={p}::{lang}==" if p and HAS_LETTER.search(p) else p for p in parts]
    return " / ".join(out)


def highlight_script(cell: str, lang: str, script: str) -> str:
    if already(cell):
        return cell
    rng = SCRIPT_RANGES[script]
    # une "unité" = suite de caractères du script, espaces internes tolérés
    run = re.compile(rf"[{rng}]+(?:[\s‌‍]+[{rng}]+)*")
    return run.sub(lambda m: f"=={m.group(0).strip()}::{lang}==", cell)


def target_columns(header: list[str], keywords) -> list[int]:
    kws = [k.lower() for k in keywords]
    return [i for i, h in enumerate(header) if any(k in h.lower() for k in kws)]


def process(text: str, lang: str, keywords, script: str) -> tuple[str, int]:
    lines = text.split("\n")
    n = len(lines)
    added = 0
    i = 0
    while i < n:
        if ROW.match(lines[i]) and i + 1 < n and SEP.match(lines[i + 1]):
            header = cells(lines[i])
            cols = None if script != "latin" else target_columns(header, keywords)
            j = i + 2
            while j < n and ROW.match(lines[j]) and not SEP.match(lines[j]):
                cs = cells(lines[j])
                for k, c in enumerate(cs):
                    if script == "latin":
                        new = highlight_latin(c, lang) if (cols and k in cols) else c
                    else:
                        new = highlight_script(c, lang, script)
                    if new != c:
                        added += new.count("==") // 2 - c.count("==") // 2
                        cs[k] = new
                lines[j] = "| " + " | ".join(cs) + " |"
                j += 1
            i = j
        else:
            i += 1
    return "\n".join(lines), added


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    root = Path(args[0]).expanduser().resolve()

    total_terms = 0
    changed_files = 0
    for md in sorted(root.rglob("*.md")):
        parts = md.relative_to(root).parts
        lang_folder = parts[0] if len(parts) > 1 else None
        cfg = CONFIG.get(lang_folder)
        if cfg is None:
            continue
        lang, keywords, script = cfg
        text = md.read_text(encoding="utf-8")
        new, added = process(text, lang, keywords, script)
        if added:
            total_terms += added
            changed_files += 1
            print(f"  +{added:3}  {md.relative_to(root)}")
            if apply:
                md.write_text(new, encoding="utf-8")

    mode = "APPLIQUÉ" if apply else "DRY-RUN (rien écrit)"
    print(f"\n[{mode}] {changed_files} fichiers, {total_terms} surlignages ajoutés.")


if __name__ == "__main__":
    main()
