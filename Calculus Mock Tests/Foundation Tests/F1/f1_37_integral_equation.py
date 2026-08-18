from manim_imports_ext import *


class F1Q37(MockTestShort):
    # Render with:
    #   ./render.sh "Calculus Mock Tests/Foundation Tests/F1/f1_37_integral_equation.py"
    test = "F1"
    question = 37
    step_buff = 1.00

    problem_tex = (
        R"\int_0^x (x - t) f(t) \, dt = 2e^{2x} + ax + b \\"
        R"f(0) + a + b = \, ?"
    )

    sections = [
        "pose",
        "differentiate_twice",
        "match_at_zero",
        "read_off_f",
        "finish",
        "outro",
    ]

    def differentiate_twice(self):
        self.get_card()
        # The x inside the integrand comes out, and the xf(x) terms cancel
        rule = self.add_step(
            R"F'(x) = \int_0^x f(t) \, dt, \quad F''(x) = f(x)",
            color=RULE_COLOR, font_size=38, wait=0.2,
        )
        box = SurroundingRectangle(rule, color=RULE_COLOR, buff=0.18)
        box.set_stroke(width=2)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(1.0)

    def match_at_zero(self):
        self.get_card()
        self.add_step(
            R"F(0) = 0 = 2 + b \quad \Longrightarrow \quad b = -2",
            color=SETUP_COLOR, font_size=40, wait=0.9,
        )
        self.add_step(
            R"F'(0) = 0 = 4 + a \quad \Longrightarrow \quad a = -4",
            color=SETUP_COLOR, font_size=40, wait=1.0,
        )

    def read_off_f(self):
        self.get_card()
        self.add_step(
            R"f(x) = F''(x) = 8e^{2x} \quad \Longrightarrow \quad f(0) = 8",
            font_size=36, wait=1.0,
        )

    def finish(self):
        self.get_card()
        self.conclude(R"8 - 4 - 2 = 2")
