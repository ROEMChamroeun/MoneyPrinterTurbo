"""Build a clone reference from a cleaned stem: the narrator's phrases inside START..END, long pauses capped at 0.5 s.

  "$AV" build_ref.py clean/s2/deverb48.wav chunks/phrases.json START END picks/<voice>_02m21s-02m50s.wav
      [--hpf 75] [--keep-other]

Same cut as chunk30.py, whose 28.6 s item became the approved doc-narrator-girl-002: phrases come from phrases.py,
whose edges already reach out to where the stem falls under -60 dB (Silero run on a short slice clips soft onsets by
about 0.2 s). Each phrase keeps 0.2 s before it and 0.3 s of tail, pauses over 0.5 s are shortened from their middle,
so every phrase keeps its own fade-in and fade-out. Phrases flagged `other` (another speaker) stop the build unless
--keep-other. Then a gentle high-pass well under the voice (75 Hz; 100-110 Hz for a high voice over rumble) and
loudness to -20 LUFS with peaks under -1.5 dBFS, mono 48 kHz 24-bit.
Writes OUT.json in chunk30's items.json shape (asr_draft.py reads it) and prints each phrase, so the transcript can
be drafted and checked phrase by phrase. VoxCPM2 hears the reference at 16 kHz: repairing a lossy source above 8 kHz
changes nothing for the clone.
"""
import argparse
import json
import os

import librosa
import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000
CAP, LEAD, TAIL, XF = 0.5, 0.20, 0.30, 0.010
TARGET_LUFS, PEAK_DB = -20.0, -1.5

ap = argparse.ArgumentParser()
ap.add_argument("stem")
ap.add_argument("phrases")
ap.add_argument("start", type=float)
ap.add_argument("end", type=float)
ap.add_argument("out")
ap.add_argument("--hpf", type=float, default=75.0)
ap.add_argument("--keep-other", action="store_true")
a = ap.parse_args()

y, _ = librosa.load(a.stem, sr=SR, mono=True)
allp = json.load(open(a.phrases))["phrases"]
idx = [k for k, p in enumerate(allp) if p["start"] >= a.start - 0.05 and p["end"] <= a.end + 0.05]
if not idx:
    raise SystemExit("No phrase lies inside START..END")
other = [allp[k] for k in idx if allp[k]["speaker"] != "narrator"]
if other and not a.keep_other:
    raise SystemExit("Another voice inside the range (check by ear, then pass --keep-other or move the range):\n" +
                     "\n".join(f"  {p['start']:.2f}-{p['end']:.2f}  sim {p['sim']:.2f}  f0 {p['f0']:.0f}" for p in other))
ph = [allp[k] for k in idx]
first, last = idx[0], idx[-1]
prev_mid = (allp[first - 1]["end"] + ph[0]["start"]) / 2 if first else 0.0
next_mid = (ph[-1]["end"] + allp[last + 1]["start"]) / 2 if last + 1 < len(allp) else len(y) / SR

pieces = [[max(ph[0]["start"] - LEAD, prev_mid), None]]
for k in range(len(ph) - 1):
    if ph[k + 1]["start"] - ph[k]["end"] > CAP:      # keep TAIL of silence after, CAP - TAIL before the next
        pieces[-1][1] = ph[k]["end"] + TAIL
        pieces.append([ph[k + 1]["start"] - (CAP - TAIL), None])
pieces[-1][1] = min(ph[-1]["end"] + TAIL, next_mid)

n = int(XF * SR)
audio, cursor, offsets = [], 0.0, []
for s, e in pieces:
    seg = y[int(s * SR):int(e * SR)].copy()
    seg[:n] *= np.linspace(0, 1, n)
    seg[-n:] *= np.linspace(1, 0, n)
    audio.append(seg)
    offsets.append((s, e, cursor))
    cursor += e - s
x = np.concatenate(audio)
if a.hpf > 0:
    x = sosfilt(butter(2, a.hpf, "highpass", fs=SR, output="sos"), x)
meter = pyln.Meter(SR)
x = x * 10 ** ((TARGET_LUFS - meter.integrated_loudness(x)) / 20)
peak = 20 * np.log10(np.abs(x).max())
if peak > PEAK_DB:
    x = x * 10 ** ((PEAK_DB - peak) / 20)
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
sf.write(a.out, x.astype(np.float32), SR, subtype="PCM_24")

layout = []
for p in ph:
    for s, e, c in offsets:
        if s - 1e-6 <= p["start"] <= e:
            layout.append({"src_start": round(p["start"], 2), "src_end": round(p["end"], 2),
                           "item_start": round(c + p["start"] - s, 2), "item_end": round(c + p["end"] - s, 2)})
            break
name = os.path.splitext(os.path.basename(a.out))[0]
speech = sum(p["end"] - p["start"] for p in ph)
json.dump({"source": a.stem, "items": [{"name": name, "src_start": round(pieces[0][0], 2),
                                        "src_end": round(pieces[-1][1], 2), "duration": round(len(x) / SR, 2),
                                        "speech": round(speech, 2), "phrases": layout,
                                        "lufs": round(meter.integrated_loudness(x), 1),
                                        "peak": round(20 * np.log10(np.abs(x).max()), 1)}]},
          open(os.path.splitext(a.out)[0] + ".json", "w"), indent=1)
for k, (p, l) in enumerate(zip(ph, layout), 1):
    print(f"phrase {k:2d}: source {p['start']:7.2f}-{p['end']:7.2f}   in ref {l['item_start']:5.2f}-{l['item_end']:5.2f}"
          f"   sim {p['sim']:.2f}")
print(f"wrote {a.out}: {len(x) / SR:.2f} s, {speech:.1f} s speech in {len(ph)} phrases, "
      f"{meter.integrated_loudness(x):.1f} LUFS, peak {20 * np.log10(np.abs(x).max()):.1f} dBFS")
