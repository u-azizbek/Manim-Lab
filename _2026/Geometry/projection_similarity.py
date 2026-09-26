from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/projection_similarity.py
#
# a = proj_v(u) = 2v and b = proj_u(v) = u/6.  With |u| = k|v|, find k.
#
# From O draw v = OB and u = OA.  Dropping perpendiculars: the foot P1 from A
# gives OP1 = |a| = 2|v|, the foot P2 from B gives OP2 = |b| = |u|/6.  The right
# triangles OP1A and OP2B share the angle theta at O, so they are similar and
#   OP1 / OA = OP2 / OB  ->  2|v| / |u| = (|u|/6) / |v|  ->  |u|^2 = 12 |v|^2,
# k = 2 sqrt 3.  (Then cos theta = 1/sqrt 3.)  The figure is drawn to scale:
# reflecting OP2B in the bisector of theta and scaling by k lands it on OP1A.

K = 2 * np.sqrt(3)
THETA = np.arccos(1 / np.sqrt(3))
V_LEN = 1.75
O_PT = np.array([-1.75, -1.95, 0])
V_DIR = RIGHT
U_DIR = np.array([np.cos(THETA), np.sin(THETA), 0])

B_PT = O_PT + V_LEN * V_DIR
A_PT = O_PT + K * V_LEN * U_DIR
P1 = O_PT + 2 * V_LEN * V_DIR
P2 = O_PT + (K * V_LEN / 6) * U_DIR

V_COLOR = "#58C4DD"
U_COLOR = "#FF9F43"
A_COLOR = "#5BD98A"
B_COLOR = "#FF6BD6"
ANGLE = YELLOW


class ProjectionSimilarity(MockTestShort):
    """k from two vector projections, by similar right triangles."""

    test = ""
    card_top_buff = 0.6
    step_buff = 0.36

    problem_tex = (
        R"\vec a = \mathrm{proj}_{\vec v}\,\vec u = 2\vec v\\"
        R"\vec b = \mathrm{proj}_{\vec u}\,\vec v = \tfrac{1}{6}\vec u\\"
        R"|\vec u| = k\,|\vec v|.\ \ \text{Find } k."
    )

    sections = ["pose", "vectors", "project_u", "project_v", "similar", "solve", "outro"]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = -2.9
        return card

    def arrow(self, start, end, color, width=6):
        return Arrow(start, end, buff=0, thickness=width / 1.5).set_color(color)

    def corner(self, at, d1, d2, size=0.2, color=WHITE):
        return VMobject().set_points_as_corners([
            at + size * d1, at + size * (d1 + d2), at + size * d2,
        ]).set_stroke(color, 2.5)

    def dot_label(self, point, text, direction, color=WHITE):
        return VGroup(
            Dot(point, radius=0.06).set_fill(color),
            Tex(text, font_size=32).set_color(color).next_to(point, direction, buff=0.1),
        )

    # Sections

    def vectors(self):
        self.get_card()
        o = self.dot_label(O_PT, "O", DL)
        v = self.arrow(O_PT, B_PT, V_COLOR)
        u = self.arrow(O_PT, A_PT, U_COLOR)
        v_name = Tex(R"\vec v", font_size=38).set_color(V_COLOR).next_to(v, UP, buff=0.08).shift(0.45 * RIGHT)
        u_name = Tex(R"\vec u", font_size=38).set_color(U_COLOR).next_to(u.get_center(), UL, buff=0.08)
        b_pt = self.dot_label(B_PT, "B", DOWN, V_COLOR)
        a_pt = self.dot_label(A_PT, "A", UP, U_COLOR)
        arc = Arc(0, THETA, radius=0.5, arc_center=O_PT).set_stroke(ANGLE, 3)
        theta = Tex(R"\theta", font_size=32).set_color(ANGLE).move_to(O_PT + 0.72 * rotate_vector(RIGHT, THETA / 2))
        self.play(FadeIn(o, scale=0.5), run_time=0.4)
        self.play(GrowArrow(v), FadeIn(v_name), FadeIn(b_pt), run_time=0.7)
        self.play(GrowArrow(u), FadeIn(u_name), FadeIn(a_pt), run_time=0.8)
        self.play(ShowCreation(arc), FadeIn(theta), run_time=0.5)
        self.set_state("base", VGroup(o, v, u, v_name, u_name, b_pt, a_pt, arc, theta))

    def project_u(self):
        base = self.lazy("base", VGroup)
        v_line = DashedLine(O_PT, O_PT + 3.2 * V_LEN * V_DIR, dash_length=0.08).set_stroke(V_COLOR, 2)
        drop = DashedLine(A_PT, P1, dash_length=0.08).set_stroke(WHITE, 2.5)
        mark = self.corner(P1, LEFT, UP)
        p1 = self.dot_label(P1, R"P_1", DR, A_COLOR)
        self.play(ShowCreation(v_line), run_time=0.5)
        self.play(ShowCreation(drop), run_time=0.7)
        self.play(ShowCreation(mark), FadeIn(p1), run_time=0.4)

        a = self.arrow(O_PT, P1, A_COLOR, 9)
        a_name = Tex(R"\vec a = 2\vec v", font_size=34).set_color(A_COLOR).next_to(Line(O_PT, P1), DOWN, buff=0.42)
        self.add(a, base[1])
        self.play(GrowArrow(a), run_time=0.8)
        self.play(FadeIn(a_name, 0.1 * DOWN), run_time=0.4)
        self.note("Projecting u onto v: drop a perpendicular\nfrom A. The green arrow is 2|v| long.", wait=1.3)
        self.set_state("proj_a", VGroup(v_line, drop, mark, p1, a, a_name))

    def project_v(self):
        base = self.lazy("base", VGroup)
        drop = DashedLine(B_PT, P2, dash_length=0.08).set_stroke(WHITE, 2.5)
        mark = self.corner(P2, -U_DIR, normalize(B_PT - P2), size=0.17)
        p2 = self.dot_label(P2, R"P_2", LEFT, B_COLOR)
        self.play(ShowCreation(drop), run_time=0.7)
        self.play(ShowCreation(mark), FadeIn(p2), run_time=0.4)
        b = self.arrow(O_PT, P2, B_COLOR, 9)
        b_name = Tex(R"\vec b = \tfrac{1}{6}\vec u", font_size=34).set_color(B_COLOR)
        b_name.next_to(p2[0], LEFT, buff=0.45).shift(0.35 * UP)
        self.add(b)
        self.play(GrowArrow(b), FadeIn(b_name, 0.1 * LEFT), run_time=0.8)
        self.note("Projecting v onto u: the pink arrow\nis |u| / 6 long.", wait=1.1)
        self.set_state("proj_b", VGroup(drop, mark, p2, b, b_name))

    def similar(self):
        # Two right triangles with the same angle theta at O
        big = Polygon(O_PT, P1, A_PT).set_stroke(A_COLOR, 3).set_fill(A_COLOR, 0.22)
        small = Polygon(O_PT, P2, B_PT).set_stroke(B_COLOR, 3).set_fill(B_COLOR, 0.4)
        self.play(FadeIn(big), run_time=0.6)
        self.play(FadeIn(small), run_time=0.6)
        self.note("Both are right triangles with angle θ at O:\nsimilar (AA).", wait=1.2)

        # Flip the small one across the bisector of theta and scale it by k
        copy = small.copy()
        bisector = rotate_vector(RIGHT, THETA / 2)
        self.play(Rotate(copy, PI, axis=bisector, about_point=O_PT), run_time=1.2)
        self.play(copy.animate.scale(K, about_point=O_PT), run_time=1.3)
        self.play(Indicate(big, color=A_COLOR, scale_factor=1.03), FadeOut(copy), run_time=0.8)
        self.set_state("triangles", VGroup(big, small))

    def solve(self):
        line = self.add_step(R"\frac{OP_1}{OA} = \frac{OP_2}{OB}", font_size=38, wait=0.6)
        line = self.replace_step(
            line,
            R"\frac{2|\vec v|}{|\vec u|} = \frac{\tfrac{1}{6}|\vec u|}{|\vec v|}",
            font_size=38, wait=0.8,
        )
        line = self.replace_step(line, R"2|\vec v|^2 = \tfrac{1}{6}|\vec u|^2", font_size=40, wait=0.6)
        line = self.replace_step(line, R"|\vec u|^2 = 12\,|\vec v|^2", font_size=40, wait=0.6)
        self.conclude(R"k = \sqrt{12} = 2\sqrt{3}", font_size=48, wait=1.5)
