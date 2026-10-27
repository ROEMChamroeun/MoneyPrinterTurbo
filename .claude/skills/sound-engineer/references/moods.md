# Moods

The moods were tested by ear on the confession narration (`drama-sister-girl-001-v2` seed 7, 2026-10-22). Each was rendered as its own session in `/home/ubuntu/money-printer/voice-tune/sessions/`. The comparison files are on the Mac in `money-printer/storage/confession-narration/moods/` and `radio/`. Each preset in `assets/presets/` keeps the original chain under `as_tested` (`--exact` renders it verbatim). The normal render layers the mood's character on top of the studio foundation chain.

## Choosing

| Mood | Feels like | Use for | Tail |
|---|---|---|---|
| `studio` | Dry, clean, close, professional | Default. Narration, explainers, ads, news, documentary | 0 s |
| `intimate` | Warm, close, a whisper in the ear | Confessions, secrets, love letters, late-night thoughts | 0.5 s |
| `memory` | Soft, distant, gently blooming | Flashbacks, regret, "I still remember…" | 3 s |
| `echo` | Repeating, haunting | Inner voice, a name or line that keeps coming back | 2.5 s |
| `dream` | Floating, airy, unreal | Dreams, fantasies, someone gone, heaven, imagination | 5 s |
| `empty-room` | Alone in a bare hard room | Loneliness, an empty house, waiting for someone | 2 s |
| `cassette` | Warm worn tape with hiss and wobble | Old voice messages, a childhood tape, a recording of someone from years ago | 0 s |
| `radio` | Narrow, driven phone/AM radio | A phone call, an old broadcast, news from far away | 0 s |

A story can switch moods by section: present-day narration in `studio` or `intimate`, a flashback in `memory`, a remembered voice in `cassette`. Render each section's file separately and let the video edit cut between them.

## How they're built

| Mood | Character inserts (after the studio foundation) | Foundation changes |
|---|---|---|
| `studio` | Polish EQ: −1.5 dB at 300 Hz, +1.5 at 4.5 kHz, +1.5 shelf at 11 kHz. Replaced by a match EQ with `--ref`; air skipped on band-limited sources | — |
| `intimate` | EQ +2.5 at 220 Hz, −2 at 3 kHz, +1.5 shelf at 10 kHz; small room (8 % mix, 0.45 s, size 15) | Leveler 3:1, knee 8, threshold −2 |
| `memory` | EQ +1.5 at 250 Hz, −2 shelf at 8 kHz; dark plate (28 %, 3.2 s, 70 ms pre-delay) | — |
| `echo` | EQ +1.5 at 250 Hz; 420 ms delay (fb 35 %, mix 22 %, LPF 3.5 kHz, slow drift); plate (16 %, 2.2 s) | — |
| `dream` | HPF 140, −1.5 at 300 Hz, +3 shelf at 9 kHz; slow chorus (25 %); huge bright plate (38 %, 5.5 s, 90 ms pre-delay) | — |
| `empty-room` | −2.5 at 3 kHz, −3 shelf at 7 kHz; hard room (30 %, 1.8 s, size 75, diffusion 35) | — |
| `cassette` | Band 70 Hz–7 kHz, +2.5 at 180 Hz; saturator (drive 8, 70 %); chorus as wow/flutter; pink-noise bed (2–7 kHz, −40 dB) | — |
| `radio` | Band 500 Hz–3.6 kHz, +6 at 1.5 kHz; saturator (drive 14); 6:1 fast compressor; lofi 11-bit/11 kHz; second band-pass; pink-noise bed (400 Hz–3.4 kHz) | No leveler, no de-esser, peak stage after the chain |

The de-esser lands before the first reverb, delay or chorus, so S sounds don't splash into the tail.

**Moods on a file that is already mastered** (e.g. a `studio` master): `master --plan-only`, then delete the foundation's high-pass, leveler and pre-chain peak stage from each `job.json` before `render`. They already ran once, and a second leveler lifts the pauses. Keep the auto de-esser and radio's post-distortion peak stage. On the MyVoice studio master (2026-10-24) this gave limiter depth 0.8–2.9 dB on all seven moods.

## Verdicts

Record the user's verdict after each listen: date, mood, source, what they said, what changed.

| Date | Mood | Source | Verdict |
|---|---|---|---|
| 2026-10-22 | intimate, memory, echo, dream, empty-room, cassette, radio | drama-sister-girl-001-v2 seed 7 | Tested by ear (LISTEN_ files); verdict not recorded yet |
| 2026-10-24 | intimate, memory, echo, dream, empty-room, cassette, radio | MyVoice: the user's own male voice memo, studio master | Delivered to `outputs/MyVoice/moods/`; verdict pending |

## Adding a mood

Create `assets/presets/<name>.json`:

```json
{
 "name": "phone-call",
 "summary": "One line: what it sounds like",
 "story_use": "When to use it",
 "status": "proposed",
 "tail_s": 0,
 "foundation": {"leveler": {"ratio": 3.0}, "deesser": false, "peak": "post"},
 "inserts": [{"plugin": "eq_7band", "params": {"hpf_on": 1, "hpf_freq": 300}, "why": "..."}],
 "bed": {"inserts": [{"plugin": "signal_generator", "params": {"waveform": 5, "level": -40}}]},
 "as_tested": null
}
```

- `foundation`: `leveler` takes `false` or overrides (`ratio`, `knee`, `threshold_offset`). `deesser` takes `false`. `peak` takes `false` or `"post"` (use `"post"` for presets that distort, because they create new peaks).
- `tail_s`: about the reverb decay plus pre-delay. Delays need feedback time too.
- An insert with `"role": "polish"` is replaced by the match EQ when `--ref` is given.
- Keep the voice track to 10 inserts total. The foundation uses up to 5 (HPF, expander, leveler, peak, de-esser).
- Run `vm.sh sync`, render a shootout against `studio`, and set `status` to `tested` once the user has heard it.
