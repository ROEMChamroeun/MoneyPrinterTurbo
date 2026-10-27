"""Sanity-check finished clips: speaker switches inside a clip, speaker separation, pitch."""
import csv
import csv as _csv_early
import sys
import warnings
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

warnings.filterwarnings("ignore")
from speechbrain.inference.speaker import EncoderClassifier  # noqa: E402

root = Path(sys.argv[1])
enc = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb", savedir=str(Path.home() / ".cache/voice-narrator/ecapa"),
    run_opts={"device": "cpu"},
)
SR = 16000


def emb(x):
    with torch.no_grad():
        v = enc.encode_batch(x.unsqueeze(0)).squeeze().numpy()
    return v / np.linalg.norm(v)


rows = [r for r in csv.DictReader(open(root / "manifest.csv")) if r["speaker"] != "unsorted"]
per_spk, clip_info = {}, []
for r in rows:
    d, sr = sf.read(str(root / r["file"]))
    w = torchaudio.functional.resample(torch.from_numpy(d.astype(np.float32)), sr, SR)
    whole = emb(w)
    wins = [emb(w[i:i + 2 * SR]) for i in range(0, len(w) - 2 * SR + 1, SR)]
    f0 = torchaudio.functional.detect_pitch_frequency(w, SR, freq_low=70, freq_high=450)
    f0 = f0[(f0 > 75) & (f0 < 440)]
    per_spk.setdefault(r["speaker"], []).append(whole)
    clip_info.append((r["file"], whole, wins, float(f0.median()) if len(f0) else float("nan")))

cent = {s: np.mean(v, axis=0) for s, v in per_spk.items()}
cent = {s: c / np.linalg.norm(c) for s, c in cent.items()}
names = sorted(cent)
with open(root / "similarity.csv", "w", newline="") as _f:
    _w = _csv_early.writer(_f); _w.writerow([""] + names)
    for a in names:
        _w.writerow([a] + [round(float(cent[a] @ cent[b]), 2) for b in names])
print("speaker centroid cosine similarity (same person would be ~0.7+):")
for a in names:
    print(" ", a, " ".join(f"{float(cent[a] @ cent[b]):.2f}" for b in names))

import csv as _csv
with open(root / "verify.csv", "w", newline="") as _f:
    _w = _csv.writer(_f); _w.writerow(["file", "min_window_similarity", "median_pitch_hz"])
    for f, whole, wins, f0 in clip_info:
        spk = f.split("/")[0]
        _w.writerow([f, round(min((float(w @ cent[spk]) for w in wins), default=1.0), 2), round(f0)])

print("\nclips where a 2 s window drifts from its speaker (min window similarity < 0.45):")
bad = 0
for f, whole, wins, f0 in clip_info:
    spk = f.split("/")[0]
    ms = min((float(w @ cent[spk]) for w in wins), default=1.0)
    if ms < 0.45:
        bad += 1
        print(f"  {f}  min={ms:.2f}")
print(f"  {bad} flagged of {len(clip_info)}")

print("\nmedian pitch per speaker (Hz): ", end="")
for s in names:
    v = [c[3] for c in clip_info if c[0].startswith(s) and not np.isnan(c[3])]
    print(f"{s}={np.median(v):.0f}", end="  ")
print()
