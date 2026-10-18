"""Word timing for the Khmer narration: when the voice says each character of each narrated line (narration/<id>.wav).

Forced alignment with the Khmer Whisper fine-tune (seanghay/whisper-small-khmer-v2, cached): the decoder is fed
the script's own spoken text (teacher forcing), and the cross-attention of the alignment heads is turned into
token start times with DTW, the method of openai-whisper's timing.py. Each character gets the start time of
the token holding its first byte. Output: narration/align.json {line id: [seconds into the line for each spoken char]}.

Run with VoiceStudio's runtime python (has transformers + torch):
  "$HOME/Library/Application Support/VoiceStudio/runtime/project/.venv/bin/python" tools/align_km.py [l01,l06]
"""
from __future__ import annotations

import json
import os
import sys
import wave
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
import numpy as np
import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "khmer-film"))
from khmer_speech import speak          # noqa: E402
from script_km import LINES             # noqa: E402

MODEL = "seanghay/whisper-small-khmer-v2"
# the fine-tune ships no alignment heads; these are openai/whisper-small's, which it was trained from
ALIGNMENT_HEADS = [[5, 3], [5, 9], [8, 0], [8, 4], [8, 7], [8, 8], [9, 0], [9, 7], [9, 9], [10, 5]]
FRAME = 0.02                            # seconds per encoder frame
MEDFILT = 7


def byte_decoder() -> dict[str, int]:
    """GPT-2 byte-level BPE: the printable character each byte is written as in token strings, reversed."""
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs, n = bs[:], 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {chr(c): b for b, c in zip(bs, cs)}


def load_16k(path: Path) -> np.ndarray:
    with wave.open(str(path)) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    n = int(len(x) * 16000 / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def dtw(cost: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n, m = cost.shape
    acc = np.full((n + 1, m + 1), np.inf)
    acc[0, 0] = 0
    step = np.zeros((n + 1, m + 1), np.int8)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = (acc[i - 1, j - 1], acc[i - 1, j], acc[i, j - 1])
            k = int(np.argmin(c))
            acc[i, j] = cost[i - 1, j - 1] + c[k]
            step[i, j] = k
    i, j, path = n, m, []
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        k = step[i, j]
        if k == 0:
            i, j = i - 1, j - 1
        elif k == 1:
            i -= 1
        else:
            j -= 1
    path.reverse()
    p = np.array(path)
    return p[:, 0], p[:, 1]


def medfilt(x: np.ndarray, w: int) -> np.ndarray:
    pad = w // 2
    xp = np.pad(x, [(0, 0)] * (x.ndim - 1) + [(pad, pad)], mode="reflect")
    win = np.lib.stride_tricks.sliding_window_view(xp, w, axis=-1)
    return np.median(win, axis=-1)


def main() -> None:
    only = set(sys.argv[1].split(",")) if len(sys.argv) > 1 else None
    proc = WhisperProcessor.from_pretrained(MODEL)
    tok = proc.tokenizer
    model = WhisperForConditionalGeneration.from_pretrained(MODEL, attn_implementation="eager").eval()
    bdec = byte_decoder()
    prefix = tok.convert_tokens_to_ids(["<|startoftranscript|>", "<|km|>", "<|transcribe|>", "<|notimestamps|>"])
    out_path = HERE / "narration/align.json"
    out = json.loads(out_path.read_text()) if out_path.exists() else {}
    for ln in LINES:
        if only and ln["id"] not in only:
            continue
        spoken = speak(ln["text"])
        text_ids = tok.encode(spoken, add_special_tokens=False)
        tok_bytes = [bytes(bdec[c] for c in t) for t in tok.convert_ids_to_tokens(text_ids)]
        assert b"".join(tok_bytes) == spoken.encode(), ln["id"]
        audio = load_16k(HERE / "narration" / f'{ln["id"]}.wav')
        n_frames = int(len(audio) / 16000 / FRAME)
        feats = proc(audio, sampling_rate=16000, return_tensors="pt").input_features
        ids = torch.tensor([prefix + text_ids + [tok.eos_token_id]])
        with torch.no_grad():
            res = model(input_features=feats, decoder_input_ids=ids, output_attentions=True)
        w = torch.stack([res.cross_attentions[l][0, h] for l, h in ALIGNMENT_HEADS]).numpy()[:, :, :n_frames]
        w = (w - w.mean(axis=-2, keepdims=True)) / (w.std(axis=-2, keepdims=True) + 1e-6)
        w = medfilt(w, MEDFILT).mean(axis=0)
        matrix = w[len(prefix) - 1:-1]                     # rows: <|notimestamps|>, then each text token
        rows, cols = dtw(-matrix)
        jumps = np.pad(np.diff(rows), (1, 0), constant_values=1).astype(bool)
        starts = cols[jumps] * FRAME                        # start of each row; drop the <|notimestamps|> row
        token_start = starts[1:len(text_ids) + 1]
        # character -> token holding its first byte
        char_t, byte_pos, k, acc = [], 0, 0, len(tok_bytes[0])
        for ch in spoken:
            while byte_pos >= acc and k + 1 < len(tok_bytes):
                k += 1
                acc += len(tok_bytes[k])
            char_t.append(round(float(token_start[min(k, len(token_start) - 1)]), 3))
            byte_pos += len(ch.encode())
        out[ln["id"]] = char_t
        spaces = [f"{spoken[i + 1:i + 6]}@{char_t[i + 1]:.2f}" for i, c in enumerate(spoken) if c == " "]
        print(f'{ln["id"]}: {len(text_ids)} tokens over {len(audio) / 16000:.2f}s | {" ".join(spaces)}', flush=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
