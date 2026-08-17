from manim_imports_ext import *


SETUP_COLOR = "#7FB3FF"
RULE_COLOR = "#5BD98A"
RESULT_COLOR = YELLOW


class ConstantIntegralEquation(BrandOutroMixin, CardSolutionScene):
    # Render with:
    #   ./render.sh _2026/Integrals/constant_integral_equation.py
    # or one beat with:
    #   ./render.sh -s solve_for_k _2026/Integrals/constant_integral_equation.py
    problem_tex = (
        R"f(x) = x^2 + 2\int_0^1 f(t) \, dt \\"
        R"\text{Find } f(1)"
    )
    card_font_size = 42
    card_width = 7.3
    # Seven steps have to clear YouTube's bottom UI, so they sit tighter and
    # start higher than the ftc_limit card does
    steps_top_y = 3.7
    step_buff = 0.30
    step_font_size = 36

    sections = [
        "pose",
        "name_the_constant",
        "plug_back_in",
        "solve_for_k",
        "finish",
        "outro",
    ]

    def transform_step(self, source, tex, color=None, font_size=None,
                       run_time=1.4, wait=0.6, **kwargs):
        """Like `add_step`, but grows the new line out of the previous one."""
        line = Tex(tex, font_size=font_size or self.step_font_size, **kwargs)
        line.set_color(color or self.step_color)
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.steps().add(line)
        self.play(TransformFromCopy(source, line), run_time=run_time)
        if wait:
            self.wait(wait)
        return line

    def pose(self):
        self.show_problem()
        self.wait(0.7)

    def name_the_constant(self):
        self.get_card()
        # The whole trick: the integral has no x in it, so it is a number
        constant = self.add_step(
            R"\int_0^1 f(t) \, dt = k \quad \text{(a constant)}",
            color=SETUP_COLOR, font_size=38, wait=0.5,
        )
        self.play(FlashAround(constant, color=SETUP_COLOR, time_width=1.5), run_time=1.3)
        self.wait(0.8)
        self.transform_step(constant, R"f(x) = x^2 + 2k", font_size=40, wait=1.0)

    def plug_back_in(self):
        self.get_card()
        # f is now known up to k, so feed it back through its own integral
        setup = self.add_step(
            R"k = \int_0^1 \left( t^2 + 2k \right) dt",
            color=SETUP_COLOR, wait=1.0,
        )
        self.transform_step(
            setup,
            R"= \left[ \frac{t^3}{3} + 2kt \right]_0^1 = \frac{1}{3} + 2k",
            run_time=1.6, wait=1.1,
        )

    def solve_for_k(self):
        self.get_card()
        equation = self.add_step(
            R"k = \frac{1}{3} + 2k \Longrightarrow k = -\frac{1}{3}",
            color=RULE_COLOR, font_size=38, wait=0.2,
        )
        box = SurroundingRectangle(equation, color=RULE_COLOR, buff=0.18)
        box.set_stroke(width=2)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(1.1)

        self.transform_step(
            equation, R"f(x) = x^2 - \frac{2}{3}", font_size=40, wait=1.1,
        )

    def finish(self):
        self.get_card()
        answer = self.add_step(
            R"f(1) = 1 - \frac{2}{3} = \frac{1}{3}",
            color=RESULT_COLOR, font_size=52, wait=0.2,
        )
        box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.22)
        box.set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(answer, color=RESULT_COLOR, time_width=1.5), run_time=1.4)
        self.wait(1.5)
