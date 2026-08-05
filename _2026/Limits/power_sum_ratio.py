from manim_imports_ext import *


NOOB_COLOR = "#FF5C39"
PRO_COLOR = "#39D353"
EXPERT_COLOR = "#C084FC"

LINE_SIZE = 34
RESULT_SIZE = 36


class PowerSumRatio(SplitScreenScene):
    """Shared problem and methods for both cuts.

    Two shorts come out of this file:
        ./render.sh _2026/Limits/power_sum_ratio.py NoobVsPro
        ./render.sh _2026/Limits/power_sum_ratio.py ProVsExpert
    """

    def get_problem_tex(self):
        return R"\lim_{n \to \infty} \frac{1^5 + 2^5 + 3^5 + \cdots + n^5}{n^6 + n^3 + 1}"

    # ---- the three methods ----

    def closed_form_lines(self):
        """Noob: quote the closed form for the sum of fifth powers."""
        return [
            Tex(R"\sum_{k=1}^{n} k^5 = \frac{n^2(n+1)^2(2n^2+2n-1)}{12}",
                font_size=LINE_SIZE),
            Tex(R"\Rightarrow \quad \sum_{k=1}^{n} k^5 \sim \frac{2n^6}{12} = \frac{n^6}{6}",
                font_size=LINE_SIZE),
            Tex(R"\lim_{n \to \infty} \frac{n^6/6}{n^6+n^3+1} = \frac{1}{6}",
                font_size=RESULT_SIZE).set_color(self.result_color),
        ]

    def riemann_lines(self):
        """Pro: read the sum as a Riemann sum."""
        return [
            Tex(R"\frac{1}{n}\sum_{k=1}^{n}\Big(\frac{k}{n}\Big)^5"
                R"\longrightarrow \int_0^1 x^5\,dx = \frac{1}{6}",
                font_size=LINE_SIZE),
            Tex(R"\Rightarrow \quad \sum_{k=1}^{n} k^5 \sim \frac{n^6}{6}",
                font_size=LINE_SIZE),
            Tex(R"\lim_{n \to \infty} \frac{n^6/6}{n^6+n^3+1} = \frac{1}{6}",
                font_size=RESULT_SIZE).set_color(self.result_color),
        ]

    def growth_lines(self):
        """Expert: only the leading order matters."""
        return [
            Tex(R"\sum_{k=1}^{n} k^m \approx \frac{n^{m+1}}{m+1}",
                font_size=LINE_SIZE + 4),
            Tex(R"m = 5 \quad \Rightarrow \quad \sum_{k=1}^{n} k^5 \approx \frac{n^6}{6}",
                font_size=LINE_SIZE),
            Tex(R"\lim_{n \to \infty} \frac{n^6/6}{n^6} = \frac{1}{6}",
                font_size=RESULT_SIZE + 6).set_color(self.result_color),
        ]


class NoobVsPro(PowerSumRatio):
    beginner_label = "NOOB"
    pro_label = "PRO"
    beginner_color = NOOB_COLOR
    pro_color = PRO_COLOR
    verdict = "Both give 1/6"

    def beginner_lines(self):
        return self.closed_form_lines()

    def pro_lines(self):
        return self.riemann_lines()


class ProVsExpert(BrandOutroMixin, PowerSumRatio):
    beginner_label = "PRO"
    pro_label = "EXPERT"
    beginner_color = PRO_COLOR
    pro_color = EXPERT_COLOR
    verdict = "No formula, no integral"

    # The branded tail; drop "outro" to render without it
    sections = SplitScreenScene.sections + ["outro"]

    def beginner_lines(self):
        return self.riemann_lines()

    def pro_lines(self):
        return self.growth_lines()
