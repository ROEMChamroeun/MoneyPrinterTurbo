"""Place the narrated lines on the short's timeline and time every caption row to the voice.

Inputs: script_km.py (words, caption marks, scenes), narration/index.json (line durations),
narration/align.json (when each spoken character starts, from tools/align_km.py).
Outputs:
  timeline.json        line starts/ends, caption blocks with each row's time, scene spans, video length
  narration_full.wav   all lines placed on the timeline (48 kHz mono)
Run: python3 timeline.py
"""
from __future__ import annotations

import json
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "khmer-film"))
from khmer_speech import speak          # noqa: E402
from script_km import LINES             # noqa: E402

LEAD = 0.25                              # silence before the first word: the hook must start at once
GAP = 0.45                               # between lines
GAP_BEFORE = {"l06": 0.65, "l08": 0.55}  # a beat before the festival montage and the closing question
TAIL = 1.8                               # end card after the last word
ROW_LEAD = 0.06                          # a row appears this long before its first sound

index = json.loads((HERE / "narration/index.json").read_text())
align = json.loads((HERE / "narration/align.json").read_text())


def spoken_offset(text: str, offset: int) -> int:
    """Caption-text character offset -> offset in the spoken text (repeat marks change the length)."""
    return len(speak(text[:offset] + "x")) - 1


t = LEAD
lines, blocks_out = [], []
for ln in LINES:
    t += GAP_BEFORE.get(ln["id"], 0.0) if lines else 0.0
    start, dur = round(t, 3), index[ln["id"]]["dur"]
    times = align[ln["id"]]
    rows_t = []
    for b in ln["blocks"]:
        rows = []
        for r in b:
            k = min(spoken_offset(ln["text"], r["offset"]), len(times) - 1)
            rows.append({"text": r["text"], "big": r["big"], "t": round(start + max(times[k] - ROW_LEAD, 0), 3)})
        rows_t.append(rows)
    for i, rows in enumerate(rows_t):
        nxt = rows_t[i + 1][0]["t"] if i + 1 < len(rows_t) else None
        blocks_out.append({"line": ln["id"], "scene": ln["scene"], "start": rows[0]["t"], "end": nxt, "rows": rows})
    lines.append({"id": ln["id"], "scene": ln["scene"], "start": start, "end": round(start + dur, 3),
                  "dur": dur, "text": ln["text"]})
    t = start + dur + GAP

length = round(lines[-1]["end"] + TAIL, 3)
# a block with no successor in its line stays until the next line's first block (or the end of the video)
for i, b in enumerate(blocks_out):
    if b["end"] is None:
        b["end"] = blocks_out[i + 1]["start"] if i + 1 < len(blocks_out) else length

# scenes: each runs from its line's start (the hook from 0) to the next scene's start
scenes = []
for i, ln in enumerate(lines):
    s = 0.0 if i == 0 else round(ln["start"] - 0.2, 3)
    scenes.append({"scene": ln["scene"], "line": ln["id"], "start": s})
for i, sc in enumerate(scenes):
    sc["end"] = scenes[i + 1]["start"] if i + 1 < len(scenes) else length

# phrase markers inside lines (seconds on the video timeline), for picture cuts that follow the words
markers = {}
for b in blocks_out:
    for r in b["rows"]:
        markers.setdefault(r["text"], r["t"])

out = {"fps": 30, "width": 1080, "height": 1920, "length": length, "lines": lines, "scenes": scenes,
       "blocks": blocks_out, "markers": markers}
(HERE / "timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))

# narration track
sr = index["l01"]["sr"]
mix = np.zeros(int(length * sr) + sr, np.float32)
for ln in lines:
    with wave.open(str(HERE / "narration" / f'{ln["id"]}.wav')) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    a = int(ln["start"] * sr)
    mix[a:a + len(x)] += x
mix = mix[:int(length * sr)]
with wave.open(str(HERE / "narration_full.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())

for ln in lines:
    print(f'{ln["id"]} {ln["scene"]:6s} {ln["start"]:6.2f} -> {ln["end"]:6.2f}')
for b in blocks_out:
    print(f'   {b["start"]:6.2f}-{b["end"]:6.2f}  ' + " | ".join(("*" if r["big"] else "") + r["text"] for r in b["rows"]))
print(f"length {length:.2f}s, {len(blocks_out)} caption blocks, narration_full.wav at {sr} Hz")
