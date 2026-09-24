from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/apollonius_circles.py
#
# Apollonius' problem: circles tangent to three given circles.  Each given
# circle can touch the answer from outside or sit inside it, so there are
# 2 x 2 x 2 = 8 sign patterns and at most 8 solutions.  For each pattern e,
#   |X - c_i| = r + e_i r_i     (e_i = +1 outside, -1 inside)
# and subtracting the equations pairwise leaves x, y linear in r, so r solves a
# quadratic.  The three circles below were picked by a search so that all 8
# solutions exist and fit on a portrait screen; each one is checked against
# all three tangency conditions when it is computed.

GIVEN = [(0.454, -0.409, 0.423), (-0.479, 1.045, 0.356), (-1.452, -0.799, 0.611)]
NAMES = "ABC"
ZOOM = 1.7
PLANE_CENTER = np.array([-0.95, -0.2])
FIG_CENTER = 0.8 * UP

RED = "#FF5C5C"
BLUE = "#4C8DFF"
TOUCH = YELLOW

ORDER = [  # all outside, all inside, then one inside, then two inside
    (1, 1, 1), (-1, -1, -1),
    (-1, 1, 1), (1, -1, 1), (1, 1, -1),
    (-1, -1, 1), (-1, 1, -1), (1, -1, -1),
]


def apollonius(circles, signs):
    """The circle with |X - c_i| = r + e_i r_i for all i, as (x, y, r)."""
    (x1, y1, r1), rest = circles[0], circles[1:]
    A = np.array([[-2 * (xi - x1), -2 * (yi - y1)] for xi, yi, ri in rest])
    c = np.array([(ri ** 2 - r1 ** 2) - (xi ** 2 + yi ** 2 - x1 ** 2 - y1 ** 2) for xi, yi, ri in rest])
    d = np.array([2 * (e * ri - signs[0] * r1) for (xi, yi, ri), e in zip(rest, signs[1:])])
    p, q = np.linalg.solve(A, c), np.linalg.solve(A, d)          # centre = p + q r
    u = p - np.array([x1, y1])
    roots = np.roots([q @ q - 1, 2 * u @ q - 2 * signs[0] * r1, u @ u - r1 ** 2])
    for r in roots:
        if abs(r.imag) < 1e-9 and r.real > 1e-6:
            r = r.real
            x, y = p + q * r
            if all(abs(np.hypot(x - xi, y - yi) - (r + e * ri)) < 1e-7
                   for (xi, yi, ri), e in zip(circles, signs)):
                return x, y, r
    raise ValueError(f"no solution for {signs}")


SOLUTIONS = [apollonius(GIVEN, signs) for signs in ORDER]


def sp(x, y):
    return FIG_CENTER + ZOOM * ((x - PLANE_CENTER[0]) * RIGHT + (y - PLANE_CENTER[1]) * UP)


def contact(given, solution, sign):
    """Where a given circle touches the solution."""
    (xi, yi, ri), (x, y, r) = given, solution
    toward = np.array([x - xi, y - yi]) / np.hypot(x - xi, y - yi)
    return np.array([xi, yi]) + sign * ri * toward


def describe(signs):
    inside = [n for n, e in zip(NAMES, signs) if e < 0]
    if not inside:
        return R"\text{all three outside}"
    if len(inside) == 3:
        return R"\text{all three inside}"
    return R"\text{" + " and ".join(inside) + R" inside}"


class ApolloniusCircles(MockTestShort):
    """The eight circles tangent to three given circles."""

    test = ""
    card_top_buff = 0.6

    problem_tex = (
        R"\text{Three red circles. How many circles}\\"
        R"\text{touch all three of them?}"
    )

    sections = [
        "pose",
        "given",
        "solutions",
        "all_eight",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = -3.05
        return card

    def icon(self, sign):
        """A blue circle with a small red one touching it from outside or inside."""
        blue = Circle(radius=0.34).set_stroke(BLUE, 3.5)
        red = Circle(radius=0.14).set_stroke(RED, 3.5).set_fill(RED, 0.3)
        red.move_to(blue.get_center() + (0.34 + sign * 0.14) * RIGHT)
        if sign > 0:
            return VGroup(blue, red).set_x(0)
        return VGroup(blue, red)

    def legend(self, signs):
        icons = VGroup()
        for name, sign in zip(NAMES, signs):
            letter = Tex(name, font_size=32).set_color(RED)
            icons.add(VGroup(self.icon(sign), letter).arrange(DOWN, buff=0.1))
        icons.arrange(RIGHT, buff=0.45)
        words = Tex(describe(signs), font_size=36)
        group = VGroup(icons, words).arrange(RIGHT, buff=0.5)
        return group.move_to(3.55 * DOWN)

    # Sections

    def given(self):
        self.get_card()
        reds = VGroup(*[
            Circle(radius=ZOOM * r).move_to(sp(x, y)).set_stroke(RED, 5).set_fill(RED, 0.12)
            for x, y, r in GIVEN
        ])
        centers = VGroup(*[Dot(sp(x, y), radius=0.05).set_fill(RED) for x, y, r in GIVEN])
        names = VGroup(*[
            Tex(n, font_size=34).set_color(RED).next_to(sp(x, y), UP, buff=0.08)
            for n, (x, y, r) in zip(NAMES, GIVEN)
        ])
        self.play(LaggedStart(*[ShowCreation(c) for c in reds], lag_ratio=0.3), run_time=1.3)
        self.play(FadeIn(centers), FadeIn(names), run_time=0.5)
        self.note("Each red circle can touch it from outside,\nor sit inside it: 2 choices for each.", wait=1.6)
        self.set_state("reds", VGroup(reds, centers, names))

    def solutions(self):
        reds = self.lazy("reds", VGroup)
        counter = VGroup(Integer(0, font_size=40), Tex("/ 8", font_size=40)).arrange(RIGHT, buff=0.12)
        counter.set_color(BLUE).move_to(4.45 * DOWN)
        counter[0].set_value(0)
        self.play(FadeIn(counter), run_time=0.3)

        drawn = VGroup()
        legend = None
        for k, (signs, (x, y, r)) in enumerate(zip(ORDER, SOLUTIONS)):
            circle = Circle(radius=ZOOM * r).move_to(sp(x, y)).set_stroke(BLUE, 5)
            touches = VGroup(*[
                Dot(sp(*contact(g, (x, y, r), e)), radius=0.07).set_fill(TOUCH).set_stroke(BLACK, 1)
                for g, e in zip(GIVEN, signs)
            ])
            new_legend = self.legend(signs)
            anims = [FadeOut(legend, 0.2 * UP)] if legend is not None else []
            counter[0].set_value(k + 1)
            self.play(
                ShowCreation(circle),
                *anims,
                FadeIn(new_legend, 0.2 * UP),
                drawn.animate.set_stroke(opacity=0.25),
                Indicate(counter, color=WHITE, scale_factor=1.15),
                run_time=1.0,
            )
            self.play(LaggedStart(*[FadeIn(t, scale=2.5) for t in touches], lag_ratio=0.2), run_time=0.6)
            self.wait(0.9 if k > 1 else 1.4)
            self.play(FadeOut(touches), run_time=0.25)
            drawn.add(circle)
            legend = new_legend
        self.play(FadeOut(legend), run_time=0.3)
        self.set_state("drawn", drawn)
        self.set_state("counter", counter)

    def all_eight(self):
        drawn = self.lazy("drawn", VGroup)
        reds = self.lazy("reds", VGroup)

        # Everything at once, as in the classic picture
        self.play(drawn.animate.set_stroke(BLUE, 4, opacity=1), run_time=0.9)
        self.add(reds)
        self.play(LaggedStart(*[Indicate(c, color=WHITE, scale_factor=1.02) for c in drawn], lag_ratio=0.1), run_time=1.4)
        self.play(FadeOut(self.lazy("counter", VGroup)), run_time=0.3)
        self.note("Apollonius' problem: two choices for each\ncircle, so at most 2 × 2 × 2 circles.", wait=1.6)
        self.conclude(R"2 \times 2 \times 2 = 8 \text{ circles}", font_size=48, wait=1.5)
