---
name: tiktok-short
description: Make a Khmer TikTok short (30–45 s, 1080x1920) for the user's TikTok account @my_space_ha, end to end. Find what is trending on Khmer TikTok, write the plan (hook, Khmer script, scenes) to docs/video-plan-NN/plan.md, build it with the khmer-voice-artist clone plus EffectCraft motion graphics and a FilmCraft edit on the Ubuntu VM, and hand over the posting package (caption, hashtags, cover frame, time). Use whenever the user wants a TikTok, short, reel or vertical video, asks what is trending, asks why their TikTok gets no views, or wants a caption or hashtags for a post — even if they only say "make a short".
---

# TikTok short

The first one was built on 2026-10-18: "Cambodia has a river that flows backwards" (Water Festival trend).
- Plan: `docs/video-plan-10/plan.md`.
- Build: `storage/short-01-river/`. Its README has every command, plus the gotchas.
- A copy of its code lives in `template/` next to this file, because `storage/` is gitignored and has been wiped before.

## The account and what it taught us

`@my_space_ha` ("It's my space", bio "Learning & useful little things"). Its first three posts got 0–6 views. The review is
`docs/channel/tiktok-review-2026-10-18.md`. Every short follows its lessons:

- **Original work only.** Use our own narration over our own motion graphics. Use licensed photos and clips only for mood. No reposts, no dubs of a whole video without permission, and no songs uploaded as "original sound".
- **One topic:** learning and useful little things, for a Khmer audience.
- **Length:** 30–45 s, with the strongest line in the first 2 seconds.
- **Frame:** fill the 9:16 frame edge to edge. No letterbox, no blurred sides.
- **Posting time:** 11:00–13:00 or 19:00–22:00 Cambodia time, one post a day. Never in the middle of the night.
- **Music:** none in the export. The user adds a calm TikTok library sound at 5–10% when posting.
- **No politics.** For example, the 2026 Phnom Penh Water Festival was cancelled because of the Thai border crisis, and the short never mentions it.

## Stop points

1. After the plan, show the topic choice and the Khmer script, then **wait**. The user may answer "start build"; that approves the plan as written.
2. After the build, deliver the MP4 with an honest list of what still needs the user:
   - **A Khmer read and listen.** Claude writes all the Khmer and cannot hear the voice.
   - The voice owner's permission.
   - TikTok's AI-generated content label, because the voice is a clone.

## 1. Find what is trending

TikTok's own trend tools don't cover Cambodia:
- Studio "Inspiration" has no Cambodia region.
- Creative Center has no Cambodia either.
- Google Trends KH is mostly football.

What works is searching Khmer TikTok directly, in the user's logged-in Chrome:

- **Connect** with the `pw-attach` skill (`playwright-cli attach --cdp=chrome`).
  - Work in **your own new tab**: `tab-new`. Read only, never post or like.
  - When done, close your tab, then `detach`. Never `close`.
  - If Chrome stops answering, it is waiting for the user to allow remote debugging again. Don't wait on it. Logged-out TikTok won't load tag pages.
- **Search:** `https://www.tiktok.com/search/video?q=<url-encoded Khmer term>`, then `playwright-cli -s=chrome snapshot --filename=<scratchpad>/sN.yml`.
- **Rank** with `python3 scripts/tiktok_cards.py cards sN.yml`. The number on a card is **likes**, and the date shows freshness: `13h ago`, `2d ago`, `M-D`, or `YYYY-M-D` for older posts.
- **Seed terms:** តើអ្នកដឹងទេ, ចំណេះដឹងទូទៅ, រឿងគួរដឹង, ចិត្តវិទ្យា, គន្លឹះសុខភាព, អង្គរវត្ត, មនុស្សភពក្រៅ, plus the next Khmer event or holiday. Examples: បុណ្យអុំទូក (Water Festival), ភ្ជុំបិណ្ឌ, ចូលឆ្នាំ, ឯករាជ្យ.
- **What it found on 2026-10-18:**
  - Festival news was rising fast: 12K–38K likes in 1–4 days.
  - Psychology does well all year: 20K–53K likes.
  - "Did you know" posts get steady likes: 5.8K in 2 days.
  - Health tips are crowded by doctors.
  - Aliens were cold on TikTok, under 500 likes this year.

Pick a topic that is **rising now**, fits the bio, can be told with our own graphics, and stays out of politics.
A good topic can also be explained once and still be true next year. Check web sources for any number that goes on screen
(prefer Wikipedia, JICA, government or news sites). Use ranges where sources disagree.

## 2. Write the plan

Write `docs/video-plan-NN/plan.md`, using the next free number. Follow `docs/video-plan-10/plan.md`:

- The trend table, with the search, what gets likes, how fresh it is, and whether it fits.
- What is known about the event, with sources.
- The pick and why.
- The script as a table: Khmer | meaning | on screen.
- Look and sound.
- Posting.
- A 2–3 part series if the topic carries one.
- Production steps.

Length rule: the clone reads about 12–14 Khmer characters a second, so about 480 characters makes about 40 s. Keep
sentences short. End on a question that invites comments, such as "which province will you celebrate in?".

## 3. Build

Copy the template into a new folder:

```bash
cp -R .claude/skills/tiktok-short/template storage/short-NN-<name>
cp -n .claude/skills/tiktok-short/template/khmer-film/*.py storage/khmer-film/   # shared voice rules, if missing
```

Change these for the new story:

- **`script_km.py`:** the lines `(id, scene, Khmer with caption marks)`. The marks are:
  - `/` starts a new caption block.
  - `|` starts a new row with no pause.
  - ` | ` starts a new row where the voice may breathe.
  - `*` at the start of a row makes it big and yellow.
  - Write numbers as Khmer words in the text.
- **`build_jsx.py`:**
  - The `T` key times, looked up by caption-row text with `mk("…")`.
  - The `FOOT` list: file, in and out times, camera move, credit.
  - The story-specific JSX block. The map section belongs to the river story; replace it with this story's motion graphics.
  - The caption, cut-flash, footage, credit, comment-bubble and bold-pass code is generic, so keep it.
- **`tools/map_data.py`:** only if the story needs a map (Natural Earth, public domain).

Then run, from the new folder:

```bash
VS="$HOME/Library/Application Support/VoiceStudio/runtime/project/.venv/bin/python"
python3 script_km.py && "$VS" narrate.py && "$VS" tools/align_km.py && ../../.venv/bin/python timeline.py
python3 tools/commons.py search "<topic>"; python3 tools/commons.py sheet titles.txt sheet.jpg   # pick by eye
python3 tools/pixabay.py sheet "<query>" sheet.jpg; python3 tools/pixabay.py get "<query>" <id> assets/pixabay/x.mp4
python3 vm_build.py build && python3 vm_build.py stills 0.6 3 6 …       # ~20 times, then look at a contact sheet
uv run --with numpy --with scipy python tools/sfx.py                     # synthesised sound design, no licences
python3 vm_build.py render                                               # ~23 min for 43 s on the VM's 4 cores
python3 vm_edit.py                                                       # FilmCraft: mix + export -> out/*_tiktok.mp4
```

Check before handing it over:
- **Stills:** `python3 tools/sheet.py out/sheet.jpg 7 270 out/stills/*.png`, then fix what looks wrong and rebuild.
- **Streams:** `ffprobe` should show 1080x1920, 30 fps, H.264 and AAC.
- **Loudness:** `ffmpeg -af ebur128=peak=true` should read about -14 LUFS, with true peak at or below -1.5 dBFS.
- **Frames:** pull about 15 frames from the final MP4 into one sheet and look at every one.

**Gotchas from the first build** (details in the template README):
- EffectCraft draws Google Sans at weight 400 unless a text animator offsets `wght`. That only works through the CLI chain `run text.animatorFontAxes … prop.set …` after the script. `vm_build.py build` does it for every text layer.
- Shape vertices are relative to the layer. Parent map layers to a null with anchor [0,0].
- Dash offset rising moves dashes toward the path start.
- CC Rainfall needs Screen blending.
- In shape Contents, the first group draws on top.
- Some Commons JPEGs carry EXIF rotation. Make them upright first.
- FilmCraft's `file.import` returns item ids in the order of `paths`. `file.exportMedia` takes `loudnessLufs`.
- `pgrep -f "<pattern>"` over ssh matches its own command line, so a wait loop on it never ends. Poll for the output file instead.

## 4. The posting package

Give the user a caption ready to paste, written for Khmer viewers. The Khmer is Claude's, so ask the user to read it.

```
តើអ្នកដឹងទេ? <the surprising fact in one line> <emoji>

<two short sentences: how it works, why it matters to Khmer people>

<the question that ends the video>? សរសេរប្រាប់ខ្ញុំនៅខាងក្រោម 👇

<5 hashtags>

រូបថត៖ <Commons authors> / Wikimedia Commons (<licences>)
វីដេអូ៖ Pixabay | ផែនទី៖ Natural Earth
```

**Hashtags.** Rank them with `python3 scripts/tiktok_cards.py tags s*.yml` over the trend searches, then pick 5:
1. The event or topic tag.
2. Its short variant.
3. The specific subject.
4. `#ចំណេះដឹងទូទៅ`, the biggest Khmer knowledge tag.
5. `#cambodia`.

Optional: `#DidYouKnow`. Skip like-begging tags (`#សុំ❤️ម្នាក់មួយ`, `#ជួយចុចfollow`) and tags for things the video does not
show. `#fyp` is optional, because nothing shows it brings views. Tell the user plainly that watch time, the first 2
seconds, the cover and replies in the first hour matter more than hashtags.

Also tell them:
- **Cover:** the frame with the hook's big yellow caption.
- **AI label:** on.
- **Sound:** a TikTok library sound at 5–10%.
- **Posting time:** 11:00–13:00 or 19:00–22:00.
- **Comments:** reply to every one in the first hour.
