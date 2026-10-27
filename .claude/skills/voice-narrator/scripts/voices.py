"""VoiceStudio voice profiles on the Mac: list them, show one, create one, fix a transcript.

  python3 voices.py list
  python3 voices.py show doc-narrator-girl-002
  python3 voices.py create --name doc-narrator-girl-003 --audio picks/ref.wav --text picks/ref.txt [--language Khmer]
  python3 voices.py set-text e6b0acc9 --text picks/ref.txt

list/show read VoiceStudio's database directly (read-only). create and set-text go through VoiceStudio's own API on
port 3900: if nothing listens there, the backend is started headless for the call and stopped afterwards (the app
itself quits right after `open -a` when launched from a script). After the call the profile is read back and checked:
the stored audio must be byte-identical to the file given and ref_text equal to the transcript. A profile created
with an empty transcript gets a gibberish auto-transcript, so create refuses an empty --text.
Names in the database can change: the user renames voices in the app (khmer-voice-artist is now
reader-voice-girl-001), so record and pass ids.
"""
import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request
import wave

STUDIO = os.path.expanduser("~/Library/Application Support/OmniVoice")
BACKEND = os.path.expanduser("~/Library/Application Support/VoiceStudio/runtime/project/backend")
API = "http://127.0.0.1:3900"


def rows():
    con = sqlite3.connect(f"file:{STUDIO}/omnivoice.db?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return [dict(r) for r in con.execute("select * from voice_profiles order by created_at")]


def find(key):
    hits = [r for r in rows() if key in (r["id"], r["name"])]
    if not hits:
        raise SystemExit(f"No voice {key!r}. Run: voices.py list")
    return hits[0]


def seconds(path):
    try:
        with wave.open(path) as w:
            return w.getnframes() / w.getframerate()
    except (wave.Error, OSError, EOFError):
        return float("nan")


def up():
    try:
        urllib.request.urlopen(f"{API}/profiles", timeout=3).read()
        return True
    except OSError:
        return False


def backend():
    """Start the headless backend unless something already serves the API. Returns the process to stop, or None."""
    if up():
        return None
    log = open(os.path.join(os.path.dirname(STUDIO), "voice-narrator-backend.log"), "w")
    p = subprocess.Popen(["../.venv/bin/python", "main.py"], cwd=BACKEND, stdout=log, stderr=subprocess.STDOUT,
                         env={**os.environ, "HF_HUB_OFFLINE": "1", "OMNIVOICE_PORT": "3900"})
    for _ in range(90):
        if up():
            return p
        if p.poll() is not None:
            raise SystemExit(f"VoiceStudio backend exited; see {log.name}")
        time.sleep(1)
    p.terminate()
    raise SystemExit("VoiceStudio backend did not answer on port 3900 within 90 s")


def verify(pid, audio, text):
    r = find(pid)
    same_text = (r["ref_text"] or "").strip() == text.strip()
    stored = os.path.join(STUDIO, "voices", r["ref_audio_path"])
    same_audio = audio is None or hashlib.sha1(open(stored, "rb").read()).digest() == \
        hashlib.sha1(open(audio, "rb").read()).digest()
    print(f"{r['name']} ({r['id']}): transcript {'equal' if same_text else 'DIFFERENT'}, "
          f"stored audio {'byte-identical' if same_audio else 'DIFFERENT'} ({stored})")
    return same_text and same_audio


ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
sub = ap.add_subparsers(dest="cmd", required=True)
sub.add_parser("list")
s = sub.add_parser("show")
s.add_argument("voice")
c = sub.add_parser("create")
c.add_argument("--name", required=True)
c.add_argument("--audio", required=True)
c.add_argument("--text", required=True, help="file with the exact transcript")
c.add_argument("--language", default="Khmer")
t = sub.add_parser("set-text")
t.add_argument("voice")
t.add_argument("--text", required=True)
a = ap.parse_args()

if a.cmd == "list":
    print(f"{'id':9s} {'name':30s} {'language':9s} {'ref s':>6s} {'transcript':>10s}")
    for r in rows():
        n = len((r["ref_text"] or "").strip())
        print(f"{r['id']:9s} {r['name']:30s} {r['language']:9s} "
              f"{seconds(os.path.join(STUDIO, 'voices', r['ref_audio_path'] or '')):6.1f} "
              f"{(str(n) + ' chars') if n else 'NONE':>10s}")
elif a.cmd == "show":
    r = find(a.voice)
    path = os.path.join(STUDIO, "voices", r["ref_audio_path"])
    print(json.dumps({k: r[k] for k in ("id", "name", "language", "kind", "ref_audio_path")}, ensure_ascii=False))
    print(f"audio: {path} ({seconds(path):.2f} s)")
    print(f"transcript ({len(r['ref_text'] or '')} chars):\n{r['ref_text']}")
else:
    text = open(a.text, encoding="utf-8").read().strip()
    if not text:
        raise SystemExit("The transcript file is empty; get the exact Khmer text from the user first.")
    proc = backend()
    try:
        if a.cmd == "create":
            if any(r["name"] == a.name for r in rows()):
                raise SystemExit(f"A voice called {a.name} already exists; pick the next number or a -vN suffix.")
            out = subprocess.run(["curl", "-sS", "-f", "-X", "POST", f"{API}/profiles",
                                  "--form-string", f"name={a.name}", "-F", f"ref_audio=@{a.audio};type=audio/wav",
                                  "--form-string", f"ref_text={text}", "--form-string", f"language={a.language}",
                                  "--form-string", "kind=clone"],
                                 capture_output=True, text=True)
            if out.returncode:
                raise SystemExit(f"create failed: {out.stderr or out.stdout}")
            pid = json.loads(out.stdout)["id"]
            ok = verify(pid, a.audio, text)
        else:
            pid = find(a.voice)["id"]
            req = urllib.request.Request(f"{API}/profiles/{pid}", method="PUT",
                                         data=json.dumps({"ref_text": text}).encode(),
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=30).read()
            ok = verify(pid, None, text)
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=20)
    sys.exit(0 if ok else 1)
