"""The final edit in FilmCraft on the VM: picture + narration + sound design -> TikTok MP4, pulled back to out/.

  python3 vm_edit.py            new project, 1080x1920 30 fps sequence, import, place, mix, export, pull
Picture: out/short_picture.mov on the VM (EffectCraft ProRes render, vm_build.py render).
Audio: narration_full.wav (timeline.py) on A1 at 0 dB, sfx.wav (tools/sfx.py) on A2 at SFX_DB.
Export: H.264 1080x1920 30 fps, 16 Mbps 2-pass VBR, AAC, whole mix normalised to -14 LUFS (TikTok's level).
"""
from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
VM = "ubuntu-vm"
REMOTE = "/home/ubuntu/money-printer/short-01-river"
PROJ = f"{REMOTE}/vm/short_edit.fcproj"
OUT = f"{REMOTE}/out/short-01-river_tiktok.mp4"
SFX_DB = 3.0


def ssh(cmd: str) -> str:
    r = subprocess.run(["ssh", VM, cmd], text=True, capture_output=True)
    if r.returncode:
        print(r.stdout[-4000:], r.stderr[-4000:])
        raise SystemExit(f"failed: {cmd[:160]}")
    return r.stdout


def fc(args: str, project: bool = True, save: bool = True) -> str:
    pre = f"filmcraft-cli --compact --project {PROJ}" + (" --save" if save else "") if project else "filmcraft-cli --compact"
    return ssh(f"cd {REMOTE}/vm && {pre} {args}")


def j(obj: dict) -> str:
    return shlex.quote(json.dumps(obj))


def main() -> None:
    subprocess.run(f"rsync -a {HERE}/narration_full.wav {HERE}/sfx.wav {VM}:{REMOTE}/out/", shell=True, check=True)
    ssh(f"rm -f {PROJ}")
    print(fc(f"--save-as {PROJ} exec file.newSequence " + j({
        "name": "River short", "width": 1080, "height": 1920, "fps": 30, "sampleRate": 48000,
        "video": 2, "audio": 3, "mix": "Stereo"}), project=False, save=False)[:300])
    imp = json.loads(fc("exec file.import " + j({"paths": [f"{REMOTE}/out/short_picture.mov",
                                                          f"{REMOTE}/out/narration_full.wav", f"{REMOTE}/out/sfx.wav"]})))
    if imp.get("errors"):
        raise SystemExit(f"import errors: {imp['errors']}")
    ids = dict(zip(["pic", "nar", "sfx"], imp["items"]))          # items come back in the order of `paths`
    print("items:", ids)
    lines = [
        {"id": "timeline.place", "params": {"item": ids["pic"], "track": "V1", "seconds": 0, "audio": False}},
        {"id": "timeline.place", "params": {"item": ids["nar"], "track": "A1", "seconds": 0, "video": False}},
        {"id": "timeline.place", "params": {"item": ids["sfx"], "track": "A2", "seconds": 0, "video": False}},
        {"id": "timeline.setTrack", "params": {"track": "A1", "name": "Narration", "volumeDb": 0}},
        {"id": "timeline.setTrack", "params": {"track": "A2", "name": "Sound design", "volumeDb": SFX_DB}},
    ]
    (HERE / "vm/edit.jsonl").write_text("\n".join(json.dumps(l) for l in lines) + "\n")
    subprocess.run(f"rsync -a {HERE}/vm/edit.jsonl {VM}:{REMOTE}/vm/", shell=True, check=True)
    print(fc(f"run {REMOTE}/vm/edit.jsonl")[-600:])
    seq = json.loads(fc("inspect sequence", save=False))
    print("sequence:", json.dumps(seq)[:700])
    print(fc("exec file.exportMedia " + j({
        "path": OUT, "format": "h264", "width": 1080, "height": 1920, "fps": 30, "bitrateKbps": 16000,
        "bitrateMode": "vbr2Pass", "audioCodec": "aac", "loudnessLufs": -14, "range": "entire", "wait": True}),
        save=False)[-600:])
    (HERE / "out").mkdir(exist_ok=True)
    subprocess.run(f"rsync -a {VM}:{OUT} {HERE}/out/", shell=True, check=True)
    print("pulled", Path(OUT).name)


if __name__ == "__main__":
    main()
