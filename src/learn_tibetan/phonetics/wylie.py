"""Tibetan -> Wylie transliteration (EWTS, the Extended Wylie Transliteration Scheme).

Wylie renders the letters, not the sound: བསྒྲུབས is ``bsgrubs``. The only hard part is where
the inherent ``a`` goes; it follows the root letter, which `learn_tibetan.phonetics.tz.analyse` already
determines. Units written with Sanskrit letters or marks follow EWTS conventions: long vowels as
capitals (``hUM``), retroflex letters as capitals (``T``, ``D``, ``N``, ``Sh``), non-Tibetan stacks
joined with ``+`` (``pad+ma``), anusvara ``M``, visarga ``H``. Lines use the same segmentation as the
pronunciation aid, so both can be shown together.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from learn_tibetan.phonetics import tz

LETTERS = {
    "ཀ": "k", "ཁ": "kh", "ག": "g", "ང": "ng", "ཅ": "c", "ཆ": "ch", "ཇ": "j", "ཉ": "ny",
    "ཏ": "t", "ཐ": "th", "ད": "d", "ན": "n", "པ": "p", "ཕ": "ph", "བ": "b", "མ": "m",
    "ཙ": "ts", "ཚ": "tsh", "ཛ": "dz", "ཝ": "w", "ཞ": "zh", "ཟ": "z", "འ": "'", "ཡ": "y",
    "ར": "r", "ལ": "l", "ཤ": "sh", "ས": "s", "ཧ": "h", "ཨ": "",
    "ཊ": "T", "ཋ": "Th", "ཌ": "D", "ཎ": "N", "ཥ": "Sh", "ཪ": "R",
}
VOWELS = {"ི": "i", "ུ": "u", "ེ": "e", "ོ": "o", "ཻ": "ai", "ཽ": "au",
          "ྀ": "-i", "ྲྀ": "r-i", "ཷ": "r-I", "ླྀ": "l-i", "ཹ": "l-I"}
LONG = {"a": "A", "i": "I", "u": "U", "-i": "-I"}
MARKS = {"ཾ": "M", "ྂ": "~M`", "ྃ": "~M", "ཿ": "H", "྄": "?", "྅": "&"}
SUBSCRIPTS = {"ཡ", "ར", "ལ", "ཝ"}


@dataclass
class Line:
    tibetan: str
    wylie: str


def _stack(letters: list[str]) -> str:
    """EWTS for one stack; letters outside Tibetan stacking rules are joined with '+'."""
    names, j = [], 0
    while j < len(letters):
        if j + 1 < len(letters) and letters[j + 1] == "ཧ" and letters[j] in "གདབཛཌ":
            names.append(LETTERS[letters[j]] + "h")  # aspirated Sanskrit stop: དྷ dh
            j += 2
        elif letters[j] == "ཀ" and j + 1 < len(letters) and letters[j + 1] == "ཥ":
            names.append("k+Sh")
            j += 2
        else:
            names.append(LETTERS[letters[j]])
            j += 1
    if len(letters) == 1 or tz.valid_tibetan_stack(letters) or \
            (len(names) == 2 and letters[-1] in SUBSCRIPTS):
        return "".join(names)
    return "+".join(names)


def _tibetan(syllable: str) -> str:
    a = tz.analyse(syllable)
    vowel = a["vowel"]
    prefix = LETTERS[a["prefix"]] if a["prefix"] else ""
    stack = _stack(a["stack"])
    if prefix == "g" and stack.startswith("y"):
        prefix += "."  # g.yag: prefix ག before root ཡ, not ག with subjoined ཡ
    if a["root"] == "ཨ" and not a["superscript"] and len(a["stack"]) == 1:
        stack = ""
    suffix = LETTERS[a["suffix"]] if a["suffix"] else ""
    post = LETTERS[a["postsuffix"]] if a["postsuffix"] else ""
    affix = {"i": "'i", "o": "'o", "u": "'u", "ang": "'ang", "am": "'am", None: ""}[a["affix"]]
    return prefix + stack + vowel + suffix + post + affix


def _sanskrit(syllable: str) -> str:
    clusters: list[dict] = []
    for ch in syllable:
        if ch in tz.BASE:
            clusters.append({"letters": [ch], "vowel": "", "long": False, "marks": ""})
        elif ch in tz.SUB and clusters:
            clusters[-1]["letters"].append(tz.SUB[ch])
        elif ch == "ཱ" and clusters:
            clusters[-1]["long"] = True
        elif ch in VOWELS and clusters:
            clusters[-1]["vowel"] = VOWELS[ch]
        elif ch in MARKS and clusters:
            clusters[-1]["marks"] += MARKS[ch]
    out = []
    for index, cl in enumerate(clusters):
        vowel = cl["vowel"] or "a"
        last = index == len(clusters) - 1
        if not cl["vowel"] and not cl["long"] and not cl["marks"] and index > 0 and len(cl["letters"]) == 1 \
                and (last or len(clusters[index + 1]["letters"]) > 1):
            vowel = ""  # closing consonant: ཕཊ phaT, པདྨ pad+ma
        if cl["long"]:
            vowel = LONG.get(vowel, vowel)
        stack = _stack(cl["letters"])
        if cl["letters"] == ["ཨ"]:
            stack = ""
        out.append(stack + vowel + cl["marks"])
    return "".join(out)


def syllable(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    if tz.is_sanskrit(text):
        return _sanskrit(text)
    try:
        return _tibetan(text)
    except (ValueError, KeyError):
        glued = tz.split_glued(text)
        if glued:
            return " ".join(_tibetan(part) for part in glued)
        return _sanskrit(text)


def generate(text: str) -> list[Line]:
    """Wylie lines with the same slices as `learn_tibetan.phonetics.tz.generate`."""
    return [Line(piece, " ".join(syllable(s) for s in tz.split_syllables(unicodedata.normalize("NFC", piece))))
            for piece in tz.segment(text)]


def render(text: str) -> str:
    return " / ".join(line.wylie for line in generate(text) if line.wylie)
