"""Cross-check the external observation corpus against an independent Tesseract OCR.

For every page, the other agent's phonetic tokens (ordered by block/position) are aligned with the
phonetic tokens of our own OCR. Each observation is classified as identical, different (pair kept)
or unaligned. Research helper; prints a summary and writes a CSV next to the OCR pages.
"""

from __future__ import annotations

import csv
import difflib
import sys
from collections import Counter
from pathlib import Path

from tz_ocr_lines import page_lines, tokens

OCR = Path(sys.argv[1])
PREFIX = {"hayagriva": "hay", "chakrasamvara": "chak"}


def norm(t: str) -> str:
    return t.lower().replace("’", "'").strip("'")


def main() -> None:
    obs = list(csv.DictReader(open(OCR.parent / "observations.csv", encoding="utf-8")))
    pages: dict[tuple[str, int], list[dict]] = {}
    for o in obs:
        pages.setdefault((o["document"], int(o["page"])), []).append(o)
    results = []
    for (doc, page), items in sorted(pages.items()):
        items.sort(key=lambda o: (int(o["block"]), int(o["position_phonetic"])))
        ours = [t for line in page_lines(OCR / f"{PREFIX[doc]}-{page:02d}.txt") for t in tokens(line)]
        theirs = [norm(o["phonetic_raw"]) for o in items]
        sm = difflib.SequenceMatcher(a=theirs, b=[norm(t) for t in ours], autojunk=False)
        paired: dict[int, str] = {}
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
                for k in range(i2 - i1):
                    paired[i1 + k] = ours[j1 + k]
        for i, o in enumerate(items):
            mine = paired.get(i)
            kind = "unaligned" if mine is None else ("identical" if norm(mine) == theirs[i] else "different")
            results.append({**o, "tesseract": mine or "", "check": kind})
    with open(OCR.parent / "observation-crosscheck.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    for doc in ("hayagriva", "chakrasamvara"):
        print(doc, Counter(r["check"] for r in results if r["document"] == doc))
    diffs = Counter((r["phonetic_raw"], r["tesseract"]) for r in results if r["check"] == "different")
    print("most frequent differences (theirs -> tesseract):")
    print("  " + "  ".join(f"{a}->{b}:{c}" for (a, b), c in diffs.most_common(80)))


if __name__ == "__main__":
    main()
