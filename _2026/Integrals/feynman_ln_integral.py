from manim_imports_ext import *


RULE_COLOR = GREEN_B
PARAM_COLOR = TEAL_B
RESULT_COLOR = YELLOW

INTEGRAL_TEX = R"\int_0^1 \ln x \, dx"


class FeynmanLogIntegral(ShortsScene):
    # 9:16 portrait for YouTube Shorts.  Render with:
    #   ./render.sh _2026/Integrals/feynman_ln_integral.py
    # or a single beat with:
    #   ./render.sh -s differentiate _2026/Integrals/feynman_ln_integral.py
    sections = [
        "show_problem",
        "introduce_parameter",
        "easy_integral",
        "differentiate",
        "reveal_answer",
    ]

    # State shared between sections

    def make_header(self):
        header = Tex(INTEGRAL_TEX, font_size=44)
        header.set_width(2.6)
        return self.pin_to_top(header, buff=0.5)

    def get_header(self):
        return self.lazy("header", self.make_header)

    def make_family(self):
        """The parametrised integral every later section refers back to."""
        family = Tex(R"I(s) = \int_0^1 x^s \, dx = \frac{1}{s+1}", font_size=48)
        family.set_color(PARAM_COLOR)
        family.set_width(5.6)
        family.next_to(self.get_header(), DOWN, buff=0.6)
        return family

    def get_family(self):
        return self.lazy("family", self.make_family)

    # Sections

    def show_problem(self):
        banned = Text("No integration by parts!", font_size=44)
        banned.set_color(RULE_COLOR)
        banned.set_width(6.6)

        integral = Tex(INTEGRAL_TEX, font_size=96)
        integral.set_width(4.6)

        trick = Text("FEYNMAN'S TRICK", font_size=46)
        trick.set_color(RESULT_COLOR)
        trick.set_width(6.0)

        stack = VGroup(banned, integral, trick)
        stack.arrange(DOWN, buff=1.3)
        stack.move_to(0.6 * UP)

        self.play(FadeIn(banned, 0.2 * DOWN), run_time=1.0)
        self.play(Write(integral), run_time=1.4)
        self.wait(0.8)
        self.play(FadeIn(trick, scale=1.1), run_time=1.0)
        self.play(FlashAround(trick, color=RESULT_COLOR, time_width=1.5), run_time=1.4)
        self.wait(0.8)

        self.play(
            FadeOut(banned, UP),
            FadeOut(trick, DOWN),
            Transform(integral, self.make_header()),
            run_time=1.1,
        )
        self.set_state("header", integral)

    def introduce_parameter(self):
        title = Text("Smuggle in a parameter", font_size=40)
        title.set_color(PARAM_COLOR)
        title.next_to(self.get_header(), DOWN, buff=0.8)

        definition = Tex(R"x^s = e^{s \ln x}", font_size=52)
        definition.next_to(title, DOWN, buff=0.9)

        derivative = Tex(
            R"\frac{\partial}{\partial s} x^s = x^s \ln x",
            font_size=56,
        )
        derivative.set_color(RESULT_COLOR)
        derivative.next_to(definition, DOWN, buff=1.0)
        derivative_box = SurroundingRectangle(derivative, color=RESULT_COLOR, buff=0.25)
        derivative_box.set_stroke(width=2)

        punchline = Tex(R"s = 0 \quad \Longrightarrow \quad x^0 \ln x = \ln x", font_size=46)
        punchline.set_width(6.6)
        punchline.next_to(derivative_box, DOWN, buff=1.1)

        self.play(FadeIn(title, 0.2 * DOWN), run_time=0.9)
        self.play(Write(definition), run_time=1.2)
        self.wait(0.5)
        self.play(TransformFromCopy(definition, derivative), run_time=1.3)
        self.play(ShowCreation(derivative_box), run_time=0.5)
        self.wait(0.8)
        self.play(Write(punchline), run_time=1.4)
        self.wait(1.2)

        self.play(
            FadeOut(VGroup(title, definition, derivative, derivative_box, punchline), UP),
            run_time=0.8,
        )

    def easy_integral(self):
        title = Text("This one is easy", font_size=40)
        title.set_color(PARAM_COLOR)
        title.next_to(self.get_header(), DOWN, buff=0.8)

        setup = Tex(R"I(s) = \int_0^1 x^s \, dx", font_size=52)
        setup.next_to(title, DOWN, buff=0.9)

        work = Tex(
            R"= \left[ \frac{x^{s+1}}{s+1} \right]_0^1 = \frac{1}{s+1}",
            font_size=48,
        )
        work.set_width(6.2)
        work.next_to(setup, DOWN, buff=0.9)

        caveat = Tex(R"(s > -1)", font_size=34)
        caveat.set_color(GREY_B)
        caveat.next_to(work, DOWN, buff=0.5)

        self.play(FadeIn(title, 0.2 * DOWN), run_time=0.8)
        self.play(Write(setup), run_time=1.2)
        self.wait(0.4)
        self.play(Write(work), run_time=1.6)
        self.play(FadeIn(caveat), run_time=0.6)
        self.wait(1.0)

        # Collapse the whole calculation into the one line later sections need
        self.play(
            FadeOut(VGroup(title, caveat), UP),
            FadeOut(work, UP),
            Transform(setup, self.make_family()),
            run_time=1.1,
        )
        self.set_state("family", setup)

    def differentiate(self):
        title = TexText(R"Differentiate both sides in $s$", font_size=40)
        title.set_color(PARAM_COLOR)
        title.set_width(6.6)
        title.next_to(self.get_family(), DOWN, buff=0.8)

        left = Tex(
            R"I'(s) = \int_0^1 \frac{\partial}{\partial s} x^s \, dx"
            R"= \int_0^1 x^s \ln x \, dx",
            font_size=44,
        )
        left.set_width(6.9)
        left.next_to(title, DOWN, buff=0.8)

        right = Tex(
            R"I'(s) = \frac{d}{ds} \frac{1}{s+1} = -\frac{1}{(s+1)^2}",
            font_size=44,
        )
        right.set_width(6.6)
        right.next_to(left, DOWN, buff=1.0)

        conclusion = Tex(
            R"\int_0^1 x^s \ln x \, dx = -\frac{1}{(s+1)^2}",
            font_size=48,
        )
        conclusion.set_color(RESULT_COLOR)
        conclusion.set_width(6.4)
        # Land where the two lines were, so they visibly collapse into it
        conclusion.move_to(VGroup(left, right))
        conclusion_box = SurroundingRectangle(conclusion, color=RESULT_COLOR, buff=0.25)
        conclusion_box.set_stroke(width=2)

        self.play(FadeIn(title, 0.2 * DOWN), run_time=0.9)
        self.play(Write(left), run_time=1.8)
        self.wait(0.6)
        self.play(Write(right), run_time=1.6)
        self.wait(0.6)
        self.play(FadeTransform(VGroup(left, right), conclusion), run_time=1.4)
        self.play(ShowCreation(conclusion_box), run_time=0.5)
        self.wait(1.0)

        self.play(
            FadeOut(title, UP),
            FadeOut(self.get_family(), UP),
            VGroup(conclusion, conclusion_box).animate.next_to(
                self.get_header(), DOWN, buff=0.7,
            ),
            run_time=1.0,
        )
        self.set_state("conclusion", VGroup(conclusion, conclusion_box))

    def reveal_answer(self):
        conclusion = self.lazy("conclusion", self.make_conclusion)

        substitute = Tex(R"\text{now set } s = 0", font_size=44)
        substitute.set_color(PARAM_COLOR)
        substitute.next_to(conclusion, DOWN, buff=0.9)

        answer = Tex(
            R"\int_0^1 \ln x \, dx = -\frac{1}{(0+1)^2} = -1",
            font_size=48,
        )
        answer.set_width(6.8)
        answer.next_to(substitute, DOWN, buff=0.9)

        boxed = Tex(R"= -1", font_size=96)
        boxed.set_color(RESULT_COLOR)
        boxed.next_to(answer, DOWN, buff=1.0)
        boxed_box = SurroundingRectangle(boxed, color=RESULT_COLOR, buff=0.3)
        boxed_box.set_stroke(width=4)

        self.play(FadeIn(substitute, 0.2 * DOWN), run_time=0.8)
        self.play(Write(answer), run_time=1.6)
        self.wait(0.5)
        self.play(FadeTransform(answer.copy(), boxed), run_time=1.0)
        self.play(ShowCreation(boxed_box), run_time=0.5)
        self.play(FlashAround(boxed, time_width=1.5), run_time=1.4)
        self.wait(1.0)

        self.show_area(VGroup(conclusion, substitute, answer, boxed, boxed_box))

    def make_conclusion(self):
        conclusion = Tex(
            R"\int_0^1 x^s \ln x \, dx = -\frac{1}{(s+1)^2}",
            font_size=48,
        )
        conclusion.set_color(RESULT_COLOR)
        conclusion.set_width(6.4)
        group = VGroup(
            conclusion,
            SurroundingRectangle(conclusion, color=RESULT_COLOR, buff=0.25).set_stroke(width=2),
        )
        return group.next_to(self.get_header(), DOWN, buff=0.7)

    def show_area(self, to_clear):
        self.play(FadeOut(to_clear, UP), run_time=0.8)

        axes = Axes(
            x_range=(0, 1.25, 0.5),
            y_range=(-4, 1, 1),
            width=5.0,
            height=4.6,
            axis_config=dict(stroke_color=GREY_B, stroke_width=2),
        )
        axes.add_coordinate_labels(x_values=[1], y_values=[-2], font_size=24)
        axes.move_to(1.2 * UP)

        graph = axes.get_graph(np.log, x_range=(0.018, 1, 0.002))
        graph.set_stroke(RESULT_COLOR, 3)
        area = axes.get_area_under_graph(
            graph, [0.018, 1], fill_color=RESULT_COLOR, fill_opacity=0.35,
        )

        label = Tex(R"y = \ln x", font_size=40)
        label.set_color(RESULT_COLOR)
        label.next_to(axes.c2p(1, 0), UR, buff=0.15)

        caption = TexText(
            R"the region is below the axis,\\so the integral is $-1$",
            font_size=38,
        )
        caption.set_width(6.4)
        caption.next_to(axes, DOWN, buff=0.9)

        self.play(ShowCreation(axes), run_time=0.8)
        self.play(ShowCreation(graph), FadeIn(label), run_time=1.5)
        self.play(FadeIn(area), run_time=1.0)
        self.play(FadeIn(caption, 0.2 * DOWN), run_time=1.0)
        self.wait(2.0)
