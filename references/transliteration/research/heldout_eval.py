"""Held-out check: generator output vs TZ Gebetsbuch phonetics for reconstructed Tibetan lines."""

import difflib
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tz_phonetics as tz  # noqa: E402

pairs = [l.split("\t") for l in (Path(__file__).parent / "gebetsbuch_heldout.tsv").read_text().splitlines()
         if l and not l.startswith("#")]
for profile in ("hayagriva", "gebetsbuch"):
    for use_mapping in (True, False):
        gen = tz.Generator(profile=profile, use_mapping=use_mapping)
        total = same = 0
        misses = Counter()
        for tz_line, tibetan in pairs:
            ref = tz_line.split()
            out = [t for r in gen.text(tibetan) for x in r for t in x.phonetic.replace("-", " ").split()]
            total += len(ref)
            sm = difflib.SequenceMatcher(a=ref, b=out, autojunk=False)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == "equal":
                    same += i2 - i1
                else:
                    misses[(" ".join(ref[i1:i2]), " ".join(out[j1:j2]))] += 1
        print(f"profile={profile} mapping={use_mapping}: {same}/{total} TZ tokens identical ({same / total:.1%})")
        if profile == "gebetsbuch" and use_mapping:
            print("  TZ -> generator:", "  ".join(f"{a}->{b}" + (f" x{c}" if c > 1 else "") for (a, b), c in misses.most_common()))
