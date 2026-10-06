"""Extract TZ phonetic lines from Tesseract (deu) page OCR of TZ practice texts.

Research helper. A line counts as phonetic when it ends with the TZ verse slash or when nearly all
of its tokens look like TZ syllables (short, lowercase or mantra capitals) and it has no German
function words.
"""

from __future__ import annotations

import re
from pathlib import Path

GERMAN = set("""und der die das den dem des ein eine einer eines einem zu zum zur im in ist sich mit auf
von aus als wie so ich du er sie wir ihr mein meine deine alle aller allen möge mögen durch für nicht
auch dann diese dieser dieses bis nach vor über unter wird werden sind ohne oder sein seine ihre man""".split())
SYL = re.compile(r"^(?:[a-zäöüé’']{1,8}|[A-ZÄÖÜ]{1,10})$")


def tokens(line: str) -> list[str]:
    return [t for t in re.split(r"[\s/|]+", line.strip().strip("‚,.")) if t]


def is_phonetic(line: str) -> bool:
    toks = tokens(line)
    if len(toks) < 2:
        return False
    if any(t.lower() in GERMAN for t in toks):
        return False
    good = sum(bool(SYL.match(t)) for t in toks)
    share = good / len(toks)
    if line.rstrip().endswith("/") and share >= 0.6:
        return True
    return share >= 0.9 and len(toks) >= 4 and sum(t[0].islower() for t in toks) >= len(toks) / 2


def page_lines(txt: Path) -> list[str]:
    return [l.strip() for l in txt.read_text(encoding="utf-8").splitlines() if is_phonetic(l)]
