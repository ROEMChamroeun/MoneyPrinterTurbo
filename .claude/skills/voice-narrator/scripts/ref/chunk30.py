"""Cut a cleaned narration into items of about 30 s, each starting and ending on a whole phrase.

  "$AV" chunk30.py SRC.wav chunks/phrases.json items [--target 30] [--prefix <voice-folder>]
Only `narrator` phrases go in; an item never spans a flagged phrase. Pauses inside an item longer than CAP are
shortened by cutting silence from their middle, so every phrase keeps its own fade-in and fade-out (Silero ends
phrases early on soft tails, so TAIL seconds after each end are always kept). The cut points are planned over the
whole narration at once: items of at most TARGET+0.5 s, as long as possible, cut at her longer pauses (0.6 s or
more; this narrator never pauses over 1 s between sentences, so pause length is the sentence marker). Output: mono
48 kHz 24-bit at -20 LUFS (peak under -1.5 dBFS) plus OUT_DIR/items.json with every phrase's place in its item.
"""
import argparse
import json
import os

import librosa
import numpy as np
import soundfile as sf
import pyloudnorm as pyln

SR = 48000
CAP, LEAD, TAIL, XF = 0.5, 0.20, 0.30, 0.010
TARGET_LUFS, PEAK_DB = -20.0, -1.5

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("phrases")
ap.add_argument("out")
ap.add_argument("--target", type=float, default=30.0)
ap.add_argument("--prefix", default="item")
a = ap.parse_args()

y, _ = librosa.load(a.src, sr=SR, mono=True)
ph = json.load(open(a.phrases))["phrases"]


def gap_kept(g):
    return g if g <= CAP else CAP


def span_len(i, j):
    """Item length for phrases i..j after pause capping, plus lead-in and tail."""
    n = LEAD + ph[j]["end"] - ph[i]["start"] + TAIL
    for k in range(i, j):
        g = ph[k + 1]["start"] - ph[k]["end"]
        n -= g - gap_kept(g)
    return n


def pause_after(j):
    return ph[j + 1]["start"] - ph[j]["end"] if j + 1 < len(ph) else 9.0


def end_cost(j, last):
    """Cutting after phrase j: free at a pause of 0.6 s or more (her sentence ends), a little at 0.45-0.6 s, and
    about an extra item's worth below that, more the shorter the pause, so a mid-sentence cut is the last resort
    and, when a stretch has no sentence end at all, lands on its longest pause."""
    p = pause_after(j)
    return 0 if last or p >= 0.6 else 5 if p >= 0.45 else 25 + 60 * (0.45 - p)


def short_cost(L, last):
    return 0 if last or L >= 20 else 3 * (20 - L)


def plan(run):
    """Cut one run of narrator phrases into items of at most TARGET+0.5 s: fewest items, then best cut points."""
    best = {run[0]: (0.0, None)}
    for j in run:
        for i in run:
            if i > j or i not in best or span_len(i, j) > a.target + 0.5 and i != j:
                continue
            L, last = span_len(i, j), j == run[-1]
            c = best[i][0] + (a.target - L) + end_cost(j, last) + short_cost(L, last)
            if j + 1 not in best or c < best[j + 1][0]:
                best[j + 1] = (c, i)
    out, k = [], run[-1] + 1
    while k != run[0]:
        i = best[k][1]
        out.append((i, k - 1))
        k = i
    return out[::-1]


items, run = [], []
for k, p in enumerate(ph + [{"speaker": "end"}]):
    if p["speaker"] == "narrator":
        run.append(k)
    elif run:
        items += plan(run)
        run = []


def fade(seg, head=True, tail=True):
    n = int(XF * SR)
    if head:
        seg[:n] *= np.linspace(0, 1, n)
    if tail:
        seg[-n:] *= np.linspace(1, 0, n)
    return seg


os.makedirs(a.out, exist_ok=True)
meter = pyln.Meter(SR)
manifest = []
for n, (i, j) in enumerate(items, 1):
    prev_mid = (ph[i - 1]["end"] + ph[i]["start"]) / 2 if i else 0.0
    next_mid = (ph[j]["end"] + ph[j + 1]["start"]) / 2 if j + 1 < len(ph) else len(y) / SR
    pieces = [[max(ph[i]["start"] - LEAD, prev_mid), None]]
    for k in range(i, j):
        if ph[k + 1]["start"] - ph[k]["end"] > CAP:  # keep TAIL of silence after, CAP - TAIL before the next
            pieces[-1][1] = ph[k]["end"] + TAIL
            pieces.append([ph[k + 1]["start"] - (CAP - TAIL), None])
    pieces[-1][1] = min(ph[j]["end"] + TAIL, next_mid)
    layout = []
    audio = []
    for p, (s, e) in enumerate(pieces):
        seg = fade(y[int(s * SR):int(e * SR)].copy())
        audio.append(seg)
    x = np.concatenate(audio)
    # where each phrase landed in the item (for transcripts)
    offset, cursor = [], 0.0
    for s, e in pieces:
        offset.append((s, e, cursor))
        cursor += e - s
    for k in range(i, j + 1):
        for s, e, c in offset:
            if s - 1e-6 <= ph[k]["start"] <= e:
                layout.append({"src_start": round(ph[k]["start"], 2), "src_end": round(ph[k]["end"], 2),
                               "item_start": round(c + ph[k]["start"] - s, 2), "item_end": round(c + ph[k]["end"] - s, 2)})
    lufs = meter.integrated_loudness(x)
    x = x * 10 ** ((TARGET_LUFS - lufs) / 20)
    peak = 20 * np.log10(np.abs(x).max())
    if peak > PEAK_DB:
        x = x * 10 ** ((PEAK_DB - peak) / 20)
    src_a, src_b = pieces[0][0], pieces[-1][1]
    name = f"{a.prefix}_{n:02d}_{int(src_a // 60):02d}m{int(src_a % 60):02d}s-{int(src_b // 60):02d}m{int(src_b % 60):02d}s"
    sf.write(os.path.join(a.out, name + ".wav"), x.astype(np.float32), SR, subtype="PCM_24")
    speech = sum(ph[k]["end"] - ph[k]["start"] for k in range(i, j + 1))
    manifest.append({"name": name, "src_start": round(src_a, 2), "src_end": round(src_b, 2),
                     "duration": round(len(x) / SR, 2), "speech": round(speech, 2), "phrases": layout,
                     "pause_after": round(min(pause_after(j), 9.0), 2), "lufs": round(meter.integrated_loudness(x), 1),
                     "peak": round(20 * np.log10(np.abs(x).max()), 1)})
    print(f"{name}  {len(x) / SR:5.2f} s  speech {speech:5.2f} s  {j - i + 1:2d} phrases  "
          f"pause after {pause_after(j):4.2f} s")
json.dump({"source": a.src, "items": manifest}, open(os.path.join(a.out, "items.json"), "w"), indent=1)
