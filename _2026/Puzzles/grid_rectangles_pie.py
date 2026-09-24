from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Puzzles/grid_rectangles_pie.py
#
# A 5 x 7 grid has two coloured cells, A (row 2, column 2) and B (row 4,
# column 5).  How many rectangles made of grid cells contain at least one?
#
# A rectangle is two horizontal grid lines and two vertical ones.  It holds a
# cell exactly when one horizontal line is above the cell and the other below,
# and likewise left and right, so the choices multiply:
#   |A| = (2 * 4)(2 * 6) = 96,  |B| = (4 * 2)(5 * 3) = 120,
#   |A and B| = (2 * 2)(2 * 3) = 24   (lines outside the box spanning both).
# Inclusion-exclusion: 96 + 120 - 24 = 192.  Checked by brute force over all
# 420 rectangles.

ROWS, COLS = 5, 7
UNIT = 0.9
GRID_CENTER = 1.55 * UP

CELLS = {"A": (2, 2), "B": (4, 5)}      # (row, column), counted from the top left

GRID_COLOR = "#9FB3C8"
CELL_COLOR = "#3B82F6"
TOP = "#5BD98A"
BOTTOM = "#FF9F43"
LEFT_SIDE = "#C39BFF"
RIGHT_SIDE = "#FF6B9A"
SAMPLE = YELLOW
NO = "#FF5C5C"


def line_choices(cells):
    """Grid lines a rectangle can use and still hold every cell in `cells`:
    horizontal ones above / below, vertical ones left / right."""
    rows = [r for r, c in cells]
    cols = [c for r, c in cells]
    return (
        list(range(0, min(rows))), list(range(max(rows), ROWS + 1)),
        list(range(0, min(cols))), list(range(max(cols), COLS + 1)),
    )


class GridRectanglesPIE(MockTestShort):
    """Rectangles holding at least one of two cells, by inclusion-exclusion."""

    test = ""
    card_top_buff = 0.7
    step_buff = 0.4

    problem_tex = (
        R"\text{A } 5 \times 7 \text{ grid has two blue cells.}\\"
        R"\text{How many rectangles contain}\\"
        R"\text{at least one blue cell?}"
    )

    sections = [
        "pose",
        "draw_grid",
        "examples",
        "count_a",
        "count_b",
        "count_both",
        "combine",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = self.grid_point(ROWS, 0)[1] - 0.95
        return card

    # Grid geometry: horizontal line i runs along the top of row i + 1,
    # vertical line j along the left of column j + 1

    def grid_point(self, i, j):
        corner = GRID_CENTER + 0.5 * UNIT * (COLS * LEFT + ROWS * UP)
        return corner + UNIT * (j * RIGHT + i * DOWN)

    def h_line(self, i):
        return Line(self.grid_point(i, 0), self.grid_point(i, COLS))

    def v_line(self, j):
        return Line(self.grid_point(0, j), self.grid_point(ROWS, j))

    def box(self, top, bottom, left, right):
        return Polygon(
            self.grid_point(top, left), self.grid_point(top, right),
            self.grid_point(bottom, right), self.grid_point(bottom, left),
        )

    def make_grid(self):
        lines = VGroup(
            *[self.h_line(i) for i in range(ROWS + 1)],
            *[self.v_line(j) for j in range(COLS + 1)],
        ).set_stroke(GRID_COLOR, 2)
        cells = VGroup()
        for name, (r, c) in CELLS.items():
            square = self.box(r - 1, r, c - 1, c).set_stroke(width=0).set_fill(CELL_COLOR, 0.85)
            letter = Tex(name, font_size=38).move_to(square)
            cells.add(VGroup(square, letter))
        grid = VGroup(cells, lines)
        grid.lines, grid.cells = lines, cells
        return grid

    def get_grid(self):
        return self.lazy("grid", self.make_grid)

    def make_sample(self, top, bottom, left, right):
        """A rectangle whose sides slide along the grid lines."""
        sides = [ValueTracker(v) for v in (top, bottom, left, right)]
        rect = always_redraw(lambda: self.box(*[s.get_value() for s in sides]).set_stroke(
            SAMPLE, 6).set_fill(SAMPLE, 0.14))
        rect.sides = sides
        return rect

    def move_sample(self, rect, target, run_time=0.6):
        self.play(
            *[s.animate.set_value(v) for s, v in zip(rect.sides, target)],
            run_time=run_time,
        )

    # Sections

    def draw_grid(self):
        self.get_card()
        grid = self.make_grid()
        self.play(ShowCreation(grid.lines, lag_ratio=0.05), run_time=1.2)
        self.play(
            LaggedStart(*[FadeIn(cell, scale=0.6) for cell in grid.cells], lag_ratio=0.4),
            run_time=0.9,
        )
        self.set_state("grid", grid)
        self.wait(0.3)

    def examples(self):
        grid = self.get_grid()

        # Holds A, holds both, holds neither
        rect = self.make_sample(0, 3, 1, 3)
        verdict = VGroup()
        self.play(FadeIn(rect), run_time=0.5)
        for target, ok in [((0, 3, 1, 3), True), ((1, 4, 1, 6), True), ((2, 5, 0, 3), False)]:
            self.move_sample(rect, target, run_time=0.6)
            mark = Tex(R"\checkmark" if ok else R"\times", font_size=60)
            mark.set_color(SAMPLE if ok else NO)
            mark.next_to(self.grid_point(0, COLS), RIGHT, buff=0.12)
            mark.set_y(self.grid_point((target[0] + target[1]) / 2, 0)[1])
            self.play(FadeTransform(verdict, mark), run_time=0.35)
            verdict = mark
            self.wait(0.45)
        self.play(FadeOut(rect), FadeOut(verdict), run_time=0.4)

        # Any two horizontal and two vertical lines fence off one rectangle
        pair_h = VGroup(self.h_line(1), self.h_line(3)).set_stroke(TOP, 6)
        pair_v = VGroup(self.v_line(2), self.v_line(5)).set_stroke(LEFT_SIDE, 6)
        fenced = self.box(1, 3, 2, 5).set_stroke(SAMPLE, 6).set_fill(SAMPLE, 0.14)
        self.play(ShowCreation(pair_h, lag_ratio=0.3), run_time=0.6)
        self.play(ShowCreation(pair_v, lag_ratio=0.3), run_time=0.6)
        self.play(FadeIn(fenced), run_time=0.4)
        self.note("A rectangle = 2 horizontal + 2 vertical grid lines.", wait=1.2)
        self.play(FadeOut(VGroup(pair_h, pair_v, fenced)), run_time=0.4)

    def count_cells(self, cells, tex, picks, samples, focus):
        """Count the rectangles holding every cell in `cells`: pick a line
        above, below, left and right of them, and multiply the choices.

        `picks` selects the four counts inside `tex`, in the order top,
        bottom, left, right, as (substring, occurrence) pairs.
        """
        grid = self.get_grid()
        tops, bottoms, lefts, rights = line_choices(cells)
        self.play(focus, run_time=0.8)

        # Colour each family of lines and count it
        groups = [
            (tops, self.h_line, TOP), (bottoms, self.h_line, BOTTOM),
            (lefts, self.v_line, LEFT_SIDE), (rights, self.v_line, RIGHT_SIDE),
        ]
        families, counts = VGroup(), VGroup()
        for indices, make, color in groups:
            family = VGroup(*[make(k) for k in indices]).set_stroke(color, 6)
            count = Tex(str(len(indices)), font_size=40).set_color(color)
            if make == self.h_line:
                count.next_to(family, RIGHT, buff=0.22)
            else:
                count.next_to(family, DOWN, buff=0.2)
            families.add(family)
            counts.add(count)
        for pair in [(0, 1), (2, 3)]:
            self.play(
                *[ShowCreation(families[k], lag_ratio=0.2) for k in pair],
                *[FadeIn(counts[k], scale=0.6) for k in pair],
                run_time=0.8,
            )

        # Any one of each works
        rect = self.make_sample(*samples[0])
        self.play(FadeIn(rect), run_time=0.3)
        for target in samples[1:]:
            self.move_sample(rect, target, run_time=0.5)
        self.play(FadeOut(rect), run_time=0.3)

        # The counts drop into the product
        line = Tex(tex, isolate=sorted({s for s, k in picks}), font_size=40)
        parts = [line[s][k] for s, k in picks]
        for part, (_, _, color) in zip(parts, groups):
            part.set_color(color)
        self.place_step(line)
        self.steps().add(line)
        covered = {id(g) for part in parts for g in part.family_members_with_points()}
        rest = VGroup(*[g for g in line.family_members_with_points() if id(g) not in covered])
        self.play(
            *[TransformFromCopy(count, part) for count, part in zip(counts, parts)],
            FadeIn(rest),
            run_time=1.1,
        )
        self.play(FadeOut(families), FadeOut(counts), run_time=0.4)
        return line

    def result_of(self, line, digits):
        line.result = line[-digits:]
        self.play(Indicate(line.result, color=YELLOW, scale_factor=1.15), run_time=0.6)
        return line

    def count_a(self):
        grid = self.get_grid()
        cell = grid.cells[0]
        line = self.count_cells(
            [CELLS["A"]], R"|A| = (2 \cdot 4)(2 \cdot 6) = 96",
            [("2", 0), ("4", 0), ("2", 1), ("6", 0)],
            [(1, 2, 1, 2), (0, 5, 0, 4), (1, 3, 0, 7)],
            FlashAround(cell, color=CELL_COLOR),
        )
        self.result_of(line, 2)
        self.note("Choices multiply: the product rule.", wait=1.0)
        self.set_state("count_a", line)

    def count_b(self):
        grid = self.get_grid()
        self.lazy("count_a", lambda: self.add_step(R"|A| = (2 \cdot 4)(2 \cdot 6) = 96", font_size=40, wait=0))
        line = self.count_cells(
            [CELLS["B"]], R"|B| = (4 \cdot 2)(5 \cdot 3) = 120",
            [("4", 0), ("2", 0), ("5", 0), ("3", 0)],
            [(3, 4, 4, 5), (0, 5, 2, 7), (2, 4, 1, 6)],
            FlashAround(grid.cells[1], color=CELL_COLOR),
        )
        self.result_of(line, 3)
        self.set_state("count_b", line)

    def count_both(self):
        grid = self.get_grid()
        self.lazy("count_a", lambda: self.add_step(R"|A| = (2 \cdot 4)(2 \cdot 6) = 96", font_size=40, wait=0))
        self.lazy("count_b", lambda: self.add_step(R"|B| = (4 \cdot 2)(5 \cdot 3) = 120", font_size=40, wait=0))

        # A rectangle holding both cells was counted in |A| and again in |B|
        rect = self.make_sample(1, 4, 1, 5)
        self.play(FadeIn(rect), run_time=0.4)
        twice = Tex(R"\text{in } |A| \text{ and in } |B|", font_size=34).set_color(SAMPLE)
        twice.next_to(self.grid_point(ROWS, 0), DOWN, buff=0.2).set_x(GRID_CENTER[0])
        self.play(FadeIn(twice, 0.1 * UP), run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(rect), FadeOut(twice), run_time=0.4)

        # Such a rectangle must reach round the box spanning both cells
        span = self.box(1, 4, 1, 5).set_stroke(SAMPLE, 3).set_fill(opacity=0)
        span = DashedVMobject(span, num_dashes=60)
        line = self.count_cells(
            list(CELLS.values()), R"|A \cap B| = (2 \cdot 2)(2 \cdot 3) = 24",
            [("2", 0), ("2", 1), ("2", 2), ("3", 0)],
            [(1, 4, 1, 5), (0, 5, 0, 7), (1, 5, 0, 6)],
            ShowCreation(span),
        )
        self.play(FadeOut(span), run_time=0.3)
        self.result_of(line, 2)
        self.set_state("count_both", line)

    def combine(self):
        self.get_grid()
        lines = [
            self.lazy(name, lambda tex=tex: self.add_step(tex, font_size=40, wait=0))
            for name, tex in [
                ("count_a", R"|A| = (2 \cdot 4)(2 \cdot 6) = 96"),
                ("count_b", R"|B| = (4 \cdot 2)(5 \cdot 3) = 120"),
                ("count_both", R"|A \cap B| = (2 \cdot 2)(2 \cdot 3) = 24"),
            ]
        ]
        results = [line[-digits:] for line, digits in zip(lines, (2, 3, 2))]

        self.note("Inclusion-exclusion: rectangles holding both\nwere counted twice, so subtract them once.", wait=1.6)

        total = Tex(
            R"|A \cup B| = 96 + 120 - 24 = 192",
            isolate=["96", "120", "24", "192"], font_size=46,
        )
        self.place_step(total)
        self.steps().add(total)
        numbers = [total[s][0] for s in ("96", "120", "24")]
        answer = total["192"][0].set_color(RESULT_COLOR)
        covered = {id(g) for part in [*numbers, answer] for g in part.family_members_with_points()}
        rest = VGroup(*[g for g in total.family_members_with_points() if id(g) not in covered])
        self.play(
            *[TransformFromCopy(result, number) for result, number in zip(results, numbers)],
            FadeIn(rest[:-1]),
            run_time=1.3,
        )
        self.play(FadeIn(rest[-1]), Write(answer), run_time=0.7)
        box = SurroundingRectangle(total, color=RESULT_COLOR, buff=0.2).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(answer, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.wait(1.5)
