"""Khmer script for the TikTok short "Cambodia's river that flows backwards" (docs/video-plan-10/plan.md).

Single source of truth for words, caption layout and scenes. Each line: id, scene, Khmer text with caption marks:
  " / "  starts a new caption block (the screen clears)
  "|"    starts a new row inside the block; write " | " where the voice may take a breath, "|" where it must not
  "*"    at the start of a row sets it large and in the accent colour (the key words)
The voice reads the text with the marks removed (a space is a short pause for the clone, so spaces only go at
phrase boundaries). Written by Claude: needs a native Khmer read before publishing.
"""

from __future__ import annotations

import re

# (id, scene, Khmer text with caption marks)
_LINES: list[tuple[str, str, str]] = [
    ("l01", "hook", "*តើអ្នកដឹងទេ? / កម្ពុជាមាន|*ទន្លេមួយ / ដែល|*ហូរបញ្ច្រាសទិស។"),
    ("l02", "rain", "រៀងរាល់|*រដូវវស្សា / ទន្លេមេគង្គ|*ឡើងទឹកខ្លាំង / រហូតរុញទឹក|ចូលទន្លេសាប / "
                    "ឲ្យ|*ហូរត្រឡប់|ទៅបឹងវិញ។"),
    ("l03", "grow", "បឹងទន្លេសាប / *រីកធំជាងមុន / ប្រហែល|*បួនទៅប្រាំដង។"),
    ("l04", "fish", "ទឹកនោះនាំ|*ត្រីរាប់លានក្បាល / ចូលមក|*ពងកូន / ហើយចិញ្ចឹមជីវិត|*ប្រជាជនខ្មែររាប់លាននាក់។"),
    ("l05", "turn", "ដល់|*ខែកត្តិក / ទន្លេសាបក៏|*ត្រឡប់ហូរចុះ|ទៅទន្លេមេគង្គវិញ។"),
    ("l06", "fest", "ហើយនោះហើយ / ជាពេលដែលខ្មែរយើង|ប្រារព្ធ|*ពិធីបុណ្យអុំទូក / *បណ្តែតប្រទីប / *សំពះព្រះខែ / "
                    "និង|*អកអំបុក។"),
    ("l07", "thanks", "បុណ្យនេះ | គឺជា|*ការអរគុណដល់ទន្លេ / ដែលចិញ្ចឹមយើង|*គ្រប់ៗឆ្នាំ។"),
    ("l08", "ask", "ឆ្នាំនេះ | អ្នកនឹងទៅលេង|*បុណ្យអុំទូក|នៅខេត្តណា? / សរសេរប្រាប់ខ្ញុំផង។"),
]

_MARKS = re.compile(r"[|/*]")


def plain(text: str) -> str:
    """Text with the caption marks removed: what the voice reads and what the index stores."""
    return re.sub(r"\s+", " ", _MARKS.sub("", text)).strip()


def blocks(text: str) -> list[list[dict]]:
    """Caption blocks -> rows: {"text", "big", "offset" (character offset of the row in plain(text))}."""
    out, pos, flat = [], 0, plain(text)
    for blk in text.split(" / "):
        rows = []
        for raw in blk.split("|"):
            row = raw.strip()
            big = row.startswith("*")
            row = row.lstrip("*").strip()
            at = flat.index(row, pos)
            rows.append({"text": row, "big": big, "offset": at})
            pos = at + len(row)
        out.append(rows)
    return out


LINES: list[dict] = [
    {"id": i, "scene": sc, "start": None, "text": plain(t), "say": None, "blocks": blocks(t), "marked": t}
    for i, sc, t in _LINES
]

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "khmer-film"))
    from khmer_speech import speak, speech_problems

    bad = 0
    for ln in LINES:
        spoken = speak(ln["say"] or ln["text"])
        probs = speech_problems(spoken)
        bad += bool(probs)
        rows = sum(len(b) for b in ln["blocks"])
        print(f'{ln["id"]} {ln["scene"]:6s} {len(spoken):3d} chars ~{len(spoken) / 12:4.1f}s  '
              f'{len(ln["blocks"])} blocks {rows} rows  {"; ".join(probs)}')
        print(f'     spoken: {spoken}')
    total = sum(len(speak(l["say"] or l["text"])) for l in LINES)
    print(f"{len(LINES)} lines, {total} spoken chars (~{total / 12:.0f}s), problems: {bad}")
    sys.exit(1 if bad else 0)
