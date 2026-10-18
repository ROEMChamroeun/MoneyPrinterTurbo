"""Synthesised sound design for the short (no samples, so nothing to license): sfx.wav, 48 kHz stereo.

What goes in, timed from vm/times.json (written by build_jsx.py):
  - a soft low hit on the first frame, a whoosh on the opening camera push and on the arrow flips
  - a quieter whoosh on every picture cut, a gentle river bed under the map scenes
  - rain while it rains on the map, rising blips on the lake counter (x1 -> x5), a pop for the comment bubble
Run: uv run --with numpy --with scipy python tools/sfx.py
"""
from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent.parent
SR = 48000
EV = json.loads((HERE / "vm/times.json").read_text())
T, LEN = EV["T"], EV["len"]
rng = np.random.default_rng(7)
out = np.zeros((int((LEN + 1) * SR), 2), np.float32)


def db(x: float) -> float:
    return 10 ** (x / 20)


def put(t: float, x: np.ndarray, gain_db: float, pan: float | np.ndarray = 0.0) -> None:
    """Mix a mono signal at time t; pan -1 (left) .. 1 (right), constant power."""
    a = int(t * SR)
    x = x[: max(0, len(out) - a)] * db(gain_db)
    p = (np.asarray(pan) + 1) * np.pi / 4
    out[a:a + len(x), 0] += x * np.cos(p)
    out[a:a + len(x), 1] += x * np.sin(p)


def band(x: np.ndarray, lo: float, hi: float, order: int = 2) -> np.ndarray:
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def lowpass(x: np.ndarray, f: float) -> np.ndarray:
    return sosfilt(butter(2, f, btype="low", fs=SR, output="sos"), x)


def highpass(x: np.ndarray, f: float) -> np.ndarray:
    return sosfilt(butter(2, f, btype="high", fs=SR, output="sos"), x)


def norm(x: np.ndarray) -> np.ndarray:
    return x / (np.max(np.abs(x)) + 1e-9)


def whoosh(dur: float, f0: float = 250, f1: float = 2600) -> np.ndarray:
    """Noise through a band that sweeps up, in short blocks; swelling then fading."""
    n = int(dur * SR)
    noise = rng.standard_normal(n + SR // 10)
    y = np.zeros(n)
    block = 512
    for i in range(0, n, block):
        u = i / n
        fc = f0 * (f1 / f0) ** u
        seg = band(noise[i:i + block + 2048], fc / 1.6, min(fc * 1.6, SR / 2 - 100))[2048 - 2048:][:block]
        y[i:i + block] = seg[: len(y[i:i + block])]
    env = np.sin(np.pi * np.clip(np.linspace(0, 1, n) ** 0.8, 0, 1)) ** 2
    return norm(y * env)


def hit(dur: float = 1.2) -> np.ndarray:
    t = np.arange(int(dur * SR)) / SR
    sub = np.sin(2 * np.pi * (48 + 30 * np.exp(-t * 18)) * t) * np.exp(-t * 3.2)
    click = lowpass(rng.standard_normal(len(t)), 1800) * np.exp(-t * 60) * 0.5
    return norm(sub + click)


def blip(freq: float, dur: float = 0.09) -> np.ndarray:
    t = np.arange(int(dur * SR)) / SR
    env = np.minimum(t / 0.004, 1) * np.exp(-t * 38)
    return norm((np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)) * env)


def pop() -> np.ndarray:
    t = np.arange(int(0.14 * SR)) / SR
    f = 380 + 700 * np.minimum(t / 0.05, 1)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30))


def bed(t0: float, t1: float, kind: str) -> np.ndarray:
    """River bed (brown noise, low) or rain (hiss plus droplets), with 0.5 s fades."""
    n = int((t1 - t0) * SR)
    if kind == "river":
        x = lowpass(np.cumsum(rng.standard_normal(n)) * 0.02, 520)
        x = highpass(x, 60)
        x *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.13 * np.arange(n) / SR)
    else:
        x = band(rng.standard_normal(n), 900, 9000) * 0.6
        drops = np.zeros(n)
        idx = rng.integers(0, n, int((t1 - t0) * 70))
        drops[idx] = rng.uniform(0.3, 1.0, len(idx))
        x += band(drops, 1500, 7000) * 6
    fade = int(0.5 * SR)
    env = np.ones(n)
    env[:fade] = np.linspace(0, 1, fade)
    env[-fade:] = np.linspace(1, 0, fade)
    return norm(x) * env


# ---- the mix (levels relative to full scale; the export normalises the whole film to -14 LUFS)
put(0.0, hit(), -14)
put(0.45, whoosh(2.1, 180, 1800), -22, np.linspace(-0.6, 0.6, int(2.1 * SR)))
for t in (T["hook_flip"] - 0.1, T["flip_back"] - 0.1):
    put(t, whoosh(0.45, 600, 4000), -24, 0.2)
for c in EV["cuts"]:
    put(c - 0.18, whoosh(0.42, 400, 3500), -26, np.linspace(0.5, -0.5, int(0.42 * SR)))
for a, b in EV["map_spans"]:
    put(a, bed(a, b, "river"), -36)
put(T["rain_in"], bed(T["rain_in"], T["rain_out"] + 0.4, "rain"), -30)
for i, c in enumerate(EV["count"]):
    put(c, blip(660 * 2 ** (i * 2 / 12)), -24, 0.3)
put(T["write"], pop(), -20)

out = out[: int(LEN * SR)]
peak = np.max(np.abs(out))
if peak > db(-3):
    out *= db(-3) / peak
with wave.open(str(HERE / "sfx.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print(f"sfx.wav: {LEN:.2f}s, peak {20 * np.log10(np.max(np.abs(out)) + 1e-9):.1f} dBFS, "
      f"{len(EV['cuts'])} cut whooshes, rain {T['rain_in']:.2f}-{T['rain_out']:.2f}s")
