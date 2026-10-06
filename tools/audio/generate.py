"""Generate candidate audio clips with Meta MMS-TTS (Central Tibetan, `facebook/mms-tts-bod`).

Spike result 2026-10-06 (docs/decisions.md D-013): isolated letters come out as 0.08-0.35 s blips;
the tsheg is the tokenizer's pad token, so syllable boundaries are lost. Kept as a candidate source only.

Dev-only (uv sync --group audio). Clips are CANDIDATES: listen in the app's audio review screen,
then set `status` in content/audio.toml. Approved, rejected or manual clips are never overwritten
unless --force. Model license: CC-BY-NC-4.0 (fine for this private prototype, not for publishing).

    uv run --group audio python tools/audio/generate.py [--items l-ka v-ki ...] [--seed 0] [--force]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, VitsModel

from curate import PUBLIC, load, save  # same directory

ROOT = Path(__file__).resolve().parents[2]
MODEL, REVISION = "facebook/mms-tts-bod", "e5767a90abf2293827ca6f467a9b964c0dc35fc5"
CANDIDATES = ROOT / "tools/audio/candidates"
DIALECT = "Zentraltibetisch (MMS bod; Varietät nicht verifiziert)"


def default_items(curriculum: dict) -> list[dict]:
    """All letters plus the vowel forms on ཀ (lessons a1-a3)."""
    return [it for it in curriculum["items"] if it["kind"] == "letter" or it["baseId"] == "l-ka"]


def trim(wav: np.ndarray, sr: int) -> np.ndarray:
    level = np.abs(wav)
    idx = np.where(level > 0.02 * level.max())[0]
    pad = int(0.06 * sr)
    out = wav[max(0, idx[0] - pad): idx[-1] + pad] if len(idx) else wav
    return 0.89 * out / max(1e-9, np.abs(out).max())  # peak ~ -1 dBFS


def write_wav(path: Path, wav: np.ndarray, sr: int) -> None:
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((wav * 32767).astype("<i2").tobytes())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", nargs="*")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    curriculum = json.loads((ROOT / "web/src/content/curriculum.json").read_text(encoding="utf-8"))
    items = default_items(curriculum)
    if args.items:
        items = [it for it in curriculum["items"] if it["id"] in args.items]
    clips = load()

    tok = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    model = VitsModel.from_pretrained(MODEL, revision=REVISION).eval()
    sr = model.config.sampling_rate
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "audio").mkdir(parents=True, exist_ok=True)

    for it in items:
        old = clips.get(it["id"])
        if old and old.get("status") != "candidate" and not args.force:
            print(f"skip {it['id']} ({old.get('status')}, {old.get('source')})")
            continue
        text = it["tibetan"] + "་"  # tsheg closes the syllable like in running text
        torch.manual_seed(args.seed)
        with torch.no_grad():
            wav = model(**tok(text, return_tensors="pt")).waveform[0].numpy()
        wav = trim(wav, sr)
        wav_path = CANDIDATES / f"{it['id']}.wav"
        write_wav(wav_path, wav, sr)
        rel = f"audio/{it['id']}.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path), "-codec:a", "libmp3lame",
                        "-b:a", "48k", str(PUBLIC / rel)], check=True)
        clips[it["id"]] = {"item": it["id"], "file": rel, "source": f"mms-tts-bod@{REVISION[:7]}",
                           "dialect": DIALECT, "status": "candidate",
                           "note": f"Eingabe {text} · seed {args.seed} · {len(wav) / sr:.2f} s"}
        print(f"{it['id']:8} {it['tibetan']}  {len(wav) / sr:.2f}s")

    save(clips)

if __name__ == "__main__":
    main()
