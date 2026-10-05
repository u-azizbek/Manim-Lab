from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/pentagon_distances.py
#
# Regular pentagon ABCDE (EA at the bottom).  P is 5 from AB, 3 from BC and
# 4 from CD; find its distance x to EA.
#
# Reflect P in the axis through B to P'.  P'P is perpendicular to the axis,
# so parallel to ED and hence to the diagonal AC.  P' is 3 from AB and 4 from
# EA, so along P'P the distance to AB grows by 2 and the distance to EA by
# x - 4.  Along AC (from A, on both lines, to C) they grow in the same ratio:
#   (x - 4)/2 = d(C, EA)/d(C, AB) = [AEC]/[ABC]        (equal bases EA = AB)
#            = [BDE]/[ADE]                              (rotations of the pentagon)
#            = BD/AE = phi                              (trapezoid ABDE, BD || AE)
# so x = 4 + 2 phi = 5 + sqrt 5.
#
# The figure is the real one: each distance is r - n.P for the side's outward
# normal n and the inradius r, so P and r come from a 3 x 3 linear system.

PHI = (1 + np.sqrt(5)) / 2
ANGLES = {"A": -54, "B": 18, "C": 90, "D": 162, "E": 234}
NORMALS = {"EA": -90, "AB": -18, "BC": 54, "CD": 126, "DE": 198}
GIVEN = {"AB": 5, "BC": 3, "CD": 4}


def unit(deg):
    return np.array([np.cos(deg * DEGREES), np.sin(deg * DEGREES)])


def solve_figure():
    rows = [[1, *(-unit(NORMALS[side]))] for side in GIVEN]
    r, px, py = np.linalg.solve(np.array(rows), np.array(list(GIVEN.values()), dtype=float))
    p = np.array([px, py])
    circum = r / np.cos(36 * DEGREES)
    verts = {k: circum * unit(a) for k, a in ANGLES.items()}
    x = r - unit(NORMALS["EA"]) @ p
    return verts, p, r, x


VERTS, P_PT, INRADIUS, X_VALUE = solve_figure()          # X_VALUE = 5 + sqrt 5
SCALE = 0.46

D_COLORS = {"AB": "#58C4DD", "BC": "#5BD98A", "CD": "#C39BFF", "EA": YELLOW}
MIRROR = "#FF9F43"
AXIS = "#E6EDF5"
TRI_BIG = "#FF6BD6"
TRI_SMALL = "#4FD1C5"


def to_screen(q):
    return np.array([q[0] * SCALE, q[1] * SCALE - 0.25, 0])


class PentagonDistances(MockTestShort):
    """Distance from a point to a pentagon's side, by reflection and phi."""

    test = ""
    step_buff = 0.3
    step_font_size = 34

    problem_tex = (
        R"\text{Regular pentagon } ABCDE.\\"
        R"PH_2 = 5,\ \ PH_3 = 3,\ \ PH_4 = 4.\\"
        R"\text{Find } x = PH_1."
    )

    sections = ["pose", "reflect", "changes", "diagonal", "golden", "general", "outro"]

    def make_figure(self):
        pts = {k: to_screen(v) for k, v in VERTS.items()}
        pts["P"] = to_screen(P_PT)
        for k, side in [("H_1", "EA"), ("H_2", "AB"), ("H_3", "BC"), ("H_4", "CD")]:
            d = X_VALUE if side == "EA" else GIVEN[side]
            pts[k] = to_screen(P_PT + d * unit(NORMALS[side]))
        pentagon = Polygon(*[pts[k] for k in "ABCDE"]).set_stroke(WHITE, 3.5)
        perps = VGroup(*[
            Line(pts["P"], pts[h]).set_stroke(D_COLORS[side], 4)
            for h, side in [("H_1", "EA"), ("H_2", "AB"), ("H_3", "BC"), ("H_4", "CD")]
        ])
        marks = VGroup(*[self.corner(pts[h], pts["P"], side) for h, side in
                         [("H_1", "EA"), ("H_2", "AB"), ("H_3", "BC"), ("H_4", "CD")]])
        values = VGroup(*[
            Tex(t, font_size=34).set_color(D_COLORS[side]).move_to(
                (pts["P"] + pts[h]) / 2 + 0.28 * rotate_vector(normalize(pts[h] - pts["P"]), PI / 2))
            for t, h, side in [("x", "H_1", "EA"), ("5", "H_2", "AB"), ("3", "H_3", "BC"), ("4", "H_4", "CD")]
        ])
        dots = {k: Dot(p, radius=0.055).set_fill(WHITE) for k, p in pts.items()}
        center = to_screen((0, 0))
        names = VGroup(*[
            Tex(k, font_size=30).move_to(p + 0.3 * normalize(p - center)) for k, p in pts.items() if k in "ABCDE"
        ])
        p_name = Tex("P", font_size=30).next_to(pts["P"], DL, buff=0.06)
        fig = VGroup(pentagon, perps, marks, values, dots["P"], names, p_name)
        fig.pts_dots = dots
        fig.anchor = VGroup(*[Dot(p, radius=0.001).set_opacity(0) for p in pts.values()])
        fig.anchor_keys = list(pts)
        fig.add(fig.anchor)
        fig.pentagon, fig.perps, fig.values = pentagon, perps, values
        return fig

    def corner(self, foot, p, side, size=0.16):
        along = rotate_vector(unit(NORMALS[side]).tolist() + [0], PI / 2)[:3]
        back = normalize(p - foot)
        return VMobject().set_points_as_corners([
            foot + size * back, foot + size * (back + along), foot + size * along,
        ]).set_stroke(WHITE, 2)

    def get_figure(self):
        def build():
            fig = self.make_figure()
            self.settle(fig, animate=False)
            self.add(fig)
            return fig
        return self.lazy("figure", build)

    def settle(self, fig, animate=True):
        card = self.get_card()
        target = fig.copy().scale(0.8).next_to(card, DOWN, buff=0.45).set_x(0)
        if animate:
            self.play(fig.animate.scale(0.8).move_to(target), run_time=1.0)
        else:
            fig.scale(0.8).move_to(target)
        self.steps_top_y = fig.pentagon.get_bottom()[1] - 0.8

    def at(self, key):
        fig = self.get_figure()
        return fig.anchor[fig.anchor_keys.index(key)].get_center()

    def plane_to_now(self, q):
        """Plane coordinates to the figure's current screen position."""
        a, b = self.at("A"), self.at("B")
        s0, s1 = to_screen(VERTS["A"]), to_screen(VERTS["B"])
        k = get_norm(b - a) / get_norm(s1 - s0)
        return a + k * (to_screen(q) - s0)

    # Sections

    def pose(self):
        card = self.make_card()
        fig = self.make_figure()
        self.play(FadeIn(card, 0.2 * DOWN), ShowCreation(fig.pentagon), run_time=1.0)
        self.play(
            LaggedStart(*[ShowCreation(l) for l in fig.perps], lag_ratio=0.2),
            *[FadeIn(m) for m in fig if m not in (fig.pentagon, fig.perps)],
            run_time=1.2,
        )
        self.add(fig)
        self.set_state("card", card)
        self.wait(2.6)
        self.settle(fig)
        self.set_state("figure", fig)

    def reflect(self):
        fig = self.get_figure()
        o = self.plane_to_now((0, 0))
        b = self.at("B")
        axis_dir = normalize(b - o)
        axis = DashedLine(o - 1.25 * (b - o), b + 0.25 * (b - o), dash_length=0.1).set_stroke(AXIS, 2)
        axis_name = Tex(R"\mathcal{L}", font_size=32).next_to(axis.get_end(), UR, buff=0.05)
        self.play(ShowCreation(axis), FadeIn(axis_name), run_time=0.7)

        # Flip P, with its 3 and its 4, across the axis
        piece = VGroup(fig.pts_dots["P"].copy(), fig.perps[2].copy(), fig.perps[3].copy()).set_color(MIRROR)
        self.play(Rotate(piece, PI, axis=axis_dir, about_point=o), run_time=1.4)
        p_prime = self.plane_to_now(2 * (P_PT @ unit(18)) * unit(18) - P_PT)
        prime_name = Tex("P'", font_size=30).set_color(MIRROR).next_to(p_prime, DOWN, buff=0.08)
        link = Line(p_prime, self.at("P")).set_stroke(MIRROR, 4)
        self.play(FadeIn(prime_name), ShowCreation(link), run_time=0.6)

        # P'P, ED and AC all run the same way
        ed = Line(self.at("E"), self.at("D")).set_stroke(MIRROR, 6)
        ac = DashedLine(self.at("A"), self.at("C"), dash_length=0.1).set_stroke(MIRROR, 3)
        self.play(ShowCreation(ed), ShowCreation(ac), run_time=0.8)
        self.add_step(R"P'P \perp \mathcal{L}\ \Rightarrow\ P'P \parallel ED \parallel AC", color=MIRROR, wait=0.3)
        self.note("In a regular pentagon, AC is parallel to ED.", wait=1.0)
        self.play(FadeOut(ed), run_time=0.3)
        self.set_state("mirror", VGroup(axis, axis_name, piece, prime_name, link, ac))

    def changes(self):
        fig = self.get_figure()
        mirror = self.lazy("mirror", VGroup)
        piece = mirror[2]
        # The mirrored 3 now reaches AB, the mirrored 4 reaches EA
        tags = VGroup(
            Tex("3", font_size=30).set_color(D_COLORS["BC"]).next_to(piece[1], RIGHT, buff=0.05),
            Tex("4", font_size=30).set_color(D_COLORS["CD"]).next_to(piece[2], RIGHT, buff=0.05),
        )
        self.play(FadeIn(tags), Indicate(fig.values[1], color=D_COLORS["AB"]), Indicate(fig.values[0], color=YELLOW), run_time=0.9)
        self.note("P' is 3 from AB and 4 from EA; P is 5 and x.", wait=1.3)
        self.add_step(R"\text{from } P' \text{ to } P:\ \ \Delta d_{AB} = 5 - 3 = 2,\ \ \Delta d_{EA} = x - 4", wait=0.8)
        self.play(FadeOut(tags), run_time=0.3)

    def diagonal(self):
        fig = self.get_figure()
        mirror = self.lazy("mirror", VGroup)
        self.play(FadeOut(mirror), FadeOut(fig.perps), FadeOut(fig.values), run_time=0.5)

        # The same growth along AC: from A (on both lines) up to C
        a, c = self.at("A"), self.at("C")
        line_ab = DashedLine(a + 0.4 * (a - self.at("B")), self.at("B") + 1.7 * (self.at("B") - a), dash_length=0.1).set_stroke(D_COLORS["AB"], 2)
        foot_ea = self.plane_to_now(VERTS["C"] + (INRADIUS + np.linalg.norm(VERTS["C"])) * unit(-90))
        n_ab = unit(-18)
        d_c_ab = INRADIUS - n_ab @ VERTS["C"]
        foot_ab = self.plane_to_now(VERTS["C"] + d_c_ab * n_ab)
        h_ea = Line(c, foot_ea).set_stroke(D_COLORS["EA"], 5)
        h_ab = Line(c, foot_ab).set_stroke(D_COLORS["AB"], 5)
        ac = Arrow(a, c, buff=0, thickness=4).set_color(MIRROR)
        self.play(GrowArrow(ac), run_time=0.7)
        self.play(ShowCreation(line_ab), ShowCreation(h_ea), ShowCreation(h_ab), run_time=0.9)
        self.add_step(R"\frac{x - 4}{2} = \frac{d(C, EA)}{d(C, AB)}", wait=0.4)
        self.note("A is on both lines, so from A to C the\ndistances grow from 0 to C's two heights.", wait=1.3)

        # Same base s: heights become areas
        big = Polygon(self.at("A"), self.at("E"), c).set_stroke(TRI_BIG, 3).set_fill(TRI_BIG, 0.3)
        small = Polygon(self.at("A"), self.at("B"), c).set_stroke(TRI_SMALL, 3).set_fill(TRI_SMALL, 0.3)
        self.play(FadeIn(big), FadeIn(small), FadeOut(VGroup(h_ea, h_ab, line_ab, ac)), run_time=0.8)
        steps = self.steps()
        self.replace_step(steps[-1], R"\frac{x - 4}{2} = \frac{S_{AEC}}{S_{ABC}}", wait=0.5)
        self.set_state("triangles", VGroup(big, small))

    def golden(self):
        fig = self.get_figure()
        big, small = self.lazy("triangles", VGroup)
        o = self.plane_to_now((0, 0))

        # Turn the pentagon: AEC lands on BDE, ABC on ADE
        self.play(Rotate(big, -72 * DEGREES, about_point=o), Rotate(small, -144 * DEGREES, about_point=o), run_time=1.6)
        bd = Line(self.at("B"), self.at("D")).set_stroke(TRI_BIG, 6)
        ae = Line(self.at("A"), self.at("E")).set_stroke(TRI_SMALL, 6)
        self.play(ShowCreation(bd), ShowCreation(ae), run_time=0.7)
        self.note("BD is parallel to AE: same height, so the areas\ncompare like the bases, diagonal : side = φ.", wait=1.6)
        # Make room: the distance changes are in the ratio line now
        steps = self.steps()
        if len(steps) >= 3:
            gap = steps[2].get_top()[1] - steps[1].get_top()[1]
            self.play(FadeOut(steps[1]), steps[2].animate.shift(-gap * UP), run_time=0.5)
            steps.set_submobjects([steps[0], steps[2]])
        self.add_step(
            R"\frac{S_{AEC}}{S_{ABC}} = \frac{S_{BDE}}{S_{ADE}} = \frac{BD}{AE} = \varphi = \frac{1 + \sqrt{5}}{2}",
            color=TRI_BIG, wait=0.6,
        )
        self.play(FadeOut(VGroup(bd, ae, big, small)), FadeIn(fig.perps), FadeIn(fig.values), run_time=0.6)
        self.conclude(R"\frac{x - 4}{2} = \varphi\ \Rightarrow\ x = 4 + 2\varphi = 5 + \sqrt{5}", font_size=42, wait=1.4)

    def general(self):
        """Not a proof: the same relation for any point inside."""
        fig = self.get_figure()
        card = self.get_card()
        # Clear the working (and the answer box, which is not a step) but keep the pentagon
        keep = {id(m) for m in (*fig.get_family(), *card.get_family(), self.frame)}
        leftovers = [m for m in self.mobjects if id(m) not in keep]
        self.play(*[FadeOut(m) for m in leftovers], FadeOut(VGroup(fig[1], fig[2], fig[3], fig[4], fig[6])), run_time=0.6)
        self._step_lines = VGroup()

        # P wanders; its four distances follow
        t = ValueTracker(0)

        def p_now():
            return P_PT + 1.25 * np.array([np.cos(t.get_value()) - 1, 0.8 * np.sin(t.get_value())])

        sides = [("EA", "d_1"), ("AB", "d_2"), ("BC", "d_3"), ("CD", "d_4")]

        def perps():
            p = p_now()
            group = VGroup()
            for side, name in sides:
                n = unit(NORMALS[side])
                foot = p + (INRADIUS - n @ p) * n
                a, b = self.plane_to_now(p), self.plane_to_now(foot)
                label = Tex(name, font_size=32).set_color(D_COLORS[side])
                label.move_to((a + b) / 2 + 0.3 * rotate_vector(normalize(b - a), PI / 2))
                group.add(Line(a, b).set_stroke(D_COLORS[side], 4), label)
            group.add(Dot(self.plane_to_now(p), radius=0.07).set_fill(WHITE))
            return group

        moving = always_redraw(perps)
        self.play(FadeIn(moving), run_time=0.6)
        title = Text("For any point P inside a regular pentagon:", font_size=28).set_color(GREY_A)
        title.move_to(self.steps_top_y * UP + 0.15 * DOWN)
        formula = Tex(
            R"\frac{d_1 - d_4}{d_2 - d_3} = \varphi = \frac{1 + \sqrt{5}}{2}",
            t2c={"d_1": D_COLORS["EA"], "d_2": D_COLORS["AB"], "d_3": D_COLORS["BC"], "d_4": D_COLORS["CD"]},
            font_size=50,
        ).next_to(title, DOWN, buff=0.45)
        box = SurroundingRectangle(formula, buff=0.22).set_stroke(RESULT_COLOR, 4)
        self.play(FadeIn(title, 0.15 * DOWN), run_time=0.5)
        self.play(Write(formula), run_time=1.2)
        self.play(ShowCreation(box), t.animate.set_value(TAU), run_time=5.0)
        self.play(FlashAround(formula, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.wait(1.2)

