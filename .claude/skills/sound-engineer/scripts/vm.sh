#!/usr/bin/env bash
# Mac-side helper for the sound-engineer toolkit on the Ubuntu VM.
#
#   vm.sh sync                     copy scripts + presets to the VM, create the venv if missing
#   vm.sh push FILE...             upload audio to the VM inbox; prints the VM paths
#   vm.sh se ARGS...               run se.py on the VM (paths relative to the workspace)
#   vm.sh pull PATH... DEST_DIR    download files (paths relative to the workspace) into DEST_DIR
set -euo pipefail

VM=ubuntu-vm
ROOT=/home/ubuntu/CHR/sound-engineer
SK="$(cd "$(dirname "$0")/.." && pwd)"
UV=/home/ubuntu/.local/bin/uv

abs() { case "$1" in /*) echo "$1" ;; *) echo "$ROOT/$1" ;; esac; }

case "${1:-}" in
  sync)
    ssh "$VM" "mkdir -p $ROOT/tools $ROOT/jobs $ROOT/inbox $ROOT/refs"
    rsync -a --delete "$SK/scripts" "$SK/assets" "$VM:$ROOT/tools/"
    ssh "$VM" "cd $ROOT && { [ -x .venv/bin/python ] || { $UV venv -q .venv --python 3.11 && $UV pip install -q --python .venv/bin/python numpy scipy; }; } && chown -R ubuntu:ubuntu $ROOT && echo synced: \$(soundcraft-cli --version)"
    ;;
  push)
    shift
    for f in "$@"; do  # cat over ssh: survives spaces and Khmer in file names
      ssh "$VM" "cat > $(printf '%q' "$ROOT/inbox/$(basename "$f")")" < "$f"
      echo "inbox/$(basename "$f")"
    done
    ssh "$VM" "chown -R ubuntu:ubuntu $ROOT/inbox"
    ;;
  se)
    shift
    ssh "$VM" "cd $ROOT && .venv/bin/python tools/scripts/se.py $(printf '%q ' "$@")"
    ;;
  pull)
    shift
    dest="${!#}"
    mkdir -p "$dest"
    for p in "${@:1:$#-1}"; do
      ssh "$VM" "cat $(printf '%q' "$(abs "$p")")" > "$dest/$(basename "$p")"
      echo "$dest/$(basename "$p")"
    done
    ;;
  *)
    sed -n '2,8p' "$0"
    exit 1
    ;;
esac
