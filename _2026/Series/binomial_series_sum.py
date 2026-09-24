from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Series/binomial_series_sum.py
#
# I = 1 + 3/4 + (3*5)/(4*8) + (3*5*7)/(4*8*12) + ...
#
# Read it as a binomial series (1 + x)^n = 1 + nx + n(n-1)/2! x^2 + ...
# Matching the first two terms:  nx = 3/4  and  n(n-1)/2 x^2 = 15/32.
# Squaring the first and dividing:  (n-1)/n = (15/16)/(9/16) = 5/3, so
# n = -3/2 and x = -1/2.  Then (n-k)x = (2k+3)/4, so every later term matches
# too: the k-th is 3*5*...*(2k+1) / (4^k k!) = 3*5*...*(2k+1) / (4*8*...*4k).
# |x| = 1/2 < 1, so  I = (1 - 1/2)^(-3/2) = 2^(3/2) = 2 sqrt(2).
# Checked with exact fractions for the first eight terms, and numerically.

ONE = "#4FD1C5"       # the x term
TWO = "#FF9F43"       # the x^2 term
THREE = "#C39BFF"     # the x^3 term

TABLE_GAP = 0.3           # between the card and the table


def row(tokens, font_size=34, buff=0.14, colors=None):
    """A line of math built from separate pieces, so pieces can fly on their own."""
    pieces = VGroup(*[Tex(t, font_size=font_size) for t in tokens]).arrange(RIGHT, buff=buff)
    for index, color in (colors or {}).items():
        pieces[index].set_color(color)
    return pieces


class BinomialSeriesSum(MockTestShort):
    """A series summed by recognising it as a binomial series."""

    test = ""
    card_top_buff = 0.6
    step_buff = 0.38

    problem_tex = (
        R"I = 1 + \frac{3}{4} + \frac{3\cdot 5}{4\cdot 8}\\"
        R"+ \frac{3\cdot 5\cdot 7}{4\cdot 8\cdot 12} + \cdots\\"
        R"\text{Find } I."
    )

    sections = [
        "pose",
        "binomial",
        "match_terms",
        "solve",
        "check",
        "finish",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.table_top = card.get_bottom()[1] - TABLE_GAP
        self.steps_top_y = self.make_table().get_bottom()[1] - 0.45
        return card

    def piece_step(self, tokens, colors=None, font_size=None):
        """A step line made of pieces, placed in the next step slot."""
        line = row(tokens, font_size or self.step_font_size, colors=colors)
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.steps().add(line)
        return line

    def extend_step(self, line, tokens, colors=None, run_time=0.9, wait=0.5):
        """Carry a piece-built line on with more pieces, keeping what is there."""
        longer = row([p.get_tex() for p in line] + tokens, line[0].font_size)
        for piece, old in zip(longer, line):
            piece.set_color(old.get_color())
        for index, color in (colors or {}).items():
            longer[len(line) + index].set_color(color)
        longer.set_max_width(self.step_max_width)
        longer.move_to(line).set_x(0)
        self.play(
            *[ReplacementTransform(a, b) for a, b in zip(line, longer)],
            FadeIn(longer[len(line):], 0.2 * LEFT, lag_ratio=0.1),
            run_time=run_time,
        )
        steps = list(self.steps().submobjects)
        if line in steps:
            steps[steps.index(line)] = longer
            self.steps().set_submobjects(steps)
        if wait:
            self.wait(wait)
        return longer

    # The two series side by side, term against term

    def make_table(self):
        pairs = [
            ("I", "(1+x)^n"),
            ("1", "1"),
            (R"\frac{3}{4}", "nx"),
            (R"\frac{3\cdot 5}{4\cdot 8}", R"\frac{n(n-1)}{2!}\,x^2"),
            (R"\frac{3\cdot 5\cdot 7}{4\cdot 8\cdot 12}", R"\frac{n(n-1)(n-2)}{3!}\,x^3"),
        ]
        left = VGroup(*[Tex(a, font_size=40) for a, b in pairs])
        right = VGroup(*[Tex(b, font_size=40) for a, b in pairs])
        signs = VGroup(*[Tex(R"\leftrightarrow" if k == 0 else "=", font_size=40) for k in range(len(pairs))])
        rows = VGroup(*[VGroup(a, s, b) for a, s, b in zip(left, signs, right)])
        rows.arrange(DOWN, buff=0.26)
        for a, sign, b in rows:
            a.set_x(-2.25)
            sign.set_x(-0.95)
            b.set_x(1.35)
        # Regroup, so each row's bounding box covers where its parts now sit
        rows = VGroup(*[VGroup(*r) for r in rows])
        rule = Line(3.6 * LEFT, 3.6 * RIGHT).set_stroke(GREY_B, 1.5)
        rule.move_to(midpoint(rows[0].get_bottom(), rows[1].get_top()))
        table = VGroup(rows, rule)
        if not hasattr(self, "table_top"):
            self.make_card()
        table.set_y(self.table_top - table.get_height() / 2)
        table.rows, table.left, table.right, table.signs, table.rule = rows, left, right, signs, rule
        return table

    def get_table(self):
        return self.lazy("table", self.make_table)

    # Sections

    def binomial(self):
        self.get_card()
        table = self.make_table()
        self.play(FadeIn(table.left, lag_ratio=0.15, shift=0.2 * RIGHT), run_time=1.0)
        self.play(ShowCreation(table.rule), Write(table.right), FadeIn(table.signs), run_time=1.5)
        self.note("Binomial series: true for any power n,\nas long as |x| < 1.", wait=1.4)
        self.set_state("table", table)

    def match_terms(self):
        table = self.get_table()
        top, bottom = table.left, table.right

        # Same shape, term by term
        colors = [(2, ONE), (3, TWO), (4, THREE)]
        boxes = VGroup(*[
            SurroundingRectangle(table.rows[k], buff=0.1).set_stroke(color, 2.5).set_fill(color, 0.12)
            for k, color in colors
        ])
        for k, color in colors:
            top[k].set_color(color)
            bottom[k].set_color(color)
        self.play(LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.3), run_time=1.0)
        self.set_state("boxes", boxes)

        # The first two matches give two equations
        first = self.piece_step(["nx", "=", R"\frac{3}{4}"], {0: ONE, 2: ONE})
        self.play(
            TransformFromCopy(bottom[2], first[0]),
            FadeIn(first[1]),
            TransformFromCopy(top[2], first[2]),
            run_time=1.0,
        )
        second = self.piece_step([R"\frac{n(n-1)}{2}x^2", "=", R"\frac{15}{32}"], {0: TWO, 2: TWO})
        self.play(
            TransformFromCopy(bottom[3], second[0]),
            FadeIn(second[1]),
            TransformFromCopy(top[3], second[2]),
            run_time=1.0,
        )
        self.wait(0.4)

    def solve(self):
        steps = self.steps()
        first, second = steps[0], steps[1]

        # Shrink the table up under the card to make room for the algebra
        table = VGroup(self.get_table(), self.lazy("boxes", VGroup))
        lift = (1 - 0.72) * table.get_height()
        self.play(
            table.animate.scale(0.72, about_edge=UP),
            VGroup(first, second).animate.shift(lift * UP),
            run_time=0.8,
        )
        self.steps_top_y += lift
        self.lift = lift

        # Square one, clear the 2 in the other, and divide
        first = self.extend_step(first, [R"\Rightarrow", R"n^2x^2 = \frac{9}{16}"], {1: ONE})
        second = self.extend_step(second, [R"\Rightarrow", R"n(n-1)x^2 = \frac{15}{16}"], {1: TWO})
        self.note("Divide the two: x² and 1/16 cancel.", wait=1.1)
        ratio = self.piece_step([R"\frac{n-1}{n}", "=", R"\frac{15}{9}", "=", R"\frac{5}{3}"])
        self.play(
            TransformFromCopy(VGroup(first[-1], second[-1]), ratio[0]),
            FadeIn(ratio[1:], lag_ratio=0.15),
            run_time=1.1,
        )
        ratio = self.extend_step(ratio, [R"\Rightarrow", R"n = -\tfrac{3}{2}"], {1: YELLOW})
        x_line = self.piece_step(["x", "=", R"\frac{3/4}{n}", "=", R"-\tfrac{1}{2}"], {4: YELLOW})
        self.play(FadeIn(x_line, 0.15 * DOWN, lag_ratio=0.1), run_time=0.9)
        self.wait(0.6)

        # Keep just the two values
        values = row(["n", "=", R"-\tfrac{3}{2}", R",\quad", "x", "=", R"-\tfrac{1}{2}"], 40)
        values[2].set_color(YELLOW)
        values[6].set_color(YELLOW)
        values.move_to(steps[0]).set_x(0)
        self.play(
            ReplacementTransform(ratio[-1], VGroup(*values[:3])),
            ReplacementTransform(x_line[-1], values[6]),
            FadeIn(VGroup(values[3:6])),
            FadeOut(VGroup(*steps[:2], ratio[:-1], x_line[:-1])),
            run_time=1.1,
        )
        self.steps().set_submobjects([values])
        self.wait(0.4)
        self.set_state("values", values)

    def check(self):
        table = self.get_table()
        values = self.lazy("values", VGroup)

        # The algebra is done: give the table its full size back
        lift = getattr(self, "lift", 0)
        if lift:
            self.play(
                VGroup(table, self.lazy("boxes", VGroup)).animate.scale(1 / 0.72, about_edge=UP),
                values.animate.shift(lift * DOWN),
                run_time=0.8,
            )
            self.steps_top_y -= lift
            self.lift = 0

        # With these, (n-1)x = 5/4 and (n-2)x = 7/4: the next term matches too
        self.play(Indicate(table.rows[4], color=THREE, scale_factor=1.05), run_time=0.9)
        self.note("Check the x³ term: nx, (n-1)x, (n-2)x\nare 3/4, 5/4, 7/4.", wait=1.4)
        line = self.add_step(
            R"\tfrac{3}{4}\cdot\tfrac{5}{4}\cdot\tfrac{7}{4}\cdot\tfrac{1}{1\cdot 2\cdot 3}"
            R" = \tfrac{3\cdot 5\cdot 7}{4\cdot 8\cdot 12}\ \checkmark",
            color=THREE, wait=0.6,
        )
        self.note("Every term matches in the same way.", wait=1.0)
        self.play(FadeOut(line), run_time=0.4)
        self.steps().set_submobjects([values])

    def finish(self):
        table = self.get_table()
        values = self.lazy("values", VGroup)

        # So the whole series is (1 + x)^n
        self.note("|x| = 1/2 < 1, so the series converges.", wait=1.1)
        total = self.piece_step(
            ["I", "=", "(1+x)^n", "=", R"\left(1-\tfrac{1}{2}\right)^{-3/2}"], font_size=40,
        )
        self.play(
            TransformFromCopy(table.left[0], total[0]),
            TransformFromCopy(table.right[0], total[2]),
            FadeIn(VGroup(total[1], total[3])),
            run_time=1.0,
        )
        self.play(
            TransformFromCopy(VGroup(values[2], values[6]), total[4]),
            run_time=1.1,
        )
        self.wait(0.4)
        answer = self.piece_step([R"=", R"2^{3/2}", "=", R"2\sqrt{2}"], font_size=46)
        answer.set_color(RESULT_COLOR)
        self.play(FadeIn(answer[:2], 0.2 * DOWN), run_time=0.6)
        self.play(FadeIn(answer[2:], 0.2 * DOWN), run_time=0.6)
        box = SurroundingRectangle(answer[-1], color=RESULT_COLOR, buff=0.16).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(answer[-1], color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.wait(1.5)
