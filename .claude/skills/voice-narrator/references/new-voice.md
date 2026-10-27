# Building a new narrator voice

From a recording (YouTube video, MP3 episode, film, TV dub) to an approved VoiceStudio profile. Done this way for
doc-narrator-girl-001/002, sad-main-char-girl-001, drama-sister-girl-001-v2 and flower-wilted-speaker-c-v2. Each
step says what to measure, because you can't hear the result.

## Contents
1. Folder and source
2. Clean: music, room, noise
3. Phrase map and speaker check
4. Choose the reference
5. Transcript
6. Create the profile
7. Test and hand over
8. Multi-speaker sources (films, dramas)

Paths: `R=~/Personal/projects/money-printer/storage/voice-refs`, `SK=<this skill>/scripts`,
`AV=$R/venv/bin/python` (analysis), `VS=` VoiceStudio's runtime python (Whisper, MLX). Run everything on the Mac.

## 1. Folder and source

Make `$R/<voice-folder>/` with `src/ clean/ chunks/ items/ picks/ test/ listen/` and a `README.md` that you keep
current (source, every command, what was measured, the user's verdicts). `storage/` is gitignored and has been wiped
before, so the README is the only record of how a voice was built. A profile itself survives, because VoiceStudio
keeps its own copy of the audio and transcript.

- **YouTube:** `yt-dlp -f 251 -o src/source.webm "<url>"`. If it answers 429 or "confirm you're not a bot", add
  `--js-runtimes node --remote-components ejs:github --cookies-from-browser chrome`. Safari cookies are blocked by
  macOS privacy. Without cookies only format 18 (48 kbps AAC) comes through.
- **Files** the user drops in `money-printer/resource/voices/`: copy to `src/`.
- Note the source quality in the README (`ffprobe`; MP3 bitrate, the cut-off frequency in a spectrogram). VoxCPM2
  hears the reference at 16 kHz anyway, so a 16 kHz cut-off costs nothing for the clone.
- Song videos often burn the spoken lines into the picture as captions. Read the transcript off them before guessing
  with ASR; caption-change times also give better line boundaries than Whisper.

## 2. Clean: music, room, noise

```bash
$SK/ref/clean.sh src/source.mp3 clean           # full.wav, s1/vocals.wav, s2/deverb.wav, s2/deverb48.wav
```

RoFormer bleedless takes the music out (about 2x real time on MPS, so a 7-minute episode takes about 15 min). Then
UVR-DeEcho-DeReverb takes the room out. Don't run it while VoiceStudio or narrate.py is generating. The clone copies
the reference's room: any echo or noise left in the clip comes back in every generated line ("background not clean",
2026-10-18).

**DeepFilterNet only when needed, and checked.** First run phrases.py (step 3). It prints the speech-to-pause gap:
45 dB or more is clean, and pauses near -140 dB mean the separator gated them to silence. Then check the fade-outs:

```bash
"$AV" $SK/ref/endings.py chunks/phrases.json clean/s2/deverb48.wav
```

Natural speech fades in steps of about 10 dB (median biggest drop near 10–16 dB, a few % hard cut-offs). If the
separator already left the pauses near digital silence, stop here: no DF. If hiss or room noise remains, run
`clean.sh … --df` and check endings.py on `s3/df48.wav`. A median drop of 60–85 dB means DF snapped the fade-outs.
The clone then ends every sentence abruptly and loses emotion (drama-sister-girl-001 v1). In that case, use the
de-reverb stem.

If the voice is thin, boxy or harsh compared with an approved voice, polish the *built reference* (step 4) with the
sound-engineer skill (`--preset studio --target stem --ref <an approved reference>`), then bring it back to -20 LUFS
mono 48 kHz. Keep moves gentle. Afterwards, ECAPA similarity to the unpolished reference should stay at 0.98 or more.

## 3. Phrase map and speaker check

```bash
"$AV" $SK/ref/phrases.py clean/s2/deverb48.wav chunks/phrases.json [--narrator-at SEC ...]
```

Silero phrases, with edges moved out to where the stem falls under -60 dB (Silero starts soft onsets about 0.3 s late).
It also gives median pitch and ECAPA similarity to the narrator's centroid. Phrases far from her voice or pitch are
flagged `other` and never go into a reference. ECAPA needs length: 0.9 s slices of the narrator's own sentences score
0.48–0.71, so short flagged phrases at her pitch are usually hers. Check them by ear (ask the user) or by context,
then keep them with `--narrator-at`.

## 4. Choose the reference

What makes a good reference:
- **20–30 s of one calm speaker**, cut on whole sentences, natural pauses capped at 0.5 s. 30 s gave the best clone so
  far ("very good result"). 10–15 s generates faster but read the same.
- **Calm delivery for narration.** A clip cut from film dialogue carries its acting energy into every line. Pleading
  or crying references make an emotional voice, which is right for drama and wrong for a documentary.
- Pure: no second voice, no music bleed, no laugh or breath effect, natural fade-outs, no hard cut at either end.

Offer candidates, then let the user choose by ear:

```bash
"$AV" $SK/ref/chunk30.py clean/s2/deverb48.wav chunks/phrases.json items --prefix <voice-folder>   # ~30 s items
"$AV" $SK/ref/build_ref.py clean/s2/deverb48.wav chunks/phrases.json START END picks/<name>.wav      # one range
```

chunk30 plans cuts over the whole narration: items of at most 30.5 s at the narrator's longer pauses (0.6 s or more
is a sentence end). Recommend 2–4 items that are 27–30 s long and end at a long pause. The user may also give their
own range ("14:30–17:00, only the woman"); then cut exactly that with build_ref.py. If they say the start "looks
fast" or want only part of it, rebuild from their new range rather than trimming the file.

Make a before/after listen file, with the same stretch from the original mix and from the reference at the same
loudness, and a spectrogram. Put both in `listen/`. Everything the user should hear also goes to
`/Users/roemchamroeun/Personal/remote-vm/outputs/<voice-folder>/`, never the Desktop.

## 5. Transcript

VoxCPM2 *continues* from the reference's transcript, so it must be exact. A wrong one garbles every line, and with no
transcript the pace and tone drift from line to line (measured 2026-10-14). Never create a profile, or test a voice,
without the user's exact text.

```bash
"$VS" $SK/ref/asr_draft.py clean/s2/deverb48.wav picks/<name>.json        # writes picks/<name>.draft.txt
```

Give the user the draft one phrase per line, with the doubtful words marked ([?], or "beam and greedy disagree").
Use the story's context to make it as good as you can, but say plainly that it's a draft. They correct it. Save their
text, exactly as they wrote it, to `picks/<name>.txt`. Keep their spacing and their `..` marks; spaces where the
narrator pauses help. Then run `python3 $SK/khmer_text.py picks/<name>.txt` to catch misordered vowels or stray
characters, and ask about anything it flags rather than fixing it silently.

## 6. Create the profile

```bash
python3 $SK/voices.py create --name <role>-<gender>-NNN --audio picks/<name>.wav --text picks/<name>.txt
```

It starts the headless VoiceStudio backend if needed, posts the profile, and checks that the stored audio is
byte-identical and the transcript equal. To fix a transcript later, use `voices.py set-text <id> --text <file>`.
Then add the voice to [voices.md](voices.md) with the status "listen check pending".

## 7. Test and hand over

```bash
"$VS" $SK/narrate.py --profile <id> --text $SK/../assets/test-lines.txt --out test/v1_s7
"$AV" $SK/ref/measure_take.py test/v1_s7
```

The five standard test lines make voices comparable (all approved voices were judged on them). Seed 7 first. Add
seeds 11 and 23 only if a line goes wrong or the user wants to hear alternatives. Then check:
- similarity 0.7 or more on lines of a few seconds
- pitch within about 10% of the reference
- pace: lines 1 and 3 run 20–27% fast on every voice so far, which is normal
- gap close to the reference's own; far under it means the reference's room came through
- no CUT-OFF flags

Build `listen/<name>_original-then-clone.wav`: about 15 s of the reference, 1 s of silence, then the test, at matched
loudness. Copy the test and that file to `remote-vm/outputs/<voice-folder>/` and hand them over from there. Ask one short question, e.g. "Does this sound like her, and does any line
sound wrong?". Record the verdict in voices.md and the voice folder's README. "Very good", "that's good" or "good"
means approved at that seed.

## 8. Multi-speaker sources (films, dramas)

- **Who speaks when:** for a quick map, Demucs (`demucs -n htdemucs --two-stems=vocals -d cpu -o sep full.wav`, about
  4x real time) or the RoFormer stem. Then
  `"$AV" $SK/ref/chunk_voices.py vocals.wav no_vocals.wav out/` and `"$AV" $SK/ref/verify_clips.py out/`. Speakers
  are clustered by ECAPA and merged at 0.65 similarity. Nothing detected is thrown away: leftovers go to
  `_unsorted`, drifting clips to `_review`. Give the user a page of players per speaker so they can pick by ear.
- Phrase-level clustering is too coarse for drama, because one phrase often holds two actors. Check a chosen span for a
  second voice with phrases.py's similarity and pitch. A pitch split works well for a man and a woman (about 155 Hz vs
  340 Hz).
- Report speech seconds, not clip length. Never drop small speakers: one clean 8–10 s clip can make a clone.
- If the user says a voice is missing from a stretch, trust their ear over the clustering. Look for a group that
  split off and merge it.
