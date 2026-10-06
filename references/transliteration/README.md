# Transliteration reference material (index)

Unpacked from `umschrift-generator-transfer-2026-10-06-mit-quelltexten.zip` (kept here, gitignored)
and re-sorted for this repo. The original package description is `README_UMSCHRIFT.md` (unchanged).

| What | Where now | Committed? |
|---|---|---|
| Production engine `tz.py`, `wylie.py` | `src/learn_tibetan/phonetics/` (import path adapted only) | yes |
| Unit tests + Gebetsbuch held-out fixture | `tests/phonetics/` | yes |
| Function/trust doc, research notes | `docs/` | yes |
| Exploratory predecessor scripts | `research/` | yes |
| Audit/gap outputs, OCR page texts (was `evidence_outputs/`) | `evidence/` | yes |
| Reader integration example (not standalone) | `integration_example/` | yes |
| Historical design prompt | `design/` | yes |
| Origin project metadata | `project_metadata/` | yes |
| TZ mapping CSV + provenance | `reference_phonetics/` | yes |
| TZ mapping JSON (623 KB, same data as CSV), corpus XLSX | `reference_phonetics/` | **no** (gitignored) |
| DILA Mahāvyutpatti index (7 MB, used by one Wylie test, skipped if absent) | `data/reference_resources/index/` | **no** |
| TZ PDF scans (47 MB, internal primary evidence) | `primary_sources/tz_scans/` | **no** |
| Original zip (47 MB) | `./*.zip` | **no** |

Dropped: `src/atp/__init__.py` (origin-project package stub).

Rights: origin project is declared *Proprietary*; TZ scans released by the owner for internal use
in this project only; DILA redistribution not assessed. Do not publish this folder or the engine
as a third-party package. To restore ignored files on a fresh clone, unzip the original package
and copy the folders listed above.
