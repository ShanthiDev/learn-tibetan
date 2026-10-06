"""Focused acceptance checks for Publication Read Model v2.3."""

from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from convert_sample import (
    DEFAULT_BUNDLE,
    DEFAULT_BUNDLE_SHA256,
    DIPLOMATIC_LAYER,
    RECITATION_LAYER,
    ROOT,
    DEFAULT_AUTHORING_STORE,
    apply_editions,
    load_bundle,
    load_registries,
    project,
    project_authoring_context,
    serialize,
    validate_publication,
)


class EditionProjectionTests(unittest.TestCase):
    """The repository store's explicit editions over the frozen v10 projection."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle()
        cls.base = project(cls.bundle)
        cls.store = json.loads(DEFAULT_AUTHORING_STORE.read_text(encoding="utf-8"))
        cls.registries = load_registries()
        cls.output = apply_editions(cls.bundle, cls.base, cls.store, cls.registries)

    def test_every_edition_pins_every_passage_once_and_default_is_explicit(self):
        editions = [value["id"] for value in self.output["editions"]]
        self.assertEqual(self.output["default_edition_id"], self.store["current_edition_id"])
        self.assertEqual(len(editions), 1 + len(self.store["editions"]))
        for section in self.output["sections"]:
            for passage in section["passages"]:
                recitation = [value for value in passage["translations"] if value["layer_id"] == RECITATION_LAYER]
                self.assertEqual(sorted(edition for value in recitation for edition in value["edition_ids"]), sorted(editions))

    def test_v10_text_is_unchanged_and_changed_passages_match_the_store_edition(self):
        v10 = self.base["editions"][0]["id"]
        for edition in self.store["editions"]:
            entries = {value["passage_id"]: value["candidate_id"] for value in edition["entries"]}
            changed = {key for key, value in entries.items() if not value.startswith("baseline:")}
            projected = next(value for value in self.output["editions"] if value["id"] == edition["id"])
            self.assertEqual(set(projected["history"]["changed_passage_ids"]), changed)
            for section, base_section in zip(self.output["sections"], self.base["sections"]):
                for passage, base_passage in zip(section["passages"], base_section["passages"]):
                    old = next(value for value in base_passage["translations"] if value["layer_id"] == RECITATION_LAYER)
                    shown_v10 = next(value for value in passage["translations"] if value["layer_id"] == RECITATION_LAYER and v10 in value["edition_ids"])
                    self.assertEqual(shown_v10["blocks"], old["blocks"])
                    shown = next(value for value in passage["translations"] if value["layer_id"] == RECITATION_LAYER and edition["id"] in value["edition_ids"])
                    self.assertEqual(shown.get("candidate_id", entries[passage["id"]]), entries[passage["id"]])

    def test_projection_is_byte_stable_and_keeps_private_references_out(self):
        again = apply_editions(self.bundle, self.base, self.store, self.registries)
        self.assertEqual(serialize(self.output), serialize(again))
        encoded = serialize(self.output) + serialize(project_authoring_context(self.bundle, self.base, self.store, self.registries))
        self.assertIsNone(re.search(r"\bT0\d\b", encoded))
        self.assertNotIn("private_references", encoded)
        self.assertNotIn("data/intake", (ROOT / "scripts/convert_sample.py").read_text(encoding="utf-8"))

    def test_post_v10_questions_target_the_edition_wording(self):
        targets = {value["id"]: value for value in self.output["targets"]}
        requests = [value for value in self.output["questions"] if value["kind"] == "reviewer_request"]
        self.assertEqual(len(requests), len(self.store["public_question_ids"]))
        for question in requests:
            self.assertTrue(question["edition_ids"])
            for target_id in question["target_ids"]:
                self.assertIn(":rev-", targets[target_id]["block_id"])


class ConverterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle()
        cls.output = project(cls.bundle)
        cls.passages = [passage for section in cls.output["sections"] for passage in section["passages"]]
        cls.targets = {target["id"]: target for target in cls.output["targets"]}

    def translation(self, passage, layer_id):
        return next(value for value in passage["translations"] if value["layer_id"] == layer_id)

    def context_questions(self, layer_id):
        result = []
        for passage in self.passages:
            questions = [question for question in self.output["questions"] if any(
                self.targets[target_id]["passage_id"] == passage["id"] and
                self.targets[target_id].get("translation_layer_id") == layer_id
                for target_id in question["target_ids"]
            )]
            if questions:
                result.append((passage, questions))
        return result

    def test_contract_is_breaking_generalized_and_current_scope_is_complete(self):
        self.assertEqual(hashlib.sha256(DEFAULT_BUNDLE.read_bytes()).hexdigest(), DEFAULT_BUNDLE_SHA256)
        self.assertEqual(self.output["version"], "2.3")
        self.assertEqual(len(self.output["sections"]), 19)
        self.assertEqual(len(self.passages), 192)
        self.assertEqual([section["id"] for section in self.output["sections"]],
                         [f"r{number:02}" for number in range(1, 20)])
        self.assertEqual(sum(len(unit["derived_from"]) for unit in self.bundle["units"]), 258)
        self.assertEqual(len(self.bundle["segments"]), 258)
        self.assertEqual({layer["id"] for layer in self.output["translation_layers"]},
                         {RECITATION_LAYER, DIPLOMATIC_LAYER})
        self.assertEqual({(layer["language"], layer["mode"]) for layer in self.output["translation_layers"]},
                         {("de", "recitation"), ("de", "diplomatic")})
        self.assertTrue(all(layer.get("style_policy") and layer.get("edition_ids")
                            for layer in self.output["translation_layers"]))
        self.assertEqual([value["language"] for value in self.output["editions"]], ["de"])
        self.assertEqual(self.output["default_edition_id"], self.output["editions"][0]["id"])
        encoded = serialize(self.output)
        for obsolete in ('"recitation_de"', '"diplomatic_de"', '"sense_open"', '"open_questions"'):
            self.assertNotIn(obsolete, encoded)
        for passage in self.passages:
            self.assertEqual({value["layer_id"] for value in passage["translations"]},
                             {RECITATION_LAYER, DIPLOMATIC_LAYER})
        kinds = {block["kind"] for passage in self.passages
                 for block in self.translation(passage, RECITATION_LAYER)["blocks"]}
        self.assertEqual(kinds, {"prose", "verse", "rubric", "mantra", "heading", "paratext"})

    def test_synthetic_additional_language_uses_the_same_contract_and_reader_lookup(self):
        synthetic = deepcopy(self.output)
        layer_id = "translation:en:readable"
        synthetic["translation_layers"].append({
            "id": layer_id, "language": "en", "mode": "readable", "label": "Readable English",
            "description": "Synthetic architecture test", "edition_ids": [synthetic["editions"][0]["id"]],
            "style_policy": {"label": "Synthetic test policy"},
            "attribution_ids": ["agent:model:claude-fable-5-1"],
        })
        synthetic["editions"][0]["translation_layer_ids"].append(layer_id)
        passage = synthetic["sections"][0]["passages"][0]
        passage["translations"].append({
            "layer_id": layer_id, "edition_ids": [synthetic["editions"][0]["id"]],
            "blocks": [{"id": "block:synthetic:r01-u01", "kind": "prose", "text": "Synthetic."}],
            "source_status": ["synthetic-test"],
        })
        validate_publication(synthetic)
        app = (ROOT / "src/App.tsx").read_text(encoding="utf-8")
        self.assertIn("layers.map", app)
        self.assertIn("translationFor(passage, layer.id, ", app)
        self.assertNotIn("recitation_de", app)
        self.assertNotIn("diplomatic_de", app)

    def test_all_namespaces_and_references_validate_and_builds_are_identical(self):
        validate_publication(self.output)
        self.assertEqual(serialize(self.output), serialize(project(self.bundle)))
        namespaces = {
            "layers": self.output["translation_layers"], "attributions": self.output["attributions"],
            "references": self.output["references"], "targets": self.output["targets"],
            "annotations": self.output["annotations"], "questions": self.output["questions"],
            "issues": self.output["issues"], "passages": self.passages,
        }
        for name, records in namespaces.items():
            with self.subTest(name=name):
                self.assertEqual(len(records), len({record["id"] for record in records}))
        blocks = [block for passage in self.passages
                  for block in passage["source"]["blocks"] +
                  [block for translation in passage["translations"] for block in translation["blocks"]]]
        self.assertEqual(len(blocks), len({block["id"] for block in blocks}))

    def test_exact_tibetan_stable_deep_links_blocks_and_selectors(self):
        source = {unit["local_id"].lower(): unit["source"]["quote"] for unit in self.bundle["units"]}
        self.assertEqual(set(source), {passage["id"] for passage in self.passages})
        for passage in self.passages:
            projected = "".join(block["text"] for block in passage["source"]["blocks"])
            self.assertEqual(projected.encode("utf-8"), source[passage["id"]].encode("utf-8"))
        for old_id in ("r01-u01", "r04-u01", "r04-u05", "r04-u06", "r10-u01", "r10-u03"):
            self.assertIn(old_id, source)
        selectors = [target for target in self.output["targets"] if "selector" in target]
        self.assertTrue(selectors)
        blocks = {block["id"]: block["text"] for passage in self.passages
                  for translation in passage["translations"] for block in translation["blocks"]}
        for target in selectors:
            selector = target["selector"]
            self.assertEqual(selector["coordinate_system"], "unicode_code_points")
            self.assertEqual(blocks[target["block_id"]][selector["start"]:selector["end"]], selector["quote"])

    def test_legacy_child_ids_use_content_and_disambiguate_identical_siblings(self):
        mutated = deepcopy(self.bundle)
        duplicate = deepcopy(mutated["units"][0]["blocks"][0])
        mutated["units"][0]["blocks"].append(duplicate)
        output = project(mutated)
        passage = output["sections"][0]["passages"][0]
        ids = [block["id"] for block in self.translation(passage, RECITATION_LAYER)["blocks"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(any(":occurrence-2" in value for value in ids))
        renamed = deepcopy(self.output)
        original_id = renamed["translation_layers"][0]["id"]
        renamed["translation_layers"][0]["label"] = "Geändertes Anzeigelabel"
        self.assertEqual(renamed["translation_layers"][0]["id"], original_id)

    def test_diplomatic_segments_notes_alternatives_and_status_survive(self):
        annotations = self.output["annotations"]
        diplomatic = [annotation for annotation in annotations if annotation["family"] == "diplomatic"]
        self.assertEqual(sum(annotation["kind"] == "diplomatic_note" for annotation in diplomatic), 515)
        self.assertEqual(sum(annotation["kind"] == "diplomatic_alternative" for annotation in diplomatic), 61)
        self.assertTrue(all(annotation["source_id"].startswith("sj2017.de.dipl:") for annotation in diplomatic))
        self.assertTrue(all("machine-generated" in annotation["source_status"] for annotation in diplomatic))
        expected_parts = sum(len(segment["translation"]["parts"]) for segment in self.bundle["segments"])
        actual_parts = sum(len(self.translation(passage, DIPLOMATIC_LAYER)["blocks"])
                           for passage in self.passages)
        self.assertEqual(actual_parts, expected_parts)
        block_ids = {block["id"] for passage in self.passages
                     for block in self.translation(passage, DIPLOMATIC_LAYER)["blocks"]}
        self.assertTrue(all(any(segment["id"] in block_id for block_id in block_ids)
                            for segment in self.bundle["segments"]))

    def test_questions_issues_multi_targets_and_owner_supplied_attribution(self):
        questions, issues = self.output["questions"], self.output["issues"]
        self.assertEqual(len(questions), 201)
        self.assertEqual(len(issues), 58)
        self.assertEqual(len({question["id"] for question in questions}), 201)
        self.assertEqual(len({issue["id"] for issue in issues}), 58)
        self.assertEqual(sum(bool(question["related_issue_ids"]) for question in questions), 58)
        self.assertEqual(sum(len(question["target_ids"]) > 1 for question in questions), 58)
        self.assertTrue(all(question["primary_target_id"] in question["target_ids"]
                            for question in questions))
        self.assertTrue(all("selector" in self.targets[question["primary_target_id"]]
                            for question in questions
                            if self.targets[question["primary_target_id"]].get("block_id")))
        self.assertTrue(all(issue["status"] == "open" for issue in issues))
        self.assertEqual(len(self.context_questions(RECITATION_LAYER)), 119)
        self.assertEqual(sum(len(values) for _, values in self.context_questions(RECITATION_LAYER)), 201)
        self.assertEqual(len(self.context_questions(DIPLOMATIC_LAYER)), 37)
        self.assertEqual(sum(len(values) for _, values in self.context_questions(DIPLOMATIC_LAYER)), 58)
        self.assertIn("issue:P49-S01-2", {issue["id"] for issue in issues})
        self.assertIn("issue:P51-S03-1", {issue["id"] for issue in issues})
        self.assertEqual(sum(question["attribution"]["attributed_to"] == ["agent:model:gpt-5.6-sol-high"]
                             for question in questions), 130)
        self.assertEqual(sum(issue["attribution"]["attributed_to"] == ["agent:model:gpt-5.6-sol-high"]
                             for issue in issues), 29)
        self.assertTrue(all(value["attribution"]["recorded_by"] == ["agent:human:andreas"]
                            for value in questions + issues))

    def test_sense_offen_cannot_reenter_or_become_a_question(self):
        self.assertFalse(any("offen" in unit.get("sense", {}) for unit in self.bundle["units"]
                             if unit.get("sense") is not None))
        self.assertNotIn("sense_open", serialize(self.output))
        mutated = deepcopy(self.bundle)
        mutated["units"][0]["sense"] = deepcopy(mutated["units"][0]["sense"] or {})
        mutated["units"][0]["sense"]["offen"] = "Darf niemals projiziert werden?"
        with self.assertRaisesRegex(ValueError, "sense.offen to be absent"):
            project(mutated)

    def test_only_exact_house_decisions_are_structured_references(self):
        source_refs = {reference for unit in self.bundle["units"] for mark in unit.get("marks", [])
                       for reference in mark.get("refs", [])}
        expected = {reference for reference in source_refs if re.fullmatch(r"HD-\d{3}", reference)}
        target_ids = {target["id"] for target in self.output["references"]}
        self.assertEqual(target_ids, expected)
        self.assertEqual(len(target_ids), 40)
        projected_refs = {reference for item in self.output["annotations"] + self.output["questions"]
                          for reference in item["reference_ids"]}
        self.assertEqual(projected_refs, target_ids)
        self.assertTrue(any(reference.startswith("SJ-") for reference in source_refs))
        self.assertTrue(any(reference.startswith("tz:") for reference in source_refs))
        self.assertFalse(any(reference.startswith(("SJ-", "tz:", "issue:")) for reference in projected_refs))

    def test_meaning_pronunciation_and_attribution_status_survive(self):
        self.assertEqual(sum("meaning" in passage for passage in self.passages), 165)
        self.assertTrue(all("pronunciation" in passage for passage in self.passages))
        layer_ids = {layer["id"] for layer in self.output["translation_layers"]}
        self.assertFalse(any(passage["pronunciation"]["id"] in layer_ids for passage in self.passages))
        for passage in self.passages:
            aid = passage["pronunciation"]
            self.assertEqual((aid["language"], aid["status"], aid["generator"]["name"]),
                             ("de", "generated", "atp.phonetics.tz"))
            source = "".join(block["text"] for block in passage["source"]["blocks"])
            for variant in aid["variants"]:
                self.assertEqual("".join(line["tibetan"] for line in variant["lines"]), source)
        attribution_ids = {value["id"] for value in self.output["attributions"]}
        self.assertEqual(attribution_ids, {
            "agent:model:claude-fable-5-1", "agent:model:claude-opus-5",
            "agent:model:gpt-5.6-sol-high", "agent:human:andreas",
        })
        self.assertFalse(any(value["kind"] == "human" and value["id"] != "agent:human:andreas"
                             for value in self.output["attributions"]))

    def test_unknown_internal_fields_do_not_cross_the_boundary(self):
        mutated = deepcopy(self.bundle)
        mutated["section_map"]["resolved_config"] = "PRIVATE_SENTINEL"
        mutated["units"][0]["resolved_config"] = {"provider": "PRIVATE_SENTINEL"}
        mutated["units"][0]["blocks"][0]["internal"] = "PRIVATE_SENTINEL"
        mutated["segments"][0]["provenance"]["private"] = "PRIVATE_SENTINEL"
        output = serialize(project(mutated))
        self.assertEqual(output, serialize(self.output))
        self.assertNotIn("PRIVATE_SENTINEL", output)

    def test_validation_fails_clearly_on_dangling_and_corrupt_relationships(self):
        malformed = deepcopy(self.output)
        malformed["questions"][0]["target_ids"] = ["target:missing"]
        with self.assertRaisesRegex(ValueError, "dangling target"):
            validate_publication(malformed)
        malformed = deepcopy(self.output)
        malformed["questions"][0]["primary_target_id"] = malformed["targets"][-1]["id"]
        with self.assertRaisesRegex(ValueError, "primary Question target"):
            validate_publication(malformed)
        malformed = deepcopy(self.output)
        selector = next(target["selector"] for target in malformed["targets"] if "selector" in target)
        selector["quote"] += "x"
        with self.assertRaisesRegex(ValueError, "selector quote"):
            validate_publication(malformed)
        malformed = deepcopy(self.output)
        malformed["annotations"][1]["id"] = malformed["annotations"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate ID"):
            validate_publication(malformed)

    def test_cli_is_deterministic_and_failure_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "publication.json"
            command = [sys.executable, str(ROOT / "scripts/convert_sample.py"),
                       "--bundle", str(DEFAULT_BUNDLE),
                       "--output", str(output)]
            subprocess.run(command, check=True, capture_output=True)
            first = output.read_bytes()
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(first, output.read_bytes())
            bad = Path(temp) / "bad.zip"
            bad.write_bytes(b"not a zip")
            result = subprocess.run(command[:2] + ["--bundle", str(bad), "--output", str(output)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("unexpected v10 SHA-256", result.stderr)
            self.assertEqual(first, output.read_bytes())

    def test_pronunciation_variants_are_declared_and_generated(self):
        variants = self.output["pronunciation_variants"]
        self.assertEqual([(v["id"], v["label"], v["default"]) for v in variants], [
            ("tz-aktuell", "TZ aktuell", True), ("tz-gebetsbuch", "TZ Gebetsbuch", False),
            ("silbengetreu", "Silbengetreu", False)])
        first = self.passages[0]["pronunciation"]["variants"]
        self.assertEqual([v["variant_id"] for v in first], ["tz-aktuell", "tz-gebetsbuch", "silbengetreu"])
        self.assertTrue(first[0]["lines"][0]["pronunciation"].startswith("pema yang sang thrö pä"))
        self.assertTrue(first[2]["lines"][0]["pronunciation"].startswith("padma yang sang thrö pä"))

    def test_wylie_transliteration_shares_pronunciation_lines(self):
        for passage in self.passages:
            transliteration = passage["transliteration"]
            self.assertEqual(transliteration["scheme"], "ewts")
            self.assertEqual([line["tibetan"] for line in transliteration["lines"]],
                             [line["tibetan"] for line in passage["pronunciation"]["variants"][0]["lines"]])
        first = self.passages[0]["transliteration"]["lines"][0]["text"]
        self.assertTrue(first.startswith("pad+ma yang gsang khros pa'i las byang"))

    def test_pronunciation_invariants_fail_loudly(self):
        for mutate, message in (
            (lambda p: p["sections"][0]["passages"][0]["pronunciation"]["variants"][0]["lines"][0]
             .__setitem__("tibetan", "བོད"), "concatenate to the exact Tibetan source"),
            (lambda p: p["sections"][0]["passages"][0]["pronunciation"]["variants"].pop(),
             "exactly one entry per declared variant"),
            (lambda p: p["sections"][0]["passages"][0].pop("pronunciation"), "lacks a pronunciation"),
            (lambda p: p["pronunciation_variants"][1].__setitem__("default", True), "exactly one default"),
            (lambda p: p["sections"][0]["passages"][0]["transliteration"]["lines"][0].__setitem__("tibetan", "བོད"),
             "transliteration lines must use the pronunciation line slices"),
        ):
            mutated = deepcopy(self.output)
            mutate(mutated)
            with self.assertRaisesRegex(ValueError, message):
                validate_publication(mutated)

    def test_malformed_source_relationships_fail_clearly(self):
        malformed = deepcopy(self.bundle)
        malformed["segments"].pop()
        with self.assertRaisesRegex(ValueError, "missing diplomatic segment"):
            project(malformed)
        malformed = deepcopy(self.bundle)
        malformed["units"][1]["id"] = malformed["units"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate recitation unit"):
            project(malformed)
        malformed = deepcopy(self.bundle)
        malformed["segments"][0]["translation"]["parts"][0]["role"] = "MYSTERY"
        with self.assertRaisesRegex(ValueError, "unknown diplomatic role"):
            project(malformed)



if __name__ == "__main__":
    unittest.main()
