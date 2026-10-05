from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/five_solutions_quad.py
#
# ABCD: BC = CD, AC bisects angle A, angle ACB = 90, angle ACD = 20.  Find
# alpha = angle ABC.  Answer 55 degrees, five ways.
#
# Coordinates (checked numerically): C(0, 0), B(-1, 0), A(0, tan 55),
# D(sin 20, cos 20).
#   1. BC and AD meet at T(1, 0): AC is altitude and bisector in ABT, so CT = CB
#      = CD; angle DCT = 70, so angle T = 55 = alpha.
#   2. Reflect D in AC: D'(-sin 20, cos 20) lands on AB, CD' = CB, angle
#      BCD' = 70, so alpha = 55.
#   3. BCD is isosceles with apex 110: 35 at B.  ABCD is cyclic (AB is a
#      diameter, D is on the circle), so angle ABD = angle ACD = 20; 35 + 20.
#   4. Turn ABC about C by -110 (B -> D): A -> P, and A, D, P line up.  ACP is
#      isosceles with apex 110, so angle P = 35 and alpha = 90 - 35.
#   5. Turn CDA about C by +110 (D -> B): A -> Q, and A, B, Q line up.  ACQ is
#      isosceles with apex 110, so angle BAC = 35 and alpha = 90 - 35.

A55, A20 = 55 * DEGREES, 20 * DEGREES


def rot(p, t):
    return np.array([p[0] * np.cos(t) - p[1] * np.sin(t), p[0] * np.sin(t) + p[1] * np.cos(t)])


PT = {"A": np.array([0, np.tan(A55)]), "B": np.array([-1.0, 0]), "C": np.array([0.0, 0]),
      "D": np.array([np.sin(A20), np.cos(A20)])}
PT["T"] = np.array([1.0, 0])
PT["D'"] = np.array([-np.sin(A20), np.cos(A20)])
PT["P"] = rot(PT["A"], -110 * DEGREES)
PT["Q"] = rot(PT["A"], 110 * DEGREES)
CIRCLE_CENTER = (PT["A"] + PT["B"]) / 2

SCALE = 2.7
FIG = 0.55 * UP
MID_Y = (PT["A"][1] + PT["P"][1]) / 2

GOLD = YELLOW
C1, C2, C3, C4, C5 = "#C39BFF", "#FF5C5C", "#58C4DD", "#FF6B6B", "#5BD98A"
EQ_Y = -3.35


def sp(name):
    x, y = PT[name] if isinstance(name, str) else name
    return FIG + SCALE * np.array([x, y - MID_Y, 0])


class FiveSolutionsQuad(BrandOutroMixin, ShortsScene):
    """One angle problem, five solutions."""

    sections = ["intro", "sol1", "sol2", "sol3", "sol4", "sol5", "finale", "outro"]

    # Drawing helpers

    def seg(self, a, b, color=WHITE, width=3.5, dashed=False):
        if dashed:
            return DashedLine(sp(a), sp(b), dash_length=0.1).set_stroke(color, width)
        return Line(sp(a), sp(b)).set_stroke(color, width)

    def tri(self, names, color, opacity=0.3):
        return Polygon(*[sp(n) for n in names]).set_stroke(color, 3).set_fill(color, opacity)

    def arc(self, v, p1, p2, color, radius=0.42, tex=None, font_size=28, label_r=None):
        vs, a = sp(v), angle_of_vector(sp(p1) - sp(v))
        delta = (angle_of_vector(sp(p2) - sp(v)) - a + PI) % TAU - PI
        mob = VGroup(Arc(a, delta, radius=radius, arc_center=vs).set_stroke(color, 4))
        if tex:
            mid = a + delta / 2
            r = label_r or radius + 0.3
            mob.add(Tex(tex, font_size=font_size).set_color(color).move_to(vs + r * np.array([np.cos(mid), np.sin(mid), 0])))
        return mob

    def right(self, v, p1, p2, size=0.2, color=WHITE):
        vs = sp(v)
        d1, d2 = normalize(sp(p1) - vs), normalize(sp(p2) - vs)
        return VMobject().set_points_as_corners([vs + size * d1, vs + size * (d1 + d2), vs + size * d2]).set_stroke(color, 2.5)

    def tick(self, a, b, color=GOLD, count=1):
        mid, d = (sp(a) + sp(b)) / 2, normalize(sp(b) - sp(a))
        n = rotate_vector(d, PI / 2)
        return VGroup(*[
            Line(mid + (k - (count - 1) / 2) * 0.09 * d - 0.13 * n, mid + (k - (count - 1) / 2) * 0.09 * d + 0.13 * n).set_stroke(color, 3)
            for k in range(count)
        ])

    def point(self, name, direction, color=WHITE):
        return VGroup(
            Dot(sp(name), radius=0.06).set_fill(color),
            Tex(name, font_size=32).set_color(color).next_to(sp(name), direction, buff=0.08),
        )

    def badge(self, k, text, color):
        head = Text(f"Solution {k}", font_size=34, weight=BOLD).set_color(color)
        sub = Text(text, font_size=24).set_color(GREY_A)
        return VGroup(head, sub).arrange(DOWN, buff=0.1).move_to(4.15 * UP)

    def equation(self, tex, color=WHITE, font_size=40):
        return Tex(tex, font_size=font_size).set_color(color).move_to(EQ_Y * UP)

    def run_solution(self, k, text, color, build):
        """Badge in, the solution's own animations, then everything it added out."""
        before = set(id(m) for m in self.mobjects)
        badge = self.badge(k, text, color)
        old = self.lazy_state.get("badge")
        self.play(*([FadeOut(old, 0.2 * UP)] if old else []), FadeIn(badge, 0.2 * UP), run_time=0.5)
        self.set_state("badge", badge)
        build()
        self.wait(1.4)
        added = [m for m in self.mobjects if id(m) not in before and m is not badge]
        self.play(*[FadeOut(m) for m in added], run_time=0.4)

    # Sections

    def setup_figure(self):
        quad = Polygon(*[sp(n) for n in "ABCD"]).set_stroke(WHITE, 3.5)
        diag = self.seg("A", "C", WHITE, 3)
        names = VGroup(
            self.point("A", UP), self.point("B", LEFT), self.point("C", DR), self.point("D", RIGHT),
        )
        marks = VGroup(
            self.right("C", "B", "A"),
            self.arc("C", "A", "D", GOLD, 0.55, R"20^\circ", 26, 0.85),
            self.arc("B", "C", "A", C3, 0.45, R"\alpha", 32),
            self.arc("A", "B", "C", WHITE, 0.5), self.arc("A", "C", "D", WHITE, 0.58),
            self.tick("B", "C"), self.tick("C", "D"),
        )
        return VGroup(quad, diag, names, marks)

    def get_figure(self):
        return self.lazy("figure", self.setup_figure)

    def intro(self):
        title = Text("One problem, five solutions", font_size=44, weight=BOLD).set_color(GOLD)
        given = Tex(
            R"BC = CD,\ \ \angle BAC = \angle CAD,\ \ \angle ACD = 20^\circ.\ \ \alpha = ?",
            font_size=34,
        ).set_max_width(7.4)
        header = VGroup(title, given).arrange(DOWN, buff=0.25).move_to(5.55 * UP)
        fig = self.setup_figure()
        # The thumbnail frame: title and the whole figure
        self.add(header, fig)
        self.wait(1.2)
        choices = Tex(R"A)\ 40^\circ \quad B)\ 45^\circ \quad C)\ 50^\circ \quad D)\ 55^\circ", font_size=34)
        choices.set_color(GREY_A).move_to(EQ_Y * UP)
        self.play(FadeIn(choices, 0.15 * UP), run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(choices), run_time=0.3)
        self.set_state("figure", fig)
        self.set_state("header", header)

    def sol1(self):
        self.get_figure()

        def build():
            lines = VGroup(self.seg("C", "T", C1, 3, True), self.seg("D", "T", C1, 3, True))
            t = self.point("T", DR, C1)
            self.play(ShowCreation(lines), FadeIn(t), run_time=0.8)
            self.play(Indicate(self.get_figure()[1], color=GOLD, scale_factor=1.03), run_time=0.6)
            self.play(FadeIn(self.tick("C", "T")), run_time=0.4)
            yellow = self.tri(["C", "D", "T"], GOLD, 0.3)
            c70 = self.arc("C", "D", "T", GOLD, 0.35, R"70^\circ", 26, 0.62)
            self.play(FadeIn(yellow), ShowCreation(c70), run_time=0.6)
            t55 = self.arc("T", "C", "D", C1, 0.4, R"55^\circ", 26, 0.72)
            self.play(ShowCreation(t55), run_time=0.5)
            eq = self.equation(R"\angle T = \tfrac{180^\circ - 70^\circ}{2} = 55^\circ = \alpha")
            self.play(FadeIn(eq, 0.2 * UP), TransformFromCopy(t55[1], eq[R"55^\circ"][0]), run_time=0.9)

        self.run_solution(1, "extend BC and AD to meet at T", C1, build)

    def sol2(self):
        fig = self.get_figure()

        def build():
            glow = self.seg("A", "C", GOLD, 7)
            self.play(ShowCreation(glow), run_time=0.4)
            flap = self.tri(["A", "C", "D"], C2, 0.3)
            self.add(flap)
            self.play(Rotate(flap, PI, axis=normalize(sp("A") - sp("C")), about_point=sp("C")), run_time=1.2)
            dp = self.point("D'", LEFT, C2)
            cd = self.seg("C", "D'", C2, 4)
            self.play(FadeIn(dp), ShowCreation(cd), FadeIn(self.tick("C", "D'", C2)), run_time=0.6)
            c70 = self.arc("C", "B", "D'", C2, 0.35, R"70^\circ", 26, 0.62)
            iso = self.tri(["B", "C", "D'"], C2, 0.25)
            self.play(FadeOut(flap), FadeIn(iso), ShowCreation(c70), run_time=0.6)
            self.play(Indicate(self.arc("D'", "B", "C", C2, 0.35), color=C2), run_time=0.5)
            eq = self.equation(R"\alpha = \tfrac{180^\circ - 70^\circ}{2} = 55^\circ")
            self.play(FadeIn(eq, 0.2 * UP), run_time=0.6)

        self.run_solution(2, "reflect D across the bisector AC", C2, build)

    def sol3(self):
        def build():
            bd = self.seg("B", "D", C3, 3)
            bcd = self.tri(["B", "C", "D"], C3, 0.25)
            self.play(ShowCreation(bd), FadeIn(bcd), run_time=0.6)
            b35 = self.arc("B", "C", "D", C3, 0.75, R"35^\circ", 24, 1.05)
            d35 = self.arc("D", "B", "C", C3, 0.35, R"35^\circ", 24, 0.62)
            self.play(ShowCreation(b35), ShowCreation(d35), run_time=0.6)
            circle = Circle(radius=SCALE * np.linalg.norm(PT["A"] - CIRCLE_CENTER)).move_to(sp(CIRCLE_CENTER)).set_stroke(C3, 3)
            self.play(ShowCreation(circle), FadeOut(bcd), run_time=1.0)
            b20 = self.arc("B", "D", "A", GOLD, 1.05, R"20^\circ", 24, 1.35)
            arrow = CurvedArrow(sp("C") + 0.7 * UP + 0.25 * RIGHT, sp("B") + 1.25 * UP + 0.35 * RIGHT, angle=0.8).set_color(GOLD)
            self.play(ShowCreation(arrow), ShowCreation(b20), run_time=0.8)
            eq = self.equation(R"\alpha = 35^\circ + 20^\circ = 55^\circ")
            self.play(FadeIn(eq, 0.2 * UP), run_time=0.6)

        self.run_solution(3, "a cyclic quadrilateral", C3, build)

    def sol4(self):
        def build():
            red = self.tri(["A", "B", "C"], C4, 0.35)
            self.add(red)
            self.play(Rotate(red, -110 * DEGREES, about_point=sp("C")), run_time=1.3)
            p = self.point("P", DR, C4)
            marks = VGroup(self.tick("C", "A", C4, 2), self.tick("C", "P", C4, 2), self.right("C", "D", "P", color=C4))
            self.play(FadeIn(p), FadeIn(marks), run_time=0.5)
            ap = self.seg("A", "P", C4, 3)
            acp = self.tri(["A", "C", "P"], GOLD, 0.2)
            c110 = self.arc("C", "A", "P", GOLD, 0.3, R"110^\circ", 24, 0.62)
            self.play(ShowCreation(ap), FadeIn(acp), ShowCreation(c110), run_time=0.7)
            base = VGroup(self.arc("P", "C", "A", GOLD, 0.45, R"35^\circ", 24, 0.78))
            self.play(ShowCreation(base), run_time=0.5)
            eq = self.equation(R"\angle P = 35^\circ \Rightarrow \alpha = 90^\circ - 35^\circ = 55^\circ")
            self.play(FadeIn(eq, 0.2 * UP), run_time=0.6)

        self.run_solution(4, "rotate triangle ABC about C", C4, build)

    def sol5(self):
        def build():
            green = self.tri(["C", "D", "A"], C5, 0.35)
            arrow = CurvedArrow(sp("C") + 1.0 * UP + 0.6 * RIGHT, sp("C") + 0.9 * LEFT + 0.6 * DOWN, angle=-1.6).set_color(C5)
            self.add(green)
            self.play(Rotate(green, 110 * DEGREES, about_point=sp("C")), ShowCreation(arrow), run_time=1.3)
            q = self.point("Q", DL, C5)
            marks = VGroup(self.tick("C", "A", C5, 2), self.tick("C", "Q", C5, 2))
            c20 = self.arc("C", "Q", "B", C5, 0.45, R"20^\circ", 22, 0.75)
            self.play(FadeIn(q), FadeIn(marks), ShowCreation(c20), FadeOut(arrow), run_time=0.6)
            aq = self.seg("A", "Q", C5, 3)
            acq = self.tri(["A", "C", "Q"], GOLD, 0.2)
            c110 = self.arc("C", "Q", "A", GOLD, 0.3, R"110^\circ", 24, 0.95)
            self.play(ShowCreation(aq), FadeIn(acq), ShowCreation(c110), run_time=0.7)
            a35 = self.arc("A", "Q", "C", GOLD, 0.8, R"35^\circ", 24, 1.1)
            self.play(ShowCreation(a35), run_time=0.5)
            eq = self.equation(R"\angle BAC = 35^\circ \Rightarrow \alpha = 90^\circ - 35^\circ = 55^\circ")
            self.play(FadeIn(eq, 0.2 * UP), run_time=0.6)

        self.run_solution(5, "rotate triangle CDA about C", C5, build)

    def finale(self):
        fig = self.get_figure()
        badge = self.lazy_state.get("badge")
        answer = Tex(R"\alpha = 55^\circ", font_size=64).set_color(GOLD).move_to(EQ_Y * UP)
        box = SurroundingRectangle(answer, buff=0.22).set_stroke(GOLD, 4)
        note = Text("Five different ideas, one answer.", font_size=28).set_color(GREY_A).next_to(box, DOWN, buff=0.35)
        self.play(*([FadeOut(badge)] if badge else []), Write(answer), run_time=0.8)
        self.play(ShowCreation(box), FadeIn(note, 0.15 * UP), FlashAround(answer, color=GOLD, time_width=1.5), run_time=1.2)
        self.wait(1.2)
