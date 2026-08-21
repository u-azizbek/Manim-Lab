from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Puzzles/five_circles_grid.py
#
# Puzzle: five circles are drawn through a 5x5 grid of dots.  Can every dot be
# made to lie on one of them?
#
# Both covers below came out of an exhaustive search: there are 997 circles
# through three or more grid points, and each solution was checked to hit all
# 25 dots.  The same search shows four circles can never be enough, so five is
# the minimum.  Ordered so each circle adds as many new dots as it can, both
# run 8 -> 14 -> 18 -> 22 -> 25.

GRID_N = 5
STEP = 1.05                 # scene units per grid step

DOT_COLOR = "#C23B3B"       # a dot no circle passes through yet
HIT_COLOR = YELLOW          # a dot sitting on a circle

TITLE_Y = 5.90
STATS_Y = 4.55
CAPTION_Y = -4.45

POINTS = [(x, y) for x in range(GRID_N) for y in range(GRID_N)]

# (centre x, centre y, radius), in grid units
MAIN_SOLUTION = [
    (1.5000000000, 2.5000000000, 1.5811388301),   # 8 dots
    (2.5000000000, 1.5000000000, 1.5811388301),   # 8 dots
    (2.5000000000, 2.5000000000, 1.5811388301),   # 8 dots
    (2.0000000000, 2.0000000000, 2.8284271247),   # the four corners
    (1.1666666667, 1.1666666667, 1.1785113020),   # (0,1), (1,0) and the centre
]

ALT_SOLUTION = [
    (2.0000000000, 2.0000000000, 2.2360679775),   # 8 dots
    (2.0000000000, 1.0000000000, 2.2360679775),   # 6 dots
    (3.0000000000, 2.0000000000, 2.2360679775),   # 6 dots
    (2.5000000000, 1.5000000000, 0.7071067812),   # 4 dots
    (0.8333333333, 3.1666666667, 1.1785113020),   # 3 dots
]


class FiveCirclesPuzzle(BrandOutroMixin, ShortsScene):
    """The 5x5 dot puzzle: cover every dot with five circles."""

    sections = [
        "pose",
        "first_tries",
        "solve",
        "alternative",
        "outro",
    ]

    def setup(self):
        super().setup()
        self.circle_colors = color_gradient([BLUE_C, TEAL_C, GREEN_B], 5)

    # Geometry

    def grid_pos(self, x, y):
        return (x - 2) * STEP * RIGHT + (y - 2) * STEP * UP

    def dots_on(self, spec):
        """Which grid dots lie on this circle.  The nearest dot that is *not*
        on a circle still misses it by 0.236 grid units, so the tolerance here
        is never a close call."""
        cx, cy, r = spec
        return [
            p for p in POINTS
            if abs(((p[0] - cx) ** 2 + (p[1] - cy) ** 2) ** 0.5 - r) < 1e-6
        ]

    def make_circle(self, spec, color):
        cx, cy, r = spec
        circle = Circle(radius=r * STEP)
        circle.set_stroke(color, 4).set_fill(opacity=0)
        circle.move_to(self.grid_pos(cx, cy))
        return circle

    # Pieces carried between sections

    def make_grid(self):
        dots = VGroup(*[
            Dot(self.grid_pos(x, y), radius=0.085).set_color(DOT_COLOR)
            for x, y in POINTS
        ])
        dots.dot_at = dict(zip(POINTS, dots))
        return dots

    def get_grid(self):
        return self.lazy("grid", self.make_grid)

    def make_stats(self):
        def block(label, color, value):
            name = Text(label, font_size=21).set_color(GREY_B)
            # `edge_to_fix=ORIGIN` keeps the number centred under its label as
            # it grows and shrinks; the default pins its left edge instead
            number = Integer(value, font_size=44, edge_to_fix=ORIGIN)
            number.set_color(color)
            number.next_to(name, DOWN, buff=0.16)
            group = VGroup(name, number)
            group.number = number
            return group

        stats = VGroup(
            block("CIRCLES", WHITE, 0),
            block("COVERED", HIT_COLOR, 0),
            block("MISSING", DOT_COLOR, 25),
        )
        stats.arrange(RIGHT, buff=1.0, aligned_edge=UP)
        stats.set_y(STATS_Y)
        stats.circles, stats.covered, stats.missing = stats
        return stats

    def get_stats(self):
        return self.lazy("stats", self.make_stats)

    def get_circles(self):
        return self.lazy("circles", VGroup)

    def covered(self):
        if not hasattr(self, "_covered"):
            self._covered = set()
        return self._covered

    # Beats

    def set_stats(self, n_circles, n_covered, run_time=0.6):
        stats = self.get_stats()
        self.play(
            ChangeDecimalToValue(stats.circles.number, n_circles),
            ChangeDecimalToValue(stats.covered.number, n_covered),
            ChangeDecimalToValue(stats.missing.number, 25 - n_covered),
            run_time=run_time,
        )

    def caption(self, message, wait=1.3, font_size=30):
        """A sentence under the grid saying what the step is doing, cleared
        again so it costs no permanent room."""
        text = Text(message, font_size=font_size).set_color(GREY_A)
        text.set_max_width(6.9)
        text.set_y(CAPTION_Y)
        self.play(FadeIn(text, 0.12 * UP), run_time=0.45)
        self.wait(wait)
        self.play(FadeOut(text, 0.12 * UP), run_time=0.35)

    def light_up(self, points, run_time=0.8):
        grid = self.get_grid()
        self.play(
            LaggedStart(*[
                grid.dot_at[p].animate.set_color(HIT_COLOR).scale(1.25)
                for p in points
            ], lag_ratio=0.06),
            run_time=run_time,
        )

    def add_circle(self, spec, index, run_time=1.0):
        """Draw one circle and light the dots it newly passes through."""
        circle = self.make_circle(spec, self.circle_colors[index])
        self.get_circles().add(circle)
        self.play(ShowCreation(circle), run_time=run_time)

        covered = self.covered()
        fresh = [p for p in self.dots_on(spec) if p not in covered]
        if fresh:
            self.light_up(fresh)
            covered.update(fresh)
        return circle

    def fill_in_through(self, count):
        """Put the first `count` circles on screen with no animation, so any
        section can be rendered on its own."""
        grid = self.get_grid()
        circles = self.get_circles()
        covered = self.covered()
        while len(circles) < count:
            spec = MAIN_SOLUTION[len(circles)]
            circles.add(self.make_circle(spec, self.circle_colors[len(circles)]))
            for p in self.dots_on(spec):
                if p not in covered:
                    grid.dot_at[p].set_color(HIT_COLOR).scale(1.25)
                    covered.add(p)
        self.add(circles)
        stats = self.get_stats()
        stats.circles.number.set_value(len(circles))
        stats.covered.number.set_value(len(covered))
        stats.missing.number.set_value(25 - len(covered))
        return circles

    # Sections

    def pose(self):
        grid = self.make_grid()
        self.play(
            LaggedStart(*[FadeIn(d, scale=0.4) for d in grid], lag_ratio=0.03),
            run_time=1.4,
        )
        self.set_state("grid", grid)

        title = Text("25 dots, 5 circles", font_size=48, weight=BOLD)
        title.set_color(WHITE)
        title.set_y(TITLE_Y)
        question = Text("Can every dot be made to lie on a circle?", font_size=31)
        question.set_color(GREY_A)
        question.set_max_width(6.9)
        question.set_y(CAPTION_Y)

        self.play(FadeIn(title, 0.2 * DOWN), run_time=0.6)
        self.play(FadeIn(question, 0.12 * UP), run_time=0.6)
        self.wait(1.4)
        self.play(FadeOut(question, 0.12 * UP), run_time=0.35)

        stats = self.make_stats()
        self.play(FadeIn(stats, 0.15 * DOWN), run_time=0.5)
        self.set_state("stats", stats)

    def first_tries(self):
        self.get_grid()
        self.get_stats()
        self.caption("A dot counts only if it sits on the circle itself.")

        for i in range(3):
            self.add_circle(MAIN_SOLUTION[i], i)
            self.set_stats(i + 1, len(self.covered()))
            if i == 0:
                self.caption("One circle can pass through 8 dots at once.")

        self.caption("Three circles, and 7 dots are still stranded.", wait=1.4)

    def solve(self):
        self.fill_in_through(3)

        self.caption("The four corners want a circle of their own.")
        self.add_circle(MAIN_SOLUTION[3], 3)
        self.set_stats(4, len(self.covered()))

        self.caption("Three left, the stubborn centre dot among them.")
        self.add_circle(MAIN_SOLUTION[4], 4)
        self.set_stats(5, len(self.covered()))

        grid = self.get_grid()
        self.play(
            LaggedStart(*[
                Flash(d, color=HIT_COLOR, line_length=0.14, flash_radius=0.26)
                for d in grid
            ], lag_ratio=0.02),
            run_time=1.2,
        )
        self.caption("All 25 dots covered.", wait=1.2, font_size=34)
        self.caption("Four circles could never do it - five is the minimum.", wait=1.5)

    def alternative(self):
        self.fill_in_through(5)
        grid = self.get_grid()

        self.caption("And this is not the only answer.", wait=1.0)
        self.play(FadeOut(self.get_circles()), run_time=0.5)
        self.play(
            *[d.animate.set_color(DOT_COLOR).scale(0.8) for d in grid],
            run_time=0.4,
        )
        self.lazy_state.pop("circles", None)
        self.covered().clear()
        self.set_stats(0, 0, run_time=0.3)

        alt = VGroup(*[
            self.make_circle(spec, self.circle_colors[i])
            for i, spec in enumerate(ALT_SOLUTION)
        ])
        self.set_state("circles", alt)
        self.play(
            LaggedStart(*[ShowCreation(c) for c in alt], lag_ratio=0.35),
            run_time=2.6,
        )
        self.light_up(POINTS, run_time=1.0)
        self.covered().update(POINTS)
        self.set_stats(5, 25, run_time=0.5)
        self.caption("Same 25 dots, a different five.", wait=1.4, font_size=34)
