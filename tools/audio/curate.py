"""Audio manifest helpers (stdlib only): import own recordings, apply review results.

    # own recordings: files named by item id (l-ka.m4a, v-ki.wav, ...) in any ffmpeg-readable format
    uv run python tools/audio/curate.py import ~/aufnahmen [--dialect "Zentraltibetisch (Lhasa)"]

    # one recording with several syllables separated by pauses (e.g. a whole alphabet row)
    uv run python tools/audio/curate.py split Ka.m4a l-ka l-kha l-ga l-nga
    uv run python tools/audio/curate.py split GaJaDaBa-B.m4a l-ga l-ja l-da l-ba --variant B

    # review results copied from the app (#/audio-review → "Status kopieren"), one "item status" per line
    uv run python tools/audio/curate.py status review.txt

Split finds the syllables by short-time energy, drops extra blips (clicks, breath: the quietest
segments) and exports each syllable with a little padding, short fades and peak normalisation.
Import trims silence, normalises loudness, encodes mp3 into web/public/audio/ and marks the clip
`source = "manual"`, `status = "approved"`. Run `uv run learn-tibetan build-content` afterwards.
"""

from __future__ import annotations

import argparse
import array
import json
import math
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
FIELDS = ("item", "variant", "file", "source", "dialect", "status", "note")


def key(c: dict) -> str:
    """Manifest key: item id, plus the pronunciation variant for ག ཇ ད བ clips (D-019)."""
    return f"{c['item']}#{c['variant']}" if c.get("variant") else c["item"]


def load() -> dict[str, dict]:
    return {key(c): c for c in tomllib.loads(MANIFEST.read_text(encoding="utf-8")).get("clips", [])}


def save(clips: dict[str, dict]) -> None:
    curriculum = json.loads((ROOT / "web/src/content/curriculum.json").read_text(encoding="utf-8"))
    order = {it["id"]: it["order"] for it in curriculum["items"]}
    entries = []
    for c in sorted(clips.values(), key=lambda c: (order.get(c["item"], 1e9), c.get("variant", ""))):
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


def _pcm(f: Path, sr: int) -> array.array:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return array.array("h", raw)


def find_segments(f: Path, win: float = 0.02, rel_db: float = -30, min_gap: float = 0.18,
                  min_len: float = 0.12) -> list[tuple[float, float, float]]:
    """Voiced regions as (start, end, loudness dB): frames within rel_db of the loud end of the file."""
    sr = 16000
    x = _pcm(f, sr)
    n = int(win * sr)
    env = [10 * math.log10(sum(v * v for v in x[i:i + n]) / n + 1e-9) for i in range(0, len(x) - n, n)]
    th = sorted(env)[int(len(env) * 0.95)] + rel_db
    segs, start, end, gap = [], None, 0, 0
    for i, e in enumerate(env + [-999.0] * int(min_gap / win + 1)):
        if e > th:
            start, end, gap = (i if start is None else start), i, 0
        elif start is not None:
            gap += 1
            if gap * win >= min_gap:
                if (end + 1 - start) * win >= min_len:
                    segs.append((start * win, (end + 1) * win, max(env[start:end + 1])))
                start = None
    return segs


def split(src: Path, items: list[str], dialect: str, variant: str | None = None) -> None:
    segs = find_segments(src)
    if len(segs) < len(items):
        raise SystemExit(f"{src.name}: only {len(segs)} syllables found for {len(items)} items")
    keep = sorted(sorted(segs, key=lambda s: -s[2])[:len(items)])  # drop the quietest extras, keep order
    dropped = [s for s in segs if s not in keep]
    clips = load()
    (PUBLIC / "audio").mkdir(parents=True, exist_ok=True)
    for item, (a, b, loud) in zip(items, keep):
        a, b = max(0.0, a - 0.08), b + 0.12
        rel = f"audio/{item}{'-' + variant if variant else ''}.mp3"
        filt = f"afade=t=in:d=0.01,afade=t=out:st={b - a - 0.04:.3f}:d=0.04,dynaudnorm=p=0.89:m=10"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(src),
                        "-af", filt, "-ac", "1", "-ar", "44100", "-codec:a", "libmp3lame", "-b:a", "64k",
                        str(PUBLIC / rel)], check=True)
        clip = {"item": item, "file": rel, "source": "manual", "dialect": dialect, "status": "approved",
                "note": f"{src.name} {a:.2f}-{b:.2f} s"}
        if variant:
            clip["variant"] = variant
        clips[key(clip)] = clip
        print(f"{item:8} {a:5.2f}-{b:5.2f}s  {loud:5.1f} dB")
    for a, b, loud in dropped:
        print(f"  dropped {a:5.2f}-{b:5.2f}s  {loud:5.1f} dB")
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
    sp = sub.add_parser("split")
    sp.add_argument("file", type=Path)
    sp.add_argument("items", nargs="+")
    sp.add_argument("--dialect", default="Zentraltibetisch (Lhasa)")
    sp.add_argument("--variant", choices=["A", "B"], help="ག ཇ ད བ: A = wie ཁ ཆ ཐ ཕ mit tiefem Ton, B = weich g dsch d b")
    st = sub.add_parser("status")
    st.add_argument("file", type=Path)
    args = ap.parse_args()
    if args.cmd == "import":
        import_dir(args.dir, args.dialect)
    elif args.cmd == "split":
        split(args.file, args.items, args.dialect, args.variant)
    else:
        apply_status(args.file)


if __name__ == "__main__":
    main()
