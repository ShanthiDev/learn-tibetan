"""Exploratory Tibetan -> German (TZ-style) phonetic generator.

Research code, not part of the Reader/Workbench. Resolution order per syllable:

1. curated override (reviewed by hand, see overrides.json)
2. Sanskrit/mantra exception lexicon (built in + mapping ``inferred_exception``)
3. observed TZ evidence from the v0.2 mapping, after OCR-noise filtering
4. orthographic rule engine (Tibetan syllable structure -> TZ spelling)
5. Sanskrit transliteration rules for syllables that are not valid Tibetan

Every emitted syllable carries its origin so gaps and guesses stay visible.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
MAPPING = REPOSITORY / "data/reference_phonetics/TZ_tibetan_phonetics_mapping_v0.2_resolved.json"
OVERRIDES = HERE / "overrides.json"

TSHEG = "་"
# shad, double shad, gter tsheg, rin chen spungs shad and similar phrase breaks
BREAKS = set("།༎༏༐༑༒༔༈")
SKIP = set("༄༅༆༇༉༊༓༺༻༼༽") | set(
    chr(c) for c in range(0x0F15, 0x0F40) if chr(c) not in "\u0f0b")  # yig mgo, brackets, digits

# ---------------------------------------------------------------------------
# Tibetan letters
# ---------------------------------------------------------------------------

BASE = {chr(c): chr(c) for c in range(0x0F40, 0x0F6D)}
SUB = {chr(c): chr(c - 0x50) for c in range(0x0F90, 0x0FBD)}  # subjoined -> base
SUB["ྺ"] = "ཝ"  # fixed-form wa
SUB["ྻ"] = "ཡ"  # fixed-form ya
SUB["ྼ"] = "ར"  # fixed-form ra
VOWELS = {"ི": "i", "ུ": "u", "ེ": "e", "ོ": "o", "ྀ": "i"}
SANSKRIT_MARKS = set("ཱཱཱིུྲྀཷླྀཹཻཽཾཿ྄ཱྀྂྃ")
SANSKRIT_MARKS.add("\u0f80")  # reversed gigu: vocalic r/l (མྲྀ mṛ)
SANSKRIT_LETTERS = set("\u0f4a\u0f4b\u0f4c\u0f4e\u0f65\u0f69\u0f6a\u0f9a\u0f9b\u0f9c\u0f9e\u0fb5")  # retroflex, ssa, kssa

PREFIXES = {
    "ག": set("ཅཉཏདནཙཞཟཡཤས"),
    "ད": set("ཀགངཔབམ"),
    "བ": set("ཀགངཅཉཏདནཙཞཟཤས"),
    "མ": set("ཁགངཆཇཉཐདནཚཛ"),
    "འ": set("ཁགཆཇཐདཕབཚཛ"),
}
SUFFIXES = set("གངདནབམའརལས")
POSTSUFFIXES = set("སད")

# Tibetan consonant -> (TZ onset). Profile "hayagriva": aspiration written as h.
ONSET = {
    "ཀ": "k", "ཁ": "kh", "ག": "g", "ང": "ng",
    "ཅ": "tsch", "ཆ": "tsch", "ཇ": "dsch", "ཉ": "ny",
    "ཏ": "t", "ཐ": "th", "ད": "d", "ན": "n",
    "པ": "p", "ཕ": "ph", "བ": "b", "མ": "m",
    "ཙ": "ts", "ཚ": "tsh", "ཛ": "dz", "ཝ": "w",
    "ཞ": "sch", "ཟ": "s", "འ": "", "ཡ": "y",
    "ར": "r", "ལ": "l", "ཤ": "sch", "ས": "s",
    "ཧ": "h", "ཨ": "",
}
YATA = {"ཀ": "ky", "ཁ": "khy", "ག": "gy", "པ": "tsch", "ཕ": "tsch", "བ": "dsch", "མ": "ny", "ཧ": "hy"}
RATA = {
    "ཀ": "tr", "ཏ": "tr", "པ": "tr", "ཁ": "thr", "ཐ": "thr", "ཕ": "thr",
    "ག": "dr", "ད": "dr", "བ": "dr", "ས": "s", "ཧ": "hr", "མ": "m", "ཤ": "schr", "ཙ": "ts",
}
LATA = {"ཀ": "l", "ག": "l", "བ": "l", "ར": "l", "ས": "l", "ཟ": "d"}
FINAL = {"ག": "g", "ང": "ng", "བ": "b", "མ": "m", "ར": "r", "ལ": "l", "ན": "n", "ད": "", "ས": "", "འ": ""}
UMLAUT = {"a": "ä", "o": "ö", "u": "ü", "i": "i", "e": "e"}

# ---------------------------------------------------------------------------
# Sanskrit / mantra layer
# ---------------------------------------------------------------------------

MANTRA_EXCEPTIONS = {
    "ཨོཾ": "OM", "ཨོྃ": "OM", "ཧཱུཾ": "HUNG", "ཧཱུྃ": "HUNG", "ཧཱུྂ": "HUNG", "ཧཱུ": "HUNG",
    "ཨཱཿ": "AH", "ཨཱ": "AH", "ཨ": "A", "ཕཊ": "PHE", "ཕཊ྄": "PHE", "ཕཱཊ": "PHE",
    "ཧྲཱིཿ": "HRIH", "ཧྲཱི": "HRIH", "ཧྲཱིཾ": "HRING",
    "བཛྲ": "BENDSA", "བཛྲཱ": "BENDSA", "སྭཱཧཱ": "SOHA", "སྭཱ": "SO", "ཧཱ": "HA",
    "པདྨ": "PEMA", "པདྨཱ": "PEMA", "ཛཿ": "DZA", "བཾ": "BAM", "ཧོཿ": "HO",
    "ཧ": "HA", "ཧི": "HI", "ཧུ": "HU", "ཧེ": "HE", "ཧོ": "HO",
    "ཀྲོ": "KRO", "དྷ": "DHA", "ཨཿ": "AH", "རཀྵ": "RAKSCHA", "ཀྵ": "KSCHA",
    "ཏྲཱཾ": "TRAM", "ཛྙཱ": "DSCHNYA", "ཛྙ": "DSCHNYA", "ཤྲཱི": "SCHRI", "ཧྲི": "HRI",
    "སྭཧཱ": "SOHA", "པདྨེ": "PEME", "སརྦ": "SARWA", "སརྦ྄": "SARWA", "ཝ": "WA", "ཡ": "YA", "གྲཱི": "GRI",
}
# Tibetan words whose TZ reading is a fixed Sanskrit loan pronunciation
TIBETAN_WORD_EXCEPTIONS = {
    "པདྨ": "pema", "པདྨའི": "pemä", "བཻ": "be", "པདྨས": "pemä", "པདྨོ": "pemo", "བཛྲ": "bendsa",
}

SKT_CONS = {
    "ཀ": "K", "ཁ": "KH", "ག": "G", "གྷ": "GH", "ང": "NG", "ཙ": "TS", "ཚ": "TSH", "ཛ": "DS", "ཆ": "TSCH",
    "ཛྷ": "DSH", "ཉ": "NY", "ཊ": "T", "ཋ": "TH", "ཌ": "D", "ཌྷ": "DH", "ཎ": "N", "ཏ": "T",
    "ཐ": "TH", "ད": "D", "དྷ": "DH", "ན": "N", "པ": "P", "ཕ": "PH", "བ": "B", "བྷ": "BH",
    "མ": "M", "ཡ": "Y", "ར": "R", "ལ": "L", "ཝ": "W", "ཤ": "SCH", "ཥ": "SCH", "ས": "S",
    "ཧ": "H", "ཀྵ": "KSCH", "ཨ": "", "ཅ": "TSCH", "ཇ": "DSCH", "ཞ": "SCH", "ཟ": "S", "འ": "",
}
SKT_VOWEL = {
    "ཱ": "A", "ི": "I", "ཱི": "I", "ུ": "U", "ཱུ": "U", "ེ": "E",
    "ཻ": "AI", "ོ": "O", "ཽ": "AU", "ྀ": "I", "ཱྀ": "I",
    "ྲྀ": "RI", "ཷ": "RI", "ླྀ": "LI", "ཹ": "LI",
}


@dataclass
class SyllableResult:
    tibetan: str
    phonetic: str
    origin: str  # override | mantra_exception | observed_TZ | rule_tibetan | rule_sanskrit | unresolved
    note: str = ""


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def stacks(syllable: str) -> list[dict]:
    """Split a syllable into stacks: base letter + subjoined letters + marks."""
    out: list[dict] = []
    for ch in syllable:
        if ch in BASE:
            out.append({"letters": [ch], "vowel": None, "marks": []})
        elif ch in SUB and out:
            out[-1]["letters"].append(SUB[ch])
        elif ch in VOWELS and out:
            out[-1]["vowel"] = VOWELS[ch]
        elif out:
            out[-1]["marks"].append(ch)
        else:
            raise ValueError(f"cannot parse {syllable!r}")
    return out


def is_sanskrit(syllable: str) -> bool:
    if any(ch in SANSKRIT_MARKS for ch in syllable):
        return True
    if any(ch in SANSKRIT_LETTERS for ch in syllable):
        return True
    try:
        parsed = stacks(syllable)
    except ValueError:
        return True
    for st in parsed:
        letters = st["letters"]
        if len(letters) == 1:
            continue
        if not valid_tibetan_stack(letters):
            return True
    if sum(1 for st in parsed if st["vowel"]) > 1:
        # e.g. genitive "འི" after vowel "ོ" (པོའི) is fine; other double vowels are not
        rest = [st for st in parsed if st["vowel"]]
        if not (len(rest) == 2 and rest[1]["letters"] == ["འ"]):
            return True
    return False


SUPERSCRIPT_OK = {
    "ར": set("ཀགངཇཉཏདནབམཙཛ"),
    "ལ": set("ཀགངཅཇཏདཔབཧ"),
    "ས": set("ཀགངཉཏདནཔབམཙ"),
}
SUBSCRIPT_OK = {
    "ཡ": set("ཀཁགཔཕབམཧ"),
    "ར": set("ཀཁགཏཐདཔཕབམསཧཤཙ"),
    "ལ": set("ཀགབརསཟ"),
    "ཝ": set("ཀཁགཅཉཏདཙཚཞཟརལཤསཧཕཡ"),
}


def valid_tibetan_stack(letters: list[str]) -> bool:
    head, *rest = letters
    if head in SUPERSCRIPT_OK and rest and rest[0] in SUPERSCRIPT_OK[head]:
        root, subs = rest[0], rest[1:]
    else:
        root, subs = head, rest
    ok_subs = []
    for sub in subs:
        if sub in SUBSCRIPT_OK and root in SUBSCRIPT_OK[sub]:
            ok_subs.append(sub)
        elif sub == "ཝ" and ok_subs:  # e.g. གྲྭ
            ok_subs.append(sub)
        else:
            return False
    return len(ok_subs) <= 2


def analyse(syllable: str) -> dict:
    """Return prefix/superscript/root/subscripts/vowel/suffix/postsuffix/affix."""
    parsed = stacks(syllable)
    affix = None
    # genitive / terminative / connective particles fused with the syllable
    if len(parsed) >= 2 and parsed[-1]["letters"] == ["འ"] and parsed[-1]["vowel"] in {"i", "o", "u"}:
        affix = {"i": "i", "o": "o", "u": "u"}[parsed[-1]["vowel"]]
        parsed = parsed[:-1]
    elif len(parsed) >= 2 and parsed[-1]["letters"] == ["འ"] and parsed[-1]["vowel"] is None and len(parsed) >= 3:
        pass
    if affix is None and len(parsed) >= 3 and parsed[-2]["letters"] == ["འ"] and not parsed[-2]["vowel"] \
            and parsed[-1]["letters"][0] in {"ང", "མ"} and not parsed[-1]["vowel"]:
        affix = {"ང": "ang", "མ": "am"}[parsed[-1]["letters"][0]]  # concessive འང / alternative འམ
        parsed = parsed[:-2]
    root_index = None
    for i, st in enumerate(parsed):
        if len(st["letters"]) > 1 or st["vowel"]:
            root_index = i
            break
    n = len(parsed)
    if root_index is None:
        if n == 1:
            root_index = 0
        elif n == 2:
            a, b = (p["letters"][0] for p in parsed)
            root_index = 1 if (a in PREFIXES and b in PREFIXES[a] and b not in SUFFIXES) else 0
        elif n == 3:
            a, b, c = (p["letters"][0] for p in parsed)
            if a in PREFIXES and b in PREFIXES[a]:
                root_index = 0 if (c == "ས" and b in "གངབམ" and a not in PREFIXES) else 1
            else:
                root_index = 0
        elif n == 4:
            root_index = 1
        else:
            raise ValueError(f"unexpected syllable length {syllable!r}")
    root_stack = parsed[root_index]
    pre = parsed[:root_index]
    post = parsed[root_index + 1:]
    if len(pre) > 1 or any(len(p["letters"]) > 1 or p["vowel"] for p in pre + post):
        raise ValueError(f"unexpected structure {syllable!r}")
    prefix = pre[0]["letters"][0] if pre else None
    if prefix and prefix not in PREFIXES:
        raise ValueError(f"invalid prefix {syllable!r}")
    letters = root_stack["letters"]
    superscript = None
    if len(letters) > 1 and letters[0] in SUPERSCRIPT_OK and letters[1] in SUPERSCRIPT_OK[letters[0]]:
        superscript, letters = letters[0], letters[1:]
    root, subs = letters[0], [s for s in letters[1:] if s != "ཝ"]
    suffix = post[0]["letters"][0] if post else None
    postsuffix = post[1]["letters"][0] if len(post) > 1 else None
    if len(post) > 2 or (suffix and suffix not in SUFFIXES) or (postsuffix and postsuffix not in POSTSUFFIXES):
        raise ValueError(f"invalid suffix {syllable!r}")
    return {
        "prefix": prefix, "superscript": superscript, "root": root, "subs": subs,
        "vowel": root_stack["vowel"] or "a", "suffix": suffix, "postsuffix": postsuffix, "affix": affix,
    }


# ---------------------------------------------------------------------------
# Rule engines
# ---------------------------------------------------------------------------


def onset(a: dict) -> str:
    root, subs, prefix = a["root"], a["subs"], a["prefix"]
    if subs and subs[0] == "ཡ" and root == "བ" and prefix == "ད":
        return "y"  # དབྱིངས ying, དབྱངས yang
    if subs and subs[0] == "ཡ" and root in YATA:
        return YATA[root]
    if subs and subs[0] == "ར" and root in RATA:
        return RATA[root]
    if subs and subs[0] == "ལ" and root in LATA:
        return LATA[root]
    if root == "བ" and prefix == "ད" and not a["superscript"]:
        return "w"  # དབང wang, དབུ u
    if root == "ཧ" and a["superscript"] == "ལ":
        return "lh"
    return ONSET[root]


def rule_tibetan(syllable: str, particle_context: bool = False) -> str:
    a = analyse(syllable)
    head = onset(a)
    if a["root"] == "བ" and not a["prefix"] and not a["superscript"] and not a["subs"] and particle_context:
        head = "w"
    if head == "w" and a["root"] == "བ" and a["prefix"] == "ད" and a["vowel"] in {"u", "o"}:
        head = ""  # དབུ -> u, དབོ -> o
    vowel = a["vowel"]
    suffix = a["suffix"]
    coda = ""
    if suffix in {"ད", "ས", "ན", "ལ"}:
        vowel = UMLAUT[vowel]
    if suffix:
        coda = FINAL[suffix]
    if suffix == "ས" and a["postsuffix"] is None:
        coda = ""
    if a["affix"] == "i":
        vowel = UMLAUT[vowel] if vowel in "aou" else vowel
        if vowel == "e" and not coda:
            pass
    elif a["affix"] == "o":
        coda += "-o"
    elif a["affix"] == "u":
        coda += "-u"
    elif a["affix"] in {"ang", "am"}:
        coda += "-" + a["affix"]
    if vowel == "e" and head == "" and not coda:
        return "e"
    return head + vowel + coda


PARTICLES_WITH_WA = {"བ", "བར", "བའི", "བས", "བོ", "བོའི", "བའོ", "བོར", "བོས", "བའམ", "བའང"}


def split_glued(syllable: str) -> list[str] | None:
    """Split a token like གཡསགཉིས (missing tsheg) into two well-formed Tibetan syllables."""
    for cut in range(2, len(syllable) - 1):
        left, right = syllable[:cut], syllable[cut:]
        if not ("\u0f40" <= right[0] <= "\u0f6c"):
            continue
        try:
            if len(stacks(left)) >= 1 and not is_sanskrit(left) and not is_sanskrit(right):
                analyse(left), analyse(right)
                return [left, right]
        except (ValueError, KeyError):
            continue
    return None


def rule_sanskrit(syllable: str) -> str:
    """Transliterate a Sanskrit unit in Tibetan script into TZ-like mantra capitals.

    Every cluster (base letter + subjoined letters + vowel/marks) receives the inherent vowel
    unless it carries a vowel sign, closes a syllable before a conjunct (པདྨ pad-ma) or is a bare
    final letter after a vowel (ཕཊ phaṭ).
    """
    clusters: list[dict] = []
    for ch in syllable:
        if ch in BASE:
            clusters.append({"letters": [ch], "vowel": "", "tail": ""})
        elif ch in SUB and clusters:
            clusters[-1]["letters"].append(SUB[ch])
        elif ch in SKT_VOWEL and clusters:
            if clusters[-1]["vowel"] == "A":
                clusters[-1]["vowel"] = ""  # a-chung + vowel sign = long vowel (ཱི ī, ཱུ ū, ཱོ ō)
            clusters[-1]["vowel"] += SKT_VOWEL[ch]
        elif ch in {"ཾ", "ྂ", "ྃ"} and clusters:
            clusters[-1]["tail"] += "M"
        elif ch == "ཿ" and clusters:
            clusters[-1]["tail"] += "H"
        elif ch == "྄" and clusters:
            clusters[-1]["vowel"] = "-"  # halanta: explicitly no vowel
    out = []
    for index, cl in enumerate(clusters):
        letters = cl["letters"]
        parts = []
        j = 0
        while j < len(letters):
            letter = letters[j]
            if j + 1 < len(letters) and letters[j + 1] == "ཧ":
                parts.append(SKT_CONS.get(letter + "ྷ", SKT_CONS.get(letter, "?") + "H"))
                j += 2
                continue
            if letter == "ཀ" and j + 1 < len(letters) and letters[j + 1] == "ཥ":
                parts.append(SKT_CONS["ཀྵ"])
                j += 2
                continue
            if letter in {"ཉ", "ཎ", "ང"} and j + 1 < len(letters):
                parts.append("N" if letter != "ང" else "NG")  # nasal before a conjunct: པཉྩ pañca
                j += 1
                continue
            parts.append(SKT_CONS.get(letter, "?"))
            j += 1
        onset_text = "".join(parts)
        vowel = cl["vowel"]
        is_last = index == len(clusters) - 1
        if vowel == "-":
            vowel = ""
        elif not vowel:
            nxt = None if is_last else clusters[index + 1]
            closing = index > 0 and len(letters) == 1 and nxt is not None and len(nxt["letters"]) > 1 and not cl["tail"]
            final_bare = index > 0 and is_last and len(letters) == 1 and not cl["tail"]
            vowel = "" if (letters == ["འ"] or closing or final_bare) else "A"
        if not vowel and onset_text == "NY":
            onset_text = "N"  # nasal closing a syllable: པཉྩ pañca
        tail = cl["tail"]
        if tail.startswith("M") and vowel.endswith("U"):
            tail = "NG" + tail[1:]
        out.append(onset_text + vowel + tail)
    return "".join(out)


# ---------------------------------------------------------------------------
# Mapping evidence (with OCR-noise filtering)
# ---------------------------------------------------------------------------

TZ_TOKEN = re.compile(r"^(?:[a-zäöü]+(?:-[aou])?|[A-ZÄÖÜ]+)$")


def plausible_variant(value: str) -> bool:
    """Reject Latin OCR artefacts: 'Iha', 'IG', 'nd', 'gyda', 'kG', 'thé' ..."""
    if not TZ_TOKEN.match(value):
        return False
    low = value.lower()
    if low.endswith("d"):
        return False
    if re.search(r"[bcdfghjklmnpqrstvwxz]{2}$", low) and not low.endswith(("ng", "ch", "sch")):
        return False
    if not re.search(r"[aeiouäöü]", low):
        return False
    return True


def parse_variants(text: str) -> list[tuple[str, int]]:
    out = []
    for part in text.split(";"):
        part = part.strip()
        if not part:
            continue
        value, _, count = part.rpartition(":")
        out.append((value, int(count)))
    return out


def load_mapping(path: Path = MAPPING) -> dict[str, dict]:
    return {e["tibetan_syllable"]: e for e in json.loads(path.read_text(encoding="utf-8"))}


def convention_key(value: str) -> str:
    """Collapse spelling-convention and OCR-umlaut differences for comparison.

    Equivalent: tsh ~ z ~ ts (TZ Hayagriva vs Chakrasamvara for ཚ), aspirated ~ plain stops,
    umlaut ~ plain vowel (OCR drops the dots), j ~ y (gjur/gyur), trailing "-o" link.
    """
    v = value.lower().replace("-", "")
    for a, b in (("tsch", "C"), ("dsch", "J"), ("sch", "S"), ("dz", "D"), ("tsh", "Z"), ("ts", "Z"),
                 ("z", "Z"), ("thr", "tr"), ("th", "t"), ("kh", "k"), ("ph", "p"), ("j", "y"),
                 ("ä", "a"), ("ö", "o"), ("ü", "u"), ("é", "e"), ("sh", "S")):
        v = v.replace(a, b)
    return v


def required_count(value: str, rule_value: str | None) -> int:
    """Evidence that contradicts the orthographic coda (e.g. 'khan' for མཁའ) needs more support."""
    if rule_value is None:
        return 2
    coda = re.search(r"(ng|[gbmrln])?$", value.lower().replace("-", "")).group(0)
    rule_coda = re.search(r"(ng|[gbmrln])?$", rule_value.lower().replace("-", "")).group(0)
    return 2 if coda == rule_coda else 3


def evidence_decision(entry: dict, rule_value: str | None) -> tuple[str | None, str, str]:
    """Combine observed TZ variants with the rule output.

    Returns (value, origin, note). Origins:
      confirmed      rule output agrees with at least one plausible observation (modulo convention)
      observed_TZ    rule disagrees, but a plausible observation occurs at least twice -> trust evidence
      rule_contested only single, disagreeing observations -> keep rule output, flag for review
    """
    raw = parse_variants(entry.get("variants", ""))
    variants = [(v, c) for v, c in raw if plausible_variant(v)]
    dropped = [v for v, _ in raw if not plausible_variant(v)]
    note = f"OCR-like variants ignored: {', '.join(dropped)}" if dropped else ""
    variants.sort(key=lambda vc: -vc[1])
    if rule_value is not None:
        key = convention_key(rule_value)
        agreeing = sum(c for v, c in variants if convention_key(v) == key)
        others = [(v, c) for v, c in variants if convention_key(v) != key]
        best_other = others[0] if others else None
        if best_other and best_other[1] > agreeing and best_other[1] >= required_count(best_other[0], rule_value):
            return best_other[0], "observed_TZ", "; ".join(
                x for x in (note, f"majority evidence overrides rule '{rule_value}' ({agreeing} agreeing)") if x)
        if agreeing:
            return rule_value, "confirmed", note
    variants.sort(key=lambda vc: -vc[1])
    strong = [(v, c) for v, c in variants if c >= required_count(v, rule_value)]
    if strong:
        return strong[0][0], "observed_TZ", "; ".join(x for x in (note, f"rule gives '{rule_value}'") if x)
    if rule_value is not None:
        seen = ", ".join(f"{v}:{c}" for v, c in variants) or "none plausible"
        return rule_value, "rule_contested", "; ".join(x for x in (note, f"single TZ observation(s) {seen}") if x)
    if variants:
        return variants[0][0], "observed_TZ", "; ".join(x for x in (note, "rule failed") if x)
    return None, "unresolved", note


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------


MANTRA_SHARE = 0.4


def gebetsbuch_style(value: str) -> str:
    """Older TZ prayer-book convention: aspiration unmarked, ཛ as ds (tsog, tam, kor, pän, dsin)."""
    if value.isupper():
        return value
    for a, b in (("tsch", "tsch"), ("tsh", "ts"), ("thr", "tr"), ("th", "t"), ("kh", "k"), ("ph", "p"),
                 ("dz", "ds")):
        if value.startswith(a):
            return b + value[len(a):]
    return value


PROFILES = {"hayagriva": lambda v: v, "gebetsbuch": gebetsbuch_style}


class Generator:
    def __init__(self, mapping: dict[str, dict] | None = None, overrides: dict[str, str] | None = None,
                 use_mapping: bool = True, profile: str = "hayagriva"):
        self.style = PROFILES[profile]
        self.mapping = mapping if mapping is not None else load_mapping()
        if overrides is None and OVERRIDES.exists():
            overrides = {k: v["phonetic"] for k, v in json.loads(OVERRIDES.read_text(encoding="utf-8")).items()}
        self.overrides = overrides or {}
        self.use_mapping = use_mapping
        self.mantra = dict(MANTRA_EXCEPTIONS)
        for key, entry in self.mapping.items():
            if entry["resolution_origin"] == "inferred_exception" and key not in self.mantra:
                self.mantra[key] = entry["resolved_tz_phonetic"].upper()

    def rule(self, syllable: str, previous: str | None) -> tuple[str | None, str, str]:
        if syllable in TIBETAN_WORD_EXCEPTIONS:
            return TIBETAN_WORD_EXCEPTIONS[syllable], "mantra_exception", ""
        if is_sanskrit(syllable):
            return rule_sanskrit(syllable), "rule_sanskrit", ""
        try:
            particle = previous is not None and syllable in PARTICLES_WITH_WA
            return rule_tibetan(syllable, particle_context=particle), "rule_tibetan", ""
        except (ValueError, KeyError) as exc:
            glued = split_glued(syllable)
            if glued:
                return " ".join(rule_tibetan(part) for part in glued), "rule_tibetan", \
                    f"missing tsheg in source, read as {'+'.join(glued)}"
            # not a well-formed Tibetan syllable: most often an unmarked Sanskrit loan (ཀརྨ, སཏྭ)
            value = rule_sanskrit(syllable)
            if "?" in value or not value:
                return None, "unresolved", str(exc)
            return value, "rule_sanskrit", f"invalid Tibetan structure: {exc}"

    def syllable(self, syllable: str, previous: str | None = None) -> SyllableResult:
        if syllable in self.overrides:
            return SyllableResult(syllable, self.overrides[syllable], "override")
        if syllable in self.mantra:
            return SyllableResult(syllable, self.mantra[syllable], "mantra_exception")
        rule_value, rule_origin, rule_note = self.rule(syllable, previous)
        entry = self.mapping.get(syllable) if self.use_mapping else None
        if entry and entry["resolution_origin"] == "observed_TZ" and rule_origin != "rule_sanskrit":
            value, origin, note = evidence_decision(entry, rule_value)
            if value is not None:
                return SyllableResult(syllable, value, origin, note)
        if rule_value is None:
            return SyllableResult(syllable, "?", "unresolved", rule_note)
        return SyllableResult(syllable, rule_value, rule_origin, rule_note)

    def phrase(self, phrase: str) -> list[SyllableResult]:
        results: list[SyllableResult] = []
        previous = None
        for syl in split_syllables(phrase):
            result = self.syllable(syl, previous)
            result.phonetic = self.style(result.phonetic)
            results.append(result)
            previous = syl
        # mantra phrase: mostly Sanskrit -> uppercase everything
        skt = sum(r.origin in {"rule_sanskrit", "mantra_exception"} or r.phonetic.isupper() for r in results)
        if results and skt / len(results) >= MANTRA_SHARE:
            for r in results:
                if r.origin in {"rule_tibetan", "rule_contested"}:
                    r.phonetic, r.origin = rule_sanskrit(r.tibetan), "rule_sanskrit"
                    r.note = "Tibetan-looking syllable inside a mantra phrase"
                r.phonetic = r.phonetic.upper()
        else:
            for r in results:
                if r.tibetan in TIBETAN_WORD_EXCEPTIONS:
                    r.phonetic = TIBETAN_WORD_EXCEPTIONS[r.tibetan]
                elif r.origin == "rule_sanskrit":
                    r.phonetic = r.phonetic.lower()  # Sanskrit loan inside Tibetan prose (སྨན་རཀ män rak)
        return results

    def text(self, text: str) -> list[list[SyllableResult]]:
        return [self.phrase(p) for p in split_phrases(text)]


def split_phrases(text: str) -> list[str]:
    text = unicodedata.normalize("NFC", text)
    phrases, current = [], []
    for ch in text:
        if ch in BREAKS:
            if "".join(current).strip(TSHEG + " "):
                phrases.append("".join(current))
            current = []
        elif ch in SKIP:
            continue
        elif ch == "\n":
            current.append(" ")
        else:
            current.append(ch)
    if "".join(current).strip(TSHEG + " "):
        phrases.append("".join(current))
    return phrases


def split_syllables(phrase: str) -> list[str]:
    out = []
    for token in re.split(r"[\u0f0b\u0f0c\s]+", phrase):
        # mantra units glued without tsheg after anusvara/visarga: ཨཱཿཧཱུཾ -> ཨཱཿ ཧཱུཾ
        token = re.sub(r"([\u0f7e\u0f7f\u0f82\u0f83])(?=[\u0f40-\u0f6c])", r"\1 ", token)
        # ignore non-Tibetan tokens (Latin notes, stray signs)
        out.extend(t for t in token.split() if any("\u0f40" <= ch <= "\u0f6c" for ch in t))
    return out


def render(phrases: list[list[SyllableResult]]) -> str:
    return " / ".join(" ".join(r.phonetic for r in p) for p in phrases)


if __name__ == "__main__":
    import sys

    gen = Generator()
    for line in sys.argv[1:] or ["༄༅། །པདྨ་ཡང་གསང་ཁྲོས་པའི་ལས་བྱང་སྙིང་པོ་བཅུད་བསྡུས་"]:
        for phrase in gen.text(line):
            print(" ".join(f"{r.phonetic}[{r.origin[:3]}]" for r in phrase))
