"""Phrase map of a vocal stem, with a speaker check: Silero VAD phrases, median pitch and ECAPA similarity to the
narrator's centroid per phrase.

  "$AV" phrases.py clean/s2/deverb48.wav chunks/phrases.json [--narrator-at SEC ...]
Silero starts phrases late on soft onsets (0.3 s on her first word) and ends them early, so each edge is moved out
to where the stem falls under EDGE_DB (the separator leaves pauses near digital silence), never past the middle of
the pause to the next phrase. --narrator-at marks the phrase holding SEC as hers after listening or checking.
The centroid is built in two passes (all phrases of 1.5 s or more, then only those within 0.55 of the first
centroid), so a few guest voices do not pull it. ECAPA needs length: 0.9 s slices of her own sentences score only
0.48-0.71, so phrases under 1.2 s are judged at 0.45 and by pitch; longer ones under 0.6 or more than half an
octave off her pitch are flagged `other` and never go into a 30 s item.
"""
import json
import os
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
import librosa
import numpy as np
import torch
from silero_vad import get_speech_timestamps, load_silero_vad
from speechbrain.inference.speaker import EncoderClassifier

SR, HOP, EDGE_DB, MAX_MOVE = 16000, 160, -60.0, 0.6
src, out = sys.argv[1], sys.argv[2]
keep = [float(t) for t in sys.argv[sys.argv.index("--narrator-at") + 1:]] if "--narrator-at" in sys.argv else []
y, _ = librosa.load(src, sr=SR)
stamps = get_speech_timestamps(torch.from_numpy(y), load_silero_vad(), sampling_rate=SR,
                               min_silence_duration_ms=150, speech_pad_ms=0)
phrases = [{"start": s["start"] / SR, "end": s["end"] / SR} for s in stamps]
db = 20 * np.log10(np.maximum(librosa.feature.rms(y=y, frame_length=HOP, hop_length=HOP, center=False)[0], 1e-7))
for k, p in enumerate(phrases):
    lo = (phrases[k - 1]["end"] + p["start"]) / 2 if k else 0.0
    hi = (p["end"] + phrases[k + 1]["start"]) / 2 if k + 1 < len(phrases) else len(y) / SR
    a, b = int(p["start"] * SR / HOP), int(p["end"] * SR / HOP)
    while a > max(lo * SR / HOP, a - MAX_MOVE * SR / HOP, 1) and db[a - 1] > EDGE_DB:
        a -= 1
    while b < min(hi * SR / HOP, b + MAX_MOVE * SR / HOP, len(db) - 1) and db[b] > EDGE_DB:
        b += 1
    p["vad"] = [round(p["start"], 3), round(p["end"], 3)]
    p["start"], p["end"] = a * HOP / SR, b * HOP / SR

enc = EncoderClassifier.from_hparams("speechbrain/spkrec-ecapa-voxceleb",
                                     savedir=os.path.expanduser("~/.cache/voice-narrator/ecapa"),
                                     run_opts={"device": "cpu"})
for p in phrases:
    seg = y[int(p["start"] * SR):int(p["end"] * SR)]
    f0, vf, _ = librosa.pyin(seg, fmin=70, fmax=600, sr=SR, frame_length=1024)
    f0 = f0[vf & ~np.isnan(f0)]
    p["f0"] = float(np.median(f0)) if len(f0) else 0.0
    with torch.no_grad():
        e = enc.encode_batch(torch.tensor(seg)[None]).squeeze().numpy()
    p["_emb"] = e / np.linalg.norm(e)


def centroid(ps):
    c = np.mean([p["_emb"] for p in ps], 0)
    return c / np.linalg.norm(c)


long_ = [p for p in phrases if p["end"] - p["start"] >= 1.5]
c = centroid(long_)
c = centroid([p for p in long_ if p["_emb"] @ c >= 0.55])
f0_med = float(np.median([p["f0"] for p in long_ if p["_emb"] @ c >= 0.6 and p["f0"]]))
for p in phrases:
    p["sim"] = float(p.pop("_emb") @ c)
    off_pitch = p["f0"] and abs(np.log2(p["f0"] / f0_med)) > 0.5
    short = p["end"] - p["start"] < 1.2
    p["speaker"] = "other" if p["sim"] < (0.45 if short else 0.6) or off_pitch else "narrator"
    if p["speaker"] == "other" and any(p["start"] <= t <= p["end"] for t in keep):
        p["speaker"], p["note"] = "narrator", "--narrator-at: checked by hand"

json.dump({"source": src, "narrator_f0": f0_med, "phrases": phrases}, open(out, "w"), indent=1, ensure_ascii=False)
speech = sum(p["end"] - p["start"] for p in phrases)
other = [p for p in phrases if p["speaker"] == "other"]
print(f"{len(phrases)} phrases, {speech:.1f} s speech, narrator f0 {f0_med:.0f} Hz")
# speech-to-pause gap: median frame level inside phrases vs in pauses (0.1 s clear of every phrase edge).
# 45 dB or more is clean; near -140 dB pauses mean the separator gated them, so look for hiss inside speech instead.
in_speech = np.zeros(len(db), bool)
near = np.zeros(len(db), bool)
for p in phrases:
    a, b = int(p["start"] * SR / HOP), int(p["end"] * SR / HOP)
    in_speech[a:b] = True
    near[max(a - 10, 0):b + 10] = True
if (~near).any():
    sp, pa = np.median(db[in_speech]), np.median(db[~near])
    print(f"speech {sp:.1f} dB, pauses {pa:.1f} dB: gap {sp - pa:.1f} dB")
print(f"flagged other: {len(other)} phrases, {sum(p['end'] - p['start'] for p in other):.1f} s")
for p in other:
    print(f"  {p['start']:7.2f}-{p['end']:7.2f}  {p['end'] - p['start']:4.2f}s  f0 {p['f0']:4.0f}  sim {p['sim']:.2f}")
