from manim_imports_ext import *


TITLE_COLOR = "#7FB3FF"
RESULT_COLOR = YELLOW
TRI_COLOR = "#7FB3FF"

# The vertices, listed downwards with the first one repeated at the bottom
TABLE = [
    ["x_1", "y_1"],
    ["x_2", "y_2"],
    ["x_3", "y_3"],
    ["x_1", "y_1"],
]

# Down-right pairs are added, up-right pairs are subtracted
DOWN_SPEC = [
    ([(0, 0), (1, 1)], "x_1y_2"),
    ([(1, 0), (2, 1)], "x_2y_3"),
    ([(2, 0), (3, 1)], "x_3y_1"),
]
UP_SPEC = [
    ([(1, 0), (0, 1)], "x_2y_1"),
    ([(2, 0), (1, 1)], "x_3y_2"),
    ([(3, 0), (2, 1)], "x_1y_3"),
]

A_TEX = R"a = x_1y_2 + x_2y_3 + x_3y_1"
B_TEX = R"b = x_2y_1 + x_3y_2 + x_1y_3"
AREA_TEX = R"\text{Area} = \frac{1}{2} \left| a - b \right|"
FULL_TEX = (
    R"\text{Area} = \frac{1}{2} \Big| "
    R"x_1y_2 + x_2y_3 + x_3y_1 - x_2y_1 - x_3y_2 - x_1y_3"
    R" \Big|"
)


class TriangleAreaSarrus(BrandOutroMixin, BandDiagramScene):
    # Render with:
    #   ./render.sh _2026/Geometry/triangle_area_sarrus.py
    # or one beat with:
    #   ./render.sh -s down_sum _2026/Geometry/triangle_area_sarrus.py
    sections = [
        "pose",
        "build_table",
        "down_sum",
        "up_sum",
        "finish",
        "outro",
    ]

    # Layout

    def make_title(self):
        title = Text("AREA FROM COORDINATES", font_size=46, weight=BOLD)
        title.set_color(TITLE_COLOR)
        title.set_max_width(7.2)
        return self.pin_to_top(title, buff=0.55)

    def get_title(self):
        return self.lazy("title", self.make_title)

    def caption(self, words, color=GREY_B, font_size=36):
        line = Text(words, font_size=font_size)
        line.set_color(color)
        line.set_max_width(7.0)
        return line.next_to(self.get_title(), DOWN, buff=0.55)

    def swap_caption(self, words, color=GREY_B, run_time=0.6):
        new = self.caption(words, color=color)
        old = self.lazy_state.get("caption")
        if old is None:
            self.play(FadeIn(new, 0.2 * DOWN), run_time=run_time)
        else:
            # Crossfading in place would show both captions at once
            self.play(FadeTransform(old, new), run_time=run_time)
        return self.set_state("caption", new)

    def parts(self):
        """The table and the three result lines, positioned as one block.

        Built once and shared by every solution section, so the lines keep
        their places as they appear one at a time.
        """
        if not hasattr(self, "_parts"):
            grid = LetterGrid(TABLE, cell_width=1.55, cell_height=1.12, font_size=50)
            bars = grid.bars()

            a_line = Tex(A_TEX, font_size=44).set_color(POS_COLOR)
            a_line.set_max_width(6.9)
            a_line.next_to(VGroup(grid, bars), DOWN, buff=1.0)

            b_line = Tex(B_TEX, font_size=44).set_color(NEG_COLOR)
            b_line.set_max_width(6.9)
            b_line.next_to(a_line, DOWN, buff=0.6)

            area = Tex(AREA_TEX, font_size=56).set_color(RESULT_COLOR)
            area.next_to(b_line, DOWN, buff=1.0)

            self.center_body(
                grid, bars, a_line, b_line, area,
                under=self.get_title(), buff=1.9,
            )
            self._parts = (grid, bars, a_line, b_line, area)
        return self._parts

    def get_table(self):
        grid, bars, *_ = self.parts()
        return self.lazy("table", lambda: VGroup(grid, bars))

    # Sections

    def make_figure(self):
        a_pt = np.array([-1.75, -1.50, 0.0])
        b_pt = np.array([2.00, -1.00, 0.0])
        c_pt = np.array([0.20, 1.80, 0.0])

        triangle = Polygon(a_pt, b_pt, c_pt)
        triangle.set_stroke(TRI_COLOR, 4)
        triangle.set_fill(TRI_COLOR, 0.15)

        dots = VGroup(*[Dot(point, radius=0.075) for point in (a_pt, b_pt, c_pt)])
        dots.set_color(WHITE)

        labels = VGroup(
            Tex(R"A(x_1, y_1)", font_size=34).next_to(a_pt, DL, buff=0.18),
            Tex(R"B(x_2, y_2)", font_size=34).next_to(b_pt, DR, buff=0.18),
            Tex(R"C(x_3, y_3)", font_size=34).next_to(c_pt, UP, buff=0.22),
        )
        return VGroup(triangle, dots, labels)

    def pose(self):
        title = self.get_title()
        self.play(FadeIn(title, 0.2 * DOWN), run_time=0.8)
        self.swap_caption("three corners, no base and no height")

        figure = self.make_figure()
        triangle, dots, labels = figure
        question = Tex(R"\text{Area} = \, ?", font_size=60)
        question.next_to(figure, DOWN, buff=1.1)

        self.center_body(figure, question, under=self.lazy_state["caption"])

        self.play(ShowCreation(triangle), run_time=1.5)
        self.play(
            LaggedStartMap(FadeIn, dots, scale=0.5, lag_ratio=0.2),
            LaggedStartMap(FadeIn, labels, lag_ratio=0.2),
            run_time=1.3,
        )
        self.wait(0.6)
        self.play(FadeIn(question, 0.2 * UP), run_time=0.8)
        self.play(FlashAround(question, color=RESULT_COLOR, time_width=1.5), run_time=1.3)
        self.wait(0.9)

        self.play(FadeOut(VGroup(figure, question), UP), run_time=0.8)

    def build_table(self):
        self.swap_caption("list the corners, repeat the first", color=TITLE_COLOR)

        grid, bars, *_ = self.parts()
        original = grid.sub_grid(range(3), range(2))
        ghost = grid.sub_grid((3,), range(2))
        ghost.set_opacity(0)

        self.play(
            Write(original, lag_ratio=0.15),
            ShowCreation(bars, lag_ratio=0),
            run_time=1.6,
        )
        self.wait(0.5)
        self.play(ghost.animate.set_opacity(GHOST_OPACITY), run_time=0.9)
        self.wait(1.0)
        self.set_state("table", VGroup(grid, bars))

    def down_sum(self):
        self.get_table()
        self.swap_caption("down to the right: add", color=POS_COLOR)

        grid, _, a_line, _, _ = self.parts()
        bands = grid.bands(DOWN_SPEC, POS_COLOR)

        self.reveal_bands(bands, grid)
        self.wait(0.4)
        self.play(FadeIn(a_line, 0.2 * UP), run_time=0.9)
        self.wait(1.1)
        self.set_state("down_bands", bands)

    def up_sum(self):
        self.get_table()
        self.swap_caption("up to the right: subtract", color=NEG_COLOR)

        grid, _, a_line, b_line, _ = self.parts()
        self.lazy("a_line", lambda: a_line)
        self.lazy("down_bands", lambda: grid.bands(DOWN_SPEC, POS_COLOR))

        bands = grid.bands(UP_SPEC, NEG_COLOR)
        self.reveal_bands(bands, grid)
        self.wait(0.4)
        self.play(FadeIn(b_line, 0.2 * UP), run_time=0.9)
        self.wait(1.1)
        self.set_state("up_bands", bands)

    def finish(self):
        grid, bars, a_line, b_line, area = self.parts()
        self.get_table()
        self.lazy("a_line", lambda: a_line)
        self.lazy("b_line", lambda: b_line)
        down_bands = self.lazy("down_bands", lambda: grid.bands(DOWN_SPEC, POS_COLOR))
        up_bands = self.lazy("up_bands", lambda: grid.bands(UP_SPEC, NEG_COLOR))
        caption = self.lazy_state.get("caption")

        area_box = SurroundingRectangle(area, color=RESULT_COLOR, buff=0.26)
        area_box.set_stroke(width=3)

        self.play(TransformFromCopy(VGroup(a_line, b_line), area), run_time=1.3)
        self.play(ShowCreation(area_box), run_time=0.5)
        self.wait(1.4)

        # Clear the working, and answer the opening question next to the figure
        # that asked it
        recap = self.make_figure()
        full = Tex(FULL_TEX, font_size=34)
        full.set_color(RESULT_COLOR)
        full.set_max_width(7.2)
        full.next_to(recap, DOWN, buff=1.2)

        note = Text("the absolute value keeps it positive", font_size=30)
        note.set_color(GREY_B)
        note.set_max_width(6.6)
        note.next_to(full, DOWN, buff=1.0)

        self.center_body(recap, full, note, under=self.get_title(), buff=1.2)
        full_box = SurroundingRectangle(full, color=RESULT_COLOR, buff=0.28)
        full_box.set_stroke(width=4)

        leaving = VGroup(grid, bars, down_bands, up_bands, a_line, b_line)
        exits = [FadeOut(leaving, UP), ReplacementTransform(area, full), FadeOut(area_box)]
        if caption is not None:
            exits.append(FadeOut(caption))
        self.play(*exits, run_time=1.4)

        self.play(ShowCreation(full_box), run_time=0.6)
        self.play(FadeIn(recap), run_time=0.9)
        self.play(FlashAround(full, color=RESULT_COLOR, time_width=1.5), run_time=1.5)
        self.play(FadeIn(note), run_time=0.7)
        self.wait(1.7)
