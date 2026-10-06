from learn_tibetan.content import build

C = build()
ITEMS = {it["id"]: it for it in C["items"]}


def test_alphabet_order_and_groups():
    letters = [it for it in C["items"] if it["kind"] == "letter"]
    assert "".join(it["tibetan"] for it in letters) == "ཀཁགངཅཆཇཉཏཐདནཔཕབམཙཚཛཝཞཟའཡརལཤསཧཨ"
    assert [len(g["itemIds"]) for g in C["groups"]] == [4, 4, 4, 4, 4, 4, 4, 2]
    assert len({it["wylie"] for it in letters}) == 30


def test_generated_fields_and_unique_ids():
    assert len(ITEMS) == len(C["items"]) == 150
    assert (ITEMS["l-ca"]["wylie"], ITEMS["l-ca"]["tz"], ITEMS["l-ca"]["devanagari"]) == ("ca", "tscha", "च")
    assert ITEMS["v-ki"]["tibetan"] == "ཀི" and ITEMS["v-ki"]["baseId"] == "l-ka"
    assert ITEMS["l-_a"]["wylie"] == "'a" and ITEMS["l-a"]["wylie"] == "a"
    assert ITEMS["l-ka"]["phonology"] == {"aspiration": "unbehaucht", "tone": "hoch", "hintDe": ITEMS["l-ka"]["phonology"]["hintDe"]}
    assert all(it["phonology"]["tone"] in {"hoch", "tief"} for it in C["items"] if it["kind"] == "letter")


def test_lessons_reference_existing_items():
    assert len(C["lessons"]) == 22
    assert all(i in ITEMS for les in C["lessons"] for i in les["newItemIds"] + les.get("introItemIds", []))
