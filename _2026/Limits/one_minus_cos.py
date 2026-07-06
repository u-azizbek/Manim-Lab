from manim_imports_ext import *


F_COLOR = BLUE
G_COLOR = YELLOW
RATIO_COLOR = GREEN
DERIV_COLOR = TEAL
BAD_COLOR = RED

# 9:16 portrait for YouTube Shorts (1080x1920)
SHORTS_CAMERA_CONFIG = dict(
    pixel_width=1080,
    pixel_height=1920,
    frame_width=8.0,
    frame_height=8.0 * 16 / 9,
)


class OneMinusCosOverXSquared(InteractiveScene):
    camera_config = SHORTS_CAMERA_CONFIG

    def construct(self):
        # The limit in question, anchored at the top
        limit_tex = Tex(R"\lim_{x \to 0} \frac{1 - \cos(x)}{x^2}", font_size=52)
        limit_tex[R"1 - \cos(x)"].set_color(F_COLOR)
        limit_tex["x^2"].set_color(G_COLOR)
        limit_tex.set_backstroke(BLACK, 8)
        limit_tex.to_edge(UP, buff=0.6)

        self.play(Write(limit_tex))
        self.wait()

        # Both pieces vanish at zero — graph in the lower band
        axes = Axes(
            x_range=(-3, 3, 1),
            y_range=(0, 2, 1),
            width=7.0,
            height=3.2,
        )
        axes.to_edge(DOWN, buff=0.5)
        axes.add_coordinate_labels(
            x_values=np.arange(-3, 4),
            y_values=[1, 2],
            font_size=18,
        )

        f_graph = axes.get_graph(lambda x: 1 - math.cos(x), color=F_COLOR)
        g_graph = axes.get_graph(lambda x: x**2, x_range=(-1.414, 1.414), color=G_COLOR)

        f_label = Tex(R"1 - \cos(x)", font_size=30, color=F_COLOR)
        f_label.next_to(axes.i2gp(-2.6, f_graph), UP, buff=0.1)
        g_label = Tex("x^2", font_size=30, color=G_COLOR)
        g_label.next_to(axes.i2gp(1.35, g_graph), RIGHT, buff=0.15)

        self.play(Write(axes, run_time=1.5, lag_ratio=0.01))
        self.play(
            ShowCreation(f_graph, run_time=2),
            ShowCreation(g_graph, run_time=2),
            FadeIn(f_label, 0.5 * UP, time_span=(1, 2)),
            FadeIn(g_label, 0.5 * RIGHT, time_span=(1, 2)),
        )

        origin_dot = GlowDot(axes.c2p(0, 0), color=WHITE, radius=0.3)
        self.play(FadeIn(origin_dot, scale=3))
        self.wait()

        # Substitution fails: 0/0
        zero_over_zero = Tex(R"\rightarrow \frac{0}{0}", font_size=52, color=BAD_COLOR)
        zero_over_zero.set_backstroke(BLACK, 8)
        zero_over_zero.next_to(limit_tex, DOWN, buff=0.35)

        self.play(
            FadeIn(zero_over_zero[R"\rightarrow"]),
            TransformFromCopy(limit_tex[R"\frac{1 - \cos(x)}{x^2}"], zero_over_zero[R"\frac{0}{0}"]),
            run_time=1.5,
        )
        self.play(FlashAround(zero_over_zero[R"\frac{0}{0}"], color=BAD_COLOR, run_time=1.5))
        self.wait()

        # Watch the ratio approach 1/2
        x_tracker = ValueTracker(3.0)
        get_x = x_tracker.get_value

        def ratio(x):
            return (1 - math.cos(x)) / x**2

        ratio_graph = axes.get_graph(ratio, x_range=(-3, -0.01), color=RATIO_COLOR)
        ratio_dot = GlowDot(color=RATIO_COLOR, radius=0.2)
        ratio_dot.add_updater(lambda m: m.move_to(axes.c2p(-get_x(), ratio(get_x()))))

        half_line = DashedLine(axes.c2p(-3, 0.5), axes.c2p(3, 0.5))
        half_line.set_stroke(RATIO_COLOR, 2, opacity=0.7)
        half_label = Tex(R"\frac{1}{2}", font_size=32, color=RATIO_COLOR)
        half_label.next_to(half_line, RIGHT, buff=0.15)

        ratio_label = Tex(R"\frac{1 - \cos(x)}{x^2} = ", font_size=40)
        ratio_label[R"1 - \cos(x)"].set_color(F_COLOR)
        ratio_label["x^2"].set_color(G_COLOR)
        ratio_value = DecimalNumber(ratio(3), num_decimal_places=4, font_size=40)
        readout = VGroup(ratio_label, ratio_value)
        readout.arrange(RIGHT, buff=0.2)
        readout.set_backstroke(BLACK, 8)
        readout.next_to(limit_tex, DOWN, buff=0.4)

        self.play(
            FadeOut(zero_over_zero),
            ShowCreation(half_line),
            FadeIn(half_label),
            FadeIn(readout, 0.5 * DOWN),
            FadeIn(ratio_dot),
        )
        ratio_value.add_updater(lambda m: m.set_value(ratio(get_x())))
        self.play(
            x_tracker.animate.set_value(0.05),
            ShowCreation(ratio_graph),
            run_time=6,
        )
        self.play(FlashAround(readout, color=RATIO_COLOR, run_time=2, time_width=1.5))
        self.wait()

        # First application of L'Hopital, stacked vertically
        arrow1 = Tex(R"\Downarrow", font_size=54, color=DERIV_COLOR)
        arrow1.next_to(limit_tex, DOWN, buff=0.3)
        deriv_label1 = Tex(R"\frac{d}{dx}", font_size=30, color=DERIV_COLOR)
        deriv_label1.next_to(arrow1, RIGHT, buff=0.25)
        rule_name = Text("L'Hôpital", font_size=26, color=GREY_B)
        rule_name.next_to(arrow1, LEFT, buff=0.35)

        step1 = Tex(R"\lim_{x \to 0} \frac{\sin(x)}{2x}", font_size=52)
        step1[R"\sin(x)"].set_color(F_COLOR)
        step1["2x"].set_color(G_COLOR)
        step1.set_backstroke(BLACK, 8)
        step1.next_to(arrow1, DOWN, buff=0.3)

        # Push the plot to the background so the multi-step chain stays readable,
        # keeping the y = 1/2 line bright as the eventual payoff
        self.play(
            FadeOut(readout),
            FadeOut(ratio_dot),
            VGroup(f_graph, g_graph, ratio_graph).animate.set_stroke(opacity=0.2),
            VGroup(axes, f_label, g_label).animate.set_opacity(0.2),
            origin_dot.animate.set_opacity(0.15),
            Write(arrow1),
            Write(deriv_label1),
            FadeIn(rule_name),
        )
        self.play(
            TransformMatchingTex(
                limit_tex.copy(), step1,
                key_map={R"1 - \cos": R"\sin", "x^2": "2x"},
                run_time=1.5,
            )
        )
        self.wait()

        # Still 0/0
        still_bad = Tex(R"\frac{0}{0}", font_size=40, color=BAD_COLOR)
        still_bad.next_to(step1, RIGHT, buff=0.5)
        self.play(FadeIn(still_bad, 0.3 * RIGHT))
        self.play(FlashAround(still_bad, color=BAD_COLOR, run_time=1.5))
        self.wait()

        # Second application
        arrow2 = Tex(R"\Downarrow", font_size=54, color=DERIV_COLOR)
        arrow2.next_to(step1, DOWN, buff=0.3)
        deriv_label2 = Tex(R"\frac{d}{dx}", font_size=30, color=DERIV_COLOR)
        deriv_label2.next_to(arrow2, RIGHT, buff=0.25)

        step2 = Tex(R"\lim_{x \to 0} \frac{\cos(x)}{2}", font_size=52)
        step2[R"\cos(x)"].set_color(F_COLOR)
        step2["2"].set_color(G_COLOR)
        step2.set_backstroke(BLACK, 8)
        step2.next_to(arrow2, DOWN, buff=0.3)

        self.play(FadeOut(still_bad), Write(arrow2), Write(deriv_label2))
        self.play(
            TransformMatchingTex(
                step1.copy(), step2,
                key_map={R"\sin": R"\cos", "2x": "2"},
                run_time=1.5,
            )
        )
        self.wait()

        # Substitution finally works
        result = Tex(R"= \frac{1}{2}", font_size=56)
        result[R"\frac{1}{2}"].set_color(RATIO_COLOR)
        result.set_backstroke(BLACK, 8)
        result.next_to(step2, DOWN, buff=0.35)

        self.play(Write(result))
        box = SurroundingRectangle(result[R"\frac{1}{2}"], color=RATIO_COLOR, buff=0.15)
        self.play(ShowCreation(box))
        self.wait()

        # Tie the answer back to the picture
        self.play(
            TransformFromCopy(result[R"\frac{1}{2}"], half_label.copy(), remover=True),
            FlashAround(half_label, color=RATIO_COLOR, run_time=2),
        )
        self.play(VShowPassingFlash(
            half_line.copy().set_stroke(RATIO_COLOR, 6, opacity=1),
            time_width=1.5,
            run_time=2,
        ))
        self.wait(2)
