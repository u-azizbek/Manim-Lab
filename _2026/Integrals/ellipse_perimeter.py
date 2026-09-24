from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Integrals/ellipse_perimeter.py
#
# Why an ellipse's perimeter has no simple formula.  Adding up tiny straight
# pieces ds = sqrt(dx^2 + dy^2) around x = a sin t, y = b cos t gives
#   P = 4a * integral_0^{pi/2} sqrt(1 - e^2 sin^2 t) dt,   e^2 = 1 - b^2/a^2.
# For a circle (e = 0) the integrand is 1 and P = 2 pi a; for any other e the
# integrand has no antiderivative built from elementary functions, so the
# answer is a new function E(e) -- computable to any precision, but with no
# closed form.  Ramanujan's approximation pi[3(a+b) - sqrt((3a+b)(a+3b))] is
# astonishingly close.
#
# For a = 5, b = 3 (so e = 0.8): P = 25.5269988..., Ramanujan 25.5269864...,
# a relative error of 5e-7.  All values checked with mpmath.

A_AX, B_AX = 5, 3
ECC = np.sqrt(1 - (B_AX / A_AX) ** 2)          # exactly 0.8
EXACT_P = 25.5269988634
RAMANUJAN_P = PI * (3 * (A_AX + B_AX) - np.sqrt((3 * A_AX + B_AX) * (A_AX + 3 * B_AX)))

SCALE = 0.62                 # screen units per unit, for the ellipse
FIG_CENTER = 1.7 * UP
POLYGON_SIDES = [4, 8, 16, 32, 64]

CURVE = "#58C4DD"
PIECE = YELLOW
DX_COLOR = "#4FD1C5"
DY_COLOR = "#FF6B9A"
GRAPH = "#E8D594"
EXACT = "#83C167"


def on_ellipse(theta, a=A_AX, b=B_AX):
    """The walk used throughout: theta = 0 at the top, going clockwise."""
    return a * np.sin(theta), b * np.cos(theta)


def polygon_length(n):
    pts = [on_ellipse(TAU * k / n) for k in range(n)]
    return sum(np.hypot(*np.subtract(pts[(k + 1) % n], pts[k])) for k in range(n))


def quarter_integral(e, samples=400):
    """integral_0^{pi/2} sqrt(1 - e^2 sin^2 t) dt, by Simpson's rule."""
    t = np.linspace(0, PI / 2, samples + 1)
    f = np.sqrt(1 - (e * np.sin(t)) ** 2)
    return (PI / 2) / samples / 3 * (f[0] + f[-1] + 4 * f[1:-1:2].sum() + 2 * f[2:-1:2].sum())


class EllipsePerimeter(MockTestShort):
    """No simple formula for an ellipse's perimeter: the integral, why it is
    stuck, and Ramanujan's approximation."""

    test = ""
    card_top_buff = 0.85
    step_buff = 0.4

    problem_tex = (
        R"\text{Circle: } P = 2\pi r.\\"
        R"\text{Ellipse: why no simple formula?}"
    )

    sections = [
        "pose",
        "shapes",
        "tiny_pieces",
        "the_integral",
        "stuck",
        "ramanujan",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = -1.1
        return card

    # Pieces

    def p(self, x, y):
        return FIG_CENTER + SCALE * (x * RIGHT + y * UP)

    def make_ellipse(self):
        ellipse = Ellipse(width=2 * A_AX * SCALE, height=2 * B_AX * SCALE)
        ellipse.move_to(FIG_CENTER).set_stroke(CURVE, 4)
        a_line = Line(self.p(0, 0), self.p(A_AX, 0)).set_stroke(GREY_A, 2)
        b_line = Line(self.p(0, 0), self.p(0, B_AX)).set_stroke(GREY_A, 2)
        a_label = Tex("a", font_size=36).next_to(a_line, DOWN, buff=0.1)
        b_label = Tex("b", font_size=36).next_to(b_line, LEFT, buff=0.1)
        group = VGroup(ellipse, a_line, b_line, a_label, b_label)
        group.curve = ellipse
        group.axes = VGroup(a_line, b_line, a_label, b_label)
        return group

    def get_ellipse(self):
        return self.lazy("ellipse", self.make_ellipse)

    def polygon(self, n):
        return Polygon(*[self.p(*on_ellipse(TAU * k / n)) for k in range(n)]).set_stroke(PIECE, 3)

    # Sections

    def shapes(self):
        self.get_card()
        radius = 4 * SCALE
        circle = Circle(radius=radius).move_to(FIG_CENTER).set_stroke(CURVE, 4)
        r_line = Line(FIG_CENTER, FIG_CENTER + radius * RIGHT).set_stroke(GREY_A, 2)
        r_label = Tex("r", font_size=36).next_to(r_line, UP, buff=0.1)
        self.play(ShowCreation(circle), run_time=0.9)
        self.play(ShowCreation(r_line), FadeIn(r_label), run_time=0.5)
        line = self.add_step(R"\text{Circle: } P = 2\pi r", font_size=42, wait=0.7)

        # Stretch the circle into an ellipse: suddenly there is no formula
        ellipse = self.make_ellipse()
        self.play(
            Transform(circle, ellipse.curve),
            FadeOut(VGroup(r_line, r_label)),
            run_time=1.3,
        )
        self.remove(circle)
        self.add(ellipse.curve)
        self.play(FadeIn(ellipse.axes, lag_ratio=0.2), run_time=0.6)
        self.replace_step(line, R"\text{Ellipse: } P = \, ?", font_size=42, wait=0.6)
        self.set_state("ellipse", ellipse)

    def tiny_pieces(self):
        self.get_ellipse()
        self.note("Measure it with straight pieces.", wait=0.4)

        total = DecimalNumber(polygon_length(4), num_decimal_places=2, font_size=36).set_color(PIECE)
        readout = VGroup(Text("sum", font_size=28).set_color(PIECE), total).arrange(RIGHT, buff=0.18)
        readout.move_to(self.p(0, -B_AX) + 0.45 * DOWN)

        shape = self.polygon(4)
        self.play(ShowCreation(shape), FadeIn(readout), run_time=0.8)
        for n in POLYGON_SIDES[1:3]:
            self.play(
                Transform(shape, self.polygon(n)),
                ChangeDecimalToValue(total, polygon_length(n)),
                run_time=0.6,
            )

        # One piece up close: a tiny right triangle
        p2, p3 = [self.p(*on_ellipse(TAU * k / 16)) for k in (2, 3)]
        corner = np.array([p3[0], p2[1], 0])
        piece = Line(p2, p3).set_stroke(PIECE, 7)
        dx = Line(p2, corner).set_stroke(DX_COLOR, 4)
        dy = Line(corner, p3).set_stroke(DY_COLOR, 4)
        tags = VGroup(
            Tex("dx", font_size=30).set_color(DX_COLOR).next_to(dx, UP, buff=0.08),
            Tex("dy", font_size=30).set_color(DY_COLOR).next_to(dy, RIGHT, buff=0.08),
            Tex("ds", font_size=30).set_color(PIECE).move_to(midpoint(p2, p3) + 0.3 * DL),
        )
        self.play(ShowCreation(piece), run_time=0.4)
        self.play(ShowCreation(dx), ShowCreation(dy), FadeIn(tags, lag_ratio=0.3), run_time=0.8)
        self.add_step(R"ds = \sqrt{dx^2 + dy^2}", font_size=42, wait=0.5)
        self.play(FadeOut(VGroup(piece, dx, dy, tags)), run_time=0.4)

        for n in POLYGON_SIDES[3:]:
            self.play(
                Transform(shape, self.polygon(n)),
                ChangeDecimalToValue(total, polygon_length(n)),
                run_time=0.6,
            )
        self.replace_step(self.steps()[0], R"P = 25.527\ldots", font_size=42, color=PIECE, wait=0.5)
        self.play(FadeOut(VGroup(shape, readout)), run_time=0.4)

    def the_integral(self):
        ellipse = self.get_ellipse()
        steps = self.steps()
        ds_line = steps[1] if len(steps) > 1 else self.add_step(R"ds = \sqrt{dx^2 + dy^2}", font_size=42)

        # Walk a quarter of the way round: x = a sin t, y = b cos t
        theta = ValueTracker(0)
        walker = always_redraw(lambda: Dot(self.p(*on_ellipse(theta.get_value())), radius=0.09).set_color(PIECE))
        quarter = ParametricCurve(lambda t: self.p(*on_ellipse(t)), t_range=(0, PI / 2, 0.02))
        quarter.set_stroke(PIECE, 7)
        where = Tex(R"(a\sin\theta,\, b\cos\theta)", font_size=30).set_color(PIECE)
        where.add_updater(lambda m: m.next_to(walker, UR, buff=0.06))
        self.add(walker)
        self.play(FadeIn(walker, scale=0.5), FadeIn(where), run_time=0.4)
        self.play(theta.animate.set_value(PI / 2), ShowCreation(quarter), run_time=1.5)
        self.play(FadeOut(where), run_time=0.3)

        ds_line = self.replace_step(
            ds_line, R"ds = \sqrt{a^2\cos^2\theta + b^2\sin^2\theta}\,d\theta",
            font_size=40, wait=0.4,
        )
        ds_line = self.replace_step(
            ds_line, R"ds = a\sqrt{1 - e^2\sin^2\theta}\,d\theta",
            font_size=42, wait=0.5,
        )
        times_four = Tex(R"\times 4", font_size=40).set_color(PIECE).move_to(self.p(3.4, 3.2))
        self.play(FadeIn(times_four, scale=0.6), run_time=0.5)
        self.add_step(
            R"P = 4a\int_0^{\pi/2}\sqrt{1 - e^2\sin^2\theta}\,d\theta",
            font_size=44, color=YELLOW, wait=0.5,
        )
        self.note("e = √(1 − b²/a²) is the eccentricity: 0.8 here.", wait=0.8)
        self.play(FadeOut(VGroup(walker, quarter, times_four)), run_time=0.4)

    def stuck(self):
        ellipse = self.get_ellipse()
        steps = self.steps()

        # Keep only the integral; swap the picture for its integrand
        if len(steps) >= 3:
            integral = steps[2]
            self.play(
                FadeOut(VGroup(*steps[:2]), 0.3 * UP),
                integral.animate.set_y(self.steps_top_y - integral.get_height() / 2),
                FadeOut(ellipse),
                run_time=0.7,
            )
            steps.set_submobjects([integral])

        e_t = ValueTracker(0)
        axes = Axes(
            (0, 1.7, 0.5), (0, 1.25, 0.5), width=4.9, height=3.0,
            axis_config=dict(stroke_color=GREY_B, stroke_width=2, include_tip=False),
        )
        axes.move_to(FIG_CENTER + 0.75 * LEFT)
        end = DashedLine(axes.c2p(PI / 2, 0), axes.c2p(PI / 2, 1.15), dash_length=0.06).set_stroke(GREY_B, 2)
        ticks = VGroup(
            Tex("0", font_size=26).next_to(axes.c2p(0, 0), DOWN, buff=0.12),
            Tex(R"\frac{\pi}{2}", font_size=30).next_to(axes.c2p(PI / 2, 0), DOWN, buff=0.12),
            Tex("1", font_size=26).next_to(axes.c2p(0, 1), LEFT, buff=0.12),
        )

        def integrand(t):
            return np.sqrt(1 - (e_t.get_value() * np.sin(t)) ** 2)

        curve = always_redraw(
            lambda: axes.get_graph(integrand, x_range=(0, PI / 2)).set_stroke(GRAPH, 4)
        )
        area = always_redraw(lambda: Polygon(
            axes.c2p(0, 0),
            *[axes.c2p(t, integrand(t)) for t in np.linspace(0, PI / 2, 60)],
            axes.c2p(PI / 2, 0),
        ).set_fill(CURVE, 0.35).set_stroke(width=0))
        name = Tex(R"\sqrt{1 - e^2\sin^2\theta}", font_size=32).set_color(GRAPH)
        name.next_to(axes.c2p(0.05, 1.18), RIGHT, buff=0)

        # A little ellipse that squashes as e grows
        mini = always_redraw(lambda: Ellipse(
            width=1.3, height=max(1.3 * np.sqrt(1 - e_t.get_value() ** 2), 0.02),
        ).set_stroke(CURVE, 3).move_to(FIG_CENTER + 2.95 * RIGHT + 0.55 * UP))
        e_value = DecimalNumber(0, num_decimal_places=2, font_size=30)
        e_value.add_updater(lambda m: m.set_value(e_t.get_value()))
        e_readout = VGroup(Tex("e =", font_size=30), e_value).arrange(RIGHT, buff=0.1)
        e_readout.next_to(mini, DOWN, buff=0.2)
        e_value.add_updater(lambda m: m.next_to(e_readout[0], RIGHT, buff=0.1))
        area_value = DecimalNumber(quarter_integral(0), num_decimal_places=4, font_size=32).set_color(CURVE)
        area_value.add_updater(lambda m: m.set_value(quarter_integral(e_t.get_value())))
        area_readout = VGroup(Text("area", font_size=26).set_color(CURVE), area_value).arrange(RIGHT, buff=0.15)
        area_readout.move_to(axes.c2p(0.78, 0.45))
        area_value.add_updater(lambda m: m.next_to(area_readout[0], RIGHT, buff=0.15))

        self.play(ShowCreation(axes), FadeIn(ticks), ShowCreation(end), run_time=0.8)
        self.add(area, curve)
        self.play(
            FadeIn(area), ShowCreation(curve), FadeIn(name),
            FadeIn(mini), FadeIn(e_readout), FadeIn(area_readout),
            run_time=0.9,
        )
        self.note("e = 0 is a circle: a flat line, area exactly π/2,\nso P = 4a · π/2 = 2πa.", wait=1.1)

        self.play(e_t.animate.set_value(ECC), run_time=1.8)
        self.note("Any other e: no formula gives this area.\nIt defines a brand-new function, E(e).", wait=1.3)
        self.replace_step(
            steps[0], R"P = 4a\,E(e) = 25.527\ldots",
            font_size=44, color=YELLOW, wait=0.6,
        )
        self.set_state("graph", VGroup(axes, end, ticks, area, curve, name, mini, e_readout, area_readout))

    def ramanujan(self):
        self.get_card()
        graph = self.lazy("graph", VGroup)
        ellipse = self.get_ellipse()
        steps = self.steps()
        self.play(FadeOut(graph), FadeOut(steps), run_time=0.6)
        self._step_lines = VGroup()
        self.play(FadeIn(ellipse), run_time=0.6)

        self.note("Ramanujan's approximation:", wait=0.3)
        formula = self.add_step(
            R"P \approx \pi\left[3(a+b) - \sqrt{(3a+b)(a+3b)}\right]",
            font_size=38, color=YELLOW, wait=0.6,
        )
        values = self.add_step(
            R"= \pi\left(24 - \sqrt{252}\right) = 25.52699",
            font_size=40, wait=0.6, isolate=["25.52699"],
        )
        exact = self.add_step(R"\text{exact: } 25.52700", font_size=40, color=EXACT, wait=0.4, isolate=["25.52700"])
        pair = VGroup(values["25.52699"][0], exact["25.52700"][0])
        self.play(*[FlashAround(m, color=EXACT, time_width=1.5) for m in pair], run_time=1.2)
        self.note("Off by about 0.00001.", wait=1.0)
        box = SurroundingRectangle(formula, color=YELLOW, buff=0.18).set_stroke(width=3)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(1.0)
