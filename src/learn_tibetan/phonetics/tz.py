"""Tibetan -> German pronunciation aid in the spelling of the Tibetisches Zentrum (TZ).

Deterministic and standard-library only; used by the Reader projector at build time.

How it works
------------
Tibetan orthography is regular. Each syllable (between two tsheg ་) has up to seven positions:
prefix, superscript, root, subscripts, vowel, suffix, second suffix. `analyse` finds them and
`rule_tibetan` composes the pronunciation from small tables (root -> onset, subscript
combinations, finals, umlaut). Units written with Sanskrit letters or marks (ཧཱུཾ, བཛྲ, པདྨ) do
not follow that syllable plan; `rule_sanskrit` reads them letter by letter.

Every syllable is transcribed on its own. There is no mantra detection and no context beyond an
optional list of connected-speech effects (རྡོ་རྗེ dor dsche).

Switches and variants
---------------------
`Options` holds every reading choice as an independent switch; `VARIANTS` bundles them into the
three variants offered in the Reader (TZ aktuell, TZ Gebetsbuch, Silbengetreu). Evidence and
method: docs/research/phonetics-01-tz-generator-exploration.md and docs/tz-umschrift.md.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

VERSION = "1.0.0"

TSHEG = "་"
# shad, double shad, gter tsheg and related phrase breaks
BREAKS = set("།༎༏༐༑༒༔༈")
BASE = {chr(c): chr(c) for c in range(0x0F40, 0x0F6D)}
SUB = {chr(c): chr(c - 0x50) for c in range(0x0F90, 0x0FBD)}  # subjoined -> base letter
SUB["ྺ"], SUB["ྻ"], SUB["ྼ"] = "ཝ", "ཡ", "ར"  # fixed-form wa / ya / ra
VOWELS = {"ི": "i", "ུ": "u", "ེ": "e", "ོ": "o"}
# long vowels, reversed gigu, anusvara, visarga, halanta: never in native Tibetan words
SANSKRIT_MARKS = set("ཱཱཱིུྲྀཷླྀཹཻཽཾཿཱྀྀ"
                     "྄ྂྃ")
# retroflex letters, ssa, kssa and their subjoined forms
SANSKRIT_LETTERS = set("ཊཋཌཎཥཀྵཪྚྛྜྞྵ")

PREFIXES = {
    "ག": set("ཅཉཏདནཙཞཟཡཤས"),
    "ད": set("ཀགངཔབམ"),
    "བ": set("ཀགངཅཉཏདནཙཞཟཤས"),
    "མ": set("ཁགངཆཇཉཐདནཚཛ"),
    "འ": set("ཁགཆཇཐདཕབཚཛ"),
}
SUFFIXES = set("གངདནབམའརལས")
POSTSUFFIXES = set("སད")
SUPERSCRIPT_OK = {"ར": set("ཀགངཇཉཏདནབམཙཛ"), "ལ": set("ཀགངཅཇཏདཔབཧ"), "ས": set("ཀགངཉཏདནཔབམཙ")}
SUBSCRIPT_OK = {
    "ཡ": set("ཀཁགཔཕབམཧ"),
    "ར": set("ཀཁགཏཐདཔཕབམསཧཤཙ"),
    "ལ": set("ཀགབརསཟ"),
    "ཝ": set("ཀཁགཅཉཏདཙཚཞཟརལཤསཧཕཡ"),
}

# --- Tibetan tables (aspiration marked, ཛ as dz; switches rewrite the onset) ---------------------
ONSET = {
    "ཀ": "k", "ཁ": "kh", "ག": "g", "ང": "ng", "ཅ": "tsch", "ཆ": "tsch", "ཇ": "dsch", "ཉ": "ny",
    "ཏ": "t", "ཐ": "th", "ད": "d", "ན": "n", "པ": "p", "ཕ": "ph", "བ": "b", "མ": "m",
    "ཙ": "ts", "ཚ": "tsh", "ཛ": "dz", "ཝ": "w", "ཞ": "sch", "ཟ": "s", "འ": "", "ཡ": "y",
    "ར": "r", "ལ": "l", "ཤ": "sch", "ས": "s", "ཧ": "h", "ཨ": "",
}
YATA = {"ཀ": "ky", "ཁ": "khy", "ག": "gy", "པ": "tsch", "ཕ": "tsch", "བ": "dsch", "མ": "ny", "ཧ": "hy"}
RATA = {"ཀ": "tr", "ཏ": "tr", "པ": "tr", "ཁ": "thr", "ཐ": "thr", "ཕ": "thr", "ག": "dr", "ད": "dr",
        "བ": "dr", "ས": "s", "ཧ": "hr", "མ": "m", "ཤ": "schr", "ཙ": "ts"}
LATA = {"ཀ": "l", "ག": "l", "བ": "l", "ར": "l", "ས": "l", "ཟ": "d"}
FINAL = {"ག": "g", "ང": "ng", "བ": "b", "མ": "m", "ར": "r", "ལ": "l", "ན": "n", "ད": "", "ས": "", "འ": ""}
UMLAUT = {"a": "ä", "o": "ö", "u": "ü", "i": "i", "e": "e"}
# particles written with root བ that are read w after another syllable (gyäl wa, dro wa)
PARTICLES_WITH_WA = {"བ", "བར", "བའི", "བས", "བོ", "བོའི", "བའོ", "བོར", "བོས", "བའམ", "བའང"}

# Sanskrit letters as Tibetans read them (same Tibetan letters, plus retroflex ཊ ཋ ཌ ཎ ཥ and ཀྵ).
SANSKRIT_LETTER_SOUNDS = {
    "ཀ": "k", "ཁ": "kh", "ག": "g", "ང": "ng", "ཉ": "ny", "ཊ": "t", "ཋ": "th", "ཌ": "d", "ཎ": "n",
    "ཏ": "t", "ཐ": "th", "ད": "d", "ན": "n", "པ": "p", "ཕ": "ph", "བ": "b", "མ": "m", "ཡ": "y",
    "ར": "r", "ལ": "l", "ཤ": "sh", "ཥ": "sh", "ས": "s", "ཧ": "h", "ཨ": "", "འ": "", "ཞ": "sh",
    "ཟ": "s", "ཚ": "tsh", "ཙ": "ts", "ཛ": "dz", "ཇ": "dsch", "ཅ": "ts", "ཆ": "tsch", "ཝ": "w",
    "ཀྵ": "ksch",
}
SANSKRIT_VOWELS = {"ཱ": "a", "ི": "i", "ུ": "u", "ེ": "e", "ཻ": "ai", "ོ": "o",
                   "ཽ": "au", "ྀ": "i", "ྲྀ": "ri", "ཷ": "ri", "ླྀ": "li", "ཹ": "li"}

# --- Word-level choices, each behind a switch and backed by evidence ---------------------------
# Connected speech: a letter of the next syllable is heard at the end of this one.
# རྡོ་རྗེ: the superscript ར of རྗེ -> dor dsche (TZ mapping dor:12, do:1).
CONNECTED_SPEECH = {("རྡོ", "རྗེ"): "dor"}
# TZ spelling habits for single Tibetan words: ཤོག printed scho (Chakrasamvara 8:1, Gebetsbuch 5:0).
TZ_SPELLINGS = {"ཤོག": "scho"}
# Traditional Tibetan pronunciation of mantra words written with Sanskrit letters, as printed in the
# TZ mantra lines (BENDSA, PEMA, SOHA, PHÄ, SHUDDHO HANG, PHÜPE, DHÜPE, GHÄNDE, NEWIDYÄ, TISHTRA).
TRADITIONAL_READINGS = {
    "བཛྲ": "bendsa", "བཛྲཱ": "bendsa", "པདྨ": "pema", "པདྨཱ": "pema", "པདྨའི": "pemä", "པདྨས": "pemä",
    "པདྨོ": "pemo", "པདྨེ": "peme", "སྭཱཧཱ": "soha", "སྭཧཱ": "soha", "ཕཊ": "phä", "ཕཊ྄": "phä",
    "ཕཱཊ": "phä", "ཕཊཿ": "phä", "ཛཿ": "dza", "ཧཾ": "hang", "ཧཱཾ": "hang", "སརྦ": "sarva",
    "སརྦ྄": "sarva", "ཏིཥྛ": "tishtra", "ཥྱོ": "kayo", "པུཥྤེ": "phüpe", "དྷཱུཔེ": "dhüpe",
    "གནྡྷེ": "ghände", "ནཻཝིདྱ": "newidyä", "ཛྙཱ": "dschnya", "ཛྙ": "dschnya", "བཻ": "be",
    "ཤུདྡྷོ྅ཧཾ": "shuddho hang", "ཤུདྡྷོཧཾ": "shuddho hang",
}


@dataclass(frozen=True)
class Options:
    """Independent reading switches. Every combination is valid."""

    aspiration_marked: bool = True     # tshog/tham/khor vs tsog/tam/kor (ཚ ཐ ཁ ཕ, thr)
    dz: str = "dz"                     # spelling of ཛ: "dz" or "ds"
    genitive_umlaut_ou: bool = True    # བཅུའི tschü vs tschu (genitive after o/u)
    connected_speech: bool = True      # རྡོ་རྗེ dor dsche vs do dsche
    tz_spellings: bool = True          # ཤོག scho vs schog
    sanskrit: str = "traditional"      # "traditional" (bendsa, pema, soha) or "letters" (badzra, padma, swaha)
    anusvara_after_u: str = "ng"       # ཧཱུཾ hung ("ng") or hum ("m")
    sanskrit_capitals: bool = False    # write syllables with Sanskrit letters/marks in capitals (KAM, HUNG)

    def __post_init__(self) -> None:
        if self.dz not in {"dz", "ds"} or self.sanskrit not in {"traditional", "letters"} \
                or self.anusvara_after_u not in {"ng", "m"}:
            raise ValueError(f"invalid options {self}")


@dataclass(frozen=True)
class Variant:
    id: str
    label: str
    description: str
    options: Options


VARIANTS: dict[str, Variant] = {
    "tz-aktuell": Variant(
        "tz-aktuell", "TZ aktuell",
        "Wie in den aktuellen TZ-Texten: Behauchung markiert (tshog), Mantras in traditioneller "
        "Aussprache (bendsa, soha).",
        Options()),
    "tz-gebetsbuch": Variant(
        "tz-gebetsbuch", "TZ Gebetsbuch",
        "Wie im TZ-Gebetsbuch: Behauchung nicht markiert (tsog, tam, kor).",
        Options(aspiration_marked=False, dz="ds", genitive_umlaut_ou=False)),
    "silbengetreu": Variant(
        "silbengetreu", "Silbengetreu",
        "Jede Silbe für sich, ohne Wortausnahmen: do dsche, schog, Mantras nach den Zeichen (badzra, padma).",
        Options(connected_speech=False, tz_spellings=False, sanskrit="letters")),
}
DEFAULT_VARIANT = "tz-aktuell"


@dataclass
class Syllable:
    tibetan: str
    phonetic: str
    origin: str  # rule_tibetan | rule_sanskrit | traditional | tz_spelling | connected_speech | glued_split


@dataclass
class Line:
    tibetan: str  # exact slice of the input text
    pronunciation: str
    syllables: list[Syllable] = field(default_factory=list)


# --- parsing ------------------------------------------------------------------------------------


def stacks(syllable: str) -> list[dict]:
    """Split a syllable into stacks: base letter + subjoined letters + vowel."""
    out: list[dict] = []
    for ch in syllable:
        if ch in BASE:
            out.append({"letters": [ch], "vowel": None})
        elif ch in SUB and out:
            out[-1]["letters"].append(SUB[ch])
        elif ch in VOWELS and out:
            out[-1]["vowel"] = VOWELS[ch]
        elif not out:
            raise ValueError(f"cannot parse {syllable!r}")
    return out


def valid_tibetan_stack(letters: list[str]) -> bool:
    head, *rest = letters
    if head in SUPERSCRIPT_OK and rest and rest[0] in SUPERSCRIPT_OK[head]:
        root, subs = rest[0], rest[1:]
    else:
        root, subs = head, rest
    ok: list[str] = []
    for sub in subs:
        if (sub in SUBSCRIPT_OK and root in SUBSCRIPT_OK[sub]) or (sub == "ཝ" and ok):
            ok.append(sub)
        else:
            return False
    return len(ok) <= 2


def is_sanskrit(syllable: str) -> bool:
    if any(ch in SANSKRIT_MARKS or ch in SANSKRIT_LETTERS for ch in syllable):
        return True
    try:
        parsed = stacks(syllable)
    except ValueError:
        return True
    if any(len(st["letters"]) > 1 and not valid_tibetan_stack(st["letters"]) for st in parsed):
        return True
    voweled = [st for st in parsed if st["vowel"]]
    return len(voweled) > 1 and not (len(voweled) == 2 and voweled[1]["letters"] == ["འ"])


def analyse(syllable: str) -> dict:
    """Return prefix, superscript, root, subscripts, vowel, suffix, postsuffix and fused particle."""
    parsed = stacks(syllable)
    affix = None
    if len(parsed) >= 2 and parsed[-1]["letters"] == ["འ"] and parsed[-1]["vowel"] in {"i", "o", "u"}:
        affix = parsed[-1]["vowel"]  # genitive འི, terminative འོ, འུ
        parsed = parsed[:-1]
    if affix is None and len(parsed) >= 3 and parsed[-2]["letters"] == ["འ"] and not parsed[-2]["vowel"] \
            and parsed[-1]["letters"][0] in {"ང", "མ"} and not parsed[-1]["vowel"]:
        affix = {"ང": "ang", "མ": "am"}[parsed[-1]["letters"][0]]  # concessive འང, alternative འམ
        parsed = parsed[:-2]
    n = len(parsed)
    root_index = next((i for i, st in enumerate(parsed) if len(st["letters"]) > 1 or st["vowel"]), None)
    if root_index is None:
        letters = [p["letters"][0] for p in parsed]
        if n == 1:
            root_index = 0
        elif n == 2:
            a, b = letters
            root_index = 1 if (a in PREFIXES and b in PREFIXES[a] and b not in SUFFIXES) else 0
        elif n == 3:
            a, b, c = letters
            if c == "ས" and b in "གངབམ":
                root_index = 0  # classical rule: དགས is dags (root, suffix, second suffix), not dgas
            else:
                root_index = 1 if (a in PREFIXES and b in PREFIXES[a]) else 0
        elif n == 4:
            root_index = 1
        else:
            raise ValueError(f"unexpected syllable length {syllable!r}")
    pre, root_stack, post = parsed[:root_index], parsed[root_index], parsed[root_index + 1:]
    if len(pre) > 1 or any(len(p["letters"]) > 1 or p["vowel"] for p in pre + post):
        raise ValueError(f"unexpected structure {syllable!r}")
    prefix = pre[0]["letters"][0] if pre else None
    if prefix and prefix not in PREFIXES:
        raise ValueError(f"invalid prefix {syllable!r}")
    letters = root_stack["letters"]
    superscript = None
    if len(letters) > 1 and letters[0] in SUPERSCRIPT_OK and letters[1] in SUPERSCRIPT_OK[letters[0]]:
        superscript, letters = letters[0], letters[1:]
    suffix = post[0]["letters"][0] if post else None
    postsuffix = post[1]["letters"][0] if len(post) > 1 else None
    if len(post) > 2 or (suffix and suffix not in SUFFIXES) or (postsuffix and postsuffix not in POSTSUFFIXES):
        raise ValueError(f"invalid suffix {syllable!r}")
    return {"prefix": prefix, "superscript": superscript, "root": letters[0], "stack": root_stack["letters"],
            "subs": [s for s in letters[1:] if s != "ཝ"], "vowel": root_stack["vowel"] or "a",
            "suffix": suffix, "postsuffix": postsuffix, "affix": affix}


def split_glued(syllable: str) -> list[str] | None:
    """Split a token such as གཡསགཉིས (missing tsheg in the source) into two Tibetan syllables."""
    for cut in range(2, len(syllable) - 1):
        left, right = syllable[:cut], syllable[cut:]
        if right[0] not in BASE or is_sanskrit(left) or is_sanskrit(right):
            continue
        try:
            analyse(left), analyse(right)
        except (ValueError, KeyError):
            continue
        return [left, right]
    return None


# --- rules --------------------------------------------------------------------------------------


def _onset(a: dict) -> str:
    root, subs, prefix = a["root"], a["subs"], a["prefix"]
    if subs and subs[0] == "ཡ" and root == "བ" and prefix == "ད":
        return "y"  # དབྱིངས ying
    if subs and subs[0] == "ཡ" and root in YATA:
        return YATA[root]
    if subs and subs[0] == "ར" and root in RATA:
        return RATA[root]
    if subs and subs[0] == "ལ" and root in LATA:
        return LATA[root]
    if root == "བ" and prefix == "ད" and not a["superscript"]:
        return "" if a["vowel"] in {"u", "o"} else "w"  # དབང wang, དབུ u
    if root == "ཧ" and a["superscript"] == "ལ":
        return "lh"
    return ONSET[root]


UNASPIRATED = (("tsh", "ts"), ("thr", "tr"), ("th", "t"), ("kh", "k"), ("ph", "p"))


def spell(value: str, options: Options) -> str:
    """Apply the spelling switches to the start of each syllable (aspiration, ཛ)."""
    words = []
    for word in value.split(" "):
        if not options.aspiration_marked:
            for old, new in UNASPIRATED:
                if word.startswith(old):
                    word = new + word[len(old):]
                    break
        if options.dz == "ds" and word.startswith("dz"):
            word = "ds" + word[2:]
        words.append(word)
    return " ".join(words)


def rule_tibetan(syllable: str, options: Options, particle_context: bool = False) -> str:
    a = analyse(syllable)
    head = _onset(a)
    if particle_context and a["root"] == "བ" and not (a["prefix"] or a["superscript"] or a["subs"]):
        head = "w"
    vowel, suffix, coda = a["vowel"], a["suffix"], ""
    if suffix in {"ད", "ས", "ན", "ལ"}:
        vowel = UMLAUT[vowel]
    if suffix:
        coda = FINAL[suffix]
    if a["affix"] == "i":
        if vowel == "a" or options.genitive_umlaut_ou:
            vowel = UMLAUT[vowel]
    elif a["affix"] in {"o", "u", "ang", "am"}:
        coda += "-" + a["affix"]
    return head + vowel + coda


def rule_sanskrit(syllable: str, options: Options) -> str:
    """Read a unit written with Sanskrit letters or marks, letter by letter.

    Every cluster (base letter + subjoined letters + vowel/marks) receives the inherent vowel a
    unless it carries a vowel sign, closes a syllable before a conjunct (པདྨ pad-ma) or is a bare
    final letter after a vowel (ཕཊ phat). The anusvara ཾ is m, or ng after u (switch); the
    visarga ཿ is h. With ``sanskrit="traditional"`` two Tibetan reading habits apply as well:
    subjoined wa is silent and turns a after ས/ཏ into o (སྭ so, སཏྭ sato, སྟྭཾ stom), and the
    visarga is silent in longer words (shuddha, dharma).
    """
    traditional = options.sanskrit == "traditional"
    clusters: list[dict] = []
    for ch in syllable:
        if ch in BASE:
            clusters.append({"letters": [ch], "vowel": "", "tail": ""})
        elif ch in SUB and clusters:
            clusters[-1]["letters"].append(SUB[ch])
        elif ch in SANSKRIT_VOWELS and clusters:
            if clusters[-1]["vowel"] == "a":
                clusters[-1]["vowel"] = ""  # a-chung + vowel sign = long vowel (ཱི ī, ཱུ ū, ཱོ ō)
            clusters[-1]["vowel"] += SANSKRIT_VOWELS[ch]
        elif ch in "ཾྂྃ" and clusters:
            clusters[-1]["tail"] += "m"
        elif ch == "ཿ" and clusters:
            clusters[-1]["tail"] += "h"
        elif ch == "྄" and clusters:
            clusters[-1]["vowel"] = "-"  # halanta: explicitly no vowel
    table = SANSKRIT_LETTER_SOUNDS
    out = []
    for index, cl in enumerate(clusters):
        letters, parts, j = cl["letters"], [], 0
        while j < len(letters):
            letter = letters[j]
            nxt = letters[j + 1] if j + 1 < len(letters) else None
            if nxt == "ཧ":  # aspirate written with subjoined ha: དྷ dh, བྷ bh
                parts.append(table.get(letter, "?") + "h")
                j += 2
            elif letter == "ཀ" and nxt == "ཥ":
                parts.append(table["ཀྵ"])
                j += 2
            elif letter == "ཙ" and nxt in {"ཚ", "ཆ"}:
                parts.append("tsh")  # ཙྪ cch
                j += 2
            elif letter in {"ཉ", "ཎ"} and nxt:
                parts.append("n")  # nasal before a conjunct: པཉྩ pañca
                j += 1
            else:
                parts.append(table.get(letter, "?"))
                j += 1
        wa_zur = len(letters) > 1 and letters[-1] == "ཝ"
        if wa_zur and traditional:
            parts = parts[:-1]
        onset = "".join(parts)
        vowel = cl["vowel"]
        last = index == len(clusters) - 1
        if vowel == "-":
            vowel = ""
        elif not vowel:
            nxt_cl = None if last else clusters[index + 1]
            closing = index > 0 and len(letters) == 1 and nxt_cl is not None and len(nxt_cl["letters"]) > 1 \
                and not cl["tail"]
            final_bare = index > 0 and last and len(letters) == 1 and not cl["tail"]
            vowel = "" if (letters == ["འ"] or closing or final_bare) else "a"
        if wa_zur and traditional and vowel == "a" and letters[-2] in {"ས", "ཏ"}:
            vowel = "o"
        if not vowel and onset == "ny":
            onset = "n"
        tail = cl["tail"]
        if traditional and "h" in tail and len(clusters) > 1:
            tail = tail.replace("h", "")
        if tail.startswith("m") and vowel.endswith("u"):
            tail = options.anusvara_after_u + tail[1:]
        out.append(onset + vowel + tail)
    return "".join(out)


# --- segmentation -------------------------------------------------------------------------------


def split_syllables(phrase: str) -> list[str]:
    out = []
    # tsheg, spaces and all punctuation/signs of U+0F00-0F3F (shad, yig mgo, gter tsheg) separate
    for token in re.split("[\u0f00-\u0f3f\\s]+", phrase):
        # mantra units glued without tsheg after anusvara/visarga: ཨཱཿཧཱུཾ -> ཨཱཿ ཧཱུཾ
        token = re.sub(r"([ཾཿྂྃ])(?=[ཀ-ཬ])", r"\1 ", token)
        out.extend(t for t in token.split() if any(ch in BASE for ch in t))
    return out


def segment(text: str) -> list[str]:
    """Split text into exact, contiguous slices, one per phrase.

    A phrase ends after its run of break marks (shad, gter tsheg) and following spaces. Physical
    newlines are layout, not phrase breaks. Slices without any Tibetan letter (a leading ༄༅།
    or a trailing shad) are merged into a neighbour, so ``"".join(segment(t)) == t``.
    """
    slices, start, i, n = [], 0, 0, len(text)
    while i < n:
        if text[i] in BREAKS:
            j = i
            while j < n and (text[j] in BREAKS or text[j] in " ་"):
                j += 1
            slices.append(text[start:j])
            start = i = j
        else:
            i += 1
    if start < n:
        slices.append(text[start:])
    merged: list[str] = []
    carry = ""
    for piece in slices:
        if any(ch in BASE for ch in piece) and not all(ch in "༄༅༆" or ch not in BASE
                                                       for ch in piece):
            merged.append(carry + piece)
            carry = ""
        elif merged:
            merged[-1] += piece
        else:
            carry += piece
    if carry:
        if merged:
            merged[-1] += carry
        else:
            merged.append(carry)
    return merged


# --- generator ----------------------------------------------------------------------------------


def _syllable(syl: str, previous: str | None, following: str | None, options: Options) -> Syllable:
    if options.connected_speech and following:
        for (this, nxt), value in CONNECTED_SPEECH.items():
            if syl == this and following.startswith(nxt):
                return Syllable(syl, spell(value, options), "connected_speech")
    if options.tz_spellings and syl in TZ_SPELLINGS:
        return Syllable(syl, spell(TZ_SPELLINGS[syl], options), "tz_spelling")
    if options.sanskrit == "traditional" and syl in TRADITIONAL_READINGS:
        return _sanskrit_case(Syllable(syl, spell(TRADITIONAL_READINGS[syl], options), "traditional"), options)
    if is_sanskrit(syl):
        return _sanskrit_case(Syllable(syl, spell(rule_sanskrit(syl, options), options), "rule_sanskrit"), options)
    try:
        particle = previous is not None and syl in PARTICLES_WITH_WA
        return Syllable(syl, spell(rule_tibetan(syl, options, particle_context=particle), options), "rule_tibetan")
    except (ValueError, KeyError):
        glued = split_glued(syl)
        if glued:
            return Syllable(syl, spell(" ".join(rule_tibetan(p, options) for p in glued), options), "glued_split")
        # not a well-formed Tibetan syllable: an unmarked Sanskrit unit (ཀརྨ, སཏྭ)
        return _sanskrit_case(Syllable(syl, spell(rule_sanskrit(syl, options), options), "rule_sanskrit"), options)


def _sanskrit_case(result: Syllable, options: Options) -> Syllable:
    if options.sanskrit_capitals:
        result.phonetic = result.phonetic.upper()
    return result


def phrase(text: str, options: Options) -> list[Syllable]:
    syllables = split_syllables(unicodedata.normalize("NFC", text))
    return [_syllable(s, syllables[i - 1] if i else None, syllables[i + 1] if i + 1 < len(syllables) else None,
                      options) for i, s in enumerate(syllables)]


def _options(variant: str | Options) -> Options:
    return variant if isinstance(variant, Options) else VARIANTS[variant].options


def generate(text: str, variant: str | Options = DEFAULT_VARIANT) -> list[Line]:
    """Pronunciation lines for a Tibetan text; the ``tibetan`` slices concatenate to ``text``."""
    options = _options(variant)
    lines = []
    for piece in segment(text):
        syllables = phrase(piece, options)
        lines.append(Line(piece, " ".join(s.phonetic for s in syllables), syllables))
    return lines


def render(text: str, variant: str | Options = DEFAULT_VARIANT) -> str:
    return " / ".join(line.pronunciation for line in generate(text, variant) if line.pronunciation)
