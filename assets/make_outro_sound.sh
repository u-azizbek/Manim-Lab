#!/usr/bin/env bash
#
# Regenerate the one-word outro sting.  macOS `say` does the voicing, ffmpeg
# normalises it and tapers the tail so it does not click.
#
#   ./assets/make_outro_sound.sh                 # default voice
#   VOICE=Ava WORD="Neuro Edu Z" ./assets/make_outro_sound.sh
#
# Try `say -v '?' | grep en_` to see the installed voices.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VOICE="${VOICE:-Samantha}"
WORD="${WORD:-Neuro Education}"
RATE="${RATE:-165}"
OUT="$HERE/neuroeduz.wav"
RAW="$(mktemp -t outro).aiff"
trap 'rm -f "$RAW"' EXIT

say -v "$VOICE" -r "$RATE" -o "$RAW" "$WORD"

# Lift the level, then fade the last 120 ms
ffmpeg -v error -i "$RAW" \
    -af "volume=6dB,afade=t=out:st=0.62:d=0.14" \
    -ar 44100 -ac 2 -y "$OUT"

echo "wrote $OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
