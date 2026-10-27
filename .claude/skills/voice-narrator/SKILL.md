---
name: voice-narrator
description: Khmer narration with the user's cloned VoiceStudio voices (VoxCPM2 on MLX, run on the Mac), and building new narrator voices from recordings. It narrates Khmer text with a named voice (doc-narrator-girl-002, drama-sister-girl-001-v2_seed7, sad-main-char-girl-001…), honours [pause] markers and the writer's punctuation, re-rolls a cut-off or wrong line without touching the rest, and fixes lines that run fast or misread a word. It hands finished takes to the sound-engineer skill for mastering and mood effects. It also turns a YouTube video, MP3 episode, film or TV dub into a new clone voice: separate the voice, clean the room, pick a 20–30 s reference, draft the transcript, create the VoiceStudio profile and test it. Use it whenever the user wants Khmer text narrated, read, voiced or spoken; names a voice profile or a seed; wants a voice-over for a film, short or TikTok; says a narrated line is fast, misread or cut off; asks which voices exist; or wants to clone, extract or make a voice from a video or recording. That holds even if they never say "narrator" or "TTS".
---

# Voice narrator

You run the user's Khmer narration voices: you narrate their text with a cloned voice, fix the lines they flag, and
build new voices from recordings. You cannot hear. Measure pace against the voice's reference, catch cut-offs and
check similarity. Then hand over one file, plus an A/B when something changed, and let the user's ear decide. Never
say a take "sounds" good.

## Where things live

| What | Where |
|---|---|
| Generation | **The Mac**, not the VM: VoxCPM2 on MLX runs at about 4x real time, while the VM's CPU runs about 25x and holds no voices. The user chose this on 2026-10-24, an exception to this workspace's "everything on the VM" rule. Mastering still runs on the VM |
| `VS` (VoxCPM2, Whisper) | `"$HOME/Library/Application Support/VoiceStudio/runtime/project/.venv/bin/python"` |
| `AV` (analysis, new voices only) | `~/Personal/projects/money-printer/storage/voice-refs/venv/bin/python` (torch 2.5.1, speechbrain, silero-vad, librosa, pyloudnorm). If it's gone, rebuild it: `uv venv --python 3.11 venv && uv pip install --python venv/bin/python "torch==2.5.1" "torchaudio==2.5.1" "numpy<2" soundfile scipy scikit-learn speechbrain silero-vad librosa pyloudnorm` |
| `SK` (this skill's scripts) | `/Users/roemchamroeun/Personal/remote-vm/.claude/skills/voice-narrator/scripts` |
| Voices | VoiceStudio's database and `voices/*.wav` in `~/Library/Application Support/OmniVoice/`. `python3 $SK/voices.py list`. What each voice is and suits: [references/voices.md](references/voices.md) |
| Narrations, and every file the user listens to | `/Users/roemchamroeun/Personal/remote-vm/outputs/<name>-narration/`: `text.txt`, `take/`, `mastered/`. Never copy files to the Desktop; the user said it clutters it (2026-10-24). Older narrations stay in `money-printer/storage/*-narration/` |
| Voice building | `~/Personal/projects/money-printer/storage/voice-refs/<voice-folder>/`, with a README per voice |
| How the clone reads Khmer, feedback → fix | [references/khmer-delivery.md](references/khmer-delivery.md). Read it before changing any text and whenever the user gives feedback |
| Building a voice, step by step | [references/new-voice.md](references/new-voice.md) |
| This user's preferences and verdicts | [references/taste.md](references/taste.md). Read it at the start of every job |

`storage/` is gitignored and has been wiped before. The tools live here in the skill, and each voice's README records
how it was made. Write a verdict down when you get it.

## Job 1: Narrate a text

1. **Voice.** Use the voice the user names. `name_seedN` means that profile at seed N. If they name none, infer it
   from the text and say which you chose in one line: calm documentary or explainer → `doc-narrator-girl-002`
   (`e6b0acc9`); emotional, drama or confession → `drama-sister-girl-001-v2` (`d25324f7`). Check voices.md before
   using anything unapproved.
2. **Folder and text.** Make `outputs/<short-name>-narration/` and save their text to `text.txt` exactly as given:
   markers, line breaks and spacing all stay.
3. **Check the text.** Run `python3 $SK/khmer_text.py text.txt`. It shows the spoken text, each change it makes
   (joined ៗ, re-encoded vowels, quote marks) and any problems.
   - **Digits:** propose the Khmer words yourself.
   - **Latin names:** propose a Khmer spelling as spoken.
   - **Misordered vowels it can't fix:** quote the spot.
   In every case ask the user to confirm, because you write the Khmer and they read it.
4. **Generate.** Use seed 7 and one take. Add `--plan` first to see the pieces, their gaps and the expected wait
   without loading the model, then tell the user the wait:
   ```bash
   mkdir -p take && "$VS" $SK/narrate.py --profile <id> --text text.txt --out take 2>&1 | tee take/narration.log
   ```
   Generation runs about 4x real time on a quiet Mac. If the script notes swap, expect about 15x: the UTM VM's
   QEMU process can hold an 18 GB footprint. It refuses to start while VoiceStudio or another narrate.py holds a
   model. Ask the user before passing `--force`.
5. **Read `take/report.md`.**
   - **CUT-OFF:** the model stopped mid-sound three times. Re-roll that piece now with `--reroll K`.
   - **fast / slow:** more than 20% off the reference pace. Mention only the ones that stand out, as places to
     listen first. Don't rewrite their text to fix pace unasked.
6. **Hand over.** Give the take's path, its length, and the spoken-text changes if any. Ask one short question:
   "Listen once: is any line too fast, any word misread, any ending cut?" Mention the voice owner's permission and
   the AI-content label once per delivery (voices.md, Permission).
7. **Master** when it's going to a platform or the user asks for polish or a mood (next section).

## Job 2: Fix what the user heard

Map their words to a cause with the table at the end of khmer-delivery.md, then change as little as possible:
- **One bad piece** (cut ending, odd delivery): `--reroll K`, or `--reroll K:SEED` for a specific seed. Every other
  piece stays byte-identical, and the new file is named `…_rerollK`.
- **A text fix** (a space between whole phrases, a `។`, a corrected word): edit `text.txt` and re-run into the same
  folder with `--tag v2`. Only the changed pieces regenerate, and the old take stays.
- **Then give them the comparison:**
  `python3 $SK/listen.py take/LISTEN_line5_old-then-new.wav <old piece> <new piece>`. The raw piece files are listed
  in `take/spans.json`. Tell them where each part starts.
- **Misread words:** check spacing and encoding near the word before trying respellings. A space right after a word
  can cause the misread.

## Job 3: Build a new voice

Follow [references/new-voice.md](references/new-voice.md). In short, all on the Mac:
1. Fetch the source.
2. `clean.sh`: RoFormer, then de-reverb. Add DeepFilterNet only if needed and only after checking fade-outs.
3. `phrases.py`: phrase map, speaker check, speech-to-pause gap.
4. `chunk30.py` or `build_ref.py`: candidate 20–30 s references.
5. `asr_draft.py`: a transcript draft.
6. `voices.py create`: the profile.
7. `narrate.py` on `assets/test-lines.txt`, then `measure_take.py`.
8. `listen.py`: reference, then clone.

Three points belong to the user, so stop and wait at each:
- they pick the reference by ear
- they correct the transcript (the clone continues from it, and a wrong one garbles every line)
- they approve the test

Record the result in voices.md and the voice's README.

## Mastering and moods: the sound-engineer skill

Narration leaves here at -18 LUFS, 48 kHz, mono, unprocessed. For platform loudness, polish or a mood (intimate,
memory, echo, dream, empty room, cassette, radio), use the sound-engineer skill. Its SKILL.md has the details:

```bash
V=/Users/roemchamroeun/Personal/remote-vm/.claude/skills/sound-engineer/scripts/vm.sh
$V sync && $V push take/<voice>_seed7.wav
$V se master inbox/<voice>_seed7.wav --preset studio --target tiktok      # stem: narration mixed under music later
$V pull jobs/<voice>_seed7/studio/out/<voice>_seed7_studio.wav jobs/<voice>_seed7/studio/out/AB_<voice>_seed7_studio.wav mastered/
```

Pick the target from where the narration is going: TikTok or Reels → `tiktok`; a film narration mixed under music
later → `stem`. For a mood, pass `--preset <mood>`, or several moods for a shootout the user picks from.

## Rules that matter

- **Transcript first.** Never create or test a profile without the user's exact transcript of its clip.
- **One VoxCPM2 at a time** on this 16 GB Mac. Don't start RoFormer, Whisper or a second narration while one runs.
- **Seed 7, one take,** unless the user asks for alternatives.
- **Their text is the record.** Disclose every spoken-text change, and after a change ask them to re-check the words
  around it. Speech recognition can't hear a misread; only their ear can.
- **Measure, then ask.** Pace, cut-offs and similarity tell you where to look. The user's verdict decides, and it goes
  into taste.md or voices.md the same day.
- **Ids over names.** The user renames voices in the app; record and pass ids.
