"""Khmer ASR draft of a reference's transcript, one line per phrase (beam 5; greedy shown where it disagrees).

  "$VS" asr_draft.py clean/s2/deverb48.wav items/items.json          # every item from chunk30.py or build_ref.py
  "$VS" asr_draft.py clean/s2/deverb48.wav chunks/phrases.json START END   # narrator phrases in a range

Items: writes <item>.draft.txt beside items.json (skips those already drafted, so a stopped run resumes). Phrases:
prints them. Each phrase is decoded alone from the stem at its source times, so Whisper never meets its token cut-off
on a long clip. A draft only: VoxCPM2 continues from the transcript, and a wrong one garbles every line, so the user
corrects it and the corrected text is what goes on the profile. On film or emotional speech two decodes of one clip
can disagree almost everywhere; say so instead of guessing. Runs on CPU, about 5 min per 30 s item (MPS stalled
under memory pressure).
"""
import json
import os
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
import librosa
import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor

MODEL = "seanghay/whisper-small-khmer-v2"
proc = WhisperProcessor.from_pretrained(MODEL)
model = WhisperForConditionalGeneration.from_pretrained(MODEL).eval()
y, _ = librosa.load(sys.argv[1], sr=16000)
data = json.load(open(sys.argv[2]))


def decode(a, b):
    seg = y[int((a - 0.05) * 16000):int((b + 0.1) * 16000)]
    feats = proc(seg, sampling_rate=16000, return_tensors="pt").input_features
    outs = []
    for beams in (1, 5):
        with torch.no_grad():
            ids = model.generate(feats, num_beams=beams, max_new_tokens=440)
        outs.append(proc.batch_decode(ids, skip_special_tokens=True)[0].strip())
    return outs[1], outs[0]


if "items" in data:
    folder = os.path.dirname(os.path.abspath(sys.argv[2]))
    for it in data["items"]:
        out = os.path.join(folder, it["name"] + ".draft.txt")
        if os.path.exists(out):
            continue
        lines, differ = [], 0
        for p in it["phrases"]:
            beam, greedy = decode(p["src_start"], p["src_end"])
            lines.append(beam + ("" if beam == greedy else f"    [greedy: {greedy}]"))
            differ += beam != greedy
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"{it['name']}: {len(lines)} phrases, {differ} where beam and greedy differ -> {out}", flush=True)
else:
    lo, hi = float(sys.argv[3]), float(sys.argv[4])
    for p in data["phrases"]:
        if p["speaker"] != "narrator" or p["start"] < lo - 0.05 or p["end"] > hi + 0.05:
            continue
        beam, greedy = decode(p["start"], p["end"])
        flag = "" if beam == greedy else f"\n                 greedy: {greedy}   <- decodes differ"
        print(f"{p['start']:7.2f}-{p['end']:7.2f}  {beam}{flag}", flush=True)
