from manim_imports_ext import *


FACT_COLOR = BLUE_B
SUB_COLOR = RED_B
RESULT_COLOR = YELLOW


class SubfactorialLimit(ShortsScene):
    # 9:16 portrait for YouTube Shorts.  Render with:
    #   ./render.sh _2026/Limits/subfactorial_limit.py
    # or a single beat with:
    #   ./render.sh -s reveal_answer _2026/Limits/subfactorial_limit.py
    sections = [
        "hook",
        "explain_subfactorial",
        "show_table",
        "derive_formula",
        "reveal_answer",
    ]

    # State shared between sections

    def make_limit_expr(self):
        return Tex(
            R"\lim_{n \to \infty} \frac{n!}{!n}",
            font_size=96,
            t2c={"n!": FACT_COLOR, "!n": SUB_COLOR},
        )

    def make_header(self):
        header = self.make_limit_expr()
        header.set_width(3.0)
        return self.pin_to_top(header, buff=0.5)

    def get_header(self):
        return self.lazy("header", self.make_header)

    def make_series(self):
        series = Tex(
            R"\sum_{k=0}^{\infty} \frac{(-1)^k}{k!} = e^{-1}",
            font_size=52,
            t2c={"e^{-1}": RESULT_COLOR},
        )
        series.set_width(4.6)
        series.next_to(self.get_header(), DOWN, buff=0.9)
        return series

    def get_series(self):
        return self.lazy("series", self.make_series)

    # Sections

    def hook(self):
        expr = self.make_limit_expr()
        expr.set_width(5.5)
        expr.move_to(1.0 * UP)

        tease = Text("Subfactorial Limit", font_size=44, color=GREY_A)
        tease.next_to(expr, UP, buff=1.4)

        question = Text("Does this even converge?", font_size=44, color=RESULT_COLOR)
        question.set_width(6.5)
        question.next_to(expr, DOWN, buff=1.4)

        self.play(Write(expr), run_time=1.2)
        self.play(FadeIn(tease, 0.2 * DOWN), run_time=0.8)
        self.play(FlashAround(expr[R"!n"], color=SUB_COLOR, time_width=1.5), run_time=1.2)
        self.play(FadeIn(question, 0.2 * UP), run_time=0.8)
        self.wait(0.8)

        # Name the two operations
        labels = VGroup(
            TexText(R"$n!$ \; factorial", font_size=42, t2c={"n!": FACT_COLOR}),
            TexText(R"$!n$ \; subfactorial", font_size=42, t2c={"!n": SUB_COLOR}),
        )
        labels.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        labels.next_to(expr, DOWN, buff=1.2)

        self.play(
            FadeOut(tease, UP),
            FadeOut(question, DOWN),
            run_time=0.7,
        )
        self.play(FadeIn(labels, lag_ratio=0.3), run_time=1.0)
        self.wait(1.0)

        self.play(
            FadeOut(labels),
            Transform(expr, self.make_header()),
            run_time=1.0,
        )
        self.set_state("header", expr)

    def explain_subfactorial(self):
        definition = TexText(
            R"$!n$ counts the arrangements\\where nothing sits in its own spot",
            font_size=40,
            t2c={"!n": SUB_COLOR},
        )
        definition.set_width(6.9)
        definition.next_to(self.get_header(), DOWN, buff=0.9)

        example = Tex(R"n = 3", font_size=48)
        example.next_to(definition, DOWN, buff=0.8)

        perms = ["123", "132", "213", "231", "312", "321"]
        perm_mobs = VGroup(*[Tex(p, font_size=54) for p in perms])
        perm_mobs.arrange_in_grid(2, 3, h_buff=1.0, v_buff=0.7)
        perm_mobs.next_to(example, DOWN, buff=0.8)
        for mob, perm in zip(perm_mobs, perms):
            for i, char in enumerate(perm):
                if int(char) == i + 1:
                    mob[i].set_color(RED)

        self.play(FadeIn(definition, 0.2 * DOWN), run_time=1.2)
        self.play(FadeIn(example), run_time=0.6)
        self.play(FadeIn(perm_mobs, lag_ratio=0.15), run_time=1.4)
        self.wait(0.9)

        # Red digits sit in their own spot, so those arrangements are out
        deranged_indices = [3, 4]
        bad = VGroup(*[
            mob for i, mob in enumerate(perm_mobs)
            if i not in deranged_indices
        ])
        good = VGroup(*[perm_mobs[i] for i in deranged_indices])
        crosses = VGroup(*[Cross(mob) for mob in bad])

        self.play(ShowCreation(crosses, lag_ratio=0.2), run_time=1.2)
        self.wait(0.4)

        good.generate_target()
        good.target.set_color(GREEN_B)
        good.target.arrange(RIGHT, buff=1.0)
        good.target.next_to(example, DOWN, buff=0.9)

        count = Tex(R"!3 = 2", font_size=60, color=SUB_COLOR)
        count.next_to(good.target, DOWN, buff=0.9)

        self.play(
            FadeOut(VGroup(bad, crosses)),
            MoveToTarget(good),
            run_time=1.0,
        )
        self.play(Write(count), run_time=0.8)
        self.wait(1.1)

        self.play(
            FadeOut(VGroup(definition, example, good, count), UP),
            run_time=0.8,
        )

    def show_table(self):
        rows = [
            ["n", "2", "3", "4", "5", "6"],
            ["n!", "2", "6", "24", "120", "720"],
            ["!n", "1", "2", "9", "44", "265"],
            ["n!/!n", "2.000", "3.000", "2.667", "2.727", "2.717"],
        ]
        row_colors = [GREY_A, FACT_COLOR, SUB_COLOR, RESULT_COLOR]

        table = VGroup(*[
            Tex(entry, font_size=40).set_color(color)
            for row, color in zip(rows, row_colors)
            for entry in row
        ])
        table.arrange_in_grid(4, 6, h_buff=0.45, v_buff=0.55)
        table.set_width(7.2)
        table.next_to(self.get_header(), DOWN, buff=1.0)

        rule = Line(table.get_left(), table.get_right())
        rule.set_stroke(GREY_D, 2)
        rule.next_to(table[0:6], DOWN, buff=0.2)

        ratio_row = VGroup(*table[18:24])
        ratio_box = SurroundingRectangle(ratio_row, color=RESULT_COLOR, buff=0.2)
        ratio_box.set_stroke(width=2)

        closing_in = Tex(R"\longrightarrow\ 2.718 \ldots ?", font_size=52, color=RESULT_COLOR)
        closing_in.next_to(ratio_box, DOWN, buff=0.9)

        self.play(
            FadeIn(VGroup(*table[0:18]), lag_ratio=0.05),
            ShowCreation(rule),
            run_time=1.8,
        )
        self.wait(0.4)
        self.play(FadeIn(ratio_row, lag_ratio=0.2), run_time=1.4)
        self.play(ShowCreation(ratio_box), run_time=0.6)
        self.wait(0.8)
        self.play(FadeIn(closing_in, 0.2 * LEFT), run_time=1.0)
        self.wait(1.3)

        self.play(
            FadeOut(VGroup(table, rule, ratio_box, closing_in), UP),
            run_time=0.8,
        )

    def derive_formula(self):
        formula = Tex(
            R"!n = n! \sum_{k=0}^{n} \frac{(-1)^k}{k!}",
            font_size=52,
            t2c={"!n": SUB_COLOR},
        )
        formula.set_width(6.4)
        formula.next_to(self.get_header(), DOWN, buff=1.0)

        ratio = Tex(
            R"\frac{n!}{!n} = \frac{1}{\displaystyle\sum_{k=0}^{n} \frac{(-1)^k}{k!}}",
            font_size=52,
        )
        ratio.set_width(4.4)
        ratio.next_to(formula, DOWN, buff=1.2)

        self.play(Write(formula), run_time=1.6)
        self.wait(0.8)
        self.play(TransformFromCopy(formula, ratio), run_time=1.4)
        self.wait(1.2)

        # Second screen: everything now hinges on that one series
        series = self.make_series()

        reason = TexText(
            R"since $e^x = \sum_k x^k/k!$ \, at \, $x = -1$",
            font_size=36,
            color=GREY_B,
        )
        reason.set_width(6.2)
        reason.next_to(series, DOWN, buff=0.5)

        self.play(
            FadeOut(formula, UP),
            FadeOut(ratio, UP),
            run_time=0.8,
        )
        self.play(Write(series), run_time=1.5)
        self.play(FadeIn(reason, 0.2 * DOWN), run_time=0.8)
        self.wait(1.0)
        self.play(FadeOut(reason), run_time=0.5)
        self.set_state("series", series)

    def reveal_answer(self):
        answer = Tex(
            R"\lim_{n \to \infty} \frac{n!}{!n} = \frac{1}{e^{-1}} = e",
            font_size=64,
            t2c={"n!": FACT_COLOR, "!n": SUB_COLOR},
        )
        answer1 = Tex(
            R"\lim_{n \to \infty} \frac{n!}{!n} = e",
            font_size=64,
            t2c={"n!": FACT_COLOR, "!n": SUB_COLOR},
        )
        answer.set_width(6.9)
        answer.next_to(self.get_series(), DOWN, buff=1.2)

        # value = Tex(R"e \approx 2.71828 \ldots", font_size=68, color=RESULT_COLOR)
        answer1.next_to(answer, DOWN, buff=1.1)
        value_box = SurroundingRectangle(answer1, color=RESULT_COLOR, buff=0.3)
        value_box.set_stroke(width=4)

        self.play(Write(answer), run_time=1.8)
        self.wait(0.5)
        self.play(FadeTransform(answer.copy(), answer1), run_time=1.0)
        self.play(ShowCreation(value_box), run_time=0.6)
        self.play(FlashAround(answer1, time_width=1.5), run_time=1.5)
        self.wait(2.0)
