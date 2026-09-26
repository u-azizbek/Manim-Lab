"""Drawing any picture with a chain of rotating vectors (complex Fourier series).

The pipeline has three independent pieces, so each can be reused on its own:

    path_samples(mobject)          any VMobject (SVGMobject, Tex, Text, ...) ->
                                   one closed loop of complex numbers, sampled
                                   uniformly by arc length
    FourierSeries.from_samples()   those samples -> the coefficients c_n of
                                   f(t) = sum c_n e^{n 2 pi i t}
    FourierMachine                 the series -> vectors, circles, the drawn
                                   trace, a comet tail and a pen, all driven by
                                   one time tracker, plus a camera rig that
                                   follows the pen for zoomed-in shots

`FourierDrawingScene` strings them into a finished landscape video.  For a new
picture, subclass it and set `svg_file` (or override `get_source_mobject` to
draw a Tex / Text / hand-built VMobject instead).

Everything is deterministic: the same SVG and settings always give the same
coefficients and the same frames.
"""
from __future__ import annotations

import numpy as np

from manimlib import *

from custom.shorts import ShortsScene


# Palette, after the look of the 3Blue1Brown Fourier videos
FOURIER_CIRCLE_COLOR = "#58C4DD"
FOURIER_VECTOR_COLOR = "#ECECEC"
FOURIER_TRACE_COLOR = "#FFD54A"
FOURIER_TAIL_COLOR = "#FFF4C2"
FOURIER_TARGET_COLOR = GREY_B
FOURIER_ACCENT_COLOR = "#58C4DD"


# ---- 1. Picture -> closed loop of samples ----

def bezier_polyline(subpath: np.ndarray, samples_per_curve: int = 12) -> np.ndarray:
    """Dense polyline through a manim subpath of quadratic bezier curves."""
    a0 = subpath[0:-1:2]
    h = subpath[1::2]
    a1 = subpath[2::2]
    s = np.linspace(0, 1, samples_per_curve, endpoint=False)[:, None, None]
    points = (1 - s)**2 * a0 + 2 * s * (1 - s) * h + s**2 * a1
    points = points.transpose(1, 0, 2).reshape(-1, 3)
    return np.vstack([points, a1[-1:]])


def polyline_length(points: np.ndarray) -> float:
    return float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum())


def mobject_polylines(mobject: Mobject, min_length: float = 0.0) -> list[np.ndarray]:
    """Every subpath of every VMobject in the family, as a 2D polyline."""
    polylines = []
    for submob in mobject.family_members_with_points():
        if not isinstance(submob, VMobject):
            continue
        for subpath in submob.get_subpaths():
            if len(subpath) < 3:
                continue
            line = bezier_polyline(subpath)[:, :2]
            if polyline_length(line) > max(min_length, 1e-6):
                polylines.append(line)
    return polylines


def chain_polylines(polylines: list[np.ndarray], order: str = "nearest") -> np.ndarray:
    """Join separate strokes into one path the pen can follow without lifting.

    "nearest" greedily visits the closest remaining stroke next, entering a
    closed stroke at whichever of its points is nearest and an open stroke at
    whichever end is nearest.  That keeps the connecting jumps short, which is
    what makes a multi-part picture look like a single-line drawing.
    "document" keeps the SVG's own order.
    """
    if not polylines:
        raise ValueError("The picture has no drawable paths")
    if order == "document":
        return np.vstack(polylines)

    def is_closed(line):
        scale = max(np.ptp(line, axis=0).max(), 1e-6)
        return np.linalg.norm(line[0] - line[-1]) < 1e-3 * scale

    remaining = list(polylines)
    path = [remaining.pop(0)]
    while remaining:
        pen = path[-1][-1]
        best = None
        for index, line in enumerate(remaining):
            if is_closed(line):
                dists = np.linalg.norm(line - pen, axis=1)
                k = int(np.argmin(dists))
                candidate = (dists[k], index, "rotate", k)
            else:
                d_start = np.linalg.norm(line[0] - pen)
                d_end = np.linalg.norm(line[-1] - pen)
                candidate = (d_start, index, "keep", 0) if d_start <= d_end else (d_end, index, "reverse", 0)
            if best is None or candidate[0] < best[0]:
                best = candidate
        _, index, how, k = best
        line = remaining.pop(index)
        if how == "rotate":
            line = np.vstack([line[k:-1], line[:k + 1]])
        elif how == "reverse":
            line = line[::-1]
        path.append(line)
    return np.vstack(path)


def resample_closed(points: np.ndarray, n_samples: int) -> np.ndarray:
    """n points evenly spaced by arc length around the closed loop."""
    loop = np.vstack([points, points[:1]])
    seg = np.linalg.norm(np.diff(loop, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    targets = np.linspace(0, cum[-1], n_samples, endpoint=False)
    x = np.interp(targets, cum, loop[:, 0])
    y = np.interp(targets, cum, loop[:, 1])
    return x + 1j * y


def path_samples(
    mobject: Mobject,
    n_samples: int = 4096,
    order: str = "nearest",
    min_length: float = 0.0,
) -> np.ndarray:
    """Any drawable mobject -> one closed loop of complex samples, in the
    mobject's own world coordinates."""
    polylines = mobject_polylines(mobject, min_length=min_length)
    return resample_closed(chain_polylines(polylines, order), n_samples)


# ---- 2. Samples -> Fourier coefficients ----

def frequency_order(n_vectors: int, include_constant: bool = True) -> np.ndarray:
    """0, 1, -1, 2, -2, 3, ... -- the order the vectors are chained in."""
    freqs = [0] if include_constant else []
    k = 1
    while len(freqs) < n_vectors:
        freqs.append(k)
        if len(freqs) < n_vectors:
            freqs.append(-k)
        k += 1
    return np.array(freqs[:n_vectors], dtype=int)


class FourierSeries:
    """f(t) = origin + sum_k c_k e^{2 pi i freq_k t}, for t in [0, 1).

    Complex numbers are world coordinates x + iy.  `origin` is where the chain
    of vectors is pinned; the constant term c_0 then points from there to the
    picture's centre of mass.
    """

    def __init__(self, freqs: np.ndarray, coefs: np.ndarray, origin: complex = 0j):
        self.freqs = np.asarray(freqs, dtype=int)
        self.coefs = np.asarray(coefs, dtype=complex)
        self.origin = complex(origin)

    @classmethod
    def from_samples(
        cls,
        samples: np.ndarray,
        n_vectors: int = 101,
        pivot: complex | None = None,
        order: str = "frequency",
    ) -> "FourierSeries":
        """Coefficients from evenly spaced samples of one loop.

        With pivot=None the chain is pinned at the centre of mass, so the
        constant term vanishes and every vector in the chain rotates.
        order="magnitude" chains the vectors largest first instead.
        """
        n = len(samples)
        spectrum = np.fft.fft(samples) / n
        centroid = spectrum[0]
        origin = centroid if pivot is None else complex(pivot)
        freqs = frequency_order(n_vectors, include_constant=pivot is not None)
        coefs = spectrum[freqs % n].copy()
        coefs[freqs == 0] -= origin
        if order == "magnitude":
            index = np.argsort(-np.abs(coefs), kind="stable")
            freqs, coefs = freqs[index], coefs[index]
        return cls(freqs, coefs, origin)

    def truncated(self, n_vectors: int) -> "FourierSeries":
        return FourierSeries(self.freqs[:n_vectors], self.coefs[:n_vectors], self.origin)

    def __len__(self) -> int:
        return len(self.freqs)

    def terms(self, t: float) -> np.ndarray:
        return self.coefs * np.exp(TAU * 1j * self.freqs * t)

    def chain(self, t: float) -> np.ndarray:
        """Tail of every vector, then the pen: len(self) + 1 complex points."""
        return self.origin + np.concatenate([[0], np.cumsum(self.terms(t))])

    def evaluate(self, ts: np.ndarray) -> np.ndarray:
        ts = np.asarray(ts, dtype=float)
        return self.origin + np.exp(TAU * 1j * np.outer(ts, self.freqs)) @ self.coefs

    def points(self, ts: np.ndarray) -> np.ndarray:
        z = self.evaluate(ts)
        return np.column_stack([z.real, z.imag, np.zeros(len(z))])

    def derivative(self, ts: np.ndarray) -> np.ndarray:
        ts = np.asarray(ts, dtype=float)
        return np.exp(TAU * 1j * np.outer(ts, self.freqs)) @ (TAU * 1j * self.freqs * self.coefs)

    def bezier_points(self, n_curves: int = 3000) -> np.ndarray:
        """The loop as n quadratic beziers, t = k / n at the k-th anchor.

        Handles come from the exact derivative (the quadratic closest to the
        cubic Hermite segment), so the curve is smooth at every anchor and
        stays smooth under deep zoom with far fewer points than a polyline.
        """
        ts = np.linspace(0, 1, n_curves + 1)
        z = self.evaluate(ts)
        dz = self.derivative(ts)
        dt = 1 / n_curves
        points = np.empty(2 * n_curves + 1, dtype=complex)
        points[0::2] = z
        points[1::2] = 0.5 * (z[:-1] + z[1:]) + (dz[:-1] - dz[1:]) * dt / 8
        return to_3d(points)

    def curve(self, n_curves: int = 3000, **style) -> VMobject:
        """The whole approximated loop as a static curve."""
        curve = VMobject().set_points(self.bezier_points(n_curves))
        curve.set_stroke(**style)
        return curve


def partial_bezier_path(points: np.ndarray, alpha: float) -> np.ndarray:
    """The first `alpha` of a path of equal-duration quadratic beziers.

    Used instead of pointwise_become_partial, which copies joint angles from
    its source; a source curve that is never rendered has none computed, and
    the trace then shows small gaps at every joint.
    """
    n_curves = (len(points) - 1) // 2
    x = clip(alpha, 0, 1) * n_curves
    k = min(int(x), n_curves - 1)
    last = partial_quadratic_bezier_points(points[2 * k:2 * k + 3], 0, x - k)
    return np.vstack([points[:2 * k + 1], last[1:]])


def to_3d(z: complex | np.ndarray) -> np.ndarray:
    z = np.asarray(z)
    if z.ndim == 0:
        return np.array([z.real, z.imag, 0.0])
    return np.column_stack([z.real, z.imag, np.zeros(len(z))])


# ---- 3. Series -> animated machine ----

def arrow_outlines(
    starts: np.ndarray,
    ends: np.ndarray,
    width: float,
    tip_width_ratio: float = 4.0,
    max_width_to_length_ratio: float = 0.06,
    max_tip_to_length_ratio: float = 0.35,
) -> np.ndarray:
    """Bezier points for many arrow outlines at once, shape (n, 15, 3).

    Same proportions as manim's Arrow (short arrows get proportionally thinner
    shafts and smaller tips), but computed in one numpy pass rather than
    rebuilding a mobject per arrow, which matters with ~100 arrows per frame.
    """
    vects = ends - starts
    lengths = np.maximum(np.linalg.norm(vects, axis=1), 1e-8)[:, None]
    unit = vects / lengths
    normal = np.column_stack([-unit[:, 1], unit[:, 0], np.zeros(len(unit))])

    w = np.minimum(width, max_width_to_length_ratio * lengths)
    tip_w = tip_width_ratio * w
    tip_l = tip_w * np.sqrt(3) / 2
    shrink = np.minimum(1, max_tip_to_length_ratio * lengths / tip_l)
    tip_w, tip_l = tip_w * shrink, tip_l * shrink

    neck = lengths - tip_l
    along = np.hstack([0 * neck, neck, neck, lengths, neck, neck, 0 * neck, 0 * neck])
    across = np.hstack([w / 2, w / 2, tip_w / 2, 0 * w, -tip_w / 2, -w / 2, -w / 2, w / 2])
    corners = (
        starts[:, None, :]
        + along[:, :, None] * unit[:, None, :]
        + across[:, :, None] * normal[:, None, :]
    )
    points = np.empty((len(starts), 15, 3))
    points[:, 0::2] = corners
    points[:, 1::2] = 0.5 * (corners[:, :-1] + corners[:, 1:])
    return points


class FourierVector(VMobject):
    """A filled arrow whose points are set directly from `arrow_outlines`."""

    def __init__(
        self,
        start: np.ndarray = ORIGIN,
        end: np.ndarray = RIGHT,
        thickness: float = 1.6,
        color: ManimColor = FOURIER_VECTOR_COLOR,
        **kwargs,
    ):
        super().__init__(fill_color=color, fill_opacity=1, stroke_width=0, **kwargs)
        self.thickness = thickness
        self.put_start_and_end_on(start, end)

    def put_start_and_end_on(self, start, end) -> "FourierVector":
        width = self.thickness * Arrow.tickness_multiplier
        points = arrow_outlines(np.array([start]), np.array([end]), width)[0]
        self.set_points(points)
        return self

    def get_start(self) -> np.ndarray:
        points = self.get_points()
        return 0.5 * (points[0] + points[12])


class FourierMachine:
    """Vectors, circles, trace, tail and pen for one FourierSeries.

    Not a mobject itself: the layers are separate top-level mobjects with
    their own z_index, because manimgl draws a batched family's fills before
    all of its strokes, which would put circles on top of vectors.  Add them
    with `scene.add(*machine.layers())`, or pick layers individually.

    Time lives in `self.time` (cycles, so t=1 is one full drawing).  While
    `self.speed` is nonzero the time runs by itself; otherwise animate
    `self.time` directly.  Sizes that should look constant on screen --
    arrow thickness, the pen's glow, circle fading -- are rescaled every frame
    from the camera frame's height, so the machine looks right at any zoom.
    """

    def __init__(
        self,
        series: FourierSeries,
        frame: Mobject,
        home_height: float = FRAME_HEIGHT,
        vector_color: ManimColor = FOURIER_VECTOR_COLOR,
        vector_thickness: float = 1.6,
        circle_color: ManimColor = FOURIER_CIRCLE_COLOR,
        circle_width: float = 1.2,
        circle_opacity: float = 0.45,
        trace_color: ManimColor = FOURIER_TRACE_COLOR,
        trace_width: float = 3.0,
        trace_curves: int = 4000,
        tail_color: ManimColor = FOURIER_TAIL_COLOR,
        tail_width: float = 6.0,
        tail_length: float = 0.035,
        pen_radius: float = 0.12,
        zoom_slowdown: float = 0.85,
    ):
        self.series = series
        self.frame = frame
        self.home_height = home_height
        self.vector_thickness = vector_thickness
        self.circle_opacity = circle_opacity
        self.tail_width = tail_width
        self.tail_length = tail_length
        self.pen_radius = pen_radius
        self.zoom_slowdown = zoom_slowdown

        self.time = ValueTracker(0.0)
        self.speed = ValueTracker(0.0)
        # Camera rig: when locked, the frame is placed from these every frame
        self.zoom = ValueTracker(1.0)
        self.follow = ValueTracker(0.0)
        self.camera_locked = False
        self.home_center = frame.get_center().copy()

        radii = np.abs(series.coefs)
        chain = to_3d(series.chain(0))
        self.vectors = VGroup(*(
            FourierVector(chain[i], chain[i + 1], vector_thickness, vector_color)
            for i in range(len(series))
        ))
        self.circles = VGroup(*(
            Circle(radius=max(r, 1e-6), n_components=24).move_to(chain[i])
            for i, r in enumerate(radii)
        ))
        self.circles.set_stroke(circle_color, circle_width, circle_opacity)
        # A constant term does not spin, so it gets no circle
        for circle, freq in zip(self.circles, series.freqs):
            if freq == 0:
                circle.set_stroke(opacity=0)
        self.radii = radii

        self.trace_points = series.bezier_points(trace_curves)
        self.trace = VMobject()
        self.trace.set_stroke(trace_color, trace_width)
        self.tail = VMobject()
        self.tail.set_stroke(tail_color, tail_width)
        self.tail_samples = 60
        self.pen = GlowDot(chain[-1], color=tail_color, radius=pen_radius, glow_factor=1.5)

        for z, mob in enumerate([self.circles, self.trace, self.tail, self.vectors]):
            mob.z_index = z
        self.pen.z_index = 4

        self.driver = Mobject()
        self.driver.add_updater(lambda m, dt: self.update(dt))
        self.refresh()

    # Layers and state

    def layers(self) -> list[Mobject]:
        return [self.driver, self.circles, self.trace, self.tail, self.vectors, self.pen]

    def get_zoom(self) -> float:
        return self.home_height / self.frame.get_height()

    def get_t(self) -> float:
        return self.time.get_value()

    def get_tip(self, t: float | None = None) -> np.ndarray:
        t = self.get_t() if t is None else t
        return to_3d(self.series.chain(t)[-1])

    def set_time(self, t: float) -> "FourierMachine":
        self.time.set_value(t)
        self.refresh()
        return self

    # Per-frame update

    def update(self, dt: float) -> None:
        speed = self.speed.get_value()
        if speed != 0:
            self.time.increment_value(dt * speed / self.get_zoom()**self.zoom_slowdown)
        self.refresh()

    def refresh(self) -> None:
        t = self.get_t()
        chain = to_3d(self.series.chain(t))
        tip = chain[-1]

        if self.camera_locked:
            self.frame.set_height(self.home_height / self.zoom.get_value())
            self.frame.move_to(interpolate(self.home_center, tip, self.follow.get_value()))

        frame_height = self.frame.get_height()
        frame_scale = frame_height / self.home_height

        width = self.vector_thickness * Arrow.tickness_multiplier * frame_scale
        outlines = arrow_outlines(chain[:-1], chain[1:], width)
        for arrow, points in zip(self.vectors, outlines):
            arrow.set_points(points)

        # Circles fade out as they shrink toward a pixel, and come back when
        # the camera zooms in on them
        apparent = self.radii / frame_height
        fade = np.clip((apparent - 0.0015) / 0.008, 0, 1)
        opacities = np.where(self.series.freqs == 0, 0, self.circle_opacity * fade)
        for circle, center, opacity in zip(self.circles, chain[:-1], opacities):
            circle.shift(center - circle.get_center())
            circle.set_stroke(opacity=opacity)

        # Trace: everything drawn so far; after one cycle, the whole loop
        self.trace.set_points(partial_bezier_path(self.trace_points, t))

        # Comet tail just behind the pen, shortened when zoomed in so it stays
        # smooth on screen
        length = self.tail_length / self.get_zoom()**0.8
        start = max(t - length, 0) if t < 1 else t - length
        if t - start > 1e-6:
            ts = np.linspace(start, t, self.tail_samples)
            self.tail.set_points_as_corners(self.series.points(ts))
            ramp = np.linspace(0, 1, self.tail.get_num_points())
            self.tail.set_stroke(width=self.tail_width * ramp, opacity=ramp**0.7)
        else:
            self.tail.clear_points()

        self.pen.move_to(tip)
        self.pen.set_radius(self.pen_radius * frame_scale)


# ---- 4. A finished scene ----

class FourierDrawingScene(ShortsScene):
    """Landscape 16:9 video that draws `svg_file` with rotating vectors.

    Render with `./render.sh -q hd <file>` (or -q 4k-landscape via -q 3840x2160).
    Beats, each renderable on its own with -s:

        intro        the picture is traced as one loop, parametrised by t
        spectrum     the lowest frequencies, each spinning on its own
        assemble     they chain tip to tail; the rest of the vectors join
        draw         one full cycle draws the picture
        zoom         the camera dives in after the pen, then pulls back out
        convergence  more vectors, closer fit
    """

    frame_width = FRAME_HEIGHT * 16 / 9
    frame_height = FRAME_HEIGHT

    sections = ["intro", "spectrum", "assemble", "draw", "zoom", "convergence"]

    # The picture
    svg_file: str = "eighth_note.svg"
    title: str = "Complex Fourier series"
    drawing_height: float = 6.6
    drawing_center: np.ndarray = np.array([1.6, 0.0, 0.0])

    # The series
    n_vectors: int = 101
    n_samples: int = 4096
    path_order: str = "nearest"    # how separate strokes are joined
    vector_order: str = "frequency"  # or "magnitude"
    pivot: np.ndarray | None = None  # None pins the chain at the centre of mass

    # Timing
    cycle_duration: float = 18.0     # seconds for one full drawing
    zoom_levels: tuple = (6.0, 24.0)
    zoom_hold: float = 7.0
    spectrum_range: int = 3          # show frequencies -3..3
    convergence_counts: tuple = (3, 11, 31, None)  # None = all vectors

    def setup(self) -> None:
        super().setup()
        aspect = self.frame_width / self.frame_height
        if abs(self.camera.get_aspect_ratio() - aspect) > 0.01:
            raise ValueError(
                f"{type(self).__name__} is a 16:9 landscape scene but the render is "
                f"{self.camera.get_pixel_width()}x{self.camera.get_pixel_height()}. "
                "Render with ./render.sh -q hd (or -q 3840x2160)."
            )
        self.target = self.get_target()
        pivot = None if self.pivot is None else complex(self.pivot[0], self.pivot[1])
        self.series = FourierSeries.from_samples(
            path_samples(self.target, self.n_samples, self.path_order),
            n_vectors=self.n_vectors,
            pivot=pivot,
            order=self.vector_order,
        )
        self.machine = FourierMachine(self.series, self.frame, home_height=self.frame_height)
        self.hud = self.get_hud()

    # Building blocks; override these to restyle

    def get_source_mobject(self) -> VMobject:
        """The picture to draw.  Override to use Tex, Text, or custom shapes."""
        return SVGMobject(self.svg_file)

    def get_target(self) -> VMobject:
        target = self.get_source_mobject()
        target.set_height(self.drawing_height)
        target.move_to(self.drawing_center)
        target.set_fill(opacity=0)
        target.set_stroke(FOURIER_TARGET_COLOR, 1.5, 0.3)
        return target

    def get_hud(self) -> VGroup:
        title = Text(self.title, font_size=40)
        title.to_corner(UL, buff=0.5)
        formula = Tex(
            R"f(t) = \sum_{n} c_n \, e^{n \cdot 2 \pi i t}",
            t2c={"c_n": FOURIER_CIRCLE_COLOR, "n": FOURIER_CIRCLE_COLOR},
            font_size=38,
        )
        formula.next_to(title, DOWN, buff=0.35, aligned_edge=LEFT)
        count = Text(f"{len(self.series)} vectors", font_size=26)
        count.set_color(GREY_B)
        count.next_to(formula, DOWN, buff=0.35, aligned_edge=LEFT)
        hud = VGroup(title, formula, count)
        hud.fix_in_frame()
        return hud

    def get_zoom_badge(self) -> VGroup:
        label = Text("zoom", font_size=26).set_color(GREY_B)
        value = DecimalNumber(1.0, num_decimal_places=1, font_size=34)
        value.set_color(FOURIER_ACCENT_COLOR)
        times = Tex(R"\times", font_size=34).set_color(FOURIER_ACCENT_COLOR)
        badge = VGroup(label, times, value).arrange(RIGHT, buff=0.15)
        badge.to_corner(DL, buff=0.5)
        # set_value rebuilds the digits, which would drop the fixed-in-frame flag
        value.add_updater(lambda m: m.set_value(self.machine.get_zoom()).fix_in_frame())
        badge.fix_in_frame()
        return badge

    def get_focus_box(self, zoom: float) -> Rectangle:
        box = Rectangle(self.frame_width / zoom, self.frame_height / zoom)
        box.set_stroke(FOURIER_ACCENT_COLOR, 2)
        box.add_updater(lambda m: m.move_to(self.machine.get_tip()))
        return box

    # Making the scene renderable one section at a time

    def machine_on_screen(self) -> bool:
        return self.machine.vectors in self.mobjects

    def ensure_machine(self, t: float | None = None) -> None:
        """Put the full machine up without animation, if an earlier section
        that would have built it was skipped."""
        if t is not None and self.machine.get_t() < t:
            self.machine.set_time(t)
        if not self.machine_on_screen():
            self.add(self.target, *self.machine.layers())
        if self.hud not in self.mobjects:
            self.add(self.hud)

    def run_cycles(self, cycles: float, duration: float) -> None:
        """Advance time by `cycles` at a constant rate over `duration` seconds."""
        time = self.machine.time
        self.play(
            time.animate.set_value(time.get_value() + cycles),
            run_time=duration,
            rate_func=linear,
        )

    # Sections

    def intro(self) -> None:
        title = Text("Drawing with circles", font_size=60)
        subtitle = Text("any closed path is a sum\nof spinning vectors", font_size=30, alignment="LEFT")
        subtitle.set_color(GREY_B)
        heading = VGroup(title, subtitle).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        heading.to_edge(LEFT, buff=0.6).set_y(0.8)
        heading.fix_in_frame()

        outline = self.target.copy()
        outline.set_stroke(WHITE, 3, 1)
        self.play(FadeIn(title, 0.2 * UP), run_time=1.0)
        self.play(FadeIn(subtitle), ShowCreation(outline, run_time=3.5, rate_func=smooth))
        self.wait(0.5)

        # The picture as a function of time: one loop, t from 0 to 1
        pen = GlowDot(self.machine.get_tip(0), color=FOURIER_TRACE_COLOR, radius=0.2)
        t_tracker = ValueTracker(0)
        pen.add_updater(lambda m: m.move_to(self.machine.get_tip(t_tracker.get_value())))
        t_label = VGroup(
            Tex("t = ", font_size=40),
            DecimalNumber(0, num_decimal_places=2, font_size=40),
        ).arrange(RIGHT, buff=0.12)
        t_label.to_corner(DL, buff=0.6)
        t_label[1].add_updater(lambda m: m.set_value(t_tracker.get_value()).fix_in_frame())
        f_label = Tex("f(t)", font_size=40).set_color(FOURIER_TRACE_COLOR)
        f_label.add_updater(lambda m: m.next_to(pen, UR, buff=0.05))
        VGroup(t_label).fix_in_frame()

        self.play(
            FadeOut(subtitle),
            outline.animate.set_stroke(FOURIER_TARGET_COLOR, 1.5, 0.3),
            FadeIn(pen), FadeIn(t_label), FadeIn(f_label),
        )
        self.play(t_tracker.animate.set_value(1), run_time=5, rate_func=linear)
        self.wait(0.5)
        self.play(FadeOut(VGroup(title, t_label, f_label)), FadeOut(pen))
        self.remove(outline)
        self.add(self.target)

    def spectrum(self) -> None:
        if self.target not in self.mobjects:
            self.add(self.target)
        machine = self.machine
        k = self.spectrum_range
        freqs = list(range(-k, k + 1))

        # One slot per frequency, drawn larger than life so each is visible
        index_of = {int(f): i for i, f in enumerate(self.series.freqs)}
        mags = [abs(self.series.coefs[index_of[f]]) if f in index_of else 0 for f in freqs]
        max_mag = max(mags) or 1
        slots = VGroup()
        for f, mag in zip(freqs, mags):
            radius = 0.62 * np.sqrt(mag / max_mag) if mag > 0 else 0
            slot = VGroup()
            slot.freq = f
            slot.radius = max(radius, 0.1)
            slot.coef = self.series.coefs[index_of[f]] if f in index_of else 0
            circle = Circle(radius=slot.radius)
            circle.set_stroke(FOURIER_CIRCLE_COLOR, 1.5, 0.6)
            arrow = FourierVector(ORIGIN, RIGHT, thickness=2.5)
            label = Integer(f, font_size=44)
            slot.add(circle, arrow, label)
            slots.add(slot)
        for i, slot in enumerate(slots):
            slot[0].move_to(1.7 * (i - k) * RIGHT + 2.55 * UP)
            slot[2].move_to(slot[0].get_center() + 1.05 * DOWN)
        dots = VGroup(
            Tex(R"\cdots", font_size=48).next_to(slots[0][0], LEFT, buff=0.5),
            Tex(R"\cdots", font_size=48).next_to(slots[-1][0], RIGHT, buff=0.5),
        )

        def update_arrows(group):
            t = machine.get_t()
            for slot in slots:
                center = slot[0].get_center()
                if slot.coef == 0:
                    slot[1].set_opacity(0)
                    continue
                z = slot.coef / abs(slot.coef) * np.exp(TAU * 1j * slot.freq * t)
                slot[1].put_start_and_end_on(center, center + slot.radius * to_3d(z))

        arrows = VGroup(*(slot[1] for slot in slots))
        arrows.add_updater(update_arrows)
        update_arrows(arrows)

        panel = Rectangle(self.frame_width, 3.2)
        panel.set_fill(BLACK, 0.85).set_stroke(width=0)
        panel.move_to(2.45 * UP)

        caption = Text("vector n spins n turns per second", font_size=30)
        caption.set_color(GREY_B)
        caption.move_to(0.35 * DOWN + 2.8 * LEFT)
        formula = Tex(
            R"f(t) = \cdots + c_{-1} e^{-1 \cdot 2 \pi i t} + c_0 + c_1 e^{1 \cdot 2 \pi i t} + \cdots",
            t2c={"c_{-1}": FOURIER_CIRCLE_COLOR, "c_1": FOURIER_CIRCLE_COLOR, "c_0": FOURIER_CIRCLE_COLOR},
            font_size=40,
        )
        formula.next_to(caption, DOWN, buff=0.35)
        backdrop = BackgroundRectangle(VGroup(caption, formula), buff=0.25, fill_opacity=0.85)

        self.play(
            self.target.animate.set_stroke(opacity=0.15),
            FadeIn(panel),
            LaggedStart(*(FadeIn(slot, 0.3 * DOWN) for slot in slots), lag_ratio=0.1),
            FadeIn(dots),
            run_time=2,
        )
        self.add(arrows)
        self.play(FadeIn(backdrop), Write(formula), FadeIn(caption), run_time=2)
        self.run_cycles(1.0, 8.0)
        self.machine.set_time(0)
        self.spectrum_slots = slots
        self.spectrum_extras = VGroup(panel, dots, caption, formula, backdrop)

    def assemble(self) -> None:
        machine = self.machine
        slots = getattr(self, "spectrum_slots", VGroup())
        extras = getattr(self, "spectrum_extras", VGroup())
        if self.target not in self.mobjects:
            self.add(self.target)
        machine.set_time(0)
        for mob in slots:
            mob.clear_updaters()
        arrows = VGroup(*(slot[1] for slot in slots))
        arrows.clear_updaters()

        # Low frequencies fly from the strip to their place in the chain
        index_of = {int(f): i for i, f in enumerate(self.series.freqs)}
        flights = [
            TransformFromCopy(slot[1], machine.vectors[index_of[slot.freq]])
            for slot in slots if slot.freq in index_of
        ]
        flown = {index_of[slot.freq] for slot in slots if slot.freq in index_of}
        rest = [v for i, v in enumerate(machine.vectors) if i not in flown]

        # The driver stays off until the entrances finish, or its per-frame
        # refresh would overwrite what GrowArrow and FadeIn are animating
        # (With the spectrum section skipped there is nothing to fly in, and
        # every vector simply grows in place)
        if flights:
            self.play(
                LaggedStart(*flights, lag_ratio=0.15),
                self.target.animate.set_stroke(opacity=0.3),
                run_time=2.5,
            )
        self.play(
            FadeOut(slots), FadeOut(extras),
            self.target.animate.set_stroke(opacity=0.3),
            LaggedStart(*(GrowArrow(v) for v in rest), lag_ratio=0.02),
            FadeIn(machine.circles, lag_ratio=0.02),
            run_time=3,
        )
        self.play(FadeIn(self.hud, lag_ratio=0.1), run_time=1)
        # The entrances left individual arrows in the scene; swap them for the
        # layer groups, in drawing order
        self.remove(*machine.layers(), *machine.vectors, *machine.circles)
        self.add(*machine.layers(), self.hud)
        self.wait(0.5)

    def draw(self) -> None:
        self.ensure_machine(t=0)
        self.add(self.machine.pen)
        self.run_cycles(1.0, self.cycle_duration)
        self.machine.set_time(1.0)
        self.wait(1)

    def zoom(self) -> None:
        self.ensure_machine(t=1.0)
        machine = self.machine
        badge = self.get_zoom_badge()
        first, *deeper = self.zoom_levels

        box = self.get_focus_box(first)
        machine.speed.set_value(1 / self.cycle_duration)
        self.play(ShowCreation(box), FadeIn(badge), self.hud.animate.set_opacity(0.35), run_time=1.5)

        machine.home_center = self.frame.get_center().copy()
        machine.camera_locked = True
        self.play(
            machine.follow.animate.set_value(1),
            machine.zoom.animate.set_value(first),
            run_time=3,
        )
        self.play(FadeOut(box), run_time=0.5)
        self.wait(self.zoom_hold)
        for level in deeper:
            self.play(machine.zoom.animate.set_value(level), run_time=3)
            self.wait(self.zoom_hold)
        self.play(
            machine.zoom.animate.set_value(1),
            machine.follow.animate.set_value(0),
            self.hud.animate.set_opacity(1),
            run_time=4,
        )
        self.play(FadeOut(badge))
        machine.camera_locked = False
        machine.speed.set_value(0)
        self.wait(0.5)

    def convergence(self) -> None:
        self.ensure_machine(t=1.0)
        machine = self.machine
        counts = [len(self.series) if n is None else n for n in self.convergence_counts]

        # Retire the machine; its finished drawing stays for the comparison.
        # Stop the driver first so it does not fight the fades.
        self.remove(machine.driver)
        self.play(
            FadeOut(machine.vectors), FadeOut(machine.circles),
            FadeOut(machine.pen), FadeOut(machine.tail),
            FadeOut(self.hud),
            run_time=1.5,
        )

        panels = VGroup()
        for n in counts:
            outline = self.target.copy().set_stroke(opacity=0.25)
            curve = self.series.truncated(n).curve(2000, color=FOURIER_TRACE_COLOR, width=2.5)
            label = Text(f"{n} vectors", font_size=30)
            label.set_color(GREY_A)
            panel = VGroup(outline, curve)
            panel.set_height(5.0)
            label.next_to(panel, DOWN, buff=0.35)
            panels.add(VGroup(panel, label))
        panels.arrange(RIGHT, buff=0.6, aligned_edge=DOWN)
        panels.set_max_width(self.frame_width - 1.0)
        panels.move_to(0.5 * DOWN)

        heading = Text("More vectors, closer fit", font_size=48)
        heading.to_edge(UP, buff=0.6)

        # The finished drawing becomes the last panel
        last_curve = panels[-1][0][1]
        self.play(
            ReplacementTransform(machine.trace, last_curve),
            ReplacementTransform(self.target, panels[-1][0][0]),
            FadeIn(panels[-1][1]),
            FadeIn(heading, 0.2 * DOWN),
            run_time=2,
        )
        self.play(
            LaggedStart(*(
                AnimationGroup(FadeIn(p[0][0]), ShowCreation(p[0][1]), FadeIn(p[1]))
                for p in panels[:-1]
            ), lag_ratio=0.35),
            run_time=4,
        )
        self.wait(3)
        self.play(FadeOut(VGroup(panels, heading)), run_time=1.5)
