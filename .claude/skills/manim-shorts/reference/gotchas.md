# manimgl gotchas (v1.7.2, this repo)

Each of these has already cost a render here. Most fail **silently**.

## Environment

- `manimgl` is not on PATH. Always use `./render.sh` from the repo root (it sets `PYTHONPATH` and
  finds `/usr/local/Caskroom/miniconda/base/envs/manim/bin/manimgl`).
- To probe in Python: `PYTHONPATH=/Users/future/Documents/Manim-Lab /usr/local/Caskroom/miniconda/base/envs/manim/bin/python`.
  System `python3` has no manim.
- When probing `Tex` strings, an uncached `Tex` prints `Writing ...` on the same line first. Print a
  marker (`print("RESULT", ...)`) and filter with an *unanchored* `grep -oE "RESULT.*"`.
- Read colours from raw data (`mob.family_members_with_points()[0].data['fill_rgba']`), not from
  `get_fill_color()` on a group (it returns a misleading grey).
- macOS `/bin/bash` is 3.2: no `mapfile`. Under `set -e` a bare `cond && exit` kills the script.

## Colour

- **`color=` is ignored by `Tex`, `TexText` and `Text`.** They render white with no warning. Use
  `.set_color(...)` after construction, or `t2c=`. (`color=` works on `Line`, `Dot`,
  `SurroundingRectangle` and other plain VMobjects.)
- **`add_step(..., t2c=...)` loses the colours.** `add_step` calls `line.set_color(...)` after
  building, which overwrites every part (verified). Use a custom coloured-step helper
  (`reference/toolkit.md`) or `replace_step(..., colors=...)`.
- `mob.animate.set_opacity(x)` on a graph curve adds a fill. Use `set_stroke(opacity=x)`.
- **Pango `<span foreground=...>` markup is ignored** by `MarkupText` here: everything comes out white.
  Colour parts of a `Text` with character spans instead: `Text(s, t2c={(start, end): color})`.
  (`custom/hooks.py` and `custom/narration.py` do this.)
- The configured default text font is `CMU Serif`. For the bold sans look pass
  `font="Avenir Next"` (weights `BOLD`, `HEAVY`). Installed alternatives: `Arial Black`, `Futura`.
- SVG import: `fill="url(#grad)"` imports black (re-tint, e.g. `tint_by_position`), and
  `fill-rule="evenodd"` is ignored (holes fill in).

## TeX

- **Never use `\;`, `\:` or `\!`.** They raise cryptic `LatexError`s or render no space. Use `\,`,
  `\quad`, `\qquad`, or `\ `. Safe arrow spacing is `\quad\Rightarrow\quad`.
- **Isolating a substring that starts with a sign kills its spacing** (`isolate=["+ 1"]` renders
  tight). Write `{}+ 1` / `{}- 4` / `{}= 2` in the TeX *and* the isolate key. Ending an isolate on `=`
  breaks the same way.
- **Substring indexing (`tex["A^2"]`) is unreliable** for anything with `^`, `{}` or `\commands`.
  Pass the substring through `t2c=` or `isolate=` first, then index.
- Check match counts: `len(tex["8"])` may be 2. Pick `[0]` or `[-1]` deliberately.
- `Tex` uses `align*`. Multi-row card statements go through `CardTex` (`gather*`, centred rows).
- Joining adjacent string literals can weld commands: `R"\quad" R"B"` gives `\quadB`. End a piece
  with a space: `R"\quad "`.
- Use `Tex` / `TexText`, never `MathTex` (that is ManimCommunity).
- For live numbers inside TeX: `value = tex.make_number_changeable("50.0")`, then
  `value.f_always.set_value(lambda: ...)`.

## Layout

- `to_edge`, `to_corner` and `FRAME_HEIGHT/WIDTH` use the *global* 8 × 4.5 frame, not the reshaped
  portrait frame. Use `pin_to_top` or explicit `y * UP`.
- `get_center()` returns a live view: stash `mob.get_center().copy()` before moving the mobject.
- A `VGroup`'s bounding box goes stale if you move its children one by one. Rebuild the group
  (`VGroup(*[VGroup(*row) for row in rows])`) before `SurroundingRectangle` or `about_edge`.
- `Axes(x_range=(-2.5, 2.5, 1))` gives duplicate "0" tick labels. Pass explicit `x_values`/`y_values`.
- Stroke width is absolute (pixels). After shrinking a detailed mark, re-set its stroke widths
  or thin lines clot into a blob (the `NeuroEduLogo` thumbnail rule: `height >= 1.9`, edges
  `2.2 * h / 2`).

## Drawing order

- manimgl batches a family: **all fills, then all strokes**. Overlapping filled 3D-looking blocks in
  one VGroup show back edges through front faces. Put each block in a `Group` with an invisible
  `DotCloud` between blocks, and animate blocks individually (see `_2026/Series/binomial_blocks.py`).
- Put shaded regions behind lines and labels: `self.add(fill); self.bring_to_back(fill)`.
- `always_redraw` can't `become` mixed `Group`s. Use an updater doing
  `m.set_submobjects(build().submobjects); m.note_changed_data()`.

## Updaters and animation

- `clear_updaters()` on every `always_redraw` / `f_always` mobject once its motion is over, before
  transforming or reusing it.
- A per-frame driver updater fights `FadeIn`/`GrowArrow` on the same mobjects. Keep it out of
  the scene during entrances and exits.
- `pointwise_become_partial` copies `joint_angle` from its source, so a never-rendered source shows
  tiny gaps at joints. Use `partial_bezier_path` + `set_points`.
- `Arrow.put_start_and_end_on` is slow (~1.4 ms each). For many arrows per frame compute the
  outlines in numpy.
- **`FadeIn(mob, scale=s)` starts the mobject at `1/s` times its size**, so `scale=0.3` flies in
  3.3× too large (dots appear outside the figure). For things that should grow in, use
  `GrowFromCenter` (in a `LaggedStart` for many).
- `self.play(*anims)` with different `run_time`s: each animation's alpha is `t / its run_time`,
  so don't rely on mixing lengths in one play. Play short fades separately.
- `row.animate.shift(...)` snapshots `row` when it is built. Don't `row.add(...)` before that play
  runs, or the target and the mobject no longer match. Add new members after.
- `GlowDot` is not a VMobject. Group it with `Group`, not `VGroup`.

## Naming

- Don't name a section or helper `setup`, `run`, `p` or `window`. They shadow `Scene` attributes
  (`self.window` is `None` when writing to file, so `self.p()` / `self.window()` crash).
