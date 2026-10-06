"""Audio manifest helpers (stdlib only): import own recordings, apply review results.

    # own recordings: files named by item id (l-ka.m4a, v-ki.wav, ...) in any ffmpeg-readable format
    uv run python tools/audio/curate.py import ~/aufnahmen [--dialect "Zentraltibetisch (Lhasa)"]

    # review results copied from the app (#/audio-review → "Status kopieren"), one "item status" per line
    uv run python tools/audio/curate.py status review.txt

Import trims silence, normalises loudness, encodes mp3 into web/public/audio/ and marks the clip
`source = "manual"`, `status = "approved"`. Run `uv run learn-tibetan build-content` afterwards.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "content/audio.toml"
PUBLIC = ROOT / "web/public"
HEADER = """# Audio-Manifest. Ein Eintrag pro Clip; der Content-Build hängt ihn an das Item.
# file: Pfad relativ zu web/public/ · source: "mms-tts-bod@<rev>" (KI-Kandidat) oder "manual"
# status: "candidate" | "approved" | "rejected". Quiz und Referenz nutzen nur "approved".
# Pflege: tools/audio/curate.py (Import eigener Aufnahmen, Prüfergebnisse) · Prüfansicht: #/audio-review
"""
FIELDS = ("item", "file", "source", "dialect", "status", "note")


def load() -> dict[str, dict]:
    return {c["item"]: c for c in tomllib.loads(MANIFEST.read_text(encoding="utf-8")).get("clips", [])}


def save(clips: dict[str, dict]) -> None:
    curriculum = json.loads((ROOT / "web/src/content/curriculum.json").read_text(encoding="utf-8"))
    order = {it["id"]: it["order"] for it in curriculum["items"]}
    entries = []
    for c in sorted(clips.values(), key=lambda c: order.get(c["item"], 1e9)):
        entries.append("\n".join(["[[clips]]"] + [f"{k} = {json.dumps(c[k], ensure_ascii=False)}" for k in FIELDS if k in c]))
    MANIFEST.write_text(HEADER + "\n" + "\n\n".join(entries) + "\n", encoding="utf-8")


def import_dir(src: Path, dialect: str) -> None:
    clips = load()
    (PUBLIC / "audio").mkdir(parents=True, exist_ok=True)
    for f in sorted(p for p in src.iterdir() if p.is_file()):
        item, rel = f.stem, f"audio/{f.stem}.mp3"
        # trim leading/trailing silence, EBU R128 loudness, mono 48 kbit/s mp3
        filt = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
                "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,loudnorm=I=-18")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-af", filt, "-ac", "1", "-ar", "44100",
                        "-codec:a", "libmp3lame", "-b:a", "48k", str(PUBLIC / rel)], check=True)
        clips[item] = {"item": item, "file": rel, "source": "manual", "dialect": dialect, "status": "approved",
                       "note": f"Import {f.name}"}
        print(f"imported {item}")
    save(clips)


def apply_status(review: Path) -> None:
    clips = load()
    for line in review.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0] in clips and parts[1] in {"candidate", "approved", "rejected"}:
            clips[parts[0]]["status"] = parts[1]
    save(clips)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    imp = sub.add_parser("import")
    imp.add_argument("dir", type=Path)
    imp.add_argument("--dialect", default="Zentraltibetisch (Lhasa)")
    st = sub.add_parser("status")
    st.add_argument("file", type=Path)
    args = ap.parse_args()
    import_dir(args.dir, args.dialect) if args.cmd == "import" else apply_status(args.file)


if __name__ == "__main__":
    main()
