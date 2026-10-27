"""One listen file from several takes, back to back at the same loudness, for the user's A/B.

  python3 listen.py OUT.wav A.wav B.wav [C.wav ...] [--max 15] [--gap 1.0]

Each input is cut to its first --max seconds (if given), set to -20 LUFS by plain gain (no compression, so the
comparison stays fair: louder always sounds better at first), and joined with --gap seconds of silence, mono 48 kHz.
Prints where each part starts, so the user can be told "original at 0:00, new at 0:17".
Typical uses: the reference then the clone's test (`--max 15` on the reference); a line's old take then its new one
(the pieces' raw files are listed in spans.json); several respellings of one word in context, the original first.
"""
import argparse
import re
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("inputs", nargs="+")
ap.add_argument("--max", type=float, default=0.0)
ap.add_argument("--gap", type=float, default=1.0)
a = ap.parse_args()


def lufs(path):
    trim = ["-t", str(a.max)] if a.max else []
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *trim, "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def seconds(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout
    return min(float(out), a.max) if a.max else float(out)


args, chains, labels, t = [], [], [], 0.0
for i, path in enumerate(a.inputs):
    args += ["-i", path]
    trim = f"atrim=0:{a.max}," if a.max else ""
    chains.append(f"[{i}:a]{trim}aformat=sample_fmts=fltp:channel_layouts=mono,aresample=48000,"
                  f"volume={-20 - lufs(path):.2f}dB,alimiter=limit=0.95:level=disabled[p{i}]")
    labels.append(f"[p{i}]")
    print(f"{int(t // 60)}:{t % 60:04.1f}  {path}")
    t += seconds(path) + a.gap
    if i < len(a.inputs) - 1:
        chains.append(f"anullsrc=r=48000:cl=mono,atrim=0:{a.gap}[s{i}]")
        labels.append(f"[s{i}]")
graph = ";".join(chains) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1[out]"
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args, "-filter_complex", graph, "-map", "[out]",
                "-c:a", "pcm_s16le", a.out], check=True)
print(f"wrote {a.out}")
