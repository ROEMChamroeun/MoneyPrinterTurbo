# Voice craft: standards, metrics, fixes

## Contents
- Loudness targets
- What the analysis numbers mean
- Voice frequency map
- Feedback → fix
- TTS voices (VoxCPM / VoiceStudio)
- Real recordings
- Listening protocol

## Loudness targets

| `--target` | Integrated | True peak | Notes |
|---|---|---|---|
| `tiktok` | −14 LUFS | ≤ −1.5 dBTP | TikTok, Reels and Shorts. Matches the tiktok-short skill's export check. Phones want low dynamics: phrase spread under ±2 dB |
| `youtube` | −14 LUFS | ≤ −1.0 | YouTube turns louder uploads down |
| `podcast` | −16 LUFS | ≤ −1.0 | Apple's spec, also the AES streaming recommendation. Spotify uses −14, but −16 is safe everywhere |
| `broadcast` | −23 LUFS ±0.5 | ≤ −1.0 | EBU R128 TV and radio. ATSC (US) is −24 LKFS, ≤ −2 dBTP |
| `audiobook` | RMS −23 to −18 dB (aims −20) | sample peak ≤ −3 | ACX also requires a noise floor ≤ −60 dBFS, 0.5–1 s room tone at the head, 1–5 s at the tail, and 44.1 kHz 192 kbps CBR MP3 delivery |
| `stem` | −20 LUFS | ≤ −3 | Narration that gets mixed under music later (FilmCraft normalizes the final mix) |

Mono files are measured as dual-mono (`ebur128 dualmono=true`), which is how they play on stereo. They read the same as the stereo bounce.

## What the analysis numbers mean

| Metric | Meaning | Good |
|---|---|---|
| loudness (LUFS) | Integrated, gated perceived loudness | target ±0.5 |
| true peak (dBTP) | Peak after reconstruction | ≤ target |
| LRA (LU) | Spread of short-term loudness | ≤ 6 for phones. Unreliable under 30 s with long pauses (compression can even raise it there), so use phrase spread instead |
| phrase spread | Standard deviation of per-phrase level | ≤ ±2 dB. Studio leveling usually reaches ±0.5 |
| speech level | Median 20 ms frame RMS on speech | Used to set the leveler threshold |
| noise floor | Level in pauses (30th percentile of non-speech frames) | ≤ −60 dBFS (ACX); ≤ −70 is excellent. Digital silence in TTS gaps reads as "digital silence" |
| SNR | Speech level minus noise floor | ≥ 45 dB clean; under 30 dB audible noise |
| sibilance | Loudest S sounds (5–10 kHz, 99th percentile) vs loud syllables (80th percentile) | Natural is about −10 to −7. Above −6 is hot; above −4 is harsh |
| low bursts | 25–100 Hz bursts vs loud syllables | Below −10; above means plosive thumps or rumble |
| tilt | 1/3-octave slope from 250 Hz to 8 kHz | Information only. Shallower (−2) is bright, steeper (−6) is dark. Compare against a reference rather than an absolute |
| bandwidth | Highest frequency within 50 dB of the 1–4 kHz level | ≥ 16 kHz full band. Under 12 kHz means a low-rate or MP3 source, and air boosts only add noise |
| pitch median / lowest | Voice F0 (lowest = 5th percentile) | Sets the high-pass (half the lowest pitch, 60–100 Hz) |
| limiter depth | How far the master limiter pushes | ≤ 2 dB ideal, ≤ 4 acceptable. More means fix the stages before it |

## Voice frequency map

| Range | What lives there | Too much | Too little |
|---|---|---|---|
| < 80 Hz | Rumble, handling noise, plosive thumps | Boomy, muddy on headphones | — |
| 80–250 Hz | Chest and body (fundamental of low voices) | Boomy, chesty | Thin, small |
| 200–500 Hz | Warmth, but also mud | Muddy, boxy, "in a cupboard" | Cold, thin |
| 500 Hz–1.5 kHz | Nasal and honk, telephone character | Honky, nasal, phone-like | Hollow |
| 2–5 kHz | Presence, intelligibility, edge | Harsh, shouty, tiring | Distant, dull, mumbled |
| 5–9 kHz | Sibilance (S, SH, CH) | Spitty, harsh S sounds | Lisping, dull |
| 9–16 kHz | Air, breath, sparkle | Hissy, brittle, fizzy (TTS) | Dull, closed-in |

EQ moves: cut narrow (Q 1–2), boost wide (Q 0.7–1), and keep everything within ±4 dB. Cut before you boost.

## Feedback → fix

Change one thing, re-render, and compare against the previous master at matched loudness (`se.py compare`).

| The user says | Likely cause | Change in `job.json` |
|---|---|---|
| muddy, boxy, cloudy | 200–500 Hz build-up | Polish EQ `low_mid_gain` −2 to −3 at 250–350 Hz, Q 1.2 |
| boomy, bassy | Too much under 150 Hz | Raise the high-pass to 100–120 Hz or use slope 2 (18 dB/oct). Remove warmth boosts (intimate/cassette `low_mid_gain`) |
| thin, small, no body | High-pass too high, or warmth missing | Lower the high-pass; `low_mid_gain` +1.5 to +2.5 at 180–250 Hz |
| harsh, shouty, tiring | 2.5–4 kHz too strong, or heavy limiting | `mid_gain`/`high_mid_gain` −2 at 3 kHz; check the limiter depth |
| S sounds hurt, spitty | Sibilance | Move the de-esser goal to [−10.5, −8.5], or raise `range` |
| lisping, dull S | Over de-essed | De-esser goal [−8.5, −6.5] or lower `range` |
| dull, muffled, far away | Missing presence or air | Polish `high_mid_gain` +2 at 3–5 kHz and `high_shelf_gain` +2 at 10–12 kHz (if bandwidth ≥ 16 kHz) |
| fizzy, hissy, robotic, metallic (TTS) | Boosting the vocoder's synthetic band | Move presence down to 2.5–3 kHz, `high_shelf_gain` 0 or −1.5, optionally `eq_1band` −2 dB at 6–8 kHz. A touch of room (intimate) masks the artificial dryness |
| too dry, clinical | No space | Try the intimate mood (small room) or a `room_reverb` at mix 5–8 |
| too much reverb, voice too far | Mood too wet | Lower the reverb `mix` by 5–10; raise `pre_delay` (keeps words clear); shorten `decay` |
| echo is distracting | Delay too loud or too long | `mod_delay` `mix` −8, `feedback` 20–25 |
| squashed, lifeless, flat | Too much compression or limiting | Leveler ratio 2:1; peak-stage goal +1.5 dB; aim lower (`stem` or `podcast`) |
| pumping, breathing | Fast release or heavy gain reduction | Leveler release 150–250 ms; less ratio |
| hiss, noise in pauses | Noise floor | Expander `range` 15–18 and threshold +2; denoise `nr` 20 |
| words cut off at the ends | Expander too aggressive | Expander threshold −4, `hold` 150, `release` 250 |
| clicks or pops | Mouth clicks or bad span joins | `preclean.declick: true` |
| uneven: some lines loud, some quiet | Leveling | Leveler ratio 3:1, threshold −2; check the phrase spread |
| too quiet on the phone | Loudness or dynamics | Confirm −14 LUFS. Lower the phrase spread (more leveling) and add presence at 2–4 kHz, which phones reproduce |
| distorted, crunchy (not radio/cassette) | Clipping in the source, or limiter overload | Check `clipped` in the analysis (declip); keep limiter depth under 4 dB |

## TTS voices (VoxCPM / VoiceStudio)

Measured on `drama-sister-girl-001-v2` seed 7 (October 2026). Re-measure for other voices.

- The narration pipeline makes each span separately. Spans arrive pre-leveled (±0.3 LU), and pauses between spans are digital silence (81% of non-speech time). Expect a phrase spread around ±1.2 dB and an LRA around 3.
- Almost no energy below 80 Hz (−53 dB), so a 60 Hz/6 dB safety high-pass is enough. A higher one only raises peaks.
- The spectrogram shows harmonics stopping sharply around 4.3 kHz, noise-like content above, and a brick wall at 20 kHz. That's a vocoder signature. Presence boosts above 4 kHz and air shelves lift the synthetic part. Keep them gentle (+1.5 dB in `studio`), and move them lower if the user hears fizz.
- Compression plus presence lifts its S sounds from about −9 to −4 dB, so the de-esser does real work. After tuning, sibilance lands near −9.
- The noise floor near words sits around −63 to −73 dBFS. No denoise needed.
- Some problems are the model, not the mix: unnatural prosody, Khmer pronunciation, a line that cuts off ("the model cut the line off"), breath artifacts. Processing can't fix those. Say so and suggest regenerating the span, another seed, or another voice.

## Real recordings

- **Noise:** with the noise floor above −60, `se.py` adds denoise plus an expander. Above −50 is audible hiss; warn the user that re-recording beats rescue.
- **Plosives:** low bursts above −10 trigger an 18 dB/oct high-pass. Bad pops need clip gain on the burst (`clip.gain`) or a re-record.
- **Low male voices trip the low-burst check.** On a phone memo with f0 down to 83 Hz (October 2026), every "burst" frame after mastering was voiced at 93–98 Hz: the voice's own fundamental, raised relative to the loud syllables by the leveler. Check voicing at the burst times before steepening the high-pass; a pitch reading of "lowest 60 Hz" there was room rumble, and 80 Hz/18 dB was right.
- **Room rumble memos** (noise floor −52, mostly below 300 Hz): the auto peak stage dropped to its floor and lifted the pauses to −46. Pin the peak stage near speech level +3.5 dB, use a voice-track `maximizer` (threshold 0, ceiling ~2.5 dB under the chain peak) as a first limiter stage, and an expander at range 24 / hold 120 / release 200 reached −61 with word tails intact.
- **Electronic whine** (a steady line at 15,625 Hz in the spectrogram): `eq_1band` type 5 notch, Q 10.
- **Mouth clicks:** set `preclean.declick: true`.
- **Room echo:** processing can't remove it. Don't add more reverb on top. Say so.
- **Long files** (minutes) take about 1 minute end to end. The tuning loops dominate.

## Listening protocol (what to ask the user)

1. Play the AB file on headphones, then on a phone speaker. Both segments are at the same loudness, so differences are tone and dynamics, not volume.
2. Listen for: S sounds (natural, not spitty), word endings (not chopped), pauses (clean, no hiss pumping), body (not thin, not boomy) and presence (clear but not harsh).
3. One question back: which is better, and is anything too bright, too dull, too processed or too wet?
