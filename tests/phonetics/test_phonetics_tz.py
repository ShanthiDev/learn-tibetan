"""TZ-style German phonetics generator (learn_tibetan.phonetics.tz)."""

import difflib
from pathlib import Path

import pytest

from learn_tibetan.phonetics import tz

HELDOUT = Path(__file__).parent / "fixtures/gebetsbuch_heldout.tsv"


def say(text: str, variant="tz-aktuell") -> str:
    return tz.render(text, variant)


@pytest.mark.parametrize("tibetan, expected", [
    ("བསྒྲུབས", "drub"),     # prefix, superscript, root, ra-subscript, suffix, second suffix
    ("སངས་རྒྱས", "sang gyä"),  # ས suffix: umlaut, silent
    ("ཆོས", "tschö"),
    ("གསལ", "säl"),            # ལ suffix: umlaut, kept
    ("དབང", "wang"),           # prefix ད + བ -> w
    ("དབུས", "ü"),
    ("དབྱིངས", "ying"),        # ད + བྱ -> y
    ("ཕྱག", "tschag"),         # ya-subscript on ph
    ("བྱང་ཆུབ", "dschang tschub"),
    ("ཁྲོ", "thro"),
    ("ཟླ་བ", "da wa"),         # ཟླ -> d; particle བ after a syllable -> w
    ("ལྷ", "lha"),
    ("པའི", "pä"),             # fused genitive
    ("མཁའི", "khä"),
    ("བསྔོའོ", "ngo-o"),
    ("པོའང", "po-ang"),
    ("གཡསགཉིས", "yä nyi"),     # missing tsheg in the source is split
])
def test_tibetan_syllable_rules(tibetan, expected):
    assert say(tibetan) == expected


def test_word_level_switches():
    text = "བཀྲ་ཤིས་བདེ་ལེགས་ཤོག རྡོ་རྗེ་འཛིན"
    assert say(text, "tz-aktuell") == "tra schi de leg scho dor dsche dzin"
    assert say(text, "silbengetreu") == "tra schi de leg schog do dsche dzin"
    assert say("རྡོ་རྗེའི") == "dor dsche"
    assert say("རྡོ") == "do"                     # connected speech needs the following རྗེ
    assert say("ཅི") == "tschi"
    assert say("ལྷན") == "lhän"


@pytest.mark.parametrize("aktuell, gebetsbuch, tibetan", [
    ("tshog", "tsog", "ཚོགས"),
    ("tham", "tam", "ཐམས"),
    ("thrag", "trag", "ཁྲག"),
    ("kham", "kam", "ཁམས"),
    ("khyen", "kyen", "མཁྱེན"),
    ("phän", "pän", "ཕན"),
    ("dzin", "dsin", "འཛིན"),
    ("tschü", "tschu", "བཅུའི"),   # genitive umlaut after o/u only in tz-aktuell
    ("pä", "pä", "པའི"),           # after a: both
    ("tschag", "tschag", "ཕྱག"),   # tsch/dsch/sch/g/d/b identical
    ("gyäl", "gyäl", "རྒྱལ"),
])
def test_gebetsbuch_differs_only_in_aspiration_dz_and_genitive(aktuell, gebetsbuch, tibetan):
    assert say(tibetan, "tz-aktuell") == aktuell
    assert say(tibetan, "tz-gebetsbuch") == gebetsbuch


MANTRA = ("ཨོཾ་བཛྲ་ས་མ་ཡ་ཛཿ ཞེས་བྱིན་གྱིས་བརླབས། ཨོཾ་སྭ་བྷཱ་ཝ་ཤུདྡྷཱཿ་སརྦ་དྷརྨཱཿ་སྭ་བྷཱ་ཝ་ཤུདྡྷོ྅ཧཾ། "
          "ཧཱུཾ་ཕཊ་སྭཱཧཱ། པདྨ་ཀྲོ་དྷ")


def test_mantras_are_ordinary_syllables():
    """No mantra detection: every syllable is read on its own, lower case."""
    assert say(MANTRA, "tz-aktuell") == (
        "om bendsa sa ma ya dza sche dschin gyi lab / om sa bha wa shuddha sarva dharma sa bha wa "
        "shuddho hang / hung phä soha / pema tro dha")
    assert say(MANTRA, "silbengetreu") == (
        "om badzra sa ma ya dzah sche dschin gyi lab / om sa bha wa shuddhah sarba dharmah sa bha wa "
        "shuddhoham / hung phat swaha / padma tro dha")


def test_individual_switches():
    assert say("ཧཱུཾ", tz.Options(anusvara_after_u="m")) == "hum"
    assert say("ཀཾ་ལས་བྱུང་། ཧཱུཾ་ལས", tz.Options(sanskrit_capitals=True)) == "KAM lä dschung / HUNG lä"
    assert say("སཏྭ", tz.Options()) == "sato" and say("སཏྭ", tz.Options(sanskrit="letters")) == "satwa"
    with pytest.raises(ValueError):
        tz.Options(dz="z")


def test_sanskrit_detection():
    assert tz.is_sanskrit("ཧཱུཾ") and tz.is_sanskrit("པདྨ") and tz.is_sanskrit("མྲྀ")
    assert not tz.is_sanskrit("བསྒྲུབས") and not tz.is_sanskrit("པོའི")
    assert say("སྨན་རཀ་གཏོར་མ") == "män rak tor ma"


@pytest.mark.parametrize("text", [
    "༄༅། །པདྨ་ཡང་གསང་ཁྲོས་པའི་ལས་བྱང་\nདབང་ཆེན། །ཞེས་བྱ་བ་བཞུགས་སོ།།",
    "ཧཱུཾ། ཨོཾ་ཨཱཿཧཱུཾ། ",
    "བདག་ནི་དེང་ནས་\nཚེ་རབས་ཐམས་ཅད་དུ། །",
])
def test_lines_are_exact_contiguous_slices(text):
    lines = tz.generate(text)
    assert "".join(line.tibetan for line in lines) == text
    assert all(line.pronunciation for line in lines)


def test_gebetsbuch_heldout_regression():
    """TZ Gebetsbuch phonetics vs generator; the Tibetan side is assistant-reconstructed."""
    same = total = 0
    for row in HELDOUT.read_text(encoding="utf-8").splitlines():
        if not row or row.startswith("#"):
            continue
        reference, tibetan = row.split("\t")
        ref = reference.split()
        out = say(tibetan, "tz-gebetsbuch").replace(" / ", " ").replace("-", " ").split()
        total += len(ref)
        same += sum(b.size for b in difflib.SequenceMatcher(a=ref, b=out, autojunk=False).get_matching_blocks())
    assert total == 566
    assert same / total >= 0.97, f"{same}/{total}"
