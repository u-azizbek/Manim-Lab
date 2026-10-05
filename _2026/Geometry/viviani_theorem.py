from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/viviani_theorem.py
#
# Viviani's theorem: from any point P inside an equilateral triangle, the
# distances to the three sides add up to the height h.
# Proof.  Through P draw parallels to the sides: DE || AB, PG || BC, PH || AC,
# PI || AC, PF || BC.  They cut off three small equilateral triangles DGP
# (yellow, on AC), PHE (blue, on BC) and IPF (green, on AB), and each distance
# from P is an altitude of one of them.  Every altitude of an equilateral
# triangle is the same length, so use the vertical ones: from P down to IF,
# from G down to DP, from H down to PE.  PGCH is a parallelogram (PG || HC,
# PH || GC), so sliding the blue triangle by C - H puts it on top of the level
# of G with its apex at C.  The three vertical altitudes now stack from AB to C.

SIDE = 6.3
A = np.array([-3.55, -2.25, 0])
B = A + SIDE * RIGHT
C = A + SIDE * np.array([0.5, np.sqrt(3) / 2, 0])
HEIGHT = C[1] - A[1]
P_FINAL = A + np.array([0.667 * SIDE, 0.333 * HEIGHT, 0])
ARROW_X = B[0] + 0.62
BAR_X = B[0] + 0.3

GREEN_T = "#3DDC5A"      # distance to AB
YELLOW_T = "#FFE14D"     # distance to AC
BLUE_T = "#8C8CFF"       # distance to BC
PERP = "#FF4D4D"


def foot(p, x, y):
    d = normalize(y - x)
    return x + np.dot(p - x, d) * d


def meet(p1, d1, p2, d2):
    """Intersection of the lines p1 + s d1 and p2 + t d2."""
    s = np.linalg.solve(np.array([d1[:2], -d2[:2]]).T, (p2 - p1)[:2])[0]
    return p1 + s * d1


class VivianiTheorem(BrandOutroMixin, ShortsScene):
    """Viviani's theorem, by cutting off three small equilateral triangles."""

    sections = ["theorem", "proof", "outro"]

    def note(self, text, wait=1.4):
        line = Text(text, font_size=28).set_color(GREY_A).move_to(4.15 * DOWN)
        line.set_max_width(7.4)
        self.play(FadeIn(line, 0.15 * UP), run_time=0.5)
        self.wait(wait)
        self.play(FadeOut(line), run_time=0.35)

    def theorem(self):
        title = Text("Viviani's Theorem", font_size=64, weight=BOLD)
        title.set_color_by_gradient(GREEN_T, YELLOW_T, BLUE_T).move_to(6.2 * UP)
        tri = Polygon(A, B, C).set_stroke(WHITE, 4)
        names = VGroup(
            Tex("A", font_size=40).next_to(A, DL, buff=0.1),
            Tex("B", font_size=40).next_to(B, DR, buff=0.1),
            Tex("C", font_size=40).next_to(C, UP, buff=0.12),
        )
        guide = DashedLine(C + 0.2 * RIGHT, np.array([ARROW_X, C[1], 0]), dash_length=0.08).set_stroke(GREY_B, 1.5)
        bottom, top = np.array([ARROW_X, A[1], 0]), np.array([ARROW_X, C[1], 0])
        arrow = VGroup(
            Line(bottom, top).set_stroke(PERP, 4),
            ArrowTip().set_fill(PERP).scale(0.55).rotate(PI / 2).move_to(top, aligned_edge=UP),
            ArrowTip().set_fill(PERP).scale(0.55).rotate(-PI / 2).move_to(bottom, aligned_edge=DOWN),
        )
        h = Tex("h", font_size=44).set_color(PERP).next_to(arrow, RIGHT, buff=0.08).shift(0.4 * DOWN)
        self.play(Write(title), ShowCreation(tri), run_time=1.2)
        self.play(FadeIn(names), ShowCreation(guide), GrowFromCenter(arrow), FadeIn(h), run_time=0.8)

        # A point anywhere inside, and its distances to the three sides
        p = Dot(A + np.array([0.3 * SIDE, 0.25 * HEIGHT, 0]), radius=0.08).set_fill(WHITE)
        p_name = always_redraw(lambda: Tex("P", font_size=40).next_to(p, UP, buff=0.12))
        sides = [(A, B, GREEN_T), (A, C, YELLOW_T), (B, C, BLUE_T)]
        perps = always_redraw(lambda: VGroup(*[
            DashedLine(p.get_center(), foot(p.get_center(), x, y), dash_length=0.08).set_stroke(color, 4)
            for x, y, color in sides
        ]))

        def stacked():
            lengths = [np.linalg.norm(p.get_center() - foot(p.get_center(), x, y)) for x, y, _ in sides]
            bottoms = np.cumsum([0] + lengths[:-1])
            return VGroup(*[
                Line(np.array([BAR_X, A[1] + b, 0]), np.array([BAR_X, A[1] + b + l, 0])).set_stroke(color, 9)
                for b, l, (_, _, color) in zip(bottoms, lengths, sides)
            ])

        bar = always_redraw(stacked)
        self.play(FadeIn(p, scale=0.5), FadeIn(p_name), ShowCreation(perps), run_time=0.7)
        self.play(FadeIn(bar), run_time=0.5)
        statement = Text(
            "From any point inside, the distances\nto the three sides add up to the height.", font_size=28,
        ).set_color(GREY_A).move_to(4.3 * DOWN)
        self.play(FadeIn(statement, 0.15 * UP), run_time=0.6)
        for spot in [(0.5, 0.55), (0.35, 0.08), (0.62, 0.12), (0.667, 0.333)]:
            self.play(p.animate.move_to(A + np.array([spot[0] * SIDE, spot[1] * HEIGHT, 0])), run_time=1.0)
        self.wait(0.4)
        self.play(FadeOut(bar), FadeOut(statement), run_time=0.5)
        perps.clear_updaters()
        p_name.clear_updaters()
        self.p, self.p_name, self.perps = p, p_name, perps

    def proof(self):
        p = P_FINAL
        up_left, up_right = C - A, C - B
        # The parallels through P
        D = meet(p, RIGHT, A, up_left)
        E = meet(p, RIGHT, B, up_right)
        G = meet(p, up_right, A, up_left)
        H = meet(p, up_left, B, up_right)
        I = meet(p, up_left, A, RIGHT)
        F = meet(p, up_right, A, RIGHT)
        parallels = VGroup(
            DashedLine(D, E), DashedLine(p, G), DashedLine(p, H), DashedLine(p, I), DashedLine(p, F),
        ).set_stroke(GREY_A, 2)
        self.play(LaggedStart(*[ShowCreation(line) for line in parallels], lag_ratio=0.2), run_time=1.3)
        labels = VGroup(*[
            Tex(n, font_size=32).next_to(pt, d, buff=0.1)
            for n, pt, d in [("D", D, LEFT), ("E", E, RIGHT), ("G", G, UL), ("H", H, UR), ("I", I, DOWN), ("F", F, DOWN)]
        ])

        yellow = Polygon(D, G, p).set_stroke(YELLOW_T, 2).set_fill(YELLOW_T, 0.5)
        blue = Polygon(p, H, E).set_stroke(BLUE_T, 2).set_fill(BLUE_T, 0.5)
        green = Polygon(I, p, F).set_stroke(GREEN_T, 2).set_fill(GREEN_T, 0.5)
        self.play(
            LaggedStart(FadeIn(green), FadeIn(yellow), FadeIn(blue), lag_ratio=0.3), FadeIn(labels), run_time=1.1,
        )
        g_perp, y_perp, b_perp = self.perps
        self.add(g_perp, y_perp, b_perp, self.p, self.p_name)
        self.note("Three small equilateral triangles appear,\nand each distance is one of their altitudes.", wait=1.6)

        # Every altitude of an equilateral triangle is the same: turn each so it stands upright
        def turn(vertices, vertex_from, vertex_to):
            """The third of a turn about the centroid that carries one vertex to the next."""
            centre = np.mean(vertices, axis=0)
            a = np.angle(complex(*(vertex_to - centre)[:2]) / complex(*(vertex_from - centre)[:2]))
            return a, centre

        y_angle, y_centre = turn([D, G, p], p, G)
        b_angle, b_centre = turn([p, H, E], p, H)
        y_group, b_group = VGroup(yellow, y_perp), VGroup(blue, b_perp)
        self.play(
            Rotate(y_group, y_angle, about_point=y_centre),
            Rotate(b_group, b_angle, about_point=b_centre),
            run_time=1.6,
        )
        self.add(self.p, self.p_name)
        self.note("All altitudes are equal: use the upright ones.", wait=1.0)

        # PGCH is a parallelogram: the blue triangle slides up to C
        para = Polygon(p, G, C, H).set_stroke(BLUE_T, 3).set_fill(opacity=0)
        self.play(ShowCreation(para), run_time=0.7)
        self.play(b_group.animate.shift(C - H), FadeOut(para), run_time=1.3)
        self.note("PGCH is a parallelogram, so it fits exactly at the top.", wait=1.2)

        # The three upright altitudes stack from AB up to C
        bars = VGroup(*[
            Line(np.array([BAR_X, m.get_bottom()[1], 0]), np.array([BAR_X, m.get_top()[1], 0])).set_stroke(color, 9)
            for m, color in zip((g_perp, y_perp, b_perp), (GREEN_T, YELLOW_T, BLUE_T))
        ])
        self.play(
            LaggedStart(*[TransformFromCopy(m, bar) for m, bar in zip((g_perp, y_perp, b_perp), bars)], lag_ratio=0.25),
            run_time=1.5,
        )
        result = Tex("d_1 + d_2 + d_3 = h", font_size=62).move_to(5.1 * DOWN)
        for part, color in zip(("d_1", "d_2", "d_3", "h"), (GREEN_T, YELLOW_T, BLUE_T, PERP)):
            result[part].set_color(color)
        self.play(Write(result), run_time=1.0)
        box = SurroundingRectangle(result, buff=0.22).set_stroke(YELLOW, 3)
        self.play(ShowCreation(box), FlashAround(result, color=YELLOW, time_width=1.5), run_time=1.2)
        self.wait(1.5)
