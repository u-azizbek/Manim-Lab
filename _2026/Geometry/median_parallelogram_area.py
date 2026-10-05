from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/median_parallelogram_area.py
#
# A triangle has sides sqrt(4a^2+3), sqrt(a^2-a+1), sqrt(a^2+a+1).  Find its area.
# Double the median AM through the midpoint M of BC to D: ABDC is a
# parallelogram, and the parallelogram law AD^2 + BC^2 = 2(AB^2 + AC^2) gives
# AD^2 + 4a^2 + 3 = 4a^2 + 4, so AD = 1 whatever a is.  The diagonal AD halves
# ABDC, so [ABC] = [ABD].  Lay AD flat with M at the origin: A = (1/2, 0),
# D = (-1/2, 0).  The point B = (a, sqrt3/2) has AB^2 = (a - 1/2)^2 + 3/4 and
# BD^2 = (a + 1/2)^2 + 3/4, exactly the given sides, so B sits at the height
# of the apex E of the equilateral triangle on AD.  Sliding B to E keeps the
# base and the height: [ABC] = [ADE] = sqrt3/4.
#
# The whole figure is drawn in those coordinates (C = -B), then turned so BC
# lies flat for the opening.

A_VAL = 0.7
H = np.sqrt(3) / 2
P = {
    name: np.array([x, y, 0.0]) for name, (x, y) in dict(
        A=(0.5, 0), D=(-0.5, 0), B=(A_VAL, H), C=(-A_VAL, -H), M=(0, 0), E=(0, H), H=(A_VAL, 0),
    ).items()
}
THETA = -angle_of_vector(P["C"] - P["B"])    # turns BC to point right
SCALE = 2.9
BIG = 3.4

SIDE_BC = "#58C4DD"
SIDE_AB = "#5BD98A"      # sqrt(a^2 - a + 1)
SIDE_AC = "#FF9F43"      # sqrt(a^2 + a + 1)
ABC_FILL = "#58C4DD"
ABD_FILL = "#FF6BD6"
PARA_FILL = "#7F8CFF"
EQ_COLOR = "#4FD1C5"
AD_COLOR = YELLOW


class MedianParallelogramArea(MockTestShort):
    """Area of a triangle from its sides, by doubling the median and shearing."""

    test = ""
    step_buff = 0.4
    step_font_size = 38

    problem_tex = (
        R"\text{Triangle sides: } \sqrt{4a^2+3},\\"
        R"\sqrt{a^2-a+1},\ \ \sqrt{a^2+a+1}.\\"
        R"\text{Find its area.}"
    )

    sections = ["pose", "median", "diagonal", "halves", "equilateral", "shear", "outro"]

    # Geometry helpers

    def world(self, p):
        """A point in the flat-AD coordinates, wherever the figure now sits."""
        m, a, d = [self.dots[n].get_center() for n in "MAD"]
        u = a - d
        return m + p[0] * u + p[1] * rotate_vector(u, PI / 2)

    def at(self, name):
        return self.dots[name].get_center()

    def ticks(self, p, q, count, color=WHITE):
        mid, direction = (p + q) / 2, normalize(q - p)
        normal = rotate_vector(direction, PI / 2)
        return VGroup(*[
            Line(mid + (k - (count - 1) / 2) * 0.1 * direction - 0.13 * normal,
                 mid + (k - (count - 1) / 2) * 0.1 * direction + 0.13 * normal).set_stroke(color, 3)
            for k in range(count)
        ])

    def side_label(self, tex, p, q, color, away, along=0.5):
        """A length label beside segment pq, on the side away from `away`."""
        label = Tex(tex, font_size=28).set_color(color)
        spot = p + along * (q - p)
        normal = rotate_vector(normalize(q - p), PI / 2)
        if np.dot(normal, spot - away) < 0:
            normal = -normal
        reach = 0.5 * abs(normal[0]) * label.get_width() + 0.5 * abs(normal[1]) * label.get_height()
        return label.move_to(spot + (0.12 + reach) * normal)

    def vertex_label(self, name, direction):
        return Tex(name, font_size=36).next_to(self.at(name), direction, buff=0.1)

    # Sections

    def pose(self):
        card = self.make_card()
        self.set_state("card", card)
        center = 0.6 * DOWN

        def base(name):
            return center + SCALE * rotate_vector(P[name], THETA)

        self.dots = {n: Dot(base(n), radius=0.06).set_fill(WHITE) for n in "ABCDM"}
        for n in "DM":
            self.dots[n].set_fill(opacity=0)
        a, b, c = self.at("A"), self.at("B"), self.at("C")
        self.sides = dict(
            BC=Line(b, c).set_stroke(SIDE_BC, 4),
            AB=Line(a, b).set_stroke(SIDE_AB, 4),
            AC=Line(a, c).set_stroke(SIDE_AC, 4),
        )
        self.abc = Polygon(a, b, c).set_stroke(width=0).set_fill(ABC_FILL, 0.25)
        self.side_labels = dict(
            BC=self.side_label(R"\sqrt{4a^2+3}", b, c, SIDE_BC, a),
            AB=self.side_label(R"\sqrt{a^2-a+1}", a, b, SIDE_AB, c),
            AC=self.side_label(R"\sqrt{a^2+a+1}", a, c, SIDE_AC, b),
        )
        self.names = dict(A=self.vertex_label("A", UP), B=self.vertex_label("B", LEFT), C=self.vertex_label("C", RIGHT))
        question = Tex("S = ?", font_size=48).set_color(YELLOW).next_to(self.side_labels["BC"], DOWN, buff=0.45)

        self.fig = VGroup(
            self.abc, *self.sides.values(), *self.dots.values(), *self.side_labels.values(), *self.names.values(),
        )
        self.play(FadeIn(card, 0.2 * DOWN), ShowCreation(VGroup(*self.sides.values()), lag_ratio=0.2), run_time=1.1)
        self.play(
            FadeIn(self.abc), FadeIn(VGroup(*self.side_labels.values()), lag_ratio=0.2),
            FadeIn(VGroup(*[self.dots[n] for n in "ABC"], *self.names.values())), FadeIn(question, scale=0.8),
            run_time=0.9,
        )
        self.wait(2.4)

        # Up under the card, making room for the working
        m_y = card.get_bottom()[1] - 2.05
        self.play(self.fig.animate.shift((m_y - self.at("M")[1]) * UP), FadeOut(question), run_time=0.9)
        self.steps_top_y = m_y - 2.05

    def median(self):
        a, b, c, m, d = [self.at(n) for n in "ABCMD"]

        # M halves BC; the median AM, doubled to D
        self.dots["M"].set_fill(opacity=1)
        self.names["M"] = self.vertex_label("M", DL)
        single = VGroup(self.ticks(b, m, 1), self.ticks(m, c, 1))
        self.play(
            FadeOut(self.side_labels["BC"]), FadeIn(self.dots["M"], scale=0.5), FadeIn(self.names["M"]),
            ShowCreation(single), run_time=0.7,
        )
        self.am = Line(a, m).set_stroke(WHITE, 3)
        self.md = Line(m, d).set_stroke(WHITE, 3)
        self.play(ShowCreation(self.am), run_time=0.5)
        self.dots["D"].set_fill(opacity=1)
        self.names["D"] = self.vertex_label("D", DOWN)
        double = VGroup(self.ticks(a, m, 2), self.ticks(m, d, 2))
        self.play(ShowCreation(self.md), FadeIn(self.dots["D"], scale=0.5), FadeIn(self.names["D"]), run_time=0.7)
        self.play(ShowCreation(double), run_time=0.4)

        # Opposite sides of the parallelogram come across
        self.sides["BD"] = Line(b, d).set_stroke(SIDE_AC, 4)
        self.sides["CD"] = Line(c, d).set_stroke(SIDE_AB, 4)
        self.side_labels["BD"] = self.side_label(R"\sqrt{a^2+a+1}", b, d, SIDE_AC, a)
        self.side_labels["CD"] = self.side_label(R"\sqrt{a^2-a+1}", c, d, SIDE_AB, a)
        self.play(
            TransformFromCopy(self.sides["AC"], self.sides["BD"]),
            TransformFromCopy(self.sides["AB"], self.sides["CD"]),
            TransformFromCopy(self.side_labels["AC"], self.side_labels["BD"]),
            TransformFromCopy(self.side_labels["AB"], self.side_labels["CD"]),
            run_time=1.2,
        )
        self.para = Polygon(a, b, d, c).set_stroke(width=0).set_fill(PARA_FILL, 0.18)
        self.play(FadeIn(self.para), run_time=0.4)
        self.add(self.am, self.md, *self.dots.values())
        self.note("Double the median: the diagonals bisect\neach other, so ABDC is a parallelogram.", wait=1.4)
        self.marks = VGroup(single, double)

    def diagonal(self):
        # The parallelogram law pins down the other diagonal
        law = self.add_step(R"AD^2 + BC^2 = 2\left(AB^2 + AC^2\right)", wait=0.2)
        self.note("Parallelogram law: squares of the diagonals\n= squares of the four sides.", wait=1.3)
        law = self.replace_step(law, R"AD^2 + 4a^2 + 3 = 2\left(2a^2 + 2\right)", wait=0.5)
        law = self.replace_step(law, R"AD^2 = 1 \ \Rightarrow\ AD = 1", color=AD_COLOR, wait=0.2)

        a, d = self.at("A"), self.at("D")
        self.ad = Line(a, d).set_stroke(AD_COLOR, 5)
        one = self.side_label("1", a, self.at("M"), AD_COLOR, self.at("B"), along=0.45)
        one.scale(1.4)
        self.play(ShowCreation(self.ad), FadeOut(self.marks[1]), FadeIn(one, scale=0.6), run_time=0.8)
        self.add(*self.dots.values())
        self.play(Flash(one, color=AD_COLOR), run_time=0.6)
        self.wait(0.6)
        self.one = one

    def halves(self):
        self.clear_steps()
        a, b, c, d = [self.at(n) for n in "ABCD"]

        # Each diagonal cuts the parallelogram in half
        self.abd = Polygon(a, b, d).set_stroke(width=0).set_fill(ABD_FILL, 0.4)
        self.play(FadeOut(self.para), self.abc.animate.set_fill(opacity=0.45), run_time=0.6)
        self.play(FadeIn(self.abd), self.abc.animate.set_fill(opacity=0.12), run_time=0.8)
        self.add(self.ad, *self.dots.values())
        self.add_step(R"S_{ABC} = \tfrac{1}{2}\,S_{ABDC} = S_{ABD}", wait=0.2)
        self.note("A diagonal cuts a parallelogram in half.", wait=1.1)

    def equilateral(self):
        self.clear_steps()

        # Keep triangle ABD only, and lay AD flat
        gone = [
            self.abc, self.sides["BC"], self.sides["AC"], self.sides["CD"], self.am, self.md, self.one,
            self.dots["C"], self.marks, *self.side_labels.values(), *self.names.values(),
        ]
        self.play(*[FadeOut(m) for m in gone], run_time=0.6)
        self.dots.pop("C")
        kept = VGroup(self.abd, self.sides["AB"], self.sides["BD"], self.ad, *[self.dots[n] for n in "ABDM"])
        self.play(Rotate(kept, -THETA, about_point=self.at("M")), run_time=1.1)
        card = self.get_card()
        target = np.array([-0.4, card.get_bottom()[1] - 3.55, 0])
        self.play(kept.animate.scale(BIG / SCALE, about_point=self.at("M")).shift(target - self.at("M")), run_time=0.7)
        self.steps_top_y = target[1] - 1.75

        w = self.world
        names = VGroup(
            self.vertex_label("A", DOWN), self.vertex_label("D", DOWN), self.vertex_label("M", DOWN),
            self.vertex_label("B", UR),
        )
        rails = VGroup(*[
            DashedLine(w(np.array([-1.0, y, 0])), w(np.array([1.1, y, 0])), dash_length=0.1).set_stroke(GREY_B, 2)
            for y in (0, H)
        ])
        self.play(FadeIn(names), ShowCreation(rails, lag_ratio=0.3), run_time=0.8)
        self.add(kept)

        # The equilateral triangle on AD, and its height
        e = w(P["E"])
        equi = Polygon(w(P["A"]), w(P["D"]), e).set_stroke(EQ_COLOR, 3).set_fill(EQ_COLOR, 0.2)
        e_dot = Dot(e, radius=0.06).set_fill(WHITE)
        e_name = Tex("E", font_size=36).next_to(e, UP, buff=0.1)
        self.play(ShowCreation(equi), FadeIn(e_dot), FadeIn(e_name), run_time=0.8)
        height = DashedLine(e, self.at("M"), dash_length=0.08).set_stroke(EQ_COLOR, 3)
        h_label = Tex(R"\frac{\sqrt3}{2}", font_size=30).set_color(EQ_COLOR).next_to(height, LEFT, buff=0.12)
        self.play(ShowCreation(height), FadeIn(h_label), run_time=0.6)
        self.add(self.ad, *self.dots.values())
        self.note("Equilateral ADE on AD = 1: its height is √3/2.", wait=1.1)

        # B is a units along the top rail: two right triangles
        h_pt = w(P["H"])
        drop = DashedLine(self.at("B"), h_pt, dash_length=0.08).set_stroke(WHITE, 2.5)
        h_name = Tex("H", font_size=32).next_to(h_pt, DR, buff=0.08)
        corner = VMobject().set_points_as_corners([
            w(P["H"] + 0.07 * UP), w(P["H"] + 0.07 * (UP + LEFT)), w(P["H"] + 0.07 * LEFT),
        ]).set_stroke(WHITE, 2)
        brace = Brace(Line(self.at("M"), h_pt), DOWN, buff=0.5)
        a_label = Tex("a", font_size=34).next_to(brace, DOWN, buff=0.08)
        self.play(ShowCreation(drop), FadeIn(h_name), ShowCreation(corner), GrowFromCenter(brace), FadeIn(a_label), run_time=0.8)

        left = Polygon(self.at("B"), h_pt, self.at("A")).set_stroke(SIDE_AB, 3).set_fill(SIDE_AB, 0.35)
        self.play(FadeIn(left), run_time=0.4)
        self.add_step(
            R"AB^2 = \tfrac34 + \left(a - \tfrac12\right)^2 = a^2 - a + 1\ \checkmark", color=SIDE_AB, wait=0.4,
        )
        right = Polygon(self.at("B"), h_pt, self.at("D")).set_stroke(SIDE_AC, 3).set_fill(SIDE_AC, 0.25)
        self.play(FadeOut(left), FadeIn(right), run_time=0.4)
        self.add_step(
            R"BD^2 = \tfrac34 + \left(a + \tfrac12\right)^2 = a^2 + a + 1\ \checkmark", color=SIDE_AC, wait=0.4,
        )
        self.play(FadeOut(VGroup(right, drop, h_name, corner, brace, a_label)), run_time=0.4)
        self.names = names
        self.equi = VGroup(equi, e_dot, e_name, height, h_label)

    def shear(self):
        # Slide B along the top rail: same base AD, same height, same area
        w = self.world
        bx = ValueTracker(A_VAL)

        def b_pt():
            return w(np.array([bx.get_value(), H, 0]))

        tri = always_redraw(lambda: VGroup(
            Polygon(self.at("A"), b_pt(), self.at("D")).set_stroke(width=0).set_fill(ABD_FILL, 0.4),
            Line(self.at("A"), b_pt()).set_stroke(SIDE_AB, 4),
            Line(b_pt(), self.at("D")).set_stroke(SIDE_AC, 4),
        ))
        self.remove(self.abd, self.sides["AB"], self.sides["BD"])
        self.add(tri, self.ad, *self.dots.values())
        b_dot, b_name = self.dots["B"], self.names[3]
        b_dot.add_updater(lambda m: m.move_to(b_pt()))
        b_name.add_updater(lambda m: m.next_to(b_dot, UR, buff=0.1))
        self.add(b_dot, b_name)

        self.play(bx.animate.set_value(0), run_time=1.8)
        self.note("Same base, same height: the area never changes.", wait=0.8)
        self.play(bx.animate.set_value(1.0), run_time=1.0)
        self.play(bx.animate.set_value(0), run_time=0.9)
        self.play(Indicate(self.equi[0], color=EQ_COLOR, scale_factor=1.04), run_time=0.8)
        self.add_step(R"S_{ABD} = S_{ADE} = \tfrac12 \cdot 1 \cdot \tfrac{\sqrt3}{2}", wait=0.2)
        self.conclude(R"S_{ABC} = \frac{\sqrt{3}}{4}", font_size=54, wait=1.3)
        b_dot.clear_updaters()
        b_name.clear_updaters()
