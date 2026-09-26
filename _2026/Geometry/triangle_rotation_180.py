from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/triangle_rotation_180.py
#
# Triangle A(3; 7), B(-4; 2), C(5; 1) turned 180 degrees about the origin.
# R(180) = [[cos 180, -sin 180], [sin 180, cos 180]] = [[-1, 0], [0, -1]], so
# (x; y) -> (-x; -y):  A'(-3; -7), B'(4; -2), C'(-5; -1).  A half turn is a
# reflection in the origin: O is the midpoint of AA', BB' and CC'.

POINTS = {"A": (3, 7), "B": (-4, 2), "C": (5, 1)}
ORIGINAL = "#58C4DD"
ROTATED = "#FF9F43"
TURN = YELLOW


class TriangleRotation180(MockTestShort):
    """A half turn about the origin, by the rotation matrix."""

    test = ""
    card_top_buff = 0.6
    step_buff = 0.34

    problem_tex = (
        R"\text{Rotate } \triangle ABC \text{ by } 180^\circ \text{ about } O.\\"
        R"A(3;\,7),\ B(-4;\,2),\ C(5;\,1)\\"
        R"\text{Find } A',\,B',\,C'."
    )

    sections = ["pose", "figure", "matrix", "rotate", "coordinates", "midpoints", "outro"]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = self.get_plane().get_bottom()[1] - 0.35
        return card

    def make_plane(self):
        plane = NumberPlane(
            x_range=(-6, 6, 1), y_range=(-8, 8, 1), width=12 * 0.38, height=16 * 0.38,
            background_line_style=dict(stroke_color="#3A4A5C", stroke_width=1, stroke_opacity=0.6),
            faded_line_ratio=1,
        )
        plane.axes.set_stroke(GREY_A, 2)
        plane.move_to(0.7 * UP)
        return plane

    def get_plane(self):
        if not hasattr(self, "_plane"):
            self._plane = self.make_plane()
        return self._plane

    def p(self, x, y):
        return self.get_plane().c2p(x, y)

    def triangle(self, pts, color):
        return Polygon(*[self.p(*q) for q in pts]).set_stroke(color, 3).set_fill(color, 0.3)

    def vertex(self, name, xy, color, direction):
        text = Rf"{name}({xy[0]};\,{xy[1]})"
        return VGroup(
            Dot(self.p(*xy), radius=0.06).set_fill(color),
            Tex(text, font_size=26).set_color(color).next_to(self.p(*xy), direction, buff=0.08),
        )

    # Sections

    def figure(self):
        self.get_card()
        plane = self.get_plane()
        names = VGroup(
            Tex("x", font_size=28).next_to(plane.c2p(6, 0), UP, buff=0.08),
            Tex("y", font_size=28).next_to(plane.c2p(0, 8), RIGHT, buff=0.08),
            Tex("O", font_size=26).next_to(plane.c2p(0, 0), DL, buff=0.05),
        ).set_color(GREY_A)
        self.play(ShowCreation(plane, lag_ratio=0.02), FadeIn(names), run_time=1.3)

        tri = self.triangle(POINTS.values(), ORIGINAL)
        dirs = {"A": UR, "B": LEFT, "C": RIGHT}
        labels = VGroup(*[self.vertex(n, xy, ORIGINAL, dirs[n]) for n, xy in POINTS.items()])
        self.play(ShowCreation(tri), LaggedStart(*[FadeIn(l, scale=0.6) for l in labels], lag_ratio=0.25), run_time=1.3)
        self.set_state("figure", VGroup(plane, names))
        self.set_state("original", VGroup(tri, labels))

    def matrix(self):
        self.lazy("figure", lambda: VGroup(self.get_plane()))
        line = self.add_step(
            R"R(\theta) = \begin{pmatrix}\cos\theta & -\sin\theta\\ \sin\theta & \cos\theta\end{pmatrix}",
            font_size=36, wait=0.4,
        )
        self.note("Rotating about the origin by θ:\nmultiply every point by R(θ).", wait=1.3)
        self.replace_step(
            line,
            R"R(180^\circ) = \begin{pmatrix}\cos 180^\circ & -\sin 180^\circ\\ \sin 180^\circ & \cos 180^\circ\end{pmatrix}"
            R" = \begin{pmatrix}-1 & 0\\ 0 & -1\end{pmatrix}",
            font_size=34, wait=1.0,
        )

    def rotate(self):
        original = self.lazy("original", VGroup)
        origin = self.p(0, 0)

        # Each vertex swings half way round a circle about O
        paths = VGroup(*[
            DashedVMobject(Arc(
                start_angle=angle_of_vector(self.p(*xy) - origin), angle=PI,
                radius=get_norm(self.p(*xy) - origin), arc_center=origin,
            ), num_dashes=40).set_stroke(TURN, 2, 0.8)
            for xy in POINTS.values()
        ])
        turning = original[0].copy().set_stroke(ROTATED, 3).set_fill(ROTATED, 0.3)
        sweep = ValueTracker(0)
        dial = always_redraw(lambda: Arc(0, sweep.get_value(), radius=0.35, arc_center=origin).set_stroke(TURN, 4))
        dial_label = always_redraw(lambda: Integer(int(round(sweep.get_value() / DEGREES)), unit=R"^\circ", font_size=28)
                                   .set_color(TURN).next_to(origin, UR, buff=0.3))
        self.add(dial, dial_label)
        self.play(
            Rotate(turning, PI, about_point=origin),
            *[ShowCreation(pth) for pth in paths],
            sweep.animate.set_value(PI),
            run_time=3.2,
        )
        self.play(FadeOut(dial), FadeOut(dial_label), run_time=0.4)
        self.set_state("rotated", turning)
        self.set_state("paths", paths)

    def coordinates(self):
        steps = self.steps()
        images = {"A": (-3, -7), "B": (4, -2), "C": (-5, -1)}

        # One vertex by the matrix, then the rule for all
        work = self.add_step(
            R"\begin{pmatrix}-1 & 0\\ 0 & -1\end{pmatrix}\begin{pmatrix}3\\ 7\end{pmatrix}"
            R" = \begin{pmatrix}-3\\ -7\end{pmatrix}",
            font_size=34, wait=0.4,
        )
        dirs = {"A": DL, "B": RIGHT, "C": LEFT}
        new_labels = VGroup(*[self.vertex(n + "'", images[n], ROTATED, dirs[n]) for n in "ABC"])
        self.play(TransformFromCopy(work[-6:], new_labels[0]), run_time=1.0)
        self.note("Each coordinate just changes sign.", wait=1.0)
        rule = self.replace_step(work, R"(x;\,y) \longmapsto (-x;\,-y)", font_size=40, wait=0.4)
        self.play(LaggedStart(*[FadeIn(l, scale=0.6) for l in new_labels[1:]], lag_ratio=0.4), run_time=1.0)
        self.set_state("new_labels", new_labels)

    def midpoints(self):
        origin = self.p(0, 0)
        images = {"A": (-3, -7), "B": (4, -2), "C": (-5, -1)}

        # A half turn is a reflection through O: O halves every segment
        chords = VGroup(*[
            DashedLine(self.p(*POINTS[n]), self.p(*images[n]), dash_length=0.08).set_stroke(WHITE, 2)
            for n in "ABC"
        ])
        self.play(FadeOut(self.lazy("paths", VGroup)), ShowCreation(chords, lag_ratio=0.3), run_time=1.2)
        self.play(Flash(origin, color=TURN, flash_radius=0.25), run_time=0.7)
        self.note("O is the midpoint of AA', BB' and CC':\na half turn is a reflection through O.", wait=1.4)
        # The matrix has done its job: lift the rule up and finish under it
        steps = self.steps()
        if len(steps) >= 2:
            self.play(
                FadeOut(steps[0]), FadeOut(chords),
                steps[1].animate.set_y(self.steps_top_y - steps[1].get_height() / 2),
                run_time=0.6,
            )
            steps.set_submobjects(list(steps[1:]))
        else:
            self.play(FadeOut(chords), run_time=0.4)
        self.conclude(R"A'(-3;\,-7),\ \ B'(4;\,-2),\ \ C'(-5;\,-1)", font_size=40, wait=1.5)
