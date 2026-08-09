from manim_imports_ext import *


CIRCLE_COLOR = "#7FB3FF"
SQUARE_COLOR = "#5BD98A"
HEX_COLOR = "#FFB86B"
LABEL_COLOR = GREY_A


def ngon_radius(theta, n: int, vertex_at: float = 0.0):
    """Polar radius of a regular n-gon of circumradius 1.

    `vertex_at` is the angle of one vertex, so the shape can be oriented the
    same way it is drawn.  Edge normals sit half a step away from the
    vertices, which is where the apothem cos(pi/n) is attained.
    """
    step = TAU / n
    psi = np.mod(theta - vertex_at, step) - step / 2
    return np.cos(PI / n) / np.cos(psi)


def circle_radius(theta):
    return np.ones_like(np.asarray(theta, dtype=float))


# (name, radius function, colour, how the shape is drawn)
SHAPES = [
    ("circle", circle_radius, CIRCLE_COLOR, None),
    ("square", lambda t: ngon_radius(t, 4, PI / 4), SQUARE_COLOR, (4, PI / 4)),
    ("hexagon", lambda t: ngon_radius(t, 6, 0.0), HEX_COLOR, (6, 0.0)),
]


class WaveFromShapes(BrandOutroMixin, ShortsScene):
    # Rolling shapes tracing their own waves.  Render with:
    #   ./render.sh _2026/Functions/wave_from_shapes.py
    # or one beat with:
    #   ./render.sh -s name_the_functions _2026/Functions/wave_from_shapes.py
    sections = ["trace", "name_the_functions", "generalise", "outro"]

    omega = 1.4              # radians per second of the sweeping arm
    shape_radius = 0.70
    shape_x = -2.45
    plot_x0 = -1.15
    plot_x1 = 3.55
    row_ys = [3.9, 1.9, -0.1]
    span = 2.0 * TAU         # phase across the plot window
    amplitude = 0.72
    heading_y = 5.5
    lower_y = -1.7           # where the text block under the rows starts

    # ---- the moving picture ----

    def build_rows(self):
        """Shape, sweeping arm, tie line and scrolling wave for each row.

        Split into `static` and `dynamic`: anything wrapped in always_redraw
        re-`become`s itself every frame, which overwrites the opacity a FadeIn
        is setting, so those parts have to be added rather than faded in.
        """
        theta = ValueTracker(0.0)
        theta.add_updater(lambda m, dt: m.increment_value(self.omega * dt))
        self.add(theta)
        self.theta = theta

        static, dynamic = Group(), Group()
        for (name, radius_fn, color, poly), y in zip(SHAPES, self.row_ys):
            centre = np.array([self.shape_x, y, 0.0])

            if poly is None:
                outline = Circle(radius=self.shape_radius)
                outline.move_to(centre)
            else:
                n, vertex_at = poly
                outline = Polygon(*[
                    centre + self.shape_radius * np.array(
                        [np.cos(vertex_at + k * TAU / n),
                         np.sin(vertex_at + k * TAU / n), 0.0]
                    )
                    for k in range(n)
                ])
            outline.set_stroke(color, 3).set_fill(opacity=0)

            baseline = Line(
                np.array([self.plot_x0, y, 0.0]),
                np.array([self.plot_x1, y, 0.0]),
            )
            baseline.set_stroke(GREY_D, 1.5)
            pivot = Dot(centre, radius=0.035).set_fill(color, 1)

            static.add(outline, baseline, pivot)
            dynamic.add(*self.moving_parts(centre, y, radius_fn, color))

        rows = Group(static, dynamic)
        rows.static, rows.dynamic = static, dynamic
        return rows

    def moving_parts(self, centre, y, radius_fn, color):
        radius = self.shape_radius

        def tip():
            t = self.theta.get_value()
            r = float(radius_fn(np.array([t]))[0]) * radius
            return centre + r * np.array([np.cos(t), np.sin(t), 0.0])

        arm = always_redraw(lambda: Line(
            centre, tip(), stroke_color=color, stroke_width=2.5,
        ))
        knob = always_redraw(lambda: Dot(tip(), radius=0.05).set_fill(color, 1))
        tie = always_redraw(lambda: DashedLine(
            tip(), np.array([self.plot_x0, tip()[1], 0.0]),
            stroke_color=GREY_C, stroke_width=1.5, dash_length=0.06,
        ))
        wave = always_redraw(lambda: self.make_wave(y, radius_fn, color))
        seam = always_redraw(lambda: Dot(
            np.array([self.plot_x0, self.height_at(y, radius_fn,
                                                   self.theta.get_value()), 0.0]),
            radius=0.05,
        ).set_fill(color, 1))
        return [tie, arm, wave, knob, seam]

    def height_at(self, y, radius_fn, t):
        return y + self.amplitude * float(radius_fn(np.array([t]))[0]) * np.sin(t)

    def make_wave(self, y, radius_fn, color, samples: int = 260):
        """The window holds the recent past: newest value at the left edge,
        older values pushed right.  Early on there is less history than the
        window can show, so the trace grows out of the left."""
        t_now = self.theta.get_value()
        shown = min(self.span, max(t_now, 1e-3))
        width = (self.plot_x1 - self.plot_x0) * shown / self.span
        xs = np.linspace(self.plot_x0, self.plot_x0 + width, samples)
        frac = (xs - self.plot_x0) / (self.plot_x1 - self.plot_x0)
        ts = t_now - frac * self.span
        ys = y + self.amplitude * radius_fn(ts) * np.sin(ts)
        curve = VMobject()
        curve.set_points_as_corners(
            np.stack([xs, ys, np.zeros_like(xs)], axis=1)
        )
        curve.set_stroke(color, 3)
        return curve

    def get_rows(self):
        return self.lazy("rows", self.build_rows)

    def make_headings(self):
        actions = Text("Your actions", font_size=38).set_color(LABEL_COLOR)
        actions.move_to(np.array([self.shape_x, self.heading_y, 0.0]))
        future = Text("Your future", font_size=38).set_color(LABEL_COLOR)
        future.move_to(np.array([1.2, self.heading_y, 0.0]))
        return VGroup(actions, future)

    def get_headings(self):
        return self.lazy("headings", self.make_headings)

    # ---- sections ----

    def trace(self):
        headings = self.make_headings()
        rows = self.build_rows()

        caption = Text("The future depends on what you do today.", font_size=30)
        caption.set_color(GREY_B)
        caption.set_max_width(6.9)
        caption.set_y(self.lower_y)

        self.play(FadeIn(headings, lag_ratio=0.3), run_time=0.9)
        self.play(FadeIn(rows.static, lag_ratio=0.15), run_time=1.2)
        self.add(rows.dynamic)
        self.wait(5.5)
        self.play(FadeIn(caption, 0.15 * UP), run_time=0.9)
        self.wait(2.0)

        self.set_state("headings", headings)
        self.set_state("rows", rows)
        self.set_state("caption", caption)

    def name_the_functions(self):
        self.get_headings()
        self.get_rows()
        caption = self.lazy("caption", self.make_caption)

        title = Text("Same sweep, different shape", font_size=32)
        title.set_color(GREY_A)
        title.set_y(self.lower_y)

        lines = VGroup(
            Tex(R"\text{circle:} \quad y = \sin\theta",
                font_size=32).set_color(CIRCLE_COLOR),
            Tex(R"\text{square:} \quad y = \frac{\sin\theta}"
                R"{\max(|\cos\theta|, |\sin\theta|)}",
                font_size=32).set_color(SQUARE_COLOR),
            Tex(R"\text{hexagon:} \quad y = \frac{\cos 30^\circ \, \sin\theta}"
                R"{\cos\big((\theta \bmod 60^\circ) - 30^\circ\big)}",
                font_size=32).set_color(HEX_COLOR),
        )
        for line in lines:
            line.set_max_width(6.9)
        lines.arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        lines.set_x(0)
        lines.next_to(title, DOWN, buff=0.45)

        self.play(FadeOut(caption, 0.2 * UP), FadeIn(title, 0.2 * UP), run_time=0.8)
        for line in lines:
            self.play(FadeIn(line, 0.15 * DOWN), run_time=0.8)
            self.wait(0.5)
        self.wait(1.0)

        self.set_state("fn_title", title)
        self.set_state("fn_lines", lines)

    def generalise(self):
        self.get_headings()
        self.get_rows()
        title = self.lazy("fn_title", self.make_fn_title)
        lines = self.lazy("fn_lines", self.make_fn_lines)

        general = Tex(R"y(\theta) = r(\theta)\, \sin\theta", font_size=48)
        general.set_color(YELLOW)
        general.set_y(self.lower_y - 1.0)
        box = SurroundingRectangle(general, color=YELLOW, buff=0.25)
        box.set_stroke(width=3)

        note = TexText(R"$r$ is the shape's own radius, and $n \to \infty$"
                       R" brings back the circle", font_size=30)
        note.set_color(GREY_B)
        note.set_max_width(6.9)
        note.next_to(box, DOWN, buff=0.45)

        self.play(
            FadeOut(lines, 0.2 * UP),
            FadeOut(title, 0.2 * UP),
            run_time=0.7,
        )
        self.play(Write(general), run_time=1.2)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FadeIn(note, 0.15 * DOWN), run_time=0.8)
        self.wait(2.4)

    # ---- static rebuilds, so any section renders on its own ----

    def make_caption(self):
        caption = Text("The future depends on what you do today.", font_size=30)
        caption.set_color(GREY_B)
        caption.set_max_width(6.9)
        caption.set_y(self.lower_y)
        return caption

    def make_fn_title(self):
        title = Text("Same sweep, different shape", font_size=32)
        title.set_color(GREY_A)
        title.set_y(self.lower_y)
        return title

    def make_fn_lines(self):
        lines = VGroup(
            Tex(R"\text{circle:} \quad y = \sin\theta",
                font_size=32).set_color(CIRCLE_COLOR),
            Tex(R"\text{square:} \quad y = \frac{\sin\theta}"
                R"{\max(|\cos\theta|, |\sin\theta|)}",
                font_size=32).set_color(SQUARE_COLOR),
            Tex(R"\text{hexagon:} \quad y = \frac{\cos 30^\circ \, \sin\theta}"
                R"{\cos\big((\theta \bmod 60^\circ) - 30^\circ\big)}",
                font_size=32).set_color(HEX_COLOR),
        )
        for line in lines:
            line.set_max_width(6.9)
        lines.arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        lines.set_x(0)
        lines.next_to(self.lazy("fn_title", self.make_fn_title), DOWN, buff=0.45)
        return lines
