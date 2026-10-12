from manim_imports_ext import *


# Render with:
#   ./render.sh .claude/skills/manim-shorts/templates/formula_hook_short.py
#
# TEMPLATE for the FORMULA HOOK look (silent).  Copy it to
# _2026/<Topic>/<snake_name>.py and replace everything.
#
# Find  sum_{n >= 1} 1 / (n (n + 1)).
# Partial fractions: 1 / (n (n + 1)) = 1/n - 1/(n + 1), so the partial sum
# telescopes to 1 - 1/(N + 1), which tends to 1.
# On a unit bar the terms 1/2, 1/6, 1/12, ... are blocks laid end to end; the
# gap left after N blocks is exactly 1/(N + 1).
# Checked: partial sums at N = 1, 2, 3, 10, 1000 are 0.5, 0.6667, 0.75,
# 0.9091, 0.9990 = 1 - 1/(N + 1).

N_BLOCKS = 7
BAR_WIDTH = 6.4
BAR_Y = 2.0

TERM_C = "#58C4DD"       # the terms of the sum
GAP_C = "#FF6B9A"        # 1/(N+1), the gap
BLOCK_COLORS = color_gradient([TERM_C, "#C39BFF", "#FFD166"], N_BLOCKS)

SUM = R"\sum_{n=1}^{\infty} \frac{1}{n(n+1)}"


class TelescopeFormulaHook(BrandOutroMixin, StepListMixin, ShortsScene):
    """A telescoping sum, opened with the formula itself as the hook."""

    step_font_size = 42
    step_buff = 0.42
    sections = ["hook", "split", "telescope", "picture", "outro"]
    upload = dict(
        title="This Infinite Sum Is Exactly 1",
        description="Partial fractions make this series collapse. A telescoping sum.",
        hashtags=["#math", "#shorts", "#calculus"],
        pinned_comment="Which step surprised you?",
    )

    # Layout

    def make_sum(self):
        return Tex(SUM, t2c={R"\frac{1}{n(n+1)}": TERM_C}, font_size=72)

    def make_header(self):
        header = self.make_sum().set_height(1.5)
        return self.pin_to_top(header, buff=0.7)

    def get_header(self):
        header = self.lazy("header", self.make_header)
        self.steps_top_y = header.get_bottom()[1] - 0.6
        return header

    def bar_point(self, value):
        return np.array([-BAR_WIDTH / 2 + BAR_WIDTH * value, BAR_Y, 0])

    # Sections

    def hook(self):
        """Frame 0: the title, the sum itself huge, the teaser."""
        hook = formula_hook("Infinite Sum", self.make_sum(), "Can you see the answer?")
        self.add(hook)
        self.wait(2.0)
        self.play(FlashAround(hook.formula, color=TERM_C, time_width=1.5), run_time=1.2)
        # Clear the title first, so the formula does not rise through it
        self.play(FadeOut(hook.title, 0.4 * UP), FadeOut(hook.teaser, 0.4 * DOWN), run_time=0.5)
        self.play(Transform(hook.formula, self.make_header()), run_time=0.9)
        self.remove(hook)
        self.add(hook.formula)
        self.set_state("header", hook.formula)
        self.get_header()

    def split(self):
        self.get_header()
        self.note("Partial fractions split each term in two.", wait=1.2)
        self.add_step(R"\frac{1}{n(n+1)} = \frac{1}{n} - \frac{1}{n+1}", wait=0.6)

    def telescope(self):
        self.get_header()
        line = self.add_step(
            R"S_N = \left(1 - \tfrac{1}{2}\right) + \left(\tfrac{1}{2} - \tfrac{1}{3}\right)"
            R" + \cdots + \left(\tfrac{1}{N} - \tfrac{1}{N+1}\right)",
            wait=0.5,
        )
        self.note("Neighbouring terms cancel: the sum telescopes.", wait=1.3)
        self.replace_step(line, R"S_N = 1 - \frac{1}{N+1}", colors={R"\frac{1}{N+1}": GAP_C}, wait=0.6)

    def picture(self):
        self.get_header()
        self.clear_steps()

        # The terms as blocks on a unit bar: what is left is always 1/(N+1)
        frame = Rectangle(width=BAR_WIDTH, height=1.1).move_to(BAR_Y * UP).set_stroke(GREY_B, 2)
        ends = VGroup(
            Tex("0", font_size=36).next_to(frame, DL, buff=0.1).shift(0.25 * RIGHT),
            Tex("1", font_size=36).next_to(frame, DR, buff=0.1).shift(0.25 * LEFT),
        )
        self.play(ShowCreation(frame), FadeIn(ends), run_time=0.6)
        edges = [1 - 1 / (k + 1) for k in range(N_BLOCKS + 1)]
        blocks = VGroup(*[
            Rectangle(width=BAR_WIDTH * (b - a), height=1.1).move_to(self.bar_point((a + b) / 2))
            .set_stroke(BLACK, 1.5).set_fill(color, 0.85)
            for a, b, color in zip(edges[:-1], edges[1:], BLOCK_COLORS)
        ])
        labels = VGroup(*[
            Tex(t, font_size=36).move_to(block)
            for t, block in zip([R"\tfrac{1}{2}", R"\tfrac{1}{6}", R"\tfrac{1}{12}"], blocks)
        ])
        self.play(LaggedStart(*[FadeIn(b, 0.3 * RIGHT) for b in blocks], lag_ratio=0.35), FadeIn(labels), run_time=2.4)
        gap = Brace(Line(self.bar_point(edges[-1]), self.bar_point(1)), UP, buff=0.5).set_color(GAP_C)
        gap_label = Tex(R"\tfrac{1}{N+1} \to 0", font_size=34).set_color(GAP_C).next_to(gap, UP, buff=0.1)
        self.play(GrowFromCenter(gap), FadeIn(gap_label), run_time=0.7)
        self.note("The blocks fill the bar, and the gap shrinks to nothing.", wait=1.4)

        answer = Tex(SUM + " = 1", font_size=58).set_color(YELLOW)
        answer.move_to(0.6 * DOWN)
        self.play(Write(answer), run_time=1.0)
        box = SurroundingRectangle(answer, buff=0.22).set_stroke(YELLOW, 3.5)
        self.play(ShowCreation(box), FlashAround(answer, color=YELLOW, time_width=1.5), run_time=1.2)
        self.wait(1.4)
