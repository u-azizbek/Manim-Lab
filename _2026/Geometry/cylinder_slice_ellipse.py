from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/cylinder_slice_ellipse.py
#
# A cylinder of radius 2 is cut by a slanted plane, 10 high over A and 13 high
# over B.  The cut is an ellipse: find its area.
#
# Its semi-axes come from two special views.  From straight above, the cut
# sits exactly over the base circle, so the width across it is still 2r:
# b = r = 2.  From the side, the cut is seen edge-on as CD, the hypotenuse of
# a right triangle with legs AB = 4 and 13 - 10 = 3, so 2a = 5.  Hence
# area = pi a b = 5 pi.  Checked by measuring the cut directly, and against
# base area / cos(tilt) = 4 pi / (4/5).
#
# The figure is drawn with a hand-rolled projection driven by a view angle,
# so the video can tilt between the oblique, top and side views.  As in the
# textbook figure the lower walls are shortened, but everything from height 9
# up -- the whole cut and the 3-4-5 triangle -- is at true scale.

R = 2
H_LOW, H_HIGH = 10, 13
Z_MID = (H_LOW + H_HIGH) / 2
SLOPE = (H_HIGH - H_LOW) / (2 * R)
SQUEEZE, BREAK = 0.45, 9          # heights below BREAK are drawn at SQUEEZE

FIG_CENTER = 0.95 * UP
VIEWS = {                          # (view angle above the horizon, zoom)
    "oblique": (20, 0.62),
    "top": (90, 1.0),
    "side": (0, 0.72),
}

WALL = GREY_A
CUT = "#58C4DD"
MINOR = "#83C167"
MAJOR = "#FF9F43"
LEG_4 = "#4FD1C5"
LEG_3 = "#FF6B9A"

POINTS = {
    "A": (-R, 0, 0), "B": (R, 0, 0), "O": (0, 0, 0),
    "D": (-R, 0, H_LOW), "C": (R, 0, H_HIGH), "E": (R, 0, H_LOW),
    "M": (0, 0, Z_MID),
}


def drawn_height(z):
    return SQUEEZE * z if z <= BREAK else SQUEEZE * BREAK + (z - BREAK)


def cut_height(x):
    return Z_MID + SLOPE * x


class CylinderSliceEllipse(MockTestShort):
    """Area of a slanted cut through a cylinder, as pi a b."""

    test = ""
    card_top_buff = 0.85
    step_buff = 0.4

    problem_tex = (
        R"\text{Cylinder of radius } 2,\ \text{cut on a slant.}\\"
        R"\text{Area of the cut?}"
    )

    sections = [
        "pose",
        "draw_cylinder",
        "name_axes",
        "top_view",
        "side_view",
        "finish",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = -2.75
        return card

    # The projection

    def trackers(self):
        if not hasattr(self, "_view"):
            angle, zoom = VIEWS["oblique"]
            self._view = (ValueTracker(angle), ValueTracker(zoom))
        return self._view

    def sp(self, x, y, z):
        """A point of the solid on screen, seen from the current view angle.
        The figure is kept centred in its area however the view turns."""
        angle_t, zoom_t = self.trackers()
        phi = angle_t.get_value() * DEGREES
        zoom = zoom_t.get_value()
        py = drawn_height(z) * np.cos(phi) + y * np.sin(phi)
        # vertical extent: the front of the base to the top of the cut
        low = -R * np.sin(phi)
        top = drawn_height(Z_MID) * np.cos(phi) + np.hypot(R * SLOPE * np.cos(phi), R * np.sin(phi))
        return FIG_CENTER + zoom * (x * RIGHT + (py - (low + top) / 2) * UP)

    def at(self, name):
        return self.sp(*POINTS[name])

    def view(self, name, run_time=2.0, *extra):
        angle, zoom = VIEWS[name]
        angle_t, zoom_t = self.trackers()
        self.play(
            angle_t.animate.set_value(angle),
            zoom_t.animate.set_value(zoom),
            *extra,
            run_time=run_time,
        )

    def follow(self, mob, name, direction, buff=0.12):
        mob.add_updater(lambda m: m.next_to(self.at(name), direction, buff=buff))
        return mob.update()

    # Pieces

    def make_solid(self):
        def arc(t0, t1, z_of):
            return ParametricCurve(
                lambda t: self.sp(R * np.cos(t), R * np.sin(t), z_of(R * np.cos(t))),
                t_range=(t0, t1, 0.04),
            )

        base_front = always_redraw(lambda: arc(PI, TAU, lambda x: 0).set_stroke(WALL, 3))
        base_back = always_redraw(
            lambda: DashedVMobject(arc(0, PI, lambda x: 0), num_dashes=24).set_stroke(WALL, 2)
        )
        walls = always_redraw(lambda: VGroup(
            Line(self.at("A"), self.at("D")), Line(self.at("B"), self.at("C")),
        ).set_stroke(WALL, 3))
        diameter = always_redraw(
            lambda: DashedLine(self.at("A"), self.at("B"), dash_length=0.08).set_stroke(GREY_B, 2)
        )
        center = always_redraw(lambda: Dot(self.at("O"), radius=0.05).set_color(WHITE))
        cut = always_redraw(
            lambda: arc(0, TAU, cut_height).set_stroke(CUT, 4).set_fill(CUT, 0.3)
        )

        letters = VGroup(
            self.follow(Tex("A", font_size=32), "A", LEFT),
            self.follow(Tex("B", font_size=32), "B", RIGHT),
            self.follow(Tex("C", font_size=32), "C", UR, buff=0.08),
            self.follow(Tex("D", font_size=32), "D", UL, buff=0.08),
            self.follow(Tex("O", font_size=28), "O", DOWN, buff=0.1),
        )
        numbers = VGroup(
            Tex("10", font_size=32).add_updater(
                lambda m: m.next_to(midpoint(self.at("A"), self.at("D")), LEFT, buff=0.15)),
            Tex("13", font_size=32).add_updater(
                lambda m: m.next_to(midpoint(self.at("B"), self.at("C")), RIGHT, buff=0.15)),
            Tex("2", font_size=30).set_color(GREY_A).add_updater(
                lambda m: m.next_to(midpoint(self.at("O"), self.at("B")), UP, buff=0.08)),
        )
        numbers.update()

        solid = VGroup(base_back, base_front, walls, diameter, center, cut, letters, numbers)
        solid.base = VGroup(base_back, base_front)
        solid.walls, solid.diameter, solid.center, solid.cut = walls, diameter, center, cut
        solid.letters, solid.numbers = letters, numbers
        return solid

    def get_solid(self):
        return self.lazy("solid", self.make_solid)

    def make_axes(self):
        major = always_redraw(lambda: Line(self.at("D"), self.at("C")).set_stroke(MAJOR, 5))
        minor = always_redraw(
            lambda: Line(self.sp(0, -R, Z_MID), self.sp(0, R, Z_MID)).set_stroke(MINOR, 5)
        )
        middle = always_redraw(lambda: Dot(self.at("M"), radius=0.06).set_color(WHITE))
        axes = VGroup(major, minor, middle)
        axes.major, axes.minor = major, minor
        return axes

    def get_axes(self):
        return self.lazy("axes", self.make_axes)

    # Sections

    def draw_cylinder(self):
        self.get_card()
        solid = self.make_solid()
        self.play(ShowCreation(solid.base), ShowCreation(solid.diameter), FadeIn(solid.center), run_time=0.9)
        self.play(ShowCreation(solid.walls), run_time=0.8)
        self.play(ShowCreation(solid.cut), run_time=1.0)
        self.play(FadeIn(solid.letters, lag_ratio=0.1), FadeIn(solid.numbers, lag_ratio=0.2), run_time=0.8)
        self.set_state("solid", solid)
        self.wait(0.6)

    def name_axes(self):
        self.get_solid()
        axes = self.make_axes()
        labels = VGroup(
            Tex("2a", font_size=36).set_color(MAJOR).add_updater(
                lambda m: m.move_to(interpolate(self.at("D"), self.at("C"), 0.3) + 0.42 * UL)),
            Tex("2b", font_size=36).set_color(MINOR).add_updater(
                lambda m: m.next_to(self.sp(0, R, Z_MID), UP, buff=0.12)),
        )
        labels.update()
        self.play(ShowCreation(axes.major), FadeIn(labels[0]), run_time=0.8)
        self.play(ShowCreation(axes.minor), FadeIn(axes[2]), FadeIn(labels[1]), run_time=0.8)
        self.add_step(R"\text{Area} = \pi a b", font_size=44, wait=0.8)
        self.set_state("axes", axes)
        self.set_state("axis_names", labels)

    def top_view(self):
        solid = self.get_solid()
        axes = self.get_axes()
        names = self.lazy("axis_names", VGroup)

        # From straight above every point of the cut sits over the base circle
        self.play(FadeOut(VGroup(solid.letters, solid.numbers, names, axes.major)), run_time=0.4)
        self.view("top", 2.0)
        rim = always_redraw(lambda: ParametricCurve(
            lambda t: self.sp(R * np.cos(t), R * np.sin(t), 0), t_range=(0, TAU, 0.04),
        ).set_stroke(WHITE, 3))
        self.play(ShowCreation(rim), run_time=0.7)
        across = Tex("2b = 2r = 4", font_size=34).set_color(MINOR)
        across.add_updater(lambda m: m.next_to(self.sp(0, R, Z_MID), UP, buff=0.12))
        across.update()
        self.play(Indicate(axes.minor, color=MINOR, scale_factor=1.05), FadeIn(across), run_time=0.9)
        self.note("Seen from above, the cut covers the base circle:\nits width across is still the diameter.", wait=1.2)
        self.add_step(R"b = r = 2", color=MINOR, font_size=42, wait=0.5)
        self.play(FadeOut(rim), FadeOut(across), run_time=0.4)

    def side_view(self):
        solid = self.get_solid()
        axes = self.get_axes()

        # Turn right round to the side: the cut is now seen edge-on as DC
        self.view("side", 2.2, FadeIn(solid.letters), FadeIn(solid.numbers[:2]), FadeIn(axes.major))
        legs = always_redraw(lambda: VGroup(
            Line(self.at("D"), self.at("E")).set_stroke(LEG_4, 5),
            Line(self.at("E"), self.at("C")).set_stroke(LEG_3, 5),
        ))
        corner = always_redraw(lambda: VMobject().set_points_as_corners([
            self.at("E") + 0.18 * LEFT, self.at("E") + 0.18 * (LEFT + UP), self.at("E") + 0.18 * UP,
        ]).set_stroke(WHITE, 2))
        e_label = self.follow(Tex("E", font_size=30), "E", RIGHT, buff=0.1)
        self.play(ShowCreation(legs), ShowCreation(corner), FadeIn(e_label), run_time=0.9)

        sides = VGroup(
            Tex("4", font_size=34).set_color(LEG_4).add_updater(
                lambda m: m.next_to(midpoint(self.at("D"), self.at("E")), DOWN, buff=0.1)),
            Tex("3", font_size=34).set_color(LEG_3).add_updater(
                lambda m: m.next_to(midpoint(self.at("E"), self.at("C")), LEFT, buff=0.1)),
            Tex("5", font_size=34).set_color(MAJOR).add_updater(
                lambda m: m.move_to(midpoint(self.at("D"), self.at("C")) + 0.3 * UL)),
        )
        sides.update()
        self.play(FadeIn(sides[0]), Indicate(solid.diameter, color=LEG_4), run_time=0.7)
        self.play(FadeIn(sides[1]), run_time=0.5)
        self.play(FadeIn(sides[2]), Indicate(axes.major, color=MAJOR, scale_factor=1.03), run_time=0.7)
        self.note("DE = AB = 4 and EC = 13 - 10 = 3: Pythagoras.", wait=1.1)
        self.add_step(
            R"2a = \sqrt{4^2 + 3^2} = 5 \quad\Rightarrow\quad a = \tfrac{5}{2}",
            color=MAJOR, font_size=40, wait=0.6,
        )
        self.set_state("triangle", VGroup(legs, corner, e_label, sides))

    def finish(self):
        solid = self.get_solid()
        axes = self.get_axes()
        triangle = self.lazy("triangle", VGroup)
        steps = self.steps()

        # Back to the first view, with both semi-axes named
        self.play(FadeOut(triangle), run_time=0.4)
        self.view("oblique", 1.6)
        semi = VGroup(
            Tex(R"a = \tfrac{5}{2}", font_size=36).set_color(MAJOR).add_updater(
                lambda m: m.move_to(interpolate(self.at("M"), self.at("C"), 0.4) + 0.5 * UL)),
            Tex("b = 2", font_size=36).set_color(MINOR).add_updater(
                lambda m: m.next_to(self.sp(0, -R, Z_MID), DOWN, buff=0.22)),
        )
        semi.update()
        self.play(FadeIn(semi, lag_ratio=0.3), run_time=0.6)

        # Collapse the working into the answer
        if len(steps) >= 3:
            self.play(FadeOut(VGroup(*steps[1:]), 0.3 * UP), run_time=0.5)
            steps.set_submobjects(list(steps[:1]))
        area = self.replace_step(
            steps[0], R"\text{Area} = \pi \cdot \tfrac{5}{2} \cdot 2 = 5\pi",
            font_size=50, color=RESULT_COLOR, wait=0.2,
        ) if len(steps) else self.add_step(
            R"\text{Area} = \pi \cdot \tfrac{5}{2} \cdot 2 = 5\pi", font_size=50, color=RESULT_COLOR,
        )
        self.play(solid.cut.animate.set_fill(CUT, 0.7), run_time=0.6)
        box = SurroundingRectangle(area, color=RESULT_COLOR, buff=0.2).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(area, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.wait(1.5)
