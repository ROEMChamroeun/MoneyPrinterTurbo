"""Shared spoken-Khmer rules for channel films (rebuilt 2026-10-14 from notes after the old copy was lost).

What it guards against (see memory khmer-voice-review-before-build):
- the voice clone pauses at every space, so a repeated word must be joined, never "X X";
- a leftover repeat mark ៗ, Latin letters or digits reach the voice and get misread;
- some rare words are misread: add the respelling that sounds right to PRON (caption keeps the real spelling).
Only the spoken text changes; captions always keep the correct spelling.
"""

from __future__ import annotations

import re

# caption spelling -> spoken respelling. Fill only with winners found by listening (tts_try.py style).
PRON: dict[str, str] = {}

# Repeat-mark compounds the ICU word breaker splits into pieces (នី+មួយ+ៗ): spoken form, joined, no space.
REPEATS: dict[str, str] = {"នីមួយៗ": "នីមួយនីមួយ"}

_LATIN = re.compile(r"[A-Za-z]")
_DIGIT = re.compile(r"[0-9០-៩]")
_KH = "ក-៿"


def expand_repeats(text: str) -> str:
    """Spoken form of the repeat mark ៗ: the whole word twice, joined with NO space (នីមួយៗ -> នីមួយនីមួយ).

    A space between the copies made the voice read them as two disconnected words (user, 2026-10-07).
    Uses the same ICU word breaker as khmer_phrasing, so a multi-syllable word repeats as a whole.
    """
    for word, spoken in REPEATS.items():     # compounds the word breaker splits wrongly
        text = text.replace(word, spoken)
    if "ៗ" not in text:
        return text
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from khmer_phrasing import segments

    out: list[str] = []
    for seg in segments(text):
        if seg == "ៗ" and out:
            out[-1] = out[-1] * 2
        elif seg.endswith("ៗ") and len(seg) > 1:
            out.append(seg[:-1] * 2)
        else:
            out.append(seg)
    return "".join(out)


def speak(text: str) -> str:
    """Caption text -> text for the voice (respellings, calm punctuation, joined spacing)."""
    t = expand_repeats(text)
    for src in sorted(PRON, key=len, reverse=True):
        t = t.replace(src, PRON[src])
    t = t.replace("៖", "។")          # a colon is not a pause mark for the clone; a full stop is
    t = re.sub(r"\s+", " ", t).strip()
    return t


def speech_problems(text: str) -> list[str]:
    """Reasons this spoken text must not be sent to the voice (empty list = fine)."""
    problems: list[str] = []
    if "ៗ" in text:
        problems.append("leftover repeat mark ៗ")
    if _LATIN.search(text):
        problems.append("Latin letters")
    if _DIGIT.search(text):
        problems.append("digits (write numbers as Khmer words)")
    if re.search(rf"([{_KH}]{{2,}}) \1(?![{_KH}])", text):
        problems.append("repeated word separated by a space (the voice pauses at it)")
    if not re.search(rf"[{_KH}]", text):
        problems.append("no Khmer text")
    return problems
