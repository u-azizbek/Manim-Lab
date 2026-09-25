from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/spinning_ellipses.py
#
# One ellipse, turned in equal steps about a fixed point, leaving a coloured
# copy at each step.
#   about its centre: every point is between b and a from the pivot, and each
#     copy touches both circles (at the ends of its axes), so the copies fill
#     the ring b <= r <= a.  Half a turn is enough: the ellipse is symmetric.
#   about a focus:    the distance from a focus runs from a - c to a + c
#     (c = sqrt(a^2 - b^2)), so the copies fill the ring a - c <= r <= a + c.

FIG_CENTER = 0.35 * UP
RAINBOW = ["#FF5C5C", "#FF9F43", "#FFD166", "#5BD98A", "#4FD1C5", "#58C4DD", "#7F8CFF", "#C39BFF", "#FF6BD6"]

A_CENTRE, B_CENTRE = 3.35, 1.7
A_FOCUS, B_FOCUS = 1.95, 1.2
C_FOCUS = np.sqrt(A_FOCUS ** 2 - B_FOCUS ** 2)


class SpinningEllipses(BrandOutroMixin, ShortsScene):
    """Rosettes of rotated ellipses: about the centre, then about a focus."""

    sections = ["about_centre", "about_focus", "outro"]

    def title(self, text, sub):
        title = Text(text, font_size=46, weight=BOLD)
        subtitle = Text(sub, font_size=26).set_color(GREY_B)
        line = Line(LEFT, RIGHT).set_width(title.get_width() * 0.5).set_stroke(RAINBOW[5], 4)
        return VGroup(title, line, subtitle).arrange(DOWN, buff=0.18).move_to(5.55 * UP)

    def caption(self, text, y=-4.35):
        return Text(text, font_size=28).set_color(GREY_A).move_to(y * UP)

    def spin(self, ellipse, pivot, copies, total_angle, run_time):
        """Turn `ellipse` about `pivot`, leaving a coloured copy every step."""
        colors = color_gradient(RAINBOW, copies)
        step = total_angle / copies
        stamps = VGroup()
        for k in range(copies):
            stamp = ellipse.copy().set_stroke(colors[k], 3.5, 1)
            stamps.add(stamp)
            self.add(stamp, ellipse)
            self.play(Rotate(ellipse, step, about_point=pivot), run_time=run_time / copies, rate_func=linear)
        return stamps

    def envelope(self, radii, names, pivot):
        rings = VGroup(*[
            DashedVMobject(Circle(radius=r), num_dashes=int(24 * r) + 12).set_stroke(WHITE, 2.5).move_to(pivot)
            for r in radii
        ])
        spokes = VGroup()
        labels = VGroup()
        for r, name, angle in zip(radii, names, [-PI / 2 - 0.35, -PI / 2 + 0.35]):
            end = pivot + r * np.array([np.cos(angle), np.sin(angle), 0])
            spokes.add(Line(pivot, end).set_stroke(WHITE, 2.5))
            label = Tex(name, font_size=40).move_to(
                pivot + 0.62 * (end - pivot) + 0.32 * rotate_vector(normalize(end - pivot), PI / 2))
            labels.add(label.add_background_rectangle(color=BLACK, opacity=0.85, buff=0.06))
        return rings, spokes, labels

    # Sections

    def about_centre(self):
        title = self.title("Spin an ellipse", "about its centre, leaving a copy every 10°")
        self.play(FadeIn(title[0], 0.2 * DOWN), ShowCreation(title[1]), FadeIn(title[2]), run_time=0.9)

        pivot = FIG_CENTER
        ellipse = Ellipse(width=2 * A_CENTRE, height=2 * B_CENTRE).move_to(pivot).set_stroke(WHITE, 5)
        center = Dot(pivot, radius=0.07).set_fill(WHITE)
        axes = VGroup(
            Line(pivot, pivot + A_CENTRE * RIGHT).set_stroke(RAINBOW[0], 4),
            Line(pivot, pivot + B_CENTRE * UP).set_stroke(RAINBOW[5], 4),
        )
        axis_names = VGroup(
            Tex("a", font_size=38).set_color(RAINBOW[0]).next_to(axes[0], DOWN, buff=0.1),
            Tex("b", font_size=38).set_color(RAINBOW[5]).next_to(axes[1], LEFT, buff=0.1),
        )
        self.play(ShowCreation(ellipse), FadeIn(center, scale=0.5), run_time=1.0)
        self.play(ShowCreation(axes, lag_ratio=0.4), FadeIn(axis_names), run_time=0.8)
        self.wait(0.4)
        self.play(FadeOut(VGroup(axes, axis_names)), run_time=0.4)

        # Half a turn, 18 copies
        stamps = self.spin(ellipse, pivot, 18, PI, 7.2)
        self.play(FadeOut(ellipse), run_time=0.4)

        # Every copy stays between two circles, and touches both
        rings, spokes, labels = self.envelope([B_CENTRE, A_CENTRE], ["b", "a"], pivot)
        self.play(ShowCreation(rings, lag_ratio=0.3), run_time=1.2)
        self.play(ShowCreation(spokes), FadeIn(labels), run_time=0.7)
        note = self.caption("Every copy touches the circle of radius b\nand the circle of radius a.")
        self.play(FadeIn(note, 0.15 * UP), run_time=0.5)
        self.wait(1.4)

        # The whole rosette, turning
        self.play(FadeOut(VGroup(rings, spokes, labels, note)), run_time=0.5)
        self.play(Rotate(stamps, PI / 3, about_point=pivot), run_time=3.0, rate_func=smooth)
        self.play(FadeOut(VGroup(stamps, center, title)), run_time=0.6)

    def about_focus(self):
        title = self.title("Spin it about a focus", "now a full turn, a copy every 15°")
        self.play(FadeIn(title[0], 0.2 * DOWN), ShowCreation(title[1]), FadeIn(title[2]), run_time=0.9)

        # The pivot is the left focus
        pivot = FIG_CENTER
        ellipse = Ellipse(width=2 * A_FOCUS, height=2 * B_FOCUS).set_stroke(WHITE, 5)
        ellipse.move_to(pivot + C_FOCUS * RIGHT)
        foci = VGroup(
            Dot(pivot, radius=0.08).set_fill(RAINBOW[2]),
            Dot(pivot + 2 * C_FOCUS * RIGHT, radius=0.06).set_fill(GREY_B),
        )
        self.play(ShowCreation(ellipse), FadeIn(foci, scale=0.5), run_time=1.0)
        self.play(Flash(pivot, color=RAINBOW[2], flash_radius=0.3), run_time=0.7)
        self.play(FadeOut(foci[1]), run_time=0.3)

        stamps = self.spin(ellipse, pivot, 24, TAU, 8.4)
        self.play(FadeOut(ellipse), run_time=0.4)

        rings, spokes, labels = self.envelope(
            [A_FOCUS - C_FOCUS, A_FOCUS + C_FOCUS], ["a - c", "a + c"], pivot,
        )
        labels[0].next_to(rings[0], LEFT, buff=0.12)
        self.play(ShowCreation(rings, lag_ratio=0.3), run_time=1.2)
        self.play(ShowCreation(spokes), FadeIn(labels), run_time=0.7)
        note = self.caption("From a focus, the ellipse is between\na - c and a + c away.")
        self.play(FadeIn(note, 0.15 * UP), run_time=0.5)
        self.wait(1.4)

        self.play(FadeOut(VGroup(rings, spokes, labels, note)), run_time=0.5)
        self.play(Rotate(stamps, PI / 2, about_point=pivot), run_time=3.0, rate_func=smooth)
        self.wait(0.6)
