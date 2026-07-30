from manim_imports_ext import *


class SumSquaresRatio(SplitScreenScene):
    # Beginner vs Pro split-screen short.  Render with:
    #   ./render.sh _2026/Limits/split_screen_limit.py
    # or one beat with:
    #   ./render.sh -s solve_pro _2026/Limits/split_screen_limit.py
    #
    # To reuse this template for another problem, copy this class and change
    # get_problem_tex / beginner_lines / pro_lines.  Set `credit` to your
    # handle to stamp it along the bottom.
    beginner_label = "NAIVE"
    pro_label = "PRO"
    credit = ""
    verdict = "Both ways give 0"

    def get_problem_tex(self):
        return R"\lim_{n \to \infty} \frac{1^2 + 2^2 + \cdots + n^2}{(1 + 2 + \cdots + n)^2}"

    def beginner_lines(self):
        return [
            Tex(R"\sum_{k=1}^{n} k^2 = \frac{n(n+1)(2n+1)}{6}", font_size=40),
            Tex(R"\Big(\sum_{k=1}^{n} k\Big)^2 = \frac{n^2(n+1)^2}{4}", font_size=40),
            Tex(
                R"\text{ratio} = \frac{2(2n+1)}{3n(n+1)} \longrightarrow 0",
                font_size=42,
            ).set_color(self.result_color),
        ]

    def pro_lines(self):
        return [
            Tex(
                R"\frac{1}{n}\sum \Big(\tfrac{k}{n}\Big)^2 \longrightarrow \int_0^1 x^2\,dx = \tfrac{1}{3}",
                font_size=38,
            ),
            Tex(
                R"\frac{1}{n}\sum \tfrac{k}{n} \longrightarrow \int_0^1 x\,dx = \tfrac{1}{2}",
                font_size=38,
            ),
            Tex(
                R"\frac{n^3 \cdot \frac{1}{3}}{\big(n^2 \cdot \frac{1}{2}\big)^2} = \frac{4}{3n} \longrightarrow 0",
                font_size=40,
            ).set_color(self.result_color),
        ]
