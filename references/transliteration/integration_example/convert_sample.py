"""Disposable, stdlib-only v10 projector for Publication Read Model v2.3 (editions over v10 + repo-native store)."""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY / "src"))
from atp.authoring.core import (V10_EDITION_ID, body_hash, candidate_agent_id, empty_registries, validate_package,
                                validate_registries, validate_store)
from atp.phonetics import tz, wylie
DEFAULT_BUNDLE = REPOSITORY / "data/reference_hayagriva_atp_lite/hayagriva_atp_lite_bundle_rez_v10_question_curated.zip"
DEFAULT_BUNDLE_SHA256 = "24230b7d3ab9047364176182b0d67ca49ba0d06f83927f6d24654087a37146d7"
DEFAULT_AUTHORING_STORE = REPOSITORY / "data/authoring/hayagriva/store.json"
DEFAULT_RULES = REPOSITORY / "data/rules/de/rules.json"
DEFAULT_EVIDENCE = REPOSITORY / "data/evidence/registry.json"
DEFAULT_AUTHORING_OUTPUT = ROOT / "src/generated/authoring-context.json"
KINDS = {"prose", "verse", "rubric", "mantra", "heading", "paratext"}
MARKS = {"decision", "alternative", "addition", "omission", "question"}
ROLES = {
    "MAIN": "prose", "RUBRIC": "rubric", "HEADING": "heading",
    "TITLE": "heading", "PARATEXT": "paratext", "BLUE_TEXT": "paratext",
}
SOURCE_PREFIX = "atp_lite/"
RECITATION_LAYER = "translation:de:recitation"
DIPLOMATIC_LAYER = "translation:de:diplomatic"
EDITION_ID = "edition:hayagriva-de-working-v10"
CURATION_AGENT = "agent:model:gpt-5.6-sol-high"
QUESTION_RECORDER = "agent:human:andreas"


def require(condition, where, message):
    if not condition:
        raise ValueError(f"{where}: {message}")


def obj(value, where):
    require(isinstance(value, dict), where, "expected an object")
    return value


def text(value, where):
    require(isinstance(value, str) and bool(value.strip()), where, "expected non-empty text")
    return value  # Never normalize Tibetan or rewrite source whitespace.


def items(value, where, nonempty=True):
    require(isinstance(value, list), where, "expected an array")
    require(not nonempty or bool(value), where, "expected a non-empty array")
    return value


def statuses(value, where):
    return [text(item, where) for item in items(value, where, nonempty=False)]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()[:16]


def _read_json(archive, path):
    full_path = SOURCE_PREFIX + path
    try:
        return json.loads(archive.read(full_path).decode("utf-8-sig"))
    except KeyError as exc:
        raise ValueError(f"bundle: missing required member {full_path}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{full_path}: invalid UTF-8 JSON: {exc}") from exc


def _read_jsonl(archive, path):
    full_path = SOURCE_PREFIX + path
    try:
        raw = archive.read(full_path).decode("utf-8-sig")
    except KeyError as exc:
        raise ValueError(f"bundle: missing required member {full_path}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"{full_path}: invalid UTF-8: {exc}") from exc
    records = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{full_path}:{line_number}: invalid JSON: {exc}") from exc
    return records


def load_bundle(path=DEFAULT_BUNDLE):
    """Read only the exact allowlisted members used by the temporary projector."""
    path = Path(path)
    try:
        observed_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        require(observed_sha256 == DEFAULT_BUNDLE_SHA256, "bundle",
                f"unexpected v10 SHA-256: {observed_sha256}")
        with ZipFile(path) as archive:
            section_map = obj(_read_json(archive, "recitation/sections.json"), "sections.json")
            sections = items(section_map.get("sections"), "sections.json.sections")
            diplomatic_files = items(section_map.get("diplomatic_files"), "sections.json.diplomatic_files")
            units, segments, runs = [], [], []
            for section in sections:
                section_id = text(obj(section, "sections.json.section").get("id"), "section.id")
                records = _read_jsonl(archive, f"recitation/sj2017.de.rez.{section_id}.jsonl")
                units.extend(record for record in records if record.get("type") == "rec_unit")
                runs.extend(record for record in records if record.get("type") == "run")
            for source_path in diplomatic_files:
                records = _read_jsonl(archive, text(source_path, "diplomatic_files"))
                segments.extend(record for record in records if record.get("type") == "segment")
                runs.extend(record for record in records if record.get("type") == "run")
            decisions = [record for record in _read_jsonl(archive, "recitation/house_decisions.jsonl")
                         if record.get("type") == "house_decision"]
            curation = _read_jsonl(archive, "question_curation_mapping_v0.1.jsonl")
    except (BadZipFile, OSError) as exc:
        raise ValueError(f"bundle: cannot read {path}: {exc}") from exc
    return {
        "section_map": section_map, "sections": deepcopy(sections), "units": units,
        "segments": segments, "house_decisions": decisions, "runs": runs,
        "question_curation": curation, "bundle_sha256": observed_sha256,
    }


def pronunciation_variants():
    return [{"id": variant.id, "label": variant.label, "description": variant.description,
             "default": variant.id == tz.DEFAULT_VARIANT} for variant in tz.VARIANTS.values()]


def project_transliteration(passage_id, source_block):
    """Wylie (EWTS) transliteration with the same line slices as the pronunciation aid."""
    return {
        "id": f"transliteration:ewts:{passage_id}", "scheme": "ewts", "status": "generated",
        "generator": {"name": "atp.phonetics.wylie", "version": tz.VERSION},
        "source_block_id": source_block["id"],
        "lines": [{"tibetan": line.tibetan, "text": line.wylie} for line in wylie.generate(source_block["text"])],
    }


def project_pronunciation(passage_id, source_block):
    """Generated pronunciation aid, one variant per generator variant (atp.phonetics.tz)."""
    variants = []
    for variant_id in tz.VARIANTS:
        lines = [{"tibetan": line.tibetan, "pronunciation": line.pronunciation}
                 for line in tz.generate(source_block["text"], variant_id)]
        variants.append({"variant_id": variant_id, "lines": lines})
    return {
        "id": f"pronunciation:de:{passage_id}", "language": "de", "status": "generated",
        "generator": {"name": "atp.phonetics.tz", "version": tz.VERSION},
        "source_block_id": source_block["id"], "variants": variants,
    }


def _agent_id(agent, where):
    agent = obj(agent, where)
    require(agent.get("kind") == "model", where, "only explicit model run agents are supported")
    model = text(agent.get("model"), where + ".model")
    require(re.fullmatch(r"[a-z0-9-]+", model), where, "model name is not ID-safe")
    return "agent:model:" + model


def _synthesized_id(prefix, parent, payload, seen_ids, state, where):
    payload_key = canonical(payload)
    base = f"{prefix}:{parent}:{digest(payload)}"
    prior_payload = state["payloads"].get(base)
    require(prior_payload is None or prior_payload == payload_key, where,
            "synthesized ID hash collision between different legacy children")
    state["payloads"][base] = payload_key
    occurrence = state["counts"].get(base, 0) + 1
    state["counts"][base] = occurrence
    value = base if occurrence == 1 else f"{base}:occurrence-{occurrence}"
    require(value not in seen_ids, where, "synthesized ID collision")
    seen_ids.add(value)
    return value


def _block(value, where, identity_parent, seen_block_ids, synth_state):
    source = obj(value, where)
    kind = source.get("kind")
    require(isinstance(kind, str) and kind in KINDS, where, "unknown block kind")
    if kind == "verse":
        result = {"kind": kind, "text": "\n".join(
            text(line, where + ".lines") for line in items(source.get("lines"), where + ".lines")
        )}
    else:
        key = "recite" if kind == "mantra" else "text"
        result = {"kind": kind, "text": text(source.get(key), where + "." + key)}
    if kind == "mantra":
        for key in ("repeat", "iast", "note"):
            if source.get(key) is not None:
                result[key] = text(source[key], where + "." + key)
    block_id = _synthesized_id("block", identity_parent, result, seen_block_ids, synth_state, where)
    return {"id": block_id, **result}


def _positions(haystack, needle):
    positions, start = [], 0
    while True:
        index = haystack.find(needle, start)
        if index < 0:
            return positions
        positions.append(index)
        start = index + 1


class TargetRegistry:
    def __init__(self):
        self.targets = []
        self.by_key = {}
        self.key_by_id = {}

    def add(self, passage_id, scope, translation_layer_id=None, block_id=None, selector=None):
        value = {"passage_id": passage_id, "scope": scope}
        if translation_layer_id is not None:
            value["translation_layer_id"] = translation_layer_id
        if block_id is not None:
            value["block_id"] = block_id
        if selector is not None:
            value["selector"] = selector
        key = canonical(value)
        if key in self.by_key:
            return self.by_key[key]
        target_id = f"target:{passage_id}:{digest(value)}"
        require(target_id not in self.key_by_id or self.key_by_id[target_id] == key,
                passage_id, "synthesized target ID collision")
        self.by_key[key] = target_id
        self.key_by_id[target_id] = key
        self.targets.append({"id": target_id, **value})
        return target_id

    def layer(self, passage_id, layer_id):
        return self.add(passage_id, "translation", translation_layer_id=layer_id)

    def block(self, passage_id, scope, block_id, layer_id=None):
        return self.add(passage_id, scope, translation_layer_id=layer_id, block_id=block_id)

    def quote_or_layer(self, passage_id, layer_id, blocks, quote, where):
        matches = [(block, start) for block in blocks for start in _positions(block["text"], quote)]
        require(matches, where, "annotation anchor is absent from its translation layer")
        if len(matches) != 1:
            return self.layer(passage_id, layer_id)
        block, start = matches[0]
        selector = {
            "type": "text_position", "coordinate_system": "unicode_code_points",
            "start": start, "end": start + len(quote), "quote": quote,
        }
        return self.add(passage_id, "translation", translation_layer_id=layer_id,
                        block_id=block["id"], selector=selector)


def project(bundle):
    """Project the current corpus into generalized Publication Read Model v2.0."""
    bundle = obj(bundle, "bundle")
    section_records = items(bundle.get("sections"), "bundle.sections")
    unit_records = items(bundle.get("units"), "bundle.units")
    segment_records = items(bundle.get("segments"), "bundle.segments")
    decision_records = items(bundle.get("house_decisions"), "bundle.house_decisions")
    run_records = items(bundle.get("runs"), "bundle.runs")
    curation_records = items(bundle.get("question_curation"), "bundle.question_curation")
    require(len(curation_records) == 233, "bundle.question_curation",
            "expected the complete v0.1 mapping ledger")

    runs, attributions = {}, {}
    for run in run_records:
        run = obj(run, "run")
        run_id = text(run.get("id"), "run.id")
        require(run_id not in runs, run_id, "duplicate run")
        attribution_id = _agent_id(run.get("agent"), run_id + ".agent")
        runs[run_id] = attribution_id
        model = attribution_id.removeprefix("agent:model:")
        attributions.setdefault(attribution_id, {
            "id": attribution_id, "kind": "model", "label": model,
            "detail": "Machine agent explicitly recorded by the source bundle's translation run.",
        })
    attributions[CURATION_AGENT] = {
        "id": CURATION_AGENT, "kind": "model", "label": "GPT-5.6 Sol (high)",
        "detail": "Owner-asserted author of the wording changes and atomic restructuring in Question Curation v0.1 on 2026-09-24; no human authorship is claimed.",
    }
    attributions[QUESTION_RECORDER] = {
        "id": QUESTION_RECORDER, "kind": "human", "label": "Andreas",
        "detail": "Owner-asserted recorder/submitting editor of the curated Questions and Issues; authorship is represented separately.",
    }

    curated_question_keys, curated_issue_ids = set(), set()
    for record in curation_records:
        action = record.get("action")
        if action == "rewrite_question":
            curated_question_keys.add((text(record.get("unit"), "curation.unit"),
                                       text(record.get("mark"), "curation.mark")))
        elif action in {"split_question_component", "materialize_question_from_sense"}:
            curated_question_keys.add((text(record.get("unit"), "curation.unit"),
                                       text(record.get("new_mark"), "curation.new_mark")))
        elif action == "split_issue":
            curated_issue_ids.update(text(value, "curation.curated_issues") for value in
                                     items(record.get("curated_issues"), "curation.curated_issues"))

    segments = {}
    for segment in segment_records:
        segment = obj(segment, "segment")
        segment_id = text(segment.get("id"), "segment.id")
        require(segment_id not in segments, segment_id, "duplicate diplomatic segment")
        segments[segment_id] = segment
    decisions = {}
    for decision in decision_records:
        decision = obj(decision, "house_decision")
        decision_id = text(decision.get("id"), "house_decision.id")
        require(re.fullmatch(r"HD-\d{3}", decision_id), decision_id, "invalid House Decision ID")
        require(decision_id not in decisions, decision_id, "duplicate House Decision")
        decisions[decision_id] = decision
    units_by_section, all_unit_ids = {}, set()
    for unit in unit_records:
        unit = obj(unit, "rec_unit")
        unit_id = text(unit.get("id"), "rec_unit.id")
        require(unit_id not in all_unit_ids, unit_id, "duplicate recitation unit")
        all_unit_ids.add(unit_id)
        units_by_section.setdefault(text(unit.get("section"), unit_id + ".section"), []).append(unit)

    result = {
        "version": "2.3", "id": "hayagriva-reader-phase1",
        "release": {"id": "hayagriva-v10-question-curated",
                    "source_bundle_sha256": text(bundle.get("bundle_sha256"), "bundle.bundle_sha256")},
        "metadata": {
            "title": "Hayagrīva", "subtitle": "Der Wohlklang des Lachens des Mächtigen",
            "edition_note": "Vollständiger Arbeitsstand aus v10/question-curated · R01–R19. Die Übersetzungen und Sinnskizzen sind maschinell erstellt; die offenen Fragen wurden in einem maschinellen Kurationslauf redaktionell überarbeitet, aber nicht beantwortet.",
        },
        "editions": [{
            "id": EDITION_ID, "label": "v10", "language": "de", "status": "unreviewed-working-edition",
            "translation_layer_ids": [RECITATION_LAYER, DIPLOMATIC_LAYER],
            "note": "Maschinell erstellte Ausgangsfassung (ATP-lite v10, eingefroren).",
        }],
        "default_edition_id": EDITION_ID,
        "pronunciation_variants": pronunciation_variants(),
        "translation_layers": [
            {
                "id": RECITATION_LAYER, "language": "de", "mode": "recitation",
                "label": "Rezitation", "description": "Für das Lesen und Rezitieren",
                "edition_ids": [EDITION_ID],
                "style_policy": {"label": "TZ Hamburg, Praxisheft-Stil",
                                 "terminology": "TZ-Terminologie mit Projektglossar"},
                "attribution_ids": ["agent:model:claude-fable-5-1"],
            },
            {
                "id": DIPLOMATIC_LAYER, "language": "de", "mode": "diplomatic",
                "label": "Diplomatisch", "description": "Nahe am Wortlaut der Vorlage",
                "edition_ids": [EDITION_ID],
                "style_policy": {"label": "Diplomatische Arbeitsübersetzung",
                                 "terminology": "Projektglossar"},
                "attribution_ids": ["agent:model:claude-opus-5"],
            },
        ],
        "attributions": [attributions[key] for key in sorted(attributions)],
        "references": [], "targets": [], "annotations": [], "questions": [], "issues": [],
        "sections": [],
    }
    registry = TargetRegistry()
    seen_anchors = {"reading", "top"}
    seen_block_ids, seen_annotation_ids = set(), set()
    block_synth_state = {"counts": {}, "payloads": {}}
    annotation_synth_state = {"counts": {}, "payloads": {}}
    used_segments, used_reference_ids = set(), set()
    questions_by_id, issues_by_id, question_for_issue = {}, {}, {}

    def identifier(value, where):
        value = text(value, where).lower()
        require(re.fullmatch(r"[a-z][a-z0-9-]*", value), where, "expected a URL-safe ID")
        require(value not in seen_anchors, where, f"duplicate ID: {value}")
        seen_anchors.add(value)
        return value

    def source_status(record, where):
        return statuses(record.get("status", []), where + ".status")

    def run_attribution(record, where):
        run_id = text(record.get("run"), where + ".run")
        require(run_id in runs, where, f"unknown run {run_id}")
        return {"attributed_to": [runs[run_id]]}

    def external_references(source_refs, where):
        reference_ids, issue_ids = [], []
        for reference in items(source_refs, where, nonempty=False):
            reference = text(reference, where)
            if re.fullmatch(r"HD-\d{3}", reference):
                require(reference in decisions, where, f"unresolved House Decision {reference}")
                reference_ids.append(reference)
                used_reference_ids.add(reference)
            elif reference.startswith("issue:"):
                issue_ids.append(reference)
        return reference_ids, issue_ids

    for section_index, source_section in enumerate(section_records):
        source_section = obj(source_section, f"section[{section_index}]")
        source_section_id = text(source_section.get("id"), "section.id")
        section = {
            "id": identifier(source_section_id, "section.id"),
            "title": text(source_section.get("title"), source_section_id + ".title"), "passages": [],
        }
        heading_id = section["id"] + "-title"
        require(heading_id not in seen_anchors, "section.id", "heading ID collision")
        seen_anchors.add(heading_id)
        source_units = sorted(units_by_section.pop(source_section_id, []), key=lambda unit: unit.get("seq", 0))
        require(source_units, source_section_id, "section has no recitation units")
        require([unit.get("seq") for unit in source_units] == list(range(1, len(source_units) + 1)),
                source_section_id, "recitation sequence is not contiguous")
        for unit in source_units:
            unit_id = text(unit.get("id"), "rec_unit.id")
            local_id = text(unit.get("local_id"), unit_id + ".local_id")
            passage_id = identifier(local_id, unit_id + ".local_id")
            unit_status = source_status(unit, passage_id)
            unit_attribution = run_attribution(unit, passage_id)
            tibetan = text(obj(unit.get("source"), passage_id + ".source").get("quote"),
                           passage_id + ".source.quote")
            source_block = {"id": f"block:source:{passage_id}", "kind": "source", "text": tibetan}
            require(source_block["id"] not in seen_block_ids, passage_id, "source block ID collision")
            seen_block_ids.add(source_block["id"])
            recitation_blocks = [
                _block(value, passage_id + ".blocks", f"recitation:{passage_id}",
                       seen_block_ids, block_synth_state)
                for value in items(unit.get("blocks"), passage_id + ".blocks")
            ]
            diplomatic_blocks = []
            passage = {
                "id": passage_id,
                "source": {"id": f"source:{passage_id}", "language": "bo", "blocks": [source_block]},
                "translations": [
                    {"layer_id": RECITATION_LAYER, "edition_ids": [EDITION_ID], "blocks": recitation_blocks,
                     "source_status": unit_status, "attribution": unit_attribution},
                ],
            }
            registry.add(passage_id, "passage")
            registry.block(passage_id, "source", source_block["id"])
            registry.layer(passage_id, RECITATION_LAYER)
            for recitation_block in recitation_blocks:
                registry.block(passage_id, "translation", recitation_block["id"], RECITATION_LAYER)

            if unit.get("sense") is not None:
                sense = obj(unit["sense"], passage_id + ".sense")
                require("offen" not in sense, passage_id + ".sense",
                        "v10 question curation requires sense.offen to be absent")
                passage["meaning"] = {
                    "translation_layer_id": RECITATION_LAYER,
                    "summary": text(sense.get("sinn"), passage_id + ".sense.sinn"),
                    "source_status": unit_status, "attribution": unit_attribution,
                }
                for source_key, target_key in (("vorgang", "practice"), ("begriffe", "concepts")):
                    if sense.get(source_key) is not None:
                        passage["meaning"][target_key] = text(
                            sense[source_key], passage_id + ".sense." + source_key)

            if any(ch in tz.BASE for ch in tibetan):
                passage["pronunciation"] = project_pronunciation(passage_id, source_block)
                passage["transliteration"] = project_transliteration(passage_id, source_block)

            for source_mark in items(unit.get("marks", []), passage_id + ".marks", nonempty=False):
                mark = obj(source_mark, passage_id + ".mark")
                kind = mark.get("kind")
                require(isinstance(kind, str) and kind in MARKS, passage_id, "unknown mark kind")
                mark_id = text(mark.get("id"), passage_id + ".mark.id")
                source_id = unit_id + "#" + mark_id
                annotation_text = text(mark.get("text"), source_id + ".text")
                if mark.get("anchor") is not None:
                    quote = text(mark["anchor"], source_id + ".anchor")
                    target_id = registry.quote_or_layer(
                        passage_id, RECITATION_LAYER, recitation_blocks, quote, source_id)
                else:
                    target_id = registry.layer(passage_id, RECITATION_LAYER)
                alternatives = [text(value, source_id + ".alternatives") for value in
                                items(mark.get("alternatives", []), source_id + ".alternatives", nonempty=False)]
                reference_ids, issue_ids = external_references(mark.get("refs", []), source_id + ".refs")
                if kind == "question":
                    require(source_id not in questions_by_id, source_id, "duplicate Question ID")
                    require(len(issue_ids) <= 1, source_id, "Question relates to more than one Issue")
                    origin_attribution_id = unit_attribution["attributed_to"][0]
                    question_attribution = {
                        "attributed_to": [CURATION_AGENT] if (local_id, mark_id) in curated_question_keys
                        else [origin_attribution_id],
                        "recorded_by": [QUESTION_RECORDER],
                    }
                    if (local_id, mark_id) in curated_question_keys:
                        question_attribution["derived_from_attribution_ids"] = [origin_attribution_id]
                    question = {
                        "id": source_id, "kind": "curated_question", "text": annotation_text,
                        "status": "open", "primary_target_id": target_id,
                        "target_ids": [target_id], "related_issue_ids": issue_ids,
                        "source_id": source_id,
                        "source_status": list(dict.fromkeys(unit_status + ["agent-curated-question"])),
                        "reference_ids": reference_ids,
                        "attribution": question_attribution,
                    }
                    questions_by_id[source_id] = question
                    result["questions"].append(question)
                    if issue_ids:
                        issue_id = issue_ids[0]
                        require(issue_id not in question_for_issue, issue_id,
                                "more than one curated Question points to Issue")
                        question_for_issue[issue_id] = source_id
                else:
                    annotation = {
                        "id": source_id, "family": "recitation", "kind": kind,
                        "text": annotation_text, "alternatives": alternatives,
                        "target_ids": [target_id], "source_id": source_id,
                        "source_status": unit_status, "reference_ids": reference_ids,
                        "attribution": unit_attribution,
                    }
                    require(source_id not in seen_annotation_ids, source_id, "duplicate annotation ID")
                    seen_annotation_ids.add(source_id)
                    result["annotations"].append(annotation)

            for segment_id in items(unit.get("derived_from"), passage_id + ".derived_from"):
                segment_id = text(segment_id, passage_id + ".derived_from")
                require(segment_id in segments, passage_id, f"missing diplomatic segment {segment_id}")
                require(segment_id not in used_segments, passage_id, f"reused diplomatic segment {segment_id}")
                used_segments.add(segment_id)
                segment = segments[segment_id]
                translation = obj(segment.get("translation"), segment_id + ".translation")
                segment_status = source_status(segment, segment_id)
                segment_attribution = run_attribution(segment, segment_id)
                segment_blocks = []
                for part in items(translation.get("parts"), segment_id + ".parts"):
                    part = obj(part, segment_id + ".part")
                    role = part.get("role")
                    require(isinstance(role, str) and role in ROLES, segment_id, "unknown diplomatic role")
                    block_value = {"kind": ROLES[role], "text": text(part.get("text"), segment_id + ".part.text")}
                    block_id = _synthesized_id("block", f"diplomatic:{segment_id}", block_value,
                                               seen_block_ids, block_synth_state, segment_id)
                    segment_blocks.append({"id": block_id, **block_value})
                diplomatic_blocks.extend(segment_blocks)
                segment_target_ids = [registry.block(
                    passage_id, "translation", value["id"], DIPLOMATIC_LAYER
                ) for value in segment_blocks]
                for note in items(segment.get("notes", []), segment_id + ".notes", nonempty=False):
                    note = obj(note, segment_id + ".note")
                    payload = {
                        "category": text(note.get("kind"), segment_id + ".note.kind"),
                        "text": text(note.get("text"), segment_id + ".note.text"),
                    }
                    annotation_id = _synthesized_id(
                        "annotation", f"diplomatic-note:{segment_id}", payload,
                        seen_annotation_ids, annotation_synth_state, segment_id)
                    result["annotations"].append({
                        "id": annotation_id, "family": "diplomatic", "kind": "diplomatic_note",
                        **payload, "alternatives": [], "target_ids": segment_target_ids,
                        "source_id": segment_id, "source_status": segment_status,
                        "reference_ids": [], "attribution": segment_attribution,
                    })
                for alternative in items(segment.get("alternatives", []), segment_id + ".alternatives",
                                         nonempty=False):
                    alternative = obj(alternative, segment_id + ".alternative")
                    payload = {
                        "scope": alternative.get("scope") if isinstance(alternative.get("scope"), str) else None,
                        "text": text(alternative.get("text"), segment_id + ".alternative.text"),
                    }
                    annotation_id = _synthesized_id(
                        "annotation", f"diplomatic-alternative:{segment_id}", payload,
                        seen_annotation_ids, annotation_synth_state, segment_id)
                    annotation = {
                        "id": annotation_id, "family": "diplomatic",
                        "kind": "diplomatic_alternative", "category": "alternative",
                        "text": payload["text"], "alternatives": [], "target_ids": segment_target_ids,
                        "source_id": segment_id, "source_status": segment_status,
                        "reference_ids": [], "attribution": segment_attribution,
                    }
                    result["annotations"].append(annotation)
                for issue in items(segment.get("issues", []), segment_id + ".issues", nonempty=False):
                    issue = obj(issue, segment_id + ".issue")
                    issue_id = text(issue.get("id"), segment_id + ".issue.id")
                    require(issue_id not in issues_by_id, issue_id, "duplicate Issue ID")
                    require(issue.get("type") == "open_question", issue_id, "unsupported issue type")
                    origin_attribution_id = segment_attribution["attributed_to"][0]
                    issue_attribution = {
                        "attributed_to": [CURATION_AGENT] if issue_id in curated_issue_ids
                        else [origin_attribution_id],
                        "recorded_by": [QUESTION_RECORDER],
                    }
                    if issue_id in curated_issue_ids:
                        issue_attribution["derived_from_attribution_ids"] = [origin_attribution_id]
                    projected_issue = {
                        "id": issue_id, "kind": "diplomatic_issue",
                        "text": text(issue.get("text"), issue_id + ".text"),
                        "status": text(issue.get("status"), issue_id + ".status"),
                        "target_ids": segment_target_ids, "related_question_ids": [],
                        "source_id": issue_id,
                        "source_status": list(dict.fromkeys(segment_status + ["agent-curated-issue"])),
                        "attribution": issue_attribution,
                    }
                    issues_by_id[issue_id] = projected_issue
                    result["issues"].append(projected_issue)
            require(diplomatic_blocks, passage_id, "no diplomatic blocks projected")
            registry.layer(passage_id, DIPLOMATIC_LAYER)
            passage["translations"].append({
                "layer_id": DIPLOMATIC_LAYER, "edition_ids": [EDITION_ID], "blocks": diplomatic_blocks,
                "source_status": list(dict.fromkeys(
                    status for segment_id in unit["derived_from"]
                    for status in source_status(segments[segment_id], segment_id)
                )),
                "attribution": {"attributed_to": sorted({
                    runs[text(segments[segment_id].get("run"), segment_id + ".run")]
                    for segment_id in unit["derived_from"]
                })},
            })
            section["passages"].append(passage)
        result["sections"].append(section)

    require(not units_by_section, "bundle.units", f"unknown sections: {sorted(units_by_section)}")
    require(not (set(segments) - used_segments), "bundle.segments",
            f"unprojected segments: {sorted(set(segments) - used_segments)}")
    require(set(question_for_issue) == set(issues_by_id), "Question/Issue relations",
            "every Issue must have exactly one explicit curated Question")
    for issue_id, question_id in question_for_issue.items():
        issue = issues_by_id[issue_id]
        question = questions_by_id[question_id]
        issue["related_question_ids"] = [question_id]
        question["target_ids"] = list(dict.fromkeys(question["target_ids"] + issue["target_ids"]))
    for decision_id in sorted(used_reference_ids):
        decision = decisions[decision_id]
        result["references"].append({
            "id": decision_id, "kind": "house_decision",
            "label": text(decision.get("topic"), decision_id + ".topic"),
            "preview": text(decision.get("decision"), decision_id + ".decision"),
            "status": text(decision.get("status"), decision_id + ".status"),
        })
    result["targets"] = registry.targets
    validate_publication(result)
    return result


def _unique(records, namespace):
    ids = [text(record.get("id"), namespace + ".id") for record in records]
    require(len(ids) == len(set(ids)), namespace, "duplicate ID")
    return set(ids)


def validate_publication(publication):
    """Validate v2 namespace uniqueness, all references and exact selector semantics."""
    publication = obj(publication, "publication")
    require(publication.get("version") == "2.3", "publication.version", "expected 2.3")
    encoded = canonical(publication)
    for legacy in ('"recitation_de"', '"diplomatic_de"', '"sense_open"', '"open_questions"'):
        require(legacy not in encoded, "publication", f"obsolete v1.2 field {legacy} is forbidden")

    variants = items(publication.get("pronunciation_variants"), "pronunciation_variants")
    variant_ids = _unique(variants, "pronunciation_variants")
    require(sum(variant.get("default") is True for variant in variants) == 1, "pronunciation_variants",
            "exactly one default variant")
    for variant in variants:
        text(variant.get("label"), variant["id"] + ".label")
        text(variant.get("description"), variant["id"] + ".description")
    layers = items(publication.get("translation_layers"), "translation_layers")
    layer_ids = _unique(layers, "translation_layers")
    require(not (variant_ids & layer_ids), "pronunciation_variants", "variant ID collides with a layer ID")
    attribution_ids = _unique(items(publication.get("attributions"), "attributions"), "attributions")
    reference_ids = _unique(items(publication.get("references"), "references", nonempty=False), "references")
    targets = items(publication.get("targets"), "targets")
    target_ids = _unique(targets, "targets")
    annotations = items(publication.get("annotations"), "annotations", nonempty=False)
    questions = items(publication.get("questions"), "questions", nonempty=False)
    issues = items(publication.get("issues"), "issues", nonempty=False)
    _unique(annotations, "annotations")
    question_ids = _unique(questions, "questions")
    issue_ids = _unique(issues, "issues")

    def validate_attribution_links(attribution, namespace):
        if attribution is None:
            return
        attribution = obj(attribution, namespace + ".attribution")
        for relation in ("attributed_to", "recorded_by", "derived_from_attribution_ids"):
            relation_ids = items(attribution.get(relation, []), namespace + "." + relation,
                                 nonempty=False)
            require(len(relation_ids) == len(set(relation_ids)), namespace,
                    f"duplicate {relation} attribution")
            for attribution_id in relation_ids:
                require(attribution_id in attribution_ids, namespace,
                        f"dangling attribution {attribution_id}")

    editions = items(publication.get("editions"), "editions")
    edition_ids = _unique(editions, "editions")
    require(publication.get("default_edition_id") in edition_ids, "default_edition_id", "unknown default edition")
    editions_by_layer = {}
    for edition in editions:
        text(edition.get("label"), edition["id"] + ".label")
        for layer_id in items(edition.get("translation_layer_ids"), edition["id"] + ".translation_layer_ids"):
            require(layer_id in layer_ids, edition["id"], f"dangling translation layer {layer_id}")
            editions_by_layer.setdefault(layer_id, set()).add(edition["id"])
    for layer in layers:
        for attribution_id in items(layer.get("attribution_ids", []), "layer.attribution_ids", nonempty=False):
            require(attribution_id in attribution_ids, layer["id"], f"dangling attribution {attribution_id}")
        require(set(layer.get("edition_ids", [])) == editions_by_layer.get(layer["id"], set()), layer["id"],
                "layer/edition relation is not reciprocal")
    for reference in publication["references"]:
        validate_attribution_links(reference.get("attribution"), reference["id"])

    sections = items(publication.get("sections"), "sections")
    _unique(sections, "sections")
    passages = [passage for section in sections for passage in items(section.get("passages"), "passages")]
    passage_ids = _unique(passages, "passages")
    block_context, block_ids, source_ids, pronunciation_ids = {}, set(), set(), set()
    for passage in passages:
        passage_id = passage["id"]
        source = obj(passage.get("source"), passage_id + ".source")
        source_id = text(source.get("id"), passage_id + ".source.id")
        require(source_id not in source_ids, source_id, "duplicate source-content ID")
        source_ids.add(source_id)
        text(source.get("language"), passage_id + ".source.language")
        for block in items(source.get("blocks"), passage_id + ".source.blocks"):
            block_id = text(block.get("id"), passage_id + ".source.block.id")
            require(block_id not in block_ids, block_id, "duplicate block ID")
            block_ids.add(block_id)
            block_context[block_id] = (passage_id, "source", None, text(block.get("text"), block_id))
        seen_passage_layers, covered = set(), {}
        for translation in items(passage.get("translations"), passage_id + ".translations"):
            layer_id = text(translation.get("layer_id"), passage_id + ".translation.layer_id")
            require(layer_id in layer_ids, passage_id, f"dangling translation layer {layer_id}")
            seen_passage_layers.add(layer_id)
            for edition_id in items(translation.get("edition_ids"), passage_id + ".translation.edition_ids"):
                require(edition_id in editions_by_layer.get(layer_id, set()), passage_id,
                        f"translation claims edition {edition_id} that does not show {layer_id}")
                require((layer_id, edition_id) not in covered, passage_id,
                        f"edition {edition_id} has more than one {layer_id} translation")
                covered[(layer_id, edition_id)] = True
            validate_attribution_links(translation.get("attribution"), passage_id + ":" + layer_id)
            for block in items(translation.get("blocks"), passage_id + ".translation.blocks"):
                block_id = text(block.get("id"), passage_id + ".translation.block.id")
                require(block_id not in block_ids, block_id, "duplicate block ID")
                block_ids.add(block_id)
                block_context[block_id] = (passage_id, "translation", layer_id,
                                           text(block.get("text"), block_id))
        for layer_id in seen_passage_layers:
            require(all((layer_id, edition_id) in covered for edition_id in editions_by_layer[layer_id]), passage_id,
                    f"not every edition selects a {layer_id} translation")
        if passage.get("pronunciation") is not None:
            pronunciation = obj(passage["pronunciation"], passage_id + ".pronunciation")
            pronunciation_id = text(pronunciation.get("id"), passage_id + ".pronunciation.id")
            require(pronunciation_id not in pronunciation_ids, pronunciation_id,
                    "duplicate pronunciation ID")
            pronunciation_ids.add(pronunciation_id)
            source_block_id = pronunciation.get("source_block_id")
            require(source_block_id in block_context, passage_id, "pronunciation has a dangling source block")
            require(block_context[source_block_id][:3] == (passage_id, "source", None), passage_id,
                    "pronunciation points outside its passage source")
            require(pronunciation.get("status") == "generated", passage_id, "pronunciation must be generated")
            require(pronunciation.get("language") == "de", passage_id, "pronunciation language must be de")
            generator = obj(pronunciation.get("generator"), passage_id + ".pronunciation.generator")
            text(generator.get("name"), passage_id + ".pronunciation.generator.name")
            text(generator.get("version"), passage_id + ".pronunciation.generator.version")
            source_text = block_context[source_block_id][3]
            seen_variants = []
            for variant in items(pronunciation.get("variants"), passage_id + ".pronunciation.variants"):
                variant = obj(variant, passage_id + ".pronunciation.variant")
                seen_variants.append(variant.get("variant_id"))
                lines = [obj(line, passage_id + ".pronunciation.line")
                         for line in items(variant.get("lines"), passage_id + ".pronunciation.lines")]
                require("".join(text(line.get("tibetan"), passage_id + ".pronunciation.tibetan")
                                for line in lines) == source_text, passage_id,
                        "pronunciation lines must concatenate to the exact Tibetan source text")
                for line in lines:
                    require(isinstance(line.get("pronunciation"), str), passage_id,
                            "pronunciation line text must be a string")
            require(sorted(seen_variants) == sorted(variant_ids) and len(seen_variants) == len(variant_ids),
                    passage_id, "pronunciation needs exactly one entry per declared variant")
            slices = [[line.get("tibetan") for line in variant["lines"]] for variant in pronunciation["variants"]]
            require(all(value == slices[0] for value in slices), passage_id,
                    "pronunciation variants must share one line segmentation")
            transliteration = obj(passage.get("transliteration"), passage_id + ".transliteration")
            require((transliteration.get("id"), transliteration.get("scheme"), transliteration.get("status"),
                     transliteration.get("source_block_id")) ==
                    (f"transliteration:ewts:{passage_id}", "ewts", "generated", source_block_id), passage_id,
                    "transliteration must be generated EWTS for the passage source")
            lines = [obj(line, passage_id + ".transliteration.line")
                     for line in items(transliteration.get("lines"), passage_id + ".transliteration.lines")]
            require([line.get("tibetan") for line in lines] == slices[0], passage_id,
                    "transliteration lines must use the pronunciation line slices")
            for line in lines:
                require(isinstance(line.get("text"), str), passage_id, "transliteration text must be a string")
        elif any(ch in tz.BASE for ch in block_context.get(f"block:source:{passage_id}", ("", "", "", ""))[3]):
            require(False, passage_id, "passage with Tibetan source lacks a pronunciation")
        if passage.get("meaning") is not None:
            meaning = obj(passage["meaning"], passage_id + ".meaning")
            require(meaning.get("translation_layer_id") in seen_passage_layers, passage_id,
                    "meaning has a dangling translation layer")
            validate_attribution_links(meaning.get("attribution"), passage_id + ".meaning")

    for target in targets:
        target_id = target["id"]
        passage_id = target.get("passage_id")
        require(passage_id in passage_ids, target_id, f"dangling passage {passage_id}")
        scope = target.get("scope")
        require(scope in {"passage", "source", "translation"}, target_id, "invalid target scope")
        layer_id = target.get("translation_layer_id")
        if scope == "translation":
            require(layer_id in layer_ids, target_id, f"dangling translation layer {layer_id}")
        else:
            require(layer_id is None, target_id, "non-translation target has a translation layer")
        block_id = target.get("block_id")
        if block_id is not None:
            require(block_id in block_context, target_id, f"dangling block {block_id}")
            actual_passage, actual_scope, actual_layer, block_text = block_context[block_id]
            require((actual_passage, actual_scope, actual_layer) == (passage_id, scope, layer_id),
                    target_id, "block does not belong to the declared target context")
        if target.get("selector") is not None:
            require(block_id is not None, target_id, "selector requires a block")
            selector = obj(target["selector"], target_id + ".selector")
            require(selector.get("type") == "text_position" and
                    selector.get("coordinate_system") == "unicode_code_points",
                    target_id, "unsupported selector semantics")
            start, end = selector.get("start"), selector.get("end")
            require(isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(block_text),
                    target_id, "selector bounds are invalid")
            require(block_text[start:end] == selector.get("quote"), target_id,
                    "selector quote does not match exact block code-point offsets")

    def validate_links(record, namespace):
        record_target_ids = items(record.get("target_ids"), namespace + ".target_ids")
        require(len(record_target_ids) == len(set(record_target_ids)), namespace, "duplicate target reference")
        for target_id in record_target_ids:
            require(target_id in target_ids, namespace, f"dangling target {target_id}")
        record_reference_ids = items(record.get("reference_ids", []), namespace + ".reference_ids",
                                     nonempty=False)
        require(len(record_reference_ids) == len(set(record_reference_ids)), namespace,
                "duplicate reference target")
        for reference_id in record_reference_ids:
            require(reference_id in reference_ids, namespace, f"dangling reference {reference_id}")
        validate_attribution_links(record.get("attribution"), namespace)

    for annotation in annotations:
        validate_links(annotation, annotation["id"])
    for question in questions:
        validate_links(question, question["id"])
        require(question.get("kind") in {"curated_question", "reviewer_request"}, question["id"], "unknown Question kind")
        for edition_id in items(question.get("edition_ids", list(edition_ids)), question["id"] + ".edition_ids"):
            require(edition_id in edition_ids, question["id"], f"dangling edition {edition_id}")
        require(question.get("primary_target_id") in question["target_ids"], question["id"],
                "primary Question target must be one of its target references")
        for issue_id in items(question.get("related_issue_ids", []), question["id"] + ".issues", nonempty=False):
            require(issue_id in issue_ids, question["id"], f"dangling Issue {issue_id}")
    for issue in issues:
        validate_links(issue, issue["id"])
        for question_id in items(issue.get("related_question_ids", []), issue["id"] + ".questions",
                                 nonempty=False):
            require(question_id in question_ids, issue["id"], f"dangling Question {question_id}")
    for question in questions:
        for issue_id in question["related_issue_ids"]:
            issue = next(value for value in issues if value["id"] == issue_id)
            require(question["id"] in issue["related_question_ids"], question["id"],
                    "Question/Issue relationship is not reciprocal")
    for issue in issues:
        for question_id in issue["related_question_ids"]:
            question = next(value for value in questions if value["id"] == question_id)
            require(issue["id"] in question["related_issue_ids"], issue["id"],
                    "Issue/Question relationship is not reciprocal")
    return publication


def convert(bundle_path=DEFAULT_BUNDLE):
    return project(load_bundle(bundle_path))


def serialize(publication):
    return json.dumps(publication, ensure_ascii=False, indent=2) + "\n"


def _authoring_body(blocks):
    return {"blocks": [
        {key: value for key, value in {
            "slot_key": block["id"], "kind": block["kind"], "text": block["text"],
            "repeat": block.get("repeat"), "iast": block.get("iast"), "note": block.get("note"),
        }.items() if value is not None}
        for block in blocks
    ]}


LEVEL_LABELS = {"language:de": "Deutsch allgemein", "house:tz": "Stil des Tibetischen Zentrums"}
ROLE_LABELS = {"writes": "geschrieben", "drafts": "entworfen", "confirms": "geprüft und bestätigt",
               "decides": "entschieden", "executes": "ausgeführt"}


def load_registries(rules_path=DEFAULT_RULES, evidence_path=DEFAULT_EVIDENCE):
    registries = empty_registries()
    if Path(rules_path).exists():
        registries["rules"] = json.loads(Path(rules_path).read_text(encoding="utf-8"))
    if Path(evidence_path).exists():
        registries["evidence"] = json.loads(Path(evidence_path).read_text(encoding="utf-8"))
    return validate_registries(registries)


def _trusted_context(bundle, publication):
    """Exact editable v10 bases, bound to the displayed recitation blocks."""
    passages = {passage["id"]: passage for section in publication["sections"] for passage in section["passages"]}
    baselines = []
    for unit in bundle["units"]:
        passage_id = text(unit.get("local_id"), "rec_unit.local_id").lower()
        passage = passages[passage_id]
        translation = next(value for value in passage["translations"]
                           if value["layer_id"] == RECITATION_LAYER and EDITION_ID in value["edition_ids"])
        body = _authoring_body(translation["blocks"])
        source_text = "".join(block["text"] for block in passage["source"]["blocks"])
        legacy_id = text(unit.get("id"), passage_id + ".id")
        baselines.append({
            "id": f"baseline:{bundle['bundle_sha256']}:{legacy_id}",
            "legacy_source_id": legacy_id, "project_id": "hayagriva",
            "release_id": "hayagriva-v10-question-curated", "passage_id": passage_id,
            "language": "de", "mode": "recitation",
            "source_binding": {
                "release_id": "hayagriva-v10-question-curated", "passage_id": passage_id,
                "source_id": passage["source"]["id"],
                "source_sha256": "sha256:" + hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            },
            "body": body, "body_sha256": body_hash(body),
            "attribution": {"run_id": unit.get("run"), "date": next(
                (record.get("date") for record in bundle["runs"] if record.get("id") == unit.get("run")), None)},
        })
    baselines.sort(key=lambda value: value["passage_id"])
    return {"schema_version": "atp-authoring-context-v3", "project_id": "hayagriva",
            "release": publication["release"], "baselines": baselines}


def apply_editions(bundle, publication, store, registries):
    """Add the store's explicit editions and public post-v10 Questions to a v10-only publication.

    Every edition pins every passage; the recitation entry of a passage lists exactly the editions that
    select it. Nothing is inferred from recency: the default is the store's explicit current edition.
    """
    publication = deepcopy(publication)
    context = _trusted_context(bundle, publication)
    store = validate_store(deepcopy(store), registries, context)
    if not store["editions"]:
        return publication
    baselines = {item["id"]: item for item in context["baselines"]}
    candidates = {item["id"]: item for item in store["candidates"]}
    activities = {item["id"]: item for item in store["activities"]}
    agents = {item["id"]: item for item in store["agents"]}
    decisions = {item["id"]: item for item in store["decisions"]}
    rules = {item["id"]: item for item in registries["rules"]["rules"]}
    exposed = set(store["public_candidate_ids"])
    for agent in store["agents"]:
        publication["attributions"].append({
            "id": agent["id"], "kind": "human" if agent["kind"] == "human" else "agent_workflow", "label": agent["label"],
            "detail": "Selbst deklarierte Identität im Authoring-Store (nicht authentifiziert)." if agent["kind"] == "human"
            else "Software-Agent im Authoring-Store."})
    publication["attributions"].sort(key=lambda value: value["id"])
    selection = {}
    for edition in store["editions"]:
        changed = []
        for entry in edition["entries"]:
            if entry["candidate_id"] not in baselines:
                if entry["candidate_id"] not in exposed:
                    raise ValueError(f"{edition['id']}: selected candidate {entry['candidate_id']} is not public")
                changed.append(entry["passage_id"])
            selection.setdefault(entry["passage_id"], {})[edition["id"]] = entry["candidate_id"]
        question_ids = sorted(question["id"] for question in store["questions"]
                              if question["id"] in store["public_question_ids"]
                              and question["origin"]["activity_id"] in edition["based_on"]["activity_ids"])
        publication["editions"].append({
            "id": edition["id"], "label": edition["label"], "language": "de", "status": "working-edition",
            "translation_layer_ids": [RECITATION_LAYER, DIPLOMATIC_LAYER],
            "note": edition["selection_rule"], "recorded_at": edition["recorded_at"],
            "history": {
                "based_on_edition_id": EDITION_ID, "changed_passage_ids": changed, "question_ids": question_ids,
                "applications": [activities[value]["label"] for value in edition["based_on"]["activity_ids"]],
                "decisions": [{
                    "id": decision_id, "label": decisions[decision_id]["label"],
                    "statements": [rules[rule_id]["statement"] for rule_id in decisions[decision_id]["adopts"]],
                    "exceptions": [value for rule_id in decisions[decision_id]["adopts"] for value in rules[rule_id].get("exceptions", [])],
                    "levels": [LEVEL_LABELS.get(rules[rule_id]["level"], "nur dieses Projekt") for rule_id in decisions[decision_id]["adopts"]],
                    "scope_note": decisions[decision_id]["scope"].get("note"),
                } for decision_id in edition["based_on"]["decision_ids"]],
            },
        })
    edition_ids = [value["id"] for value in publication["editions"]]
    for layer in publication["translation_layers"]:
        layer["edition_ids"] = edition_ids
    if store["current_edition_id"]:
        publication["default_edition_id"] = store["current_edition_id"]
    block_ids = {}
    for section in publication["sections"]:
        for passage in section["passages"]:
            chosen = selection[passage["id"]]
            translations = []
            for translation in passage["translations"]:
                if translation["layer_id"] != RECITATION_LAYER:
                    translation["edition_ids"] = edition_ids
                    translations.append(translation)
                    continue
                baseline_id = next(value["id"] for value in baselines.values() if value["passage_id"] == passage["id"])
                translation["edition_ids"] = [EDITION_ID] + [key for key, value in chosen.items() if value == baseline_id]
                translations.append(translation)
                for candidate_id in sorted({value for value in chosen.values() if value != baseline_id}):
                    candidate = candidates[candidate_id]
                    suffix = candidate_id.removeprefix("candidate:")[:8]
                    blocks = []
                    for block in candidate["body"]["blocks"]:
                        block_id = f"{block['slot_key']}:rev-{suffix}"
                        block_ids[(candidate_id, block["slot_key"])] = block_id
                        blocks.append({"id": block_id, **{key: value for key, value in block.items() if key != "slot_key"}})
                    activity = activities[candidate["activity_id"]]
                    agents_involved = ([activity["associated_agent_id"]] if activity["kind"] == "human_translation_revision"
                                       else list(dict.fromkeys(item["agent_id"] for item in activity["associations"])))
                    translations.append({
                        "layer_id": RECITATION_LAYER, "edition_ids": sorted(key for key, value in chosen.items() if value == candidate_id),
                        "candidate_id": candidate_id, "blocks": blocks,
                        "source_status": ["post-v10", activity["kind"].replace("_", "-")],
                        "attribution": {"attributed_to": agents_involved,
                                        "derived_from_attribution_ids": translation["attribution"]["attributed_to"]},
                    })
            passage["translations"] = translations
    targets = {value["id"] for value in publication["targets"]}
    for question in store["questions"]:
        if question["id"] not in store["public_question_ids"]:
            continue
        target_ids = []
        for target in question["targets"]:
            block_id = block_ids[(target["candidate_id"], target["slot_key"])]
            body_text = next(block["text"] for block in candidates[target["candidate_id"]]["body"]["blocks"]
                             if block["slot_key"] == target["slot_key"])
            start = body_text.index(target["quote"])
            value = {"passage_id": target["passage_id"], "scope": "translation", "translation_layer_id": RECITATION_LAYER,
                     "block_id": block_id, "selector": {"type": "text_position", "coordinate_system": "unicode_code_points",
                                                        "start": start, "end": start + len(target["quote"]), "quote": target["quote"]}}
            target_id = f"target:{target['passage_id']}:{digest(value)}"
            if target_id not in targets:
                targets.add(target_id)
                publication["targets"].append({"id": target_id, **value})
            target_ids.append(target_id)
        passage_id = question["targets"][0]["passage_id"]
        shown_in = sorted(key for key, value in selection[passage_id].items()
                          if value == question["targets"][0]["candidate_id"])
        drafted = [item["agent_id"] for item in question["associations"] if item["role"] == "drafts"]
        prompted = [item["agent_id"] for item in question["associations"] if item["role"] == "decides"]
        publication["questions"].append({
            "id": question["id"], "kind": "reviewer_request", "label": question["label"], "request": question["request"],
            "addressed_to": [value["label"] for value in question["addressed_to"]], "text": question["text"],
            "options": [{"label": value["label"], "text": value["text"]} for value in question["options"]],
            "status": question["status"], "primary_target_id": target_ids[0], "target_ids": target_ids,
            "related_issue_ids": [], "source_id": question["id"], "source_status": ["post-v10", "open-request"],
            "reference_ids": [], "edition_ids": shown_in,
            "attribution": {"attributed_to": drafted, "recorded_by": prompted},
        })
    validate_publication(publication)
    return publication


def project_authoring_context(bundle, publication, store, registries=None):
    """Project exact editable bases and explicitly public post-v10 records (contract v3)."""
    registries = registries if registries is not None else empty_registries()
    trusted_context = _trusted_context(bundle, publication)
    store = validate_store(deepcopy(store), registries, trusted_context)
    empty_store = validate_store({
        "schema_version": "atp-authoring-store-v3", "project_id": "hayagriva", "release": store["release"],
        "current_edition_id": None, "public_candidate_ids": [], "public_review_note_ids": [], "public_question_ids": [],
        "agents": [], "candidates": [], "activities": [], "review_notes": [], "withdrawals": [], "decisions": [],
        "questions": [], "editions": [], "receipts": []})
    validate_package({
        "schema_version": "atp-authoring-package-v3", "project_id": "hayagriva",
        "release": publication["release"], "exported_at": "2000-01-01T00:00:00+00:00",
        **{key: store[key] for key in ("agents", "candidates", "activities", "review_notes", "withdrawals", "decisions", "questions")},
    }, trusted_context, empty_store, registries)
    baselines = trusted_context["baselines"]
    base_ids = {value["id"] for value in baselines}
    candidates = {value["id"]: value for value in store["candidates"]}
    activities = {value["id"]: value for value in store["activities"]}
    withdrawals = {value["candidate_id"]: value for value in store["withdrawals"]}
    active_roots = [value for value in store["public_candidate_ids"] if value not in withdrawals]
    exposed, pending = set(active_roots), list(active_roots)
    while pending:
        current = candidates[pending.pop()]
        parent_id = current["parent_candidate_id"]
        if parent_id not in base_ids and parent_id not in candidates:
            raise ValueError(f"authoring store: public candidate {current['id']} has unknown parent {parent_id}")
        if parent_id in candidates and parent_id not in exposed:
            exposed.add(parent_id); pending.append(parent_id)
    public_candidates = sorted((candidates[value] for value in exposed), key=lambda value: value["id"])
    public_withdrawals = sorted((withdrawals[value] for value in exposed if value in withdrawals), key=lambda value: value["id"])
    public_activities = sorted((activities[value] for value in {item["activity_id"] for item in public_candidates}),
                               key=lambda value: value["id"])
    public_notes = [value for value in store["review_notes"] if value["id"] in store["public_review_note_ids"]]
    public_questions = [value for value in store["questions"] if value["id"] in store["public_question_ids"]]
    decision_ids = {decision_id for activity in public_activities if activity["kind"] == "rule_application"
                    for decision_id in activity["plan"]["decision_ids"]}
    public_decisions = []
    for decision in store["decisions"]:
        if decision["id"] in decision_ids:
            decision = deepcopy(decision)  # private transcript references never leave the repository store
            decision["capture"] = {key: value for key, value in decision["capture"].items() if key != "private_references"}
            public_decisions.append(decision)
    rule_ids = {rule_id for decision in public_decisions for rule_id in decision["adopts"]}
    public_rules = [value for value in registries["rules"]["rules"] if value["id"] in rule_ids]
    citation_ids = {link["citation_id"] for rule in public_rules for link in rule["evidence"]}
    public_citations = [value for value in registries["evidence"]["citations"] if value["id"] in citation_ids]
    resource_ids = {value["resource_id"] for value in public_citations}
    agent_ids = set()
    for activity in public_activities:
        if activity["kind"] == "human_translation_revision":
            agent_ids.add(activity["associated_agent_id"])
        else:
            agent_ids |= {item["agent_id"] for item in activity["associations"]} | {hit["drafted_by"] for hit in activity["hits"]}
    for record in [*public_decisions, *public_questions, *store["editions"]]:
        agent_ids |= {item["agent_id"] for item in record["associations"]}
    agent_ids |= {value["author_agent_id"] for value in [*public_notes, *public_withdrawals]}
    return {
        "schema_version": "atp-authoring-context-v3", "contract_version": "3.0",
        "project_id": "hayagriva", "projection_version": "3.0", "publication_id": publication["id"],
        "release": publication["release"], "editable_layer_id": RECITATION_LAYER,
        "v10_edition_id": V10_EDITION_ID, "current_edition_id": store["current_edition_id"] or V10_EDITION_ID,
        "baselines": baselines,
        "repository": {
            "agents": sorted((value for value in store["agents"] if value["id"] in agent_ids), key=lambda value: value["id"]),
            "candidates": public_candidates, "activities": public_activities,
            "review_notes": sorted(public_notes, key=lambda value: value["id"]),
            "withdrawals": public_withdrawals, "decisions": public_decisions, "questions": public_questions,
            "editions": [{key: value[key] for key in ("id", "label", "entries", "recorded_at")} for value in store["editions"]],
            "rules": public_rules, "citations": public_citations,
            "resources": [value for value in registries["evidence"]["resources"] if value["id"] in resource_ids],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=ROOT / "src/generated/publication.json")
    parser.add_argument("--authoring-store", type=Path, default=DEFAULT_AUTHORING_STORE)
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--authoring-output", type=Path, default=DEFAULT_AUTHORING_OUTPUT)
    args = parser.parse_args()
    try:
        bundle = load_bundle(args.bundle)
        base = project(bundle)
        store = json.loads(args.authoring_store.read_text(encoding="utf-8"))
        registries = load_registries(args.rules, args.evidence)
        publication = apply_editions(bundle, base, store, registries)
        context = project_authoring_context(bundle, base, store, registries)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialize(publication), encoding="utf-8")
        args.authoring_output.parent.mkdir(parents=True, exist_ok=True)
        args.authoring_output.write_text(serialize(context), encoding="utf-8")
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Hayagriva projection failed: {exc}\n")
    print(f"Publication written: {args.output}")
    print(f"Authoring context written: {args.authoring_output}")


if __name__ == "__main__":
    main()
