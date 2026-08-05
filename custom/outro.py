from __future__ import annotations

import os

import numpy as np

from manimlib import *


ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

# Drop a square PNG of the real badge here and the outro uses it instead of
# the vector rebuild below
LOGO_IMAGE = os.path.join(ASSETS, "neuroeduz_logo.png")
OUTRO_SOUND = os.path.join(ASSETS, "neuroeduz.wav")

PURPLE_DARK = "#3D1670"
PURPLE_MID = "#6B2FA8"
PURPLE_LIGHT = "#A15FE4"
CHROME = "#C8CDD4"
CHROME_DARK = "#8E959E"

# Node positions read off the badge, in units of the disc radius
LOGO_NODES = [
    (0.44, 0.60),    # 0 top
    (0.72, 0.34),    # 1 upper right
    (-0.04, 0.03),   # 2 left, against the N
    (0.46, 0.05),    # 3 centre
    (0.74, 0.04),    # 4 right
    (0.25, -0.30),   # 5 lower left
    (0.68, -0.28),   # 6 lower right
    (0.38, -0.58),   # 7 bottom
]
LOGO_EDGES = [
    (0, 1), (0, 3), (1, 3), (1, 4), (2, 0), (2, 3), (2, 5),
    (3, 4), (3, 5), (3, 6), (3, 7), (5, 6), (5, 7), (6, 7),
]
LOGO_RADII = [0.095, 0.100, 0.075, 0.095, 0.090, 0.090, 0.095, 0.088]


def n_glyph(width: float = 0.70, height: float = 0.90, stem: float = 0.22) -> Polygon:
    """A heavy geometric capital N, built as an outline.

    Drawn rather than typeset so it keeps the badge's blocky proportions
    whatever fonts happen to be installed.
    """
    w, h, t = width, height, stem
    y1, y2 = 0.20 * h, 0.80 * h
    points = [
        (0, 0), (0, h), (t, h),            # left stem
        (w - t, y1), (w - t, h),           # diagonal down, then up the right stem
        (w, h), (w, 0), (w - t, 0),        # right stem
        (t, y2), (t, 0),                   # diagonal back up, down to the base
    ]
    poly = Polygon(*[np.array([x, y, 0.0]) for x, y in points])
    poly.set_stroke(width=0)
    return poly


class NeuroEduLogo(Group):
    """The channel badge: a chrome-rimmed white disc, a purple N and a
    node-graph mark.  `disc`, `mark`, `nodes` and `edges` are exposed so the
    outro can animate the pieces separately."""

    def __init__(self, height: float = 3.2, use_image: bool = True):
        super().__init__()

        if use_image and os.path.exists(LOGO_IMAGE):
            image = ImageMobject(LOGO_IMAGE)
            image.set_height(height)
            self.disc = Group(image)
            self.letter = Group()
            self.mark = Group()
            self.nodes = Group()
            self.edges = VGroup()
            self.add(image)
            return

        rim = Circle(radius=1.0).set_fill(CHROME, 1).set_stroke(CHROME_DARK, 3)
        inner_rim = Circle(radius=0.93).set_fill(WHITE, 1).set_stroke(CHROME_DARK, 1.5)
        face = Circle(radius=0.90).set_fill(WHITE, 1).set_stroke(width=0)
        self.disc = VGroup(rim, inner_rim, face)

        letter = n_glyph()
        letter.set_fill(PURPLE_DARK, 1)
        letter.move_to(np.array([-0.41, 0.0, 0.0]))

        points = [np.array([x, y, 0.0]) for x, y in LOGO_NODES]
        # Shade each node by how far up-and-right it sits, like the original
        keys = [0.5 * (p[0] + p[1]) for p in points]
        lo, hi = min(keys), max(keys)
        colors = [
            interpolate_color(PURPLE_DARK, PURPLE_LIGHT, (k - lo) / (hi - lo))
            for k in keys
        ]

        self.edges = VGroup(*[
            Line(points[i], points[j], stroke_width=3.2).set_stroke(
                interpolate_color(colors[i], colors[j], 0.5)
            )
            for i, j in LOGO_EDGES
        ])
        self.nodes = VGroup(*[
            Dot(point, radius=radius).set_fill(color, 1).set_stroke(width=0)
            for point, radius, color in zip(points, LOGO_RADII, colors)
        ])

        self.letter = letter
        self.mark = VGroup(letter, self.edges, self.nodes)
        self.add(self.disc, self.mark)
        self.set_height(height)


class BrandOutroMixin:
    """Adds an `outro` section: badge pops in, the network lights up, the
    handle types out, and a one-word sting plays on the pop.

    Add "outro" to the scene's `sections` list.  Set `outro_sound = ""` to
    render it silent.
    """

    outro_handle = "@neuroeduz"
    outro_tagline = "math, every day"
    outro_sound = OUTRO_SOUND
    outro_logo_height = 3.4
    outro_hold = 1.2

    def outro(self):
        self.clear_for_outro()

        logo = NeuroEduLogo(height=self.outro_logo_height)
        logo.move_to(1.15 * UP)

        handle = Text(self.outro_handle, font_size=62, weight=BOLD)
        handle.set_color(WHITE)
        handle.next_to(logo, DOWN, buff=0.85)

        tagline = Text(self.outro_tagline, font_size=32)
        tagline.set_color(GREY_B)
        tagline.next_to(handle, DOWN, buff=0.38)

        underline = Line(LEFT, RIGHT)
        underline.set_width(handle.get_width() * 0.62)
        underline.set_stroke(PURPLE_LIGHT, 5)
        underline.next_to(handle, DOWN, buff=0.24)

        if self.outro_sound_enabled():
            self.add_sound(self.outro_sound, time_offset=0.18, gain=-2)

        # The badge lands with a little overshoot
        self.play(FadeIn(logo.disc, scale=0.35), run_time=0.45, rate_func=rush_from)
        if len(logo.edges) > 0:
            self.play(
                ShowCreation(logo.edges, lag_ratio=0.06),
                FadeIn(logo.nodes, lag_ratio=0.10, scale=0.4),
                FadeIn(logo.letter, scale=0.75),
                run_time=0.85,
            )
        else:
            self.wait(0.5)

        halo = Circle(radius=logo.get_height() / 2)
        halo.move_to(logo)
        halo.set_stroke(PURPLE_LIGHT, 6).set_fill(opacity=0)
        self.play(
            halo.animate.scale(1.55).set_stroke(width=0, opacity=0),
            run_time=0.7,
            rate_func=rush_from,
        )
        self.remove(halo)

        self.play(
            FadeIn(handle, 0.25 * UP),
            ShowCreation(underline),
            run_time=0.55,
        )
        self.play(FadeIn(tagline, 0.15 * UP), run_time=0.4)
        self.wait(self.outro_hold)

    def outro_sound_enabled(self) -> bool:
        """False when NO_SOUND is set (render.sh --silent), when the scene
        sets `outro_sound = ""`, or when the asset is missing."""
        if os.environ.get("NO_SOUND", "").strip().lower() in ("1", "true", "yes", "on"):
            return False
        return bool(self.outro_sound) and os.path.exists(self.outro_sound)

    def clear_for_outro(self, run_time: float = 0.5):
        """Sweep whatever is on screen before the badge lands."""
        leftovers = Group(*self.mobjects)
        if len(leftovers) > 0:
            self.play(FadeOut(leftovers, 0.3 * UP), run_time=run_time)
        if hasattr(self, "lazy_state"):
            self.lazy_state.clear()


class BrandOutro(BrandOutroMixin, Scene):
    """The outro on its own, for rendering a reusable tail clip:
        ./render.sh custom/outro.py BrandOutro
    """

    frame_width = 8.0
    frame_height = 8.0 * 16 / 9
    sections = ["outro"]

    def setup(self):
        super().setup()
        self.camera.background_color = BLACK
        self.frame.set_shape(self.frame_width, self.frame_height)

    def construct(self):
        self.outro()
