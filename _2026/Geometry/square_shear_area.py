from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/square_shear_area.py
#
# Square ABCD, E outside with angle BEC = 90 and BE = sqrt 5.  Find [ABE].
#
# Method 1.  Turn triangle CEB about B by 90 so that C lands on A (in this
# picture that is clockwise): E goes to K, BK = BE = sqrt 5 and BK is
# perpendicular to BE.  A is AB cos(theta) = BE from line BE, the same as K,
# so AK is parallel to BE and sliding A to K keeps the area:
#   [ABE] = [KBE] = 1/2 * sqrt 5 * sqrt 5 = 5/2.
# Method 2.  With H the foot from E on BC, the height of ABE on base AB is BH,
# so [ABE] = 1/2 AB * BH = 1/2 BC * BH = 1/2 BE^2 = 5/2 (leg rule in BEC).
# Drawn with side 3 (so EC = 2); the answer does not depend on the side.
# Method 3.  Turn CBE a quarter turn about the square's centre: C -> B, B -> A,
# E -> K.  Then AK = BE = sqrt 5, the right angle sits at K, and K lies on line
# EB, so AK is the height from A: [ABE] = 1/2 * BE * AK = 5/2.
# Checked: shoelace [ABE] = 2.5, AK parallel to BE, BC * BH = 5, K3 on line EB.

SIDE = 3.0
BE = np.sqrt(5)
COS_T = BE / SIDE
SIN_T = np.sqrt(1 - COS_T ** 2)

PTS = {"D": (0, 0), "C": (SIDE, 0), "B": (SIDE, SIDE), "A": (0, SIDE)}
PTS["E"] = (SIDE + BE * SIN_T, SIDE - BE * COS_T)
_e = np.array(PTS["E"]) - np.array(PTS["B"])
PTS["K"] = tuple(np.array(PTS["B"]) + np.array([_e[1], -_e[0]]))      # quarter turn, C -> A
PTS["H"] = (SIDE, PTS["E"][1])
_c = np.array([SIDE / 2, SIDE / 2])
_q = np.array(PTS["E"]) - _c
PTS["K3"] = tuple(_c + np.array([-_q[1], _q[0]]))                     # CBE turned about the centre onto BAK3

SCALE = 1.15
CENTER_XY = np.array([2.35, 1.5])

SHADE = "#58C4DD"
TURN = "#5BD98A"
ISO = "#FF9F43"
PARALLEL = "#C39BFF"
PROJ = "#FF6BD6"


def plane(p):
    x, y = PTS[p] if isinstance(p, str) else p
    return SCALE * np.array([x - CENTER_XY[0], y - CENTER_XY[1], 0])


class SquareShearArea(MockTestShort):
    """Area of triangle ABE from a square and a right angle at E."""

    test = ""
    step_buff = 0.3
    step_font_size = 36

    problem_tex = (
        R"ABCD \text{ is a square},\ \angle BEC = 90^\circ,\\"
        R"BE = \sqrt{5}\ \text{m}.\ \text{Find the shaded area.}"
    )

    sections = ["pose", "rotate", "parallel", "shear", "method_two", "method_three", "outro"]

    # The figure is built at the centre, then moved up; read points off it

    def make_figure(self):
        pts = {k: plane(k) for k in PTS}
        square = Polygon(*[pts[k] for k in "ABCD"]).set_stroke(WHITE, 3.5)
        sides = VGroup(Line(pts["B"], pts["E"]), Line(pts["E"], pts["C"])).set_stroke(WHITE, 3.5)
        shade = Polygon(pts["A"], pts["B"], pts["E"]).set_stroke(SHADE, 3).set_fill(SHADE, 0.4)
        ae = Line(pts["A"], pts["E"]).set_stroke(WHITE, 3)
        corner = self.corner_at(pts["E"], pts["B"], pts["C"])
        names = VGroup(*[
            Tex(k, font_size=34).next_to(pts[k], d, buff=0.1)
            for k, d in [("A", UL), ("B", UR), ("C", DR), ("D", DL), ("E", RIGHT)]
        ])
        be = Tex(R"\sqrt{5}", font_size=30).set_color(SHADE).move_to((pts["B"] + pts["E"]) / 2 + 0.35 * UR)
        anchors = VGroup(*[Dot(p, radius=0.001).set_opacity(0) for p in pts.values()])
        fig = VGroup(shade, square, sides, ae, corner, names, be, anchors)
        fig.keys = list(pts)
        fig.shade, fig.be_label, fig.anchors = shade, be, anchors
        return fig

    def corner_at(self, v, p1, p2, size=0.2, color=WHITE):
        d1, d2 = normalize(p1 - v), normalize(p2 - v)
        return VMobject().set_points_as_corners([v + size * d1, v + size * (d1 + d2), v + size * d2]).set_stroke(color, 2.5)

    def get_figure(self):
        def build():
            fig = self.make_figure()
            self.settle(fig, animate=False)
            self.add(fig)
            return fig
        return self.lazy("figure", build)

    def settle(self, fig, animate=True):
        card = self.get_card()
        target = fig.copy().next_to(card, DOWN, buff=0.55).set_x(0)
        if animate:
            self.play(fig.animate.move_to(target), run_time=1.0)
        else:
            fig.move_to(target)
        self.steps_top_y = fig.get_bottom()[1] - 0.6

    def at(self, key):
        fig = self.get_figure()
        return fig.anchors[fig.keys.index(key)].get_center()

    def poly(self, keys, color, opacity=0.35):
        return Polygon(*[self.at(k) for k in keys]).set_stroke(color, 3).set_fill(color, opacity)

    def seg(self, a, b, color, width=4, dashed=False):
        pa = self.at(a) if isinstance(a, str) else a
        pb = self.at(b) if isinstance(b, str) else b
        line = DashedLine(pa, pb, dash_length=0.08) if dashed else Line(pa, pb)
        return line.set_stroke(color, width)

    def header(self, text, color):
        """A method title that takes its own line, so what follows stacks under it."""
        title = Text(text, font_size=30, weight=BOLD).set_color(color)
        self.place_step(title)
        self.steps().add(title)
        self.play(FadeIn(title, 0.15 * UP), run_time=0.4)
        return title

    # Sections

    def pose(self):
        card = self.make_card()
        fig = self.make_figure()                       # centred on the screen
        self.play(FadeIn(card, 0.2 * DOWN), ShowCreation(fig[1]), run_time=1.0)
        self.play(ShowCreation(fig[2]), FadeIn(fig.shade), ShowCreation(fig[3]), run_time=0.9)
        self.play(FadeIn(fig[4]), FadeIn(fig[5]), FadeIn(fig.be_label), run_time=0.6)
        self.add(fig)
        self.set_state("card", card)
        self.wait(2.4)
        self.settle(fig)
        self.set_state("figure", fig)

    def rotate(self):
        self.get_figure()
        self.header("Method 1: rotate and shear", TURN)

        # Turn triangle CEB about B until C lands on A
        tri = self.poly("CEB", TURN, 0.4)
        self.play(FadeIn(tri), run_time=0.4)
        self.play(Rotate(tri, -PI / 2, about_point=self.at("B")), run_time=1.5)
        k = VGroup(Dot(self.at("K"), radius=0.06).set_fill(TURN),
                   Tex("K", font_size=32).set_color(TURN).next_to(self.at("K"), DOWN, buff=0.1))
        self.play(FadeIn(k), run_time=0.4)
        self.note("A quarter turn about B sends C to A and E to K.", wait=1.0)

        # BEK is a right isosceles triangle
        bk = self.seg("B", "K", ISO, 4)
        iso = self.poly("EBK", ISO, 0.25)
        mark = self.corner_at(self.at("B"), self.at("E"), self.at("K"), 0.22, ISO)
        bk_label = Tex(R"\sqrt{5}", font_size=30).set_color(ISO).move_to((self.at("B") + self.at("K")) / 2 + 0.3 * UP + 0.1 * LEFT)
        self.play(FadeOut(tri), ShowCreation(bk), FadeIn(iso), ShowCreation(mark), FadeIn(bk_label), run_time=0.9)
        self.add_step(R"BK = BE = \sqrt{5},\quad \angle EBK = 90^\circ", color=ISO, wait=0.6)
        self.set_state("turn", VGroup(k, bk, iso, mark, bk_label))

    def parallel(self):
        self.get_figure()
        self.lazy("turn", VGroup)

        # A and K are both sqrt 5 from the line BE
        b, e = self.at("B"), self.at("E")
        d = normalize(e - b)
        line_be = DashedLine(b - 1.6 * d, e + 0.6 * d, dash_length=0.1).set_stroke(PARALLEL, 2.5)
        a, k = self.at("A"), self.at("K")
        line_ak = DashedLine(a - 0.4 * (k - a), k + 1.2 * (k - a), dash_length=0.1).set_stroke(PARALLEL, 2.5)
        foot_a = b + ((a - b) @ d) * d
        drop = DashedLine(a, foot_a, dash_length=0.07).set_stroke(YELLOW, 3)
        self.play(ShowCreation(line_be), run_time=0.6)
        self.play(ShowCreation(drop), run_time=0.6)
        self.add_step(R"d(A, BE) = AB\cos\theta = BE = \sqrt{5} = BK", font_size=34, wait=0.4)
        self.note("A is as far from line BE as K: AK is parallel to BE.", wait=1.2)
        self.play(ShowCreation(line_ak), FadeOut(drop), run_time=0.7)
        self.set_state("lines", VGroup(line_be, line_ak))

    def shear(self):
        fig = self.get_figure()
        turn = self.lazy("turn", VGroup)
        lines = self.lazy("lines", VGroup)

        # Slide A along the parallel down to K: same base, same height
        t = ValueTracker(0)
        a, k = self.at("A"), self.at("K")
        moving = always_redraw(lambda: Polygon(
            interpolate(a, k, t.get_value()), self.at("B"), self.at("E"),
        ).set_stroke(SHADE, 3).set_fill(SHADE, 0.5))
        self.add(moving)
        self.play(fig.shade.animate.set_fill(opacity=0.1), run_time=0.3)
        self.play(t.animate.set_value(1), run_time=2.0)
        self.note("Same base BE, same height: the area does not change.", wait=1.1)
        steps = self.steps()
        if len(steps) > 1:
            self.play(FadeOut(VGroup(*steps[1:])), run_time=0.3)
            steps.set_submobjects([steps[0]])
        self.add_step(R"S_{ABE} = S_{KBE} = \tfrac{1}{2}\cdot\sqrt{5}\cdot\sqrt{5} = \tfrac{5}{2}", color=SHADE, font_size=40, wait=1.0)
        self.play(t.animate.set_value(0), run_time=1.0)
        moving.clear_updaters()
        self.play(FadeOut(VGroup(moving, turn, lines)), fig.shade.animate.set_fill(opacity=0.4), run_time=0.5)

    def method_two(self):
        self.get_figure()
        self.clear_steps()
        self.header("Method 2: the leg rule", PROJ)

        # The height of ABE on base AB is BH
        eh = self.seg("E", "H", PROJ, 3, dashed=True)
        h = VGroup(Dot(self.at("H"), radius=0.06).set_fill(PROJ),
                   Tex("H", font_size=30).set_color(PROJ).next_to(self.at("H"), LEFT, buff=0.1))
        bh = self.seg("B", "H", PROJ, 7)
        mark = self.corner_at(self.at("H"), self.at("E"), self.at("B"), 0.17, PROJ)
        self.play(ShowCreation(eh), FadeIn(h), ShowCreation(mark), run_time=0.7)
        self.play(ShowCreation(bh), run_time=0.5)
        self.note("With base AB, the height of triangle ABE is BH.", wait=1.1)
        line = self.add_step(R"S = \tfrac{1}{2}\,AB\cdot BH = \tfrac{1}{2}\,BC\cdot BH", wait=0.4)
        bec = self.poly("BEC", PROJ, 0.2)
        self.play(FadeIn(bec), run_time=0.4)
        self.note("Right triangle BEC: BE² = BC · BH (leg rule).", wait=1.1)
        self.replace_step(line, R"S = \tfrac{1}{2}\,BE^2 = \tfrac{1}{2}(\sqrt{5})^2", wait=0.4)
        self.play(FadeOut(VGroup(eh, h, bh, mark, bec)), run_time=0.5)
        self.add_step(R"S_{ABE} = \tfrac{5}{2}", color=PROJ, font_size=40, wait=0.8)

    def method_three(self):
        fig = self.get_figure()
        self.clear_steps()
        self.header("Method 3: copy the triangle onto AB", ISO)

        # Turn CBE about the centre of the square: C -> B, B -> A, E -> K
        center = (self.at("A") + self.at("C")) / 2
        tri = self.poly("CBE", ISO, 0.4)
        self.play(FadeIn(tri), run_time=0.4)
        self.play(Rotate(tri, PI / 2, about_point=center), run_time=1.6)
        k = VGroup(Dot(self.at("K3"), radius=0.06).set_fill(ISO),
                   Tex("K", font_size=32).set_color(ISO).next_to(self.at("K3"), UP, buff=0.1))
        self.play(FadeIn(k), run_time=0.4)
        self.note("A copy of CBE on side AB: AK = BE = √5,\nand the right angle is at K.", wait=1.3)

        # K sits on line EB, so AK is the height from A
        ext = self.seg("B", "K3", ISO, 3, dashed=True)
        ak = self.seg("A", "K3", YELLOW, 6)
        mark = self.corner_at(self.at("K3"), self.at("A"), self.at("B"), 0.2, YELLOW)
        ak_label = Tex(R"\sqrt{5}", font_size=30).set_color(YELLOW).next_to((self.at("A") + self.at("K3")) / 2, UL, buff=0.08)
        self.play(ShowCreation(ext), run_time=0.6)
        self.play(ShowCreation(ak), ShowCreation(mark), FadeIn(ak_label), run_time=0.8)
        self.add_step(R"AK \perp BE \ \Rightarrow\ S = \tfrac{1}{2}\,BE\cdot AK", wait=0.6)
        self.play(Indicate(fig.shade, color=SHADE), run_time=0.7)
        self.conclude(R"S_{ABE} = \tfrac{1}{2}\cdot\sqrt{5}\cdot\sqrt{5} = \tfrac{5}{2}\ \text{m}^2", font_size=44, wait=1.4)
