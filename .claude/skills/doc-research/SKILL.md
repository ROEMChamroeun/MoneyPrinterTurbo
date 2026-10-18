---
name: doc-research
description: Research a documentary before any script, voice or footage work, to find the story that moves people. Traces where the story came from, gathers the human details, emotional moments and, for UFO, alien and ancient-mystery topics, the strongest case that we are not alone, then writes a story dossier (the heart, story spine, key moments, Khmer script lines, names in Khmer, visuals and rights) to docs/video-plan-NN/research.md. Use whenever the user wants to make, plan or start a documentary or explainer video for the channel, or hands over an article, Facebook post, link or topic to turn into a video — even if they never say "research".
---

# Documentary research

*My Little Space | រឿងគួរដឹង* tells stories people feel. Viewers stay for love, longing, courage, loss and wonder, not for a list
of corrected facts: a film that stops to fact-check every line loses its audience. This skill runs **before production** and digs
for what makes a story move: the people, their moments, and the mystery.

## Channel voice

- **Heart first.** Every film is about people: what they loved, wanted, feared and lost. Find that before anything else.
- **Wonder over debunking.** A mystery stays a mystery. The channel believes alien life exists and that we are not alone. On UFO,
  alien, crop-circle and ancient-mystery topics, tell the story from that side: the witnesses, the strange evidence, the questions
  no one has answered. Hoaxes and "natural explanations" are not the story. Leave them out, or when one is too famous to skip, give
  it one line and turn back to what it doesn't explain.
- **Facts serve the story.** Don't check every claim, and a dramatic detail from the article can stay. Research is for finding
  richer, more vivid material, not for stripping the article down.

## Input and output

The input is one of:
- a source article: a file (usually `docs/video-plan-NN/<title>.md`, often in Khmer), a URL, or pasted text;
- a topic with no article.

Write the dossier next to the article as `docs/video-plan-NN/research.md`. For a topic with no plan folder yet, create the next
`docs/video-plan-NN/`. Put today's date at the top.

## Workflow

### 1. Find the heart

Read the whole article and list:
- the people, and what each one wants, loves or fears;
- the moments that carry a feeling: a first sighting, a letter, a loss, a promise, a strange night;
- the mystery: what happened that no one can explain;
- why a Cambodian viewer would care, and any link to Cambodia or Southeast Asia.

Then write one sentence on what the story is really about. Not the topic, the feeling: "a farmer who saw something in his field
and spent the rest of his life being doubted."

Keep short Khmer excerpts beside English renderings so the dossier maps back to the Khmer lines the script will use. Convert Khmer
numerals (០–៩) to digits in the English rendering so they are searchable.

For a topic with no article, write questions instead: who lived this, what did they see or lose, what is the most beautiful or
strangest detail, what is still unanswered.

### 2. Trace the origin

Do this yourself, before spawning agents. The original is usually the richest version of the story: the subject's own words, real
names, real photos, and the details the reposts dropped.

Search distinctive details (names plus unusual numbers or phrases) in English, and in Thai, Vietnamese or Chinese if the English
trail is thin, with `scout.py` (see "Gathering sources"). Look for first-hand accounts first: the witness's own interview, the
person's own posts and talks, the letter, the diary.

Record the chain: original → reposts → this article. The last hop (the exact Facebook or TikTok post the Khmer writer used) usually
can't be fetched. Say so.

### 3. Research in parallel

Spawn at most five research agents, in one message so they run at the same time, each with `model: "sonnet"`: reading and
searching don't need a bigger model, and you write the dossier yourself. Follow up on origin leads while they work. If you are
yourself running as a subagent, run them in the foreground: you may not be notified when background agents finish.

Each brief must stand alone. Include:
- the topic, the heart sentence and the origin trail you found;
- what the agent owns;
- today's date and the plan folder (`docs/video-plan-NN`);
- the channel voice and the limits below;
- the "Gathering sources" section below, word for word;
- every constraint the user gave you (paths to avoid, sources to skip). Agents only know what the brief tells them;
- the return format, and that it should return findings and not write files.

A typical split (for a small topic, fold Context into People and story):

| Agent | Owns |
|---|---|
| People and story | The human side: who they were, what they loved and lost, first-hand testimony, letters, interviews, family memories; small, vivid details that make a scene |
| Mystery and wonder | The strongest witnesses, evidence and unanswered questions, best first. For alien topics, the best case that they are real and have been here. Famous counter-explanations only so the script can answer them in a line |
| Context and Cambodia | The background a Khmer viewer needs to follow the story, the order of events, and any link to Cambodia or the region |
| Visuals and rights | Real imagery that exists and its licence (CC-licensed talks, press kits, Wikimedia Commons; the subject's own photos are usually not reusable without permission); scenes that must be illustrative stock, with Pixabay/Unsplash search queries |
| Names and terms | Every person, company, product and place: correct spelling, role, and how Khmer speakers say it, written in Khmer script; technical terms with a natural Khmer rendering. Start from the spellings already in earlier documentaries' `SAY` tables (`storage/*/script_km.py`) so a name sounds the same across the channel, and flag any change |

Return format for every agent: item id, the detail, why it moves or surprises, then for each source the URL, publisher, date, and a
quote under 15 words or a close paraphrase.

If subagents are unavailable, work through the same slices yourself, one after another.

### Gathering sources

Pages are what make research expensive: every page an agent prints stays in its context and is re-read on every later turn. The
crop-circles run printed 2.9 million characters of pages over 1,000 tool calls. `scout.py` keeps pages on disk and prints only what
you ask for:

```bash
S=.claude/skills/doc-research/scripts/scout.py; P=docs/video-plan-NN
uv run $S search --plan $P "query one" "query two" "query three"  # many queries per call, one line per result
uv run $S search --plan $P --news "query"                          # news results, with dates
uv run $S fetch  --plan $P 1a2b3c 4d5e6f https://…                 # ids from search, or URLs; one line per page
uv run $S find   --plan $P "witness" "light"                       # only the matching paragraphs, across all pages
uv run $S find   --plan $P "Oliver" "orbs" --all --ids 1a2b3c      # a paragraph must hold every term; one page
uv run $S list   --plan $P                                         # what is saved
```

- **Batch.** Put a theme's queries in one `search` and the promising results in one `fetch`.
- **Read through `find`.** Never print a whole page (`cat`, `curl` to the screen, Read without a line range). Open a saved page
  (`$P/sources/<id>-*.txt`) with Read and a line range only when `find` shows the passage is worth it.
- **Shared cache.** All agents save to the same folder, so `find` also searches pages another agent fetched. The folder is
  git-ignored: cached copies are research material, not ours to publish.
- **Awkward sources are handled.** X posts come through fxtwitter; blocked or paywalled pages (Medium, Cloudflare) through older
  Wayback snapshots; GitHub READMEs as raw files; YouTube as captions with `[m:ss]` times (auto-captions are marked: check quotes
  against the audio); PDFs with `[p. N]` page numbers. Facebook and TikTok are skipped: search around them.
- **When scout is thin.** DuckDuckGo finds little for Khmer-language queries; use WebSearch for those and for any search that comes
  back thin. WebSearch allows 200 calls per session, shared by every agent, so spend them there. Use WebFetch for a page `fetch`
  can't get. Both may be deferred tools: load them before use.

### Limits that still apply

The story doesn't need proving, but a few things can still hurt a viewer, get a video taken down, or bring a complaint from a real
person:

- **Real, named people.** Imagined thoughts and scenes are fine when the narration frames them ("imagine her that night, alone in
  the field…"). Don't present an invented quote as something a real person said, and don't say a real person did something shameful
  or criminal without a source. If their age, ethnicity, nationality or family isn't published, don't guess it from a name or photo.
- **Advice a viewer might act on.** A cure, an investment, a dangerous place or stunt needs a real source, or it stays out. YouTube
  removes medical misinformation, and a viewer can get hurt.
- **Footage.** Use only material the channel may use (see Visuals). A stock actor can play "a farmer" but is never named as the
  real person.

Note anything that touches these in the dossier's "Handle with care" section.

### 4. Write the dossier

When the agents return, pick the strongest material: the moments that give you a feeling, the witness who sounds most real, the
detail no one else used. Then write `research.md` with this structure:

```markdown
# Research: <English title> (<Khmer title>)

As of <YYYY-MM-DD> · Source: `<path or URL>` · Origin: <the original source, one line>

## The heart
2–4 sentences: what the story is really about, the feeling the viewer should leave with, and the proposed title (Khmer and English).

## Story spine
1. Hook (first 15 seconds): the image or question that stops the scroll.
2. The people: who they are and what they want.
3. The turn: what happened.
4. The mystery or the cost: what it meant, what is still unanswered.
5. Ending: the line the viewer remembers.
For each beat: what happens, the feeling, and source numbers where there are any.

## Moments
The 5–10 most vivid details found, best first: a witness's words, a strange measurement, a letter, a photo. Each with why it works
and where it came from.

## The case for
For mystery and alien topics: the strongest witnesses, evidence and open questions, best first. Then any famous counter-explanation
and the one line the script answers it with.

## Script lines (Khmer)
Lines in natural, warm Khmer, ready for `script_km.py`, keyed to the story beats:
- Hook: «…»

## Timeline
| Date | Event | Sources |

## Names and terms
| Name or term | Who or what | Khmer spelling (as spoken) | Sources |

Spellings built from letter-name rules rather than Khmer media precedent are marked †; run them through the documentary's
`asr_check.py` once narrated.

## Visuals
- Real material: item, where it lives, licence, whether we can use it
- Stock to illustrate: scene → Pixabay/Unsplash query
- Mood: the feeling of each part of the story (music, colour, pace)

## Handle with care
Anything that touches the limits above, and how the script handles it. "None" is fine.

## Sources
1. Publisher — "Title", date. URL `[scout id]`

## For the YouTube description
The 3–6 sources a curious viewer would enjoy following.
```

### 5. Report

In chat, give: the heart in one sentence, the proposed title, the three to five strongest moments, anything in "Handle with care",
and the dossier path. Add one line on what the research cost, from
`python3 .claude/skills/doc-research/scripts/usage.py` (tool calls, page characters and cache reads per agent). The crop-circles
run, before `scout.py`, is the baseline: 7 agents, 1,008 tool calls, 2.9 million page characters, 162 million cache-read tokens.

Production builds from the **Story spine**, **Moments** and **Script lines**. The article is not a list of mistakes to fix: when a
documentary's `script_km.py` checks its captions against the article, the article's dramatic details may stay. Keep a `NOT` table
(claims that fail the check if they return) only for "Handle with care" items.

When the script is voiced, the narrator (a voice clone) can misread rare words and pauses at every space in the spoken text, and the speech-recognition
check cannot hear either. So production uses the shared rules in `storage/khmer-film/khmer_speech.py` (repeated words joined, a `PRON` table of
respellings) and, after narration and before the film is built, runs `storage/khmer-film/listen_list.py` and asks the user to listen to the lines it
lists. In the dossier's "Names and terms" table, flag any rare Khmer word, loan word or foreign name the voice might misread, so production can respell it (`PRON` or `SAY`) and check it.
