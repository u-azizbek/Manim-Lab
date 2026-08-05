#!/usr/bin/env bash
#
# Render a manimgl scene from anywhere in the repo.
#
# Fixes the two things that bite when calling manimgl directly:
#   * `from manim_imports_ext import *` needs the repo root on PYTHONPATH
#   * manimgl is not on PATH; it lives inside the conda env
#
# It also knows about ShortsScene, whose `sections` list lets you render a
# single beat of a video instead of the whole thing.
#
# Examples
#   ./render.sh -s reveal_answer -q draft -p _2026/Limits/subfactorial_limit.py
#   ./render.sh _2026/Limits/subfactorial_limit.py
#   ./render.sh -s reveal_answer _2026/Limits/subfactorial_limit.py
#   ./render.sh -s hook,show_table -q draft _2026/Limits/subfactorial_limit.py
#   ./render.sh -p _2026/matrix/matrix_power_2024.py MatrixPower2024
#   ./render.sh -l _2026/matrix/matrix_power_2024.py

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Override either of these from the environment if your setup differs
MANIMGL="${MANIMGL:-/usr/local/Caskroom/miniconda/base/envs/manim/bin/manimgl}"
CONFIG="$REPO_ROOT/custom_config.yml"

bold=$(tput bold 2>/dev/null || true)
dim=$(tput dim 2>/dev/null || true)
red=$(tput setaf 1 2>/dev/null || true)
green=$(tput setaf 2 2>/dev/null || true)
reset=$(tput sgr0 2>/dev/null || true)

die() { echo "${red}error:${reset} $*" >&2; exit 1; }

usage() {
    cat <<EOF
${bold}Usage:${reset} ./render.sh [options] <file.py> [SceneName]

${bold}Options:${reset}
  -s, --sections LIST   Render only these section methods (comma or space
                        separated).  Requires a ShortsScene subclass; other
                        sections are filled in statically so any one renders
                        on its own.
  -q, --quality NAME    shorts  1080x1920  portrait, final  (default)
                        draft    540x960   portrait, fast iteration
                        4k      2160x3840  portrait, high res
                        hd      1920x1080  landscape
                        or an explicit WIDTHxHEIGHT
  -S, --silent          Render without the outro sound (sets NO_SOUND=1)
  -p, --preview         Open a live window instead of writing a file
      --presenter       Preview, pausing at every wait() until you hit space
  -e, --embed LINE      Drop into the interactive shell at this line number
  -o, --open            Reveal the finished video in Finder
  -l, --list            List the scenes (and their sections) in the file
  -n, --dry-run         Print the manimgl command without running it
  -h, --help            Show this message

${bold}Note:${reset} options come before the file, and each option that takes a
value must be followed by that value:
  ${dim}./render.sh -s reveal_answer -p _2026/Limits/subfactorial_limit.py${reset}

${bold}Environment:${reset}
  MANIMGL   path to the manimgl executable
            (currently: $MANIMGL)
EOF
}

sections=""
silent=false
quality="shorts"
preview=false
presenter=false
embed_line=""
open_after=false
list_only=false
dry_run=false

# Catch `-s -p reveal_answer`, where the value of -s silently swallows the
# next flag and everything downstream goes wrong
need_value() {
    case "${2:-}" in
        ""|-*) die "$1 needs a value, got '${2:-}'. Options come before the file: try --help" ;;
    esac
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -s|--sections) need_value "$1" "${2:-}"; sections="$2"; shift 2 ;;
        -q|--quality)  need_value "$1" "${2:-}"; quality="$2"; shift 2 ;;
        -e|--embed)    need_value "$1" "${2:-}"; embed_line="$2"; shift 2 ;;
        -S|--silent)   silent=true; shift ;;
        -p|--preview)  preview=true; shift ;;
        --presenter)   preview=true; presenter=true; shift ;;
        -o|--open)     open_after=true; shift ;;
        -l|--list)     list_only=true; shift ;;
        -n|--dry-run)  dry_run=true; shift ;;
        -h|--help)     usage; exit 0 ;;
        -*)            die "unknown option: $1 (try --help)" ;;
        *)             break ;;
    esac
done

[[ $# -ge 1 ]] || { usage; exit 1; }

# Resolve the file before moving to the repo root, so relative paths work
# from whatever directory you happen to be standing in
file="$1"; shift
if [[ ! -f "$file" ]]; then
    case "$file" in
        *.py) die "no such file: $file" ;;
        *)    die "no such file: $file -- did you mean it as an option value? Options come before the file: try --help" ;;
    esac
fi
file="$(cd "$(dirname "$file")" && pwd)/$(basename "$file")"

scene="${1:-}"

# Read class names and their `sections` list straight out of the source.
# Parsing beats importing here: it stays fast and cannot be broken by an
# import-time error in the scene file.
probe() {
    python3 - "$file" "$1" <<'PY'
import ast, sys

path, mode = sys.argv[1], sys.argv[2]
tree = ast.parse(open(path).read())

for node in tree.body:
    if not isinstance(node, ast.ClassDef):
        continue
    sections = []
    for statement in node.body:
        targets = getattr(statement, "targets", [])
        if any(getattr(t, "id", None) == "sections" for t in targets):
            try:
                sections = ast.literal_eval(statement.value)
            except ValueError:
                sections = []
    if mode == "names":
        print(node.name)
    else:
        print(node.name)
        for section in sections:
            print(f"    - {section}")
PY
}

if $list_only; then
    echo "${bold}Scenes in $(basename "$file")${reset}"
    probe sections | sed 's/^/  /'
    exit 0
fi

if [[ -z "$scene" ]]; then
    found="$(probe names)"
    if [[ "$(echo "$found" | wc -l)" -eq 1 && -n "$found" ]]; then
        scene="$found"
    else
        echo "${red}error:${reset} several scenes in $(basename "$file"); name one:" >&2
        echo "$found" | sed 's/^/  /' >&2
        exit 1
    fi
fi

case "$quality" in
    shorts) resolution="1080x1920" ;;
    draft)  resolution="540x960" ;;
    4k)     resolution="2160x3840" ;;
    hd)     resolution="1920x1080" ;;
    *x*)    resolution="$quality" ;;
    *)      die "unknown quality: $quality (shorts, draft, 4k, hd, or WIDTHxHEIGHT)" ;;
esac

[[ -x "$MANIMGL" ]] || MANIMGL="$(command -v manimgl || true)"
[[ -n "$MANIMGL" ]] || die "manimgl not found; set MANIMGL to its path"

# manimgl opens a live window whenever -w is absent.  Its own -p is presenter
# mode (pause at every wait), which is a different thing.
cmd=("$MANIMGL" "$file" "$scene" -r "$resolution")
if [[ -n "$embed_line" ]]; then
    cmd+=(-se "$embed_line")
elif $preview; then
    if $presenter; then
        cmd+=(-p)
    fi
else
    cmd+=(-w)
fi

echo "${dim}scene      $scene${reset}"
echo "${dim}resolution $resolution${reset}"
[[ -n "$sections" ]] && echo "${dim}sections   $sections${reset}"
$silent && echo "${dim}sound      off${reset}" || true

if $dry_run; then
    echo "SECTIONS='$sections' NO_SOUND='$($silent && echo 1)' PYTHONPATH='$REPO_ROOT' ${cmd[*]}"
    exit 0
fi

marker="$(mktemp)"
trap 'rm -f "$marker"' EXIT

cd "$REPO_ROOT"
NO_SOUND="$($silent && echo 1 || true)" SECTIONS="$sections" \
    PYTHONPATH="$REPO_ROOT" "${cmd[@]}"

# Nothing was written to disk in these modes
if $preview || [[ -n "$embed_line" ]]; then
    exit 0
fi

# manimgl only reports the output path through wrapped log output, so rather
# than scrape it, look for what appeared while we were rendering
base="$(sed -n 's/^[[:space:]]*base:[[:space:]]*"\(.*\)"/\1/p' "$CONFIG" | head -1)"
base="${base:-$HOME/Movies/Manim/}"
video="$(find "${base%/}/videos" -name "$scene.mp4" -newer "$marker" 2>/dev/null | head -1)"

if [[ -z "$video" ]]; then
    echo "${green}done${reset}  (no new file under ${base%/}/videos)"
    exit 0
fi

duration="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$video" 2>/dev/null || true)"
echo "${green}done${reset}  $video${duration:+  ${dim}(${duration%.*}s)${reset}}"
if $open_after; then
    open -R "$video"
fi
