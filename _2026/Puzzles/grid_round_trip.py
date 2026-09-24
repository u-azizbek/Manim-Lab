from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Puzzles/grid_round_trip.py
#
# Travel from A to B along the grid (right/up) and back again (left/down),
# with the way back different from the way there.  How many round trips?
#
# Vertex addition: every point's count is the sum of the counts of the points
# that step into it, which reaches 17 at B.  The way back can be any of those
# 17 except the one already used, so there are 17 x 16 = 272 trips.  Checked by
# brute force: 17 monotone paths, and 272 ordered pairs of distinct ones.

UNIT = 1.5
GRID_A = 3.0 * LEFT + (3.4 - 3 * UNIT) * UP     # where A sits on screen
STEPS_TOP = -2.0

# Unit squares by lower-left corner, read off the figure
SQUARES = [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2), (3, 2)]
A, B = (0, 0), (4, 3)

GO = YELLOW
BACK = "#58C4DD"
POINT = "#FF5C5C"

GO_PATH = [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2), (3, 2), (3, 3), (4, 3)]
OTHER_PATH = [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2), (2, 3), (3, 3), (4, 3)]


def grid_edges():
    edges = set()
    for x, y in SQUARES:
        edges |= {
            ((x, y), (x + 1, y)), ((x, y + 1), (x + 1, y + 1)),
            ((x, y), (x, y + 1)), ((x + 1, y), (x + 1, y + 1)),
        }
    return sorted(edges)


EDGES = grid_edges()
VERTICES = sorted({v for edge in EDGES for v in edge}, key=lambda v: (sum(v), v))


def incoming(v):
    """The points that step into v: the one to its left first, then below."""
    return sorted((u for u, w in EDGES if w == v), key=lambda u: u[1] != v[1])


def count_ways():
    ways = {A: 1}
    for v in VERTICES[1:]:
        ways[v] = sum(ways[u] for u in incoming(v))
    return ways


WAYS = count_ways()                        # WAYS[B] == 17


class GridRoundTrip(MockTestShort):
    """Round trips on a staircase grid, counted by vertex addition."""

    test = ""
    card_top_buff = 0.85
    step_buff = 0.45

    problem_tex = (
        R"\text{Walk } A \to B \text{ and back.}\\"
        R"\text{Back} \ne \text{there. How many trips?}"
    )

    sections = [
        "pose",
        "draw_grid",
        "examples",
        "count_ways",
        "round_trip",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        # The steps hang below the grid rather than straight off the card
        self.steps_top_y = STEPS_TOP
        return card

    # Pieces

    def gp(self, v):
        return GRID_A + UNIT * (v[0] * RIGHT + v[1] * UP)

    def make_grid(self):
        lines = VGroup(*[Line(self.gp(u), self.gp(v)) for u, v in EDGES])
        lines.set_stroke(GREY_B, 4)
        ends = VGroup(*[Dot(self.gp(v), radius=0.11).set_color(POINT) for v in (A, B)])
        # Far enough out to clear the count discs that later sit on A and B
        labels = VGroup(
            Tex("A", font_size=40).set_color(POINT).next_to(self.gp(A), DL, buff=0.3),
            Tex("B", font_size=40).set_color(POINT).next_to(self.gp(B), UR, buff=0.3),
        )
        grid = VGroup(lines, ends, labels)
        grid.lines, grid.ends, grid.labels = lines, ends, labels
        return grid

    def get_grid(self):
        return self.lazy("grid", self.make_grid)

    def make_path(self, vertices, color, width):
        path = VMobject().set_points_as_corners([self.gp(v) for v in vertices])
        return path.set_stroke(color, width)

    def get_badges(self):
        """A disc per point holding its count, keyed by point.  Built once and
        revealed wave by wave."""
        if not hasattr(self, "_badges"):
            self._badges = {}
            for v in VERTICES:
                disc = Circle(radius=0.27).set_fill(BLACK, 1)
                disc.set_stroke(POINT if v in (A, B) else GREY_B, 2.5)
                disc.move_to(self.gp(v))
                number = Tex(str(WAYS[v]), font_size=30).move_to(disc)
                number.set_color(GO if v == B else WHITE)
                self._badges[v] = VGroup(disc, number)
        return self._badges

    def edge_flash(self, u, v):
        # Stop at the discs' rims, so the flash never paints over a count
        line = Line(self.gp(u), self.gp(v), buff=0.3).set_stroke(GO, 7)
        return ShowPassingFlash(line, time_width=0.7)

    def verdict(self, ok):
        if ok:
            mark = VMobject().set_points_as_corners(
                [0.22 * LEFT, 0.2 * DOWN + 0.05 * LEFT, 0.3 * RIGHT + 0.3 * UP]
            ).set_stroke(GREEN, 7)
            text = Text("a different way back", font_size=28).set_color(GREEN)
        else:
            mark = VGroup(Line(UL, DR), Line(UR, DL)).scale(0.17).set_stroke(RED, 7)
            text = Text("the same way back", font_size=28).set_color(RED)
        group = VGroup(mark, text).arrange(RIGHT, buff=0.18)
        return group.move_to((STEPS_TOP - 0.3) * UP)

    def build_step(self, tex, font_size=44, isolate=()):
        line = Tex(tex, font_size=font_size, isolate=list(isolate))
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.steps().add(line)
        return line

    def rest_of(self, line, *parts):
        """Every glyph of `line` not in one of `parts`."""
        covered = set()
        for part in parts:
            covered.update(part.family_members_with_points())
        return VGroup(*[g for g in line.family_members_with_points() if g not in covered])

    # Sections

    def draw_grid(self):
        self.get_card()
        grid = self.make_grid()
        self.play(ShowCreation(grid.lines, lag_ratio=0.05), run_time=1.4)
        self.play(FadeIn(grid.ends, scale=0.5), FadeIn(grid.labels), run_time=0.5)
        self.set_state("grid", grid)
        self.wait(0.3)

    def examples(self):
        grid = self.get_grid()
        self.note("Along the lines: right/up there,\nleft/down on the way back.", wait=1.2)
        runner = Dot(self.gp(A), radius=0.13).set_color(GO)

        # A round trip that counts...
        go = self.make_path(GO_PATH, GO, 10)
        back = self.make_path(OTHER_PATH[::-1], BACK, 4.5)
        self.add(go, grid.ends, runner)
        self.play(ShowCreation(go), MoveAlongPath(runner, go), run_time=1.3)
        runner.set_color(BACK)
        self.add(back, grid.ends, runner)
        self.play(ShowCreation(back), MoveAlongPath(runner, back), run_time=1.3)
        good = self.verdict(True)
        self.play(FadeIn(good, scale=0.7), run_time=0.4)
        self.wait(0.7)

        # ...and one that doesn't
        same = self.make_path(GO_PATH[::-1], BACK, 4.5)
        self.play(FadeOut(back), FadeOut(good), run_time=0.4)
        self.add(same, grid.ends, runner)
        self.play(ShowCreation(same), MoveAlongPath(runner, same), run_time=1.3)
        bad = self.verdict(False)
        self.play(FadeIn(bad, scale=0.7), run_time=0.4)
        self.wait(0.7)
        self.play(FadeOut(VGroup(go, same, bad, runner)), run_time=0.5)

    def count_ways(self):
        self.get_grid()
        badges = self.get_badges()

        disc, number = badges[A]
        self.play(FadeIn(disc, scale=0.6), Write(number), run_time=0.6)
        self.note(
            "Vertex addition: each point gets the sum\n"
            "of the points that step into it.",
            wait=1.5,
        )

        # One diagonal at a time, so every point's inputs are already known
        waves = [[v for v in VERTICES if sum(v) == d] for d in range(1, 8)]
        for k, wave in enumerate(waves):
            fly, settle, flashes = [], [], []
            for v in wave:
                disc, number = badges[v]
                sources = incoming(v)
                flashes += [self.edge_flash(u, v) for u in sources]
                if len(sources) == 1:
                    # One way in: its count simply carries across
                    fly += [FadeIn(disc, scale=0.6), TransformFromCopy(badges[sources[0]][1], number)]
                    continue
                # Two ways in: the counts meet as a sum, then collapse into it
                left, below = sources
                terms = VGroup(
                    Tex(str(WAYS[left]), font_size=34),
                    Tex("+", font_size=34),
                    Tex(str(WAYS[below]), font_size=34),
                ).arrange(RIGHT, buff=0.08).move_to(self.gp(v))
                backing = BackgroundRectangle(terms, fill_opacity=0.9, buff=0.08)
                fly += [
                    FadeIn(backing),
                    TransformFromCopy(badges[left][1], terms[0]),
                    FadeIn(terms[1]),
                    TransformFromCopy(badges[below][1], terms[2]),
                ]
                settle += [FadeIn(disc, scale=0.6), FadeTransform(VGroup(backing, terms), number)]
            self.play(*fly, *flashes, run_time=1.1 if k < 3 else 0.95)
            if settle:
                self.play(*settle, run_time=0.7)
            self.wait(0.3)

        self.play(
            Flash(badges[B], color=GO, flash_radius=0.45),
            badges[B].animate.scale(1.25),
            run_time=0.8,
        )
        self.set_state("badges", VGroup(*badges.values()))

    def round_trip(self):
        grid = self.get_grid()
        self.lazy("badges", lambda: VGroup(*self.get_badges().values()))
        b_count = self.get_badges()[B][1]

        # There: the 17 is read straight off B
        there = self.build_step(R"A \to B:\ \ 17", isolate=["17"])
        there["17"][0].set_color(GO)
        self.play(
            FadeIn(self.rest_of(there, there["17"][0])),
            TransformFromCopy(b_count, there["17"][0]),
            run_time=0.9,
        )

        # Back: any of those 17, except the one just used.  `{}` keeps the
        # minus binary once isolated.
        self.note("Back: any of the 17, except the way you came.", wait=1.2)
        used = self.make_path(GO_PATH, GO, 10)
        back = self.build_step(R"B \to A:\ \ 17 {}- 1 = 16", isolate=["17", "{}- 1", "16"])
        back["{}- 1"][0].set_color(GO)
        back["16"][0].set_color(BACK)
        self.add(used, grid.ends, *self.get_badges().values())
        self.play(
            ShowCreation(used),
            TransformFromCopy(there["17"][0], back["17"][0]),
            FadeIn(self.rest_of(back, back["17"][0])),
            run_time=1.2,
        )
        self.play(
            FlashAround(back["{}- 1"][0], color=GO, time_width=1.5),
            used.animate.set_stroke(opacity=0.35),
            run_time=0.9,
        )

        # Multiply
        total = self.build_step(R"17 \times 16 = 272", font_size=52, isolate=["17", "16", "272"])
        total["272"][0].set_color(RESULT_COLOR)
        self.play(
            TransformFromCopy(there["17"][0], total["17"][0]),
            TransformFromCopy(back["16"][0], total["16"][0]),
            FadeIn(self.rest_of(total, total["17"][0], total["16"][0], total["272"][0])),
            run_time=1.0,
        )
        self.play(Write(total["272"][0]), run_time=0.6)
        box = SurroundingRectangle(total, color=RESULT_COLOR, buff=0.2).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(total, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.wait(2.0)
