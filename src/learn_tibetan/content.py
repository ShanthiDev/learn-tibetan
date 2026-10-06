"""Build web/src/content/curriculum.json from content/*.toml.

Only orthography, grouping and pedagogy live in the TOML sources. Wylie, TZ pronunciation and
syllable analysis are generated here with the reference engine, never maintained by hand.
"""

from __future__ import annotations

import json
import tomllib
import unicodedata
from pathlib import Path

from learn_tibetan.phonetics import tz, wylie

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"
OUT = ROOT / "web/src/content/curriculum.json"
TZ_VARIANT = "tz-aktuell"
WYLIE_VERSION = "transfer-2026-10-06"  # wylie.py carries no version of its own


def item_id(prefix: str, w: str) -> str:
    return f"{prefix}-{w.replace(chr(39), '_')}"  # 'a -> l-_a


def analysis(tibetan: str) -> dict:
    a = tz.analyse(tibetan)
    return {"prefix": a["prefix"], "superscript": a["superscript"], "root": a["root"],
            "subscripts": a["subs"], "vowel": a["vowel"], "suffix": a["suffix"],
            "postsuffix": a["postsuffix"]}


def make_item(kind: str, tibetan: str, order: int, **extra) -> dict:
    tibetan = unicodedata.normalize("NFC", tibetan)
    w = wylie.syllable(tibetan)
    item = {"id": item_id("l" if kind == "letter" else "v", w), "kind": kind, "tibetan": tibetan,
            "wylie": w, "tz": tz.render(tibetan, TZ_VARIANT), "order": order}
    item.update({k: v for k, v in extra.items() if v is not None})
    item["analysis"] = analysis(tibetan)
    return item


def build(content_dir: Path = CONTENT) -> dict:
    src = tomllib.loads((content_dir / "curriculum.toml").read_text(encoding="utf-8"))
    audio = tomllib.loads((content_dir / "audio.toml").read_text(encoding="utf-8")).get("clips", [])

    groups, letters = [], []
    for g_order, g in enumerate(src["groups"], 1):
        ids = []
        for entry in g["letters"]:
            it = make_item("letter", entry["tibetan"], len(letters) + 1, groupId=g["id"],
                           devanagari=entry.get("devanagari"), devanagariNote=entry.get("devanagari_note"))
            it["baseId"], it["vowel"] = it["id"], "a"
            letters.append(it)
            ids.append(it["id"])
        groups.append({"id": g["id"], "order": g_order, "labelDe": g["label_de"],
                       "linguistic": g.get("linguistic"), "itemIds": ids})

    vowels = src["vowels"]
    forms = []
    for base in letters:
        for v in vowels:
            if v["sign"]:
                forms.append(make_item("vowel-form", base["tibetan"] + v["sign"], 0,
                                       groupId=base["groupId"], baseId=base["id"], vowel=v["id"]))
    for n, it in enumerate(forms, len(letters) + 1):
        it["order"] = n
    items = letters + forms

    by_id = {it["id"]: it for it in items}
    for clip in audio:
        if clip.get("status") != "rejected":
            by_id[clip["item"]]["audio"] = {k: clip.get(k) for k in ("file", "source", "dialect", "status")}

    lessons = []
    for r, g in enumerate(groups, 1):
        ids = g["itemIds"]
        lessons.append({"id": f"r{r}-tw", "chapter": 2, "titleDe": f"{g['labelDe']}: Zeichen → Wylie",
                        "introItemIds": ids, "newItemIds": ids, "modes": ["tib-wylie"]})
        lessons.append({"id": f"r{r}-wt", "chapter": 3, "titleDe": f"{g['labelDe']}: Wylie → Zeichen",
                        "newItemIds": ids, "modes": ["wylie-tib"]})

    def family(base_ids: list[str]) -> list[str]:
        return [it["id"] for it in items if it.get("baseId") in base_ids]

    first4 = [i for g in groups[:4] for i in g["itemIds"]]
    all_letters = [it["id"] for it in letters]
    both = ["tib-wylie", "wylie-tib"]
    lessons += [
        {"id": "v1", "chapter": 4, "titleDe": "Vokale auf ཀ", "introItemIds": family(["l-ka"]),
         "newItemIds": family(["l-ka"]), "modes": both},
        # Generalisation lessons: reading direction only and a lighter mastery bar (D-011),
        # otherwise 80/150 forms x 2 directions x box 3 would take many hundred answers.
        {"id": "v2", "chapter": 4, "titleDe": "Vokale: erste vier Reihen", "newItemIds": family(first4),
         "modes": ["tib-wylie"], "mastery": {"box": 2, "share": 0.8}},
        {"id": "v3", "chapter": 4, "titleDe": "Vokale: alle Buchstaben", "newItemIds": family(all_letters),
         "modes": ["tib-wylie"], "mastery": {"box": 1, "share": 0.8}},
        {"id": "a1", "chapter": 5, "titleDe": "Hören: erste vier Reihen", "newItemIds": first4, "modes": ["audio-tib"]},
        {"id": "a2", "chapter": 5, "titleDe": "Hören: restliche Buchstaben",
         "newItemIds": [i for i in all_letters if i not in first4], "modes": ["audio-tib"]},
        {"id": "a3", "chapter": 5, "titleDe": "Hören: Vokale auf ཀ", "newItemIds": family(["l-ka"]), "modes": ["audio-tib"]},
    ]

    return {
        "meta": {"engine": {"tz": tz.VERSION, "wylie": WYLIE_VERSION, "tzVariant": TZ_VARIANT}},
        "alphabetNoteDe": src["alphabet"]["note_de"],
        "vowels": [{"id": v["id"], "sign": v["sign"], "nameDe": v["name_de"]} for v in vowels],
        "groups": groups,
        "items": items,
        "lessons": lessons,
        "confusables": src["confusables"],
        "audioEquivalent": src["audio_equivalent"]["groups"],
    }


def write(out: Path = OUT) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out
