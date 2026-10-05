from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/four_squares_circle.py
#
# Four squares of area 16 (side 4) in a staircase inside a circle.  With the
# first square [0,4] x [0,4], the others are [4,8] x [4,8], [8,12] x [8,12] and
# [12,16] x [4,8].  The circle passes through P(0, 0) and the right corners
# Q(16, 4), C(16, 8) of the last square.
#   1. The centre is on the perpendicular bisector y = 6 of the chord QC, so
#      reflecting P in it gives another point of the circle, A(0, 12).
#   2. AC runs 16 across and 4 down, through (8, 10), the midpoint of the third
#      square's left side: the blue triangle has legs 8 and 2, AC = 4 sqrt 17.
#   3. Turn that triangle a quarter turn about A: B(-2, 4), AB = 2 sqrt 17 and
#      AB is perpendicular to AC.  P sees BC at a right angle too (PB = (-2, 4),
#      PC = (16, 8)), so the circle on diameter BC passes through A, P and C --
#      three points of our circle, so it is our circle.
#   4. BC^2 = 68 + 272 = 340, BC = 2 sqrt 85, R = sqrt 85.
# Checked: all of P, Q, C, A, B are sqrt 85 from (7, 6).

SQUARES = [(0, 0), (4, 4), (8, 8), (12, 4)]
CENTER = np.array([7.0, 6.0])
RADIUS = np.sqrt(85)
POINTS = {"P": (0, 0), "Q": (16, 4), "C": (16, 8), "A": (0, 12), "B": (-2, 4), "M": (8, 10), "T": (8, 12), "F": (0, 4)}

SCALE = 0.385
FIG_Y = 0.55

GREEN = "#6BCB3F"
GREEN_EDGE = "#2E8B3A"
CIRCLE = "#2FB86E"
BLUE = "#3FA7FF"
MIRROR = "#FF9F43"
DIAM = YELLOW


def sp(x, y):
    return np.array([SCALE * (x - CENTER[0]), FIG_Y + SCALE * (y - CENTER[1]), 0])


def at(name):
    return sp(*POINTS[name])


class FourSquaresCircle(MockTestShort):
    """Radius of the circle through a staircase of four squares."""

    test = ""
    step_buff = 0.32
    step_font_size = 36

    problem_tex = (
        R"\text{Four squares of area } 16\\"
        R"\text{inside a circle. Find its radius.}"
    )

    sections = ["pose", "figure", "symmetry", "diagonal", "rotate", "diameter", "outro"]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = sp(0, CENTER[1] - RADIUS)[1] - 0.45
        return card

    def label(self, tex, point, direction, color=WHITE, font_size=30, buff=0.1):
        return Tex(tex, font_size=font_size).set_color(color).next_to(point, direction, buff=buff)

    def dot(self, name, color=WHITE, radius=0.07):
        return Dot(at(name), radius=radius).set_fill(color).set_stroke(BLACK, 1)

    def right_angle(self, corner, d1, d2, size=0.22, color=WHITE):
        corner, d1, d2 = at(corner), normalize(np.array([*d1, 0])), normalize(np.array([*d2, 0]))
        return VMobject().set_points_as_corners([
            corner + size * d1, corner + size * (d1 + d2), corner + size * d2,
        ]).set_stroke(color, 2.5)

    def make_figure(self):
        squares = VGroup(*[
            Square(4 * SCALE).move_to(sp(x + 2, y + 2)).set_stroke(GREEN_EDGE, 4).set_fill(GREEN, 0.75)
            for x, y in SQUARES
        ])
        areas = VGroup(*[Tex("16", font_size=32).set_color(WHITE).move_to(s) for s in squares])
        circle = Circle(radius=RADIUS * SCALE).move_to(sp(*CENTER)).set_stroke(CIRCLE, 5)
        fig = VGroup(circle, squares, areas)
        fig.circle, fig.squares, fig.areas = circle, squares, areas
        return fig

    def get_figure(self):
        return self.lazy("figure", self.make_figure)

    # Sections

    def figure(self):
        self.get_card()
        fig = self.make_figure()
        self.play(LaggedStart(*[DrawBorderThenFill(s) for s in fig.squares], lag_ratio=0.25), run_time=1.5)
        self.play(FadeIn(fig.areas, lag_ratio=0.2), run_time=0.5)
        self.play(ShowCreation(fig.circle), run_time=1.2)
        side = self.label("4", sp(2, 0), DOWN, GREEN, 30)
        self.play(FadeIn(side), Indicate(fig.squares[0], color=GREEN, scale_factor=1.05), run_time=0.7)
        self.note("Area 16, so every side is 4.", wait=0.8)

        # The three corners that sit on the circle
        corners = VGroup(self.dot("P", YELLOW), self.dot("Q", YELLOW), self.dot("C", YELLOW))
        names = VGroup(
            self.label("P", at("P"), DL, YELLOW),
            self.label("Q", at("Q"), RIGHT, YELLOW),
            self.label("C", at("C"), RIGHT, YELLOW),
        )
        self.play(LaggedStart(*[FadeIn(c, scale=2) for c in corners], lag_ratio=0.3), FadeIn(names), run_time=0.9)
        self.play(*[Flash(c, color=YELLOW, flash_radius=0.25) for c in corners], run_time=0.7)
        self.set_state("figure", fig)
        self.set_state("given", VGroup(side, corners, names))

    def symmetry(self):
        fig = self.get_figure()
        given = self.lazy("given", VGroup)

        # QC is a chord: its perpendicular bisector is a line of symmetry
        mid = sp(16, 6)
        bisector = DashedLine(sp(-3.5, 6), sp(17.5, 6), dash_length=0.1).set_stroke(MIRROR, 2.5)
        qc = Line(at("Q"), at("C")).set_stroke(MIRROR, 6)
        self.play(ShowCreation(qc), run_time=0.5)
        self.play(ShowCreation(bisector), run_time=0.8)
        self.note("The centre lies on the perpendicular bisector\nof chord QC: the circle is symmetric about it.", wait=1.3)

        # Reflect P across it: A is on the circle too
        ghost = self.dot("P", MIRROR)
        down = DashedLine(at("P"), at("A"), dash_length=0.08).set_stroke(MIRROR, 2)
        self.play(ShowCreation(down), ghost.animate.move_to(at("A")), run_time=1.2)
        a_dot = self.dot("A", YELLOW)
        a_name = self.label("A", at("A"), UL, YELLOW)
        twelve = self.label("12", sp(0, 8), LEFT, MIRROR, 28)
        self.play(FadeIn(a_dot), FadeIn(a_name), FadeIn(twelve), FadeOut(ghost), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(VGroup(bisector, qc, down, twelve)), run_time=0.4)
        self.set_state("a", VGroup(a_dot, a_name))

    def diagonal(self):
        fig = self.get_figure()

        # AC passes through the midpoint of the third square's left side
        ac = Line(at("A"), at("C")).set_stroke(WHITE, 3.5)
        self.play(ShowCreation(ac), run_time=0.9)
        tri = Polygon(at("A"), at("T"), at("M")).set_stroke(BLUE, 3).set_fill(BLUE, 0.45)
        self.play(FadeIn(tri), run_time=0.5)
        legs = VGroup(
            self.label("8", sp(4, 12), UP, BLUE, 30),
            self.label("2", sp(8, 11), RIGHT, BLUE, 28, 0.06),
        )
        self.play(FadeIn(legs), run_time=0.5)
        self.note("Across 8, down 2: the line hits the middle of\nthe square's side, and runs on to C.", wait=1.3)
        ac_label = self.label(R"4\sqrt{17}", sp(12, 9.4), UR, WHITE, 30, 0.02)
        self.add_step(R"AC = \sqrt{16^2 + 4^2} = 4\sqrt{17}", wait=0.4)
        self.play(FadeIn(ac_label), run_time=0.4)
        self.set_state("ac", VGroup(ac, tri, legs, ac_label))

    def rotate(self):
        fig = self.get_figure()
        ac_group = self.lazy("ac", VGroup)
        tri = ac_group[1]

        # A quarter turn about A carries the blue triangle to the left side
        copy = tri.copy()
        self.play(Rotate(copy, -PI / 2, about_point=at("A")), run_time=1.4)
        b_dot = self.dot("B", YELLOW)
        b_name = self.label("B", at("B"), LEFT, YELLOW)
        ab = Line(at("A"), at("B")).set_stroke(WHITE, 3.5)
        legs = VGroup(
            self.label("8", sp(0, 8), RIGHT, BLUE, 30),
            self.label("2", sp(-1, 4), DOWN, BLUE, 28, 0.06),
        )
        mark = self.right_angle("A", (1, -0.25), (-0.25, -1))
        self.play(ShowCreation(ab), FadeIn(b_dot), FadeIn(b_name), FadeIn(legs), ShowCreation(mark), run_time=0.9)
        self.add_step(R"AB = \sqrt{8^2 + 2^2} = 2\sqrt{17},\quad AB \perp AC", wait=0.5)

        # P sees BC at a right angle as well
        pb = Line(at("P"), at("B")).set_stroke(GREY_A, 2.5)
        pc = Line(at("P"), at("C")).set_stroke(GREY_A, 2.5)
        p_mark = self.right_angle("P", (-1, 2), (2, 1), size=0.18, color=GREY_A)
        self.play(ShowCreation(pb), ShowCreation(pc), ShowCreation(p_mark), run_time=0.8)
        self.note("A and P both see BC at 90°, so the circle on\ndiameter BC is our circle: BC is a diameter.", wait=1.6)
        self.play(FadeOut(VGroup(pb, pc, p_mark)), run_time=0.4)
        self.set_state("b", VGroup(copy, b_dot, b_name, ab, legs, mark))

    def diameter(self):
        fig = self.get_figure()
        bc = Line(at("B"), at("C")).set_stroke(DIAM, 6)
        self.play(ShowCreation(bc), run_time=0.9)
        center = Dot(sp(*CENTER), radius=0.07).set_fill(DIAM)
        self.play(FadeIn(center, scale=0.5), run_time=0.3)

        steps = self.steps()
        self.play(FadeOut(VGroup(*steps)), run_time=0.3)
        steps.set_submobjects([])
        line = self.add_step(R"BC^2 = AB^2 + AC^2 = 68 + 272 = 340", wait=0.5)
        self.replace_step(line, R"BC = \sqrt{340} = 2\sqrt{85}", color=DIAM, wait=0.5)
        radius = Line(sp(*CENTER), at("C")).set_stroke(RESULT_COLOR, 6)
        self.play(ShowCreation(radius), Indicate(fig.circle, color=RESULT_COLOR, scale_factor=1.02), run_time=0.9)
        self.conclude(R"R = \tfrac{1}{2}BC = \sqrt{85}", font_size=48, wait=1.4)
