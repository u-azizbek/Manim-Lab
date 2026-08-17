from manim_imports_ext import *


TITLE_COLOR = "#7FB3FF"
RESULT_COLOR = YELLOW


# The six diagonals, written once so the bands and the terms cannot drift apart
TWO_POS = [([(0, 0), (1, 1)], "ad")]
TWO_NEG = [([(1, 0), (0, 1)], "bc")]

WIDE_POS = [
    ([(0, 0), (1, 1), (2, 2)], "aei"),
    ([(0, 1), (1, 2), (2, 3)], "bfg"),
    ([(0, 2), (1, 3), (2, 4)], "cdh"),
]
WIDE_NEG = [
    ([(2, 0), (1, 1), (0, 2)], "gec"),
    ([(2, 1), (1, 2), (0, 3)], "hfa"),
    ([(2, 2), (1, 3), (0, 4)], "idb"),
]

TALL_POS = [
    ([(0, 0), (1, 1), (2, 2)], "aei"),
    ([(1, 0), (2, 1), (3, 2)], "dhc"),
    ([(2, 0), (3, 1), (4, 2)], "gbf"),
]
TALL_NEG = [
    ([(2, 0), (1, 1), (0, 2)], "gec"),
    ([(3, 0), (2, 1), (1, 2)], "ahf"),
    ([(4, 0), (3, 1), (2, 2)], "dbi"),
]

FULL_RULE = R"aei + bfg + cdh - gec - hfa - idb"


class SarrusRule(BrandOutroMixin, BandDiagramScene):
    # Render with:
    #   ./render.sh _2026/matrix/sarrus_rule.py
    # or one beat with:
    #   ./render.sh -s wide_arrangement _2026/matrix/sarrus_rule.py
    sections = [
        "pose",
        "two_by_two",
        "wide_arrangement",
        "tall_arrangement",
        "only_two_and_three",
        "outro",
    ]

    # Layout

    def make_title(self):
        title = Text("SARRUS' RULE", font_size=60, weight=BOLD)
        title.set_color(TITLE_COLOR)
        return self.pin_to_top(title, buff=0.55)

    def get_title(self):
        return self.lazy("title", self.make_title)

    def caption(self, words, color=GREY_B, font_size=36):
        line = Text(words, font_size=font_size)
        line.set_color(color)
        line.set_max_width(7.0)
        return line.next_to(self.get_title(), DOWN, buff=0.55)

    # Sections

    def pose(self):
        title = self.get_title()
        subtitle = self.caption("determinants without expanding")

        grid, bars, question = self.build_two()

        self.play(FadeIn(title, 0.2 * DOWN), run_time=0.8)
        self.play(FadeIn(subtitle), run_time=0.6)
        self.play(
            Write(grid.cells, lag_ratio=0.3),
            ShowCreation(bars, lag_ratio=0),
            run_time=1.4,
        )
        self.play(FadeIn(question, 0.2 * LEFT), run_time=0.6)
        self.wait(0.9)

        self.set_state("two", VGroup(grid, bars, question))
        self.set_state("subtitle", subtitle)

    def two_by_two(self):
        two = self.lazy("two", lambda: VGroup(*self.build_two()))
        subtitle = self.lazy(
            "subtitle", lambda: self.caption("determinants without expanding"),
        )
        grid, bars, question = two

        pos_band = grid.bands(TWO_POS, POS_COLOR)
        neg_band = grid.bands(TWO_NEG, NEG_COLOR)

        pos_label = Tex(R"+\,ad", font_size=56).set_color(POS_COLOR)
        pos_label.next_to(VGroup(grid, bars), DOWN, buff=1.4)
        neg_label = Tex(R"-\,bc", font_size=56).set_color(NEG_COLOR)
        neg_label.next_to(pos_label, DOWN, buff=0.8)

        answer = Tex(R"ad - bc", font_size=70)
        answer.set_color(RESULT_COLOR)
        answer.next_to(neg_label, DOWN, buff=1.4)
        answer_box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.28)
        answer_box.set_stroke(width=3)

        self.reveal_bands(pos_band, grid, run_time=0.7)
        self.play(FadeIn(pos_label, 0.2 * UP), run_time=0.6)
        self.wait(0.5)
        self.reveal_bands(neg_band, grid, run_time=0.7)
        self.play(FadeIn(neg_label, 0.2 * UP), run_time=0.6)
        self.wait(0.6)

        self.play(
            FadeTransform(VGroup(pos_label, neg_label).copy(), answer),
            question.animate.set_opacity(0),
            run_time=1.1,
        )
        self.play(ShowCreation(answer_box), run_time=0.5)
        self.wait(1.3)

        self.play(
            FadeOut(subtitle),
            FadeOut(VGroup(
                two, pos_band, neg_band, pos_label, neg_label,
                answer, answer_box,
            ), UP),
            run_time=0.8,
        )

    def wide_arrangement(self):
        caption = self.caption("3 x 3 : repeat the first two columns", color=TITLE_COLOR)

        grid = LetterGrid(["abcab", "defde", "ghigh"], cell_width=1.30, cell_height=1.20)
        bars = grid.bars(0, 2)
        pos_bands = grid.bands(WIDE_POS, POS_COLOR)
        neg_bands = grid.bands(WIDE_NEG, NEG_COLOR)

        pos_terms = terms_of(WIDE_POS, POS_COLOR, font_size=48)
        pos_terms.next_to(grid, DOWN, buff=1.4)
        neg_terms = terms_of(WIDE_NEG, NEG_COLOR, font_size=48)
        neg_terms.next_to(pos_terms, DOWN, buff=0.8)

        rule = Tex(FULL_RULE, font_size=42)
        rule.set_color(RESULT_COLOR)
        rule.set_max_width(7.0)
        rule.next_to(neg_terms, DOWN, buff=1.4)

        self.center_body(
            grid, bars, pos_bands, neg_bands, pos_terms, neg_terms, rule,
            under=caption,
        )
        rule_box = SurroundingRectangle(rule, color=RESULT_COLOR, buff=0.24)
        rule_box.set_stroke(width=3)

        original = grid.sub_grid(range(3), range(3))
        ghost = grid.sub_grid(range(3), (3, 4))
        ghost.set_opacity(0)

        self.play(FadeIn(caption, 0.2 * DOWN), run_time=0.7)
        self.play(
            Write(original, lag_ratio=0.15),
            ShowCreation(bars, lag_ratio=0),
            run_time=1.5,
        )
        self.wait(0.4)
        self.play(ghost.animate.set_opacity(GHOST_OPACITY), run_time=0.9)
        self.wait(0.5)

        self.reveal_bands(pos_bands, grid)
        self.play(FadeIn(pos_terms, 0.2 * UP), run_time=0.8)
        self.wait(0.6)
        self.reveal_bands(neg_bands, grid)
        self.play(FadeIn(neg_terms, 0.2 * UP), run_time=0.8)
        self.wait(0.9)

        self.play(TransformFromCopy(VGroup(pos_terms, neg_terms), rule), run_time=1.2)
        self.play(ShowCreation(rule_box), run_time=0.5)
        self.wait(1.4)

        # The caption fades in place; sliding it up would run it into the title
        self.play(
            FadeOut(caption),
            FadeOut(VGroup(
                grid, bars, pos_bands, neg_bands,
                pos_terms, neg_terms, rule, rule_box,
            ), UP),
            run_time=0.8,
        )

    def tall_arrangement(self):
        caption = self.caption("or repeat the first two rows", color=TITLE_COLOR)

        grid = LetterGrid(
            ["abc", "def", "ghi", "abc", "def"],
            cell_width=1.35, cell_height=1.18, font_size=58,
        )
        bars = grid.bars(0, 2)
        pos_bands = grid.bands(TALL_POS, POS_COLOR)
        neg_bands = grid.bands(TALL_NEG, NEG_COLOR)

        same = Tex(FULL_RULE, font_size=42)
        same.set_color(RESULT_COLOR)
        same.set_max_width(7.0)
        same.next_to(bars, DOWN, buff=1.2)

        note = Text("the same six products", font_size=34)
        note.set_color(GREY_B)
        note.next_to(same, DOWN, buff=0.55)

        self.center_body(grid, bars, pos_bands, neg_bands, same, note, under=caption)

        original = grid.sub_grid(range(3), range(3))
        ghost = grid.sub_grid((3, 4), range(3))
        ghost.set_opacity(0)

        self.play(FadeIn(caption, 0.2 * DOWN), run_time=0.7)
        self.play(
            Write(original, lag_ratio=0.15),
            ShowCreation(bars, lag_ratio=0),
            run_time=1.3,
        )
        self.play(ghost.animate.set_opacity(GHOST_OPACITY), run_time=0.8)
        self.wait(0.4)

        self.reveal_bands(pos_bands, grid, lag_ratio=0.3, run_time=1.3)
        self.reveal_bands(neg_bands, grid, lag_ratio=0.3, run_time=1.3)
        self.wait(0.5)
        self.play(FadeIn(same, 0.2 * UP), run_time=0.9)
        self.play(FadeIn(note), run_time=0.6)
        self.wait(1.5)

        self.play(
            FadeOut(caption),
            FadeOut(VGroup(grid, bars, pos_bands, neg_bands, same, note), UP),
            run_time=0.8,
        )

    def only_two_and_three(self):
        caption = self.caption("but only for these two sizes", color=NEG_COLOR)

        works = Tex(R"n = 2, \quad n = 3 \quad \checkmark", font_size=52)
        works.set_color(POS_COLOR)

        grid = LetterGrid(
            ["abcd", "efgh", "ijkl", "mnop"],
            cell_width=1.00, cell_height=0.95, font_size=44,
        )
        bars = grid.bars(0, 3)
        grid_group = VGroup(grid, bars)
        grid_group.next_to(works, DOWN, buff=1.1)

        fails = Tex(R"n \geq 4 : \text{ Sarrus fails}", font_size=46)
        fails.set_color(NEG_COLOR)
        fails.next_to(grid_group, DOWN, buff=1.1)

        advice = Text("use cofactor expansion or row reduction", font_size=30)
        advice.set_color(GREY_B)
        advice.set_max_width(6.8)
        advice.next_to(fails, DOWN, buff=0.55)

        self.center_body(works, grid_group, fails, advice, under=caption)
        cross = Cross(grid_group)
        cross.set_stroke(NEG_COLOR, 10)

        self.play(FadeIn(caption, 0.2 * DOWN), run_time=0.7)
        self.play(FadeIn(works, 0.2 * UP), run_time=0.8)
        self.wait(0.7)
        self.play(
            Write(grid.cells, lag_ratio=0.05),
            ShowCreation(bars, lag_ratio=0),
            run_time=1.2,
        )
        self.play(ShowCreation(cross), run_time=0.8)
        self.play(FadeIn(fails, 0.2 * UP), run_time=0.8)
        self.wait(0.8)
        self.play(FadeIn(advice), run_time=0.7)
        self.wait(1.8)

    # Rebuilt when an earlier section is not part of the render

    def build_two(self):
        grid = LetterGrid(["ab", "cd"], cell_width=1.6, cell_height=1.5, font_size=72)
        bars = grid.bars(0, 1)
        question = Tex(R"= \, ?", font_size=72)
        question.next_to(bars, RIGHT, buff=0.5)
        VGroup(grid, bars, question).move_to(2.6 * UP)
        return grid, bars, question
