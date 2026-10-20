# My Little Space | រឿងគួរដឹង — how this workspace makes videos

This folder is a fork of MoneyPrinterTurbo that has become the film factory for the channel (@mylittlespacekh).
The stock web app is only used for the narrator's voice and for quick non-Khmer videos. Every channel film is its own
folder in `storage/`, built with a small set of scripts, with you listening and approving at the points that matter.

Copy-paste prompts for each kind of video are in [PROMPTS.md](PROMPTS.md). Status below is as of 2026-10-14.

## What do you want to make?

| I want… | Prompt | Pipeline | Notes |
|---|---|---|---|
| A story or emotion documentary, 7–11 min | 1, 2 | Narration, drawn diagrams and captions: ready (`storage/ai-problem-first-edu/`). Stock footage and music: **not rebuilt** (the old `love-19-vs-29-doc/` template is gone, 2026-10-14) | Past runs: narration about 30 min, voice check about 20 min, build 5–20 min, plus your listening time |
| A mystery / alien / ancient-world story | 1, 2, 6 | Same as above | Told from the believer's side (see Rules) |
| An animated explainer, 3–10 min | 3 | Ready. Template: `storage/ai-problem-first-edu/` (`maps-traffic-edu/` is gone) | The pictures are an animated web page; one command renders the film |
| A TikTok short on a trending topic (30–45 s, 9:16) | 5b | Ready (2026-10-18): the `tiktok-short` skill. Template: `storage/short-01-river/` (copy also in the skill's `template/`) | Claude finds the trend on Khmer TikTok, writes the plan, then builds with EffectCraft + FilmCraft on the VM. The full render takes about 25 min. You get the caption and hashtags too |
| A short vertical clip (under 60 s) cut from a finished film | 4 | Partly: the TikTok short template has the 9:16 captions, footage moves and export | Ask Claude to adapt `storage/short-01-river/` to cut from a finished film |
| An emotion short made from scratch (45–90 s) | 5 | Partly: same template as 5b | Same as above |
| A quick video in English or another language | 13 | Ready: the stock web app | Its subtitle renderer breaks Khmer letters, so not for Khmer captions |
| Not sure which format | 0 | | Claude recommends one and waits |

## How a film is made

1. **Research.** The `doc-research` skill writes a dossier to `docs/video-plan-NN/research.md`: the heart (what the story is
   really about), the story spine, the most vivid moments, Khmer script lines, names in Khmer, footage and rights. **You approve it.**
2. **Script.** `script_km.py` turns the words into captions plus a separate spoken respelling (numbers as words, foreign names the way
   Khmer speakers say them).
3. **Voice.** `narrate.py` runs the cloned voice `khmer-voice-artist` (VoxCPM2 on MLX) one line at a time and caches each line.
4. **Checks.** `qa_voice.py` and `asr_check.py` score the voice. They cannot hear a misread word, so `listen_list.py` lists the
   lines **you** must listen to. **You listen, then send corrections.**
5. **Build.** `build.py` makes captions and diagrams in headless Chrome (the only thing here that shapes Khmer correctly), adds
   footage, mixes music at -14 LUFS and assembles the film.
6. **QC.** `qc.py` checks streams, loudness, silences and writes contact sheets to look at.
7. **Package.** `youtube/make_youtube.py` writes chapters, description and tags; `make_thumbnails.py` makes three thumbnails.

Your three gates: approve the dossier, listen to the narration, run the pre-publish check (Prompt 11).

## Channel rules

- **Story over facts.** Viewers stay for love, longing, courage, loss and wonder. Don't fact-check a film into a list of corrections.
  The channel believes alien life exists; UFO, alien, crop-circle and ancient-mystery films argue that side. A hoax or natural
  explanation gets one line at most.
- **A few limits stay.** No invented quotes or shameful claims about real named people. Health, money or safety advice needs a real
  source. Never guess a person's age, ethnicity or family from a name or photo.
- **Footage:** CC0, public domain, CC BY, or the Pixabay/Unsplash licence. No AI-generated clips, no readable logos, no faces unless
  licensed for it. Credit everything on the end card. Redraw maps, charts and screens in the channel's own style.
- **Voice:** short sentences, calm. The clone obeys Khmer full stops, not spaces or commas; `khmer_phrasing.relax()` handles this.
  Claude cannot hear audio: it measures, you judge by ear.
- **Brand:** navy `#1B2A4A`, yellow `#FFC845`, coral `#FF6B5B`, cream `#F5F1E8`; Google Sans for Khmer and Latin; logo and banner in
  `storage/channel-brand/`.
- **YouTube Studio:** answer Yes to "Altered or synthetic content".

## Where things are

| Path | What |
|---|---|
| `docs/video-plan-01…07/research.md` | The seven dossiers (Lauren Tan, Angkor LiDAR, Angkor and the pyramids, crop circles, love at 19 vs 29, Google Maps, AI in a company). Next is `video-plan-08`. |
| `.claude/skills/doc-research/` | The research skill |
| `.claude/skills/tiktok-short/` | The TikTok short skill: trend research, plan, build, caption and hashtags; `template/` is a copy of the build code |
| `docs/channel/tiktok-review-2026-10-18.md` | Why the first three TikToks got no views, and the checklist before each post |
| `docs/channel/mood-fav-song-lyric-edit.md` | Mood breakdown of the fav-song lyric edit (sad song over a golden sea) and a recipe for making a similar short |
| `docs/video-plan-10/plan.md` | The first TikTok short's plan (Water Festival trend, a 3-part series) |
| `storage/short-01-river/` | The first TikTok short (2026-10-18), `out/short-01-river_tiktok.mp4`; README has the rebuild commands |
| `storage/ai-problem-first-edu/` | Newest film (explainer, 2026-10-14) and the template for the next one; README has the rebuild commands |
| `storage/love-19-vs-29-doc/`, `storage/maps-traffic-edu/` | **Gone** (2026-10-14, no backup). Their films were never delivered anywhere else |
| `storage/khmer-film/` | Shared voice rules, **recreated 2026-10-14**: `khmer_speech.py` (respellings, joined repeats), `khmer_phrasing.py` (calm pauses). `listen_list.py` is not rebuilt: each film's `make_review.py` writes a listening page instead |
| `storage/channel-brand/` | Logo, banner, tools |
| `storage/tasks/` | Delivered copies of finished films (`final-1.mp4`) |
| `Claude outputs/` | Loose previews and thumbnails |
| `config.toml` | API keys, default voice (gitignored) |
| `app/`, `webui/`, `cli.py` | The stock MoneyPrinterTurbo app |

`storage/`, `config.toml` and `CLAUDE.md` are gitignored; the dossiers (`docs/video-plan-*/research.md`), the skill, `Claude outputs/`
and this `docs/channel/` folder are not committed.
**Nothing from the films is backed up** (Prompt 12).

## Commands

```bash
./webui.sh                                   # stock web app: http://127.0.0.1:8501 (or ask Claude to start "webui")
.venv/bin/python main.py                     # stock API: http://127.0.0.1:8080/docs
python3 storage/ai-problem-first-edu/make_review.py   # listening page: every narrated line with a player
node storage/ai-problem-first-edu/render.mjs --out storage/ai-problem-first-edu/out/frames   # then python3 build.py
df -h /System/Volumes/Data                   # check free disk before any build
```

Narration runs VoiceStudio's own Python directly (`$HOME/Library/Application Support/VoiceStudio/runtime/project/.venv/bin/python`);
the VoiceStudio server on port 3900 is only needed when the web app speaks with the `voicestudio` voice. The full rebuild
sequence for a documentary is in `storage/love-19-vs-29-doc/README.md`.

This is a 16 GB Mac. Narration peaks near 10 GB: **no Chrome, previews or ffmpeg jobs while it runs.** After a build, delete
`out/frames`, `out/shots` and `out/scenes` (about 3 GB for a documentary).

## Open items

1. **Rotate the Unsplash keys.** `docs/info/info.md` (with the secret key) is committed and on the public fork.
2. **Listen check waiting on you:** `storage/ai-problem-first-edu/review/review_voice.html` (24 of 45 lines starred). The love and Google Maps films no longer exist on disk.
3. **Next documentary:** needs stock footage and music added to the rebuilt pipeline before it can match the old ones.
4. **Music:** the bundled tracks in `resource/songs/` have an unclear licence. Swap or publish without music.
5. **Voice artist's permission** for the cloned narrator, before monetising.
6. **Disk is 97% full (13 GB free)** and the early film build folders are gone. Only the finished films in `storage/tasks/`
   survive. The crop-circles film was never delivered, so it is lost; its dossier remains.
7. **Upstream merge** (2026-10-14) is local only, not pushed. `edge-tts` in the venv is 7.2.7; the new pin is 7.3.1.

## Writing a good prompt

Give Claude five things and it can start without questions:

1. **The idea**: a topic line, a link, or a feeling ("a mother waiting at a bus stop").
2. **The feeling** the viewer should leave with.
3. **Length and shape**: vertical short, 3-minute explainer, 8-minute documentary.
4. **What to avoid**: sources to skip, people not to name, things already covered.
5. **Where to stop**: "dossier only", "script in Khmer and English first", "stop before building".

Claude remembers this workspace between sessions, so you don't need to explain the pipeline. A first prompt like
"Documentary on [topic], feeling [x], about 8 minutes, stop at the dossier" is enough.
