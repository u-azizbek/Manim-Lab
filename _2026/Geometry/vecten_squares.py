from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/vecten_squares.py
#
# Squares AKLB and ACEF stand outside triangle ABC on AB and AC.  The altitude
# DA, extended past A, meets KF at M, with MA = 8 and KM = 3.  Find the sum of
# the squares' areas, AB^2 + AC^2.
#
# Drop KH and FT onto the altitude line.  A quarter turn carries ABD onto KAH
# and ADC onto FTA, so KH = AD = FT; a half turn about M then carries KHM onto
# FTM, so MF = KM = 3.  Doubling AM to P makes AKPF a parallelogram with
# diagonals AP = 16 and KF = 6, and the parallelogram law gives
# 2(a^2 + b^2) = 16^2 + 6^2, so a^2 + b^2 = 146.
#
# The figure is an exact instance of the data -- BD = 13/2, DC = 19/2,
# AD = 3 sqrt(3)/2, so AB = 7 and AC = sqrt(97) -- and each congruence is a
# genuine rotation, checked with sympy, which is what lets the video turn one
# triangle onto the other.

AD = 1.5 * np.sqrt(3)
BD, DC = 6.5, 9.5
SCALE = 0.34                # the figure is 21.2 units wide, the frame 8
X_SHIFT = -1.5              # centres the figure (it runs from L at -9.1 to E at 12.1)


def quarter(v, sign):
    """A quarter turn of a 2D vector: +1 counter-clockwise, -1 clockwise."""
    return np.array([-v[1], v[0]]) * sign


_A, _B, _C, _D = map(np.array, [(0.0, AD), (-BD, 0.0), (DC, 0.0), (0.0, 0.0)])
_K = _A + quarter(_B - _A, -1)
_F = _A + quarter(_C - _A, +1)
PTS = {
    "A": _A, "B": _B, "C": _C, "D": _D,
    "K": _K, "L": _B + (_K - _A),
    "F": _F, "E": _C + (_F - _A),
    "M": (_K + _F) / 2,
    "H": np.array([0.0, _K[1]]),        # foot of K on the altitude line
    "T": np.array([0.0, _F[1]]),        # foot of F on the altitude line
    "P": _K + _F - _A,                  # completes the parallelogram AKPF
}

# (triangle, the one it turns onto, angle) -- the centre follows from these
TURNS = {
    "first": (("A", "B", "D"), ("K", "A", "H"), PI / 2),
    "second": (("A", "D", "C"), ("F", "T", "A"), -PI / 2),
    "half": (("K", "H", "M"), ("F", "T", "M"), PI),
}

SQ_AB = "#8C7BFF"
SQ_AC = "#2EC4B6"
PAIR_1 = "#FF9F43"
PAIR_2 = "#FF6B9A"
PAIR_3 = YELLOW
PARA = "#FFD166"
LINE = GREY_A


def turn_center(p, q, angle):
    """The centre of the rotation by `angle` that carries p to q."""
    R = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return np.linalg.solve(np.eye(2) - R, q - R @ p)


class VectenSquares(MockTestShort):
    """Sum of two squares on the sides of a triangle, via congruent turns and
    the parallelogram law."""

    test = ""
    card_top_buff = 0.85
    step_buff = 0.4

    problem_tex = (
        R"\text{Squares on } AB,\ AC;\ MA \perp BC.\\"
        R"MA = 8,\ KM = 3.\ \text{Total area?}"
    )

    sections = [
        "pose",
        "draw_figure",
        "first_turn",
        "second_turn",
        "half_turn",
        "parallelogram",
        "finish",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        # Hang the figure off the card: F is its highest point until P appears
        fig_top = card.get_bottom()[1] - 0.45
        self.origin = X_SHIFT * SCALE * RIGHT + (fig_top - PTS["F"][1] * SCALE) * UP
        self.steps_top_y = self.origin[1] - 0.8
        return card

    # Geometry

    def p(self, name):
        self.get_card()
        x, y = PTS[name]
        return self.origin + SCALE * (x * RIGHT + y * UP)

    def poly(self, *names):
        return Polygon(*[self.p(n) for n in names])

    def seg(self, a, b):
        return Line(self.p(a), self.p(b))

    def right_angle(self, corner, a, b, size=0.16, color=GREY_A):
        c = self.p(corner)
        u = normalize(self.p(a) - c) * size
        v = normalize(self.p(b) - c) * size
        mark = VMobject().set_points_as_corners([c + u, c + u + v, c + v])
        return mark.set_stroke(color, 2)

    def label(self, tex, near, direction, buff=0.1, font_size=30, color=WHITE):
        return Tex(tex, font_size=font_size).set_color(color).next_to(self.p(near), direction, buff=buff)

    def side_label(self, tex, a, b, offset, font_size=30, color=WHITE):
        """A label beside segment ab, pushed `offset` along its left normal."""
        pa, pb = self.p(a), self.p(b)
        normal = rotate_vector(normalize(pb - pa), PI / 2)
        return Tex(tex, font_size=font_size).set_color(color).move_to(midpoint(pa, pb) + offset * normal)

    def turn(self, key):
        """The triangle, its partner, and the rotation between them."""
        src, dst, angle = TURNS[key]
        p, q = PTS[src[0]], PTS[dst[0]]
        c = turn_center(p, q, angle)
        center = self.origin + SCALE * (c[0] * RIGHT + c[1] * UP)
        return self.poly(*src), self.poly(*dst), angle, center

    def figure_parts(self):
        """Everything drawn for the figure.  The camera frame is itself one of
        the scene's mobjects, so it has to be left out too -- shifting it
        would move the view instead of the figure."""
        card = set(self.get_card().get_family())
        return [m for m in self.mobjects if m is not self.frame and m not in card]

    # Sections

    def draw_figure(self):
        self.get_card()
        triangle = self.poly("A", "B", "C").set_stroke(WHITE, 3)
        sq_ab = self.poly("A", "K", "L", "B").set_fill(SQ_AB, 0.35).set_stroke(SQ_AB, 3)
        sq_ac = self.poly("A", "C", "E", "F").set_fill(SQ_AC, 0.35).set_stroke(SQ_AC, 3)
        kf = self.seg("K", "F").set_stroke(LINE, 2.5)
        altitude = self.seg("D", "M").set_stroke(LINE, 2.5)
        foot = self.right_angle("D", "C", "A")
        letters = VGroup(
            self.label("A", "A", RIGHT, buff=0.12),
            self.label("B", "B", DL), self.label("C", "C", DR),
            self.label("D", "D", DOWN), self.label("E", "E", RIGHT),
            self.label("F", "F", UP), self.label("K", "K", UL),
            self.label("L", "L", LEFT), self.label("M", "M", UL, buff=0.06),
        )
        eight = self.side_label("8", "A", "M", 0.22)
        three = self.side_label("3", "K", "M", 0.24)

        self.play(ShowCreation(triangle), run_time=0.8)
        self.add(sq_ab, sq_ac, triangle)
        self.play(DrawBorderThenFill(sq_ab), DrawBorderThenFill(sq_ac), run_time=1.1)
        self.play(ShowCreation(altitude), ShowCreation(foot), ShowCreation(kf), run_time=0.9)
        self.play(FadeIn(letters, lag_ratio=0.05), run_time=0.6)
        self.play(FadeIn(eight, scale=0.6), FadeIn(three, scale=0.6), run_time=0.5)
        self.set_state("squares", VGroup(sq_ab, sq_ac))
        self.set_state("eight", eight)
        self.wait(0.6)

    def first_turn(self):
        self.get_card()
        drop = DashedLine(self.p("K"), self.p("H"), dash_length=0.07).set_stroke(PAIR_1, 2.5)
        mark = self.right_angle("H", "K", "A", color=PAIR_1)
        h_label = self.label("H", "H", RIGHT, buff=0.08, font_size=28, color=PAIR_1)
        self.play(ShowCreation(drop), ShowCreation(mark), FadeIn(h_label), run_time=0.7)

        source, target, angle, center = self.turn("first")
        source.set_fill(PAIR_1, 0.7).set_stroke(PAIR_1, 2)
        self.play(FadeIn(source), run_time=0.4)
        moving = source.copy()
        self.play(Rotate(moving, angle, about_point=center), run_time=1.4)
        self.add_step(R"\triangle ABD \cong \triangle KAH \quad\Rightarrow\quad KH = AD", font_size=36, wait=0.7)
        self.set_state("first", VGroup(drop, mark, h_label, source, moving))

    def second_turn(self):
        self.get_card()
        drop = DashedLine(self.p("F"), self.p("T"), dash_length=0.07).set_stroke(PAIR_2, 2.5)
        up = DashedLine(self.p("M"), self.p("T"), dash_length=0.07).set_stroke(LINE, 2)
        mark = self.right_angle("T", "F", "A", color=PAIR_2)
        t_label = self.label("T", "T", LEFT, buff=0.08, font_size=28, color=PAIR_2)
        self.play(ShowCreation(up), ShowCreation(drop), ShowCreation(mark), FadeIn(t_label), run_time=0.7)

        source, target, angle, center = self.turn("second")
        source.set_fill(PAIR_2, 0.7).set_stroke(PAIR_2, 2)
        self.play(FadeIn(source), run_time=0.4)
        moving = source.copy()
        self.play(Rotate(moving, angle, about_point=center), run_time=1.4)
        self.add_step(R"\triangle ADC \cong \triangle FTA \quad\Rightarrow\quad FT = AD", font_size=36, wait=0.7)
        self.set_state("second", VGroup(up, drop, mark, t_label, source, moving))

    def half_turn(self):
        self.get_card()
        first = self.lazy("first", VGroup)
        second = self.lazy("second", VGroup)
        # The big triangles have done their job; keep the two drops
        self.play(
            FadeOut(VGroup(*first[3:], *second[4:])),
            run_time=0.5,
        )

        source, target, angle, center = self.turn("half")
        source.set_fill(PAIR_3, 0.75).set_stroke(PAIR_3, 2)
        self.play(FadeIn(source), run_time=0.4)
        moving = source.copy()
        self.play(Rotate(moving, angle, about_point=center), run_time=1.3)

        three = self.side_label("3", "M", "F", 0.24, color=PAIR_3)
        steps = self.steps()
        joined = Tex(R"KH = FT \quad\Rightarrow\quad KM = MF = 3", font_size=38)
        joined.move_to(steps[0]).set_x(0)
        self.play(
            FadeOut(steps[1], 0.3 * UP),
            ReplacementTransform(steps[0], joined),
            FadeIn(three, scale=0.6),
            run_time=1.0,
        )
        steps.set_submobjects([joined])
        self.wait(0.8)
        self.set_state("half", VGroup(*first[:3], *second[:4], source, moving))
        self.set_state("three_mf", three)

    def parallelogram(self):
        self.get_card()
        helpers = self.lazy("half", VGroup)
        self.play(FadeOut(helpers), FadeOut(self.steps()), run_time=0.5)
        self._step_lines = VGroup()

        # Make room above for P: slide the whole figure down
        rise = (PTS["P"][1] - PTS["F"][1]) * SCALE
        self.play(*[m.animate.shift(rise * DOWN) for m in self.figure_parts()], run_time=1.0)
        self.origin = self.origin + rise * DOWN
        self.steps_top_y -= rise

        # AM doubled: AP is a diagonal, KF the other, so AKPF is a parallelogram
        extension = self.seg("M", "P").set_stroke(PARA, 3)
        eight = self.side_label("8", "M", "P", 0.22, color=PARA)
        sides = VGroup(self.seg("K", "P"), self.seg("P", "F")).set_stroke(PARA, 3)
        body = self.poly("A", "K", "P", "F").set_fill(PARA, 0.12).set_stroke(width=0)
        p_label = self.label("P", "P", UP, color=PARA)
        self.play(ShowCreation(extension), FadeIn(eight), FadeIn(p_label), run_time=0.8)
        self.add(body)
        self.bring_to_back(body)
        self.play(ShowCreation(sides), FadeIn(body), run_time=0.8)
        a_label = self.side_label("a", "A", "K", 0.26, color=SQ_AB)
        b_label = self.side_label("b", "A", "F", -0.26, color=SQ_AC)
        self.play(FadeIn(a_label, scale=0.6), FadeIn(b_label, scale=0.6), run_time=0.5)

        self.add_step(R"AP = 8 + 8 = 16, \qquad KF = 3 + 3 = 6", font_size=36, wait=0.6)
        self.set_state("para", VGroup(extension, sides, body))

    def finish(self):
        self.get_card()
        squares = self.lazy("squares", VGroup)
        self.note("Parallelogram law: the diagonals' squares\nadd up to the four sides' squares.", wait=1.3)
        law = self.add_step(R"2(a^2 + b^2) = 16^2 + 6^2 = 292", font_size=40, wait=0.9)
        answer = self.replace_step(
            law, R"a^2 + b^2 = 146",
            font_size=54, color=RESULT_COLOR, wait=0.3,
        )

        # The two areas are a^2 and b^2: light them up
        sq_ab, sq_ac = squares
        areas = VGroup(
            Tex("a^2", font_size=40).set_color(SQ_AB).move_to(sq_ab.get_center()),
            Tex("b^2", font_size=40).set_color(SQ_AC).move_to(sq_ac.get_center()),
        )
        self.play(
            sq_ab.animate.set_fill(opacity=0.7),
            sq_ac.animate.set_fill(opacity=0.7),
            FadeIn(areas, scale=0.6),
            run_time=0.8,
        )
        box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.2).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(answer, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.wait(1.4)
