"""Spoken Khmer for the clone: what the voice should read, and what must never reach it.

The user's text stays as written (it is the caption and the record); only the text sent to VoxCPM2 changes, and
every change is listed so it can be disclosed. Each rule comes from something the user heard:
- ៗ is spoken as the whole word twice, JOINED (នីមួយៗ -> នីមួយនីមួយ). A space between the copies made the voice read
  two disconnected words (2026-10-07). Word boundaries come from ICU (Node's Intl.Segmenter), the only Khmer word
  breaker on this Mac.
- Vowels typed as two signs (េ + ី for ើ, េ + ា for ោ) are re-encoded; other vowel signs with no consonant before
  them (ថ្ងៃេនះ) are reported, not guessed.
- « » “ ” and zero-width spaces are dropped. The colon ៖ becomes ។ because the clone pauses at a full stop, not a colon.
- Digits and Latin letters stop the run: numbers are written as Khmer words, foreign names as Khmer speakers say them.
- PRON holds respellings the user's ear has approved. It is empty: the one word tried (អារម្មណ៍, 2026-10-20) was read
  right once a stray space after it was removed, so check spacing before reaching for a respelling.
VoiceStudio's [pause ...] markers pass through untouched.

  python3 khmer_text.py text.txt        # prints the spoken text, each change, and any problems
"""
from __future__ import annotations

import functools
import json
import re
import subprocess
import sys

PRON: dict[str, str] = {}

# compounds the ICU word breaker splits wrongly (នី+មួយ+ៗ): spoken form, joined
REPEATS: dict[str, str] = {"នីមួយៗ": "នីមួយនីមួយ"}

VOWEL_FIXES = {"េី": "ើ", "េា": "ោ", "ំុ": "ុំ", "ំា": "ាំ"}
DROP = {"«": "", "»": "", "“": "", "”": "", '"': "", "​": ""}

MARKER = re.compile(r"\[\s*pause[^\]]*\]", re.IGNORECASE)
DEP_VOWEL = "ា-ៅ"
_NODE = (
    "const t=JSON.parse(require('fs').readFileSync(0,'utf8'));"
    "const s=new Intl.Segmenter('km',{granularity:'word'});"
    "process.stdout.write(JSON.stringify([...s.segment(t)].map(x=>x.segment)))"
)


@functools.lru_cache(maxsize=None)
def segments(text: str) -> tuple[str, ...]:
    out = subprocess.run(["node", "-e", _NODE], input=json.dumps(text), capture_output=True, text=True,
                         check=True).stdout
    return tuple(json.loads(out))


def expand_repeats(text: str) -> str:
    for word, spoken in REPEATS.items():
        text = text.replace(word, spoken)
    if "ៗ" not in text:
        return text
    out: list[str] = []
    for seg in segments(text):
        if seg == "ៗ":
            while out and not out[-1].strip():      # "ទៅ ៗ": the mark belongs to the word before the space
                out.pop()
            if out:
                out[-1] = out[-1] * 2
            continue
        if seg.endswith("ៗ") and len(seg) > 1:
            seg = seg[:-1].rstrip() * 2
        out.append(seg)
    return "".join(out)


def prepare(text: str) -> tuple[str, list[str]]:
    """The user's text -> the spoken text, plus a plain list of what changed."""
    changes: list[str] = []
    t = text
    for src, dst in {**DROP, **VOWEL_FIXES}.items():
        n = t.count(src)
        if n:
            t = t.replace(src, dst)
            what = {"​": "zero-width space"}.get(src, src)
            changes.append(f"{what} -> {dst or 'removed'} (x{n})")
    if "៖" in t:
        changes.append(f"៖ -> ។ (x{t.count('៖')})")
        t = t.replace("៖", "។")
    before = t
    t = expand_repeats(t)
    if t != before:
        for word in sorted(set(re.findall(r"\S+ ?ៗ", before))):
            changes.append(f"{word} -> {expand_repeats(word)}")
    for src in sorted(PRON, key=len, reverse=True):
        if src in t:
            changes.append(f"{src} -> {PRON[src]} (respelling)")
            t = t.replace(src, PRON[src])
    t = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in t.splitlines())
    return t, changes


def problems(spoken: str) -> list[str]:
    """Reasons this spoken text must not go to the voice (empty = fine)."""
    t = MARKER.sub(" ", spoken)
    found: list[str] = []
    if "ៗ" in t:
        found.append("leftover repeat mark ៗ")
    if m := re.findall(r"[A-Za-z]+", t):
        found.append(f"Latin letters: {' '.join(sorted(set(m)))} (write them as Khmer speakers say them)")
    if m := re.findall(r"[0-9០-៩]+", t):
        found.append(f"digits: {' '.join(sorted(set(m)))} (write numbers as Khmer words)")
    if m := re.findall(r"([ក-៿]{2,}) \1(?![ក-៿])", t):
        found.append(f"repeated word with a space: {', '.join(sorted(set(m)))} (join the copies)")
    for m in re.finditer(rf"(^|[\s{DEP_VOWEL}ំ-ៈ])([{DEP_VOWEL}])", t):
        at = m.start(2)
        found.append(f"vowel sign {t[at]} with no consonant before it: …{t[max(at - 6, 0):at + 6]}… "
                     "(typed in visual order? ask the user)")
    return found


if __name__ == "__main__":
    raw = open(sys.argv[1], encoding="utf-8").read()
    spoken, changes = prepare(raw)
    print(spoken)
    print("\nchanges:" if changes else "\nchanges: none")
    for c in changes:
        print("  " + c)
    bad = problems(spoken)
    print("problems:" if bad else "problems: none")
    for b in bad:
        print("  " + b)
    sys.exit(1 if bad else 0)
