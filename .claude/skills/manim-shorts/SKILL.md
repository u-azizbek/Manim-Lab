---
name: manim-shorts
description: House playbook for making viral 9:16 YouTube Shorts for the @neuroeduz math channel with manimgl in this repo. Use it EVERY time the user asks to make, create, animate or render a short, shorts video, reel or vertical video, or to turn a math problem, theorem, puzzle, proof, physics idea or screenshot into a video, even if they never mention this skill. Also use it whenever the user names a style from its catalogue (card hook, formula hook, figure hook, silent, narrated, voice-over, transcript, captions). Follow it unless the user explicitly says to change something. Covers the named styles, the grid-safe thumbnail frame, the beat sheet and pacing, the 9:16 safe zones, the palette, how to explain each step, narrated captions with a saved transcript, upload metadata, the custom toolkit (MockTestShort, GeoFigure, StepListMixin, hooks, NarrationMixin, BrandOutroMixin), the manimgl traps, and the render and QA loop.
---

# @neuroeduz Shorts playbook

This skill distills the ~50 shorts in `_2026/` and `Calculus Mock Tests/`, plus reference designs
from viral channels, into one method. **Follow it by default.** The user's explicit instruction
overrides any rule here, but only for the thing they asked to change.

Supporting files (read them when you need them, not up front):
- `reference/toolkit.md` covers the API of every base class and helper, including `hooks` and `NarrationMixin`. Read it before writing code.
- `reference/gotchas.md` lists manimgl traps that fail silently. Read it before writing code, and again when something looks wrong.
- `templates/` holds four verified, runnable starting points, one per named style (section 2).

---

## 1. Non-negotiables

1. **Portrait 9:16, 1080x1920.** Subclass `ShortsScene` (directly or through a kit). Never call
   `to_edge` or use `FRAME_*` constants. Use `pin_to_top` and explicit `y * UP` instead.
2. **No audio in the render.** Never `add_sound`. A *silent* short carries everything on screen.
   A *narrated* short gets its voice later, from the transcript this render writes (section 9).
3. **Branded ending.** Mix in `BrandOutroMixin` (`MockTestShort` already includes it), and make
   `"outro"` the last section.
4. **Frame 0 is the thumbnail**, built with `self.add(...)`, never animated in, and laid out inside
   the grid-safe band |y| ≤ 4.8 (section 4).
5. **Every step says why.** Each step that uses a rule or theorem names it in 1–2 short sentences
   (`note()` when silent, `say()` when narrated). Never show bare algebra jumps.
6. **The maths is verified before it is animated.** Solve it, check it numerically, and write
   the solution plus a `Checked:` line in the file's header comment.
7. **Figures are exact by construction.** Derive coordinates from the problem's constraints
   (module-level constants, `GeoFigure`). Never eyeball or trace positions. If a picture is
   meant to show a count (pieces, crossings), verify that the drawing really shows it.
8. **Every section renders on its own** (`./render.sh -s <section> file.py`). Shared state
   goes through `set_state` / `lazy`.
9. **Length is 10–58 s** (the repo averages about 50 s). The hard cap is 60 s unless the user asks
   for longer or it is a pure simulation piece.
10. **Don't commit or push** unless asked. `output/` is git-ignored. Never commit videos.

## 2. Style catalogue: the names the user will use

A short is **one hook + one voice mode** (+ a body format from section 3). When the user names
any of these, use exactly that. When they don't, pick by the "default when" column.

### Hooks (what frame 0 looks like)

| Name | Look | Default when | Builder | Template |
| --- | --- | --- | --- | --- |
| **card hook** | Colourful title, problem card, figure blown up, huge `= ?` | A worded problem with a figure (olympiad, geometry, mock test) | `card_hook()` | `templates/problem_short.py` |
| **formula hook** | Title, the problem itself huge in the middle (`lim n!/!n`), a teaser question under it | The problem *is* one striking expression: a limit, integral, sum, equation | `formula_hook()` | `templates/formula_hook_short.py` |
| **figure hook** | Colourful word-by-word title above (not at the very top), the figure big and centred, optional teaser | The picture is the hook: visual puzzles, theorems, proofs without words, simulations | `figure_hook()` | `templates/narrated_short.py`, `templates/visual_short.py` |

### Voice modes

| Name | What it means | Default |
| --- | --- | --- |
| **silent** | No voice ever. Small grey `note()` sentences name each rule, the step list carries the maths | **yes** |
| **narrated** | Big bold two-line captions with yellow/blue/purple highlights (`say()`), paced for an AI voice. The render saves the transcript (`.txt`, `.srt`, `.json`) next to the video | when the user says narrated / voice / voice-over / transcript / captions |

Prompts the user may write: *"formula hook short: lim n!/!n"*, *"figure hook, narrated: Moser's
circle"*, *"card hook, silent"*, *"narrated version of square_shear_area"*. To convert an existing
short to narrated, replace its `note()` calls with `say()` lines and mix in `NarrationMixin`.

## 3. Pick the body format

| Content | Base class | Closest examples |
| --- | --- | --- |
| Olympiad / puzzle problem with a figure (most common) | `MockTestShort`, `test = ""`, custom `pose` thumbnail | `_2026/Geometry/square_shear_area.py`, `orthic_triangle_5_12_13.py` |
| Named theorem / property + example | `BrandOutroMixin, StepListMixin, ShortsScene` | `_2026/Integrals/king_property.py`, `_2026/Geometry/viviani_theorem.py` |
| Single-expression problem (limit, sum, integral) | `BrandOutroMixin, StepListMixin, ShortsScene` | `_2026/Limits/subfactorial_limit.py`, `templates/formula_hook_short.py` |
| Proof without words / pure visual | `BrandOutroMixin, ShortsScene` | `_2026/Series/sum_of_cubes.py` |
| Physics / simulation / eye candy | `BrandOutroMixin, ShortsScene` | `_2026/Physics/pendulum_chaos.py`, `burgers_vortex.py` |
| Beginner vs Pro / Noob vs Expert | `BrandOutroMixin, SplitScreenScene` | `_2026/Limits/power_sum_ratio.py` |
| Geometry with a title and steps, no card | `GeometryShortScene` | `_2026/Geometry/kangaroo_angle_140.py` |

For **narrated**, put `NarrationMixin` first: `class X(NarrationMixin, MockTestShort)` or
`class X(NarrationMixin, BrandOutroMixin, ShortsScene)`.

**Where files go:** `_2026/<Topic>/<snake_case_name>.py`, using the current year folder.
Topics: `Geometry`, `Integrals`, `Limits`, `Series`, `Puzzles`, `Physics`, `Graphs`, `matrix`,
`Functions`, `Fourier`. Make a new topic folder only if none fits.
**One scene class per file** (so `render.sh` picks it automatically). Name it in CamelCase after
the content (`SquareShearArea`, `TelescopingFloorSum`).

## 4. Frame 0: the thumbnail

Shorts are swiped in under a second, so frame 0 must stop the thumb *and* work as the cover image.
**The channel's Shorts grid crops frame 0 to about 3:4 around the centre**, so whatever sells the
video goes inside **|y| ≤ 4.8** (`HOOK_BAND`). The hook builders in `custom/hooks.py` enforce this.
Nothing important sits at the very top or bottom of frame 0.

Rules for every hook:
- **Title**: 2–4 words, ≤ 24 characters, built on curiosity, a promise, a twist or a famous name.
  House and reference examples: *"No Logs Needed!"*, *"The Pattern That Breaks"*, *"FREE WIFI"*,
  *"King's Property"*, *"Proof without words"*, *"COUNTERINTUITIVE"*, *"Ever Seen a 2-Sided Polygon?"*.
  Never use a dry topic label ("Geometry problem 3"). Use `hook_title()`: bold italic, colours per
  word (`mode="words"`), or `mode="gradient"` / `"solid"`.
- **Teaser**: a short question that opens a loop the video closes: *"Does this even converge?"*,
  *"Can you see the answer?"*, `2, 4, 8, 16, ?`. Put a yellow `?` on the unknown.
- **The figure**, when there is one, is big, colourful and *complete*: shaded regions, glowing
  circles (`glowing()`), every chord drawn. It is the visual promise of the video.
- **Brand**: the problem card already carries the logo. A `brand_row()` (badge + @neuroeduz) is
  optional and goes *outside* the band (y ≈ -5.8) if used at all.
- **Hold** frame 0 for 2.0–2.6 s (a narrated short holds it for its first, voice-only line), then
  clear the title and teaser *first* and move into the working layout in one 0.9–1.2 s move
  (`ReplacementTransform` the thumbnail figure into the working one). The templates show each hook's transition.

## 5. Beat sheet and pacing

| Beat | Time | What happens |
| --- | --- | --- |
| hook | 3–6 s | Thumbnail hold, then settle into the working layout |
| 3–5 body beats | 6–12 s each | One idea per section: build, *aha* move, name the rule, the step lines |
| Payoff | 3–4 s | Answer boxed in yellow + `FlashAround`, hold 1.0–1.5 s |
| `outro` | ~4.7 s | `BrandOutroMixin.outro` (fixed, don't restyle) |

- **The aha visual is the point of the channel.** Each short needs at least one motion that *is*
  the argument, not decoration: a rotation that carries one triangle onto another, a shear that
  keeps area, a reflection, pieces rearranged, blocks filling a bar, a point dragged while a
  quantity stays fixed. Prefer the geometric argument whenever one exists, and show 2–3 methods
  when they are short (`square_shear_area.py` has three).
- **Retention devices** (use 1–2): the open-loop teaser answered at the very end; a pattern that
  breaks (1, 2, 4, 8, 16, *31*); a running tally or sequence row across the top; a counter
  ticking up; a "guess" in grey that gets crossed out and replaced in yellow.
- **Something changes at least every ~2 s.** No dead `wait` longer than 1.6 s except the
  thumbnail hold and the final hold.
- **Run times**: 0.3–0.6 s for fades and small reveals, 0.7–1.2 s for writes and transforms,
  1.3–2.0 s only for the aha move itself (`Rotate`, a `ValueTracker` sweep).
- **Silent reading time**: a note needs about 0.12 s per word on top of its 0.6 s fade-in, and at least 1.0 s.
  The `note()` default (`wait=1.6`) suits 8–14 words. Narrated timing is automatic (section 9).
- **Payoff ritual**: highlight each partial result where it was found, `TransformFromCopy` them
  into the final expression, then `self.conclude(...)` (or box + `FlashAround`). The answer
  should be visibly *assembled*, not just appear.

## 6. Workflow

1. **Understand and solve.** If the problem came as an image, transcribe it exactly. Ask only
   if it is truly ambiguous. Otherwise proceed.
2. **Verify numerically** with the manim env's Python, using a scratch script in the scratchpad:
   `PYTHONPATH=$PWD /usr/local/Caskroom/miniconda/base/envs/manim/bin/python script.py`.
   Check the answer, every intermediate value you show, and every geometric claim you animate.
3. **Pick the hook, voice mode and body format** (sections 2–3), then copy the matching template
   and read the closest existing short. It is the best style reference.
4. **Write the beat sheet** before any code: the hook title + teaser, the thumbnail composition,
   3–6 sections with one idea each, the *aha visual*, the note or caption text for each rule, and
   the payoff. Narrated: write the whole script first (section 9).
5. **Assign the palette**: one colour per quantity, kept everywhere (section 8).
6. **Write the file** (section 7 has the anatomy), including the `upload` dict (section 10).
7. **Iterate in draft**: `./render.sh -q draft -s <section> <file>`, then a full draft render.
   Make a contact sheet and *look at it* (section 11). Fix overlaps, cut-offs, dead air and timing.
8. **Final render** at the default quality: `./render.sh <file>`, then report (section 11).

## 7. File anatomy

```python
from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/<Topic>/<file>.py
#
# <Problem statement, plain text.>
# <Full solution in prose: every step the video shows, with the reason.>
# <How the figure is constructed, if there is one.>
# Checked: <the numeric verifications you ran>.

SIDE = 3.0                      # constants derived from the problem's constraints
PTS = {...}                     # exact construction, at module level
FIG_CENTER = 1.6 * UP

SIDE_C = "#58C4DD"              # palette: one named colour per quantity / role
...


def helper(...):                # pure geometry helpers (foot, meet, crossing ...)
    ...


class MyShort(MockTestShort):   # or (NarrationMixin, MockTestShort) for narrated
    """One-line summary of the idea."""

    test = ""
    step_font_size = 40          # tune class attrs, not base classes
    problem_tex = R"..."
    sections = ["pose", "beat_one", "beat_two", "finish", "outro"]
    upload = dict(title="...", description="...", hashtags=["#math", "#shorts"], pinned_comment="...")

    # Layout / builders   make_*() build, get_*() wrap self.lazy(...)
    # Sections            each starts with self.get_card() / self.get_figure()
```

Style rules (from CLAUDE.md): raw strings `R"..."` for all TeX; blank lines completely empty;
build `VGroup`s declaratively; use `color_gradient`; prefer `.arrange/.next_to/.move_to` over coordinate
arithmetic; helpers are named `get_*` / `make_*`; comments are terse, say *why*, and sit above the
block they describe.

## 8. Layout and visual style

**Frame**: x ∈ [-4, 4], y ∈ [-7.11, 7.11] (8 × 14.22 units).

| Zone | y range | Contents |
| --- | --- | --- |
| Frame 0 band | **-4.8 → 4.8** | everything in the thumbnail (grid crop) |
| Top strip | 5.0 → 6.6 | after frame 0 only: pinned card or header, a sequence/tally row |
| Figure | ≈ 4.5 → -1 | the working figure, width ≤ 7 |
| Steps / notes | figure bottom - 0.6 → -5.0 | `add_step` lines, `note()` |
| Captions (narrated) | centre -3.4 to -3.6, two lines | `say()` captions, under the figure |
| **Danger** | **< -5.0** | YouTube's title/channel overlay. Keep everything important above it |

Keep content within |x| ≤ 3.65 (step lines `step_max_width ≈ 6.9`). In the lower half,
keep important labels away from the right edge (x > 3.2), where the like/comment buttons sit.

**Typography**

| Element | Size |
| --- | --- |
| Hook title | `hook_title` 54–64, bold italic (`Avenir Next`) |
| Teaser | `teaser_text` 44 bold, or `Tex` 72–96 for a sequence / `= ?` |
| Card statement | 40–46 (`card_font_size`) |
| Step lines | 36–42 (`step_font_size`) |
| Notes (silent) | `Text` 28, `GREY_B` (`note()` default) |
| Captions (narrated) | `Avenir Next` HEAVY 62, uppercase, black backstroke |
| Point / vertex labels | 30–40 |
| Final answer | 44–60, `YELLOW`, boxed |

**Colour**: black background. One saturated colour per *quantity*, used consistently in the
figure, its labels, its TeX (`t2c=`) and its caption highlights. Colours carry meaning: the same
colour means the same thing. `YELLOW` is reserved for the answer, its box and the key caption phrase.
Mock-test roles: `SETUP_COLOR` (`#7FB3FF`), `RULE_COLOR` (`#5BD98A`), `RESULT_COLOR` (`YELLOW`).
House hues: `#58C4DD` cyan, `#5BD98A` green, `#FFD166`/`#FFE14D` gold, `#FF9F43` orange,
`#FF6B9A`/`#FF6BD6` pink, `#C39BFF`/`#A78BFA` violet, `PURPLE_LIGHT` (`#A15FE4`, the logo),
`#FF6B6B` red, `#4ECDC4` teal; `#E8ECF4` or `GREY_B` for the main figure lines.
**Strokes** are 3.5–5 for the figure, 2–2.5 for chords, dashed helpers and altitudes, and 6–9 for
emphasis. **Fills** use opacity 0.15–0.25 for background regions and 0.35–0.5 for highlighted pieces. Put fills
*behind* strokes (`bring_to_back`).

## 9. Explaining

### Silent (default)

- **Name the rule** before or as it is used: `self.note("Partial fractions split each term in two.")`.
  1–2 lines, ≤ 12 words per line, plain language. For names with subscripts use a
  `Tex` note (`tex_note` pattern in `orthic_triangle_5_12_13.py`).
- **Only results earn a permanent line.** Scaffolding is rewritten in place with
  `replace_step(...)`, and transient reasoning goes in `note()`, which clears itself.
- **Point at what you talk about.** `Indicate`, `FlashAround`, or `ShowCreationThenDestruction`
  on the segment, angle or region a step refers to, at the moment the step appears.
- When the step list gets long, `clear_steps()` between beats, or lift a key line to the top
  (`lift_to_top` in `telescoping_floor_sum.py`).
- **Headers for multiple methods**: a bold coloured `Text` line ("Method 2: the leg rule") added
  as a step (see `header()` in `square_shear_area.py`).

### Narrated

`NarrationMixin` (`custom/narration.py`) replaces `note()` with spoken captions. Every caption
is one line of the voice-over script.

- **API**: `self.say(text, *animations)` shows the caption, plays the animations under it and
  holds until the voice would finish. `self.say(text, wait=False)` → several plays → `self.hold()`
  covers longer beats. `self.narrate(text)` is voice-only (no caption): use it over the thumbnail
  and wherever the screen already shows the words. `self.unsay()` clears the caption.
- **Highlights**: `{y:...}` yellow for the key phrase of the line (one per caption), `{b:...}`
  blue for the object being named, `{p:...}` neuro purple for the twist. A highlighted phrase is
  kept on one line when it fits: *"Obviously, this divides {y:the circle into two.}"*.
- **Write for the ear**: short sentences, ≤ ~10 words per caption, two lines at most (a longer one logs
  a "Caption runs to N lines" warning, so split it). Spell numbers and symbols the way they are said; when
  the caption should show symbols, pass the spoken form: `say("For six points: {y:1 + 15 + 15 = 31.}",
  speak="For six points, that is one plus fifteen plus fifteen: thirty-one.")`.
- **Script shape**: hook line (voice-only, over frame 0) → setup in the viewer's words ("Put two
  points on a circle...") → the obvious expectation → the twist → *why*, naming the rule → the
  payoff line. The outro speaks `outro_line` automatically ("Follow for a new math puzzle every day.").
- **Pacing** comes from `speech_wps = 2.6` (about 155 words a minute). If the user's AI voice is
  faster or slower, set `speech_wps` on the class and re-render. The video and transcript stay in step.
- **The transcript is saved on every file render**, next to the video:
  `<Scene>.txt` (the voice script, one line per caption), `<Scene>.srt` (with timings, so players
  show it as subtitles and voice tools can align to it), `<Scene>.json` (everything, including
  `partial: true` when only some sections were rendered). Re-render to regenerate it. The source
  holds the lines too. Tell the user where these files are when you report.
- Step lines (`add_step` Tex) still work alongside captions. Keep them above the caption zone.

## 10. Upload kit

Set `upload = dict(title=..., description=..., hashtags=[...], pinned_comment=...)` on every
scene. The render writes `<Scene>.upload.txt` next to the video.
- **YouTube title** ≠ the on-screen title. It adds a new angle in ≤ 40 characters:
  *"Not a Coincidence"*, *"3 Colors Aren't Enough"*, *"A Polygon With 2 Sides?"*,
  *"This Pattern Breaks at 6"*. Don't reveal the answer.
- **Description**: one or two lines restating the teaser, naming the theorem.
- **Hashtags**: 3–5, always `#math #shorts` + topic (`#geometry`, `#calculus`, `#puzzle`).
- **Pinned comment**: a question that invites answers ("Did you guess 32 too?").

## 11. Render and QA

```bash
./render.sh -l <file>                                    # list scenes + sections
./render.sh -q draft -s beat_one <file> 2>&1 | tail -4   # one beat, fast
./render.sh -q draft <file> 2>&1 | tail -4               # whole video, fast
./render.sh <file> 2>&1 | tail -4                        # final 1080x1920
```

Options go **before** the file. The output lands in `output/videos/<path without leading _>/<Scene>.mp4`
along with any `.upload.txt` / `.txt` / `.srt` / `.json`. Progress bars flood stdout, so always `tail` the
output (grep it for `Caption runs` when narrated). On a failure the traceback is at the end.
**Draft and `-s` renders overwrite the final `<Scene>.mp4`** (same name, same folder), so always
finish with a full default-quality render, and never test-render someone's finished short without
re-rendering it afterwards.

**Look at the video**, don't just trust that it rendered. Write stills to the scratchpad and Read them:

```bash
ffmpeg -v error -y -i <video> -frames:v 1 <scratchpad>/frame0.png                                  # the thumbnail
ffmpeg -v error -y -i <video> -frames:v 1 -vf "crop=iw:iw*4/3" <scratchpad>/grid.png               # as the grid shows it
ffmpeg -v error -y -i <video> -vf "fps=1/2.5,scale=216:-1,tile=10x2" -frames:v 1 <scratchpad>/sheet.png  # contact sheet
```

**Checklist before reporting done:**
- [ ] Frame 0 is the requested hook, complete, and survives the 3:4 grid crop
- [ ] No overlaps (labels on lines, notes or captions on figures), nothing cut off, nothing below y = -5.0
- [ ] Colours actually show on every `Tex`/`Text` (the `color=` and `add_step` traps)
- [ ] Every rule is named; every claim on screen matches the verified maths
- [ ] There is a real aha motion; no dead air over ~1.6 s
- [ ] The answer is boxed in yellow + flashed, then the outro; no audio track
- [ ] Narrated: captions are ≤ 2 lines, one yellow key phrase each, transcript files written, spoken forms read naturally
- [ ] Duration is 10–58 s (from the `done` line)
- [ ] Each section renders alone with `-s`

When you report, give the file path, the video path and duration, the hook + voice mode used, the
on-screen and YouTube titles, a one-line beat summary, and (narrated) the transcript paths. Keep it short.
