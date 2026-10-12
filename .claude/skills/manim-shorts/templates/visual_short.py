from manim_imports_ext import *


# Render with:
#   ./render.sh .claude/skills/manim-shorts/templates/visual_short.py
#
# TEMPLATE for a "theorem / proof without words / simulation" short: no
# problem card, a title over one big live figure, a caption, a boxed payoff.
# Copy it to _2026/<Topic>/<snake_name>.py and replace everything.
#
# Inscribed angle theorem: for A, B fixed on a circle, the angle APB is the
# same for every P on the major arc -- half the central angle AOB.
# Here AOB = 100 degrees, so APB = 50 degrees wherever P goes.
# Checked: angle APB at P = 10, 60, 150, 200 degrees all 50.000.

RADIUS = 2.9
CENTER = 0.6 * UP
A_DEG, B_DEG = -130, -30           # central angle AOB = 100

CIRCLE_C = "#58C4DD"
INSCRIBED_C = "#FFD166"            # the angle at P
CENTRAL_C = "#FF6B9A"              # the angle at O


def on_circle(deg):
    return CENTER + RADIUS * np.array([np.cos(deg * DEG), np.sin(deg * DEG), 0])


def angle_arc(p, a, b, radius=0.55):
    """The arc marking angle APB, whichever way round P happens to be."""
    start = angle_of_vector(a - p)
    sweep = (angle_of_vector(b - p) - start + PI) % TAU - PI
    return Arc(start_angle=start, angle=sweep, radius=radius, arc_center=p)


def angle_between(p, a, b):
    u, v = normalize(a - p), normalize(b - p)
    return np.rad2deg(np.arccos(np.clip(u @ v, -1, 1)))


class InscribedAngle(BrandOutroMixin, ShortsScene):
    """The inscribed angle stays fixed while P runs round the circle."""

    sections = ["hook", "reveal", "outro"]
    upload = dict(
        title="This Angle Never Changes",
        description="Move P anywhere on the arc: the inscribed angle theorem.",
        hashtags=["#math", "#shorts", "#geometry"],
        pinned_comment="Where else have you seen this?",
    )

    def caption(self, text, y=-4.1, wait=1.4, keep=False):
        """A short grey sentence at a fixed spot under the figure."""
        line = Text(text, font_size=30).set_color(GREY_A)
        line.set_max_width(7.2).move_to(y * UP)
        self.play(FadeIn(line, 0.15 * UP), run_time=0.5)
        self.wait(wait)
        if keep:
            return line
        self.play(FadeOut(line), run_time=0.35)

    def hook(self):
        # Frame 0 is a FIGURE HOOK, laid out by hand since the figure is live
        title = hook_title("Inscribed Angle", [CIRCLE_C, INSCRIBED_C, CENTRAL_C], mode="gradient", font_size=64)
        title.move_to(4.45 * UP)
        circle = Circle(radius=RADIUS).move_to(CENTER).set_stroke(CIRCLE_C, 4)
        a, b = on_circle(A_DEG), on_circle(B_DEG)
        fixed = VGroup(
            Dot(a, radius=0.07), Dot(b, radius=0.07),
            Tex("A", font_size=40).next_to(a, DL, buff=0.1),
            Tex("B", font_size=40).next_to(b, DR, buff=0.1),
        )

        # P runs round the major arc; the chords and the angle follow it
        t = ValueTracker(150)
        p = Dot(radius=0.08).set_fill(INSCRIBED_C)
        p.f_always.move_to(lambda: on_circle(t.get_value()))
        p_name = Tex("P", font_size=40).set_color(INSCRIBED_C)
        p_name.add_updater(lambda m: m.move_to(p.get_center() + 0.4 * normalize(p.get_center() - CENTER)))
        chords = always_redraw(lambda: VGroup(
            Line(p.get_center(), a), Line(p.get_center(), b),
        ).set_stroke(WHITE, 3))
        arc = always_redraw(lambda: angle_arc(p.get_center(), a, b).set_stroke(INSCRIBED_C, 5))
        readout = Tex(R"\angle APB = 50.0^\circ", font_size=56)
        value = readout.make_number_changeable("50.0")
        value.f_always.set_value(lambda: angle_between(p.get_center(), a, b))
        readout.set_color(INSCRIBED_C).move_to(3.1 * DOWN)

        # Frame 0: the title over the full figure, already showing the angle
        self.add(title, circle, chords, arc, fixed, p, p_name, readout)
        self.wait(1.4)
        self.caption("Move P anywhere on the big arc...", wait=0.6, keep=False)
        for target in [60, 200, 10, 150]:       # all on the major arc, (-30, 230)
            self.play(t.animate.set_value(target), run_time=1.3)
        self.caption("...the angle never changes.", wait=1.0)
        for mob in (p, p_name, value):
            mob.clear_updaters()
        self.set_state("hook", Group(title, circle, chords, arc, fixed, p, p_name, readout))

    def reveal(self):
        self.lazy("hook", Group)
        a, b = on_circle(A_DEG), on_circle(B_DEG)

        # The reason: it is half the central angle, which is fixed
        o = Dot(CENTER, radius=0.07).set_fill(CENTRAL_C)
        o_name = Tex("O", font_size=40).set_color(CENTRAL_C).next_to(o, UP, buff=0.12)
        radii = VGroup(Line(CENTER, a), Line(CENTER, b)).set_stroke(CENTRAL_C, 4)
        central = Arc(
            start_angle=A_DEG * DEG, angle=(B_DEG - A_DEG) * DEG, radius=0.6, arc_center=CENTER,
        ).set_stroke(CENTRAL_C, 5)
        self.play(FadeIn(o, scale=0.5), FadeIn(o_name), ShowCreation(radii), run_time=0.8)
        self.play(ShowCreation(central), run_time=0.6)
        self.caption("It is always half the angle at the centre.", wait=1.3)

        result = Tex(
            R"\angle APB = \tfrac{1}{2}\angle AOB",
            t2c={R"\angle APB": INSCRIBED_C, R"\angle AOB": CENTRAL_C},
            font_size=60,
        ).move_to(4.3 * DOWN)
        self.play(Write(result), run_time=1.0)
        box = SurroundingRectangle(result, buff=0.22).set_stroke(YELLOW, 3)
        self.play(ShowCreation(box), FlashAround(result, color=YELLOW, time_width=1.5), run_time=1.2)
        self.wait(1.5)
