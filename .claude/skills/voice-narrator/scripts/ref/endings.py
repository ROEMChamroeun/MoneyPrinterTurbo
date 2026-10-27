"""Do phrase endings fade out naturally, or are they snapped to silence by a gate (DeepFilterNet, separators)?

  "$AV" endings.py chunks/phrases.json STEM.wav [STEM2.wav ...]
For each narrator phrase: the biggest drop between two 10 ms frames in the last 0.2 s of speech plus 0.4 s after
(levels floored at -100 dB). Natural speech fades in steps of about 10 dB; a gate cuts 60-85 dB at once. Prints
the median drop and the share of endings that drop more than 30 dB in one step, per file.
"""
import json
import sys

import librosa
import numpy as np

SR, HOP = 16000, 160
ph = [p for p in json.load(open(sys.argv[1]))["phrases"] if p["speaker"] == "narrator"]
for path in sys.argv[2:]:
    y, _ = librosa.load(path, sr=SR)
    db = 20 * np.log10(np.maximum(librosa.feature.rms(y=y, frame_length=HOP, hop_length=HOP, center=False)[0], 1e-5))
    drops = []
    for p in ph:
        a, b = int((p["end"] - 0.2) * SR / HOP), int((p["end"] + 0.4) * SR / HOP)
        d = -np.diff(db[a:b])
        if len(d):
            drops.append(d.max())
    drops = np.array(drops)
    print(f"{path.split('/')[-1]:32s} median biggest drop {np.median(drops):5.1f} dB   "
          f"cut-off (>30 dB in 10 ms) {100 * (drops > 30).mean():4.0f}%   n={len(drops)}")
