# short-01-river: "Cambodia has a river that flows backwards" (TikTok, 9:16)

Plan and sources: `docs/video-plan-10/plan.md`. Output: `out/short-01-river_tiktok.mp4` (1080x1920, 30 fps,
H.264 + AAC, -14 LUFS, about 43 s). Voice: VoiceStudio clone `khmer-voice-artist` (f9c08f52).

The picture is made in **EffectCraft** on the Ubuntu VM (`ssh ubuntu-vm`): an animated Natural Earth map
(Cambodia, the Mekong, the Tonle Sap river and lake), the lake flooding x5, rain, a flow arrow that flips,
festival photos and clips with camera moves, and Khmer kinetic captions in Google Sans 700. The edit, audio mix
and export are done in **FilmCraft** on the VM.

## Rebuild (from this folder, on the Mac)

```bash
VS="$HOME/Library/Application Support/VoiceStudio/runtime/project/.venv/bin/python"
python3 script_km.py                         # check the Khmer lines (speech problems, rough length)
"$VS" narrate.py [--only l03,l07]            # record lines (cached by text; ~3 min for all 8)
"$VS" tools/align_km.py [l03,l07]            # when each character is spoken -> narration/align.json
../../.venv/bin/python timeline.py           # line starts, caption row times, narration_full.wav
uv run --with pyshp --with shapely --with numpy python tools/map_data.py <natural-earth dir>   # vm/map.json
python3 vm_build.py build                    # build_jsx.py -> VM: run the JSX, bold all text -> vm/short.ecproj
python3 vm_build.py stills 1.6 6 13.9 27.4   # check frames (half size) in out/stills/
uv run --with numpy --with scipy python tools/sfx.py   # sound design -> sfx.wav (synthesised, no samples)
python3 vm_build.py render                   # EffectCraft ProRes render on the VM (out/short_picture.mov there)
python3 vm_edit.py                           # FilmCraft: sequence, mix, export -> out/short-01-river_tiktok.mp4
```

Natural Earth 10m files used: admin_0_countries, admin_1_states_provinces, rivers_lake_centerlines, lakes
(from naciscdn.org, public domain). Map pixels: equirectangular around 104.6E 12.6N, 330 px per degree.

## Files

- `script_km.py`: Khmer words, scenes and caption marks (`/` new block, `|` new row, `*` big yellow row).
- `build_jsx.py`: writes `vm/short.jsx` (all scenes, timings from `timeline.json`); `vm/times.json` for the sound.
- `tools/commons.py`, `tools/pixabay.py`: search/contact sheets/downloads with author + licence JSON beside each file.
- `assets/commons/*.jpg` are made upright (EXIF rotation applied): EffectCraft and PIL disagree on it otherwise.

## Gotchas found while building

- EffectCraft draws Google Sans at 400 unless a text animator offsets the `wght` axis; that only works through
  the CLI `run text.animatorFontAxes ... prop.set ...` chain after the script (`app.executeCommand` from JSX
  does not take the parameters). `vm_build.py build` does it for every text layer.
- Shape layer vertices are relative to the layer position: set position and anchor to [0,0] (children of the
  MapCam null, whose anchor is [0,0], so world = cam position + cam scale x map px).
- Dash offset increasing moves dashes towards the path start.
- CC Rainfall draws on its solid: use Screen blending for transparent rain.
- In shape Contents the first group draws on top (add the bubble's dots before the bubble).

## Credits (put them in the TikTok description too)

Photos from Wikimedia Commons: Jeece69 (CC BY-SA 4.0), Vanna (CC BY-SA 3.0), Codas (CC BY-SA 4.0),
Willuconquer (CC BY-SA 4.0), Photo Dharma (CC BY 2.0). Clips from Pixabay (Pixabay Content License):
yourdreamclips, Janhom_Footage, Engin_Akyurt. Map data: Natural Earth.

## Before publishing

A native Khmer read of `script_km.py` and a listen (all Khmer was written by Claude), the voice owner's
permission for `khmer-voice-artist`, the AI-generated content label on TikTok (cloned voice).
