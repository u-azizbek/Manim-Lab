from __future__ import annotations

import os

import numpy as np

from manimlib import *


ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

# The channel's own artwork, used by `channel_mark` for problem cards.
# The outro badge deliberately uses the rebuilt mark further down instead --
# that one is tuned to sit inside the disc.
LOGO_SVG = os.path.join(ASSETS, "logo.svg")
LOGO_IMAGE = os.path.join(ASSETS, "neuroeduz_logo.png")

PURPLE_DARK = "#3D1670"
PURPLE_MID = "#6B2FA8"
PURPLE_LIGHT = "#A15FE4"
CHROME = "#C8CDD4"
CHROME_DARK = "#8E959E"

# The neural-E: eight nodes laid out as a capital E -- a left spine (A-D-F)
# with top / middle / bottom bars -- overlaid with a synaptic mesh.  Positions
# are in units of the disc radius and are mirror-symmetric top-to-bottom
# (A<->F, B<->G, C<->H; D and E on the axis), so the E reads as a clean,
# balanced letter rather than a scattered blob.
#
#   A --- B --- C      top bar      (y = +0.42)
#   |
#   D --------- E      middle bar   (y =  0.00)
#   |
#   F --- G --- H      bottom bar   (y = -0.42)
#
LOGO_NODES = [
    (0.06,  0.42),   # 0  A  top spine / top-bar left
    (0.40,  0.44),   # 1  B  top-bar middle
    (0.71,  0.39),   # 2  C  top-bar right
    (0.06,  0.00),   # 3  D  mid spine / middle-bar left
    (0.55,  0.00),   # 4  E  middle-bar right (hub)
    (0.06, -0.42),   # 5  F  bottom spine / bottom-bar left
    (0.40, -0.44),   # 6  G  bottom-bar middle
    (0.71, -0.39),   # 7  H  bottom-bar right
]
LOGO_EDGES = [
    # Structural E: spine + three bars
    (0, 3), (3, 5),                    # spine  A-D-F
    (0, 1), (1, 2),                    # top bar    A-B-C
    (3, 4),                            # middle bar D-E
    (5, 6), (6, 7),                    # bottom bar F-G-H
    # Synaptic mesh -- added in mirror pairs so the graph stays symmetric
    (0, 2), (5, 7),                    # A-C / F-H
    (0, 4), (4, 5),                    # A-E / E-F
    (1, 3), (3, 6),                    # B-D / D-G
    (1, 4), (4, 6),                    # B-E / E-G
    (2, 4), (4, 7),                    # C-E / E-H
    (2, 3), (3, 7),                    # C-D / D-H
]
LOGO_RADII = [0.075] * 8


def n_glyph(width: float = 0.70, height: float = 0.90, stem: float = 0.22,
            tip: float = 0.20) -> Polygon:
    """A heavy geometric capital N, built as an outline.

    Drawn rather than typeset so it keeps the badge's blocky proportions
    whatever fonts happen to be installed.  `tip` is how far up the right stem
    the diagonal lands, as a fraction of the height -- smaller means the
    diagonal runs closer to corner-to-corner.
    """
    w, h, t = width, height, stem
    y1, y2 = tip * h, (1 - tip) * h
    points = [
        (0, 0), (0, h), (t, h),            # left stem
        (w - t, y1), (w - t, h),           # diagonal down, then up the right stem
        (w, h), (w, 0), (w - t, 0),        # right stem
        (t, y2), (t, 0),                   # diagonal back up, down to the base
    ]
    poly = Polygon(*[np.array([x, y, 0.0]) for x, y in points])
    poly.set_stroke(width=0)
    return poly


def tint_by_position(mobject, dark=PURPLE_DARK, light=PURPLE_LIGHT, stroke_width=0.0):
    """Shade a mobject's parts from `dark` at the top-left to `light` at the
    bottom-right, matching the linearGradient in the channel SVG (manim's SVG
    reader does not resolve `url(#...)` fills)."""
    corner = mobject.get_corner(UL)
    width = max(mobject.get_width(), 1e-6)
    height = max(mobject.get_height(), 1e-6)
    for part in mobject.get_family():
        if not part.has_points():
            continue
        centre = part.get_center()
        t = 0.5 * ((centre[0] - corner[0]) / width + (corner[1] - centre[1]) / height)
        color = interpolate_color(dark, light, float(np.clip(t, 0, 1)))
        if stroke_width > 0:
            part.set_stroke(color, stroke_width)
        else:
            part.set_fill(color, 1).set_stroke(width=0)
    return mobject


def channel_mark(height: float = 1.0):
    """The N + neural-E mark from the channel SVG, re-tinted and split into
    `letter`, `edges` and `nodes` so it can be revealed piece by piece."""
    if not os.path.exists(LOGO_SVG):
        return None

    svg = SVGMobject(LOGO_SVG)
    # Straight connector lines come in with a handful of points; the letter and
    # the nodes are closed shapes, the letter being much the largest
    thin = VGroup(*[part for part in svg if len(part.get_points()) <= 8])
    solid = [part for part in svg if len(part.get_points()) > 8]
    solid.sort(key=lambda part: -part.get_width())
    svg_letter, nodes = solid[0], VGroup(*solid[1:])

    # manim's SVG reader ignores the file's fill-rule="evenodd", so the N comes
    # in as a solid block.  Redraw it as an outline over the same box; the
    # proportions (stem 18/75, diagonal corner to corner) are from the file.
    letter = n_glyph(width=0.75, height=1.0, stem=0.18, tip=0.10)
    letter.replace(svg_letter, stretch=True)

    tint_by_position(letter)
    tint_by_position(nodes)
    tint_by_position(thin, stroke_width=1.0)

    mark = VGroup(thin, nodes, letter)
    mark.letter, mark.edges, mark.nodes = letter, thin, nodes
    mark.set_height(height)
    set_mark_stroke(mark)
    return mark


def set_mark_stroke(mark):
    """Stroke width is absolute in manim, so the synapse lines have to be
    re-set whenever the mark is resized or they clot into a blob."""
    mark.edges.set_stroke(width=max(0.6, 1.5 * mark.get_height()))
    return mark


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

        # The badge deliberately keeps this rebuilt mark rather than the SVG
        # one: it is tuned for the disc.  `channel_mark` (the real SVG) is for
        # problem cards.
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
    handle types out.

    Add "outro" to the scene's `sections` list.  The outro is silent by
    design -- these shorts carry no audio track.
    """

    outro_handle = "@neuroeduz"
    outro_tagline = "math, every day"
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
