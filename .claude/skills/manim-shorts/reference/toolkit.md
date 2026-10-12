# Shorts toolkit reference

Everything here is exported by `from manim_imports_ext import *`. The source is the truth.
If a signature here disagrees with `custom/*.py`, trust the code (and fix this file).

## Inheritance map

```
InteractiveScene
└── ShortsScene                      custom/shorts.py      9:16 frame, sections, lazy state
    ├── + StepListMixin              custom/shorts.py      stacked solution lines, note, replace_step
    │   ├── CardSolutionScene        custom/cards.py       problem card pinned on top
    │   │   └── MockTestShort        custom/mock_tests.py  + BrandOutroMixin, conclude(), card tag
    │   └── GeometryShortScene       custom/geometry_kit.py  title + figure + steps
    ├── SplitScreenScene             custom/split_screen.py  Beginner vs Pro panels
    └── FourierDrawingScene          custom/fourier_kit.py   landscape epicycles
BrandOutroMixin                      custom/outro.py       "outro" section
NarrationMixin                       custom/narration.py   captions + transcript (mix in FIRST of all)
custom/hooks.py                      card_hook / formula_hook / figure_hook builders for frame 0
```

Mixin order: `class X(NarrationMixin, BrandOutroMixin, ShortsScene)`, or
`class X(NarrationMixin, MockTestShort)` (MockTestShort already has the outro).

## ShortsScene (`custom/shorts.py`)

- `upload = dict(title=, description=, hashtags=[...], pinned_comment=)` makes the render write
  `<Scene>.upload.txt` next to the video (`write_sidecars`, run from `tear_down`; nothing on preview).
- `get_video_path()` is the written video, or None for a preview.
- Frame is reshaped to `8 × 14.22` in `setup`. `background_color = BLACK`.
- `sections: list[str]`: method names run in order by `construct`. `SECTIONS` env var /
  `render.sh -s a,b` runs a subset (always in declared order).
- `self.lazy(name, factory)` returns the state `name`. If no earlier section produced it,
  `factory()` builds it and adds it statically, which is what makes `-s` renders work.
- `self.set_state(name, mob)` is called by the producing section once the mobject is on screen.
- `self.pin_to_top(mob, buff=0.5)` sets the y position against the *reshaped* frame.
- **Pattern** for state shared between sections:
  ```python
  def get_figure(self):
      return self.lazy("figure", self.make_figure)      # consumers call this first
  def pose(self):
      fig = self.make_figure(); ...animate...; self.set_state("figure", fig)
  def later(self):
      self.get_figure(); self.lazy("turn", VGroup)      # VGroup = "nothing if skipped"
  ```
- Each section must clean up what it alone put on screen (or hand it on through `set_state`).
- Never name a section `setup`, `run`, `p` or `window` (they shadow Scene attributes).

## StepListMixin (`custom/shorts.py`)

Class attrs: `step_color=WHITE`, `result_color=YELLOW`, `note_color=GREY_B`, `steps_top_y=-0.7`,
`step_buff=0.34`, `step_font_size=36`, `step_max_width=6.9`.

| Method | Use |
| --- | --- |
| `add_step(tex, color=None, font_size=None, run_time=1.0, wait=0.45, **tex_kwargs)` | FadeIn a new line under the last one. **It calls `set_color` after building, so any `t2c` is wiped.** |
| `transform_step(source, tex, ...)` | New line grown out of an earlier one (`TransformFromCopy`) |
| `replace_step(source, tex, key_map={}, matched_keys=(), colors={}, ...)` | Rewrite a line *in place* (`TransformMatchingTex`). `colors={"x": BLUE}` colours parts (they are auto-isolated). Fixes the step list so later lines stack under it |
| `note(message, font_size=28, wait=1.6, keep=False)` | Grey `Text` sentence in the next slot, which clears itself. `\n` for two lines |
| `place_step(mob)` | Position any mobject in the next slot (then `self.steps().add(mob)` to keep it) |
| `clear_steps(run_time=0.6)` | Fade out all lines and reset |
| `steps()` | The `VGroup` of current lines (`.set_submobjects([...])` to prune) |

Coloured step lines: build them yourself so the colours survive.
```python
def add_colored(self, tex, t2c, font_size=None, wait=0.4):
    line = Tex(tex, t2c=t2c, font_size=font_size or self.step_font_size)
    line.set_max_width(self.step_max_width)
    self.place_step(line)
    self.steps().add(line)
    self.play(FadeIn(line, 0.15 * DOWN), run_time=1.0)
    self.wait(wait)
    return line
```
(or `add_step` first, then `replace_step(..., colors=...)`, or recolour parts after `add_step`
by indexing with an isolated substring).

## CardSolutionScene / ProblemCard (`custom/cards.py`)

- `ProblemCard(tex, width=7.2, font_size=46, label="")` is a pale-blue rounded card (`#EAF1FB`, ink
  `#101828`), with the real channel mark (`channel_mark()`) in the top-right corner. Rows are centred
  (`CardTex` uses `gather*`): break lines with `\\` and wrap prose in `\text{}`.
  Parts: `.rect`, `.body`, `.logo`, `.tag`.
- `CardSolutionScene` attrs: `problem_tex`, `problem_label`, `card_width=7.2`,
  `card_font_size=46`, `card_top_buff=0.5`, `steps_top_y=-1.2`, `step_buff=0.42`.
- `make_card()` builds the card *at its pinned home*. `get_card()` is the lazy version.
- `show_problem()` writes the card in the centre, holds, then glides it up (a plain opening with no
  thumbnail; prefer a custom `pose` for viral shorts).

## MockTestShort (`custom/mock_tests.py`)

`class X(MockTestShort)` = `BrandOutroMixin + CardSolutionScene`.
- `test = "F1"`, `question = 21` tags the card `F1:21` (`label_format`). `test = ""` hides the tag,
  which is what non-workbook puzzles use.
- Defaults: `card_font_size=40`, `card_width=7.3`, `step_buff=0.50`, `step_font_size=36`,
  `steps_gap=0.55`. `make_card()` sets `steps_top_y` to just under the card. Override
  `steps_top_y` again after placing a figure (`figure.get_bottom()[1] - 0.6`).
- `"outro"` is appended to `sections` automatically if missing. Write it anyway (`render.sh -l` reads source).
- Built-in sections/helpers: `pose()` (plain card write-in; override it for a thumbnail),
  `conclude(tex, font_size=52, wait=1.5)` (yellow line + box + `FlashAround`).
- Palette constants: `SETUP_COLOR`, `RULE_COLOR`, `RESULT_COLOR`.

## GeoFigure (`custom/geometry_kit.py`)

A registry of named points plus a factory for marks. It is **not a mobject**, nothing is auto-added,
and its points do **not** follow the mobjects if you move them. Build it at its final working
position (or keep anchor dots, as in `square_shear_area.py::at`).

```python
fig = GeoFigure({"A": (0, 3), "B": (4, 0), "C": (0, 0)}, line_color=WHITE, line_width=4,
                label_font_size=34, angle_font_size=30)
fig.normalize(width=6.0, center=1.5 * UP)     # rescale stored points; marks built after use world units
```

| Points | Lines | Marks | Labels |
| --- | --- | --- | --- |
| `p(n)`, `add_point(n, xy)`, `midpoint(a, b, name=)`, `dist(a, b)`, `angle_at(a, b, c)`, `centroid()`, `bisector_direction(a, b, c)` | `polygon(*n)`, `polyline(*n)`, `segment(a, b, **stroke)`, `segments(pairs)`, `dashed(a, b, extend=)`, `circle(center, through)` | `ticks(a, b, n=)`, `angle(a, b, c, radius=, arcs=, color=, fill_opacity=)`, `right_angle(a, b, c, size=)`, `region(*n, color=, opacity=)`, `dots(*n)` | `label(n, tex=, direction=, away_from=)`, `labels({"A": UP, ...})`, `angle_label(a, b, c, tex, outside=, offset=)` |

Module helpers: `to_point(xy)`, `polar(base, deg, length)`, `bearing(frm, to)`.
Layout traps: put a given polygon angle's label `outside=True`; use `offset=` when a bisector runs
along a drawn segment; put `right_angle` squares *after* shaded sectors; end dashed axes at the vertex
rather than using `extend=` through a label; don't label the same angle in two sections.

`GeometryShortScene(StepListMixin, ShortsScene)`: `title_text`, `title_color=GREY_A`,
`figure_width=6.6`, `figure_center_y=2.9`, `make_title()`, `get_title()`.

## BrandOutroMixin / logos (`custom/outro.py`)

- `class S(BrandOutroMixin, <Base>)`: the mixin comes **first**. Add `"outro"` last to `sections`.
- `outro()`: clears the screen, the badge pops in, the network lights up, a halo expands, and
  `@neuroeduz` + "math, every day" appear (~4.7 s). Tunables: `outro_handle`, `outro_tagline`,
  `outro_logo_height=3.4`, `outro_hold=1.2`. The look is approved, so don't restyle it.
- `NeuroEduLogo(height)` is the badge (disc + rebuilt N + network) used in the outro and the thumbnail
  brand row. At small sizes use `height >= 1.9` and `logo.edges.set_stroke(width=2.2 * logo.get_height() / 2)`.
- `channel_mark(height)` loads the real `assets/logo.svg`, **for problem cards only**. The two logos are
  deliberately different. Don't unify them.

## Hooks (`custom/hooks.py`)

All builders return a positioned `Group` with named parts, sized to fit `HOOK_BAND` (4.8: the
|y| that survives the Shorts-grid crop). `self.add(hook)` it for frame 0.

| Function | Parts | Notes |
| --- | --- | --- |
| `formula_hook(title, formula, teaser="", formula_width=5.6, buff=1.3)` | `.title .formula .teaser` | title str → `hook_title(mode="gradient", 54)` |
| `figure_hook(title, figure, teaser="", figure_height=5.6, figure_width=6.6, buff=0.9)` | `.title .figure .teaser` | title str → word-coloured `hook_title`. Pass a *copy* or a throwaway figure: it is resized |
| `card_hook(title, card, figure=None, question=None, buff=0.4)` | `.title .card .figure .question` | the figure is blown up into the spare height (≤ 6). Pass `figure.copy()` |
| `hook_title(text, colors=HOOK_COLORS, mode="words"/"gradient"/"solid", font_size=58, italic=True)` | | bold italic `Avenir Next`; per-word colours via character spans |
| `teaser_text(text, color=WHITE, font_size=44)` | | bold one-liner |
| `brand_row(height=1.9)` | | badge + @neuroeduz, edges thinned; optional, outside the band |
| `fit_in_band(group, center_y=0)` | | shrink to the band and centre |

Transition pattern after the hold: `FadeOut(hook.title)`, `FadeOut(hook.teaser)` first, then
`ReplacementTransform(hook.figure, working_figure)` / `Transform(hook.formula, header)`, then
`self.remove(hook)` and re-`add` whatever stays.

## NarrationMixin (`custom/narration.py`)

| Member | Use |
| --- | --- |
| `say(text, *animations, speak=None, run_time=None, wait=True, y=None)` | caption (crossfades the last one), animations under it, hold for the speech time |
| `hold(extra=0)` | after `say(..., wait=False)` and other plays: wait out the rest of the line |
| `narrate(speak, wait=True)` | voice-only transcript line, nothing on screen |
| `unsay()` | clear the caption |
| `make_caption(text)`, `balance_lines(words)`, `speech_time(spoken)` | building blocks |

Markup: `{y:...}` `{b:...}` `{p:...}` (also `{g:...}` `{r:...}` `{w:...}`), see `CAPTION_COLORS`.
Class attrs: `caption_font="Avenir Next"`, `caption_weight="HEAVY"`, `caption_font_size=62`,
`caption_y=-3.4`, `caption_max_width=7.2`, `caption_chars_per_line=24`, `caption_upper=True`,
`caption_backstroke=8`, `speech_wps=2.6`, `speech_pad=0.35`, `min_caption_time=1.2`,
`outro_line="Follow for a new math puzzle every day."` (empty = silent outro).
Output next to the video: `<Scene>.txt`, `.srt`, `.json` (lines with `text`, `speak`, `start`,
`end`, `caption`).

## SplitScreenScene (`custom/split_screen.py`)

Implement `get_problem_tex() -> str`, `beginner_lines() -> list[Mobject]`, `pro_lines()`.
Attrs: `beginner_label="BEGINNER"`, `pro_label="PRO"`, `beginner_color="#FF5C39"`,
`pro_color="#39D353"`, `credit`, `verdict`, `result_color`, `panel_width/height`, `line_buff`.
Sections are `["arena", "solve_beginner", "solve_pro", "conclude"]`. With the outro:
`class S(BrandOutroMixin, SplitScreenScene)` + `sections = SplitScreenScene.sections + ["outro"]`.
`LabeledPanel(label, color, width, height)` gives the box with `.inner_width/.inner_height/.dim()`.

## FourierDrawingScene (`custom/fourier_kit.py`)

Landscape 16:9: the file sets module-level `RENDER_QUALITY = "hd"` (render.sh reads it). Subclass
and set `svg_file` (or override `get_source_mobject`). Sections: intro, spectrum, assemble, draw,
zoom, convergence. See `_2026/Fourier/fourier_drawing.py`.

## Other kits

- `custom/matrix_kit.py` provides `LetterGrid` (a grid of matrix entries), `terms_of(spec, color)` and
  `BandDiagramScene(ShortsScene)`, the Sarrus-style diagonal-band diagram. Examples:
  `_2026/matrix/sarrus_rule.py`, `_2026/Geometry/triangle_area_sarrus.py`.

## Recurring local helpers worth copying

| Helper | Where | What |
| --- | --- | --- |
| `glowing(circle, color)` | `Geometry/orthic_triangle_5_12_13.py` | Soft halo circles for the thumbnail |
| `side_label(tex, p, q, color, away)` | same | Length label beside a segment, on the outer side |
| `tex_note`, `boxed`, `dismiss`, `behind` | same | TeX notes; yellow box; fade what partial renders may lack; fills to back |
| `header(text, color)` | `Geometry/square_shear_area.py` | "Method 2: …" line in the step list |
| `settle(fig)` + anchor dots + `at(key)` | same | Move a figure under the card while keeping point lookup |
| `lift_to_top(keep, *drop)` | `Series/telescoping_floor_sum.py` | Slide a key line up to the first slot |
| `foot`, `meet` | `Geometry/viviani_theorem.py` | Perpendicular foot; line intersection |
| `iso_cube`, `box` (isometric) | `Puzzles/cube_exponents.py`, `Series/sum_of_cubes.py` | Isometric 3D-looking blocks |
| `swap_row` | `Puzzles/cube_exponents.py` | Rewrite several columns in place at once |
