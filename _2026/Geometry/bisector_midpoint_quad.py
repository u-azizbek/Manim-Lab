from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/bisector_midpoint_quad.py
#
# Quadrilateral ABCD with AB = 2, CD = 4, AD = 8; the bisectors of A and D meet
# at M, the midpoint of BC.  Find [ABCD].
#
# Fold AB onto AD about AM (K, AK = 2) and DC onto DA about DM (L, DL = 4): the
# wings are congruent, so KM = BM = CM = LM and KL = 2 has foot H with
# AH = 3.  The six angles at M are a, a, g, g, b, b and fill the straight
# angle BMC, so a + b + g = 90 and angle AMD = 90 + g = angle AKM.  Hence
# AKM ~ AMD, AM^2 = AK * AD = 16, AM = 4 and MH = sqrt(16 - 9) = sqrt 7.  M is
# sqrt 7 from AB, AD and CD (it is on both bisectors), so
#   [ABCD] = 1/2 (2 + 8 + 4) sqrt 7 = 7 sqrt 7.
# The figure is the actual one: A(0,0), D(8,0), M(3, sqrt 7), B and C the
# reflections of K and L; then BM = MC and the shoelace area is 7 sqrt 7.

S7 = np.sqrt(7)


def reflect(p, a, b):
    p, a, b = map(np.array, (p, a, b))
    d = (b - a) / np.linalg.norm(b - a)
    v = p - a
    return a + 2 * (v @ d) * d - v


PTS = {"A": (0.0, 0.0), "D": (8.0, 0.0), "M": (3.0, S7), "K": (2.0, 0.0), "L": (4.0, 0.0), "H": (3.0, 0.0)}
PTS["B"] = tuple(reflect(PTS["K"], PTS["A"], PTS["M"]))
PTS["C"] = tuple(reflect(PTS["L"], PTS["D"], PTS["M"]))

SCALE = 0.86
FIG_Y = 1.35

LEFT_WING = "#58C4DD"
RIGHT_WING = "#FF9F43"
CORE = "#5BD98A"
ALPHA = "#58C4DD"
GAMMA = "#5BD98A"
BETA = "#FF9F43"
SIMILAR = "#FF6BD6"
PARTS = ["#58C4DD", "#C39BFF", "#FF9F43"]


def sp(name_or_xy):
    x, y = PTS[name_or_xy] if isinstance(name_or_xy, str) else name_or_xy
    return np.array([SCALE * (x - 4), FIG_Y + SCALE * (y - 1.65), 0])


class BisectorMidpointQuad(MockTestShort):
    """Area of a quadrilateral whose angle bisectors meet on a side."""

    test = ""
    step_buff = 0.3
    step_font_size = 36

    problem_tex = (
        R"ABCD:\ AB = 2,\ CD = 4,\ AD = 8.\\"
        R"\text{The bisectors of } \angle A, \angle D\\"
        R"\text{meet at the midpoint } M \text{ of } BC.\\"
        R"\text{Find } S_{ABCD}."
    )

    sections = ["pose", "figure", "fold", "angles", "similar", "area", "outro"]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = sp((0, 0))[1] - 0.75
        return card

    def seg(self, a, b, color=WHITE, width=3):
        return Line(sp(a), sp(b)).set_stroke(color, width)

    def poly(self, names, color, opacity=0.35):
        return Polygon(*[sp(n) for n in names]).set_stroke(color, 2.5).set_fill(color, opacity)

    def name(self, n, direction, color=WHITE):
        return Tex(n, font_size=32).set_color(color).next_to(sp(n), direction, buff=0.08)

    def length(self, tex, a, b, side, color, font_size=28, buff=0.12):
        return Tex(tex, font_size=font_size).set_color(color).next_to((sp(a) + sp(b)) / 2, side, buff=buff)

    def make_figure(self):
        quad = Polygon(*[sp(n) for n in "ABCD"]).set_stroke(WHITE, 3.5)
        bisectors = VGroup(self.seg("A", "M", GREY_A, 2.5), self.seg("D", "M", GREY_A, 2.5))
        dots = VGroup(*[Dot(sp(n), radius=0.055).set_fill(WHITE) for n in "ABCDM"])
        names = VGroup(
            self.name("A", DL), self.name("B", UL), self.name("C", UR), self.name("D", DR), self.name("M", UP),
        )
        ticks = VGroup(*[
            Line(ORIGIN, 0.2 * UP).rotate(angle_of_vector(sp("C") - sp("B"))).move_to((sp(p) + sp("M")) / 2).set_stroke(YELLOW, 3)
            for p in "BC"
        ])
        lengths = VGroup(
            self.length("2", "A", "B", LEFT, WHITE),
            self.length("4", "C", "D", RIGHT, WHITE),
            self.length("8", "A", "D", DOWN, WHITE),
        )
        fig = VGroup(quad, bisectors, dots, names, ticks, lengths)
        fig.quad, fig.bisectors, fig.lengths = quad, bisectors, lengths
        return fig

    def get_figure(self):
        return self.lazy("figure", self.make_figure)

    def arc(self, p1, p2, radius, color):
        m = sp("M")
        a1 = angle_of_vector(sp(p1) - m)
        delta = (angle_of_vector(sp(p2) - m) - a1) % TAU
        return Arc(a1, delta, radius=radius, arc_center=m).set_stroke(color, 4)

    def arc_label(self, p1, p2, tex, color, radius):
        m = sp("M")
        a1 = angle_of_vector(sp(p1) - m)
        delta = (angle_of_vector(sp(p2) - m) - a1) % TAU
        mid = a1 + delta / 2
        return Tex(tex, font_size=26).set_color(color).move_to(m + radius * np.array([np.cos(mid), np.sin(mid), 0]))

    # Sections

    def figure(self):
        self.get_card()
        fig = self.make_figure()
        self.play(ShowCreation(fig.quad), run_time=1.2)
        self.play(FadeIn(fig[2]), FadeIn(fig[3]), FadeIn(fig.lengths), run_time=0.6)
        self.play(ShowCreation(fig.bisectors), FadeIn(fig[4]), run_time=0.9)
        self.set_state("figure", fig)

    def fold(self):
        fig = self.get_figure()

        # Fold triangle ABM over AM, and DCM over DM
        left = self.poly("ABM", LEFT_WING)
        right = self.poly("DCM", RIGHT_WING)
        self.play(FadeIn(left), FadeIn(right), run_time=0.5)
        left_copy, right_copy = left.copy(), right.copy()
        self.play(
            Rotate(left_copy, PI, axis=normalize(sp("M") - sp("A")), about_point=sp("A")),
            Rotate(right_copy, PI, axis=normalize(sp("M") - sp("D")), about_point=sp("D")),
            run_time=1.6,
        )
        marks = VGroup(Dot(sp("K"), radius=0.055), Dot(sp("L"), radius=0.055))
        kl_names = VGroup(self.name("K", DOWN), self.name("L", DOWN))
        folds = VGroup(self.seg("K", "M", LEFT_WING, 3), self.seg("L", "M", RIGHT_WING, 3))
        pieces = VGroup(
            self.length("2", "A", "K", UP, LEFT_WING, 26, 0.06),
            self.length("2", "K", "L", DOWN, CORE, 26, 0.35),
            self.length("4", "L", "D", UP, RIGHT_WING, 26, 0.06),
        )
        self.play(FadeIn(marks), FadeIn(kl_names), ShowCreation(folds), FadeIn(pieces), FadeOut(fig.lengths[2]), run_time=0.8)
        self.note("Folding along the bisectors: KM = BM = CM = LM,\nso triangle KML is isosceles.", wait=1.5)
        self.play(FadeOut(VGroup(left, right, left_copy, right_copy)), run_time=0.4)

        # Its altitude splits KL in half
        core = self.poly("KLM", CORE, 0.3)
        altitude = DashedLine(sp("M"), sp("H"), dash_length=0.07).set_stroke(WHITE, 2.5)
        h_name = self.name("H", DOWN)
        self.play(FadeIn(core), ShowCreation(altitude), FadeIn(h_name), run_time=0.7)
        self.add_step(R"KH = HL = 1 \quad\Rightarrow\quad AH = 3", color=CORE, wait=0.6)
        self.play(FadeOut(core), run_time=0.3)
        self.set_state("fold", VGroup(marks, kl_names, folds, pieces, altitude, h_name))

    def angles(self):
        self.get_figure()
        self.lazy("fold", VGroup)

        # Six angles at M fill the straight angle BMC
        spokes = [("B", "A", R"\alpha", ALPHA), ("A", "K", R"\alpha", ALPHA), ("K", "H", R"\gamma", GAMMA),
                  ("H", "L", R"\gamma", GAMMA), ("L", "D", R"\beta", BETA), ("D", "C", R"\beta", BETA)]
        arcs = VGroup(*[self.arc(p, q, 0.55 + 0.04 * (k % 2), c) for k, (p, q, t, c) in enumerate(spokes)])
        labels = VGroup(*[self.arc_label(p, q, t, c, 0.95) for p, q, t, c in spokes])
        self.play(LaggedStart(*[ShowCreation(a) for a in arcs], lag_ratio=0.15), FadeIn(labels, lag_ratio=0.15), run_time=1.5)
        self.add_step(R"2\alpha + 2\gamma + 2\beta = 180^\circ", wait=0.3)
        self.note("B, M, C are on one line: the six angles make 180°.", wait=1.2)

        # So AMD and AKM are both 90 + gamma
        amd = self.poly("AMD", SIMILAR, 0.15)
        self.play(FadeIn(amd), run_time=0.4)
        self.add_step(R"\angle AMD = \alpha + 2\gamma + \beta = 90^\circ + \gamma = \angle AKM", color=SIMILAR, wait=0.8)
        self.play(FadeOut(VGroup(arcs, labels, amd)), run_time=0.4)

    def similar(self):
        self.get_figure()
        self.clear_steps()

        # AKM, flipped over the bisector of angle KAM and doubled, is AMD
        small = self.poly("AKM", SIMILAR, 0.4)
        big = self.poly("AMD", SIMILAR, 0.15)
        self.play(FadeIn(small), run_time=0.5)
        half = angle_of_vector(sp("M") - sp("A")) / 2
        copy = small.copy()
        self.play(Rotate(copy, PI, axis=np.array([np.cos(half), np.sin(half), 0]), about_point=sp("A")), run_time=1.2)
        self.play(copy.animate.scale(2, about_point=sp("A")), FadeIn(big), run_time=1.2)
        self.play(FadeOut(copy), run_time=0.3)
        line = self.add_step(R"\triangle AKM \sim \triangle AMD:\quad \frac{AK}{AM} = \frac{AM}{AD}", color=SIMILAR, wait=0.5)
        self.replace_step(line, R"AM^2 = AK \cdot AD = 2 \cdot 8 = 16 \ \Rightarrow\ AM = 4", color=SIMILAR, wait=0.5)

        # Pythagoras in AMH
        amh = self.poly("AMH", YELLOW, 0.3)
        four = self.length("4", "A", "M", UL, YELLOW, 28, 0.05)
        self.play(FadeOut(VGroup(small, big)), FadeIn(amh), FadeIn(four), run_time=0.6)
        self.add_step(R"MH = \sqrt{4^2 - 3^2} = \sqrt{7}", color=YELLOW, wait=0.6)
        self.play(FadeOut(VGroup(amh, four)), run_time=0.3)

    def area(self):
        fig = self.get_figure()
        fold = self.lazy("fold", VGroup)
        self.clear_steps()
        self.play(FadeOut(VGroup(fold[0], fold[1], fold[2], fold[3])), FadeIn(fig.lengths[2]), run_time=0.5)

        # M is on both bisectors: sqrt 7 from AB, AD and CD
        def foot(a, b):
            m, a, b = map(np.array, (PTS["M"], PTS[a], PTS[b]))
            d = (b - a) / np.linalg.norm(b - a)
            return tuple(a + ((m - a) @ d) * d)

        heights = VGroup(*[
            DashedLine(sp("M"), sp(foot(a, b)), dash_length=0.07).set_stroke(YELLOW, 3)
            for a, b in [("A", "B"), ("D", "C")]
        ])
        tris = VGroup(self.poly("ABM", PARTS[0]), self.poly("AMD", PARTS[1]), self.poly("DCM", PARTS[2]))
        extensions = VGroup(*[
            DashedLine(sp(a), sp(foot(a, b)) + 0.25 * normalize(sp(foot(a, b)) - sp(a)), dash_length=0.07).set_stroke(GREY_B, 1.5)
            for a, b in [("A", "B"), ("D", "C")]
        ])
        self.play(ShowCreation(extensions), ShowCreation(heights), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(t) for t in tris], lag_ratio=0.3), run_time=1.0)
        self.note("Three triangles, all with height √7 from M.", wait=1.1)
        line = self.add_step(R"S = \tfrac{1}{2}(AB + AD + CD)\cdot\sqrt{7}", wait=0.5)
        self.replace_step(line, R"S = \tfrac{1}{2}(2 + 8 + 4)\sqrt{7}", wait=0.4)
        self.conclude(R"S_{ABCD} = 7\sqrt{7}", font_size=50, wait=1.5)
