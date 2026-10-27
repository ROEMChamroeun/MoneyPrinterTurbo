"""Split a Demucs vocals stem into single-speaker reference clips, keeping all detected speech.

usage: chunk_voices.py VOCALS.wav NO_VOCALS.wav OUT_DIR

1. Silero VAD finds speech segments.
2. SpeechBrain ECAPA embeds each segment; agglomerative clustering groups speakers.
   Groups with >= MIN_SPEAKER_SEC and >= 2 segments become speakers (A, B, C... by speech time).
3. Unlabelled short lines next to a speaker's own lines are re-attached to that speaker.
4. Adjacent segments of the SAME speaker (gap <= MAX_GAP) merge into clips of MIN_DUR..MAX_DUR.
5. Speech that still has no speaker goes to "unsorted" clips so nothing detected is lost.
6. Each clip is cleaned (mono, 75 Hz high-pass, -20 LUFS, -1.5 dB peak) and written per speaker.
"""
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio
from sklearn.cluster import AgglomerativeClustering
from silero_vad import get_speech_timestamps, load_silero_vad

SR = 16000
MIN_SEG = 0.8          # shorter segments give unreliable speaker embeddings
MAX_GAP = 0.8          # merge same-speaker segments across pauses up to this long
MIN_DUR, MAX_DUR = 2.0, 15.0
UNSORTED_MIN = 1.0     # shortest unsorted clip worth keeping
PAD = 0.12             # seconds of room kept around a clip
CLUSTER_DIST = 0.55    # cosine distance threshold for "same speaker"
MIN_SPEAKER_SEC = 10.0
MIN_SPEAKER_SEGS = 2
MERGE_SIM = 0.65       # two speakers this alike are the same person (e.g. calm vs upset)
FILL_GAP = 0.7         # an unlabelled line this close to a speaker's line can join that speaker
FILL_SIM = 0.25        # ...if its voice is at least this similar to the speaker's centroid

vocals_path, backing_path, out_dir = map(Path, sys.argv[1:4])
out_dir.mkdir(parents=True, exist_ok=True)


def load_mono(path):
    data, sr = sf.read(str(path), always_2d=True)
    return data.mean(axis=1).astype(np.float32), sr


voc, sr_full = load_mono(vocals_path)
bak, _ = load_mono(backing_path)
wav16 = torchaudio.functional.resample(torch.from_numpy(voc), sr_full, SR)

vad = load_silero_vad()
stamps = get_speech_timestamps(
    wav16, vad, sampling_rate=SR, min_speech_duration_ms=300,
    min_silence_duration_ms=250, speech_pad_ms=60,
)
segs = [(s["start"] / SR, s["end"] / SR) for s in stamps]
speech_total = sum(e - s for s, e in segs)
print(f"VAD: {len(segs)} segments, {speech_total:.0f}s of speech")

from speechbrain.inference.speaker import EncoderClassifier  # noqa: E402

enc = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir=str(Path.home() / ".cache/voice-narrator/ecapa"),
    run_opts={"device": "cpu"},
)


def embed(a, b):
    chunk = wav16[int(a * SR):int(b * SR)].unsqueeze(0)
    with torch.no_grad():
        v = enc.encode_batch(chunk).squeeze().numpy()
    return v / np.linalg.norm(v)


emb = {}  # segment index -> embedding (every segment, even short ones, for the fill pass)
for i, (s, e) in enumerate(segs):
    emb[i] = embed(s, max(e, s + 0.4))
reliable = [i for i, (s, e) in enumerate(segs) if e - s >= MIN_SEG]

labels_raw = AgglomerativeClustering(
    n_clusters=None, distance_threshold=CLUSTER_DIST, metric="cosine", linkage="average",
).fit_predict(np.stack([emb[i] for i in reliable]))

stats = {}
for i, lab in zip(reliable, labels_raw):
    d, n = stats.get(lab, (0.0, 0))
    stats[lab] = (d + segs[i][1] - segs[i][0], n + 1)
ranked = sorted(stats, key=lambda l: stats[l][0], reverse=True)
names = {}
for lab in ranked:
    d, n = stats[lab]
    if d >= MIN_SPEAKER_SEC and n >= MIN_SPEAKER_SEGS:
        names[lab] = f"speaker_{chr(65 + len(names))}"
print("speakers (speech seconds):", {names[l]: round(stats[l][0]) for l in names})

seg_speaker = {i: names.get(lab) for i, lab in zip(reliable, labels_raw)}
cent = {}
for spk in names.values():
    v = np.mean([emb[i] for i, s in seg_speaker.items() if s == spk], axis=0)
    cent[spk] = v / np.linalg.norm(v)

# merge pass: near-identical voice prints are one person; the earlier (bigger) letter wins
again = True
while again:
    again = False
    keys = sorted(cent)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            sim_ab = float(cent[a] @ cent[b])
            if sim_ab >= MERGE_SIM:
                print(f"merging {b} into {a} (voice similarity {sim_ab:.2f})")
                for k, v in seg_speaker.items():
                    if v == b:
                        seg_speaker[k] = a
                vv = np.mean([emb[k] for k, v in seg_speaker.items() if v == a], axis=0)
                cent[a] = vv / np.linalg.norm(vv)
                del cent[b]
                again = True
                break
        if again:
            break

# fill pass: unlabelled line adjacent to a labelled one adopts that speaker if the voice fits
for _ in range(2):
    for i, (s, e) in enumerate(segs):
        if seg_speaker.get(i):
            continue
        cands = []
        for j in (i - 1, i + 1):
            if 0 <= j < len(segs) and seg_speaker.get(j):
                gap = (s - segs[j][1]) if j < i else (segs[j][0] - e)
                if gap <= FILL_GAP:
                    cands.append(seg_speaker[j])
        cands = [c for c in cands if float(emb[i] @ cent[c]) >= FILL_SIM]
        if cands:
            seg_speaker[i] = max(cands, key=lambda c: float(emb[i] @ cent[c]))
n_named = sum(1 for i in range(len(segs)) if seg_speaker.get(i))
print(f"{n_named} of {len(segs)} segments assigned to a speaker")

with open(out_dir / "segments.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["idx", "start", "end", "dur", "speaker"])
    for i, (s, e) in enumerate(segs):
        w.writerow([i, round(s, 2), round(e, 2), round(e - s, 2), seg_speaker.get(i) or "unsorted"])


def build_clips(label_of, min_dur):
    """Merge adjacent same-label segments into clips; label None segments are skipped."""
    clips, cur = [], None
    for i, (s, e) in enumerate(segs):
        spk = label_of(i)
        if spk is None:
            if cur:
                clips.append(cur)
                cur = None
            continue
        if cur and cur["spk"] == spk and s - cur["end"] <= MAX_GAP and e - cur["start"] <= MAX_DUR:
            cur["end"] = e
            cur["idx"].append(i)
        else:
            if cur:
                clips.append(cur)
            cur = {"spk": spk, "start": s, "end": e, "idx": [i]}
    if cur:
        clips.append(cur)
    return [c for c in clips if min_dur <= c["end"] - c["start"] <= MAX_DUR]


clips = build_clips(lambda i: seg_speaker.get(i), MIN_DUR)
used = {i for c in clips for i in c["idx"]}   # lines too short for a speaker clip still get kept
clips += build_clips(lambda i: None if i in used else "unsorted", UNSORTED_MIN)
covered = {i for c in clips for i in c["idx"]}
in_clips = sum(segs[i][1] - segs[i][0] for i in covered)   # speech seconds, pauses excluded
print(f"{len(clips)} clips; {in_clips:.0f}s of {speech_total:.0f}s detected speech covered")


def db(x):
    return 20 * np.log10(max(float(np.sqrt(np.mean(x ** 2))), 1e-6))


for c in clips:
    a, b = int(max(c["start"] - PAD, 0) * sr_full), int((c["end"] + PAD) * sr_full)
    c["seg"] = voc[a:b]
    c["clean_db"] = round(db(voc[a:b]) - db(bak[a:b]), 1)   # voice vs music/effects, same window

for spk in sorted({c["spk"] for c in clips}):
    (out_dir / spk).mkdir(exist_ok=True)

counters, rows = {}, []
for c in sorted(clips, key=lambda c: (c["spk"] == "unsorted", c["spk"], c["start"])):
    n = counters.get(c["spk"], 0) + 1
    counters[c["spk"]] = n
    name = f"{c['spk']}_{n:03d}_{int(c['start'] // 60):02d}m{int(c['start'] % 60):02d}s.wav"
    path = out_dir / c["spk"] / name
    tmp = path.with_suffix(".raw.wav")
    sf.write(str(tmp), c["seg"], sr_full, subtype="PCM_16")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-ac", "1",
         "-af", "highpass=f=75,loudnorm=I=-20:TP=-1.5:LRA=7", "-ar", "44100",
         "-c:a", "pcm_s16le", str(path)],
        check=True,
    )
    tmp.unlink()
    rows.append([f"{c['spk']}/{name}", c["spk"], round(c["start"], 2), round(c["end"], 2),
                 round(c["end"] - c["start"], 2), c["clean_db"]])

with open(out_dir / "manifest.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["file", "speaker", "start_s", "end_s", "duration_s", "voice_vs_music_dB"])
    w.writerows(rows)
print("done")
