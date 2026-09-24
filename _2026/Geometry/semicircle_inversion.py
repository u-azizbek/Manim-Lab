from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/semicircle_inversion.py
#
# Semicircles on OA, OB and AB, with A(0, 8) and B(6, 0), and a circle
# touching all three at E, F, G.  Find its radius x.
#
# Invert about O with radius 8 (so A stays put).  Circles through O become
# lines: the semicircle on OA becomes the ray y = 8 (x <= 0), the one on OB the
# ray x = 32/3 (y <= 0), since OB' = 64/6, and the one on AB -- whose full
# circle passes through O because angle AOB = 90 -- the segment AB'.  Those
# lines make the 3-4-5 right triangle A D B' (AD = 32/3, DB' = 8, AB' = 40/3),
# and inversion keeps tangency, so the circle becomes the excircle opposite D:
# radius s = 16, centre K(-16/3, -8), touching x = 32/3 at G'(32/3, -8).
#
# Along y = -8: KT = 16/3 and TG' = 32/3.  G is the image of G', so O, G, G'
# are collinear with OG' = 40/3 and OG = 64 / OG' = 24/5.  As OM is parallel
# to G'N, triangle GOM ~ triangle GG'N with ratio GG'/GO = 16/9, so
# G'N = GN = 3 * 16/9 = 16/3 and N is the midpoint of TG'.
# (The source solution uses GN = 16/3 without saying why; this is the gap.)
#
# L, O, K are collinear (a circle and its image are both symmetric about the
# line through O and the centre), and L, M, G, N are collinear (circles
# tangent at G).  Intercept theorem in triangles LOM ~ LKN:
#   (x - 3) / (x + 16/3) = 3 / (32/3)  =>  x = 144/23.
# Checked with exact fractions: L = (48/23, 72/23) is at distance x - 4,
# x - 3, x - 5 from the three semicircle centres, and inverting the excircle
# gives radius 144/23 with that centre.

O = (0, 0)
A = (0, 8)
B = (6, 0)
M = (3, 0)
L = (48 / 23, 72 / 23)
X = 144 / 23                        # the answer
E, F, G = (-48 / 13, 72 / 13), (192 / 29, 216 / 29), (96 / 25, -72 / 25)

B_ = (32 / 3, 0)                    # images under the inversion
D = (32 / 3, 8)
K = (-16 / 3, -8)
E_, F_, G_ = (-16 / 3, 8), (64 / 15, 24 / 5), (32 / 3, -8)
T = (0, -8)
N = (16 / 3, -8)

FIG_CENTER = 0.3 * UP
FIG_HALF = (3.75, 3.2)              # half the width and height of the figure area
VIEWS = {                           # (centre x, centre y, scale)
    "problem": (2.1, 2.91, 0.478),
    "inverted": (2.75, -0.24, 0.35),
}

OA_COLOR = "#5BD98A"
OB_COLOR = "#FF6B9A"
AB_COLOR = "#C39BFF"
CIRCLE = "#58C4DD"
INVERSION = "#FFD166"
AXIS_COLOR = "#8A9BB0"
SIMILAR = "#FF9F43"
THALES = "#4FD1C5"
LEG = "#E6EDF5"

INVERTED_WINDOW = (-6.3, 11.9, -9.4, 9.2)   # how far the image rays are drawn


def invert(p):
    p = np.array(p, dtype=float)
    return 64 * p / np.dot(p, p)


def radial(p, q, alpha):
    """Part way from p to its image q, along the ray from O."""
    p, q = np.array(p, dtype=float), np.array(q, dtype=float)
    rp, rq = get_norm(p), get_norm(q)
    return p / rp * rp ** (1 - alpha) * rq ** alpha


class SemicircleInversion(MockTestShort):
    """A circle touching three semicircles, by inversion about O."""

    test = ""
    card_top_buff = 0.5
    step_buff = 0.3
    step_font_size = 34

    problem_tex = (
        R"\text{Semicircles on } OA,\ OB,\ AB.\\"
        R"\text{A circle touches all three}\\"
        R"\text{at } E,\ F,\ G.\ \ A(0,8),\ B(6,0).\\"
        R"\text{Find its radius.}"
    )

    sections = [
        "pose",
        "draw_figure",
        "invert_idea",
        "lines",
        "excircle",
        "bottom_line",
        "thales",
        "finish",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = FIG_CENTER[1] - FIG_HALF[1] - 0.3
        return card

    # The coordinate view: which part of the plane fills the figure area

    def trackers(self):
        if not hasattr(self, "_view"):
            self._view = [ValueTracker(v) for v in VIEWS["problem"]]
        return self._view

    def sp(self, point):
        cx, cy, s = [t.get_value() for t in self.trackers()]
        point = point() if callable(point) else point
        return FIG_CENTER + s * ((point[0] - cx) * RIGHT + (point[1] - cy) * UP)

    def unit(self):
        return self.trackers()[2].get_value()

    def view_window(self):
        cx, cy, s = [t.get_value() for t in self.trackers()]
        return cx - FIG_HALF[0] / s, cx + FIG_HALF[0] / s, cy - FIG_HALF[1] / s, cy + FIG_HALF[1] / s

    def view(self, name, run_time=2.0, *extra):
        self.play(
            *[t.animate.set_value(v) for t, v in zip(self.trackers(), VIEWS[name])],
            *extra,
            run_time=run_time,
        )

    # Drawing in plane coordinates.  Everything redraws from the view, so the
    # figure can zoom out to the inverted picture and back.

    def fade(self, name, value=1.0):
        if not hasattr(self, "_fades"):
            self._fades = dict()
        if name not in self._fades:
            self._fades[name] = ValueTracker(value)
        return self._fades[name]

    @staticmethod
    def level(opacity):
        return opacity.get_value() if isinstance(opacity, ValueTracker) else opacity

    def seg(self, p, q, color, width=4, opacity=1.0, dashed=False):
        def build():
            start, end = self.sp(p), self.sp(q)
            line = DashedLine(start, end, dash_length=0.1) if dashed else Line(start, end)
            return line.set_stroke(color, width, self.level(opacity))
        return always_redraw(build)

    def arc(self, center, radius, a0, a1, color, width=4, opacity=1.0, dashes=0):
        def build():
            arc = Arc(
                start_angle=a0 * DEGREES, angle=(a1 - a0) * DEGREES,
                radius=radius * self.unit(), arc_center=self.sp(center),
            )
            if dashes:
                arc = DashedVMobject(arc, num_dashes=dashes)
            return arc.set_stroke(color, width, self.level(opacity))
        return always_redraw(build)

    def dot(self, point, color=WHITE, radius=0.065, opacity=1.0):
        return always_redraw(lambda: Dot(self.sp(point), radius=radius).set_fill(
            color, self.level(opacity)).set_stroke(BLACK, 1.5, self.level(opacity)))

    def tag(self, tex, point, direction, color=WHITE, font_size=28, buff=0.12):
        label = Tex(tex, font_size=font_size).set_color(color)
        if np.any(direction):
            label.add_updater(lambda m: m.next_to(self.sp(point), direction, buff=buff))
        else:
            label.add_updater(lambda m: m.move_to(self.sp(point)))
        return label.update()

    def poly(self, points, color, opacity=0.25):
        return always_redraw(lambda: Polygon(*[self.sp(q) for q in points]).set_fill(
            color, opacity).set_stroke(color, 3))

    def right_angle(self, corner, d1, d2, size=0.55, color=LEG):
        corner, d1, d2 = map(np.array, (corner, d1, d2))
        return always_redraw(lambda: VMobject().set_points_as_corners([
            self.sp(corner + size * d1), self.sp(corner + size * (d1 + d2)), self.sp(corner + size * d2),
        ]).set_stroke(color, 2.5))

    def inverting(self, images, color, width=5):
        """A curve that starts on the preimage of `images` and, as its
        `alpha` runs to 1, slides every point out along its ray from O onto
        its image."""
        pre = [invert(q) for q in images]
        alpha = ValueTracker(0)
        curve = always_redraw(lambda: VMobject().set_points_smoothly([
            self.sp(radial(a, b, alpha.get_value())) for a, b in zip(pre, images)
        ]).set_stroke(color, width))
        curve.alpha = alpha
        return curve

    def traveling(self, point, color=WHITE):
        """A dot moving from `point` to its image as its `alpha` runs to 1."""
        alpha = ValueTracker(0)
        image = invert(point)
        where = lambda: radial(point, image, alpha.get_value())
        dot = self.dot(where, color)
        dot.alpha, dot.where = alpha, where
        return dot

    def homothety(self, points, center, factor, turns, color):
        """A triangle carried by a spiral similarity about `center`."""
        center = np.array(center, dtype=float)
        points = [np.array(q, dtype=float) for q in points]
        alpha = ValueTracker(0)

        def moved():
            a = alpha.get_value()
            scale = 1 + a * (factor - 1)
            angle = a * turns * PI
            rot = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
            return [center + scale * rot @ (q - center) for q in points]

        mob = always_redraw(lambda: Polygon(*[self.sp(q) for q in moved()]).set_fill(
            color, 0.35).set_stroke(color, 3))
        mob.alpha = alpha
        return mob

    # The original figure

    def make_figure(self):
        fade = self.fade("originals")

        def axis(horizontal):
            x0, x1, y0, y1 = self.view_window()
            start, end = ((x0, 0), (x1, 0)) if horizontal else ((0, y0), (0, y1))
            return Arrow(self.sp(start), self.sp(end), buff=0, thickness=2).set_color(AXIS_COLOR)

        fig = dict(
            axes=VGroup(always_redraw(lambda: axis(True)), always_redraw(lambda: axis(False))),
            O=self.dot(O), A=self.dot(A), B=self.dot(B),
            semi_oa=self.arc((0, 4), 4, 90, 270, OA_COLOR, opacity=fade),
            semi_ob=self.arc((3, 0), 3, 180, 360, OB_COLOR, opacity=fade),
            semi_ab=self.arc((3, 4), 5, -53.13, 126.87, AB_COLOR, opacity=fade),
            circle=self.arc(L, X, 0, 360, CIRCLE, width=5, opacity=self.fade("circle")),
            touch=VGroup(*[self.dot(q, opacity=self.fade("circle")) for q in (E, F, G)]),
        )
        fig["names"] = VGroup(
            self.tag("O", O, DL, buff=0.08),
            self.tag("A", A, UL, buff=0.08),
            self.tag("B", B, DR, buff=0.08),
        )
        fig["touch_names"] = VGroup(
            self.tag("E", E, LEFT), self.tag("F", F, UR, buff=0.06), self.tag("G", G, DOWN),
        )
        fig["center"] = self.dot(L, CIRCLE)
        fig["radius"] = self.seg(L, (L[0] + X, L[1]), CIRCLE, 3)
        fig["x"] = self.tag("x", ((L[0] + X / 2), L[1]), UP, CIRCLE, font_size=32, buff=0.08)
        return fig

    def get_figure(self):
        def build():
            fig = self.make_figure()
            for key in ["axes", "semi_oa", "semi_ob", "semi_ab", "circle", "touch",
                        "O", "A", "B", "names", "touch_names"]:
                self.add(fig[key])
            return fig
        return self.lazy("figure", build)

    # Sections

    def draw_figure(self):
        self.get_card()
        fig = self.make_figure()
        self.play(ShowCreation(fig["axes"], lag_ratio=0), run_time=0.8)
        self.play(
            *[FadeIn(fig[k], scale=0.5) for k in "OAB"],
            FadeIn(fig["names"], lag_ratio=0.2),
            run_time=0.7,
        )
        for key in ["semi_oa", "semi_ob", "semi_ab"]:
            self.play(ShowCreation(fig[key]), run_time=0.7)
        self.play(ShowCreation(fig["circle"]), run_time=1.2)
        self.play(FadeIn(fig["touch"], scale=0.5), FadeIn(fig["touch_names"], lag_ratio=0.2), run_time=0.7)
        self.play(
            FadeIn(fig["center"], scale=0.5), ShowCreation(fig["radius"]), FadeIn(fig["x"]),
            run_time=0.8,
        )
        self.set_state("figure", fig)
        self.wait(1.0)

    def invert_idea(self):
        fig = self.get_figure()
        self.play(FadeOut(VGroup(fig["center"], fig["radius"], fig["x"])), run_time=0.4)
        self.note("Circles through O are hard to work with.\nInvert about O with radius 8.", wait=1.4)

        # Make room for the inverted picture
        self.view("inverted", 1.8)
        ring = self.arc(O, 8, 0, 360, INVERSION, width=3, dashes=70)
        self.play(ShowCreation(ring), run_time=1.0)
        self.add_step(R"OP \cdot OP' = 8^2 = 64", color=INVERSION, wait=0.3)
        self.note("Each P goes to P' on ray OP with OP · OP' = 64.\nA is on the circle, so A stays: A' = A.", wait=1.6)

        # B slides out to its image
        b_ = self.traveling(B, OB_COLOR)
        b_name = self.tag("B'", b_.where, UR, OB_COLOR, buff=0.06)
        self.add(b_, b_name)
        self.play(b_.alpha.animate.set_value(1), run_time=1.2)
        self.add_step(R"OB' = \tfrac{64}{OB} = \tfrac{64}{6} = \tfrac{32}{3}", color=OB_COLOR, wait=0.8)
        self.set_state("ring", ring)
        self.set_state("b_", VGroup(b_, b_name))

    def lines(self):
        fig = self.get_figure()
        self.lazy("ring", lambda: self.arc(O, 8, 0, 360, INVERSION, width=3, dashes=70))
        self.lazy("b_", lambda: VGroup(self.dot(B_, OB_COLOR), self.tag("B'", B_, UR, OB_COLOR, buff=0.06)))
        x0, x1, y0, y1 = INVERTED_WINDOW

        self.note("A circle through O inverts to a straight line.", wait=1.2)
        self.play(self.fade("originals").animate.set_value(0.35), run_time=0.4)

        # Semicircle OA: its image is the ray y = 8 to the left of A
        ray_a = self.inverting([(t, 8) for t in np.linspace(0, x0, 60)], OA_COLOR)
        self.add(ray_a)
        self.play(ray_a.alpha.animate.set_value(1), run_time=1.6)
        # Semicircle OB: the ray x = 32/3 below B'
        ray_b = self.inverting([(B_[0], t) for t in np.linspace(0, y0, 60)], OB_COLOR)
        self.add(ray_b)
        self.play(ray_b.alpha.animate.set_value(1), run_time=1.6)

        # Semicircle AB: its full circle passes through O as well
        rest = self.arc((3, 4), 5, 126.87, 306.87, AB_COLOR, width=3, dashes=40)
        corner = self.right_angle(O, (1, 0), (0, 1), size=0.9, color=AB_COLOR)
        self.play(ShowCreation(rest), ShowCreation(corner), run_time=0.8)
        self.note("Angle AOB = 90°, so the circle on AB\npasses through O too.", wait=1.3)
        side = self.inverting([np.array(A) + u * (np.array(B_) - A) for u in np.linspace(0, 1, 60)], AB_COLOR)
        self.add(side)
        self.play(side.alpha.animate.set_value(1), FadeOut(rest), FadeOut(corner), run_time=1.6)

        # The three lines close up into a right triangle
        legs = VGroup(
            self.seg(A, D, LEG, 2.5, dashed=True),
            self.seg(D, B_, LEG, 2.5, dashed=True),
        )
        d_dot = self.dot(D)
        d_name = self.tag("D", D, UR, buff=0.06)
        at_d = self.right_angle(D, (-1, 0), (0, -1), size=0.9)
        self.play(ShowCreation(legs, lag_ratio=0.5), FadeIn(d_dot), FadeIn(d_name), ShowCreation(at_d), run_time=1.0)
        sides = VGroup(
            self.tag(R"\tfrac{32}{3}", ((A[0] + D[0]) / 2, 8), DOWN, font_size=26, buff=0.1),
            self.tag("8", (D[0], 4), LEFT, font_size=26, buff=0.1),
            self.tag(R"\tfrac{40}{3}", (16 / 3 - 0.9, 4 - 1.2), ORIGIN, AB_COLOR, font_size=26),
        )
        self.play(FadeIn(sides, lag_ratio=0.3), run_time=0.8)
        self.clear_steps()
        self.add_step(R"AD = \tfrac{32}{3},\quad DB' = 8,\quad AB' = \tfrac{40}{3}", wait=0.4)
        self.note("A 3-4-5 right triangle, scaled by 8/3.", wait=1.1)
        self.set_state("images", VGroup(ray_a, ray_b, side))
        self.set_state("triangle", VGroup(legs, d_dot, d_name, at_d, sides))

    def excircle(self):
        fig = self.get_figure()
        images = self.lazy("images", VGroup)
        self.clear_steps()

        self.note("Inversion keeps tangency: the circle becomes\none touching all three lines.", wait=1.4)
        self.play(self.fade("circle").animate.set_value(0.35), FadeOut(fig["touch_names"]), run_time=0.4)

        # The far arc E F G of the circle opens out into a quarter of a big circle
        quarter = self.inverting([
            np.array(K) + 16 * np.array([np.cos(a), np.sin(a)])
            for a in np.linspace(PI / 2, 0, 90)
        ], CIRCLE)
        dots = [self.traveling(q, CIRCLE) for q in (E, F, G)]
        names = VGroup(
            self.tag("E'", dots[0].where, UP, CIRCLE, buff=0.1),
            self.tag("F'", dots[1].where, UR, CIRCLE, buff=0.04),
            self.tag("G'", dots[2].where, DR, CIRCLE, buff=0.06),
        )
        self.add(quarter, *dots, names)
        self.play(
            quarter.alpha.animate.set_value(1),
            *[d.alpha.animate.set_value(1) for d in dots],
            run_time=2.2,
        )
        self.wait(0.4)

        # It is the excircle opposite D, and the right angle at D makes a square
        self.note("It is the excircle opposite D: the two\ntangents from D both equal s.", wait=1.4)
        square = VGroup(
            self.seg(D, E_, CIRCLE, 6),
            self.seg(D, G_, CIRCLE, 6),
        )
        self.play(ShowCreation(square, lag_ratio=0), run_time=0.8)
        self.add_step(
            R"s = \tfrac{1}{2}\left(\tfrac{32}{3} + 8 + \tfrac{40}{3}\right) = 16",
            color=CIRCLE, wait=0.5,
        )
        k_dot = self.dot(K, CIRCLE)
        k_name = self.tag("K", K, DL, CIRCLE, buff=0.06)
        radii = VGroup(
            self.seg(K, E_, CIRCLE, 3, dashed=True),
            self.seg(K, G_, CIRCLE, 3, dashed=True),
        )
        sixteens = VGroup(
            self.tag("16", (K[0], 0), RIGHT, CIRCLE, font_size=28, buff=0.1),
            self.tag("16", (2.67, -8), UP, CIRCLE, font_size=28, buff=0.1),
        )
        self.play(
            FadeIn(k_dot, scale=0.5), FadeIn(k_name), ShowCreation(radii, lag_ratio=0.5),
            FadeIn(sixteens), run_time=1.0,
        )
        self.add_step(
            R"r = s = 16,\quad K\left(-\tfrac{16}{3}, -8\right),\quad G'\left(\tfrac{32}{3}, -8\right)",
            color=CIRCLE, wait=1.0,
        )
        self.play(FadeOut(square), FadeOut(sixteens), run_time=0.4)
        self.set_state("excircle", VGroup(quarter, *dots, names, k_dot, k_name, radii))

    def bottom_line(self):
        fig = self.get_figure()
        triangle = self.lazy("triangle", VGroup)
        ring = self.lazy("ring", VGroup)
        self.clear_steps()
        self.play(FadeOut(ring), FadeOut(triangle[-1]), run_time=0.5)

        # The line y = -8 through K, T and G'
        t_dot = self.dot(T)
        t_name = self.tag("T", T, DOWN, buff=0.1)
        down = self.seg(O, T, LEG, 2.5, dashed=True)
        eight = self.tag("8", (0, -5.3), LEFT, font_size=26, buff=0.1)
        self.play(ShowCreation(down), FadeIn(t_dot), FadeIn(t_name), FadeIn(eight), run_time=0.8)
        lengths = VGroup(
            self.tag(R"\tfrac{16}{3}", (-8 / 3, -8), DOWN, font_size=26, buff=0.12),
            self.tag(R"\tfrac{32}{3}", (16 / 3, -8), DOWN, font_size=26, buff=0.12),
        )
        self.play(FadeIn(lengths, lag_ratio=0.3), run_time=0.6)

        # G' is the image of G: they lie on one ray from O
        ray = self.seg(O, G_, INVERSION, 3)
        self.play(ShowCreation(ray), run_time=0.8)
        self.play(self.fade("circle").animate.set_value(1), run_time=0.4)
        self.note("G' is the image of G, so O, G, G' line up\nand OG · OG' = 64.", wait=1.4)
        right = self.poly([O, T, G_], INVERSION, 0.12)
        self.play(FadeIn(right), run_time=0.5)
        self.add_step(
            R"OG' = \tfrac{40}{3} \quad\Rightarrow\quad OG = \tfrac{64}{40/3} = \tfrac{24}{5}",
            color=INVERSION, wait=0.6,
        )
        self.play(FadeOut(right), run_time=0.4)

        # From M through G down to N: two similar triangles
        m_dot = self.dot(M, OB_COLOR)
        m_name = self.tag("M", M, UP, OB_COLOR, buff=0.1)
        n_dot = self.dot(N, OB_COLOR)
        n_name = self.tag("N", N, DOWN, OB_COLOR, buff=0.1)
        normal = self.seg(M, N, OB_COLOR, 3)
        self.play(FadeIn(m_dot), FadeIn(m_name), FadeOut(lengths[1]), run_time=0.4)
        self.play(ShowCreation(normal), FadeIn(n_dot), FadeIn(n_name), run_time=0.8)
        small = self.poly([G, O, M], SIMILAR, 0.3)
        self.play(FadeIn(small), run_time=0.5)
        self.note("OM is parallel to G'N, so triangles GOM\nand GG'N are similar.", wait=1.3)
        grow = self.homothety([G, O, M], G, 16 / 9, 1, SIMILAR)
        self.add(grow)
        self.play(grow.alpha.animate.set_value(1), run_time=1.6)
        ratio = self.add_step(
            R"\tfrac{GG'}{GO} = \tfrac{40/3 \,-\, 24/5}{24/5} = \tfrac{16}{9}", color=SIMILAR, wait=0.6,
        )
        self.replace_step(
            ratio, R"G'N = GN = 3 \cdot \tfrac{16}{9} = \tfrac{16}{3}", color=SIMILAR, wait=0.4,
        )

        # N splits TG' in half: 16/3 three times along the bottom
        thirds = VGroup(
            self.tag(R"\tfrac{16}{3}", (8 / 3, -8), DOWN, font_size=26, buff=0.12),
            self.tag(R"\tfrac{16}{3}", (8, -8), DOWN, font_size=26, buff=0.12),
        )
        gn = self.tag(R"\tfrac{16}{3}", ((G[0] + N[0]) / 2, (G[1] + N[1]) / 2), RIGHT, SIMILAR, font_size=26, buff=0.1)
        self.play(
            FadeOut(small), FadeOut(grow),
            FadeIn(thirds, lag_ratio=0.3),
            FadeIn(gn),
            run_time=0.9,
        )
        self.wait(0.8)
        self.set_state("bottom", VGroup(t_dot, t_name, down, eight, lengths[0], thirds, ray))
        self.set_state("normal", VGroup(m_dot, m_name, n_dot, n_name, normal, gn))

    def thales(self):
        fig = self.get_figure()
        self.clear_steps()

        # The centre of the circle lies on line OK...
        l_dot = self.dot(L, CIRCLE)
        l_name = self.tag("L", L, UL, CIRCLE, buff=0.06)
        through = self.seg(K, L, THALES, 3)
        self.play(FadeIn(l_dot, scale=0.5), FadeIn(l_name), run_time=0.5)
        self.play(ShowCreation(through), run_time=0.9)
        self.note("A circle and its image are symmetric about\nline OK, so L, O, K line up.", wait=1.5)

        # ...and on line MN, since the circles touch at G
        extend = self.seg(L, M, OB_COLOR, 3)
        self.play(ShowCreation(extend), run_time=0.6)
        self.note("The circles touch at G, so L, M, G, N line up.", wait=1.2)
        parts = VGroup(
            self.tag("x - 3", ((L[0] + M[0]) / 2, (L[1] + M[1]) / 2), RIGHT, CIRCLE, font_size=26, buff=0.1),
            self.tag("3", ((M[0] + G[0]) / 2, (M[1] + G[1]) / 2), RIGHT, OB_COLOR, font_size=26, buff=0.1),
        )
        self.play(FadeIn(parts, lag_ratio=0.4), run_time=0.7)

        # Two parallel lines cut the two rays from L
        small = self.poly([L, O, M], THALES, 0.3)
        self.play(FadeIn(small), run_time=0.5)
        self.note("OM is parallel to KN: the intercept theorem.", wait=1.1)
        grow = self.homothety([L, O, M], L, 32 / 9, 0, THALES)
        self.add(grow)
        self.play(grow.alpha.animate.set_value(1), run_time=1.6)

        rule = self.add_step(R"\frac{LM}{LN} = \frac{OM}{KN}", font_size=38, wait=0.7)
        self.replace_step(
            rule, R"\frac{x - 3}{x + \frac{16}{3}} = \frac{3}{\frac{32}{3}}",
            font_size=38, wait=0.9,
        )
        work = self.add_step(R"\tfrac{32}{3}x - 32 = 3x + 16", wait=0.6)
        work = self.replace_step(work, R"\tfrac{23}{3}x = 48", wait=0.5)
        self.replace_step(work, R"x = \tfrac{144}{23}", color=RESULT_COLOR, font_size=42, wait=0.8)
        self.set_state("thales", VGroup(l_dot, l_name, through, extend, parts, small, grow))

    def finish(self):
        fig = self.get_figure()
        self.get_card()
        keep = {id(fig[k]) for k in fig} | {id(self.get_card())}
        extra = [m for m in self.mobjects if isinstance(m, VMobject) and id(m) not in keep]
        self.clear_steps()

        # Back to the original picture, with the radius found
        self.play(*[FadeOut(m) for m in extra], run_time=0.6)
        self.view(
            "problem", 1.8,
            self.fade("originals").animate.set_value(1),
            self.fade("circle").animate.set_value(1),
            FadeIn(fig["touch_names"]),
        )
        self.play(FadeIn(fig["center"], scale=0.5), ShowCreation(fig["radius"]), run_time=0.7)
        found = self.tag(R"x = \tfrac{144}{23}", ((L[0] + X / 2), L[1]), UP, YELLOW, font_size=32, buff=0.08)
        self.play(FadeIn(found, 0.1 * UP), run_time=0.6)
        self.conclude(R"x = \tfrac{144}{23} \approx 6.26", wait=1.5)
