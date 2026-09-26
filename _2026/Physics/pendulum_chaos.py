from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Physics/pendulum_chaos.py
#
# One pendulum, then a double pendulum, then two double pendulums started
# 0.001 rad apart.  Equal masses and arms (1 m, g = 9.81), integrated with
# RK4 at 1200 steps a second, shown in real time.  Energy stays constant to
# 1e-6, so the chaos is the pendulum's, not the integrator's.  From
# (theta1, theta2) = (2.2, 2.2) the two copies' tips are half an arm apart
# after about 5.4 s.

G = 9.81
DT = 1 / 1200

SINGLE_START = 70 * DEGREES
DOUBLE_START = (2.0, 2.6)
TWIN_START = (2.2, 2.2)
NUDGE = 1e-3

ROD = "#E6EDF5"
SINGLE_BOB = "#FFD166"
BOB_ONE = "#58C4DD"
BOB_TWO = "#FF6BD6"
TWIN_A = "#FF6BD6"
TWIN_B = "#4FD1C5"
RAINBOW = ["#FF5C5C", "#FF9F43", "#FFD166", "#5BD98A", "#4FD1C5", "#58C4DD", "#7F8CFF", "#C39BFF", "#FF6BD6"]


def rk4(deriv, state, duration):
    s = np.array(state, dtype=float)
    out = [s.copy()]
    for _ in range(int(duration / DT) + 2):
        k1 = deriv(s)
        k2 = deriv(s + DT / 2 * k1)
        k3 = deriv(s + DT / 2 * k2)
        k4 = deriv(s + DT * k3)
        s = s + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(s.copy())
    return np.array(out)


def single(s):
    theta, omega = s
    return np.array([omega, -G * np.sin(theta)])


def double(s):
    """Equal masses and arms of length 1."""
    t1, t2, w1, w2 = s
    d = t1 - t2
    den = 3 - np.cos(2 * d)
    a1 = (-3 * G * np.sin(t1) - G * np.sin(t1 - 2 * t2) - 2 * np.sin(d) * (w2 ** 2 + w1 ** 2 * np.cos(d))) / den
    a2 = 2 * np.sin(d) * (2 * w1 ** 2 + 2 * G * np.cos(t1) + w2 ** 2 * np.cos(d)) / den
    return np.array([w1, w2, a1, a2])


def at(path, t):
    return path[min(int(round(t / DT)), len(path) - 1)]


class PendulumChaos(BrandOutroMixin, ShortsScene):
    """A single pendulum's rhythm against a double pendulum's chaos."""

    sections = ["one_pendulum", "double_pendulum", "butterfly", "outro"]

    def title(self, text, sub, color):
        title = Text(text, font_size=48, weight=BOLD)
        subtitle = Text(sub, font_size=26).set_color(GREY_B)
        line = Line(LEFT, RIGHT).set_width(title.get_width() * 0.5).set_stroke(color, 4)
        return VGroup(title, line, subtitle).arrange(DOWN, buff=0.18).move_to(5.55 * UP)

    def show_title(self, header):
        old = self.lazy_state.get("header")
        anims = [FadeOut(old, 0.2 * UP)] if old is not None else []
        self.play(*anims, FadeIn(header[0], 0.2 * DOWN), ShowCreation(header[1]), FadeIn(header[2]), run_time=0.9)
        self.set_state("header", header)

    def caption(self, text, y=-4.55):
        return Text(text, font_size=28).set_color(GREY_A).move_to(y * UP)

    def ceiling(self, pivot, width=1.6):
        bar = Line(pivot + width / 2 * LEFT, pivot + width / 2 * RIGHT).set_stroke(ROD, 4)
        hatch = VGroup(*[
            Line(pivot + x * RIGHT, pivot + x * RIGHT + 0.16 * (UP + RIGHT)).set_stroke(ROD, 2)
            for x in np.linspace(-width / 2, width / 2 - 0.16, 9)
        ])
        return VGroup(bar, hatch, Dot(pivot, radius=0.06).set_fill(ROD))

    def clock(self):
        """t = ... s, laid out at its widest so the digits never run into the unit."""
        value = DecimalNumber(88.8, num_decimal_places=1, font_size=32)
        clock = VGroup(Tex("t =", font_size=32), value, Tex(R"\text{s}", font_size=32))
        clock.arrange(RIGHT, buff=0.1).set_color(GREY_A)
        value.set_value(0)
        return clock

    def bob(self, point, color, radius=0.15):
        return VGroup(
            Dot(point, radius=radius * 2.1).set_fill(color, 0.18),
            Dot(point, radius=radius).set_fill(color).set_stroke(WHITE, 1.5),
        )

    def trail(self, points, color, width=4):
        """A tail that fades out toward its old end."""
        if len(points) < 2:
            return VMobject()
        tail = VMobject().set_points_as_corners(points)
        return tail.set_stroke(color, width=[0.5, width], opacity=[0.0, 1.0])

    # Sections

    def one_pendulum(self):
        self.show_title(self.title("One pendulum", "a steady rhythm, the same swing again and again", SINGLE_BOB))
        pivot = 3.05 * UP
        arm = 2.4
        duration = 9.0
        path = rk4(single, (SINGLE_START, 0.0), duration)
        t = ValueTracker(0)

        def bob_at(time):
            theta = at(path, time)[0]
            return pivot + arm * np.array([np.sin(theta), -np.cos(theta), 0])

        rod = always_redraw(lambda: Line(pivot, bob_at(t.get_value())).set_stroke(ROD, 4))
        bob = always_redraw(lambda: self.bob(bob_at(t.get_value()), SINGLE_BOB, 0.17))
        tail = always_redraw(lambda: self.trail(
            [bob_at(s) for s in np.linspace(max(0, t.get_value() - 0.9), t.get_value(), 40)], SINGLE_BOB, 6,
        ))

        # theta against time, drawn as it swings
        box = Rectangle(6.8, 2.2).set_stroke(GREY_B, 1.5).move_to(2.55 * DOWN)
        mid = Line(box.get_left(), box.get_right()).set_stroke(GREY_B, 1, 0.5)
        names = VGroup(
            Tex(R"\theta", font_size=32).next_to(box, LEFT, buff=0.12).set_y(box.get_y()),
            Tex("t", font_size=30).next_to(box.get_corner(DR), DOWN, buff=0.1),
        ).set_color(GREY_A)

        def plot_point(time):
            x = box.get_left()[0] + box.get_width() * time / duration
            y = box.get_y() + (box.get_height() / 2 - 0.15) * at(path, time)[0] / SINGLE_START
            return np.array([x, y, 0])

        wave = always_redraw(lambda: VMobject().set_points_as_corners(
            [plot_point(s) for s in np.linspace(0, t.get_value(), max(2, int(60 * t.get_value())))]
        ).set_stroke(SINGLE_BOB, 3))
        pen = always_redraw(lambda: Dot(plot_point(t.get_value()), radius=0.06).set_fill(SINGLE_BOB))

        self.play(FadeIn(self.ceiling(pivot)), run_time=0.4)
        self.play(ShowCreation(rod), FadeIn(bob, scale=0.5), run_time=0.6)
        self.play(ShowCreation(box), FadeIn(mid), FadeIn(names), run_time=0.6)
        self.add(tail, rod, bob, wave, pen)
        self.play(t.animate.set_value(duration), run_time=duration, rate_func=linear)
        note = self.caption("Predictable: the same wave every period.")
        self.play(FadeIn(note, 0.15 * UP), run_time=0.5)
        self.wait(1.0)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m not in (self.frame, self.lazy_state["header"])])), run_time=0.6)

    def double_pendulum(self):
        self.show_title(self.title("Double pendulum", "hang a second pendulum from the first", BOB_TWO))
        pivot = 1.45 * UP
        arm = 1.38
        duration = 15.0
        path = rk4(double, (*DOUBLE_START, 0.0, 0.0), duration)
        t = ValueTracker(0)

        def joints(time):
            t1, t2 = at(path, time)[:2]
            p1 = pivot + arm * np.array([np.sin(t1), -np.cos(t1), 0])
            return p1, p1 + arm * np.array([np.sin(t2), -np.cos(t2), 0])

        rods = always_redraw(lambda: VMobject().set_points_as_corners(
            [pivot, *joints(t.get_value())]).set_stroke(ROD, 4))
        bobs = always_redraw(lambda: VGroup(
            self.bob(joints(t.get_value())[0], BOB_ONE, 0.13),
            self.bob(joints(t.get_value())[1], BOB_TWO, 0.15),
        ))

        # The whole path of the lower bob, coloured by time
        def trace():
            now = t.get_value()
            if now < 0.05:
                return VMobject()
            times = np.linspace(0, now, max(2, int(70 * now)))
            curve = VMobject().set_points_as_corners([joints(s)[1] for s in times])
            return curve.set_stroke(color_gradient(RAINBOW, 12), 2.2, 0.9)

        path_mob = always_redraw(trace)
        clock = self.clock()
        clock.move_to(2.3 * DOWN)
        clock[1].add_updater(lambda m: m.set_value(t.get_value()))

        self.play(FadeIn(self.ceiling(pivot, 1.2)), run_time=0.4)
        self.play(ShowCreation(rods), FadeIn(bobs, scale=0.5), FadeIn(clock), run_time=0.6)
        self.add(path_mob, rods, bobs)
        self.play(t.animate.set_value(duration), run_time=duration, rate_func=linear)
        clock[1].clear_updaters()
        note = self.caption("No repeating rhythm: the path never settles.\nThis is chaos.")
        self.play(FadeIn(note, 0.15 * UP), run_time=0.5)
        self.wait(1.2)
        self.play(FadeOut(Group(*[m for m in self.mobjects if m not in (self.frame, self.lazy_state["header"])])), run_time=0.6)

    def butterfly(self):
        self.show_title(self.title("The butterfly effect", "two double pendulums, 0.001 rad apart", TWIN_B))
        pivot = 1.45 * UP
        arm = 1.38
        duration = 12.0
        paths = [
            rk4(double, (*TWIN_START, 0.0, 0.0), duration),
            rk4(double, (TWIN_START[0] + NUDGE, TWIN_START[1], 0.0, 0.0), duration),
        ]
        t = ValueTracker(0)

        def joints(path, time):
            t1, t2 = at(path, time)[:2]
            p1 = pivot + arm * np.array([np.sin(t1), -np.cos(t1), 0])
            return p1, p1 + arm * np.array([np.sin(t2), -np.cos(t2), 0])

        def rig(path, color):
            rods = always_redraw(lambda: VMobject().set_points_as_corners(
                [pivot, *joints(path, t.get_value())]).set_stroke(color, 4, 0.9))
            bobs = always_redraw(lambda: VGroup(*[
                self.bob(p, color, r) for p, r in zip(joints(path, t.get_value()), (0.12, 0.14))
            ]))
            tail = always_redraw(lambda: self.trail(
                [joints(path, s)[1] for s in np.linspace(max(0, t.get_value() - 1.6), t.get_value(), 60)], color, 5,
            ))
            return VGroup(tail, rods, bobs)

        rigs = VGroup(rig(paths[0], TWIN_A), rig(paths[1], TWIN_B))

        # How far apart the two tips are
        gap = DecimalNumber(0, num_decimal_places=3, font_size=34).set_color(YELLOW)
        gap.add_updater(lambda m: m.set_value(
            get_norm(joints(paths[0], t.get_value())[1] - joints(paths[1], t.get_value())[1]) / arm))
        readout = VGroup(Text("gap between the tips:", font_size=28), gap, Text("arm lengths", font_size=28))
        readout.arrange(RIGHT, buff=0.15).move_to(2.3 * DOWN)
        clock = self.clock()
        clock.next_to(readout, DOWN, buff=0.3)
        clock[1].add_updater(lambda m: m.set_value(t.get_value()))

        self.play(FadeIn(self.ceiling(pivot, 1.2)), run_time=0.4)
        self.play(FadeIn(rigs), FadeIn(readout), FadeIn(clock), run_time=0.7)
        self.play(t.animate.set_value(duration), run_time=duration, rate_func=linear)
        for m in (gap, clock[1]):
            m.clear_updaters()
        note = self.caption("Almost the same start, a completely\ndifferent motion a few seconds later.")
        self.play(FadeIn(note, 0.15 * UP), run_time=0.5)
        self.wait(1.5)
