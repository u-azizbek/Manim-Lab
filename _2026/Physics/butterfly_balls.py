from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Physics/butterfly_balls.py
#
# Balls dropped inside a circle, bouncing elastically off its wall.  Each
# flight is an exact parabola; a wall hit is found by bisection on the step
# and the velocity reflected in the wall's normal, so energy stays constant
# to about 1e-10.  Every group starts from the same point, the balls shifted
# sideways by a fraction of a pixel (1e-3 units apart, 2e-4 for fifty).  The
# curved wall magnifies those differences at every bounce: after about six
# seconds of simulated time neighbours no longer move together.
#
# Played at SPEED times real time.

R = 3.7
G = 9.0
START = (0.05, 2.49)
FPS = 120                 # simulation samples per simulated second
SPEED = 0.7               # simulated seconds per second of video
CENTER = 0.35 * DOWN

RAINBOW = ["#FF3B3B", "#FF8A1F", "#FFD23F", "#7ED957", "#2FB86E", "#3FA7FF", "#3B5BFF", "#8A4DFF", "#D24DFF"]


def simulate(x0, y0, duration, sub=4):
    """Positions sampled FPS times a simulated second."""
    a = np.array([0.0, -G])
    p = np.array([x0, y0], dtype=float)
    v = np.zeros(2)
    dt = 1 / (FPS * sub)
    out = [p.copy()]
    for _ in range(int(duration * FPS) + 2):
        for _ in range(sub):
            remaining = dt
            while remaining > 0:
                q = p + v * remaining + 0.5 * a * remaining ** 2
                if q @ q <= R * R:
                    p, v = q, v + a * remaining
                    break
                # Find the moment of contact, then reflect off the wall
                lo, hi = 0.0, remaining
                for _ in range(100):
                    mid = (lo + hi) / 2
                    m = p + v * mid + 0.5 * a * mid ** 2
                    lo, hi = (mid, hi) if m @ m <= R * R else (lo, mid)
                p = p + v * lo + 0.5 * a * lo ** 2
                v = v + a * lo
                n = p / np.linalg.norm(p)
                v = v - 2 * (v @ n) * n
                p = p * (1 - 1e-12)
                remaining -= lo
        out.append(p.copy())
    return np.array(out)


def sp(p):
    return CENTER + p[0] * RIGHT + p[1] * UP


class ButterflyBalls(BrandOutroMixin, ShortsScene):
    """1, 2, 10 and 50 balls bouncing in a circle: the butterfly effect."""

    sections = ["one_ball", "two_balls", "ten_balls", "fifty_balls", "hundred_balls", "outro"]

    def setup(self):
        super().setup()
        self.circle = Circle(radius=R).move_to(CENTER).set_stroke(WHITE, 4)

    def label(self, text):
        """A big title in the middle, which then settles at the top."""
        big = Tex(Rf"\text{{{text}}}", font_size=120)
        old = self.lazy_state.get("label")
        anims = [FadeOut(old, 0.2 * UP)] if old is not None else []
        self.play(*anims, FadeIn(big, scale=0.9), run_time=0.7)
        self.wait(0.6)
        self.play(big.animate.scale(0.45).move_to(5.6 * UP), run_time=0.7)
        self.set_state("label", big)

    def run_balls(self, offsets, colors, sim_time, tail_time, width=5, radius=0.075):
        paths = [simulate(START[0] + dx, START[1], sim_time) for dx in offsets]
        clock = ValueTracker(0)

        def index(delay=0.0):
            return min(int(max(clock.get_value() * SPEED - delay, 0) * FPS), len(paths[0]) - 1)

        def trail(path, color):
            end = index()
            start = max(0, end - int(tail_time * FPS))
            if end - start < 2:
                return VMobject()
            tail = VMobject().set_points_as_corners([sp(p) for p in path[start:end + 1]])
            return tail.set_stroke(color, width=[0.3, width], opacity=[0.0, 1.0])

        trails = always_redraw(lambda: VGroup(*[trail(p, c) for p, c in zip(paths, colors)]))
        heads = always_redraw(lambda: VGroup(*[
            Dot(sp(p[index()]), radius=radius).set_fill(c).set_stroke(BLACK, 1)
            for p, c in zip(paths, colors)
        ]))
        self.add(trails, heads)
        self.play(clock.animate.set_value(sim_time / SPEED), run_time=sim_time / SPEED, rate_func=linear)
        return trails, heads

    def clear_run(self, *mobs):
        self.play(*[FadeOut(m) for m in mobs], run_time=0.5)

    # Sections

    def one_ball(self):
        self.label("1 ball")
        self.play(ShowCreation(self.circle), run_time=1.0)
        trails, heads = self.run_balls([0.0], [WHITE], sim_time=10, tail_time=1.4, width=6, radius=0.09)
        self.clear_run(trails, heads)

    def two_balls(self):
        self.lazy("circle", lambda: self.circle)
        self.label("2 balls")
        trails, heads = self.run_balls([0.0, 1e-3], ["#FF3B3B", "#3FA7FF"], sim_time=12, tail_time=1.2, width=6, radius=0.085)
        self.clear_run(trails, heads)

    def ten_balls(self):
        self.lazy("circle", lambda: self.circle)
        self.label("10 balls")
        offsets = [k * 1e-3 for k in range(10)]
        trails, heads = self.run_balls(offsets, color_gradient(RAINBOW, 10), sim_time=20, tail_time=0.9)
        self.clear_run(trails, heads)

    def fifty_balls(self):
        self.lazy("circle", lambda: self.circle)
        self.label("50 balls")
        offsets = [k * 2e-4 for k in range(50)]
        trails, heads = self.run_balls(offsets, color_gradient(RAINBOW, 50), sim_time=20, tail_time=0.75, width=4, radius=0.065)
        # note = Text(
        #     "All 50 started less than a pixel apart.\nEvery bounce magnifies the difference.",
        #     font_size=28,
        # ).set_color(GREY_A).move_to(4.8 * DOWN)
        # self.play(FadeIn(note, 0.15 * UP), run_time=0.6)
        self.clear_run(trails, heads)

    def hundred_balls(self):
        self.lazy("circle", lambda: self.circle)
        self.label("100 balls")
        offsets = [k * 2e-4 for k in range(100)]
        trails, heads = self.run_balls(offsets, color_gradient(RAINBOW, 100), sim_time=20, tail_time=0.50, width=4, radius=0.050)
        # note = Text(
        #     "All 50 started less than a pixel apart.\nEvery bounce magnifies the difference.",
        #     font_size=28,
        # ).set_color(GREY_A).move_to(4.8 * DOWN)
        # self.play(FadeIn(note, 0.15 * UP), run_time=0.6)
        self.clear_run(trails, heads)
        self.wait(1.2)
