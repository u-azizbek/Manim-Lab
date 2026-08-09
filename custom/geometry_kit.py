from __future__ import annotations

import numpy as np

from manimlib import *

from custom.shorts import ShortsScene, StepListMixin


def to_point(xy) -> np.ndarray:
    """Accept (x, y) or (x, y, z) and return a 3D point."""
    arr = np.array(xy, dtype=float)
    if arr.shape == (2,):
        return np.array([arr[0], arr[1], 0.0])
    return arr


def polar(base, angle_deg: float, length: float) -> np.ndarray:
    """The point `length` away from `base` in direction `angle_deg` (CCW from +x)."""
    a = np.deg2rad(angle_deg)
    return to_point(base) + length * np.array([np.cos(a), np.sin(a), 0.0])


def bearing(frm, to) -> float:
    """Direction from one point to another, in degrees CCW from +x."""
    return np.rad2deg(angle_of_vector(to_point(to) - to_point(frm)))


class GeoFigure:
    """Named points plus a factory for every mark you would draw on a figure.

    Points are given once, in whatever coordinates the construction is natural
    in; `normalize` then rescales them to a target width and centre, so marks
    built afterwards land in the final coordinate system.  Nothing is added to
    the scene automatically -- each method returns a mobject for the caller to
    group and animate, which is what makes step-by-step reveals easy.

    Angles are read off the stored points, so a figure built from exact
    constraints is drawn with exactly those angles.
    """

    def __init__(
        self,
        points: dict,
        line_color: ManimColor = WHITE,
        line_width: float = 4.0,
        label_font_size: int = 34,
        angle_font_size: int = 30,
    ):
        self.pts = {name: to_point(xy) for name, xy in points.items()}
        self.line_color = line_color
        self.line_width = line_width
        self.label_font_size = label_font_size
        self.angle_font_size = angle_font_size
        self.scale_factor = 1.0

    # ---- points ----

    def p(self, name: str) -> np.ndarray:
        if name not in self.pts:
            raise KeyError(f"unknown point {name!r}; have {sorted(self.pts)}")
        return self.pts[name]

    def add_point(self, name: str, xy) -> np.ndarray:
        self.pts[name] = to_point(xy)
        return self.pts[name]

    def midpoint(self, a: str, b: str, name: str | None = None) -> np.ndarray:
        m = 0.5 * (self.p(a) + self.p(b))
        if name:
            self.pts[name] = m
        return m

    def dist(self, a: str, b: str) -> float:
        return get_norm(self.p(b) - self.p(a))

    def angle_at(self, a: str, b: str, c: str) -> float:
        """The non-reflex angle ABC in degrees."""
        u = normalize(self.p(a) - self.p(b))
        v = normalize(self.p(c) - self.p(b))
        return float(np.rad2deg(np.arccos(np.clip(u @ v, -1, 1))))

    def normalize(self, width: float | None = None, height: float | None = None,
                  center=ORIGIN) -> "GeoFigure":
        """Rescale/shift the stored points to fit a target size, centred."""
        stack = np.array(list(self.pts.values()))
        lo, hi = stack.min(axis=0), stack.max(axis=0)
        span = hi - lo
        scale = 1.0
        if width is not None and span[0] > 0:
            scale = width / span[0]
        if height is not None and span[1] > 0:
            scale = min(scale, height / span[1]) if width is not None else height / span[1]
        mid = 0.5 * (lo + hi)
        for name, point in self.pts.items():
            self.pts[name] = (point - mid) * scale + to_point(center)
        self.scale_factor *= scale
        return self

    # ---- lines ----

    def _stroke(self, kwargs: dict) -> dict:
        kwargs.setdefault("stroke_color", self.line_color)
        kwargs.setdefault("stroke_width", self.line_width)
        return kwargs

    def polygon(self, *names: str, **kwargs) -> Polygon:
        poly = Polygon(*[self.p(n) for n in names])
        poly.set_stroke(**{
            k.replace("stroke_", ""): v
            for k, v in self._stroke(kwargs).items() if k.startswith("stroke_")
        })
        poly.set_fill(opacity=0)
        return poly

    def polyline(self, *names: str, **kwargs) -> VMobject:
        line = VMobject()
        line.set_points_as_corners([self.p(n) for n in names])
        kwargs = self._stroke(kwargs)
        line.set_stroke(kwargs["stroke_color"], kwargs["stroke_width"])
        return line

    def segment(self, a: str, b: str, **kwargs) -> Line:
        kwargs = self._stroke(kwargs)
        return Line(self.p(a), self.p(b), **kwargs)

    def segments(self, pairs, **kwargs) -> VGroup:
        return VGroup(*[self.segment(a, b, **kwargs) for a, b in pairs])

    def dashed(self, a: str, b: str, extend: float = 0.0, **kwargs) -> DashedLine:
        """A dashed line through a and b, optionally running past both ends."""
        u = normalize(self.p(b) - self.p(a))
        kwargs = self._stroke(kwargs)
        return DashedLine(self.p(a) - extend * u, self.p(b) + extend * u, **kwargs)

    # ---- marks ----

    def ticks(self, a: str, b: str, n: int = 1, size: float = 0.16,
              gap: float = 0.09, **kwargs) -> VGroup:
        """`n` congruence ticks across the middle of segment ab."""
        u = normalize(self.p(b) - self.p(a))
        perp = rotate_vector(u, PI / 2)
        mid = self.midpoint(a, b)
        kwargs = self._stroke(kwargs)
        offsets = (np.arange(n) - (n - 1) / 2) * gap
        return VGroup(*[
            Line(
                mid + t * u - size * perp,
                mid + t * u + size * perp,
                **kwargs,
            )
            for t in offsets
        ])

    def angle(self, a: str, b: str, c: str, radius: float = 0.55, arcs: int = 1,
              arc_gap: float = 0.09, color: ManimColor = WHITE,
              fill_opacity: float = 0.0, stroke_width: float = 3.0) -> VGroup:
        """Arc(s) marking angle ABC, optionally with a shaded sector behind."""
        start, sweep = self._span(a, b, c)
        group = VGroup()
        if fill_opacity > 0:
            sector = Sector(
                angle=sweep, start_angle=start, radius=radius,
                arc_center=self.p(b),
            )
            sector.set_fill(color, fill_opacity).set_stroke(width=0)
            group.add(sector)
        for i in range(arcs):
            arc = Arc(
                start_angle=start, angle=sweep, radius=radius + i * arc_gap,
                arc_center=self.p(b),
            )
            arc.set_stroke(color, stroke_width)
            group.add(arc)
        return group

    def right_angle(self, a: str, b: str, c: str, size: float = 0.32,
                    color: ManimColor = GREY_B, fill_opacity: float = 1.0,
                    stroke_width: float = 2.0) -> Polygon:
        """The little square marking a right angle at b (drawn from the rays)."""
        u = normalize(self.p(a) - self.p(b)) * size
        v = normalize(self.p(c) - self.p(b)) * size
        square = Polygon(self.p(b), self.p(b) + u, self.p(b) + u + v, self.p(b) + v)
        square.set_fill(color, fill_opacity).set_stroke(color, stroke_width)
        return square

    def angle_label(self, a: str, b: str, c: str, tex: str, radius: float = 0.92,
                    font_size: int | None = None, color: ManimColor = WHITE,
                    use_text: bool = False, outside: bool = False,
                    offset=ORIGIN) -> Mobject:
        """Place a label on angle ABC, along its bisector.

        `outside` puts it on the far side of the vertex instead of inside the
        wedge -- what you want for a reflex-looking or already crowded angle.
        `offset` nudges it further, in the same units as `radius`.
        """
        start, sweep = self._span(a, b, c)
        direction = np.array([np.cos(start + sweep / 2), np.sin(start + sweep / 2), 0.0])
        if outside:
            direction = -direction
        label = (Text if use_text else Tex)(
            tex, font_size=font_size or self.angle_font_size,
        )
        label.set_color(color)
        label.move_to(self.p(b) + radius * direction + np.array(offset, dtype=float))
        return label

    def bisector_direction(self, a: str, b: str, c: str) -> np.ndarray:
        start, sweep = self._span(a, b, c)
        return np.array([np.cos(start + sweep / 2), np.sin(start + sweep / 2), 0.0])

    def region(self, *names: str, color: ManimColor = BLUE,
               opacity: float = 0.35, stroke_width: float = 0.0) -> Polygon:
        """A shaded polygon over the named vertices."""
        poly = Polygon(*[self.p(n) for n in names])
        poly.set_fill(color, opacity)
        poly.set_stroke(color, stroke_width)
        return poly

    def circle(self, center: str, through: str, **kwargs) -> Circle:
        kwargs = self._stroke(kwargs)
        return Circle(radius=self.dist(center, through), **kwargs).move_to(self.p(center))

    def dots(self, *names: str, radius: float = 0.055,
             color: ManimColor = WHITE) -> VGroup:
        return VGroup(*[Dot(self.p(n), radius=radius, fill_color=color) for n in names])

    def label(self, name: str, tex: str | None = None, direction=None,
              buff: float = 0.28, font_size: int | None = None,
              color: ManimColor = WHITE, away_from=None) -> Mobject:
        """Label a vertex.  `away_from` pushes it directly away from another point."""
        label = Tex(tex if tex is not None else name,
                    font_size=font_size or self.label_font_size)
        label.set_color(color)
        if direction is None:
            if away_from is not None:
                direction = normalize(self.p(name) - self.p(away_from))
            else:
                direction = normalize(self.p(name) - self.centroid())
        label.move_to(self.p(name) + buff * np.array(direction, dtype=float))
        return label

    def labels(self, spec: dict, **kwargs) -> VGroup:
        """`{"A": UP, "B": RIGHT}` -> a VGroup of vertex labels."""
        return VGroup(*[
            self.label(name, direction=direction, **kwargs)
            for name, direction in spec.items()
        ])

    def centroid(self) -> np.ndarray:
        return np.array(list(self.pts.values())).mean(axis=0)

    # ---- internals ----

    def _span(self, a: str, b: str, c: str) -> tuple[float, float]:
        """(start_angle, sweep) for the non-reflex angle ABC, sweeping CCW."""
        ang_a = angle_of_vector(self.p(a) - self.p(b))
        ang_c = angle_of_vector(self.p(c) - self.p(b))
        diff = (ang_c - ang_a) % TAU
        if diff > PI:
            return ang_c, TAU - diff
        return ang_a, diff


class GeometryShortScene(StepListMixin, ShortsScene):
    """A 9:16 short built around one figure with a running list of steps.

    Subclasses build the figure and call `add_step` / `replace_steps`; the base
    class keeps the figure pinned in the upper area and stacks step lines
    underneath it, so nothing has to be positioned by hand.
    """

    title_text = ""
    title_color = GREY_A
    figure_width = 6.6
    figure_center_y = 2.9

    def make_title(self):
        title = Text(self.title_text, font_size=40, weight=BOLD)
        title.set_color(self.title_color)
        title.set_max_width(6.6)
        return self.pin_to_top(title, buff=0.45)

    def get_title(self):
        return self.lazy("title", self.make_title)

