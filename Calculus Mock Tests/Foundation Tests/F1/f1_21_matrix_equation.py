from manim_imports_ext import *


class F1Q21(MockTestShort):
    # Render with:
    #   ./render.sh "Calculus Mock Tests/Foundation Tests/F1/f1_21_matrix_equation.py"
    test = "F1"
    question = 21
    step_buff = 0.58

    problem_tex = (
        R"A = \begin{pmatrix} 3 & 2 \\ -1 & 4 \end{pmatrix}, \quad "
        R"B = \begin{pmatrix} 12 & 1 \\ 10 & -5 \end{pmatrix} \\"
        R"AX = B \\"
        R"\text{sum of entries of } X = \, ?"
    )

    sections = [
        "pose",
        "isolate_x",
        "invert_a",
        "multiply_out",
        "finish",
        "outro",
    ]

    def isolate_x(self):
        self.get_card()
        self.add_step(
            R"AX = B \quad \Longrightarrow \quad X = A^{-1}B",
            color=SETUP_COLOR, font_size=40, wait=0.8,
        )

    def invert_a(self):
        self.get_card()
        det = self.add_step(
            R"\det A = 3 \cdot 4 - 2 \cdot (-1) = 14",
            font_size=38, wait=0.7,
        )
        inverse = self.transform_step(
            det,
            R"A^{-1} = \frac{1}{14} \begin{pmatrix} 4 & -2 \\ 1 & 3 \end{pmatrix}",
            color=RULE_COLOR, font_size=38, wait=0.2,
        )
        box = SurroundingRectangle(inverse, color=RULE_COLOR, buff=0.18)
        box.set_stroke(width=2)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(0.9)

    def multiply_out(self):
        self.get_card()
        product = self.add_step(
            R"X = \frac{1}{14} \begin{pmatrix} 4 & -2 \\ 1 & 3 \end{pmatrix}"
            R"\begin{pmatrix} 12 & 1 \\ 10 & -5 \end{pmatrix}",
            font_size=34, wait=0.8,
        )
        self.transform_step(
            product,
            R"= \frac{1}{14} \begin{pmatrix} 28 & 14 \\ 42 & -14 \end{pmatrix}"
            R"= \begin{pmatrix} 2 & 1 \\ 3 & -1 \end{pmatrix}",
            font_size=34, wait=1.0,
        )

    def finish(self):
        self.get_card()
        self.conclude(R"2 + 1 + 3 - 1 = 5")
