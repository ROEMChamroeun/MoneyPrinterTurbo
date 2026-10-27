"""Narrate Khmer text with a VoiceStudio clone voice: VoxCPM2 on MLX on the Mac, one sentence per generation.

Run with VoiceStudio's runtime python (it has mlx-audio 0.5.0):
  VS="$HOME/Library/Application Support/VoiceStudio/runtime/project/.venv/bin/python"
  "$VS" narrate.py --profile doc-narrator-girl-002 --text text.txt --out DIR
      [--seed 7] [--reroll 5] [--reroll 9:31] [--tag v2] [--gaps 0.30 0.60 0.80] [--paragraph-gap 1.0]
      [--markers-only] [--force]

--profile takes a VoiceStudio id or name; "name_seed23" also sets the seed. The text is the user's Khmer, with
VoiceStudio's pause markers where they want them: [pause] = 350 ms, [pause 500ms], [pause 1s], a bare number = ms,
capped at 10 s, adjacent markers add up. khmer_text.prepare() makes the spoken text (joined ៗ repeats, re-encoded
vowels, no quote marks) and prints every change; digits, Latin letters or misordered vowels stop the run.

Pieces: one generation per sentence (up to ។ ? !) and per ellipsis (.. ... …); a sentence over 120 characters is
cut at one of the writer's own spaces near the middle, because long calls rush. The silence after each piece follows
the punctuation unless a marker says otherwise: no mark = phrase gap, ។ ? ! = sentence gap, ellipsis = trailing-off
gap (--gaps); a blank line makes it at least --paragraph-gap; the last piece gets none. --markers-only generates whole
marker-to-marker spans instead.

Every piece is continuation cloning (the profile's audio + its exact transcript), 10 steps, cfg 2.0, the seed reset
before each piece, so a piece depends only on (voice, text, seed). Pieces are cached in DIR/cache/, so a re-run
regenerates only pieces whose text changed. A piece the model cut off mid-sound (it ends loud instead of in silence,
about 1 in 5 short pieces) is re-rolled with seed+100, then seed+200. --reroll K[:SEED] regenerates piece K with
another seed (default seed+1000), keeps every other piece byte-identical, and names the file ..._rerollK so the
earlier take stays for an A/B. After a text fix, re-run into the same DIR with --tag v2 for the same reason.

Writes DIR/<voice>_seed<seed>[_rerollK].wav (48 kHz, -18 LUFS, -1.5 dBTP) with its <name>.report.md (pace of each
piece against the voice's own reference, re-rolls, cut-offs, timings), text_original.txt, text_spoken.txt, and
spans.json + report.md for the latest run (measure_take.py reads spans.json).
Refuses to start while another big VoxCPM2 process runs (VoiceStudio generating, another narrate.py): two copies
fill a 16 GB Mac's swap and both crawl. --force overrides that.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import wave

os.environ["HF_HUB_OFFLINE"] = "1"
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from khmer_text import prepare, problems  # noqa: E402

STEPS, CFG = 10, 2.0
TARGET_DB, MAX_GAIN_DB = -20.0, 10.0
MAX_CHARS = 120
FAST, SLOW = 0.20, -0.20                 # pace flags against the reference
STUDIO = os.path.expanduser("~/Library/Application Support/OmniVoice")
PAUSE_RE = re.compile(r"\[\s*pause(?>\s+(\d+(?:\.\d+)?)\s*(ms|s)?)?\s*\]", re.IGNORECASE)
ELLIPSIS_SPLIT = re.compile(r"(?:(?<=\.\.)(?!\.)|(?<=…))")
SENTENCE_END = ("។", "៕", "?", "!")


def pause_ms(num, unit):
    if num is None:
        return 350
    ms = float(num) * (1000.0 if unit and unit.lower() == "s" else 1.0)
    return max(0, min(int(round(ms)), 10_000))


def spans_of(text):
    spans, last = [], 0
    for m in PAUSE_RE.finditer(text):
        chunk = " ".join(text[last:m.start()].split())
        if chunk:
            spans.append([chunk, pause_ms(m.group(1), m.group(2))])
        elif spans:
            spans[-1][1] = min(spans[-1][1] + pause_ms(m.group(1), m.group(2)), 10_000)
        last = m.end()
    tail = " ".join(text[last:].split())
    if tail:
        spans.append([tail, 0])
    return spans


def balance_split(sentence, limit=MAX_CHARS):
    """A sentence over `limit` characters is cut at the writer's own spaces into parts of about 100 characters."""
    spaces = [i for i, c in enumerate(sentence) if c == " "]
    if len(sentence) <= limit or not spaces:
        return [sentence]
    n = -(-len(sentence) // 100)
    cuts = sorted({min(spaces, key=lambda s: abs(s - len(sentence) * k / n)) for k in range(1, n)})
    out, last = [], 0
    for c in cuts + [len(sentence)]:
        out.append(sentence[last:c].strip())
        last = c
    return [o for o in out if o]


def pieces_of(chunk):
    out = []
    for part in ELLIPSIS_SPLIT.split(chunk):
        for sentence in re.split(r"(?<=[។៕?!])(?![។៕?!])", part):
            if sentence.strip():
                out.extend(balance_split(sentence.strip()))
    return out


def spans_by_line(text, gaps, paragraph):
    """One generation per sentence or ellipsis. The silence after each follows the punctuation unless a [pause] says
    otherwise. A blank line makes the gap before it at least `paragraph`. A line that is only a marker adds its pause
    to the piece before. The last piece gets no trailing silence."""
    phrase, sentence, trail, para = (int(g * 1000) for g in (*gaps, paragraph))
    spans, defaulted = [], False
    for line in text.splitlines():
        parts = spans_of(line)
        if not parts:
            marks = [pause_ms(m.group(1), m.group(2)) for m in PAUSE_RE.finditer(line)]
            if spans and marks:
                spans[-1][1] += sum(marks)
                defaulted = False
            elif spans and not line.strip() and defaulted:
                spans[-1][1] = max(spans[-1][1], para)
            continue
        for k, (chunk, pause) in enumerate(parts):
            pieces = pieces_of(chunk)
            for j, piece in enumerate(pieces):
                if j == len(pieces) - 1 and not (k == len(parts) - 1 and pause == 0):
                    spans.append([piece, pause])          # the writer's own [pause]
                    defaulted = False
                else:
                    end = piece.rstrip()
                    spans.append([piece, sentence if end.endswith(SENTENCE_END)
                                  else trail if end.endswith(("..", "…")) else phrase])
                    defaulted = True
    if spans and defaulted:
        spans[-1][1] = 0
    return spans


def frames_db(x, sr, frame=0.025, hop=0.01):
    f, h = int(frame * sr), int(hop * sr)
    if len(x) < f:
        return np.array([-120.0])
    idx = np.arange(0, len(x) - f, h)
    return 20 * np.log10(np.array([np.sqrt(np.mean(x[i:i + f] ** 2)) for i in idx]) + 1e-9)


def speech_seconds(x, sr):
    db = frames_db(x, sr)
    return float((db > db.max() - 35).sum() * 0.01)


def chars(text):
    return len(re.sub(r"[\s។៕៖,.!?\"'«»“”()\-–—ៗ…​]", "", PAUSE_RE.sub("", text)))


def trim(x, sr):
    """Edges cut 55 dB under the peak, 30 ms lead-in and 80 ms tail kept, a 30 ms fade so the natural fade-out stays."""
    fr = int(0.01 * sr)
    db = 20 * np.log10(np.array([np.sqrt(np.mean(x[i:i + fr] ** 2)) for i in range(0, len(x) - fr, fr)]) + 1e-9)
    on = np.where(db > db.max() - 55)[0]
    if not len(on):
        return x
    a, b = max(on[0] * fr - int(0.03 * sr), 0), min((on[-1] + 1) * fr + int(0.08 * sr), len(x))
    y = x[a:b].copy()
    n = int(0.03 * sr)
    y[-n:] *= np.linspace(1, 0, n) ** 2
    return y


def level(x, sr):
    fr = int(0.02 * sr)
    rms = np.array([np.sqrt(np.mean(x[i:i + fr] ** 2)) for i in range(0, len(x) - fr, fr)])
    act = rms[20 * np.log10(rms + 1e-9) > 20 * np.log10(rms.max() + 1e-9) - 35]
    gain = TARGET_DB - 20 * np.log10(np.sqrt(np.mean(act ** 2)) + 1e-9)
    return x * 10 ** (np.clip(gain, -MAX_GAIN_DB, MAX_GAIN_DB) / 20)


def stopped(x, sr):
    """True when the model ended the clip while still loud (cut off mid-sound); a finished line ends in silence."""
    fr = int(0.01 * sr)
    db = 20 * np.log10(np.array([np.sqrt(np.mean(x[i:i + fr] ** 2)) for i in range(0, len(x) - fr, fr)]) + 1e-9)
    loud = np.percentile(db[db > db.max() - 40], 95)
    return bool(db[-3:].max() - loud > -35)


def write(path, x, sr):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def read(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def busy_models():
    """Other processes holding a big model: a second VoxCPM2 on this 16 GB Mac fills swap and both crawl."""
    mine = {os.getpid(), os.getppid()}
    out = subprocess.run(["ps", "-axo", "pid=,rss=,command="], capture_output=True, text=True).stdout
    hits = []
    for line in out.splitlines():
        pid, rss, cmd = line.strip().split(None, 2)
        if int(pid) not in mine and int(rss) > 1_500_000 and re.search(
                r"VoiceStudio|OmniVoice|voxcpm|mlx_audio|narrate\.py", cmd, re.IGNORECASE):
            hits.append(f"pid {pid}, {int(rss) / 1e6:.1f} GB: {cmd[:100]}")
    return hits


def find_profile(name):
    con = sqlite3.connect(f"file:{STUDIO}/omnivoice.db?mode=ro", uri=True)
    rows = con.execute("select id, name, ref_audio_path, ref_text from voice_profiles").fetchall()
    for r in rows:
        if name in (r[0], r[1]):
            return r
    near = [r for r in rows if name.lower() in r[1].lower()]
    if len(near) == 1:
        return near[0]
    listing = "\n".join(f"  {r[0]}  {r[1]}" for r in rows)
    raise SystemExit(f"No single VoiceStudio voice matches {name!r}. Voices:\n{listing}")


ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
ap.add_argument("--profile", required=True)
ap.add_argument("--text", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--seed", type=int)
ap.add_argument("--reroll", action="append", default=[], metavar="K[:SEED]")
ap.add_argument("--tag", default="", help="suffix for the output name, e.g. v2 after a text fix, so the old take stays")
ap.add_argument("--markers-only", action="store_true")
ap.add_argument("--gaps", type=float, nargs=3, default=[0.30, 0.60, 0.80], metavar=("PHRASE", "SENTENCE", "TRAIL"))
ap.add_argument("--paragraph-gap", type=float, default=1.0)
ap.add_argument("--force", action="store_true")
ap.add_argument("--plan", action="store_true", help="print the pieces, gaps and an estimate, generate nothing")
a = ap.parse_args()

profile = a.profile
m = re.fullmatch(r"(.+)_seed(\d+)", profile)
if m and a.seed is None:
    profile, a.seed = m.group(1), int(m.group(2))
seed = 7 if a.seed is None else a.seed
pid, vname, ref_file, ref_text = find_profile(profile)
if not (ref_text or "").strip():
    raise SystemExit(f"{vname} has no transcript. Continuation cloning needs the exact Khmer text of its clip: "
                     "ask the user for it, then set it with voices.py set-text.")
ref = os.path.join(STUDIO, "voices", ref_file)

raw_text = open(a.text, encoding="utf-8").read()
spoken, changes = prepare(raw_text)
bad = problems(spoken)
if bad:
    raise SystemExit("The text needs a fix before the voice reads it:\n  " + "\n  ".join(bad))
spans = spans_of(spoken) if a.markers_only else spans_by_line(spoken, a.gaps, a.paragraph_gap)
rerolls = {}
for r in a.reroll:
    k, _, s = r.partition(":")
    if not 1 <= int(k) <= len(spans):
        raise SystemExit(f"--reroll {r}: there are pieces 1..{len(spans)}")
    rerolls[int(k)] = int(s) if s else seed + 1000

print(f"voice: {vname} ({pid}) | seed {seed} | {len(spans)} pieces", flush=True)
for c in changes:
    print(f"spoken text: {c}", flush=True)
for k, (s, p) in enumerate(spans, 1):
    print(f"  {k:2d}. {s}   + {p} ms" + (f"   [re-roll, seed {rerolls[k]}]" if k in rerolls else ""), flush=True)

if a.plan:
    rx, rsr = sf.read(ref, dtype="float32")
    pace = chars(ref_text) / speech_seconds(rx.mean(1) if rx.ndim > 1 else rx, rsr)
    speech = sum(chars(s) for s, _ in spans) / pace
    total = speech + sum(p for _, p in spans) / 1000
    lo, hi = 4 * speech + 10, 15 * speech + 10                      # + model load
    span = f"{lo:.0f}-{hi:.0f} s" if hi < 180 else f"{lo / 60:.0f}-{hi / 60:.0f} min"
    print(f"about {total:.0f} s of audio ({speech:.0f} s speech at the reference's {pace:.1f} chars/s); generation "
          f"about {span} (4x real time on a quiet Mac, 15x when it swaps)")
    sys.exit(0)

os.makedirs(f"{a.out}/cache", exist_ok=True)
with open(f"{a.out}/text_original.txt", "w", encoding="utf-8") as f:
    f.write(raw_text)
with open(f"{a.out}/text_spoken.txt", "w", encoding="utf-8") as f:
    f.write(spoken)

voice_key = hashlib.sha1(open(ref, "rb").read() + ref_text.encode()).hexdigest()


def cache_key(text, s):
    return hashlib.sha1(f"{voice_key}|{STEPS}|{CFG}|{s}|{text}".encode()).hexdigest()[:16]


todo = [k for k, (s, _) in enumerate(spans, 1) if not os.path.exists(
    f"{a.out}/cache/{cache_key(s, rerolls.get(k, seed))}.wav")]
model = None
if todo:
    busy = busy_models()
    if busy and not a.force:
        raise SystemExit("Another big voice model is running; generating now would fill the Mac's swap:\n  "
                         + "\n  ".join(busy) + "\nAsk the user whether to wait (or pass --force).")
    swap = re.search(r"used = ([\d.]+)M", subprocess.run(["sysctl", "vm.swapusage"], capture_output=True,
                                                         text=True).stdout)
    if swap and float(swap.group(1)) > 6000:
        print(f"note: the Mac already has {float(swap.group(1)) / 1000:.1f} GB in swap, so expect about 15x real time "
              "instead of 4x (2026-10-24: the UTM VM's QEMU held an 18 GB footprint)", flush=True)
    import mlx.core as mx
    from mlx_audio.tts.utils import load
    import mlx_audio.tts.models.voxcpm2 as _voxcpm2_pkg

    # the two local patches mlx-audio 0.5.0 needs for VoxCPM2
    _orig_from_dict = _voxcpm2_pkg.ModelConfig.from_dict.__func__

    def _from_dict_keep_path(cls, config):
        cfg = _orig_from_dict(cls, config)
        cfg.model_path = config.get("model_path")
        return cfg

    def _post_load_hook(cls, model, model_path):
        from transformers import AutoTokenizer
        if model.tokenizer is None:
            model.tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
        return model

    _voxcpm2_pkg.ModelConfig.from_dict = classmethod(_from_dict_keep_path)
    _voxcpm2_pkg.Model.post_load_hook = classmethod(_post_load_hook)
    t0 = time.time()
    model = load("openbmb/VoxCPM2")
    print(f"model loaded in {time.time() - t0:.1f}s; {len(todo)} of {len(spans)} pieces to generate", flush=True)
    kw = dict(ref_audio=ref, prompt_audio=ref, prompt_text=ref_text)
sr = 48000

rx, rsr = sf.read(ref, dtype="float32")
rx = rx.mean(1) if rx.ndim > 1 else rx
ref_pace = chars(ref_text) / speech_seconds(rx, rsr)

parts, rows, t_all = [], [], time.time()
for k, (text, pause) in enumerate(spans, 1):
    base = rerolls.get(k, seed)
    key = cache_key(text, base)
    wav, meta_p = f"{a.out}/cache/{key}.wav", f"{a.out}/cache/{key}.json"
    if os.path.exists(wav):
        audio, meta = read(wav), json.load(open(meta_p))
    else:
        t = time.time()
        for attempt, s in enumerate((base, base + 100, base + 200)):
            mx.random.seed(s)
            audio = np.concatenate([np.array(r.audio, dtype=np.float32).reshape(-1)
                                    for r in model.generate(text=text, inference_timesteps=STEPS, cfg_value=CFG, **kw)])
            if not stopped(audio, sr):
                break
            print(f"piece {k}: the model cut it off (seed {s}); {'trying again' if attempt < 2 else 'keeping it'}",
                  flush=True)
        meta = {"text": text, "seed": base, "used_seed": s, "attempts": attempt + 1, "cut_off": stopped(audio, sr),
                "gen_s": round(time.time() - t, 1)}
        write(wav, audio, sr)
        json.dump(meta, open(meta_p, "w"), ensure_ascii=False)
        print(f"piece {k}/{len(spans)}: {len(audio) / sr:4.1f}s audio in {meta['gen_s']:5.1f}s", flush=True)
    clip = trim(audio, sr)
    sp = speech_seconds(clip, sr)
    pace = chars(text) / sp if sp else 0.0
    rel = pace / ref_pace - 1
    flags = (["CUT-OFF"] if meta["cut_off"] else []) + ([f"re-rolled x{meta['attempts'] - 1}"]
                                                         if meta["attempts"] > 1 else [])
    flags += ["fast"] if rel > FAST else ["slow"] if rel < SLOW else []
    rows.append({"piece": k, "text": text, "pause_ms": pause, "file": f"cache/{key}.wav", "seed": meta["used_seed"],
                 "audio_s": round(len(clip) / sr, 2), "chars_per_s": round(pace, 1), "vs_ref": round(rel, 3),
                 "flags": flags, "gen_s": meta["gen_s"]})
    parts.append(level(clip, sr))
    if pause:
        parts.append(np.zeros(int(sr * pause / 1000), np.float32))

name = (f"{vname}_seed{seed}" + ("_reroll" + "-".join(map(str, sorted(rerolls))) if rerolls else "")
        + (f"_{a.tag}" if a.tag else ""))
raw = f"{a.out}/{name}_raw.wav"
write(raw, np.concatenate(parts), sr)
final = f"{a.out}/{name}.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "loudnorm=I=-18:TP=-1.5:LRA=9",
                "-ar", str(sr), "-c:a", "pcm_s16le", final], check=True)
os.remove(raw)
dur = sf.info(final).duration
gen = sum(r["gen_s"] for r in rows if r["piece"] in todo)

json.dump({"voice": vname, "voice_id": pid, "seed": seed, "rerolls": rerolls, "ref_chars_per_s": round(ref_pace, 1),
           "output": os.path.basename(final), "spoken_changes": changes, "pieces": rows},
          open(f"{a.out}/spans.json", "w"), ensure_ascii=False, indent=1)
made = ("All pieces came from the cache." if not todo else
        f"Generated {len(todo)} piece{'s' * (len(todo) != 1)} in {gen:.0f} s"
        + (f" ({gen / dur:.1f}x real time)." if len(todo) == len(spans) else "; the rest came from the cache."))
lines = [f"# {name}", "",
         f"Voice {vname} ({pid}), seed {seed}. {len(spans)} pieces, {dur:.1f} s. {made}",
         f"Reference pace {ref_pace:.1f} chars/s (speech seconds, no spaces or punctuation). "
         f"Flags: fast/slow = more than 20% off it, CUT-OFF = the model stopped mid-sound after 3 tries.", ""]
if changes:
    lines += ["Spoken text differs from the user's: " + "; ".join(changes), ""]
lines += ["| # | chars/s | vs ref | gap after | seed | flags | text |", "|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['piece']} | {r['chars_per_s']} | {r['vs_ref']:+.0%} | {r['pause_ms']} ms | {r['seed']} | "
                 f"{', '.join(r['flags'])} | {r['text']} |")
for path in (f"{a.out}/report.md", f"{a.out}/{name}.report.md"):    # latest run, and one beside each take
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines[2:]), flush=True)
print(f"\nDONE {final}", flush=True)
if model is not None:
    print(f"peak memory {mx.get_peak_memory() / 1e9:.1f} GB", flush=True)
