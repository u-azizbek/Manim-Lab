from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Series/telescoping_floor_sum.py
#
# x_1 = 1/2, x_{n+1} = x_n^2 + x_n.  Find [1/(x_1+1) + ... + 1/(x_n+1)].
# x_{k+1} = x_k (x_k + 1), so 1/x_{k+1} = 1/x_k - 1/(x_k + 1), i.e.
#   1/(x_k + 1) = 1/x_k - 1/x_{k+1}.
# The sum telescopes: S_n = 1/x_1 - 1/x_{n+1} = 2 - 1/x_{n+1}.
# x_2 = 3/4, x_3 = 21/16 > 1 and the sequence increases, so for n >= 2
# 0 < 1/x_{n+1} < 1, 1 < S_n < 2 and [S_n] = 1.  (For n = 1, S_1 = 2/3.)
#
# On a number line term k is a block from 2 - 1/x_k to 2 - 1/x_{k+1}: the
# blocks tile [0, 2) end to end, and the gap left before 2 is 1/x_{n+1}.

N_BLOCKS = 6
XS = [0.5]                          # XS[k] = x_{k+1}
for _ in range(N_BLOCKS):
    XS.append(XS[-1] ** 2 + XS[-1])
EDGES = [2 - 1 / x for x in XS]     # EDGES[k] = S_k, where block k ends

BLOCK_COLORS = ["#58C4DD", "#5BD98A", "#FFD166", "#FF9F43", "#FF6B9A", "#C39BFF"]
FIRST = "#58C4DD"       # 1/x_1, the survivor on the left
LAST = "#FF6B9A"        # 1/x_{n+1}, the survivor on the right, and the gap
PAIR_2 = "#5BD98A"
PAIR_3 = "#FFD166"
PAIR_N = "#C39BFF"
STRIKE = "#FF5E5E"
WALL = "#FF8FB1"

UNIT = 3.2              # length of 1 on the number line
BLOCK_H = 0.6

KEY = R"\frac{1}{x_k+1} = \frac{1}{x_k} - \frac{1}{x_{k+1}}"
KEY_COLORS = {R"\frac{1}{x_k}": FIRST, R"\frac{1}{x_{k+1}}": LAST}
SUM = (
    R"S_n = \left(\frac{1}{x_1} - \frac{1}{x_2}\right) + \left(\frac{1}{x_2} - \frac{1}{x_3}\right)"
    R" + \cdots + \left(\frac{1}{x_n} - \frac{1}{x_{n+1}}\right)"
)
SUM_COLORS = {
    R"\frac{1}{x_1}": FIRST, R"\frac{1}{x_2}": PAIR_2, R"\frac{1}{x_3}": PAIR_3,
    R"\frac{1}{x_n}": PAIR_N, R"\frac{1}{x_{n+1}}": LAST,
}
CLOSED = R"S_n = 2 - \frac{1}{x_{n+1}}"


class TelescopingFloorSum(MockTestShort):
    """The integer part of a telescoping sum, with the terms as blocks on a number line."""

    test = ""
    step_buff = 0.42
    step_font_size = 38
    step_max_width = 7.3

    problem_tex = (
        R"x_1 = \frac{1}{2},\qquad x_{n+1} = x_n^2 + x_n\\"
        R"\text{Find}\ \left[\frac{1}{x_1+1} + \cdots + \frac{1}{x_n+1}\right]\\"
        R"\text{\small ($[x]$ is the integer part of $x$)}"
    )

    sections = ["pose", "identity", "telescope", "bound", "outro"]

    # The number line from 0 to 2, and the blocks on it

    def make_bar(self):
        axis = Line(0.08 * LEFT, 2.14 * UNIT * RIGHT).set_stroke(GREY_B, 3)
        ticks = VGroup(*[
            Line(0.12 * DOWN, 0.12 * UP).move_to(v * UNIT * RIGHT).set_stroke(GREY_B, 3) for v in range(3)
        ])
        labels = VGroup(*[Tex(str(v), font_size=34).next_to(tick, DOWN, buff=0.14) for v, tick in enumerate(ticks)])
        wall = DashedLine(2 * UNIT * RIGHT, 2 * UNIT * RIGHT + 1.0 * UP, dash_length=0.08).set_stroke(WALL, 3)
        anchors = VGroup(Dot(ORIGIN), Dot(2 * UNIT * RIGHT)).set_opacity(0)
        bar = VGroup(axis, ticks, labels, wall, anchors)
        bar.shift(UNIT * LEFT)
        bar.labels, bar.wall, bar.anchors = labels, wall, anchors
        return bar

    def place_bar(self, bar, card):
        """Sit the number line under the card, leaving room for braces above the blocks."""
        axis_y = bar.anchors[0].get_center()[1]
        bar.shift((card.get_bottom()[1] - 1.9 - axis_y) * UP)

    def get_bar(self):
        def build():
            bar = self.make_bar()
            self.place_bar(bar, self.get_card())
            return bar
        bar = self.lazy("bar", build)
        self.steps_top_y = bar.labels.get_bottom()[1] - 0.6
        return bar

    def on_bar(self, value):
        a0, a2 = [dot.get_center() for dot in self.get_bar().anchors]
        return a0 + (a2 - a0) * value / 2

    def make_block(self, k):
        """Term k: from S_{k-1} to S_k on the number line."""
        left, right = self.on_bar(EDGES[k - 1]), self.on_bar(EDGES[k])
        color = BLOCK_COLORS[k - 1]
        rect = Rectangle(width=right[0] - left[0], height=BLOCK_H)
        rect.set_stroke(color, 2).set_fill(color, 0.45).move_to(left, DL)
        block = VGroup(rect)
        if k <= 3:
            block.add(Tex(Rf"\frac{{1}}{{x_{k}+1}}", font_size=26).move_to(rect))
        return block

    def top_line(self, value0, value1):
        """A horizontal segment along the tops of the blocks, for braces."""
        return Line(self.on_bar(value0) + BLOCK_H * UP, self.on_bar(value1) + BLOCK_H * UP)

    def get_blocks(self):
        return self.lazy("blocks", lambda: VGroup(*[self.make_block(k) for k in range(1, 4)]))

    def get_key(self):
        def build():
            key = Tex(KEY, t2c=KEY_COLORS, font_size=self.step_font_size)
            group = VGroup(key, SurroundingRectangle(key, buff=0.18).set_stroke(RULE_COLOR, 3))
            self.place_step(group)
            self.steps().add(group)
            return group
        return self.lazy("key", build)

    def get_closed(self):
        def build():
            line = Tex(CLOSED, t2c={R"\frac{1}{x_{n+1}}": LAST}, font_size=self.step_font_size)
            self.place_step(line)
            self.steps().add(line)
            return line
        return self.lazy("closed", build)

    def lift_to_top(self, keep, *drop):
        """Clear the given lines and slide `keep` up into the first step slot."""
        self.play(
            *[FadeOut(m, 0.2 * UP) for m in drop],
            keep.animate.set_y(self.steps_top_y - keep.get_height() / 2),
            run_time=0.6,
        )
        self.steps().set_submobjects([keep])

    # Sections

    def pose(self):
        # The thumbnail: title, problem card with the logo, the blocks racing to 2
        card = self.make_card()
        home = card.get_center().copy()
        title = Text("Telescoping Sum", font_size=64, weight=BOLD)
        title.set_color_by_gradient(*BLOCK_COLORS[:3])
        title.move_to(6.25 * UP)
        card.next_to(title, DOWN, buff=0.4)

        bar = self.make_bar()
        bar.next_to(card, DOWN, buff=1.3)
        bar.shift((-UNIT - bar.anchors[0].get_x()) * RIGHT)
        self.lazy_state["bar"] = bar
        blocks = VGroup(*[self.make_block(k) for k in range(1, N_BLOCKS + 1)])
        question = Tex(R"\left[\,S_n\,\right] = \,?", t2c={"?": YELLOW}, font_size=110)
        question.next_to(bar, DOWN, buff=1.1)
        # The badge is built 2 units tall with fixed-width synapse lines; thin them
        # in step with the badge, or at thumbnail size they clot into a tangle
        logo = NeuroEduLogo(height=1.9)
        logo.edges.set_stroke(width=2.2 * logo.get_height() / 2)
        brand = Group(
            logo, Text("@neuroeduz", font_size=48, weight=BOLD).set_color(WHITE),
        ).arrange(RIGHT, buff=0.4).next_to(question, DOWN, buff=1.0)

        self.add(title, card, bar, blocks, question, brand)
        self.wait(2.6)

        # Clear the stage: the card goes up to its pinned spot, the number line under it
        axis_y = bar.anchors[0].get_center()[1]
        settled = card.copy().move_to(home)
        target_y = settled.get_bottom()[1] - 1.9
        self.play(
            FadeOut(title, 0.5 * UP), FadeOut(question, 0.4 * DOWN), FadeOut(brand, 0.4 * DOWN),
            FadeOut(blocks),
            card.animate.move_to(home),
            bar.animate.shift((target_y - axis_y) * UP),
            run_time=1.2,
        )
        self.set_state("card", card)
        self.get_bar()

    def identity(self):
        self.get_card()
        self.get_bar()

        line = self.add_step(R"x_{k+1} = x_k^2 + x_k", wait=0.3)
        line = self.replace_step(line, R"x_{k+1} = x_k(x_k+1)", wait=0.3)
        flip = self.transform_step(line, R"\frac{1}{x_{k+1}} = \frac{1}{x_k(x_k+1)}", run_time=1.1, wait=0.3)
        self.note("Partial fractions:  1/(a(a+1)) = 1/a − 1/(a+1)", wait=1.3)
        flip = self.replace_step(flip, R"\frac{1}{x_{k+1}} = \frac{1}{x_k} - \frac{1}{x_k+1}", wait=0.5)
        key = self.replace_step(flip, KEY, colors=KEY_COLORS, wait=0.2)
        box = SurroundingRectangle(key, buff=0.18).set_stroke(RULE_COLOR, 3)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(0.5)

        group = VGroup(key, box)
        self.lift_to_top(group, line)
        self.set_state("key", group)

    def telescope(self):
        self.get_card()
        self.get_bar()
        self.get_key()

        # Each term is a block on the number line
        sum_def = self.add_step(
            R"S_n = \frac{1}{x_1+1} + \frac{1}{x_2+1} + \cdots + \frac{1}{x_n+1}", wait=0.1,
        )
        blocks = VGroup(*[self.make_block(k) for k in range(1, 4)])
        self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in blocks], lag_ratio=0.6), run_time=1.6)
        self.set_state("blocks", blocks)
        self.note("Rewrite every term with the boxed identity.", wait=0.8)
        line = self.replace_step(sum_def, SUM, colors=SUM_COLORS, wait=0.6)

        # Neighbours cancel in pairs
        cancelled = VGroup(*[line[key] for key in (R"\frac{1}{x_2}", R"\frac{1}{x_3}", R"\frac{1}{x_n}")])
        strikes = VGroup(*[
            Line(part.get_corner(DL), part.get_corner(UR)).set_stroke(STRIKE, 4)
            for group in cancelled for part in group
        ])
        self.play(ShowCreation(strikes, lag_ratio=0.25), cancelled.animate.set_opacity(0.35), run_time=1.2)
        self.note("Telescoping: neighbours cancel, only the two ends survive.", wait=1.1)
        self.play(FadeOut(strikes), run_time=0.3)
        line = self.replace_step(
            line, R"S_n = \frac{1}{x_1} - \frac{1}{x_{n+1}}",
            colors={R"\frac{1}{x_1}": FIRST, R"\frac{1}{x_{n+1}}": LAST}, wait=0.5,
        )
        line = self.replace_step(
            line, CLOSED, colors={R"\frac{1}{x_{n+1}}": LAST},
            key_map={R"\frac{1}{x_1}": "2"}, wait=0.3,
        )

        # On the number line: the blocks run from 0 to 2 - 1/x_{n+1}
        s_brace = Brace(self.top_line(0, EDGES[3]), UP, buff=0.08).set_color(WHITE)
        s_label = Tex("S_n", font_size=36).next_to(s_brace, UP, buff=0.08)
        gap_brace = Brace(self.top_line(EDGES[3], 2), UP, buff=0.08).set_color(LAST)
        gap_label = Tex(R"\frac{1}{x_{n+1}}", font_size=28).set_color(LAST).next_to(gap_brace, UP, buff=0.06)
        self.play(
            GrowFromCenter(s_brace), FadeIn(s_label, 0.1 * UP),
            GrowFromCenter(gap_brace), FadeIn(gap_label, 0.1 * UP),
            run_time=0.8,
        )
        self.wait(1.0)
        self.set_state("closed", line)
        self.set_state("braces", VGroup(s_brace, s_label, gap_brace, gap_label))

    def bound(self):
        self.get_card()
        self.get_bar()
        self.get_blocks()
        key = self.get_key()
        closed = self.get_closed()
        braces = self.lazy("braces", VGroup)
        self.lift_to_top(closed, key)

        # The first terms, and the sequence only grows
        self.add_step(R"x_1 = \frac{1}{2},\quad x_2 = \frac{3}{4},\quad x_3 = \frac{21}{16} > 1", wait=0.4)
        self.note("x only grows, so for n ≥ 2 the gap is less than 1.", wait=1.1)
        gap = self.add_step(
            R"n \ge 2:\quad 0 < \frac{1}{x_{n+1}} < 1", t2c={R"\frac{1}{x_{n+1}}": LAST}, wait=0.2,
        )
        if len(braces) == 4:
            self.play(Indicate(braces[2:], color=LAST), run_time=0.8)
        gap = self.replace_step(
            gap, R"1 < 2 - \frac{1}{x_{n+1}} < 2", colors={R"\frac{1}{x_{n+1}}": LAST}, wait=0.4,
        )
        gap = self.replace_step(gap, R"1 < S_n < 2", wait=0.2)

        # The blocks creep towards 2 but never reach it: S_n stays in (1, 2)
        interval = Line(self.on_bar(1), self.on_bar(2)).set_stroke(YELLOW, 8)
        more = VGroup(*[self.make_block(k) for k in range(4, N_BLOCKS + 1)])
        self.play(FadeOut(braces), ShowCreation(interval), run_time=0.6)
        self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in more], lag_ratio=0.5), run_time=1.3)
        self.play(Indicate(self.get_bar().wall, color=WALL), run_time=0.7)

        self.conclude(R"\left[S_n\right] = 1 \quad (n \ge 2)", font_size=52, wait=1.4)
