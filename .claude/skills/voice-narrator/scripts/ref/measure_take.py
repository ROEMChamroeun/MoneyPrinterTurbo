"""How close a narration is to its voice's reference, piece by piece: pace, pitch, voice similarity, background gap.

  "$AV" measure_take.py narrate/test_s7 [narrate/test_s11 ...]     # folders written by narrate.py

The reference (audio and transcript) is read from VoiceStudio's database through the voice id in spans.json.
Pace = characters (no spaces or punctuation) per second of speech, measured the same way on both.
Similarity = ECAPA cosine to the reference. One speaker usually scores 0.7 or more on lines of a few seconds; ECAPA
needs length, so pieces under about 1.5 s read low even when the voice is right (0.48-0.71 measured on 0.9 s slices
of the narrator's own speech). Another voice scores about 0.2.
Gap = 95th vs 10th percentile frame level inside the piece. Read it against the reference's own gap: short pieces
sit a little under it (drama-sister-girl-001-v2: reference 41.5 dB, pieces 24-42 dB). Lines far under their
reference carry its room or noise: fav-song-girl's noisy reference gave 22-28 dB lines, its cleaned one 35-58 dB.
Then clean the reference, not the take.
"""
import json
import os
import re
import sqlite3
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
import librosa
import numpy as np
import torch
from speechbrain.inference.speaker import EncoderClassifier

STUDIO = os.path.expanduser("~/Library/Application Support/OmniVoice")
enc = EncoderClassifier.from_hparams("speechbrain/spkrec-ecapa-voxceleb",
                                     savedir=os.path.expanduser("~/.cache/voice-narrator/ecapa"),
                                     run_opts={"device": "cpu"})


def chars(s):
    return len(re.sub(r"[\s។៕៖,.!?\"'«»“”()\-–—ៗ…​]", "", s))


def stats(y):
    db = 20 * np.log10(librosa.feature.rms(y=y, frame_length=400, hop_length=160)[0] + 1e-9)
    speech = (db > db.max() - 35).sum() * 0.01
    d = db[db > db.max() - 70]
    f0 = librosa.yin(y, fmin=80, fmax=600, sr=16000, frame_length=1024)
    voiced = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0][:len(f0)] > 0.02
    with torch.no_grad():
        e = torch.nn.functional.normalize(enc.encode_batch(torch.from_numpy(y)[None]).squeeze(), dim=0)
    return speech, float(np.median(f0[voiced])) if voiced.any() else 0.0, e, np.percentile(d, 95) - np.percentile(d, 10)


refs = {}
for folder in sys.argv[1:]:
    spans = json.load(open(os.path.join(folder, "spans.json")))
    vid = spans["voice_id"]
    if vid not in refs:
        con = sqlite3.connect(f"file:{STUDIO}/omnivoice.db?mode=ro", uri=True)
        name, audio, text = con.execute("select name, ref_audio_path, ref_text from voice_profiles where id=?",
                                        (vid,)).fetchone()
        rs, rp, re_, rg = stats(librosa.load(os.path.join(STUDIO, "voices", audio), sr=16000)[0])
        refs[vid] = (re_, chars(text) / rs, rp)
        print(f"reference {name} ({vid}): pace {chars(text) / rs:4.1f} chars/s  pitch {rp:4.0f} Hz  gap {rg:4.1f} dB")
    re_, rpace, rpitch = refs[vid]
    print(f"== {folder} (seed {spans['seed']})")
    sims, paces = [], []
    for p in spans["pieces"]:
        y = librosa.load(os.path.join(folder, p["file"]), sr=16000)[0]
        s, pitch, e, g = stats(y)
        sim, pace = float(e @ re_), chars(p["text"]) / s
        sims.append(sim)
        paces.append(pace)
        print(f"  {p['piece']:2d}: pace {pace:4.1f} ({pace / rpace - 1:+4.0%})  pitch {pitch:4.0f}  "
              f"similarity {sim:.2f}  gap {g:4.1f}  ({len(y) / 16000:4.1f} s)  {', '.join(p['flags'])}")
    print(f"  median: pace {np.median(paces):4.1f} vs {rpace:4.1f}, similarity {np.median(sims):.2f}")
