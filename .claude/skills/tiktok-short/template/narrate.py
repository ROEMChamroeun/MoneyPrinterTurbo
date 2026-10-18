"""Narrate the short-01 river short (script_km.py) with a VoiceStudio clone, one sentence at a time (VoxCPM2 on MLX).

Copied from ../plan-09-dub/narrate.py (same model patches, continuation cloning, caching, levelling).
Calm breath marks (khmer_phrasing.relax) stay OFF by default: a TikTok short keeps a brisk pace (--relax turns them on).

Run with VoiceStudio's runtime python:
  "$HOME/Library/Application Support/VoiceStudio/runtime/project/.venv/bin/python" narrate.py \
      [--profile khmer-voice-artist] [--seed 7] [--only l01,l02] [--relax]
Outputs: narration/<line id>.wav, narration/index.json (durations, piece times), narration/pace.csv.
"""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
import wave
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
import numpy as np
import mlx.core as mx
from mlx_audio.tts.utils import load
import mlx_audio.tts.models.voxcpm2 as _voxcpm2_pkg

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "khmer-film"))
from script_km import LINES                                   # noqa: E402
from khmer_phrasing import relax                              # noqa: E402
from khmer_speech import speak, speech_problems               # noqa: E402

# the two local patches mlx-audio 0.5.0 needs (same as voice_test.py)
_orig_from_dict = _voxcpm2_pkg.ModelConfig.from_dict.__func__


def _from_dict_keep_path(cls, config):
    cfg = _orig_from_dict(cls, config)
    cfg.model_path = config.get("model_path")
    return cfg


_voxcpm2_pkg.ModelConfig.from_dict = classmethod(_from_dict_keep_path)


def _post_load_hook(cls, model, model_path):
    from transformers import AutoTokenizer
    if model.tokenizer is None:
        model.tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
    return model


_voxcpm2_pkg.Model.post_load_hook = classmethod(_post_load_hook)

STEPS, CFG = 10, 2.0
MIN_PIECE = 28                 # characters; a shorter sentence is merged with the neighbour
GAP_PIECE = 0.22
TARGET_DB, MAX_GAIN_DB = -20.0, 10.0

ap = argparse.ArgumentParser()
ap.add_argument("--profile", default="khmer-voice-artist")
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--only", default="", help="comma separated line ids")
ap.add_argument("--relax", action="store_true", help="add calm breath marks (slower)")
a = ap.parse_args()

studio = os.path.expanduser("~/Library/Application Support/OmniVoice")
con = sqlite3.connect(f"file:{studio}/omnivoice.db?mode=ro", uri=True)
row = con.execute("select id, name, ref_audio_path, ref_text from voice_profiles where id=? or name=?",
                  (a.profile, a.profile)).fetchone()
if row is None:
    raise SystemExit(f"No VoiceStudio voice called {a.profile!r}")
pid, vname, ref_file, ref_text = row
ref = os.path.join(studio, "voices", ref_file)
if not (ref_text or "").strip():
    raise SystemExit(f"{vname} has no transcript. Ask the user for the exact Khmer text of its clip first.")
print(f"voice: {vname} ({pid}) | mode: transcript ({len(ref_text)} chars)", flush=True)

NAR = HERE / "narration"
(NAR / "pieces").mkdir(parents=True, exist_ok=True)
INDEX = NAR / "index.json"
index = json.loads(INDEX.read_text()) if INDEX.exists() else {}


def split_sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[។?])\s*", text.strip()) if s]


def make_pieces(sentences: list[str]) -> list[list[int]]:
    """Group sentence indices into pieces: one sentence each, short ones merged forward (or back at the end)."""
    pieces: list[list[int]] = []
    cur: list[int] = []
    for i, s in enumerate(sentences):
        cur.append(i)
        if sum(len(sentences[j]) for j in cur) >= MIN_PIECE:
            pieces.append(cur)
            cur = []
    if cur:
        if pieces:
            pieces[-1].extend(cur)
        else:
            pieces.append(cur)
    return pieces


def trim(x, sr):
    fr = int(0.01 * sr)
    rms = np.array([np.sqrt(np.mean(x[i:i + fr] ** 2)) for i in range(0, len(x) - fr, fr)])
    on = np.where(20 * np.log10(rms + 1e-9) > 20 * np.log10(rms.max() + 1e-9) - 45)[0]
    if not len(on):
        return x
    pad = int(0.04 * sr)
    return x[max(on[0] * fr - pad, 0):min((on[-1] + 1) * fr + pad, len(x))]


def level(x, sr):
    fr = int(0.02 * sr)
    rms = np.array([np.sqrt(np.mean(x[i:i + fr] ** 2)) for i in range(0, len(x) - fr, fr)])
    act = rms[20 * np.log10(rms + 1e-9) > 20 * np.log10(rms.max() + 1e-9) - 35]
    gain = TARGET_DB - 20 * np.log10(np.sqrt(np.mean(act ** 2)) + 1e-9)
    return x * 10 ** (np.clip(gain, -MAX_GAIN_DB, MAX_GAIN_DB) / 20)


def write_wav(path, audio, sr):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())


def read_wav(path):
    with wave.open(str(path)) as w:
        sr = w.getframerate()
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768, sr


only = {x.strip() for x in a.only.split(",") if x.strip()}
todo = [ln for ln in LINES if not only or ln["id"] in only]

# fail early, before the model loads
for ln in todo:
    probs = speech_problems(speak(ln["say"] or ln["text"]))
    if probs:
        raise SystemExit(f"line {ln['id']}: {probs}")

t0 = time.time()
model = load("openbmb/VoxCPM2")
sr = getattr(model, "sample_rate", 48000)
print(f"model loaded in {time.time() - t0:.1f}s | active memory {mx.get_active_memory() / 1e9:.1f} GB", flush=True)

pace_rows = []
t_all = time.time()
for n, ln in enumerate(todo, 1):
    speech_sentences = split_sentences(speak(ln["say"] or ln["text"]))
    pieces = make_pieces(speech_sentences)
    audio_parts, piece_info = [], []
    for k, idxs in enumerate(pieces):
        text = " ".join(speech_sentences[j] for j in idxs)
        if a.relax:
            text = relax(text)
        key = hashlib.sha1(f"{pid}|{a.seed}|{STEPS}|{CFG}|{text}".encode()).hexdigest()[:10]
        path = NAR / "pieces" / f"{ln['id']}_{k}_{key}.wav"
        if path.exists():
            audio, _ = read_wav(path)
            took = 0.0
        else:
            mx.random.seed(a.seed)
            t = time.time()
            audio = np.concatenate([np.array(r.audio, dtype=np.float32).reshape(-1)
                                    for r in model.generate(text=text, inference_timesteps=STEPS, cfg_value=CFG,
                                                            ref_audio=ref, prompt_audio=ref, prompt_text=ref_text)])
            took = time.time() - t
            write_wav(path, audio, sr)
        clean = level(trim(audio, sr), sr)
        audio_parts.append(clean)
        dur = len(clean) / sr
        piece_info.append({"sentences": idxs, "chars": len(text), "dur": dur, "text": text})
        pace_rows.append((ln["id"], k, len(text), round(dur, 2), round(len(text) / max(dur, 0.1), 1)))
        print(f"[{n}/{len(todo)}] {ln['id']} piece {k + 1}/{len(pieces)}: {dur:4.1f}s audio "
              f"({len(text)} chars, {len(text) / max(dur, 0.1):4.1f} ch/s) in {took:5.1f}s", flush=True)

    gap = np.zeros(int(GAP_PIECE * sr), np.float32)
    joined, t_cursor = [], 0.0
    for k, (part, info) in enumerate(zip(audio_parts, piece_info)):
        info["at"] = round(t_cursor, 3)
        joined.append(part)
        t_cursor += info["dur"]
        if k < len(audio_parts) - 1:
            joined.append(gap)
            t_cursor += GAP_PIECE
    line_audio = np.concatenate(joined)
    write_wav(NAR / f"{ln['id']}.wav", line_audio, sr)
    index[ln["id"]] = {
        "start": ln["start"], "text": ln["text"], "speech": " ".join(p["text"] for p in piece_info),
        "dur": round(len(line_audio) / sr, 3), "sr": sr, "voice": pid, "seed": a.seed,
        "pieces": [{k: v for k, v in p.items() if k != "text"} for p in piece_info],
    }
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=1))

if pace_rows:
    with open(NAR / "pace.csv", "a") as f:
        for r in pace_rows:
            f.write(",".join(map(str, r)) + "\n")
print(f"done: {len(todo)} lines in {(time.time() - t_all) / 60:.1f} min", flush=True)
