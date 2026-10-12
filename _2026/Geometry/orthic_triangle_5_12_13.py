from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/orthic_triangle_5_12_13.py
#
# The feet of the altitudes of ABC form a triangle with sides
# A1B1 = 5, B1C1 = 12, A1C1 = 13.  Find the circumradius and the area of ABC.
#
# 5^2 + 12^2 = 13^2, so the orthic triangle is right-angled at B1.  The cyclic
# quadrilaterals ABA1B1 and BCB1C1 copy angle B to both sides of B1 along AC,
# so B + 90 + B = 180 and B = 45.  The circumcircle of the orthic triangle is
# the nine-point circle; its diameter is the hypotenuse, so R9 = 13/2, and the
# homothety at H with ratio 1/2 takes the circumcircle onto it: R = 13.
# Finally OA, OB, OC are perpendicular to B1C1, A1C1, A1B1 (the tangent at A
# is parallel to B1C1), so joining O to the feet cuts ABC into three
# quadrilaterals with perpendicular diagonals: S = R/2 (5 + 12 + 13) = 195.
#
# A concrete triangle with this orthic triangle has B = 45 and R = sqrt(13);
# with O at the origin and lengths in units of sqrt(13) its vertices are lattice
# points, which is the model below.

MODEL = dict(
    A=(2, 3), B=(-3, -2), C=(3, -2), O=(0, 0), H=(2, -1), N=(1, -0.5),
    A1=(2, -2), B1=(36 / 13, -11 / 13), C1=(0, 1),
    # where OA, OB (extended) and OC cross the opposite orthic sides
    XA=(6 / 13, 9 / 13), XB=(6 / 13, 4 / 13), XC=(30 / 13, -20 / 13),
)
R_MODEL = np.sqrt(13)

R_SCREEN = 3.0                   # circumradius on screen during the solution
U = R_SCREEN / R_MODEL
FIG_CENTER = 1.0 * UP            # O, during the solution
BIG = 3.5 / R_SCREEN             # the opening figure doubles as the thumbnail
BIG_CENTER = 0.75 * UP

TRI_COLOR = "#E8ECF4"
C5 = "#4ECDC4"                   # A1B1 = 5
C12 = "#FF9F43"                  # B1C1 = 12
C13 = "#FF6BD6"                  # A1C1 = 13
CIRC_COLOR = "#58C4DD"           # circumcircle, O
NINE_COLOR = "#FFD166"           # nine-point circle, N
ANG_COLOR = "#A78BFA"            # angle B and its copies
H_COLOR = "#FF6B6B"
RESULT_COLOR = YELLOW

LABEL_SPEC = dict(
    A=dict(away_from="O"), B=dict(away_from="O"), C=dict(away_from="O"),
    A1=dict(direction=DOWN), B1=dict(away_from="B"), C1=dict(away_from="C"),
)


def side_label(tex, p, q, color, away, font_size=32, buff=0.1, along=0.5):
    """A length label beside segment pq, on the side away from `away`."""
    label = Tex(tex, font_size=font_size).set_color(color)
    spot = p + along * (q - p)
    normal = rotate_vector(normalize(q - p), PI / 2)
    if np.dot(normal, spot - away) < 0:
        normal = -normal
    reach = 0.5 * abs(normal[0]) * label.get_width() + 0.5 * abs(normal[1]) * label.get_height()
    return label.move_to(spot + (buff + reach) * normal)


def glowing(circle, color):
    """A circle with a soft halo, for the thumbnail."""
    return VGroup(
        circle.copy().set_stroke(color, 20, opacity=0.07),
        circle.copy().set_stroke(color, 11, opacity=0.16),
        circle,
    )


class OrthicTriangle51213(BrandOutroMixin, StepListMixin, ShortsScene):
    """Circumradius and area of ABC from its 5-12-13 orthic triangle."""

    steps_top_y = -2.35
    step_buff = 0.4
    step_font_size = 40
    step_max_width = 6.9

    sections = ["pose", "right_angle", "angle_b", "circumradius", "area", "outro"]

    # Layout

    def place(self, xy):
        return FIG_CENTER + U * np.array([xy[0], xy[1], 0.0])

    def to_big(self, mobject):
        """Map from solution coordinates to the blown-up opening layout."""
        return mobject.scale(BIG, about_point=FIG_CENTER).shift(BIG_CENTER - FIG_CENTER)

    def at(self, name):
        return self.fig.p(name)

    def dismiss(self, *names, run_time=0.5):
        """Clear what earlier sections drew, skipping whatever a partial
        render never built."""
        leftovers = VGroup(*[getattr(self, n) for n in names if hasattr(self, n)])
        if len(leftovers) > 0:
            self.play(FadeOut(leftovers), run_time=run_time)

    def behind(self, *mobjects):
        """Fills belong under the figure's strokes and labels."""
        self.add(*mobjects)
        self.bring_to_back(*mobjects)
        return VGroup(*mobjects)

    def tex_note(self, tex, wait=1.0, font_size=32):
        """`note`, but typeset, so names like A_1B_1 keep their subscripts."""
        line = Tex(tex, font_size=font_size).set_color(GREY_B)
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.play(FadeIn(line, 0.15 * DOWN), run_time=0.5)
        self.wait(wait)
        self.play(FadeOut(line, 0.15 * UP), run_time=0.35)

    def boxed(self, line, color=RESULT_COLOR):
        box = SurroundingRectangle(line, buff=0.18).set_stroke(color, 3.5)
        self.play(ShowCreation(box), run_time=0.45)
        return box

    # Title

    def make_title(self):
        title = Text("Orthic Triangle 5-12-13", font_size=60, weight=BOLD)
        title.set_color_by_gradient(C5, NINE_COLOR, C13)
        title.set_max_width(7.3)
        subtitle = Text("Find the circumradius and the area", font_size=30)
        subtitle.set_color(GREY_A)
        subtitle.next_to(title, DOWN, buff=0.22)
        return VGroup(title, subtitle).move_to(5.2 * UP)

    def get_title(self):
        return self.lazy("title", self.make_title)

    # The figure

    def make_figure(self):
        fig = GeoFigure(
            {name: self.place(xy) for name, xy in MODEL.items()},
            line_color=TRI_COLOR, line_width=4, label_font_size=30,
        )
        self.fig = fig

        self.tri_fill = fig.region("A", "B", "C", color=CIRC_COLOR, opacity=0.06)
        self.tri = fig.polygon("A", "B", "C")
        self.alts = VGroup(*[
            fig.dashed(v, f, stroke_color=GREY_B, stroke_width=2.5, dash_length=0.07)
            for v, f in [("A", "A1"), ("B", "B1"), ("C", "C1")]
        ])
        self.orthic_fill = fig.region("A1", "B1", "C1", color=NINE_COLOR, opacity=0.14)
        self.orthic = VGroup(
            fig.segment("A1", "B1", stroke_color=C5, stroke_width=5),
            fig.segment("B1", "C1", stroke_color=C12, stroke_width=5),
            fig.segment("A1", "C1", stroke_color=C13, stroke_width=5),
        )
        self.side_nums = VGroup(
            side_label("5", self.at("A1"), self.at("B1"), C5, self.at("C1"), along=0.3),
            side_label("12", self.at("B1"), self.at("C1"), C12, self.at("A1")),
            side_label("13", self.at("A1"), self.at("C1"), C13, self.at("B1"), along=0.62),
        )
        self.vertex_dots = fig.dots("A", "B", "C", radius=0.055)
        self.foot_dots = fig.dots("A1", "B1", "C1", radius=0.06)
        self.names = {
            n: fig.label(n, tex=n.replace("1", "_1"), **spec)
            for n, spec in LABEL_SPEC.items()
        }
        self.vertex_names = VGroup(*[self.names[n] for n in "ABC"])
        self.foot_names = VGroup(*[self.names[n] for n in ["A1", "B1", "C1"]])

        return VGroup(
            self.tri_fill, self.orthic_fill, self.tri, self.alts, self.orthic,
            self.vertex_dots, self.foot_dots, self.vertex_names, self.foot_names,
            self.side_nums,
        )

    def get_figure(self):
        return self.lazy("figure", self.make_figure)

    def circumcircle(self):
        return Circle(radius=R_SCREEN).move_to(self.at("O")).set_stroke(CIRC_COLOR, 4)

    def nine_point_circle(self):
        return Circle(radius=R_SCREEN / 2).move_to(self.at("N")).set_stroke(NINE_COLOR, 4)

    # Sections

    def pose(self):
        """Title, the triangle with its orthic triangle, and both circles --
        the thumbnail frame -- then shrink to working size."""
        title = self.set_state("title", self.make_title())
        self.play(Write(title[0]), run_time=1.0)
        self.play(FadeIn(title[1], 0.2 * UP), run_time=0.5)

        figure = self.to_big(self.make_figure())
        self.play(ShowCreation(self.tri), FadeIn(self.tri_fill), run_time=0.8)
        self.play(
            FadeIn(self.vertex_dots), FadeIn(self.vertex_names, lag_ratio=0.2),
            ShowCreation(self.alts, lag_ratio=0.25),
            run_time=0.9,
        )
        self.play(FadeIn(self.foot_dots, scale=0.5), FadeIn(self.foot_names, lag_ratio=0.2), run_time=0.5)
        self.play(
            ShowCreation(self.orthic, lag_ratio=0.3), FadeIn(self.orthic_fill),
            FadeIn(self.side_nums, lag_ratio=0.3),
            run_time=1.0,
        )

        # Both circles, glowing, for the thumbnail
        circ = glowing(self.circumcircle(), CIRC_COLOR)
        nine = glowing(self.nine_point_circle(), NINE_COLOR)
        centers = VGroup(
            Dot(self.at("O"), radius=0.06).set_fill(CIRC_COLOR),
            Dot(self.at("N"), radius=0.06).set_fill(NINE_COLOR),
        )
        thumb = self.to_big(VGroup(circ, nine, centers))
        self.play(ShowCreation(circ[-1]), ShowCreation(nine[-1]), run_time=1.0)
        self.play(FadeIn(circ[:2]), FadeIn(nine[:2]), FadeIn(centers), run_time=0.4)

        given = Tex(R"A_1, B_1, C_1 \text{ are the feet of the altitudes}", font_size=32)
        given.set_color(GREY_A)
        question = Tex(R"R = \,?\qquad S_{ABC} = \,?", font_size=54).set_color(RESULT_COLOR)
        VGroup(given, question).arrange(DOWN, buff=0.3).move_to(3.85 * DOWN)
        self.play(FadeIn(given, 0.15 * UP), FadeIn(question, scale=0.85), run_time=0.6)
        self.add(figure)
        self.wait(1.5)

        # Down to working size; the circles come back when they are earned
        self.play(FadeOut(VGroup(thumb, given, question)), run_time=0.5)
        self.play(
            figure.animate.shift(FIG_CENTER - BIG_CENTER).scale(1 / BIG, about_point=FIG_CENTER),
            run_time=0.9,
        )
        self.set_state("figure", figure)

    def right_angle(self):
        """5-12-13 is Pythagorean, so the orthic triangle is right-angled at B1."""
        self.get_title()
        self.get_figure()
        fig = self.fig

        line = self.add_step(
            R"5^2 + 12^2 = 13^2",
            t2c={"5": C5, "12": C12, "13": C13}, run_time=0.7, wait=0.2,
        )
        self.play(
            LaggedStart(*[Indicate(m, scale_factor=1.3) for m in self.side_nums], lag_ratio=0.3),
            run_time=0.9,
        )
        self.rt_b1 = fig.right_angle("A1", "B1", "C1", size=0.17, color=WHITE, fill_opacity=0.9)
        self.play(FadeIn(self.rt_b1, scale=0.4), run_time=0.4)
        self.play(FlashAround(self.rt_b1, color=WHITE), run_time=0.6)
        self.replace_step(line, R"\angle A_1 B_1 C_1 = 90^\circ", wait=0.3)

    def angle_b(self):
        """Two cyclic quadrilaterals copy angle B to either side of B1."""
        self.get_title()
        self.get_figure()
        fig = self.fig
        self.clear_steps(run_time=0.4)
        if not hasattr(self, "rt_b1"):
            self.rt_b1 = fig.right_angle("A1", "B1", "C1", size=0.17, color=WHITE, fill_opacity=0.9)
            self.add(self.rt_b1)

        self.ang_b = fig.angle("A", "B", "C", radius=0.5, color=ANG_COLOR, fill_opacity=0.35, stroke_width=3.5)
        self.play(FadeIn(self.ang_b, scale=0.6), run_time=0.4)

        copies = VGroup()
        for quad, diameter, marks, target in [
            (("A", "B", "A1", "B1"), ("A", "B"), (("A", "A1", "B"), ("A", "B1", "B")), ("C", "B1", "A1")),
            (("B", "C", "B1", "C1"), ("B", "C"), (("B", "B1", "C"), ("B", "C1", "C")), ("A", "B1", "C1")),
        ]:
            circle = DashedVMobject(
                Circle(radius=fig.dist(*diameter) / 2).move_to(fig.midpoint(*diameter)),
                num_dashes=70,
            ).set_stroke(ANG_COLOR, 2.5)
            fill = self.behind(fig.region(*quad, color=ANG_COLOR, opacity=0.16))
            rights = VGroup(*[fig.right_angle(*m, size=0.14, color=GREY_A) for m in marks])
            self.play(FadeIn(fill), FadeIn(rights), ShowCreation(circle), run_time=0.8)
            copy = fig.angle(*target, radius=0.38, color=ANG_COLOR, fill_opacity=0.5, stroke_width=3.5)
            self.play(TransformFromCopy(self.ang_b, copy), run_time=0.9)
            self.play(FadeOut(VGroup(circle, fill, rights)), run_time=0.35)
            copies.add(copy)
        self.ang_copies = copies

        self.tex_note(R"\text{Cyclic quads copy } \angle B \text{ to } B_1", wait=0.8)

        # The three angles at B1 fill the straight line AC
        ac = fig.segment("A", "C", stroke_color=WHITE, stroke_width=6)
        self.play(ShowCreationThenDestruction(ac), run_time=0.9)
        line = self.add_step(
            R"\angle B + 90^\circ + \angle B = 180^\circ",
            t2c={R"\angle B": ANG_COLOR}, run_time=0.7, wait=0.3,
        )
        self.replace_step(line, R"\angle B = 45^\circ", colors={R"\angle B": ANG_COLOR}, wait=0.4)

    def circumradius(self):
        """The nine-point circle has diameter A1C1; homothety at H doubles it."""
        self.get_title()
        self.get_figure()
        fig = self.fig
        self.clear_steps(run_time=0.4)
        self.dismiss("ang_b", "ang_copies", run_time=0.4)

        # Right angle at B1: the hypotenuse is a diameter
        self.nine = self.nine_point_circle()
        n_dot = Dot(self.at("N"), radius=0.06).set_fill(NINE_COLOR)
        radius = fig.segment("N", "C1", stroke_color=NINE_COLOR, stroke_width=3)
        r9_label = Tex(R"\tfrac{13}{2}", font_size=28).set_color(NINE_COLOR)
        r9_label.next_to(radius.get_center(), UR, buff=0.06)
        self.play(Indicate(self.orthic[2], color=C13, scale_factor=1.05), run_time=0.6)
        self.play(ShowCreation(self.nine), FadeIn(n_dot, scale=0.4), run_time=1.0)
        self.play(ShowCreation(radius), FadeIn(r9_label), run_time=0.5)
        self.add_step(R"R_9 = \tfrac{13}{2}", color=NINE_COLOR, run_time=0.6, wait=0.2)
        self.tex_note(R"\text{Nine-point circle: through } A_1, B_1, C_1", wait=0.8)

        # Homothety at H, ratio 1/2: the circumcircle lands on the nine-point circle
        h_dot = Dot(self.at("H"), radius=0.065).set_fill(H_COLOR)
        h_name = Tex("H", font_size=30).set_color(H_COLOR)
        h_name.move_to(self.at("H") + 0.28 * rotate_vector(UP, 22 * DEGREES))
        self.circ = self.circumcircle()
        o_dot = Dot(self.at("O"), radius=0.06).set_fill(CIRC_COLOR)
        self.play(
            FadeIn(h_dot, scale=0.4), FadeIn(h_name),
            ShowCreation(self.circ), FadeIn(o_dot),
            run_time=0.9,
        )
        rays = VGroup(*[
            fig.dashed("H", v, stroke_color=H_COLOR, stroke_width=2, dash_length=0.06)
            for v in "ABC"
        ])
        self.play(ShowCreation(rays, lag_ratio=0.2), run_time=0.6)

        image = VGroup(
            self.circ.copy(),
            fig.polygon("A", "B", "C", stroke_color=CIRC_COLOR, stroke_width=3),
            fig.dots("A", "B", "C", radius=0.07, color=CIRC_COLOR),
        )
        self.add(image)
        self.play(image.animate.scale(0.5, about_point=self.at("H")), run_time=1.6)
        self.play(Flash(self.at("H"), color=H_COLOR, flash_radius=0.3), FadeOut(image[1:]), run_time=0.6)
        self.play(FadeOut(image[0]), self.nine.animate.set_stroke(width=6), run_time=0.4)
        self.tex_note(R"\text{Homothety at } H,\ k = \tfrac{1}{2}", wait=0.6)

        line = self.add_step(R"R = 2 R_9 = 13", color=RESULT_COLOR, font_size=42, run_time=0.6, wait=0.1)
        box = self.boxed(line)
        self.wait(0.5)
        self.r_answer = VGroup(line, box)
        self.homothety = VGroup(h_dot, h_name, rays, radius, r9_label, n_dot, self.nine, o_dot)

    def area(self):
        """OA, OB, OC meet the orthic sides at right angles, so joining O to
        the feet cuts ABC into three kites of known area."""
        self.get_title()
        self.get_figure()
        fig = self.fig
        self.clear_steps(run_time=0.4)
        self.dismiss("homothety", "rt_b1", "r_answer", run_time=0.4)
        if not hasattr(self, "circ"):
            self.circ = self.circumcircle()
            self.add(self.circ)
        o_dot = Dot(self.at("O"), radius=0.065).set_fill(CIRC_COLOR)
        o_name = Tex("O", font_size=30).set_color(CIRC_COLOR)
        o_name.move_to(self.at("O") + 0.27 * normalize(np.array([-0.87, 0.5, 0])))
        self.add(o_dot, o_name)

        # The tangent at A runs parallel to B1C1
        oa = fig.segment("O", "A", stroke_color=CIRC_COLOR, stroke_width=4)
        t_dir = normalize(rotate_vector(self.at("A") - self.at("O"), PI / 2))
        tangent = Line(self.at("A") - 1.1 * t_dir, self.at("A") + 1.1 * t_dir).set_stroke(WHITE, 3)
        self.play(ShowCreation(oa), run_time=0.5)
        self.play(GrowFromCenter(tangent), run_time=0.5)
        slide = self.orthic[1].copy().set_stroke(width=6)
        self.play(slide.animate.move_to(self.at("A")), run_time=1.0)
        self.play(FadeOut(slide), run_time=0.3)
        self.tex_note(R"\text{Tangent at } A \parallel B_1C_1 \ \Rightarrow\ OA \perp B_1C_1", wait=0.7)

        # The same holds at B and C
        ob = Line(self.at("B"), self.at("XB")).set_stroke(CIRC_COLOR, 4)
        oc = fig.segment("O", "C", stroke_color=CIRC_COLOR, stroke_width=4)
        rights = VGroup(*[
            fig.right_angle(*m, size=0.13, color=WHITE, fill_opacity=0.9)
            for m in [("A", "XA", "C1"), ("B", "XB", "C1"), ("C", "XC", "B1")]
        ])
        self.play(FadeOut(tangent), FadeIn(rights[0], scale=0.4), run_time=0.4)
        self.play(ShowCreation(ob), ShowCreation(oc), FadeIn(rights[1:], scale=0.4), run_time=0.8)
        self.play(FadeOut(self.circ), run_time=0.4)

        # Join O to the feet: three quadrilaterals with perpendicular diagonals
        spokes = VGroup(*[
            fig.segment("O", f, stroke_color=WHITE, stroke_width=2.5) for f in ["A1", "B1", "C1"]
        ])
        self.play(ShowCreation(spokes, lag_ratio=0.2), run_time=0.6)
        pieces = VGroup(
            fig.region("O", "B1", "A", "C1", color=C12, opacity=0.4),
            fig.region("O", "C1", "B", "A1", color=C13, opacity=0.4),
            fig.region("O", "A1", "C", "B1", color=C5, opacity=0.4),
        )
        self.behind(*pieces)
        self.remove(self.tri_fill, self.orthic_fill)
        self.play(LaggedStart(*[FadeIn(p) for p in pieces], lag_ratio=0.45), run_time=1.3)

        piece_line = self.add_step(
            R"S = \tfrac{1}{2} R \cdot 12 + \tfrac{1}{2} R \cdot 13 + \tfrac{1}{2} R \cdot 5",
            t2c={"12": C12, "13": C13, "5": C5}, run_time=0.7, wait=0.2,
        )
        self.tex_note(R"\text{Perpendicular diagonals: area} = \tfrac{1}{2}\, d_1 d_2", wait=0.7)
        piece_line = self.replace_step(
            piece_line, R"S = \tfrac{1}{2} R\,(12 + 13 + 5)",
            t2c={"12": C12, "13": C13, "5": C5}, wait=0.3,
        )
        self.replace_step(piece_line, R"S = 13 \cdot 15 = 195", wait=0.2)

        # Both answers, side by side
        answers = Tex(R"R = 13 \qquad S_{ABC} = 195", font_size=48).set_color(RESULT_COLOR)
        self.place_step(answers)
        answers.shift(0.15 * DOWN)
        self.play(FadeIn(answers, 0.2 * UP), run_time=0.6)
        self.boxed(answers)
        self.play(FlashAround(answers, color=RESULT_COLOR, time_width=1.5), run_time=1.1)
        self.wait(0.9)
