# How the clone reads Khmer, and how to fix what the user hears

Everything here was measured on VoxCPM2 (MLX, continuation cloning) with this user's voices between 2026-10-07 and
2026-10-22. You can't hear the audio, so measure first, then hand the user an A/B, because their ear makes the call.

## Contents
- Punctuation, spaces and pauses
- Pace
- Words
- Endings and cut-offs
- Seeds
- Speed and memory
- When the user says… (feedback table)

## Punctuation, spaces and pauses

- **A Khmer full stop `។` is the only reliable breath inside a line.** It gives a 0.27–0.31 s pause with a level or
  falling tail. Spaces, commas, line breaks, double spaces and ellipses give only 0.10–0.15 s, and the phrase ends
  on a *rising* pitch (+4 to +8 semitones). No other break mark works, so don't try more.
- `narrate.py` generates each sentence separately and inserts real silence, so the gaps between pieces are exact:
  phrase 0.30 s, sentence 0.60 s, ellipsis 0.80 s, paragraph (blank line) at least 1.0 s. Pauses come out about
  0.1 s longer than set, because each piece keeps its own natural fade.
- VoiceStudio's markers are honoured exactly: `[pause]` = 350 ms, `[pause 500ms]`, `[pause 1s]`, `[pause 1.5s]`, a bare
  number = ms, capped at 10 s, adjacent markers add up. The user writes them; keep them as written.
- Mood pieces want long gaps. In the confession short the user asked for a gap at every `...` and liked about
  2.2–2.6 s there (`--gaps 0.30 0.60 2.4`).

## Pace

- The clone copies the reference's articulation rate but makes about half its pauses, so it can feel hurried even at
  the right syllable rate. More pauses (`។`, gaps) fix this; slowing the voice doesn't.
- **Short unpunctuated pieces and long pieces rush.** In the long test (2026-10-20), 9 of 14 sentences ran 22–50%
  faster than the reference; the short climax line was +44%. Sentences over 120 characters are cut at a space by
  narrate.py, because long calls rush.
- **A space between whole phrases is the pace control** inside a dense phrase: one breath of about 0.35–0.65 s takes a
  line 3–5% slower. Put it between whole phrases (អារម្មណ៍ដែលខ្ញុំមាន ចំពោះបង). Never put it right after a word:
  a space after អារម្មណ៍ made the voice misread the word.
- `report.md` flags pieces over ±20% from the reference pace. Treat that as a pointer for the user's ear, not a verdict:
  pleading or dramatic lines run fast in the reference too.
- VoxCPM2 ignores numeric speed settings. Time-stretching works, but the user chose the raw take over a 14% WSOLA
  stretch with inserted breaths, so offer it only if they ask.
- A `(style)` prefix in the text switches VoxCPM2 from continuation to reference-only cloning, which matches the voice
  less closely. Don't use it.

## Words

- Numbers must be Khmer words (មួយពាន់ប្រាំបួនរយហុកសិប). Foreign names are written the way Khmer speakers say them;
  in the norwegian-wood narration the user swapped the Japanese names for Khmer ones (ដារ៉ា, ចិន្តា, ធីដា).
- `ៗ` is read as the word twice, joined with no space. With a space, the copies sound disconnected.
- Misordered vowels (`ដេីម្បី`, `ថ្ងៃេនះ`) look right on screen and are misread. khmer_text.py fixes the common pairs and
  reports the rest.
- **Speech recognition can't hear a misread.** It transcribed សមរាត្រី as correct when the voice said "sak mak reatrey".
  Only the user's ear finds misreads, so ask them to listen to the words near any text change.
- To fix a misread word, first look for a stray space or a bad encoding near it. Only then try respellings: render
  2–3 spellings in context at the same seed and put them in one listen file with the original first. In the one
  case so far, the user picked the original spelling once the space was gone. Add a winning respelling to `PRON` in
  khmer_text.py.

## Endings and cut-offs

- About 1 in 5 short generations stop mid-sound: the clip ends at full loudness instead of in silence. narrate.py
  re-rolls those with seed+100, then seed+200, and flags any that survive as CUT-OFF. To fix one by hand, use
  `--reroll K`. Every piece is generated on its own seed reset, so the other pieces stay byte-identical.
- If *every* sentence ends abruptly or "not properly finished", the reference is at fault: DeepFilterNet snapped its
  fade-outs to silence and the clone learned hard stops. Rebuild the reference without DF (new-voice.md).
- VoxCPM2 writes exact digital silence after speech, so a fade-out meter like endings.py reads raw model output as
  "cut off". Judge raw takes by the level at the speech end, which is what narrate.py's `stopped()` does.

## Seeds

- Narration uses **seed 7, one take** (the user, 2026-10-21: a second seed "waste time"). Run another seed only when
  they ask for an alternative delivery.
- A seed changes a line's feel: seed 23 was "more dramatic" on drama-sister. But across seeds the same lines stayed
  fast, so when a line is wrong, fix the text (gaps, `។`, spaces between phrases) before re-rolling seeds.
- A per-line "best take" picked by lowest ASR error was *not* the user's choice; they preferred the single seed-7 run.

## Speed and memory (16 GB Mac)

- The model loads in about 4 s once cached. Generation runs about 3–4x real time: a 2–3 s piece takes 8–15 s, and
  75 s of narration takes about 5 min. A 30 s reference costs more per call than a 10–15 s one, but only in time;
  the short reference didn't change the reading.
- Peak memory is about 7.5 GB. Never run two VoxCPM2 copies at once (VoiceStudio generating, a second narrate.py,
  a test). The Mac swaps and a 2.6 s line takes 119 s instead of 13 s. narrate.py refuses to start if it sees one.
- VoiceStudio's own PyTorch path is about 6x slower on clones: each call re-reads a 30 s reference twice, 80–90 s per
  call. Its default "broadcast" effect also flattens emotion (3:1 compression); if the user generates there, suggest
  the Raw effect.
- VoxCPM2 resamples the reference to 16 kHz, so nothing above 8 kHz reaches the model. The output is full-band, but
  dull above about 8 kHz compared with the original narrator; sound-engineer handles tone.

## When the user says…

| They say | Most likely cause | Do this |
|---|---|---|
| "This line is a bit fast" | Short unpunctuated piece, or a long one | Add `។` or a space *between whole phrases*; split the sentence; regenerate only that piece; A/B old vs new |
| "Too fast overall", "make it relaxed/calm" | Too few pauses, not too fast speech | Raise gaps (`--gaps 0.4 0.8 1.2`), add `។` before clause openers (ប៉ុន្តែ ហើយ ព្រោះ ដូច្នេះ បន្ទាប់មក) in long sentences; keep sentences short |
| "Word X is not read properly" | Space next to it, misordered vowel, rare word | Check spacing and encoding first, then respellings in context (above) |
| "Sentence end is cut", one line | Model stopped mid-sound | `--reroll K`; check the report's CUT-OFF flag |
| "Endings unfinished, machine-like, lost emotion", every line | DF-gated reference, or VoiceStudio's broadcast effect | Rebuild reference without DF; use Raw in VoiceStudio |
| "Background not clean", echo, hiss in every line | The reference's room | Clean the reference (new-voice.md). Lines whose measure_take.py gap sits far under the reference's confirm it |
| "Tone changes line to line", uneven | Reference-only cloning (no transcript) | Get the exact transcript on the profile; never test without one |
| "Sounds like a different person" | Wrong or short reference, or acting energy in a film clip | Check similarity with measure_take.py; pick a calmer 20–30 s stretch |
| Louder, warmer, brighter, less harsh, an effect or mood | Not a generation problem | sound-engineer skill |
