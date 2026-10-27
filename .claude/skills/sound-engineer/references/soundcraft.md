# SoundCraft CLI on the VM

SoundCraft is a DAW installed on the VM from the GitHub arm64 `.deb`. It ran as 0.11.0 and 0.12.1 in October 2026. `se.py` drives it headlessly; this page is for hand edits and debugging. If `soundcraft-cli --version` jumps a minor version, re-check the gotchas below with a quick render.

## Contents
- Commands
- Script format
- Plugins and parameters
- Verified gotchas
- Reading a .scraft session

## Commands

```bash
soundcraft-cli script FILE.sc [--in S.scraft] [--save S.scraft] [--bounce OUT.wav]   # one `command.id {json}` per line
soundcraft-cli run --cmd engine.plugins           # every plugin with parameter ids, ranges, units, defaults
soundcraft-cli describe mix.insert                # one command's parameters
soundcraft-cli commands [FILTER]                  # all ~480 commands
soundcraft-cli info FILE                          # audio file or session summary
soundcraft-cli plugins                            # short plugin list
```

Useful commands in scripts:

| Command | Parameters |
|---|---|
| `session.new` | `{name, sample_rate: 48000, bit_depth: 24}` |
| `file.import_audio` | `{path}`. Creates a track named after the file stem |
| `track.new` | `{kind: audio\|aux\|master, format: mono\|stereo, name}` |
| `mix.insert` | `{track, slot: 0..9, plugin, params}`. A track holds 10 inserts |
| `mix.insert_params` | `{track, slot, params}`. Unknown ids are errors |
| `mix.new_bus` / `track.input` / `mix.send` | `{name}` / `{tracks, input: bus}` / `{track, bus, level_db, pre_fader}`. For aux sends |
| `mix.volume` | `{track, db}` |
| `automation.set_point` | `{track, param: volume\|pan\|plugin:a:<id>, at, value}` |
| `clip.gain` | `{clips?, db \| delta_db}` |
| `audiosuite.process` | `{process: normalize\|gain\|reverse\|<plugin id>, params, tracks, start, end}` |
| `file.bounce_mix` | `{path, format: wav\|aiff\|flac, bit_depth: 16\|24\|32f, start, end, source: main\|bus, dither}` |

The `--bounce` flag (or `file.bounce_mix`) prints a JSON line such as `{"lufs":-14.1,"peak_db":-2.0,"true_peak_db":-1.9,"seconds":20.66,...}`. Use these numbers directly instead of re-measuring.

## Script format

```
session.new {"name":"take","sample_rate":48000,"bit_depth":24}
file.import_audio {"path":"/home/ubuntu/CHR/sound-engineer/jobs/take/studio/work/voice.wav"}
mix.insert {"track":"voice","slot":0,"plugin":"eq_7band","params":{"hpf_on":1,"hpf_freq":60,"hpf_slope":0}}
mix.insert {"track":"voice","slot":1,"plugin":"compressor","params":{"threshold":-17,"ratio":2.5,"attack":12,"release":100}}
track.new {"kind":"master","format":"stereo"}
mix.insert {"track":"Master 1","slot":0,"plugin":"gain","params":{"gain":7.9}}
mix.insert {"track":"Master 1","slot":1,"plugin":"maximizer","params":{"threshold":0,"ceiling":-2.0,"release":50}}
```

Errors print as `file.sc:LINE: command: message`. `se.py` treats any such line as a failure.

## Plugins and parameters

Choice parameters take the index number. Parameters you leave out keep their defaults.

| Plugin | Parameters (range, default) |
|---|---|
| `eq_7band` | `input_gain`/`output_gain` ±24; `hpf_on` 0/1, `hpf_freq` 10–2000 (80), `hpf_slope` 0:6 1:12 2:18 3:24 dB/oct; `low_shelf_freq` 20–1000 (100) `_gain` ±24 `_q` 0.3–2; `low_mid_freq` 20–2000 (250) `_gain` `_q` 0.1–10; `mid_freq` 100–8000 (1000) `_gain` `_q`; `high_mid_freq` 500–20000 (4000) `_gain` `_q`; `high_shelf_freq` 1000–20000 (8000) `_gain` `_q` 0.3–2; `lpf_on`, `lpf_freq` 1000–20000 (18000), `lpf_slope` |
| `eq_1band` | `type` 0 Peak 1 LowShelf 2 HighShelf 3 HighPass 4 LowPass 5 Notch 6 BandPass; `freq` 20–20000; `gain` ±24; `q` 0.1–10; `output_gain` |
| `compressor` | `threshold` −60–0 (−20); `ratio` 1–100 (4); `attack` 0.01–300 ms (10); `release` 5–3000 ms (100); `knee` 0–24 (6); `makeup` 0–40; `sc_hpf_on`, `sc_hpf_freq` 20–500; `limiter` 0/1; `lookahead` 0–10 ms; `mix` 0–100 % |
| `expander_gate` | `threshold` −80–0 (−40); `ratio` 1–100 (100 = gate); `range` 0–80 dB (80); `attack` 0.01–100 ms; `hold` 0–2000 ms; `release` 1–4000 ms |
| `de_esser` | `freq` 2000–16000 (6000); `range` 0–40 dB (10); `threshold` −60–0 (−30); `listen` 0/1 |
| `maximizer` | `threshold` −30–0 (0); `ceiling` −30–0 (−0.3); `release` 1–1000 ms (50) |
| `channel_strip` | gate (`gate_on`, `gate_threshold`, `gate_range`, `gate_release`), comp (`comp_on`, `comp_threshold`, `comp_ratio`, `comp_attack`, `comp_release`, `comp_makeup`), EQ (`eq_on`, `hpf_on`, `hpf_freq`, `low_gain/freq`, `mid_gain/freq/q`, `high_gain/freq`), `input_gain`, `output_gain` |
| `room_reverb` / `plate_reverb` | `mix` %; `pre_delay` 0–250 ms; `decay` 0.1–20 s; `size` %; `damping` 1000–20000 Hz; `diffusion` %; `width` %; `low_cut` 20–1000 Hz |
| `mod_delay` | `time` 1–2000 ms; `feedback` ±99 %; `mix` %; `mod_rate` 0.01–10 Hz; `mod_depth` %; `lpf` 500–20000 Hz |
| `chorus` | `rate` 0.05–5 Hz; `depth` %; `delay` 5–30 ms; `feedback` 0–90 %; `mix` %; `spread` % |
| `flanger` / `phaser` | rate, depth, delay/stages, feedback, center, mix |
| `saturator` | `drive` 0–36 dB; `bias` %; `tone` 1000–20000 Hz; `mix` %; `output` −24–12 |
| `lofi` | `bits` 1–24; `sample_rate` 500–48000; `noise` %; `mix` % |
| `rectifier` | `mode` 0 half 1 full wave; `mix`; `output`. Exciter: generates harmonics above a band-limited source |
| `pitch_shifter` | `semitones` ±24; `cents`; `mix` |
| `gain` / `trim` | `gain` dB (−96–24 / −96–12); trim adds `invert` |
| `dc_offset_removal` | `cutoff` 1–40 Hz |
| `signal_generator` | `waveform` 0 sine 1 square 2 saw 3 triangle 4 white 5 pink; `freq`; `level` dB |
| `dither` | `bits` 0:16 1:20 2:24; `noise_shaping` |

## Verified gotchas

These were measured on this VM in October 2026.

- **Pan law.** A mono track reaches the stereo mix 3 dB down. A maximizer on the voice track with ceiling −1.5 bounced at −4.5 dB peak. Put the limiter on the master.
- **The master is always `Master 1`.** `track.new {"kind":"master","name":"X"}` ignores the name.
- **A bounce never runs past the last clip.** `--end` and `file.bounce_mix {"end":…}` can't add a reverb tail. Pad the input with silence first (`apad=pad_dur=N`), at the end only.
- **Bounces are always stereo.** `fold_down` accepts only `"stereo"`. For a mono deliverable from a mono track, L = R, so take one channel losslessly: `ffmpeg -af pan=mono|c0=c0`. Don't use `-ac 1`, whose downmix matrix is less predictable.
- **Out-of-range values are clamped silently.** For example, `eq_7band` HPF tops out at 2000 Hz. `se.py` checks every value against `engine.plugins` and reports clamps. For a higher high-pass or low-pass, stack `eq_1band` (type 3/4, up to 20 kHz).
- **High-pass filters raise peaks** through phase rotation, not loudness. On a 336 Hz voice: 60 Hz/6 dB +0.4 dB, 100 Hz/12 dB +1.4 dB, 150 Hz/18 dB +2.6 dB. That headroom later costs limiting.
- **The compressor at 12 ms attack acts like slow gain riding.** It lowers peaks and loudness about equally, so the peak-to-loudness ratio stays put. For peak control use attack ≤ 1 ms with `lookahead` 2–5 ms, which brought the PLR from 15 dB to about 12.5 dB.
- **De-esser threshold doesn't line up with measured high-band levels.** Tune it by measuring (`se.py` does). `range` caps the reduction: on one voice, range 4 could only move sibilance about 2 dB, range 8 about 6 dB.
- **The maximizer limits sample peaks.** True peak can overshoot by about 0.1 dB, so set the ceiling about 0.5 dB under the true-peak target.
- **Noise beds.** A `signal_generator` insert on an empty audio track plays for the whole session (cassette and radio beds).
- **`--inspect` shows `params: null`** even when params are set. Check the saved `.scraft` JSON instead.
- **Import resamples to the session rate (48 kHz).** Bounces write WAV/AIFF/FLAC only. Make MP3/M4A with ffmpeg (libmp3lame and aac are available on the VM).
- **`--save` copies the audio into `Audio Files/`** next to the `.scraft`. Keep sessions in `work/session/` so `out/` stays clean.
- **ffmpeg on the VM is 4.4.** `afftdn` removes only about 6 dB of broadband hiss, and its `sample_noise` command had no effect here. No `arnndn` model is installed. Pair `afftdn` with SoundCraft's `expander_gate`: together they measured −49 → −68 dBFS in the pauses.

## Reading a .scraft session

A session is JSON: `tracks[] → mixer → inserts[]`. Each insert is `{plugin, params, bypass}` with the full parameter set; empty slots are `null`. Clips sit under `tracks[].playlists[].clips[]`, with `start` and `length` in samples at 48 kHz, plus `gain_db` and fades. `sources[]` points at `Audio Files/`. To dump a chain:

```bash
ssh ubuntu-vm 'python3 -c "
import json,sys; d=json.load(open(sys.argv[1]))
for t in d[\"tracks\"]:
    print(t[\"name\"], t[\"kind\"], t[\"mixer\"][\"volume_db\"])
    for i in t[\"mixer\"][\"inserts\"]:
        if i: print(\"   \", i[\"plugin\"], i[\"params\"])
" SESSION.scraft'
```

To tweak by ear, open a session in the SoundCraft GUI on the VM desktop (the UTM window, which has audio).
