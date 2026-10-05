from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/trisected_base_areas.py
#
# M1, M2 trisect BC; CP (P on AB) meets AM1 at I1 and AM2 at I2.
# [BM1I1P] = 11 and [M2I2C] = 6.  Find [AI1I2] and [ABC].
#
# The cevians AM1, AM2 cut ABC into three triangles of equal area S.  Draw the
# line through A parallel to BC and let CP meet it at K, with AK = x d
# (d = BC / 3).  The hourglasses at I2, I1 and P give
#   I2M2 / AM2 = 1/(x+1),  AI1 / AM1 = x/(x+2),  AP / AB = x/(x+3),
# so S/(x+1) = 6 and S (1 - x^2 / ((x+2)(x+3))) = 11, i.e. 19x^2 + 11x - 30 = 0
# and x = 1.  Then S = 12, [AI1I2] = 12 * 1/3 * 1/2 = 2 and [ABC] = 3S = 36.
# Checked with coordinates.  Area ratios survive any affine map, so the figure
# is drawn with a friendlier shape than the one with these exact areas.

A0, B0, C0 = np.array([-0.99, 2.0, 0]), np.array([-3.52, -2.2, 0]), np.array([3.52, -2.2, 0])

AREA_11 = "#FF9F43"
AREA_6 = "#5BD98A"
TARGET = "#FF6BD6"
PARTS = ["#3FA7FF", "#7F8CFF", "#4FD1C5"]
BOWTIE = YELLOW
AUX = "#C39BFF"


def meet(p1, p2, p3, p4):
    d1, d2 = p2 - p1, p4 - p3
    t = np.linalg.solve(np.array([d1[:2], -d2[:2]]).T, (p3 - p1)[:2])[0]
    return p1 + t * d1


def base_points():
    d = (C0 - B0) / 3
    pts = dict(A=A0, B=B0, C=C0, M_1=B0 + d, M_2=B0 + 2 * d, K=A0 - d)
    pts["P"] = meet(C0, pts["K"], A0, B0)
    pts["I_1"] = meet(C0, pts["K"], A0, pts["M_1"])
    pts["I_2"] = meet(C0, pts["K"], A0, pts["M_2"])
    return pts


class TrisectedBaseAreas(MockTestShort):
    """Areas cut from a triangle by a cevian through a trisected base."""

    test = ""
    step_buff = 0.3
    step_font_size = 34

    problem_tex = (
        R"M_1, M_2 \text{ trisect } BC,\ \ P \in AB.\\"
        R"CP \text{ meets } AM_1, AM_2 \text{ at } I_1, I_2.\\"
        R"S_{BM_1I_1P} = 11,\ \ S_{M_2I_2C} = 6.\\"
        R"\text{Find } S_{AI_1I_2} \text{ and } S_{ABC}."
    )

    sections = ["pose", "equal_parts", "parallel", "equations", "answer", "outro"]

    # The figure lives in one group so it can move; points are read off it

    def make_figure(self):
        pts = base_points()
        dots = {n: Dot(p, radius=0.06).set_fill(WHITE) for n, p in pts.items()}
        sides = {
            "A": UP, "B": DL, "C": DR, "M_1": DOWN, "M_2": DOWN, "P": LEFT, "I_1": DL, "I_2": DR, "K": UL,
        }
        names = {n: Tex(n, font_size=32).next_to(dots[n], sides[n], buff=0.08) for n in pts}
        tri = Polygon(pts["A"], pts["B"], pts["C"]).set_stroke(WHITE, 3)
        cevians = VGroup(Line(pts["A"], pts["M_1"]), Line(pts["A"], pts["M_2"])).set_stroke(WHITE, 2.5)
        cp = Line(pts["C"], pts["P"]).set_stroke(WHITE, 2.5)
        regions = VGroup(
            Polygon(pts["B"], pts["M_1"], pts["I_1"], pts["P"]).set_stroke(width=0).set_fill(AREA_11, 0.4),
            Polygon(pts["M_2"], pts["I_2"], pts["C"]).set_stroke(width=0).set_fill(AREA_6, 0.4),
            Polygon(pts["A"], pts["I_1"], pts["I_2"]).set_stroke(width=0).set_fill(TARGET, 0.4),
        )
        values = VGroup(
            Tex("11", font_size=40).move_to(regions[0].get_center_of_mass()),
            Tex("6", font_size=40).move_to(regions[1].get_center_of_mass()),
            Tex("?", font_size=40).move_to(regions[2].get_center_of_mass() + 0.05 * UP),
        )
        fig = VGroup(regions, tri, cevians, cp, *[dots[n] for n in pts if n != "K"],
                     *[names[n] for n in pts if n != "K"], values)
        fig.dots, fig.names, fig.regions, fig.values = dots, names, regions, values
        fig.tri, fig.cevians, fig.cp = tri, cevians, cp
        # K is off the figure until the parallel line is drawn; keep it moving with the rest
        fig.hidden = VGroup(dots["K"], names["K"])
        fig.add(fig.hidden.set_opacity(0))
        return fig

    def get_figure(self):
        def build():
            fig = self.make_figure()
            self.settle(fig, animate=False)
            self.add(fig)
            return fig
        return self.lazy("figure", build)

    def settle(self, fig, animate=True):
        """Move the figure up under the card, leaving the lower half for the working."""
        card = self.get_card()
        target = fig.copy().scale(0.76)
        target.next_to(card, DOWN, buff=0.35).set_x(0)
        if animate:
            self.play(fig.animate.scale(0.76).move_to(target), run_time=1.1)
        else:
            fig.scale(0.76).move_to(target)
        self.steps_top_y = fig.tri.get_bottom()[1] - 0.75

    def at(self, name):
        return self.get_figure().dots[name].get_center()

    def poly(self, names, color, opacity=0.35):
        return Polygon(*[self.at(n) for n in names]).set_stroke(color, 2.5).set_fill(color, opacity)

    # Sections

    def pose(self):
        # The opening frame: card at the top, the whole figure in the middle
        card = self.make_card()
        fig = self.make_figure()
        self.play(FadeIn(card, 0.2 * DOWN), ShowCreation(fig.tri), run_time=0.9)
        self.play(ShowCreation(fig.cevians), ShowCreation(fig.cp), run_time=0.8)
        self.play(
            FadeIn(fig.regions), FadeIn(fig.values, scale=0.7),
            *[FadeIn(m) for m in fig if m not in (fig.regions, fig.tri, fig.cevians, fig.cp, fig.values, fig.hidden)],
            run_time=0.8,
        )
        self.add(fig)
        self.set_state("card", card)
        self.wait(2.6)
        self.settle(fig)
        self.set_state("figure", fig)

    def equal_parts(self):
        fig = self.get_figure()

        # Equal bases, same height: three equal areas
        marks = VGroup(*[
            Line(self.at(a), self.at(b)).set_stroke(PARTS[k], 6)
            for k, (a, b) in enumerate([("B", "M_1"), ("M_1", "M_2"), ("M_2", "C")])
        ])
        ds = VGroup(*[Tex("d", font_size=30).set_color(PARTS[k]).next_to(m, DOWN, buff=0.28) for k, m in enumerate(marks)])
        self.play(ShowCreation(marks, lag_ratio=0.3), FadeIn(ds, lag_ratio=0.3), run_time=0.9)
        thirds = VGroup(
            self.poly(["A", "B", "M_1"], PARTS[0]), self.poly(["A", "M_1", "M_2"], PARTS[1]), self.poly(["A", "M_2", "C"], PARTS[2]),
        )
        s_labels = VGroup(*[Tex("S", font_size=36).move_to(t.get_center_of_mass() + 0.55 * DOWN) for t in thirds])
        self.play(FadeOut(fig.values), LaggedStart(*[FadeIn(t) for t in thirds], lag_ratio=0.3), FadeIn(s_labels, lag_ratio=0.3), run_time=1.1)
        self.add_step(R"S_{ABM_1} = S_{AM_1M_2} = S_{AM_2C} = S", wait=0.3)
        self.note("Equal bases, same height: equal areas.", wait=1.0)
        self.play(FadeOut(VGroup(thirds, s_labels, marks)), FadeIn(fig.values), run_time=0.6)
        self.set_state("ds", ds)

    def parallel(self):
        fig = self.get_figure()
        self.clear_steps()

        # A line through A parallel to BC; CP extended meets it at K
        a = self.at("A")
        rail = DashedLine(a + (self.at("B") - self.at("C")) * 0.42, a + (self.at("C") - self.at("B")) * 0.3,
                          dash_length=0.1).set_stroke(AUX, 2.5)
        extend = DashedLine(self.at("P"), self.at("K"), dash_length=0.08).set_stroke(AUX, 2.5)
        fig.hidden.set_opacity(1)
        self.play(ShowCreation(rail), run_time=0.7)
        self.play(ShowCreation(extend), FadeIn(fig.hidden), run_time=0.7)
        xd = Tex("xd", font_size=32).set_color(AUX).next_to(Line(self.at("K"), a), UP, buff=0.1)
        ak = Line(self.at("K"), a).set_stroke(AUX, 6)
        self.play(ShowCreation(ak), FadeIn(xd), run_time=0.6)
        self.note("Draw AK parallel to BC: three hourglasses\nof similar triangles appear.", wait=1.2)

        # The three hourglasses, one at a time
        pairs = [
            (["K", "A", "I_2"], ["C", "M_2", "I_2"], R"\frac{I_2M_2}{AM_2} = \frac{d}{xd + d} = \frac{1}{x+1}"),
            (["K", "A", "I_1"], ["C", "M_1", "I_1"], R"\frac{AI_1}{AM_1} = \frac{xd}{xd + 2d} = \frac{x}{x+2}"),
            (["K", "A", "P"], ["C", "B", "P"], R"\frac{AP}{AB} = \frac{xd}{xd + 3d} = \frac{x}{x+3}"),
        ]
        for top, bottom, tex in pairs:
            glass = VGroup(self.poly(top, BOWTIE, 0.3), self.poly(bottom, BOWTIE, 0.3))
            self.play(FadeIn(glass), run_time=0.5)
            self.add_step(tex, font_size=32, wait=0.5)
            self.play(FadeOut(glass), run_time=0.3)
        self.set_state("aux", VGroup(rail, extend, ak, xd))

    def equations(self):
        fig = self.get_figure()
        aux = self.lazy("aux", VGroup)
        self.play(FadeOut(aux), fig.hidden.animate.set_opacity(0), FadeOut(self.lazy("ds", VGroup)), run_time=0.5)
        self.clear_steps()

        # The 6: triangle M2I2C sits inside AM2C, cut at I2
        whole = self.poly(["A", "M_2", "C"], AREA_6, 0.12)
        self.play(FadeIn(whole), Indicate(fig.values[1], color=AREA_6), run_time=0.7)
        self.add_step(R"\frac{S}{x+1} = 6 \ \Rightarrow\ S = 6(x+1)", color=AREA_6, wait=0.4)
        self.play(FadeOut(whole), run_time=0.3)

        # The 11: triangle ABM1 minus the small triangle API1
        outer = self.poly(["A", "B", "M_1"], AREA_11, 0.12)
        inner = self.poly(["A", "P", "I_1"], TARGET, 0.45)
        self.play(FadeIn(outer), run_time=0.4)
        self.play(FadeIn(inner), Indicate(fig.values[0], color=AREA_11), run_time=0.6)
        rule = self.add_step(
            R"S\left(1 - \frac{x}{x+3}\cdot\frac{x}{x+2}\right) = 11", color=AREA_11, wait=0.6,
        )
        self.play(FadeOut(VGroup(outer, inner)), run_time=0.3)
        self.note("Substitute S = 6(x + 1) and clear fractions.", wait=0.9)
        line = self.replace_step(rule, R"19x^2 + 11x - 30 = 0", wait=0.5)
        self.replace_step(line, R"(x - 1)(19x + 30) = 0 \ \Rightarrow\ x = 1", color=YELLOW, wait=0.8)

    def answer(self):
        fig = self.get_figure()
        self.clear_steps()

        # x = 1: S = 12, and the pink triangle takes a third and a half
        self.add_step(R"S = 12,\quad \frac{AI_1}{AM_1} = \frac{1}{3},\quad \frac{AI_2}{AM_2} = \frac{1}{2}", wait=0.4)
        middle = self.poly(["A", "M_1", "M_2"], PARTS[1], 0.18)
        self.play(FadeIn(middle), run_time=0.4)
        line = self.add_step(R"S_{AI_1I_2} = 12 \cdot \frac{1}{3} \cdot \frac{1}{2} = 2", color=TARGET, wait=0.3)
        two = Tex("2", font_size=40).move_to(fig.values[2])
        self.play(FadeOut(middle), Transform(fig.values[2], two.set_color(TARGET)), Flash(fig.values[2], color=TARGET), run_time=0.8)

        # The whole triangle is three S
        thirds = VGroup(
            self.poly(["A", "B", "M_1"], PARTS[0], 0.22), self.poly(["A", "M_1", "M_2"], PARTS[1], 0.22),
            self.poly(["A", "M_2", "C"], PARTS[2], 0.22),
        )
        self.play(LaggedStart(*[FadeIn(t) for t in thirds], lag_ratio=0.3), run_time=0.8)
        self.conclude(R"S_{AI_1I_2} = 2,\qquad S_{ABC} = 3S = 36", font_size=40, wait=1.5)
