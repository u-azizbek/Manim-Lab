from __future__ import annotations

import re

from manimlib import *

from custom.outro import NeuroEduLogo


# Frame 0 of a short doubles as its thumbnail, and the channel's Shorts grid
# shows that frame cropped to roughly 3:4 around the centre.  Anything that
# sells the video has to sit inside |y| <= HOOK_BAND or the grid cuts it off.
HOOK_BAND = 4.8

HOOK_FONT = "Avenir Next"
# Word-by-word title colours, as in "The Poker Chip Problem"
HOOK_COLORS = ["#FFE14D", "#FF6B6B", "#58C4DD", "#5BD98A", "#C39BFF"]


def hook_title(text: str, colors=HOOK_COLORS, mode: str = "words",
               font_size: int = 58, max_width: float = 7.3,
               italic: bool = True) -> Text:
    """The bold, colourful title of a hook.

    mode="words"     each word its own colour, cycling through `colors`
    mode="gradient"  one sweep across the whole title
    mode="solid"     everything in colors[0]
    """
    spans = [match.span() for match in re.finditer(r"\S+", text)]
    t2c = {}
    if mode == "words":
        t2c = {span: colors[i % len(colors)] for i, span in enumerate(spans)}
    title = Text(
        text, font=HOOK_FONT, weight=BOLD, slant=ITALIC if italic else NORMAL,
        font_size=font_size, t2c=t2c,
    )
    if mode == "gradient":
        title.set_color_by_gradient(*colors)
    elif mode == "solid":
        title.set_color(colors[0])
    title.set_max_width(max_width)
    return title


def teaser_text(text: str, color=WHITE, font_size: int = 44, max_width: float = 6.8) -> Text:
    """The one-line question under the hook: "Does this even converge?" """
    teaser = Text(text, font=HOOK_FONT, weight=BOLD, font_size=font_size)
    teaser.set_color(color)
    teaser.set_max_width(max_width)
    return teaser


def brand_row(height: float = 1.9) -> Group:
    """Badge + handle.  The badge's synapse lines are a fixed width, so they
    are thinned with it, or at this size they clot into a tangle."""
    logo = NeuroEduLogo(height=height)
    logo.edges.set_stroke(width=2.2 * logo.get_height() / 2)
    handle = Text("@neuroeduz", font_size=48, weight=BOLD).set_color(WHITE)
    return Group(logo, handle).arrange(RIGHT, buff=0.4)


def fit_in_band(group: Mobject, center_y: float = 0.0) -> Mobject:
    """Shrink a hook to fit the grid-safe band if it has to, and centre it."""
    group.set_max_height(2 * HOOK_BAND)
    group.move_to(center_y * UP)
    return group


def formula_hook(title: str | Mobject, formula: Mobject, teaser: str | Mobject = "",
                 formula_width: float = 5.6, buff: float = 1.3) -> Group:
    """FORMULA HOOK: a title, the problem itself huge in the middle, and a
    teaser question under it.  For a single striking expression: a limit, an
    integral, a sum, an equation.  The formula is the star, so the title is
    smaller than in the other hooks."""
    if isinstance(title, str):
        title = hook_title(title, mode="gradient", font_size=54)
    if isinstance(teaser, str):
        teaser = teaser_text(teaser) if teaser else None
    formula.set_width(formula_width)
    formula.set_max_height(5.0)
    hook = Group(*[m for m in (title, formula, teaser) if m is not None]).arrange(DOWN, buff=buff)
    fit_in_band(hook, 0.3)
    hook.title, hook.formula, hook.teaser = title, formula, teaser
    return hook


def figure_hook(title: str | Mobject, figure: Mobject, teaser: str | Mobject = "",
                figure_height: float = 5.6, figure_width: float = 6.6,
                buff: float = 0.9) -> Group:
    """FIGURE HOOK: a colourful title above (inside the band, not at the very
    top) and the figure big in the middle, with an optional teaser under it.
    For problems where the picture itself is the hook."""
    if isinstance(title, str):
        title = hook_title(title)
    if isinstance(teaser, str):
        teaser = teaser_text(teaser) if teaser else None
    figure.set_height(figure_height)
    figure.set_max_width(figure_width)
    hook = Group(*[m for m in (title, figure, teaser) if m is not None]).arrange(DOWN, buff=buff)
    fit_in_band(hook, 0.0)
    hook.title, hook.figure, hook.teaser = title, figure, teaser
    return hook


def card_hook(title: str | Mobject, card: Mobject, figure: Mobject | None = None,
              question: Mobject | None = None, buff: float = 0.4) -> Group:
    """CARD HOOK: a title, the problem card, the figure and a huge "= ?",
    stacked inside the band.  The figure is blown up into whatever height is
    left (at most 6), so build it from a copy of the working figure."""
    if isinstance(title, str):
        title = hook_title(title, mode="gradient", font_size=56)
    parts = [m for m in (title, card, figure, question) if m is not None]
    if figure is not None:
        others = sum(m.get_height() for m in parts if m is not figure)
        room = 2 * HOOK_BAND - others - buff * (len(parts) - 1)
        figure.set_height(min(max(room, 2.0), 6.0))
        figure.set_max_width(7.0)
    hook = Group(*parts).arrange(DOWN, buff=buff)
    fit_in_band(hook, 0.0)
    hook.title, hook.card, hook.figure, hook.question = title, card, figure, question
    return hook
