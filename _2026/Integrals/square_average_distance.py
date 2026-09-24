from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Integrals/square_average_distance.py
#
# Average distance between two random points in the unit square.
#
# Simulation: 3000 random pairs (seed 3) average 0.5217.
#
# Exact: with gaps u = |x1 - x2|, v = |y1 - y2| the distance is sqrt(u^2 + v^2).
# A gap between two uniform numbers has density 2(1 - u) (small gaps are more
# likely), so
#   E = int_0^1 int_0^1 sqrt(u^2 + v^2) 4(1-u)(1-v) du dv.
# The integrand is symmetric in u, v: take twice the triangle below the
# diagonal, in polar coordinates (r from 0 to sec(theta), theta to pi/4):
#   E = 8 int_0^{pi/4} int_0^{sec} r^2 (1 - r cos)(1 - r sin) dr dtheta
#     = 8 int_0^{pi/4} (sec^3/12 - sec^3 tan/20) dtheta
#     = 8 [ (sec tan + ln|sec + tan|)/24 - sec^3/60 ]_0^{pi/4}
#     = (2 + sqrt(2) + 5 ln(1 + sqrt(2))) / 15 = 0.52141
# Checked against scipy's dblquad on the first integral and quad on the
# theta integral.

EXACT = (2 + np.sqrt(2) + 5 * np.log(1 + np.sqrt(2))) / 15
N_PAIRS = 3000
RNG = np.random.default_rng(3)
FIRST, SECOND = RNG.random((N_PAIRS, 2)), RNG.random((N_PAIRS, 2))
DISTANCES = np.hypot(*(FIRST - SECOND).T)
RUNNING = np.cumsum(DISTANCES) / np.arange(1, N_PAIRS + 1)

SIDE = 4.0
SQUARE_CENTER = 2.05 * UP
GRAPH_BOX = (6.4, 2.0)                  # width, height
GRAPH_CENTER = 2.35 * DOWN
GRAPH_Y = (0.35, 0.75)                  # running average range shown

POINT = WHITE
PAIR = "#FFD166"
TRAIL = "#58C4DD"
GAP_U = "#FF6B9A"
GAP_V = "#5BD98A"
REGION = "#58C4DD"
EXACT_COLOR = "#FF9F43"
CAPTION_Y = -4.55

EXAMPLES = [((0.18, 0.72), (0.43, 0.38)), ((0.08, 0.12), (0.86, 0.9)), ((0.62, 0.55), (0.78, 0.63))]


class SquareAverageDistance(MockTestShort):
    """Average distance of two random points in a unit square."""

    test = ""
    card_top_buff = 0.6
    step_buff = 0.42

    problem_tex = (
        R"\text{Two random points in a unit square.}\\"
        R"\text{What is their average distance?}"
    )

    sections = [
        "pose",
        "examples",
        "simulate",
        "gaps",
        "polar",
        "integrate",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = SQUARE_CENTER[1] - SIDE / 2 - 0.5
        return card

    # The square, as a map from [0, 1]^2 to the screen

    def to_screen(self, p, square=None):
        square = square or self.get_square()
        corner = square.get_corner(DL)
        side = square.get_width()
        return corner + side * (p[0] * RIGHT + p[1] * UP)

    def make_square(self):
        return Square(SIDE).set_stroke(WHITE, 3).move_to(SQUARE_CENTER)

    def get_square(self):
        return self.lazy("square", self.make_square)

    def pair(self, p, q, color=PAIR, width=4, radius=0.07):
        line = Line(self.to_screen(p), self.to_screen(q)).set_stroke(color, width)
        dots = VGroup(*[Dot(self.to_screen(x), radius=radius).set_fill(POINT) for x in (p, q)])
        return VGroup(line, dots)

    def caption(self, message, wait=1.3, tex=False):
        text = Tex(message, font_size=30) if tex else Text(message, font_size=26)
        text.set_color(self.note_color)
        text.set_max_width(7.4).move_to(CAPTION_Y * UP)
        self.play(FadeIn(text, 0.15 * UP), run_time=0.4)
        self.wait(wait)
        self.play(FadeOut(text), run_time=0.3)

    # Sections

    def examples(self):
        self.get_card()
        square = self.make_square()
        side = Tex("1", font_size=34).next_to(square, DOWN, buff=0.15)
        self.play(ShowCreation(square), FadeIn(side), run_time=0.8)
        self.set_state("square", square)

        # A few pairs and their distances
        shown = None
        for p, q in EXAMPLES:
            pair = self.pair(p, q)
            value = DecimalNumber(np.hypot(p[0] - q[0], p[1] - q[1]), num_decimal_places=2, font_size=32)
            value.set_color(PAIR).next_to(pair[0].get_center(), UR, buff=0.08)
            anims = [FadeOut(shown)] if shown else []
            self.play(*anims, FadeIn(pair[1], scale=0.5), ShowCreation(pair[0]), FadeIn(value), run_time=0.7)
            self.wait(0.35)
            shown = VGroup(pair, value)
        self.play(FadeOut(shown), FadeOut(side), run_time=0.4)

    def simulate(self):
        square = self.get_square()

        # Readouts: how many pairs, and their running average
        count = Integer(N_PAIRS, font_size=36)      # laid out at its widest
        average = DecimalNumber(0, num_decimal_places=4, font_size=36).set_color(PAIR)
        readout = VGroup(
            VGroup(Tex("n =", font_size=36), count).arrange(RIGHT, buff=0.15),
            VGroup(Tex(R"\text{average} \approx", font_size=36), average).arrange(RIGHT, buff=0.15),
        ).arrange(RIGHT, buff=0.8).next_to(square, DOWN, buff=0.35)
        count.edge_to_fix = LEFT
        average.edge_to_fix = LEFT
        count.set_value(0)

        # The running average over time
        frame = Rectangle(*GRAPH_BOX).set_stroke(GREY_B, 1.5).move_to(GRAPH_CENTER)

        def g(n, value):
            x = frame.get_left()[0] + GRAPH_BOX[0] * n / N_PAIRS
            y = frame.get_bottom()[1] + GRAPH_BOX[1] * (np.clip(value, *GRAPH_Y) - GRAPH_Y[0]) / (GRAPH_Y[1] - GRAPH_Y[0])
            return np.array([x, y, 0])

        axis_labels = VGroup(
            Tex("0", font_size=24).next_to(frame.get_corner(DL), DOWN, buff=0.1),
            Tex(str(N_PAIRS), font_size=24).next_to(frame.get_corner(DR), DOWN, buff=0.1),
            Tex(R"\text{pairs}", font_size=24).next_to(frame, DOWN, buff=0.1),
            Tex(str(GRAPH_Y[0]), font_size=22).next_to(frame.get_corner(DL), LEFT, buff=0.1),
            Tex(str(GRAPH_Y[1]), font_size=22).next_to(frame.get_corner(UL), LEFT, buff=0.1),
        ).set_color(GREY_B)

        n = ValueTracker(0)

        def trails():
            k = int(n.get_value())
            lines = VGroup()
            for i in range(max(0, k - 30), k):
                age = (k - 1 - i) / 30
                lines.add(Line(self.to_screen(FIRST[i]), self.to_screen(SECOND[i])).set_stroke(
                    PAIR if i == k - 1 else TRAIL, 3 if i == k - 1 else 1.5, 1 - 0.85 * age))
            return lines

        def newest():
            k = int(n.get_value())
            if k == 0:
                return VGroup()
            return VGroup(*[Dot(self.to_screen(x[k - 1]), radius=0.06).set_fill(POINT) for x in (FIRST, SECOND)])

        def curve():
            k = int(n.get_value())
            if k < 2:
                return VMobject()
            ns = np.unique(np.linspace(1, k, min(k, 300)).astype(int))
            return VMobject().set_points_as_corners([g(i, RUNNING[i - 1]) for i in ns]).set_stroke(PAIR, 3)

        lines = always_redraw(trails)
        dots = always_redraw(newest)
        graph = always_redraw(curve)
        count.add_updater(lambda m: m.set_value(int(n.get_value())))
        average.add_updater(lambda m: m.set_value(RUNNING[max(int(n.get_value()), 1) - 1]))

        self.play(FadeIn(readout), ShowCreation(frame), FadeIn(axis_labels), run_time=0.7)
        self.add(lines, dots, graph)

        # One at a time, then faster and faster
        for k in range(1, 9):
            n.set_value(k)
            self.wait(0.3)
        self.play(n.animate.set_value(80), run_time=1.6, rate_func=linear)
        self.play(n.animate.set_value(N_PAIRS), run_time=4.0, rate_func=lambda t: t ** 2)
        for m in (count, average):
            m.clear_updaters()
        lines.clear_updaters()
        self.play(FadeOut(lines), FadeOut(dots), run_time=0.4)
        self.play(FlashAround(readout[1], color=PAIR), run_time=1.0)
        self.caption("Simulation: 3000 random pairs average about 0.52.", wait=1.0)
        self.set_state("simulation", VGroup(readout, frame, axis_labels, graph))
        self.set_state("simulated", average)

    def gaps(self):
        square = self.get_square()
        simulation = self.lazy("simulation", VGroup)
        self.play(FadeOut(simulation), run_time=0.5)

        # Only the gaps matter: u across, v up
        p, q = EXAMPLES[0]
        pair = self.pair(p, q)
        corner = (q[0], p[1])
        legs = VGroup(
            Line(self.to_screen(p), self.to_screen(corner)).set_stroke(GAP_U, 5),
            Line(self.to_screen(corner), self.to_screen(q)).set_stroke(GAP_V, 5),
        )
        names = VGroup(
            Tex("u", font_size=36).set_color(GAP_U).next_to(legs[0], UP, buff=0.1),
            Tex("v", font_size=36).set_color(GAP_V).next_to(legs[1], RIGHT, buff=0.1),
        )
        self.play(FadeIn(pair[1], scale=0.5), ShowCreation(pair[0]), run_time=0.6)
        self.play(ShowCreation(legs, lag_ratio=0.5), FadeIn(names), run_time=0.8)
        self.add_step(
            R"u = |x_1 - x_2|,\quad v = |y_1 - y_2|,\quad d = \sqrt{u^2 + v^2}",
            wait=0.4,
        )
        self.caption("A gap between two random numbers is more often\nsmall: its density is 2(1 - u).", wait=1.5)
        rule = self.add_step(
            R"E = \int_0^1\int_0^1 \sqrt{u^2+v^2}\cdot 4(1-u)(1-v)\,du\,dv",
            font_size=36, wait=0.8,
        )
        self.set_state("example", VGroup(pair, legs, names))
        self.set_state("rule", rule)

    def polar(self):
        square = self.get_square()
        example = self.lazy("example", VGroup)
        rule = self.lazy("rule", VGroup)
        steps = self.steps()

        # The square becomes the (u, v) square: shrink it up out of the way
        target = square.copy().set_width(3.4).move_to(2.35 * UP)
        self.play(
            FadeOut(example),
            Transform(square, target),
            run_time=1.0,
        )
        # The steps follow it up
        self.steps_top_y = square.get_bottom()[1] - 0.5
        others = [m for m in steps if m is not rule]
        self.play(
            *[FadeOut(m) for m in others],
            rule.animate.set_y(self.steps_top_y - rule.get_height() / 2),
            run_time=0.6,
        )
        steps.set_submobjects([rule])
        u_label = Tex("u", font_size=34).set_color(GAP_U).next_to(square, DOWN, buff=0.12)
        v_label = Tex("v", font_size=34).set_color(GAP_V).next_to(square, LEFT, buff=0.12)
        diagonal = DashedLine(square.get_corner(DL), square.get_corner(UR)).set_stroke(WHITE, 2)
        region = Polygon(square.get_corner(DL), square.get_corner(DR), square.get_corner(UR))
        region.set_stroke(width=0).set_fill(REGION, 0.35)
        twice = Tex(R"\times 2", font_size=36).set_color(REGION).next_to(square, RIGHT, buff=0.2)
        self.play(FadeIn(u_label), FadeIn(v_label), ShowCreation(diagonal), run_time=0.6)
        self.play(FadeIn(region), FadeIn(twice), run_time=0.6)
        self.caption("Symmetric in u and v: twice the lower triangle.", wait=1.0)

        # Polar coordinates: a ray at angle theta runs to the side u = 1
        theta = ValueTracker(0.001)
        origin = square.get_corner(DL)
        side = square.get_width()
        ray = always_redraw(lambda: Line(
            origin, origin + side * np.array([1, np.tan(theta.get_value()), 0]),
        ).set_stroke(PAIR, 4))
        angle = always_redraw(lambda: Arc(
            0, theta.get_value(), radius=0.45, arc_center=origin,
        ).set_stroke(PAIR, 3))
        ray_label = Tex(R"r = \sec\theta", font_size=30).set_color(PAIR)
        ray_label.add_updater(lambda m: m.move_to(
            origin + 0.62 * side * np.array([1, np.tan(theta.get_value()), 0]) + 0.3 * DR))
        theta_label = Tex(R"\theta", font_size=28).set_color(PAIR).move_to(origin + 0.62 * RIGHT + 0.15 * UP)
        self.add(ray, angle)
        self.play(FadeIn(ray_label), FadeIn(theta_label), theta.animate.set_value(PI / 4), run_time=1.6)
        self.play(theta.animate.set_value(PI / 7), run_time=0.7)
        self.caption(
            R"\text{Polar: } u = r\cos\theta,\ v = r\sin\theta,\ du\,dv = r\,dr\,d\theta",
            wait=1.2, tex=True,
        )
        self.replace_step(
            rule,
            R"E = 8\int_0^{\pi/4}\int_0^{\sec\theta} r^2(1-r\cos\theta)(1-r\sin\theta)\,dr\,d\theta",
            font_size=36, wait=0.8,
        )
        self.set_state("uv", VGroup(u_label, v_label, diagonal, region, twice, ray, angle, ray_label, theta_label))

    def integrate(self):
        steps = self.steps()
        line = steps[-1]

        self.caption("Integrate in r first.", wait=0.6)
        line = self.transform_step(
            line,
            R"= 8\int_0^{\pi/4}\left(\frac{\sec^3\theta}{12} - \frac{\sec^3\theta\tan\theta}{20}\right)d\theta",
            font_size=36, wait=0.8,
        )
        self.caption(
            R"\textstyle\int\sec^3\theta = \tfrac{1}{2}(\sec\theta\tan\theta + \ln|\sec\theta+\tan\theta|),"
            R"\quad \int\sec^3\theta\tan\theta = \tfrac{1}{3}\sec^3\theta",
            wait=1.6, tex=True,
        )
        line = self.transform_step(
            line,
            R"= 8\left[\frac{\sec\theta\tan\theta + \ln|\sec\theta+\tan\theta|}{24} - \frac{\sec^3\theta}{60}\right]_0^{\pi/4}",
            font_size=36, wait=1.0,
        )
        exact = self.replace_step(
            line,
            R"E = \frac{2+\sqrt{2}+5\ln(1+\sqrt{2})}{15} \approx 0.5214",
            color=RESULT_COLOR, font_size=42, wait=0.3,
        )
        box = SurroundingRectangle(exact, color=RESULT_COLOR, buff=0.2).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)

        # The simulation agreed
        check = Tex(
            Rf"\text{{simulation: }} {RUNNING[-1]:.4f}\quad\checkmark", font_size=32,
        ).set_color(PAIR)
        check.next_to(box, DOWN, buff=0.3)
        self.play(FadeIn(check, 0.15 * UP), FlashAround(exact, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.wait(1.8)
