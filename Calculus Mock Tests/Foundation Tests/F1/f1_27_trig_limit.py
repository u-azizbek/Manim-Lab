from manim_imports_ext import *


class F1Q27(MockTestShort):
    # Render with:
    #   ./render.sh "Calculus Mock Tests/Foundation Tests/F1/f1_27_trig_limit.py"
    test = "F1"
    question = 27
    step_buff = 1.00

    problem_tex = (
        R"\lim_{x \to 0} "
        R"\frac{2x^3 + 3 \sin x \, (1 - \cos 2x)}{x (1 - \cos 2x)} = \, ?"
    )

    sections = [
        "pose",
        "key_identity",
        "split_it",
        "each_piece",
        "finish",
        "outro",
    ]

    def key_identity(self):
        self.get_card()
        identity = self.add_step(
            R"1 - \cos 2x = 2 \sin^2 x",
            color=RULE_COLOR, font_size=46, wait=0.2,
        )
        box = SurroundingRectangle(identity, color=RULE_COLOR, buff=0.18)
        box.set_stroke(width=2)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(1.0)

    def split_it(self):
        self.get_card()
        # The second term cancels the awkward factor outright
        self.add_step(
            R"\frac{2x^3 + 3 \sin x (1 - \cos 2x)}{x(1 - \cos 2x)}"
            R"= \frac{2x^3}{x(1 - \cos 2x)} + \frac{3 \sin x}{x}",
            color=SETUP_COLOR, font_size=33, wait=1.1,
        )

    def each_piece(self):
        self.get_card()
        first = self.add_step(
            R"\frac{2x^3}{x \cdot 2\sin^2 x} = \frac{x^2}{\sin^2 x}"
            R"\; \longrightarrow \; 1",
            font_size=42, wait=0.9,
        )
        self.transform_step(
            first,
            R"\frac{3 \sin x}{x} \; \longrightarrow \; 3",
            font_size=42, wait=1.0,
        )

    def finish(self):
        self.get_card()
        self.conclude(R"1 + 3 = 4")
