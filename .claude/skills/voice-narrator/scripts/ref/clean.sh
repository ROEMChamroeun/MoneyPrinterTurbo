#!/bin/bash
# Clean a voice source for cloning, on the Mac: music out (RoFormer), room out (de-reverb), mono 48 kHz.
#
#   clean.sh SOURCE OUT_DIR [--df]
#
# SOURCE is any audio or video file. Writes, resuming whatever already exists:
#   OUT_DIR/full.wav            stereo 44.1 kHz copy of the source
#   OUT_DIR/s1/vocals.wav       RoFormer bleedless vocal stem   (other.wav = the music)
#   OUT_DIR/s2/deverb.wav       UVR-DeEcho-DeReverb of the stem (reverb.wav = what it took out)
#   OUT_DIR/s2/deverb48.wav     the same, mono 48 kHz: the usual input for phrases.py and build_ref.py
#   OUT_DIR/s3/df48.wav         with --df only: DeepFilterNet on deverb48. Check endings.py before using it:
#                               DF can snap fade-outs to silence and the clone then learns hard stops.
# Models are kept in ~/.cache/audio-separator-models (downloaded on first use, about 1 GB). RoFormer runs at
# about 2x real time on MPS (a 7-minute episode takes about 15 min) and uses most of the Mac's memory, so don't
# run it while VoiceStudio or narrate.py is generating.
set -euo pipefail
[ $# -ge 2 ] || { sed -n '2,15p' "$0"; exit 1; }
src=$1
out=$2
df=${3:-}
models=${AUDIO_SEPARATOR_MODEL_DIR:-$HOME/.cache/audio-separator-models}
sep=$HOME/.local/bin/audio-separator
mkdir -p "$out/s1" "$out/s2" "$models"

[ -s "$out/full.wav" ] || ffmpeg -hide_banner -loglevel error -y -i "$src" -vn -ac 2 -ar 44100 "$out/full.wav"

if [ ! -s "$out/s1/vocals.wav" ]; then
  "$sep" "$out/full.wav" -m mel_band_roformer_kim_ft2_bleedless_unwa.ckpt --model_file_dir "$models" \
    --output_dir "$out/s1" --output_format WAV \
    --custom_output_names '{"Vocals": "vocals", "Instrumental": "other", "Other": "other"}'
fi

if [ ! -s "$out/s2/deverb.wav" ]; then
  "$sep" "$out/s1/vocals.wav" -m UVR-DeEcho-DeReverb.pth --model_file_dir "$models" \
    --output_dir "$out/s2" --output_format WAV --single_stem "No Reverb" \
    --custom_output_names '{"No Reverb": "deverb", "Reverb": "reverb"}'
fi

[ -s "$out/s2/deverb48.wav" ] || ffmpeg -hide_banner -loglevel error -y -i "$out/s2/deverb.wav" -ac 1 -ar 48000 \
  "$out/s2/deverb48.wav"

if [ "$df" = "--df" ] && [ ! -s "$out/s3/df48.wav" ]; then
  mkdir -p "$out/s3"
  "$HOME/.local/share/deep-filter/deep-filter" -D -o "$out/s3" "$out/s2/deverb48.wav"
  mv "$out/s3/deverb48.wav" "$out/s3/df48.wav"
fi

ls -l "$out"/s*/*.wav
