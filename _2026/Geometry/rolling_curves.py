from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/rolling_curves.py
#
# A curve rolling without slipping on a congruent copy of itself, starting as
# its mirror image, stays the mirror image of the fixed curve in the tangent
# line at the current contact point.  So every frame is a reflection:
#   X' = X - 2 ((X - P) . n) n      (P the contact point, n the unit normal)
#
# Circle on circle (radius R): the centre traces a circle of radius 2R, and
# the point that started at the contact traces a cardioid.
#
# Ellipse on ellipse: each focus of the rolling ellipse traces a circle of
# radius 2a about the fixed focus of the other colour -- by the reflection
# property F1, P and the reflected F2 are collinear, so the distance is
# F1P + PF2 = 2a.  The centre and the starting contact point trace ovals.

R = 1.25
A_AX, B_AX = 1.25, 0.81
C_F = np.sqrt(A_AX ** 2 - B_AX ** 2)
FIG_CENTER = 0.55 * UP

FIXED = "#E6EDF5"
ROLLING = "#58C4DD"
CENTER_TRACE = "#FFD166"
POINT_TRACE = "#FF6BD6"
FOCUS_A = "#FF9F43"          # orange, as in the reference picture
FOCUS_B = "#5BD98A"          # green


def sp(p):
    return FIG_CENTER + p[0] * RIGHT + p[1] * UP


def reflect(x, p, n):
    x = np.asarray(x, dtype=float)
    return x - 2 * np.dot(x - p, n) * n


def circle_contact(theta):
    n = np.array([np.cos(theta), np.sin(theta)])
    return R * n, n


def ellipse_contact(theta):
    p = np.array([A_AX * np.cos(theta), B_AX * np.sin(theta)])
    n = np.array([B_AX * np.cos(theta), A_AX * np.sin(theta)])
    return p, n / np.linalg.norm(n)


def glowing(points, color, width=4):
    """A bright line over a soft wide one."""
    if len(points) < 2:
        return VGroup()
    core = VMobject().set_points_smoothly([sp(p) for p in points])
    return VGroup(
        core.copy().set_stroke(color, width * 4, 0.18),
        core.set_stroke(color, width),
    )


class RollingCurves(BrandOutroMixin, ShortsScene):
    """A circle rolling around a circle, then an ellipse around an ellipse."""

    sections = ["circles", "ellipses", "outro"]

    def title(self, text, sub):
        title = Text(text, font_size=46, weight=BOLD)
        subtitle = Text(sub, font_size=26).set_color(GREY_B)
        line = Line(LEFT, RIGHT).set_width(title.get_width() * 0.5).set_stroke(ROLLING, 4)
        group = VGroup(title, line, subtitle).arrange(DOWN, buff=0.18)
        return group.move_to(5.55 * UP)

    def legend(self, rows):
        items = VGroup()
        for color, words in rows:
            chip = Dot(radius=0.09).set_fill(color)
            items.add(VGroup(chip, Text(words, font_size=26)).arrange(RIGHT, buff=0.2))
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        return items.move_to(3.85 * DOWN)

    def trace(self, theta, point_at, color, width=4):
        """Everything a point has drawn so far, as theta ran from 0."""
        def build():
            t = theta.get_value()
            if t < 1e-3:
                return VGroup()
            return glowing([point_at(s) for s in np.linspace(0, t, max(2, int(120 * t / TAU) + 2))], color, width)
        return always_redraw(build)

    # Sections

    def circles(self):
        title = self.title("Circle around a circle", "tracing its centre and a point on its rim")
        self.play(FadeIn(title[0], 0.2 * DOWN), ShowCreation(title[1]), FadeIn(title[2]), run_time=0.9)

        fixed = Circle(radius=R).move_to(sp((0, 0))).set_stroke(FIXED, 4)
        self.play(ShowCreation(fixed), run_time=0.8)

        theta = ValueTracker(0)
        start = np.array([R, 0.0])

        def center_at(t):
            p, n = circle_contact(t)
            return reflect((0, 0), p, n)

        def point_at(t):
            p, n = circle_contact(t)
            return reflect(start, p, n)

        rolling = always_redraw(lambda: Circle(radius=R).move_to(sp(center_at(theta.get_value()))).set_stroke(
            ROLLING, 4).set_fill(ROLLING, 0.1))
        spoke = always_redraw(lambda: Line(
            sp(center_at(theta.get_value())), sp(point_at(theta.get_value()))).set_stroke(ROLLING, 2.5))
        dots = always_redraw(lambda: VGroup(
            Dot(sp(center_at(theta.get_value())), radius=0.08).set_fill(CENTER_TRACE),
            Dot(sp(point_at(theta.get_value())), radius=0.09).set_fill(POINT_TRACE),
        ))
        contact = always_redraw(lambda: Dot(sp(circle_contact(theta.get_value())[0]), radius=0.05).set_fill(WHITE))
        centre_path = self.trace(theta, center_at, CENTER_TRACE)
        point_path = self.trace(theta, point_at, POINT_TRACE, 5)

        self.play(FadeIn(rolling), FadeIn(spoke), FadeIn(dots), FadeIn(contact), run_time=0.8)
        self.add(centre_path, point_path, rolling, spoke, dots, contact)
        legend = self.legend([(CENTER_TRACE, "centre"), (POINT_TRACE, "point on the rim")])
        self.play(FadeIn(legend, lag_ratio=0.3), run_time=0.6)
        self.play(theta.animate.set_value(TAU), run_time=8.0, rate_func=smooth)

        # Name what was drawn
        cardioid = VMobject().set_points_smoothly([sp(point_at(t)) for t in np.linspace(0, TAU, 200)])
        cardioid.set_stroke(width=0).set_fill(POINT_TRACE, 0.14)
        names = self.legend([
            (CENTER_TRACE, "centre: a circle of radius 2R"),
            (POINT_TRACE, "point: a cardioid"),
        ])
        self.play(FadeIn(cardioid), ReplacementTransform(legend, names), run_time=0.9)
        self.play(FadeOut(VGroup(rolling, spoke)), run_time=0.5)
        self.wait(1.6)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m is not self.frame])), run_time=0.6)

    def ellipses(self):
        title = self.title("Ellipse around an ellipse", "the same roll, a new surprise")
        self.play(FadeIn(title[0], 0.2 * DOWN), ShowCreation(title[1]), FadeIn(title[2]), run_time=0.9)

        fixed = Ellipse(width=2 * A_AX, height=2 * B_AX).move_to(sp((0, 0))).set_stroke(FIXED, 4)
        foci = VGroup(
            Dot(sp((-C_F, 0)), radius=0.08).set_fill(FOCUS_A),
            Dot(sp((C_F, 0)), radius=0.08).set_fill(FOCUS_B),
        )
        self.play(ShowCreation(fixed), FadeIn(foci, scale=0.5), run_time=0.9)

        theta = ValueTracker(0)
        outline = [np.array([A_AX * np.cos(t), B_AX * np.sin(t)]) for t in np.linspace(0, TAU, 120)]
        start = np.array([A_AX, 0.0])

        def mirrored(x):
            return lambda t: reflect(x, *ellipse_contact(t))

        center_at = mirrored((0, 0))
        point_at = mirrored(start)
        focus_a_at = mirrored((C_F, 0))       # circles the orange focus
        focus_b_at = mirrored((-C_F, 0))      # circles the green focus

        rolling = always_redraw(lambda: VMobject().set_points_smoothly([
            sp(reflect(q, *ellipse_contact(theta.get_value()))) for q in outline
        ]).set_stroke(ROLLING, 4).set_fill(ROLLING, 0.1))
        contact = always_redraw(lambda: Dot(sp(ellipse_contact(theta.get_value())[0]), radius=0.05).set_fill(WHITE))
        moving = always_redraw(lambda: VGroup(
            Dot(sp(center_at(theta.get_value())), radius=0.08).set_fill(CENTER_TRACE),
            Dot(sp(point_at(theta.get_value())), radius=0.09).set_fill(POINT_TRACE),
        ))
        moving_foci = always_redraw(lambda: VGroup(
            Dot(sp(focus_a_at(theta.get_value())), radius=0.08).set_fill(FOCUS_A),
            Dot(sp(focus_b_at(theta.get_value())), radius=0.08).set_fill(FOCUS_B),
        ))
        self.play(FadeIn(rolling), FadeIn(contact), FadeIn(moving), run_time=0.8)

        # First roll: the centre and a point on the edge
        legend = self.legend([(CENTER_TRACE, "centre"), (POINT_TRACE, "point on the edge")])
        paths = VGroup(self.trace(theta, center_at, CENTER_TRACE), self.trace(theta, point_at, POINT_TRACE, 5))
        self.add(paths, rolling, contact, moving)
        self.play(FadeIn(legend, lag_ratio=0.3), run_time=0.5)
        self.play(theta.animate.set_value(TAU), run_time=7.5, rate_func=smooth)
        for path in paths:
            path.clear_updaters()
        self.wait(0.6)

        # Second roll: now watch the foci
        self.play(
            paths.animate.set_stroke(opacity=0.12),
            FadeOut(moving),
            FadeIn(moving_foci),
            FadeOut(legend),
            run_time=0.7,
        )
        theta.set_value(0)
        legend = self.legend([(FOCUS_A, "one focus"), (FOCUS_B, "the other focus")])
        focus_paths = VGroup(self.trace(theta, focus_a_at, FOCUS_A), self.trace(theta, focus_b_at, FOCUS_B))
        self.add(focus_paths, rolling, contact, moving_foci, foci)
        self.play(FadeIn(legend, lag_ratio=0.3), run_time=0.5)
        self.play(theta.animate.set_value(TAU), run_time=7.5, rate_func=smooth)
        for path in focus_paths:
            path.clear_updaters()

        # They are circles, of radius 2a, about the fixed foci
        radii = always_redraw(lambda: VGroup(
            Line(sp((-C_F, 0)), sp(focus_a_at(theta.get_value()))).set_stroke(FOCUS_A, 2.5),
            Line(sp((C_F, 0)), sp(focus_b_at(theta.get_value()))).set_stroke(FOCUS_B, 2.5),
        ))
        def label_spot(f, g):
            f, g = sp(f), sp(g)
            along = normalize(g - f)
            return f + 0.8 * (g - f) + 0.26 * rotate_vector(along, PI / 2)

        tags = always_redraw(lambda: VGroup(*[
            Tex("2a", font_size=30).set_color(color).move_to(label_spot(f, center(theta.get_value())))
            for f, center, color in [((-C_F, 0), focus_a_at, FOCUS_A), ((C_F, 0), focus_b_at, FOCUS_B)]
        ]))
        names = self.legend([
            (FOCUS_A, "each focus: a circle of radius 2a"),
            (FOCUS_B, "centred on a focus of the fixed ellipse"),
        ])
        self.play(ReplacementTransform(legend, names), run_time=0.6)
        self.add(radii, tags, rolling, contact, moving_foci, foci)
        self.play(theta.animate.set_value(TAU + 1.25), run_time=2.0)
        self.play(
            LaggedStart(*[Indicate(p, color=c, scale_factor=1.03) for p, c in zip(focus_paths, [FOCUS_A, FOCUS_B])], lag_ratio=0.3),
            run_time=1.2,
        )
        self.wait(2.0)
