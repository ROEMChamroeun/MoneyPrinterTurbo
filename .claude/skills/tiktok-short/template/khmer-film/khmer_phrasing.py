"""Calm phrasing for the narrator clone (rebuilt 2026-10-14 from notes after the old copy was lost).

Measured 2026-10-08 (memory voice-calm-delivery): the clone ignores spaces, commas and ellipses (0.1-0.15 s
pauses, rising pitch) but obeys a Khmer full stop «។» inside a line (0.27-0.31 s pause, level or falling tail).
So a long sentence is given breath marks: a full stop is inserted before a clause opener, only when both
sides are long enough to be a phrase. Short sentences stay whole. Only the SPOKEN text changes; captions keep
the original punctuation.

Word segmentation comes from ICU through Node (Intl.Segmenter('km')), which is the only Khmer word breaker here.
"""

from __future__ import annotations

import functools
import json
import re
import subprocess

_NODE = (
    "const t=JSON.parse(require('fs').readFileSync(0,'utf8'));"
    "const s=new Intl.Segmenter('km',{granularity:'word'});"
    "process.stdout.write(JSON.stringify([...s.segment(t)].map(x=>x.segment)))"
)

# Words that open a new clause. "ពេល" is left out on purpose: it is also inside ពេលយប់, ពេលវេលា.
OPENERS = {"ប៉ុន្តែ", "ហើយ", "ព្រោះ", "ដូច្នេះ", "បន្ទាប់មក"}


@functools.lru_cache(maxsize=None)
def segments(text: str) -> tuple[str, ...]:
    out = subprocess.run(["node", "-e", _NODE], input=json.dumps(text), capture_output=True,
                         text=True, check=True).stdout
    return tuple(json.loads(out))


def _relax_sentence(s: str, min_before: int, min_after: int, long_over: int) -> str:
    if len(s.replace(" ", "")) <= long_over:
        return s
    segs = segments(s)
    total = len(s.replace(" ", ""))
    out, since_break, done = [], 0, 0
    for seg in segs:
        word = seg.strip()
        n = len(word)
        if (word in OPENERS and out and since_break >= min_before and total - done >= min_after
                and not "".join(out).rstrip().endswith("។")):
            out[-1] = out[-1].rstrip()
            out.append("។ ")
            since_break = 0
        out.append(seg)
        since_break += n
        done += n
    return "".join(out)


def relax(text: str, min_before: int = 24, min_after: int = 16, long_over: int = 52) -> str:
    """Add breath marks to long sentences of already-spoken Khmer text."""
    parts = re.split(r"(?<=។)\s*", text.strip())
    return " ".join(_relax_sentence(p, min_before, min_after, long_over) for p in parts if p)


if __name__ == "__main__":
    import sys
    for line in sys.argv[1:]:
        print(relax(line))
