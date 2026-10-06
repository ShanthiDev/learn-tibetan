"""Tibetan -> Wylie (EWTS) transliteration (learn_tibetan.phonetics.wylie)."""

import json
from pathlib import Path

import pytest

from learn_tibetan.phonetics import tz, wylie

ROOT = Path(__file__).parents[2]


@pytest.mark.parametrize("tibetan, expected", [
    ("བསྒྲུབས", "bsgrubs"),        # every letter, silent ones included
    ("སངས་རྒྱས", "sangs rgyas"),
    ("བདག", "bdag"),               # inherent a after the root, not after the prefix
    ("དགའ", "dga'"),
    ("དགས", "dags"),               # three letters ending in ས: root, suffix, second suffix
    ("གཡས", "g.yas"),              # separator: prefix ག before root ཡ
    ("གྱི", "gyi"),                 # ག with subjoined ཡ: no separator
    ("འོད", "'od"),
    ("པའི", "pa'i"),
    ("མགོན་པོའོ", "mgon po'o"),
    ("ཚྭ", "tshwa"),               # wa-zur
    ("ཨ་ཨེ་མ་ཧོ", "a e ma ho"),
    ("རྡོ་རྗེའི", "rdo rje'i"),
    ("གཡསགཉིས", "g.yas gnyis"),    # missing tsheg in the source
])
def test_tibetan_syllables(tibetan, expected):
    assert wylie.render(tibetan) == expected


@pytest.mark.parametrize("tibetan, expected", [
    ("ཨོཾ", "oM"), ("ཧཱུཾ", "hUM"), ("ཧྲཱིཿ", "hrIH"), ("ཕཊ", "phaT"), ("བཛྲ", "badzra"),
    ("པདྨ", "pad+ma"), ("སྭཱཧཱ", "swAhA"), ("སིདྡྷི", "sid+dhi"), ("ཀྵ", "k+Sha"), ("མཧཱ", "mahA"),
])
def test_sanskrit_units_follow_ewts(tibetan, expected):
    assert wylie.render(tibetan) == expected


def test_lines_share_the_pronunciation_segmentation():
    text = "༄༅། །པདྨ་ཡང་གསང་ཁྲོས་པའི་ལས་བྱང་\nདབང་ཆེན། །ཞེས་བྱ་བ་བཞུགས་སོ།།"
    lines = wylie.generate(text)
    assert [line.tibetan for line in lines] == [line.tibetan for line in tz.generate(text)]
    assert "".join(line.tibetan for line in lines) == text
    assert [line.wylie for line in lines] == ["pad+ma yang gsang khros pa'i las byang dbang chen",
                                              "zhes bya ba bzhugs so"]


def test_agreement_with_every_tibetan_only_mahavyutpatti_pair():
    """Measured, not asserted: DILA Mahāvyutpatti ships Tibetan and Wylie for each entry."""
    index_file = ROOT / "references/transliteration/data/reference_resources/index/dila_mahavyutpatti.entries.json"
    if not index_file.is_file():
        pytest.skip("Mahāvyutpatti is not ingested locally; run `atp evidence ingest`")
    entries = json.loads(index_file.read_text(encoding="utf-8"))["entries"]

    def norm(value: str) -> str:  # DILA writes the separator dot as gy or g-y
        return value.replace("g.y", "gy").replace("g-y", "gy")

    same = total = 0
    for entry in entries:
        if not (entry["tibetan_forms"] and entry["wylie_forms"]):
            continue
        tibetan, reference = entry["tibetan_forms"][0], entry["wylie_forms"][0]
        syllables = tz.split_syllables(tibetan)
        if "(" in tibetan or any(tz.is_sanskrit(s) for s in syllables) or "." in norm(reference) \
                or "(" in reference:
            continue
        ours, theirs = [norm(wylie.syllable(s)) for s in syllables], norm(reference).split()
        if len(ours) == len(theirs):
            total += len(ours)
            same += sum(a == b for a, b in zip(ours, theirs))
    # Measured 42,566 / 42,791 (99.47 %) on the 2026-08-30 export. The residual is dominated by
    # DILA entries whose own Tibetan and Wylie disagree (bcu/cu swapped, pa/ba), not by the rules.
    assert total > 40000
    assert same / total >= 0.99, f"{same}/{total}"
