# Prompts

Paste into Claude Code in this folder. Replace every `[bracket]`; delete lines you don't care about.
Claude remembers the workspace, so these stay short. Background and rules: [README.md](README.md).

Every prompt ends with a **stop point** on purpose: you approve the story, then the Khmer, then the film.

---

## 0. I have an idea but don't know the format

```
Idea: [one sentence, link, or feeling].
Which format fits best: short, 3-minute explainer, emotion piece or documentary? Give one recommendation with the reason,
what it would cost in time, and what you'd need from me. Don't start anything.
```

---

## Start a film

### 1. Research a documentary (topic or article)

```
New documentary for the channel.
Topic: [one line, or path / link to the article]
Feeling I want the viewer to leave with: [wonder / longing / pride / …]
Length: [about 8 minutes]
Skip: [sources, people or angles to avoid]
Run the doc-research skill and stop at the dossier (next docs/video-plan folder). Tell me the heart in one sentence, the
proposed title, and the 3–5 strongest moments. Don't script or voice anything until I say go.
```

### 2. Build the film from an approved dossier

```
Build the film from docs/video-plan-[NN]/research.md.
Copy storage/love-19-vs-29-doc to storage/[name]-doc as the template. Use khmer_speech.py and khmer_phrasing.relax() from the
start, with short sentences. Check free disk space first.
Stop after narration: run listen_list.py and give me the lines to listen to (starred first) with film times. Don't build
the film until I send corrections.
```

### 3. A 3-minute animated explainer

```
Make a 3-minute Khmer education video: "[the question, e.g. Why does a plane stay in the air?]".
1. Light research: at most 3 agents, the sources that matter most. Write the heart and the 5–6 claims we will make.
2. Write the animated page in the same format as storage/maps-traffic-edu/source/maps-traffic.html (8–10 scenes, each
   section.scene with data-id, data-dur, data-label, data-say). Dark theme, channel palette, Khmer on screen, no logos or
   screenshots of other companies: redraw in our style. Screenshot two scenes for me before the voice.
3. Copy storage/maps-traffic-edu to storage/[name]-edu and render. Use khmer_speech.py and relax() for the voice.
Stop before publishing and give me the lines to listen to.
```

### 4. A vertical short (under 60 s) cut from a finished film

```
Cut a 9:16 short (1080x1920, under 60 s) from [storage/…/out/…_km.mp4].
Pick one moment: a hook in the first 3 seconds, one feeling, ending on the line people remember. Tell me the 2–3 candidates
you considered and why you chose one. Burn in Khmer captions with the Chrome overlay method (not ffmpeg text filters), keep
the logo end card under 2 s. There is no vertical pipeline yet: build it as storage/[name]-short/ so the next short is one command.
Show me one frame and the caption layout before encoding.
```

### 5. An emotion short from scratch (45–90 s)

```
Make a [60 s] vertical emotion short in Khmer.
Idea: [a feeling, person or moment, e.g. a mother waiting for a bus that doesn't come]
One story, one feeling, no statistics. Write warm, simple Khmer in short sentences, then show me the script in Khmer and
English before voicing anything. Visuals: [Cambodian places, hands, backs, silhouettes]; licensed footage only, no readable
logos, no faces unless licensed. Music: calm, and tell me the licence of whatever you pick.
Build it like Prompt 4: storage/[name]-short/, reusable.
```

### 6. A mystery, alien or ancient-world story

```
Documentary on [UFO case / alien story / ancient mystery].
Tell it from the believer's side, as the channel does: the witnesses, the strange evidence, the questions nobody has answered.
A hoax or natural explanation gets one line at most. No invented quotes, nothing shameful about a real named person without
a source. Include any link to Cambodia or Southeast Asia.
Run doc-research and stop at the dossier. Give me the heart, the best witness, and the single strangest detail.
```

---

## Continue and fix

### 7a. Pick up an unfinished film

```
Pick up [love-19-vs-29-doc / maps-traffic-edu]. Read your notes on it, check what is actually on disk, and tell me exactly
what is left (listen check, voice fixes, music, thumbnails, upload notes). Don't rebuild anything yet.
```

### 7b. Apply the newer voice fixes to the Google Maps film

```
Wire khmer_speech.py and relax() into storage/maps-traffic-edu/script_km.py (joined repeats, calm phrase stops, short
sentences). Keep the current narration as v1. Re-record, then give me an A/B clip of the lines that changed. Back up
config.toml before running any tests.
```

### 8. Send listen-check corrections

```
Listen-check corrections for [film]:
- line [id] at [mm:ss]: "[word as written]" sounds like "[what I hear]", should sound like "[how it should sound]"
- line [id]: [a repeated word sounds disconnected]
Try spellings with tts_try.py, add the winner to PRON (captions keep the correct spelling), re-record only the changed lines,
rebuild, run qc, and update the YouTube chapters. Keep the old take so I can roll back.
```

### 9. The voice feels wrong

```
The narration of [film] feels [hurried / flat / too dramatic / noisy] around [mm:ss–mm:ss] (or: everywhere).
Measure it against the reference recording instead of guessing, show me the numbers, try the fix, and give me an A/B clip.
You can't hear it, so tell me what you measured and what only my ears can decide.
```

---

## Publish

### 10. YouTube package

```
YouTube package for [film]: 3 title options under 100 characters (one feeling-led, one search-led), Khmer and English
description with sources and asset credits, chapters from the real timeline, tags, and three 1280x720 thumbnails (A/B/C)
with no faces, in the channel palette. Use storage/love-19-vs-29-doc/youtube/ as the template and put the pre-publish
checklist at the top of youtube.md.
```

### 11. Pre-publish check

```
Pre-publish check for [film]: every clip, photo and song against the end-card credits and its licence; readable logos or
faces in the contact sheets (look at them, don't trust a helper's report); the music; the voice artist's permission; the
"Altered or synthetic content" answer; anything in the dossier's "Handle with care". Give me a short list of what only I can do.
```

---

## Housekeeping

### 12. Space, backup, keys, updates

```
Disk: check free space, then list what in storage/ I can delete (out/frames, shots, scenes, caches) with sizes.
Delete nothing until I pick.
```

```
Backup: copy docs/video-plan-*, docs/channel, .claude/skills, storage/channel-brand, storage/khmer-film and the finished films
in storage/tasks to [path]. Tell me the total size first.
```

```
I rotated the Unsplash keys. Update config.toml, git rm docs/info/info.md, add it to .gitignore, and update your notes.
Show me the diff; don't push.
```

```
Sync upstream: fetch harry0703/MoneyPrinterTurbo, show what is new, merge into main, bump pinned dependencies in the venv,
run the tests with config.toml backed up first. Don't push.
```

### 13. A quick video in English or another language (stock app)

```
Start the web app and make a 9:16 video in [English] about [topic], [45 s], with stock footage and subtitles. Tell me where
the file lands. This is for non-Khmer videos: the app's subtitle renderer breaks Khmer letters.
```
