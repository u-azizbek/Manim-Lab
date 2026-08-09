from manim_imports_ext import *


SETUP_COLOR = "#7FB3FF"
RULE_COLOR = "#5BD98A"
WORK_COLOR = WHITE
RESULT_COLOR = YELLOW


class FTCLimit(BrandOutroMixin, CardSolutionScene):
    # Render with:
    #   ./render.sh _2026/Limits/ftc_limit.py
    # or one beat with:
    #   ./render.sh -s apply_ftc _2026/Limits/ftc_limit.py
    problem_tex = (
        R"\lim_{x \to 1} \frac{1}{x^2 - 1}\int_2^{2x}\left(2t^3 - 5t + 1\right) dt"
    )
    card_font_size = 42
    card_width = 7.3
    steps_top_y = 3.9
    step_buff = 0.40
    step_font_size = 36

    sections = [
        "pose",
        "spot_indeterminate",
        "state_ftc",
        "apply_ftc",
        "finish",
        "outro",
    ]

    def pose(self):
        self.show_problem()

    def spot_indeterminate(self):
        self.get_card()
        self.add_step(
            R"x \to 1: \quad \int_2^{2} (\cdots)\, dt = 0, \quad x^2 - 1 = 0",
            color=SETUP_COLOR, font_size=34,
        )
        # NB: `\;` immediately before `\text{}` breaks manimgl's Tex parser
        form = self.add_step(R"\tfrac{0}{0} \quad \text{indeterminate form}",
                             color=SETUP_COLOR, wait=0.2)
        self.play(FlashAround(form, color=SETUP_COLOR, time_width=1.5), run_time=1.2)
        self.wait(0.3)

    def state_ftc(self):
        self.get_card()
        rule = self.add_step(
            R"\frac{d}{dx}\int_a^{u(x)} f(t)\, dt = f\big(u(x)\big)\cdot u'(x)",
            color=RULE_COLOR, wait=0.2,
        )
        box = SurroundingRectangle(rule, color=RULE_COLOR, buff=0.18)
        box.set_stroke(width=2)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(0.7)
        self.set_state("ftc_box", box)

    def apply_ftc(self):
        self.get_card()
        self.lazy("ftc_box", self.make_ftc_box)
        # u(x) = 2x, so u'(x) = 2
        self.add_step(
            R"\frac{d}{dx}\int_2^{2x} \left(2t^3 - 5t + 1\right) dt"
            R"= \left(2(2x)^3 - 5(2x) + 1\right)\cdot 2",
            font_size=31,
        )
        self.add_step(R"= 2\left(16x^3 - 10x + 1\right)", font_size=38)

    def finish(self):
        self.get_card()
        self.lazy("ftc_box", self.make_ftc_box)
        self.add_step(
            R"\lim_{x \to 1} \frac{2\left(16x^3 - 10x + 1\right)}{2x}"
            R"= \frac{2(16 - 10 + 1)}{2}",
            font_size=34,
        )
        answer = self.add_step(R"= \frac{14}{2} = 7", color=RESULT_COLOR,
                               font_size=52, wait=0.2)
        box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.22)
        box.set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(answer, color=RESULT_COLOR, time_width=1.5), run_time=1.4)
        self.wait(1.4)

    def make_ftc_box(self):
        rule = Tex(
            R"\frac{d}{dx}\int_a^{u(x)} f(t)\, dt = f\big(u(x)\big)\cdot u'(x)",
            font_size=self.step_font_size,
        )
        rule.set_color(RULE_COLOR)
        rule.set_max_width(self.step_max_width)
        self.place_step(rule)
        self.steps().add(rule)
        box = SurroundingRectangle(rule, color=RULE_COLOR, buff=0.18)
        box.set_stroke(width=2)
        return VGroup(rule, box)
