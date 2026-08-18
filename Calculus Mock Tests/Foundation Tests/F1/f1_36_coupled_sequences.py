from manim_imports_ext import *


class F1Q36(MockTestShort):
    # Render with:
    #   ./render.sh "Calculus Mock Tests/Foundation Tests/F1/f1_36_coupled_sequences.py"
    test = "F1"
    question = 36
    step_buff = 0.85

    problem_tex = (
        R"a_1 = 5, \quad b_1 = 8 \\"
        R"a_{n+1} = 4b_n + 3, \quad b_{n+1} = 4a_n - 6 \\"
        R"\lim_{n \to \infty} \frac{a_n + b_n}{4^n} = \, ?"
    )

    sections = [
        "pose",
        "name_the_sum",
        "add_the_two",
        "solve_it",
        "finish",
        "outro",
    ]

    def name_the_sum(self):
        self.get_card()
        # Neither sequence is nice on its own, but their sum closes up
        self.add_step(
            R"s_n = a_n + b_n, \quad s_1 = 13",
            color=SETUP_COLOR, font_size=44, wait=0.9,
        )

    def add_the_two(self):
        self.get_card()
        added = self.add_step(
            R"s_{n+1} = (4b_n + 3) + (4a_n - 6) = 4s_n - 3",
            color=RULE_COLOR, font_size=38, wait=0.2,
        )
        box = SurroundingRectangle(added, color=RULE_COLOR, buff=0.18)
        box.set_stroke(width=2)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(1.0)

    def solve_it(self):
        self.get_card()
        shifted = self.add_step(
            R"s_{n+1} - 1 = 4 \, (s_n - 1)",
            font_size=42, wait=0.9,
        )
        self.transform_step(
            shifted,
            R"s_n - 1 = 12 \cdot 4^{\,n-1} = 3 \cdot 4^n",
            font_size=42, wait=1.0,
        )

    def finish(self):
        self.get_card()
        self.add_step(
            R"\frac{a_n + b_n}{4^n} = 3 + \frac{1}{4^n}",
            font_size=44, wait=0.9,
        )
        self.conclude(R"\longrightarrow \; 3")
