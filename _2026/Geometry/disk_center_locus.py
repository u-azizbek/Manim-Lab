from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/disk_center_locus.py
#
# Rods AB = CD = 8 stand on BC = 24.  A disk of any size sits on BC between
# them.  Where can its centre F go?  With B = (0, 0), a disk touching BC has
# centre (x, y) and radius y, and must not cross the rods:
#   up to height 8:  it must clear rod AB, so x >= y   (the 45 degree bisector
#                    of angle B: touching both AB and BC)
#   above 8:         it must clear the tip A, FA >= y, so y <= (x^2 + 64)/16,
#                    the parabola with focus A and directrix BC
# and the mirror images from C and D.  The two parabolas meet at (12, 13):
# the biggest disk, radius 13, through A and D.
#   area = 2 ( int_0^8 x dx + int_8^12 (x^2 + 64)/16 dx ) = 2 (32 + 124/3) = 440/3
# Checked by Monte Carlo on the "disk clears both rods" condition.

W, H = 24, 8
SCALE = 0.27
BC_Y = -1.35

ROD = "#9FB3C8"
RIVET = "#E6EDF5"
DISK = "#58C4DD"
CENTER = YELLOW
BISECTOR = "#5BD98A"
PARABOLA = "#FF9F43"
REGION = "#C39BFF"


def sp(x, y):
    return np.array([SCALE * (x - W / 2), BC_Y + SCALE * y, 0])


def top_left(x):
    """Highest centre over x on the left half: the bisector, then the parabola."""
    return x if x <= 8 else (x * x + 64) / 16


def top(x):
    return top_left(min(x, W - x))


class DiskCenterLocus(MockTestShort):
    """The region the centre of a disk resting on BC can reach."""

    test = ""
    card_top_buff = 0.6
    step_buff = 0.38

    problem_tex = (
        R"\text{Rods: } \tfrac{|BC|}{3} = |AB| = |CD| = 8.\\"
        R"\text{A disk of any size rests on } BC.\\"
        R"\text{What area can its centre reach?}"
    )

    sections = [
        "pose",
        "apparatus",
        "bisector",
        "parabola",
        "mirror",
        "area",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        card.set_z_index(10)             # big disks slide behind it
        self.steps_top_y = BC_Y - 0.95
        return card

    # The disk, driven by where it touches BC and how big it is

    def trackers(self):
        if not hasattr(self, "_disk"):
            self._disk = (ValueTracker(5), ValueTracker(0.01))
        return self._disk

    def make_disk(self):
        x, r = self.trackers()
        disk = always_redraw(lambda: Circle(radius=SCALE * r.get_value()).move_to(
            sp(x.get_value(), r.get_value())).set_stroke(DISK, 3).set_fill(DISK, 0.18))
        center = always_redraw(lambda: Dot(sp(x.get_value(), r.get_value()), radius=0.06).set_fill(CENTER))
        radius = always_redraw(lambda: DashedLine(
            sp(x.get_value(), 0), sp(x.get_value(), r.get_value()), dash_length=0.06,
        ).set_stroke(CENTER, 2))
        touch = always_redraw(lambda: Dot(sp(x.get_value(), 0), radius=0.045).set_fill(WHITE))
        name = Tex("F", font_size=28).set_color(CENTER)
        name.add_updater(lambda m: m.next_to(sp(x.get_value(), r.get_value()), UR, buff=0.04))
        return VGroup(disk, radius, touch, center, name.update())

    def get_disk(self):
        return self.lazy("disk", self.make_disk)

    def trace(self, x_of, start, color, width=5):
        """The part of a boundary curve from `start` up to where the disk is."""
        x_tracker = self.trackers()[0]

        def build():
            end = x_tracker.get_value()
            if abs(end - start) < 1e-3:
                return VMobject()
            xs = np.linspace(start, end, 60)
            return VMobject().set_points_as_corners([sp(x, x_of(x)) for x in xs]).set_stroke(color, width)
        return always_redraw(build)

    def curve(self, x0, x1, y_of, color, width=5):
        xs = np.linspace(x0, x1, 80)
        return VMobject().set_points_as_corners([sp(x, y_of(x)) for x in xs]).set_stroke(color, width)

    def flash_at(self, point, color=WHITE):
        return Flash(sp(*point), color=color, flash_radius=0.25, line_length=0.12)

    # Sections

    def apparatus(self):
        self.get_card()
        rods = VGroup(
            Line(sp(0, 0), sp(W, 0)),
            Line(sp(0, 0), sp(0, H)),
            Line(sp(W, 0), sp(W, H)),
        ).set_stroke(ROD, 7)
        rivets = VGroup(*[
            Dot(sp(*p), radius=0.08).set_fill(RIVET).set_stroke(BLACK, 1.5)
            for p in [(0, 0), (W, 0), (0, H), (W, H)]
        ])
        names = VGroup(
            Tex("B", font_size=30).next_to(sp(0, 0), DL, buff=0.06),
            Tex("C", font_size=30).next_to(sp(W, 0), DR, buff=0.06),
            Tex("A", font_size=30).next_to(sp(0, H), UL, buff=0.06),
            Tex("D", font_size=30).next_to(sp(W, H), UR, buff=0.06),
        )
        lengths = VGroup(
            Tex("24", font_size=28).set_color(ROD).next_to(sp(W / 2, 0), DOWN, buff=0.14),
            Tex("8", font_size=28).set_color(ROD).next_to(sp(0, H / 2), LEFT, buff=0.14),
            Tex("8", font_size=28).set_color(ROD).next_to(sp(W, H / 2), RIGHT, buff=0.14),
        )
        self.play(ShowCreation(rods[0]), run_time=0.7)
        self.play(ShowCreation(rods[1:], lag_ratio=0), run_time=0.6)
        self.play(FadeIn(rivets, scale=0.5), FadeIn(names), FadeIn(lengths), run_time=0.6)
        self.set_state("frame", VGroup(rods, rivets, names, lengths))

        # A disk of any size, resting on BC
        disk = self.make_disk()
        x, r = self.trackers()
        self.add(disk)
        self.play(r.animate.set_value(3), run_time=0.9)
        self.play(x.animate.set_value(15), r.animate.set_value(6), run_time=1.3)
        self.play(x.animate.set_value(10), r.animate.set_value(2), run_time=1.0)
        self.note("Resting on BC: the radius equals the\nheight of the centre F.", wait=1.2)
        self.set_state("disk", disk)

    def bisector(self):
        disk = self.get_disk()
        x, r = self.trackers()

        # Grow it until it hits rod AB
        self.play(x.animate.set_value(5), r.animate.set_value(1), run_time=0.8)
        self.play(r.animate.set_value(5), run_time=1.2)
        self.play(self.flash_at((0, 5)), run_time=0.6)
        self.note("Touching AB and BC: F is as far from both,\nso it lies on the bisector y = x.", wait=1.3)

        # Slide along while touching both rods: the centre runs up the bisector
        line = self.trace(lambda t: t, 5, BISECTOR)
        r.add_updater(lambda m: m.set_value(x.get_value()))
        self.add(line)
        self.play(x.animate.set_value(0.4), run_time=0.8)
        self.play(x.animate.set_value(8), run_time=1.4)
        r.clear_updaters()
        self.remove(line)
        full = self.curve(0, 8, lambda t: t, BISECTOR)
        self.add(full)
        self.add_step(R"y \le 8:\quad y \le x", color=BISECTOR, wait=0.4)
        self.set_state("bisector", full)

    def parabola(self):
        disk = self.get_disk()
        x, r = self.trackers()

        # Above height 8 the disk is stopped by the tip A instead
        self.play(x.animate.set_value(10), r.animate.set_value(4), run_time=0.8)
        self.play(r.animate.set_value(top_left(10)), run_time=1.3)
        self.play(self.flash_at((0, H), PARABOLA), run_time=0.6)
        fa = always_redraw(lambda: Line(sp(0, H), sp(x.get_value(), r.get_value())).set_stroke(PARABOLA, 3))
        self.play(ShowCreation(fa), run_time=0.5)
        self.note("Now F is as far from A as from BC:\na parabola with focus A, directrix BC.", wait=1.4)
        rule = self.add_step(R"x^2 + (y-8)^2 = y^2", color=PARABOLA, wait=0.5)
        self.replace_step(rule, R"y > 8:\quad y \le \frac{x^2 + 64}{16}", color=PARABOLA, wait=0.4)

        # Slide along the parabola
        arc = self.trace(top_left, 10, PARABOLA)
        r.add_updater(lambda m: m.set_value(top_left(x.get_value())))
        self.add(arc)
        self.play(x.animate.set_value(8), run_time=0.7)
        self.play(x.animate.set_value(12), run_time=1.4)
        r.clear_updaters()
        self.remove(arc)
        full = self.curve(8, 12, top_left, PARABOLA)
        self.add(full)
        self.play(FadeOut(fa), run_time=0.3)
        self.set_state("parabola", full)

    def mirror(self):
        disk = self.get_disk()
        x, r = self.trackers()
        bisector = self.lazy("bisector", lambda: self.curve(0, 8, lambda t: t, BISECTOR))
        parabola = self.lazy("parabola", lambda: self.curve(8, 12, top_left, PARABOLA))

        # The same from the right, off rod CD and its tip D
        other = VGroup(
            self.curve(24, 16, lambda t: W - t, BISECTOR),
            self.curve(16, 12, top, PARABOLA),
        )
        self.play(
            TransformFromCopy(bisector, other[0], path_arc=-PI / 3),
            TransformFromCopy(parabola, other[1], path_arc=-PI / 3),
            run_time=1.3,
        )

        # They meet over the middle: the biggest disk passes through A and D
        self.play(x.animate.set_value(12), r.animate.set_value(13), run_time=1.0)
        self.play(self.flash_at((0, H), PARABOLA), self.flash_at((W, H), PARABOLA), run_time=0.7)
        peak = Tex(R"(12,\ 13)", font_size=28).set_color(CENTER).next_to(sp(12, 13), UP, buff=0.12)
        self.play(FadeIn(peak), run_time=0.4)
        self.note("Same from the right. They meet at (12, 13):\nthe biggest disk, radius 13, through A and D.", wait=1.4)
        self.play(FadeOut(disk), FadeOut(peak), run_time=0.5)
        self.set_state("other", other)

    def area(self):
        self.lazy("bisector", lambda: self.curve(0, 8, lambda t: t, BISECTOR))
        self.lazy("parabola", lambda: self.curve(8, 12, top_left, PARABOLA))
        self.lazy("other", VGroup)
        self.clear_steps()

        # Everything under the boundary is reachable
        def under(x0, x1, color, opacity=0.35):
            xs = np.linspace(x0, x1, 80)
            points = [sp(x0, 0), *[sp(x, top(x)) for x in xs], sp(x1, 0)]
            return Polygon(*points).set_stroke(width=0).set_fill(color, opacity)

        region = under(0, W, REGION, 0.4)
        self.play(FadeIn(region), run_time=0.8)
        self.note("Split it at x = 8 and x = 12, and use symmetry.", wait=1.1)

        triangle = under(0, 8, BISECTOR, 0.45)
        strip = under(8, 12, PARABOLA, 0.45)
        self.play(FadeIn(triangle), run_time=0.5)
        self.play(FadeIn(strip), run_time=0.5)
        area = self.add_step(
            R"S = 2\left(\int_0^8 x\,dx + \int_8^{12}\frac{x^2+64}{16}\,dx\right)",
            font_size=38, wait=0.8,
        )
        self.play(
            TransformFromCopy(triangle, under(16, 24, BISECTOR, 0.45)),
            TransformFromCopy(strip, under(12, 16, PARABOLA, 0.45)),
            run_time=1.0,
        )
        self.replace_step(area, R"S = 2\left(32 + \frac{124}{3}\right)", font_size=40, wait=0.7)
        self.conclude(R"S = \frac{440}{3} \approx 146.7", font_size=48, wait=1.5)
