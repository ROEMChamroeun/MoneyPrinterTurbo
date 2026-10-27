#!/usr/bin/env python3
"""Studio voice toolkit: diagnose, master and compare spoken voice with SoundCraft.

Runs on the Ubuntu VM, where soundcraft-cli lives. `analyze`, `compare` and
`spectrogram` need only ffmpeg, numpy and scipy, so they also run on the Mac.

  se.py analyze FILE [FILE ...] [--target T] [--ref REF] [--json OUT]
  se.py master FILE --preset P[,P2,...] [--target T] [--ref REF] [--exact] [--plan-only]
  se.py render JOB_DIR
  se.py compare FILE [FILE ...] --out OUT.wav
  se.py spectrogram FILE --out OUT.png
  se.py presets
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, resample_poly, sosfilt, welch

SR = 48000
HOP = 480  # 10 ms analysis hop
WIN = 960  # 20 ms analysis window
HOME = Path(os.environ.get("SE_HOME", "/home/ubuntu/CHR/sound-engineer"))
PRESETS = Path(__file__).resolve().parent.parent / "assets" / "presets"

TARGETS = {
    "tiktok": {"lufs": -14.0, "tp": -1.5, "lra_max": 6.0, "label": "TikTok / Reels / Shorts"},
    "youtube": {"lufs": -14.0, "tp": -1.0, "lra_max": 8.0, "label": "YouTube"},
    "podcast": {"lufs": -16.0, "tp": -1.0, "lra_max": 8.0, "label": "Podcast (Apple / AES streaming)"},
    "broadcast": {"lufs": -23.0, "tp": -1.0, "lra_max": 15.0, "label": "EBU R128 broadcast"},
    "audiobook": {"rms": -20.0, "tp": -3.5, "lra_max": 10.0, "label": "ACX audiobook (RMS -23..-18 dB, peak <= -3 dB)"},
    "stem": {"lufs": -20.0, "tp": -3.0, "lra_max": 8.0, "label": "Voice stem for a later mix"},
}

# Thresholds for the checks. The noise limits follow ACX; the others are
# relative to the median speech level, so they hold at any input volume.
NOISE_FAIL, NOISE_WARN = -50.0, -60.0
SIB_WARN, SIB_HARSH = -6.0, -4.0  # loudest S sounds vs loud syllables; natural speech sits near -10
PLOSIVE_WARN = -10.0
PHRASE_WARN = 2.0
BANDWIDTH_WARN = 12000
DC_WARN = 0.002
LIMITER_WARN = 4.0

BANDS = [("<80", 20, 80), ("80-200", 80, 200), ("200-500", 200, 500), ("500-1k", 500, 1000),
         ("1k-2k", 1000, 2000), ("2k-5k", 2000, 5000), ("5k-9k", 5000, 9000),
         ("9k-16k", 9000, 16000), (">16k", 16000, 20000)]
THIRDS = 1000 * 2 ** (np.arange(-13, 13) / 3)  # 50 Hz .. 16 kHz

# Broad regions of eq_7band used to match a reference's tonal balance.
MATCH_BANDS = [("low_shelf", 63, 160, 120, 0.707), ("low_mid", 160, 500, 280, 1.0),
               ("mid", 500, 2000, 1000, 0.8), ("high_mid", 2000, 6300, 3800, 0.8),
               ("high_shelf", 6300, 16000, 9000, 0.707)]


# ---------------------------------------------------------------- helpers

def run(cmd, binary=False):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=not binary)
    if r.returncode:
        err = r.stderr.decode(errors="replace") if binary else r.stderr
        sys.exit(f"command failed: {' '.join(map(str, cmd))}\n{err[-3000:]}")
    return r


def db_amp(v):
    return float(20 * np.log10(max(float(v), 1e-10)))


def probe(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
             "stream=channels,sample_rate,codec_name:format=duration", "-of", "json", path])
    d = json.loads(r.stdout)
    s = d["streams"][0]
    return {"channels": int(s["channels"]), "rate": int(s["sample_rate"]), "codec": s["codec_name"],
            "seconds": round(float(d["format"]["duration"]), 2)}


def decode(path, channels):
    raw = run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", channels, "-ar", SR, "-"],
              binary=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, channels)


def loudness(path, channels):
    """EBU R128 via ffmpeg. Mono files count as dual-mono, the way they play on stereo."""
    af = "ebur128=peak=true" + (":dualmono=true" if channels == 1 else "")
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", af, "-f", "null", "-"]).stderr
    summary = err[err.rfind("Summary:"):]

    def grab(key):
        m = re.search(rf"\b{key}:\s+(-?[\d.]+|-inf)", summary)
        return float(m.group(1)) if m and m.group(1) != "-inf" else float("-inf")

    return {"lufs": grab("I"), "lra": grab("LRA"), "tp": grab("Peak")}


def frames_db(x):
    if len(x) < WIN:
        return np.array([10 * np.log10(np.mean(np.square(x, dtype=np.float64)) + 1e-20)])
    c = np.concatenate([[0.0], np.cumsum(np.square(x, dtype=np.float64))])
    starts = np.arange(0, len(x) - WIN + 1, HOP)
    return 10 * np.log10((c[starts + WIN] - c[starts]) / WIN + 1e-20)


def band(x, lo, hi):
    return sosfilt(butter(4, [lo, hi], btype="band", fs=SR, output="sos"), x)


def clip_runs(x, thr=0.999, min_run=3):
    n = 0
    for ch in x.T:
        d = np.diff(np.concatenate([[0], (np.abs(ch) >= thr).astype(np.int8), [0]]))
        n += int(np.sum(np.where(d == -1)[0] - np.where(d == 1)[0] >= min_run))
    return n


def pitch(mono, speech):
    """F0 of voiced speech frames by windowed autocorrelation at 8 kHz."""
    y = resample_poly(mono.astype(np.float64), 1, 6)
    sr, w, hop = 8000, 400, 80
    win = np.hanning(w)
    wac = np.fft.irfft(np.abs(np.fft.rfft(win, 2 * w)) ** 2)[:w]
    wac /= wac[0]
    lo, hi = sr // 500, sr // 55
    idx = np.where(speech)[0]
    if idx.size == 0:
        return np.array([])
    idx = idx[np.linspace(0, idx.size - 1, min(idx.size, 1500)).astype(int)]
    out = []
    for i in idx:
        seg = y[i * hop:i * hop + w]
        if seg.size < w:
            continue
        seg = (seg - seg.mean()) * win
        ac = np.fft.irfft(np.abs(np.fft.rfft(seg, 2 * w)) ** 2)[:w]
        if ac[0] <= 1e-12:
            continue
        ac = ac / ac[0] / np.maximum(wac, 1e-3)
        r = ac[lo:hi]
        if r.max() < 0.6:
            continue
        # The first strong peak is the period; later ones are its multiples (octave-down errors).
        peaks = np.where((r[1:-1] > r[:-2]) & (r[1:-1] >= r[2:]) & (r[1:-1] >= 0.85 * r.max()))[0] + 1
        k = lo + (int(peaks[0]) if peaks.size else int(np.argmax(r)))
        a_, b_, c_ = ac[k - 1], ac[k], ac[k + 1]
        d = a_ - 2 * b_ + c_
        out.append(sr / (k + (0.5 * (a_ - c_) / d if d else 0)))
    return np.array(out)


def speech_psd(mono, speech):
    mask = np.zeros(len(mono), bool)
    for i in np.where(speech)[0]:
        mask[i * HOP:i * HOP + WIN] = True
    xs = mono[mask] if mask.sum() > 8192 else mono
    return welch(xs, fs=SR, nperseg=8192)


def thirds_db(f, p):
    tot = p.sum()
    return np.array([10 * np.log10(p[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].sum() / tot + 1e-20)
                     for c in THIRDS])


def phrase_levels(speech, lv, gap=25, min_len=30):
    idx = np.where(speech)[0]
    if idx.size == 0:
        return []
    segs, start, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - prev > gap:
            segs.append((start, prev))
            start = i
        prev = i
    segs.append((start, prev))
    out = []
    for a, b in segs:
        if b - a + 1 >= min_len:
            sel = lv[a:b + 1][speech[a:b + 1]]
            out.append(float(10 * np.log10(np.mean(10 ** (sel / 10)))))
    return out


def fix_owner(path):
    """Files under /home/ubuntu belong to the ubuntu user; we run as root."""
    if hasattr(os, "geteuid") and os.geteuid() == 0 and str(path).startswith("/home/ubuntu"):
        subprocess.run(["chown", "-R", "ubuntu:ubuntu", str(path)], capture_output=True)


def stem_of(path):
    return re.sub(r"[^\w.-]+", "_", Path(path).stem)


# ---------------------------------------------------------------- analysis

def analyse(path):
    info = probe(path)
    x = decode(path, info["channels"])
    mono = x.mean(axis=1)
    a = {"file": str(path), "name": Path(path).name, **info, **loudness(path, info["channels"])}
    a["peak_db"] = db_amp(np.abs(x).max())
    a["rms_db"] = db_amp(np.sqrt(np.mean(np.square(mono, dtype=np.float64))))
    a["clipped"] = clip_runs(x)
    a["dc_offset"] = float(np.abs(x.mean(axis=0)).max())
    a["lr_corr"] = (float(np.corrcoef(x[:, 0], x[:, 1])[0, 1])
                    if info["channels"] == 2 and x[:, 0].std() > 0 and x[:, 1].std() > 0 else None)

    lv = frames_db(mono)
    digital = lv < -100
    live = lv[~digital]
    if live.size < 50:
        a["silent"] = True
        return a
    thr = max(np.percentile(live, 5) + 12, np.percentile(live, 95) - 35)
    speech = lv > thr
    pause = ~speech & ~digital
    a["speech_level"] = float(np.median(lv[speech]))
    # Loud-syllable level: the baseline for sibilance and plosives. Reverb tails don't drag it down.
    a["body_level"] = float(np.percentile(lv[speech], 80))
    a["speech_s"] = round(speech.sum() * HOP / SR, 1)
    quiet = pause.sum() + digital.sum()
    a["digital_pct"] = round(100 * digital.sum() / quiet) if quiet else 0
    if pause.sum() >= 20:
        a["noise_floor"] = float(np.percentile(lv[pause], 30))
        a["pauses"] = (f"{a['digital_pct']}% digital silence, rest room noise" if a["digital_pct"] >= 10
                       else "room noise")
    else:
        a["noise_floor"] = None
        a["pauses"] = "digital silence" if digital.sum() >= 20 else "none"
    a["snr"] = a["speech_level"] - a["noise_floor"] if a["noise_floor"] is not None else None
    sp = np.where(speech)[0]
    a["head_s"] = round(sp[0] * HOP / SR, 2)
    a["tail_s"] = round(max(0.0, a["seconds"] - (sp[-1] * HOP + WIN) / SR), 2)

    hf = frames_db(band(mono, 5000, 10000))
    lf = frames_db(band(mono, 25, 100))
    a["sibilance"] = float(np.percentile(hf[speech], 99) - a["body_level"])
    a["sib_p90_dbfs"] = float(np.percentile(hf[speech], 90))
    a["plosive"] = float(np.percentile(lf[speech], 99) - a["body_level"])

    f0 = pitch(mono, speech)
    if f0.size >= 20:
        a["f0_median"], a["f0_p5"] = float(np.median(f0)), float(np.percentile(f0, 5))
    else:
        a["f0_median"] = a["f0_p5"] = None

    f, p = speech_psd(mono, speech)
    tot = p.sum()
    a["bands"] = {name: float(10 * np.log10(p[(f >= lo) & (f < hi)].sum() / tot + 1e-20))
                  for name, lo, hi in BANDS}
    a["thirds"] = thirds_db(f, p).round(2).tolist()
    sel = (THIRDS >= 250) & (THIRDS <= 8000)
    a["tilt"] = float(np.polyfit(np.log2(THIRDS[sel]), np.array(a["thirds"])[sel], 1)[0])
    pd = 10 * np.log10(p + 1e-30)
    k = max(1, int(200 / (f[1] - f[0])))
    sm = np.convolve(np.pad(pd, k, mode="edge"), np.ones(k) / k, mode="same")[k:-k]
    above = np.where(sm > pd[(f >= 1000) & (f <= 4000)].mean() - 50)[0]
    a["bandwidth"] = float(f[above[-1]]) if above.size else 0.0
    hi_band = (f >= 4500) & (f <= 10000)
    a["sib_freq"] = float(f[hi_band][np.argmax(sm[hi_band])])

    ph = phrase_levels(speech, lv)
    a["phrases"] = len(ph)
    a["phrase_spread"] = float(np.std(ph)) if len(ph) > 1 else 0.0
    a["hpf_suggest"] = choose_hpf(a)[0]
    return a


def sibilance_of(path):
    """Just the sibilance number, for tuning loops."""
    mono = decode(path, 2).mean(axis=1)
    lv = frames_db(mono)
    live = lv[lv >= -100]
    speech = lv > max(np.percentile(live, 5) + 12, np.percentile(live, 95) - 35)
    hf = frames_db(band(mono, 5000, 10000))
    return float(np.percentile(hf[speech], 99) - np.percentile(lv[speech], 80))


def assess(a, target, stage="input", dry=True):
    """Return [(level, text)] where level is 'fail', 'warn', 'ok' or 'info'."""
    out = []
    t = TARGETS[target]
    if "rms" in t:
        d = a["rms_db"] - t["rms"]
        lvl = "ok" if abs(d) <= 1.0 else ("fail" if stage == "output" else "info")
        out.append((lvl, f"RMS {a['rms_db']:.1f} dB vs target {t['rms']:.0f} dB"))
    else:
        d = a["lufs"] - t["lufs"]
        lvl = "ok" if abs(d) <= 0.5 else ("fail" if stage == "output" else "info")
        out.append((lvl, f"loudness {a['lufs']:.1f} LUFS vs target {t['lufs']:.0f} (mastering sets this)"
                    if stage == "input" else f"loudness {a['lufs']:.1f} LUFS vs target {t['lufs']:.0f}"))
    lvl = "ok" if a["tp"] <= t["tp"] else ("fail" if stage == "output" else "info")
    out.append((lvl, f"true peak {a['tp']:.1f} dBTP (max {t['tp']})"))
    if a["clipped"]:
        out.append(("fail", f"{a['clipped']} clipped spots: repaired with adeclip; better to re-record or regenerate"))
    if a.get("silent"):
        return out + [("fail", "no signal")]
    if a["lra"] > t["lra_max"]:
        if a["seconds"] < 30:  # LRA needs program length; on short clips the phrase spread is the better guide
            out.append(("info", f"loudness range {a['lra']:.1f} LU (short clip, unreliable; phrase spread "
                                f"±{a['phrase_spread']:.1f} dB)"))
        else:
            out.append(("warn", f"loudness range {a['lra']:.1f} LU > {t['lra_max']:.0f}: needs more leveling"))
    else:
        out.append(("ok", f"loudness range {a['lra']:.1f} LU"))
    nf = a["noise_floor"]
    if not dry and stage == "output":
        out.append(("info", "noise floor not checked: the mood's reverb or noise bed fills the pauses on purpose"))
    elif nf is None:
        out.append(("ok" if a["pauses"] == "digital silence" else "info",
                    "pauses are digital silence" if a["pauses"] == "digital silence" else "no pauses to measure noise in"))
    elif nf > NOISE_FAIL:
        out.append(("fail", f"noise floor {nf:.0f} dBFS (SNR {a['snr']:.0f} dB): audible hiss/hum, denoise"))
    elif nf > NOISE_WARN:
        out.append(("warn", f"noise floor {nf:.0f} dBFS (SNR {a['snr']:.0f} dB): above the -60 studio limit"))
    else:
        out.append(("ok", f"noise floor {nf:.0f} dBFS (SNR {a['snr']:.0f} dB)"))
    if a["sibilance"] > SIB_HARSH:
        out.append(("fail", f"sibilance {a['sibilance']:+.1f} dB: S sounds louder than the voice, de-ess around {a['sib_freq'] / 1000:.1f} kHz"))
    elif a["sibilance"] > SIB_WARN:
        out.append(("warn", f"sibilance {a['sibilance']:+.1f} dB: S sounds a bit hot, de-ess around {a['sib_freq'] / 1000:.1f} kHz"))
    else:
        out.append(("ok", f"sibilance {a['sibilance']:+.1f} dB"))
    if a["plosive"] > PLOSIVE_WARN:
        out.append(("warn", f"low-end bursts {a['plosive']:+.1f} dB: plosives or rumble, steeper high-pass"))
    if a["phrase_spread"] > PHRASE_WARN:
        out.append(("warn", f"phrase levels vary ±{a['phrase_spread']:.1f} dB: level the phrases"))
    if stage == "input" and a["bandwidth"] < BANDWIDTH_WARN:
        out.append(("warn", f"audio stops at {a['bandwidth'] / 1000:.1f} kHz (low-rate or MP3 source): an air boost "
                            "only adds noise, regenerate or export at 48 kHz if possible"))
    if a["dc_offset"] > DC_WARN:
        out.append(("warn", f"DC offset {a['dc_offset']:.4f}: remove before processing"))
    if a["rate"] < 44100:
        out.append(("info", f"source sample rate {a['rate']} Hz"))
    return out


SYMBOL = {"fail": "✗", "warn": "!", "ok": "✓", "info": "·"}


def print_report(a, target, ref=None):
    ch = "mono" if a["channels"] == 1 else "stereo"
    print(f"\n== {a['name']}  ({ch}, {a['rate'] // 1000} kHz {a['codec']}, {a['seconds']:.1f} s)")
    if a.get("silent"):
        print("   no signal")
        return
    f0 = (f"pitch median {a['f0_median']:.0f} Hz, lowest {a['f0_p5']:.0f} Hz -> high-pass at {a['hpf_suggest']} Hz"
          if a["f0_median"] else f"no clear pitch -> high-pass at {a['hpf_suggest']} Hz")
    print(f"   level    {a['lufs']:.1f} LUFS, true peak {a['tp']:.1f} dBTP, LRA {a['lra']:.1f} LU, "
          f"speech {a['speech_level']:.1f} dBFS, RMS {a['rms_db']:.1f} dB")
    print(f"   voice    {f0}")
    print(f"   tone     tilt {a['tilt']:.1f} dB/oct, bandwidth {a['bandwidth'] / 1000:.1f} kHz, "
          f"sibilance {a['sibilance']:+.1f} dB @ {a['sib_freq'] / 1000:.1f} kHz, low bursts {a['plosive']:+.1f} dB")
    print(f"   timing   head {a['head_s']:.2f} s, tail {a['tail_s']:.2f} s, {a['phrases']} phrases "
          f"(spread ±{a['phrase_spread']:.1f} dB), pauses: {a['pauses']}")
    print("   bands    " + "  ".join(f"{k} {v:.0f}" for k, v in a["bands"].items()))
    if ref:
        print("   vs ref   " + "  ".join(f"{k} {a['bands'][k] - ref['bands'][k]:+.1f}" for k in a["bands"]))
    for lvl, text in assess(a, target):
        print(f"   {SYMBOL[lvl]} {text}")


# ---------------------------------------------------------------- planning

def ins(plugin, params, why=""):
    return {"plugin": plugin, "params": params, "why": why}


def choose_hpf(a):
    """(freq, eq_7band slope index, why). Every high-pass rotates phase and raises peaks (measured
    +1.4 dB at 100 Hz/12 dB and +2.6 dB at 150 Hz/18 dB on a high voice), so filter only as high
    and as steep as the source needs."""
    if a["bands"]["<80"] < -45 and a["plosive"] < -20:
        return 60, 0, "gentle 60 Hz safety high-pass: there is almost nothing below 80 Hz to remove"
    freq = int(np.clip(5 * round(0.5 * (a["f0_p5"] or 120) / 5), 60, 100))
    steep = a["plosive"] > PLOSIVE_WARN
    pitch_note = f" (lowest pitch ~{a['f0_p5']:.0f} Hz)" if a["f0_p5"] else ""
    return (freq, 2 if steep else 1,
            f"high-pass {freq} Hz ({'18' if steep else '12'} dB/oct) under the voice{pitch_note}: "
            "removes rumble and thumps without thinning it")


def load_preset(name):
    p = PRESETS / f"{name}.json"
    if not p.exists():
        sys.exit(f"unknown preset {name!r}; have: {', '.join(sorted(q.stem for q in PRESETS.glob('*.json')))}")
    return json.loads(p.read_text())


def match_eq(a, ref):
    """eq_7band params that move `a` part of the way toward `ref`'s tonal balance."""
    diff = np.array(ref["thirds"]) - np.array(a["thirds"])
    params, notes = {}, []
    for name, lo, hi, centre, q in MATCH_BANDS:
        sel = (THIRDS >= lo) & (THIRDS < hi)
        limit = 3.0 if name == "low_shelf" else 4.0
        g = float(np.clip(round(0.7 * diff[sel].mean() * 2) / 2, -limit, limit))
        if abs(g) >= 1.0:
            params.update({f"{name}_freq": centre, f"{name}_gain": g, f"{name}_q": q})
            notes.append(f"{centre} Hz {g:+.1f}")
    why = ("match the reference's tonal balance: " + ", ".join(notes)) if notes else "already close to the reference"
    return params, why


TIME_FX = {"room_reverb", "plate_reverb", "mod_delay", "chorus", "flanger", "phaser"}


def plan(a, preset, target, ref=None, exact=False):
    """Build the job: repair -> foundation chain from the analysis -> preset character -> master.

    Inserts with an "auto" block get one parameter tuned by measuring test bounces (see tune()).
    """
    fnd = preset.get("foundation", {})
    t = TARGETS[target]
    voice = []
    if exact:
        if not preset.get("as_tested"):
            sys.exit(f"preset {preset['name']!r} has no as-tested chain to recall")
        voice = [dict(i, why="as tested") for i in preset["as_tested"]["chain"] if i["plugin"] != "maximizer"]
    else:
        if a["dc_offset"] > DC_WARN:
            voice.append(ins("dc_offset_removal", {"cutoff": 5}, "remove DC offset"))
        freq, slope, why = choose_hpf(a)
        voice.append(ins("eq_7band", {"hpf_on": 1, "hpf_freq": freq, "hpf_slope": slope}, why))
        nf = a.get("noise_floor")
        if nf is not None and nf > NOISE_WARN and (a["snr"] or 0) >= 20:
            # ffmpeg 4.4's afftdn only takes ~6 dB off broadband hiss; a downward expander drops the
            # pauses, where hiss is audible, by another 12 dB (measured -49 -> -67 dBFS together).
            voice.append(ins("expander_gate", {"threshold": round(nf + 9), "ratio": 4, "range": 12, "attack": 1,
                                               "hold": 80, "release": 150},
                             f"lower the hiss between words by up to 12 dB (noise floor {nf:.0f} dBFS)"))
        comp = fnd.get("leveler", {})
        if comp is not False:
            heavy = a["lra"] > t["lra_max"] or a["phrase_spread"] > PHRASE_WARN
            thr = round(a["speech_level"]) - (2 if heavy else 0) + comp.get("threshold_offset", 0)
            params = {"threshold": thr, "ratio": 3.0 if heavy else 2.5, "attack": 12, "release": 100,
                      "knee": 6, "makeup": 0, "sc_hpf_on": 1, "sc_hpf_freq": 120}
            params.update({k: v for k, v in comp.items() if k != "threshold_offset"})
            voice.append(ins("compressor", params,
                             f"level the phrases: threshold at the median speech level ({a['speech_level']:.0f} dBFS), "
                             f"{params['ratio']}:1"))
        peak = None
        if fnd.get("peak", True) is not False and "lufs" in t and t["tp"] - t["lufs"] < 16:
            # A loud target needs a low peak-to-loudness ratio; a fast stage gets most of the way
            # so the limiter only shaves the last 1-2 dB. Presets that distort ("peak": "post")
            # create new peaks, so theirs goes after the character chain.
            goal = t["tp"] - t["lufs"] + 2.0
            peak = dict(ins("compressor", {"threshold": -12, "ratio": 4, "attack": 1, "release": 60,
                                           "knee": 3, "lookahead": 2},
                            f"fast peak control so the limiter works lightly (peak-to-loudness goal ≤ {goal:.1f} dB)"),
                        auto={"param": "threshold", "metric": "plr", "goal": [goal - 1.5, goal],
                              "min": round(a["speech_level"]) - 3, "max": -3})
            if fnd.get("peak") != "post":
                voice.append(peak)
        mood = []
        for i in preset.get("inserts", []):
            i = json.loads(json.dumps(i))
            if i.get("role") == "polish":
                if ref:
                    params, why = match_eq(a, ref)
                    i = ins("eq_7band", params, why)
                elif a["bandwidth"] < BANDWIDTH_WARN:
                    i["params"]["high_shelf_gain"] = 0
                    i["why"] = i.get("why", "") + " (air boost skipped: source stops at "f"{a['bandwidth'] / 1000:.1f} kHz)"
            mood.append(i)
        if fnd.get("deesser", True) is not False:
            # After compression and EQ boosts (both raise S sounds, measured +5 dB), before any
            # reverb or delay (so they don't splash them).
            freq = int(np.clip(round(a["sib_freq"] / 100) * 100, 4500, 9000))
            de = dict(ins("de_esser", {"freq": freq, "threshold": -25, "range": 6},
                          f"keep S sounds natural around {freq} Hz"),
                      auto={"param": "threshold", "metric": "sibilance", "goal": [-9.5, -7.5], "min": -40, "max": 0,
                            "widen": {"param": "range", "step": 2, "max": 12}})
            at = next((n for n, i in enumerate(mood) if i["plugin"] in TIME_FX), len(mood))
            mood.insert(at, de)
        voice += mood
        if peak and fnd.get("peak") == "post":
            peak["params"]["threshold"] = -18
            peak["auto"]["min"] = -40
            voice.append(peak)
    if len(voice) > 10:
        sys.exit(f"chain has {len(voice)} inserts; SoundCraft tracks hold 10")
    nf = a.get("noise_floor")
    denoise = None
    if not exact and nf is not None and nf > NOISE_WARN:
        denoise = {"nr": 12 if nf <= NOISE_FAIL else 20, "nf": int(np.clip(round(nf) + 14, -80, -20))}
    return {
        "input": a["file"],
        "stem": stem_of(a["file"]),
        "preset": preset["name"],
        "exact": exact,
        "target": {"name": target, **t},
        "deliver": {"channels": a["channels"], "bit_depth": 24, "formats": ["wav"]},
        "preclean": {"declip": a["clipped"] > 0, "declick": False, "denoise": denoise,
                     "tail_s": preset.get("tail_s", 0.0)},
        "voice": voice,
        "bed": preset.get("bed"),
        "master": {"ceiling": round(t["tp"] - 0.5, 2)},
        "dry": not preset.get("bed") and preset.get("tail_s", 0) == 0,
    }


# ---------------------------------------------------------------- rendering

def plugin_specs():
    out = run(["soundcraft-cli", "run", "--cmd", "engine.plugins"]).stdout
    data = json.loads(out[out.index("["):])
    return {p["id"]: {q["id"]: q for q in p["params"]} for p in data}


def validate(chain, specs, warnings):
    """SoundCraft clamps out-of-range values silently; catch them here instead."""
    for i in chain:
        if i["plugin"] not in specs:
            sys.exit(f"unknown plugin {i['plugin']!r}")
        for k, v in i.get("params", {}).items():
            q = specs[i["plugin"]].get(k)
            if q is None:
                sys.exit(f"{i['plugin']} has no parameter {k!r}; it has {', '.join(specs[i['plugin']])}")
            if not q["min"] <= v <= q["max"]:
                c = min(max(v, q["min"]), q["max"])
                warnings.append(f"{i['plugin']}.{k}={v} is outside {q['min']:g}..{q['max']:g}; using {c:g}")
                i["params"][k] = c


def preclean(src, dst, pc):
    filters = []
    if pc.get("declip"):
        filters.append("adeclip")
    if pc.get("declick"):
        filters.append("adeclick")
    if pc.get("denoise"):
        filters.append("afftdn=nr={nr}:nf={nf}:tn=1".format(**pc["denoise"]))
    if pc.get("tail_s"):
        filters.append(f"apad=pad_dur={pc['tail_s']}")  # end only: the start must stay put for captions
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src]
    if filters:
        cmd += ["-af", ",".join(filters)]
    run(cmd + ["-ar", SR, "-c:a", "pcm_s24le", dst])


def sc_script(job, voice_wav, gain, ceiling):
    def cmd(name, params):
        return f"{name} {json.dumps(params)}"

    lines = [cmd("session.new", {"name": job["stem"], "sample_rate": SR, "bit_depth": 24}),
             cmd("file.import_audio", {"path": str(voice_wav)})]
    for slot, i in enumerate(job["voice"]):
        lines.append(cmd("mix.insert", {"track": voice_wav.stem, "slot": slot, "plugin": i["plugin"],
                                        "params": i.get("params", {})}))
    if job.get("bed"):
        lines.append(cmd("track.new", {"kind": "audio", "format": "mono", "name": "bed"}))
        for slot, i in enumerate(job["bed"]["inserts"]):
            lines.append(cmd("mix.insert", {"track": "bed", "slot": slot, "plugin": i["plugin"],
                                            "params": i.get("params", {})}))
    # The limiter lives on the master: on a mono track the pan law takes 3 dB off after it.
    lines.append(cmd("track.new", {"kind": "master", "format": "stereo"}))
    lines.append(cmd("mix.insert", {"track": "Master 1", "slot": 0, "plugin": "gain",
                                    "params": {"gain": round(gain, 2)}}))
    if ceiling is not None:
        lines.append(cmd("mix.insert", {"track": "Master 1", "slot": 1, "plugin": "maximizer",
                                        "params": {"threshold": 0, "ceiling": round(ceiling, 2), "release": 50}}))
    return "\n".join(lines) + "\n"


def bounce(job, voice_wav, work, gain, ceiling, save=None):
    script = work / "render.sc"
    script.write_text(sc_script(job, voice_wav, gain, ceiling))
    cmd = ["soundcraft-cli", "script", script, "--bounce", work / "bounce.wav"]
    if save:
        cmd += ["--save", save]
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    text = r.stdout + r.stderr
    errors = [ln for ln in text.splitlines() if re.match(r"^\S+\.sc:\d+: ", ln)]
    if r.returncode or errors:
        sys.exit("SoundCraft failed:\n" + "\n".join(errors or text.splitlines()[-10:]))
    for ln in reversed(text.splitlines()):
        if '"lufs"' in ln:
            return json.loads(ln[ln.index("{"):])
    sys.exit("SoundCraft printed no bounce result:\n" + text[-2000:])


def level_of(b, metric, wav):
    if metric == "lufs":
        return b["lufs"]
    x = decode(wav, 2).mean(axis=1)
    return db_amp(np.sqrt(np.mean(np.square(x, dtype=np.float64))))


def tune(job, voice_wav, work):
    """Set each insert's "auto" parameter, in chain order, by measuring bounces without the limiter.

    The plugins' detectors don't map cleanly onto analysis numbers, so measuring is more reliable
    than predicting. A bounce takes ~0.2 s per 20 s of audio. Delete an insert's "auto" block in
    job.json to pin its value by hand.
    """
    notes = []

    def measure():
        b = bounce(job, voice_wav, work, 0.0, None)
        return b["true_peak_db"] - b["lufs"] if au["metric"] == "plr" else sibilance_of(work / "bounce.wav")

    for i in job["voice"]:
        au = i.get("auto")
        if not au:
            continue
        lo, hi = au["goal"]
        key, wid = au["param"], au.get("widen")
        m = measure()
        for _ in range(10):
            if lo <= m <= hi:
                break
            v = i["params"][key]
            step = float(np.clip(abs(m - (lo + hi) / 2) * 1.5, 1, 8))
            nv = float(np.clip(v - step if m > hi else v + step, au["min"], au["max"]))
            if nv == v:
                if not (wid and m > hi and i["params"].get(wid["param"], 0) < wid["max"]):
                    break
                i["params"][wid["param"]] = min(i["params"].get(wid["param"], 0) + wid["step"], wid["max"])
            else:
                i["params"][key] = round(nv, 1)
            m = measure()
        au["result"] = round(m, 1)
        state = "in range" if lo <= m <= hi else "out of reach"
        notes.append(f"{i['plugin']} {key} tuned to {i['params'][key]}: {au['metric']} {m:.1f} "
                     f"(goal {lo}..{hi}, {state})")
    return notes


def master_loop(job, voice_wav, work):
    t = job["target"]
    metric = "rms" if "rms" in t else "lufs"
    goal = t[metric]
    raw = bounce(job, voice_wav, work, 0.0, None)  # chain only, no limiter: level and peak before the master
    gain = goal - level_of(raw, metric, work / "bounce.wav")
    ceiling = job["master"].get("ceiling", t["tp"] - 0.5)
    for it in range(1, 9):
        b = bounce(job, voice_wav, work, gain, ceiling)
        level = level_of(b, metric, work / "bounce.wav")
        if abs(level - goal) <= 0.3 and b["true_peak_db"] <= t["tp"]:
            break
        if b["true_peak_db"] > t["tp"]:
            ceiling -= b["true_peak_db"] - t["tp"] + 0.1
        gain += goal - level
    gain = float(np.clip(gain, -96, 24))
    return {"gain": round(gain, 2), "ceiling": round(ceiling, 2), "iterations": it,
            "limiting_db": round(raw["peak_db"] + gain - ceiling, 1)}


def deliver(job, bounce_wav, out):
    d = job["deliver"]
    name = f"{job['stem']}_{job['preset']}"
    x = decode(bounce_wav, 2)
    dual_mono = float(np.max(np.abs(x[:, 0] - x[:, 1]))) < 1e-4
    notes, af = [], []
    if d["channels"] == 1:
        if dual_mono:
            af.append("pan=mono|c0=c0")
        else:
            notes.append("kept stereo: the preset adds stereo width")
    files = []
    for fmt in d.get("formats", ["wav"]):
        if fmt == "wav":
            codec = ["-c:a", "pcm_s24le"] if d.get("bit_depth", 24) == 24 else ["-c:a", "pcm_s16le"]
            extra = [] if d.get("bit_depth", 24) == 24 else ["aresample=osf=s16:dither_method=triangular"]
        elif fmt == "mp3":
            codec, extra = ["-c:a", "libmp3lame", "-b:a", "320k"], []
        elif fmt == "m4a":
            codec, extra = ["-c:a", "aac", "-b:a", "256k"], []
        else:
            sys.exit(f"unknown format {fmt}")
        path = out / f"{name}.{fmt}"
        chain = af + extra
        run(["ffmpeg", "-y", "-v", "error", "-i", bounce_wav] + (["-af", ",".join(chain)] if chain else [])
            + codec + [path])
        files.append(path)
    return files, notes


def spectrogram(path, png):
    run(["ffmpeg", "-y", "-v", "error", "-i", path, "-lavfi",
         "showspectrumpic=s=1600x500:legend=1:color=intensity:scale=log", "-frames:v", "1", png])


def compare(files, out, gap=1.0, channels=None, lufs=None):
    """Concatenate files at matched loudness (attenuate only) so the louder one doesn't win."""
    ms = []
    for f in files:
        info = probe(f)
        ms.append((f, info, loudness(f, info["channels"])))
    ch = channels or max(i["channels"] for _, i, _ in ms)
    level = lufs if lufs is not None else min(L["lufs"] for *_, L in ms)
    for _, _, L in ms:  # never push a true peak past -1 dBTP
        level = min(level, L["lufs"] + (-1.0 - L["tp"])) if level > L["lufs"] else level
    inputs, parts = [], []
    for k, (f, info, L) in enumerate(ms):
        inputs += ["-i", f]
        if info["channels"] == ch:
            remix = ""
        elif ch == 1:
            remix = "pan=mono|c0=0.5*c0+0.5*c1,"
        else:
            remix = "pan=stereo|c0=c0|c1=c0,"
        pad = f",apad=pad_dur={gap}" if k < len(ms) - 1 else ""
        parts.append(f"[{k}:a]aresample={SR},{remix}volume={level - L['lufs']:.2f}dB{pad}[a{k}]")
    fc = ";".join(parts) + ";" + "".join(f"[a{k}]" for k in range(len(ms))) + f"concat=n={len(ms)}:v=0:a=1[out]"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[out]", "-c:a", "pcm_s24le", out])
    return level


def fmt_nf(a):
    if a.get("noise_floor") is None:
        return a.get("pauses", "-")
    return f"{a['noise_floor']:.0f} dBFS"


def write_report(job_dir, job, before, after, loop, files, notes, warnings):
    t = job["target"]
    metric_row = (("RMS", f"{before['rms_db']:.1f} dB", f"{after['rms_db']:.1f} dB", f"{t['rms']:.0f} ±1")
                  if "rms" in t else
                  ("Loudness", f"{before['lufs']:.1f} LUFS", f"{after['lufs']:.1f} LUFS", f"{t['lufs']:.0f} ±0.5"))
    rows = [metric_row,
            ("True peak", f"{before['tp']:.1f} dBTP", f"{after['tp']:.1f} dBTP", f"≤ {t['tp']}"),
            ("Loudness range", f"{before['lra']:.1f} LU", f"{after['lra']:.1f} LU", f"≤ {t['lra_max']:.0f}"),
            ("Noise floor", fmt_nf(before), fmt_nf(after), "≤ -60 dBFS" if job["dry"] else "n/a (mood)"),
            ("Sibilance", f"{before['sibilance']:+.1f} dB", f"{after['sibilance']:+.1f} dB", f"≤ {SIB_WARN:+.0f}"),
            ("Low bursts", f"{before['plosive']:+.1f} dB", f"{after['plosive']:+.1f} dB", f"≤ {PLOSIVE_WARN:+.0f}"),
            ("Phrase spread", f"±{before['phrase_spread']:.1f} dB", f"±{after['phrase_spread']:.1f} dB", f"≤ ±{PHRASE_WARN:.0f}"),
            ("Tilt", f"{before['tilt']:.1f} dB/oct", f"{after['tilt']:.1f} dB/oct", "info"),
            ("Bandwidth", f"{before['bandwidth'] / 1000:.1f} kHz", f"{after['bandwidth'] / 1000:.1f} kHz", "info"),
            ("Limiter depth", "-", f"{loop['limiting_db']:.1f} dB", f"≤ {LIMITER_WARN:.0f}")]
    checks = assess(after, t["name"], "output", job["dry"])
    if loop["limiting_db"] > LIMITER_WARN:
        checks.append(("warn", f"limiter pushes {loop['limiting_db']:.1f} dB: compress more before it, or aim lower"))
    verdict = "PASS" if not any(lvl == "fail" for lvl, _ in checks) else "FAIL"
    lines = [f"# {job['stem']} — {job['preset']} ({t['label']})", "", f"**{verdict}**", "",
             "| Check | Before | After | Target |", "|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
    lines += ["", "## Checks", ""] + [f"- {SYMBOL[lvl]} {text}" for lvl, text in checks]
    lines += ["", "## Chain", ""]
    pc = job["preclean"]
    repairs = [n for n, on in (("declip", pc.get("declip")), ("declick", pc.get("declick"))) if on]
    if pc.get("denoise"):
        repairs.append("denoise nr {nr} dB, floor {nf} dB".format(**pc["denoise"]))
    if pc.get("tail_s"):
        repairs.append(f"{pc['tail_s']} s tail pad at the end")
    if repairs:
        lines.append(f"0. ffmpeg: {', '.join(repairs)}")
    for n, i in enumerate(job["voice"], 1):
        lines.append(f"{n}. **{i['plugin']}** {json.dumps(i.get('params', {}))}" + (f" — {i['why']}" if i.get("why") else ""))
    if job.get("bed"):
        lines.append(f"- bed track: {', '.join(i['plugin'] for i in job['bed']['inserts'])}")
    lines.append(f"- master: gain {loop['gain']:+.2f} dB -> maximizer ceiling {loop['ceiling']} dB "
                 f"({loop['iterations']} loudness passes)")
    if notes or warnings:
        lines += ["", "## Notes", ""] + [f"- {n}" for n in notes + warnings]
    lines += ["", "## Files", ""] + [f"- {f}" for f in files]
    (job_dir / "report.md").write_text("\n".join(lines) + "\n")
    return verdict, checks


def render(job_dir):
    job_dir = Path(job_dir).resolve()
    job = json.loads((job_dir / "job.json").read_text())
    work, out = job_dir / "work", job_dir / "out"
    work.mkdir(exist_ok=True)
    out.mkdir(exist_ok=True)
    warnings = []
    specs = plugin_specs()
    validate(job["voice"], specs, warnings)
    if job.get("bed"):
        validate(job["bed"]["inserts"], specs, warnings)
    voice_wav = work / "voice.wav"
    preclean(job["input"], voice_wav, job["preclean"])
    tuned = tune(job, voice_wav, work)
    (job_dir / "job.json").write_text(json.dumps(job, indent=1, ensure_ascii=False))
    loop = master_loop(job, voice_wav, work)
    session = work / "session" / f"{job['stem']}_{job['preset']}.scraft"
    session.parent.mkdir(exist_ok=True)
    bounce(job, voice_wav, work, loop["gain"], loop["ceiling"], save=session)
    files, notes = deliver(job, work / "bounce.wav", out)
    main = files[0]
    ab = out / f"AB_{job['stem']}_{job['preset']}.wav"
    compare([job["input"], main], ab, channels=probe(main)["channels"])
    spectrogram(job["input"], out / "spectrogram_before.png")
    spectrogram(main, out / "spectrogram_after.png")
    before, after = analyse(job["input"]), analyse(main)
    (work / "analysis.json").write_text(json.dumps({"before": before, "after": after, "loop": loop}, indent=1))
    verdict, checks = write_report(job_dir, job, before, after, loop, files + [ab, session], tuned + notes, warnings)
    fix_owner(job_dir)
    print(f"{verdict}  {job['stem']} / {job['preset']}: {after['lufs']:.1f} LUFS, {after['tp']:.1f} dBTP, "
          f"LRA {after['lra']:.1f}, limiter {loop['limiting_db']:.1f} dB")
    for lvl, text in checks:
        if lvl in ("fail", "warn"):
            print(f"   {SYMBOL[lvl]} {text}")
    for w in warnings:
        print(f"   ! {w}")
    print(f"   report  {job_dir / 'report.md'}")
    print(f"   master  {main}")
    print(f"   A/B     {ab}")
    return main


# ---------------------------------------------------------------- commands

def cmd_analyze(args):
    ref = analyse(args.ref) if args.ref else None
    res = [analyse(f) for f in args.files]
    for a in res:
        print_report(a, args.target, ref)
    if args.json:
        Path(args.json).write_text(json.dumps({"files": res, "ref": ref}, indent=1))


def cmd_master(args):
    src = Path(args.file).resolve()
    stem = stem_of(src)
    root = Path(args.jobs).resolve() / stem
    (root / "in").mkdir(parents=True, exist_ok=True)
    if src.parent != root / "in":
        shutil.copy2(src, root / "in" / src.name)
        src = root / "in" / src.name
    a = analyse(src)
    ref = analyse(args.ref) if args.ref else None
    print_report(a, args.target, ref)
    if a.get("silent"):
        sys.exit("nothing to master: the file has no signal")
    masters = []
    names = [p.strip() for p in args.preset.split(",") if p.strip()]
    for name in names:
        job_dir = root / name
        job_dir.mkdir(exist_ok=True)
        job = plan(a, load_preset(name), args.target, ref, args.exact)
        (job_dir / "job.json").write_text(json.dumps(job, indent=1, ensure_ascii=False))
        print(f"\nplanned {job_dir / 'job.json'}")
        if not args.plan_only:
            masters.append(render(job_dir))
    if len(masters) > 1:
        listen = root / f"LISTEN_original-{'-'.join(names)}.wav"
        compare([src] + masters, listen, channels=probe(masters[0])["channels"])
        print(f"\nshootout {listen}  (order: original, {', '.join(names)}; 1 s gaps, loudness-matched)")
    fix_owner(root)


def cmd_render(args):
    render(args.job_dir)


def cmd_compare(args):
    level = compare(args.files, args.out, args.gap, lufs=args.lufs)
    print(f"{args.out}: {len(args.files)} files at {level:.1f} LUFS, {args.gap} s gaps, in this order:")
    for f in args.files:
        print(f"   {f}")


def cmd_spectrogram(args):
    spectrogram(args.file, args.out)
    print(args.out)


def cmd_presets(_):
    for p in sorted(PRESETS.glob("*.json")):
        d = json.loads(p.read_text())
        print(f"{d['name']:<11} {d.get('status', ''):<14} tail {d.get('tail_s', 0):>3}s  {d['summary']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("analyze")
    p.add_argument("files", nargs="+")
    p.add_argument("--target", default="tiktok", choices=TARGETS)
    p.add_argument("--ref")
    p.add_argument("--json")
    p.set_defaults(fn=cmd_analyze)
    p = sub.add_parser("master")
    p.add_argument("file")
    p.add_argument("--preset", default="studio")
    p.add_argument("--target", default="tiktok", choices=TARGETS)
    p.add_argument("--ref")
    p.add_argument("--exact", action="store_true", help="the preset's chain exactly as first tested")
    p.add_argument("--plan-only", action="store_true")
    p.add_argument("--jobs", default=str(HOME / "jobs"))
    p.set_defaults(fn=cmd_master)
    p = sub.add_parser("render")
    p.add_argument("job_dir")
    p.set_defaults(fn=cmd_render)
    p = sub.add_parser("compare")
    p.add_argument("files", nargs="+")
    p.add_argument("--out", required=True)
    p.add_argument("--gap", type=float, default=1.0)
    p.add_argument("--lufs", type=float)
    p.set_defaults(fn=cmd_compare)
    p = sub.add_parser("spectrogram")
    p.add_argument("file")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_spectrogram)
    sub.add_parser("presets").set_defaults(fn=cmd_presets)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
