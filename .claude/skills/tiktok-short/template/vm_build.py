"""Drive the EffectCraft build on the Ubuntu VM (ssh ubuntu-vm) from the Mac.

  python3 vm_build.py build                 build_jsx.py -> push -> run the JSX -> bold every text layer -> save
  python3 vm_build.py stills 1.2 5 12.5     render those times (half size) and pull them to out/stills/
  python3 vm_build.py render                full-quality render of comp "Short" -> out/short_picture.mov (ProRes)
The VM project is /home/ubuntu/money-printer/short-01-river/vm/short.ecproj.
"""
from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VM = "ubuntu-vm"
REMOTE = "/home/ubuntu/money-printer/short-01-river"
PROJ = f"{REMOTE}/vm/short.ecproj"


def sh(cmd: str, **kw) -> str:
    r = subprocess.run(cmd, shell=True, text=True, capture_output=True, **kw)
    if r.returncode:
        print(r.stdout[-3000:], r.stderr[-3000:])
        raise SystemExit(f"failed: {cmd[:200]}")
    return r.stdout


def ssh(cmd: str) -> str:
    return sh(f"ssh {VM} {shlex.quote(cmd)}")


def build() -> None:
    print(sh(f"python3 {HERE}/build_jsx.py").splitlines()[0])
    sh(f"rsync -a {HERE}/assets/ {VM}:{REMOTE}/assets/ && rsync -a {HERE}/vm/ {VM}:{REMOTE}/vm/")
    out = ssh(f"cd {REMOTE}/vm && rm -f short.ecproj && effectcraft-cli --empty --save-as {PROJ} script short.jsx")
    m = re.search(r"TEXT_LAYERS=(\[.*\])", out)
    print("\n".join(l for l in out.splitlines() if not l.startswith("TEXT_LAYERS=")))
    layers = json.loads(m.group(1))
    # weight axis: the variable font only offers its default (400) unless an animator offsets wght
    args = ["comp.open", json.dumps({"comp": "Short"})]
    for t in layers:
        args += ["text.animatorFontAxes", json.dumps({"layer": t["id"], "axis": "wght"}),
                 "prop.set", json.dumps({"layer": t["id"], "path": "text/animators/animator/properties/axis_wght",
                                          "value": t["w"]})]
    script = "effectcraft-cli --project " + PROJ + " --save run " + " ".join(shlex.quote(a) for a in args) + "\n"
    (HERE / "vm/bold.sh").write_text(script)
    sh(f"rsync -a {HERE}/vm/bold.sh {VM}:{REMOTE}/vm/bold.sh")
    ssh(f"bash {REMOTE}/vm/bold.sh > {REMOTE}/vm/bold.log 2>&1; tail -c 300 {REMOTE}/vm/bold.log")
    print(f"bold: {len(layers)} text layers")


def stills(times: list[str]) -> None:
    (HERE / "out/stills").mkdir(parents=True, exist_ok=True)
    cmds = " && ".join(f"effectcraft-cli --project {PROJ} render-frame --comp Short --time {t} --scale 0.5 "
                       f"--out {REMOTE}/out/stills/t{float(t):06.2f}.png" for t in times)
    ssh(f"mkdir -p {REMOTE}/out/stills && {cmds}")
    sh(f"rsync -a {VM}:{REMOTE}/out/stills/ {HERE}/out/stills/")
    print("pulled", len(times), "stills to out/stills/")


def render() -> None:
    (HERE / "out").mkdir(exist_ok=True)
    ssh(f"mkdir -p {REMOTE}/out && cd {REMOTE}/out && effectcraft-cli --project {PROJ} render --comp Short "
        f"--out {REMOTE}/out/short_picture.mov --format prores --prores hq --quality best --audio off "
        f"> render.log 2>&1; tail -3 render.log")
    sh(f"rsync -a {VM}:{REMOTE}/out/short_picture.mov {HERE}/out/")
    print("pulled out/short_picture.mov")


if __name__ == "__main__":
    {"build": lambda: build(), "stills": lambda: stills(sys.argv[2:]), "render": lambda: render()}[sys.argv[1]]()
