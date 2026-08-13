from manim_imports_ext import *


SUB_COLOR = TEAL_B
LOG_COLOR = GREEN_B
RESULT_COLOR = YELLOW

FDEF_TEX = R"f(x) = \left( \sqrt{x} + \sqrt{x+1} \right) e^{\sqrt{x}\sqrt{x+1}}"
INTEGRAL_TEX = R"\int_{f(1)}^{f(11)} \frac{g(x)}{x^2 g'(x)} \, dx"
RATIO_TEX = R"\frac{f'(x)}{f(x)} = \frac{\sqrt{x+1}}{\sqrt{x}}"
REDUCED_TEX = R"\int_1^{11} t \left( \frac{f'(t)}{f(t)} \right)^2 dt"


class InverseFunctionIntegral(BrandOutroMixin, ShortsScene):
    # 9:16 portrait for YouTube Shorts.  Render with:
    #   ./render.sh _2026/Integrals/inverse_function_integral.py
    # or a single beat with:
    #   ./render.sh -s log_derivative _2026/Integrals/inverse_function_integral.py
    sections = [
        "show_problem",
        "substitute",
        "log_derivative",
        "evaluate",
        "outro",
    ]

    # Layout

    # YouTube's UI covers the bottom of a Short, so nothing goes below this
    body_bottom = -4.9

    def center_body(self, *mobjects, under=None, buff=0.8):
        """Fill the space between an anchor line and the safe bottom edge.

        Sections are laid out top down with `next_to`, which otherwise leaves
        the lower half of a 9:16 frame empty.
        """
        body = VGroup(*mobjects)
        anchor = self.get_header() if under is None else under
        top = anchor.get_bottom()[1] - buff
        available = top - self.body_bottom
        if body.get_height() > available:
            body.set_height(available)
        body.set_y((top + self.body_bottom) / 2)
        return body

    # State shared between sections

    def make_header(self):
        header = Tex(INTEGRAL_TEX, font_size=44)
        header.set_width(3.4)
        return self.pin_to_top(header, buff=0.5)

    def get_header(self):
        return self.lazy("header", self.make_header)

    def make_reduced(self):
        """What the substitution leaves behind: the only thing still unknown."""
        reduced = Tex(REDUCED_TEX, font_size=54)
        reduced.set_color(RESULT_COLOR)
        reduced.set_max_width(5.4)
        group = VGroup(
            reduced,
            SurroundingRectangle(reduced, color=RESULT_COLOR, buff=0.25).set_stroke(width=2),
        )
        return group.next_to(self.get_header(), DOWN, buff=0.7)

    def make_ratio(self):
        ratio = Tex(RATIO_TEX, font_size=60)
        ratio.set_color(RESULT_COLOR)
        ratio.set_max_width(5.0)
        group = VGroup(
            ratio,
            SurroundingRectangle(ratio, color=RESULT_COLOR, buff=0.25).set_stroke(width=2),
        )
        return group.next_to(self.get_header(), DOWN, buff=0.7)

    # Sections

    def show_problem(self):
        fdef = Tex(FDEF_TEX, font_size=48)
        fdef.set_max_width(6.9)

        inverse = Tex(R"g(x) = f^{-1}(x)", font_size=54)
        inverse.set_color(SUB_COLOR)

        integral = Tex(INTEGRAL_TEX, font_size=96)
        integral.set_max_width(6.8)

        stack = VGroup(fdef, inverse, integral)
        stack.arrange(DOWN, buff=2.0)
        stack.move_to(0.2 * UP)

        self.play(Write(fdef), run_time=1.8)
        self.wait(0.5)
        self.play(FadeIn(inverse, 0.2 * DOWN), run_time=0.8)
        self.wait(0.4)
        self.play(Write(integral), run_time=1.9)
        self.play(FlashAround(integral, color=RESULT_COLOR, time_width=1.5), run_time=1.4)
        self.wait(0.9)

        self.play(
            FadeOut(fdef, UP),
            FadeOut(inverse, UP),
            Transform(integral, self.make_header()),
            run_time=1.1,
        )
        self.set_state("header", integral)

    def substitute(self):
        title = TexText(R"Let $x = f(t)$", font_size=48)
        title.set_color(SUB_COLOR)
        title.next_to(self.get_header(), DOWN, buff=0.8)

        facts = VGroup(
            Tex(R"g(f(t)) = t", font_size=58),
            Tex(R"g'(f(t)) = \frac{1}{f'(t)}", font_size=58),
            Tex(R"dx = f'(t) \, dt", font_size=58),
        )
        facts.arrange(DOWN, buff=1.0)

        bounds = TexText(R"$x: f(1) \to f(11)$ \, gives \, $t: 1 \to 11$", font_size=42)
        bounds.set_color(GREY_B)
        bounds.set_max_width(6.6)
        bounds.next_to(facts, DOWN, buff=1.1)
        self.center_body(facts, bounds, under=title)

        reduced = Tex(REDUCED_TEX, font_size=54)
        reduced.set_color(RESULT_COLOR)
        reduced.set_max_width(6.0)
        reduced.move_to(VGroup(facts, bounds))
        reduced_box = SurroundingRectangle(reduced, color=RESULT_COLOR, buff=0.25)
        reduced_box.set_stroke(width=2)

        self.play(FadeIn(title, 0.2 * DOWN), run_time=0.8)
        self.play(LaggedStartMap(Write, facts, lag_ratio=0.5), run_time=2.4)
        self.wait(0.6)
        self.play(FadeIn(bounds, 0.15 * DOWN), run_time=0.8)
        self.wait(0.6)
        self.play(FadeTransform(VGroup(facts, bounds), reduced), run_time=1.4)
        self.play(ShowCreation(reduced_box), run_time=0.5)
        self.wait(1.2)

        group = VGroup(reduced, reduced_box)
        self.play(
            FadeOut(title, UP),
            group.animate.next_to(self.get_header(), DOWN, buff=0.7),
            run_time=1.0,
        )
        self.set_state("reduced", group)

    def log_derivative(self):
        reduced = self.lazy("reduced", self.make_reduced)
        self.play(FadeOut(reduced, UP), run_time=0.6)

        title = Text("Take logs first", font_size=44)
        title.set_color(LOG_COLOR)
        title.next_to(self.get_header(), DOWN, buff=0.8)

        fdef = Tex(FDEF_TEX, font_size=44)
        fdef.set_max_width(6.9)

        ln_line = Tex(
            R"\ln f(x) = \ln \left( \sqrt{x} + \sqrt{x+1} \right) + \sqrt{x}\sqrt{x+1}",
            font_size=44,
        )
        ln_line.set_color(LOG_COLOR)
        ln_line.set_max_width(6.9)
        ln_line.next_to(fdef, DOWN, buff=2.4)
        self.center_body(fdef, ln_line, under=title)

        self.play(FadeIn(title, 0.2 * DOWN), run_time=0.7)
        self.play(FadeIn(fdef), run_time=0.7)
        self.play(TransformFromCopy(fdef, ln_line), run_time=1.5)
        self.wait(0.8)

        # Clear the way, keeping the line we are about to differentiate
        self.play(
            FadeOut(title, UP),
            FadeOut(fdef, UP),
            ln_line.animate.next_to(self.get_header(), DOWN, buff=0.7),
            run_time=1.0,
        )

        deriv = Tex(
            R"\frac{f'(x)}{f(x)} = "
            R"\frac{\frac{1}{2\sqrt{x}} + \frac{1}{2\sqrt{x+1}}}{\sqrt{x} + \sqrt{x+1}}"
            R"+ \frac{2x+1}{2\sqrt{x}\sqrt{x+1}}",
            font_size=44,
        )
        deriv.set_max_width(6.9)

        simp = Tex(
            R"= \frac{1 + (2x+1)}{2\sqrt{x}\sqrt{x+1}}"
            R"= \frac{x+1}{\sqrt{x}\sqrt{x+1}}",
            font_size=44,
        )
        simp.set_max_width(6.6)
        simp.next_to(deriv, DOWN, buff=2.2)
        self.center_body(deriv, simp, under=ln_line)

        ratio = Tex(RATIO_TEX, font_size=60)
        ratio.set_color(RESULT_COLOR)
        ratio.set_max_width(5.0)
        ratio.move_to(VGroup(deriv, simp))
        ratio_box = SurroundingRectangle(ratio, color=RESULT_COLOR, buff=0.25)
        ratio_box.set_stroke(width=2)

        self.play(Write(deriv), run_time=2.0)
        self.wait(0.9)
        self.play(Write(simp), run_time=1.5)
        self.wait(0.8)
        self.play(FadeTransform(VGroup(deriv, simp), ratio), run_time=1.3)
        self.play(ShowCreation(ratio_box), run_time=0.5)
        self.wait(1.0)

        group = VGroup(ratio, ratio_box)
        self.play(
            FadeOut(ln_line, UP),
            group.animate.next_to(self.get_header(), DOWN, buff=0.7),
            run_time=1.0,
        )
        self.set_state("ratio", group)

    def evaluate(self):
        ratio = self.lazy("ratio", self.make_ratio)

        squared = Tex(
            R"\left( \frac{f'(t)}{f(t)} \right)^2 = \frac{t+1}{t}",
            font_size=50,
        )
        squared.set_color(SUB_COLOR)

        line1 = Tex(
            R"\int_1^{11} t \cdot \frac{t+1}{t} \, dt = \int_1^{11} (t+1) \, dt",
            font_size=46,
        )
        line1.set_max_width(6.9)
        line1.next_to(squared, DOWN, buff=1.0)

        line2 = Tex(
            R"= \left[ \frac{t^2}{2} + t \right]_1^{11}"
            R"= \frac{121}{2} + 11 - \frac{1}{2} - 1",
            font_size=44,
        )
        line2.set_max_width(6.9)
        line2.next_to(line1, DOWN, buff=0.9)

        answer = Tex(R"= 70", font_size=110)
        answer.set_color(RESULT_COLOR)
        answer.next_to(line2, DOWN, buff=1.0)

        self.center_body(squared, line1, line2, answer, under=ratio)
        answer_box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.35)
        answer_box.set_stroke(width=4)

        self.play(TransformFromCopy(ratio[0], squared), run_time=1.3)
        self.wait(0.6)
        self.play(Write(line1), run_time=1.7)
        self.wait(0.6)
        self.play(Write(line2), run_time=1.7)
        self.wait(0.6)
        self.play(FadeTransform(line2.copy(), answer), run_time=1.1)
        self.play(ShowCreation(answer_box), run_time=0.5)
        self.play(FlashAround(answer, color=RESULT_COLOR, time_width=1.5), run_time=1.4)
        self.wait(1.4)
