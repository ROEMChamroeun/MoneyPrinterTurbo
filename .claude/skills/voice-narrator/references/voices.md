# The voice roster

The source of truth for what exists is VoiceStudio's database (`scripts/voices.py list`). This file records what the
database can't hold: where each voice came from, what the user said about it, and what it suits. Update it whenever a
voice is created, approved, renamed or used for a delivery.

**Ids are stable, names are not.** The user renames voices in the VoiceStudio app (`khmer-voice-artist` became
`reader-voice-girl-001`, `prosecutor-girl` became `sad-main-char-girl-001`), so record and pass ids. When the user
writes `<voice>_seed<N>` (as in "drama-sister-girl-001-v2_seed7"), they mean that profile at seed N; `narrate.py`
accepts that form directly.

Pace and pitch below were measured on each reference with narrate.py's own measure (speech seconds; characters
without spaces or punctuation), so they compare directly with the `chars/s` column of a narration's report.md.

## Approved

| Id | Name | Voice | Reference | Pace | Pitch | Verdict and use |
|---|---|---|---|---|---|---|
| `e6b0acc9` | doc-narrator-girl-002 | Calm documentary narrator, woman | Hout Bophana episode of the ជីវិតអច្ឆរិយ documentary series, item 06 (2:21–2:50), 28.6 s, SoundCraft `hout-bophana-studio` tuned. `voice-refs/hout-bophana/` | 12.9 c/s | 269 Hz | **Approved 2026-10-21** ("That's Good"), seed 7. 6–12% slower than 001. Used: norwegian-wood narration |
| `5feb7b80` | doc-narrator-girl-001 | Same narrator as 002 | Nou Hach episode opening, 6.05–35.70 s, 29.7 s, de-reverb + DeepFilterNet. `voice-refs/nou-hach/` | 14.3 c/s | 258 Hz | **Approved 2026-10-18** ("very good result"), seed 7. Clone runs dull above 8 kHz. Used: short-003/004 dubs |
| `4cd0ec06` | sad-main-char-girl-001 | Young woman, soft and sad; was `prosecutor-girl` | TVB Cambodia Khmer dub of The Unusual Prosecutor (YouTube short), five phrases, 9.9 s. `voice-refs/prosecutor-girl/` | 15.6 c/s | 335 Hz | **Approved 2026-10-18**, seed 7 (the user preferred one seed over per-line ASR picks). Used: short-02 confession |
| `d25324f7` | drama-sister-girl-001-v2 | Drama, a sister pleading; emotional | TVB Grace Under Fire Khmer dub ep 32, 15:21–16:16, speaker S04, 29.5 s; de-reverb without DeepFilterNet (natural fade-outs) + SoundCraft polish. Transcript keeps the user's `..` marks | 15.2 c/s | 343 Hz | "Much better" than v1 (2026-10-20); several narrations approved: n01 at seed 23 ("more dramatic"), n05 at seed 7. Used: confession, echo, norwegian-wood (alt take) |

## Usable, not fully judged

| Id | Name | Voice | Reference | Pace | Pitch | Status |
|---|---|---|---|---|---|---|
| `f9c08f52` | reader-voice-girl-001 | Female voice-over artist demo; was `khmer-voice-artist` | `~/Downloads/Khmer Female Voice Artists_clean.wav`, 22.6 s | 15.2 c/s | 257 Hz | The documentary default since 2026-10-05: money-printer web UI (`voicestudio:f9c08f52`), the tiktok-short template's `narrate.py` |
| `66a5b84d` | flower-wilted-speaker-b | Low male voice | After the Flower Wilted (Smart Axiata animated film) 5:32–5:45, 12.8 s, the user's transcript | 15.8 c/s | 148 Hz | Narrated the AI-in-company film (2026-10-14). Film dialogue: carries acting energy |
| `3e72d7c6` | flower-wilted-speaker-c-v2 | The film's heroine; high, breathy, emotional | After the Flower Wilted 15:07–15:40, 29.6 s, the user's transcript (2026-10-19) | 11.7 c/s | 439 Hz | Test seeds clean, similarity 0.70–0.79. **Listen check pending** |

## Don't use

- `fe90c30c` flower-wilted-speaker-c: its transcript is only an ASR draft, and a wrong transcript garbles every line. Replaced by `3e72d7c6`.
- `demo0001`: VoiceStudio's English demo.
- Gone from VoiceStudio (not in the database as of 2026-10-24): `cfa76b2e` fav-song-girl, `32406811` drama-sister-girl-001 (v1; its DeepFilterNet-gated reference taught the clone hard sentence stops), `f91db2ce` drama-sister-girl-001-short.

## Naming new voices

`<role>-<gender>-NNN`, such as `doc-narrator-girl-003` or `drama-sister-girl-002`. A rebuilt reference of the same
clip gets `-v2`. A new clip of a voice already in the roster gets the next number; doc-narrator-girl-002 is the same
narrator as 001. Ask the user for the name only if the role isn't obvious.

## Permission

Every voice here is cloned from someone else's recording: a voice actor, a TV dub, a documentary narrator, an
animated film. Before anything made with one is published or monetised, the user needs the owner's permission. On
TikTok, switch on the AI-generated content label; on YouTube, answer Yes to "Altered or synthetic content". Mention
this once per delivery, briefly, not as a lecture.
