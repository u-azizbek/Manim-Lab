from manim_imports_ext import *


GIVEN_COLOR = TEAL_B
AXIS_COLOR = BLUE_B
CIRCLE_COLOR = "#FF7AB6"
ASK_COLOR = "#FF6B8A"
GREEN_ANGLE = "#5BD98A"
RESULT_COLOR = YELLOW

HALF_D = 70.0  # half of the given 140 degrees at D


def build_points(half_d: float = HALF_D) -> dict:
    """Vertices of the figure, derived from the constraints rather than traced.

    D at the origin with the symmetry axis pointing up:
      DF = DC = FA = BC = 1 and the axis bisects the 140 degrees at D,
      angle AFD = angle BCD = 90, and E is the apex of the right isosceles
      triangle on AB.  Everything else follows.
    """
    d = np.deg2rad(half_d)
    D = np.array([0.0, 0.0])
    F = np.array([-np.sin(d), np.cos(d)])
    C = np.array([np.sin(d), np.cos(d)])
    # angle AFD = 90 with FA = 1: rotate the direction F->D by +90 degrees
    A = F + np.array([np.cos(d), np.sin(d)])
    B = np.array([-A[0], A[1]])
    # right isosceles on AB, apex on the axis below AB
    E = np.array([0.0, A[1] - abs(A[0])])
    return dict(A=A, B=B, C=C, D=D, E=E, F=F)


class KangarooAngle(GeometryShortScene):
    # Kangaroo grade 7 angle chase.  Render with:
    #   ./render.sh _2026/Geometry/kangaroo_angle_140.py
    # or one beat with:
    #   ./render.sh -s equal_radii _2026/Geometry/kangaroo_angle_140.py
    title_text = "KANGAROO . GRADE 7"
    figure_width = 6.6
    figure_center_y = 3.3
    steps_top_y = -0.7
    step_buff = 0.45

    sections = [
        "pose_problem",
        "find_symmetry",
        "angle_at_E",
        "equal_radii",
        "finish",
    ]

    # ---- the figure ----

    def make_figure(self):
        fig = GeoFigure(build_points(), line_width=4.0)
        fig.normalize(width=self.figure_width, center=self.figure_center_y * UP)
        # A point up the symmetry axis, so the two 45 degree angles at E have a
        # ray to sit against
        fig.add_point("U", fig.p("E") + 1.2 * UP)
        return fig

    def get_figure(self) -> GeoFigure:
        # not a mobject, so it is cached by hand rather than through `lazy`
        if not hasattr(self, "_figure"):
            self._figure = self.make_figure()
        return self._figure

    def make_base_figure(self):
        """Outline, congruence ticks, right angles and the two given angles."""
        fig = self.get_figure()

        outline = VGroup(
            fig.polygon("A", "B", "C", "D", "F"),
            fig.segment("A", "E"),
            fig.segment("B", "E"),
            fig.segment("F", "E"),
        )
        ticks = VGroup(
            fig.ticks("F", "A"), fig.ticks("B", "C"),
            fig.ticks("C", "D"), fig.ticks("D", "F"),
            fig.ticks("E", "A", n=2), fig.ticks("E", "B", n=2),
        )
        squares = VGroup(
            fig.right_angle("A", "E", "B", size=0.26),
            fig.right_angle("A", "F", "D", size=0.26),
            fig.right_angle("B", "C", "D", size=0.26),
        )
        given = VGroup(
            fig.angle("F", "D", "C", radius=0.62, arcs=2,
                      color=GREEN_ANGLE, fill_opacity=0.45),
            fig.angle_label("F", "D", "C", R"140^\circ", radius=0.95,
                            font_size=34, color=GREEN_ANGLE, outside=True),
        )
        asked = VGroup(
            fig.angle("A", "F", "E", radius=0.62, color=ASK_COLOR, fill_opacity=0.5),
            fig.angle_label("A", "F", "E", "?", radius=0.95,
                            font_size=42, color=ASK_COLOR),
        )
        labels = fig.labels(
            {"A": UL, "B": UR, "C": RIGHT, "D": DOWN, "F": LEFT},
            font_size=30, color=GREY_B, buff=0.30,
        )
        labels.add(fig.label("E", direction=RIGHT, font_size=30,
                             color=GREY_B, buff=0.26))

        group = VGroup(outline, ticks, given, asked, squares, labels)
        group.outline, group.ticks, group.squares = outline, ticks, squares
        group.given, group.asked, group.labels = given, asked, labels
        return group

    def get_base_figure(self):
        return self.lazy("figure", self.make_base_figure)

    # ---- sections ----

    def pose_problem(self):
        title = self.get_title()
        figure = self.make_base_figure()

        self.play(FadeIn(title, 0.2 * DOWN), run_time=0.7)
        self.play(ShowCreation(figure.outline, lag_ratio=0.15), run_time=2.0)
        self.play(
            FadeIn(figure.ticks, lag_ratio=0.12),
            FadeIn(figure.labels, lag_ratio=0.12),
            run_time=1.2,
        )
        self.play(FadeIn(figure.squares, lag_ratio=0.2), run_time=0.8)
        self.play(Write(figure.given), run_time=1.0)
        self.play(FadeIn(figure.asked), run_time=0.8)
        self.play(FlashAround(figure.asked, color=ASK_COLOR, time_width=1.5), run_time=1.3)
        self.wait(0.5)
        self.set_state("figure", figure)

    def find_symmetry(self):
        fig = self.get_figure()
        self.get_base_figure()

        axis = fig.dashed("U", "D", stroke_color=AXIS_COLOR, stroke_width=3)

        halves = VGroup(
            fig.angle_label("A", "E", "U", R"45^\circ", radius=0.62,
                            font_size=27, color=AXIS_COLOR),
            fig.angle_label("U", "E", "B", R"45^\circ", radius=0.62,
                            font_size=27, color=AXIS_COLOR),
            fig.angle_label("F", "D", "E", R"70^\circ", radius=0.95,
                            font_size=27, color=AXIS_COLOR),
            fig.angle_label("E", "D", "C", R"70^\circ", radius=0.95,
                            font_size=27, color=AXIS_COLOR),
        )

        self.play(ShowCreation(axis), run_time=1.0)
        self.add_step(R"\text{symmetric about } DE", color=AXIS_COLOR)
        self.play(FadeIn(halves, lag_ratio=0.2), run_time=1.2)
        self.wait(0.6)
        self.set_state("axis", VGroup(axis, halves))

    def angle_at_E(self):
        fig = self.get_figure()
        self.get_base_figure()
        self.lazy("axis", self.make_axis)

        arc = fig.angle("A", "E", "D", radius=0.5, color=RESULT_COLOR, stroke_width=4)
        label = fig.angle_label("A", "E", "D", R"135^\circ", radius=0.80,
                                font_size=30, color=RESULT_COLOR,
                                offset=0.46 * UP + 0.10 * LEFT)

        self.play(ShowCreation(arc), FadeIn(label), run_time=1.0)
        self.add_step(R"\angle AED = 45^\circ + 90^\circ = 135^\circ")
        self.wait(0.5)
        self.set_state("angle_E", VGroup(arc, label))

    def equal_radii(self):
        fig = self.get_figure()
        self.get_base_figure()
        self.lazy("axis", self.make_axis)
        self.lazy("angle_E", self.make_angle_E)

        circle = fig.circle("F", "A", stroke_color=CIRCLE_COLOR, stroke_width=3)
        radii = VGroup(
            fig.segment("F", "A", stroke_color=CIRCLE_COLOR, stroke_width=5),
            fig.segment("F", "D", stroke_color=CIRCLE_COLOR, stroke_width=5),
            fig.segment("F", "E", stroke_color=CIRCLE_COLOR, stroke_width=5),
        )
        hits = fig.dots("A", "D", "E", radius=0.07, color=CIRCLE_COLOR)

        self.play(ShowCreation(circle), run_time=1.5)
        self.play(FadeIn(hits, lag_ratio=0.25), run_time=0.8)
        self.play(ShowCreation(radii, lag_ratio=0.25), run_time=1.2)
        self.add_step(R"FA = FD = FE", color=CIRCLE_COLOR, font_size=42)
        self.wait(0.4)
        self.play(FadeOut(circle), FadeOut(hits), run_time=0.7)
        self.set_state("radii", radii)

    def finish(self):
        fig = self.get_figure()
        self.get_base_figure()
        self.lazy("axis", self.make_axis)
        self.lazy("angle_E", self.make_angle_E)
        self.lazy("radii", self.make_radii)

        triangle = fig.region("F", "E", "D", color=GREEN_ANGLE, opacity=0.3)
        base_angles = fig.angle_label("F", "E", "D", R"70^\circ", radius=0.66,
                                      font_size=27, color=GREEN_ANGLE,
                                      offset=0.12 * DOWN)
        apex = fig.angle_label("D", "F", "E", R"40^\circ", radius=0.72,
                              font_size=28, color=GREEN_ANGLE)

        self.play(FadeIn(triangle), run_time=0.8)
        self.play(FadeIn(base_angles), run_time=0.7)
        self.play(FadeIn(apex, scale=1.2), run_time=0.8)
        self.add_step(R"\angle DFE = 180^\circ - 70^\circ - 70^\circ = 40^\circ",
                      color=GREEN_ANGLE)
        self.wait(0.4)

        answer = self.add_step(R"? = 90^\circ - 40^\circ = 50^\circ",
                               color=RESULT_COLOR, font_size=46, wait=0)
        box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.22)
        box.set_stroke(width=4)

        solved = fig.angle_label("A", "F", "E", R"50^\circ", radius=0.88,
                                 font_size=36, color=RESULT_COLOR)
        asked_label = self.get_base_figure().asked[1]

        self.play(ShowCreation(box), run_time=0.5)
        self.play(FadeTransform(asked_label, solved), run_time=0.9)
        self.play(FlashAround(answer, color=RESULT_COLOR, time_width=1.5), run_time=1.4)
        self.wait(1.8)

    # ---- static rebuilds, so any section renders on its own ----

    def make_axis(self):
        fig = self.get_figure()
        axis = fig.dashed("U", "D", stroke_color=AXIS_COLOR, stroke_width=3)
        halves = VGroup(
            fig.angle_label("A", "E", "U", R"45^\circ", radius=0.62, font_size=27, color=AXIS_COLOR),
            fig.angle_label("U", "E", "B", R"45^\circ", radius=0.62, font_size=27, color=AXIS_COLOR),
            fig.angle_label("F", "D", "E", R"70^\circ", radius=0.95, font_size=27, color=AXIS_COLOR),
            fig.angle_label("E", "D", "C", R"70^\circ", radius=0.95, font_size=27, color=AXIS_COLOR),
        )
        return VGroup(axis, halves)

    def make_angle_E(self):
        fig = self.get_figure()
        return VGroup(
            fig.angle("A", "E", "D", radius=0.5, color=RESULT_COLOR, stroke_width=4),
            fig.angle_label("A", "E", "D", R"135^\circ", radius=0.80,
                            font_size=30, color=RESULT_COLOR,
                            offset=0.46 * UP + 0.10 * LEFT),
        )

    def make_radii(self):
        fig = self.get_figure()
        return VGroup(
            fig.segment("F", "A", stroke_color=CIRCLE_COLOR, stroke_width=5),
            fig.segment("F", "D", stroke_color=CIRCLE_COLOR, stroke_width=5),
            fig.segment("F", "E", stroke_color=CIRCLE_COLOR, stroke_width=5),
        )
