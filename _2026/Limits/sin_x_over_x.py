from manim_imports_ext import *


F_COLOR = BLUE
G_COLOR = YELLOW
DERIV_COLOR = TEAL
BAD_COLOR = RED

# 9:16 portrait for YouTube Shorts (1080x1920)
SHORTS_CAMERA_CONFIG = dict(
    pixel_width=1080,
    pixel_height=1920,
    frame_width=8.0,
    frame_height=8.0 * 16 / 9,
)


class SinXOverX(InteractiveScene):
    camera_config = SHORTS_CAMERA_CONFIG

    def construct(self):
        # Axes with sin(x) and x, sitting in the lower band
        axes = Axes(
            x_range=(-4, 4, 1),
            y_range=(-2.5, 2.5, 1),
            width=7.0,
            height=5.0,
        )
        axes.to_edge(DOWN, buff=0.4)
        axes.add_coordinate_labels(
            x_values=np.arange(-4, 5, 2),
            y_values=np.arange(-2, 3, 2),
            font_size=18,
        )

        sin_graph = axes.get_graph(np.sin, color=F_COLOR)
        x_graph = axes.get_graph(lambda x: x, x_range=(-2.3, 2.3), color=G_COLOR)

        sin_label = Tex(R"\sin(x)", font_size=36, color=F_COLOR)
        sin_label.next_to(axes.i2gp(-PI, sin_graph), DOWN, buff=0.2)
        x_label = Tex("x", font_size=36, color=G_COLOR)
        x_label.next_to(axes.i2gp(1.7, x_graph), RIGHT, buff=0.15)

        self.play(Write(axes, run_time=1.5, lag_ratio=0.01))
        self.play(
            ShowCreation(sin_graph, run_time=2),
            ShowCreation(x_graph, run_time=2),
            FadeIn(sin_label, 0.5 * DOWN, time_span=(1, 2)),
            FadeIn(x_label, 0.5 * RIGHT, time_span=(1, 2)),
        )
        self.wait()

        # The limit in question, anchored at the top
        limit_tex = Tex(R"\lim_{x \to 0} \frac{\sin(x)}{x}", font_size=54)
        limit_tex[R"\sin(x)"].set_color(F_COLOR)
        limit_tex["x"][-1].set_color(G_COLOR)
        limit_tex.set_backstroke(BLACK, 8)
        limit_tex.to_edge(UP, buff=0.7)
        limit_tex.fix_in_frame()

        self.play(Write(limit_tex))
        self.wait()

        # Naive substitution gives 0/0
        zero_over_zero = Tex(R"\rightarrow \frac{0}{0}", font_size=54, color=BAD_COLOR)
        zero_over_zero.set_backstroke(BLACK, 8)
        zero_over_zero.next_to(limit_tex, DOWN, buff=0.4)
        zero_over_zero.fix_in_frame()

        self.play(
            FadeIn(zero_over_zero[R"\rightarrow"]),
            TransformFromCopy(limit_tex[R"\frac{\sin(x)}{x}"], zero_over_zero[R"\frac{0}{0}"]),
            run_time=1.5,
        )
        self.play(FlashAround(zero_over_zero[R"\frac{0}{0}"], color=BAD_COLOR, run_time=1.5))
        self.wait()

        # Track the ratio as x approaches 0
        x_tracker = ValueTracker(2.0)
        get_x = x_tracker.get_value

        sin_dot = GlowDot(color=F_COLOR, radius=0.2)
        sin_dot.add_updater(lambda m: m.move_to(axes.i2gp(get_x(), sin_graph)))
        x_dot = GlowDot(color=G_COLOR, radius=0.2)
        x_dot.add_updater(lambda m: m.move_to(axes.c2p(get_x(), get_x())))
        v_line = always_redraw(
            lambda: axes.get_v_line_to_graph(get_x(), x_graph, stroke_width=2)
        )

        ratio_label = Tex(R"\frac{\sin(x)}{x} = ", font_size=44)
        ratio_label[R"\sin(x)"].set_color(F_COLOR)
        ratio_label["x"][-1].set_color(G_COLOR)
        ratio_value = DecimalNumber(0, num_decimal_places=4, font_size=44)
        ratio_value.add_updater(lambda m: m.set_value(np.sin(get_x()) / get_x()))
        readout = VGroup(ratio_label, ratio_value)
        readout.arrange(RIGHT, buff=0.2)
        readout.set_backstroke(BLACK, 8)
        readout.next_to(limit_tex, DOWN, buff=0.5)
        readout.fix_in_frame()

        self.play(
            FadeOut(zero_over_zero),
            FadeIn(sin_dot),
            FadeIn(x_dot),
            FadeIn(v_line),
            FadeIn(readout, 0.5 * DOWN),
        )
        self.play(x_tracker.animate.set_value(0.4), run_time=5)
        self.wait()

        # Zoom in: near zero the two curves are indistinguishable
        frame = self.frame
        self.play(
            frame.animate.set_height(1.6).move_to(axes.c2p(0.2, 0.2)),
            x_tracker.animate.set_value(0.05),
            run_time=5,
        )
        self.wait(2)
        self.play(
            frame.animate.to_default_state(),
            x_tracker.animate.set_value(1.0),
            run_time=3,
        )
        self.play(FlashAround(readout, color=G_COLOR, run_time=2, time_width=1.5))

        # Push the plot to the background
        self.play(
            VGroup(sin_graph, x_graph).animate.set_stroke(opacity=0.2),
            VGroup(axes, sin_label, x_label).animate.set_opacity(0.2),
            FadeOut(Group(sin_dot, x_dot, v_line, readout)),
        )

        # L'Hopital's rule: differentiate top and bottom, stacked vertically
        deriv_arrow = Tex(R"\Downarrow", font_size=54, color=DERIV_COLOR)
        deriv_arrow.next_to(limit_tex, DOWN, buff=0.35)
        deriv_label = Tex(R"\frac{d}{dx}", font_size=32, color=DERIV_COLOR)
        deriv_label.next_to(deriv_arrow, RIGHT, buff=0.25)
        rule_name = Text("L'Hôpital", font_size=28, color=GREY_B)
        rule_name.next_to(deriv_arrow, LEFT, buff=0.4)
        VGroup(rule_name, deriv_arrow, deriv_label).fix_in_frame()

        new_limit = Tex(R"\lim_{x \to 0} \frac{\cos(x)}{1}", font_size=54)
        new_limit[R"\cos(x)"].set_color(F_COLOR)
        new_limit["1"].set_color(G_COLOR)
        new_limit.next_to(deriv_arrow, DOWN, buff=0.35)
        new_limit.set_backstroke(BLACK, 8)
        new_limit.fix_in_frame()

        self.play(FadeIn(rule_name), Write(deriv_arrow), Write(deriv_label))
        self.play(
            TransformMatchingTex(
                limit_tex.copy(), new_limit,
                key_map={R"\sin": R"\cos"},
                run_time=1.5,
            )
        )
        self.play(
            FlashAround(new_limit[R"\cos(x)"], color=F_COLOR),
            FlashAround(new_limit["1"], color=G_COLOR),
            run_time=1.5,
        )
        self.wait()

        # Now substitution works — each step on its own line
        eval_step = Tex(R"= \frac{\cos(0)}{1}", font_size=54)
        eval_step[R"\cos(0)"].set_color(F_COLOR)
        eval_step["1"].set_color(G_COLOR)
        eval_step.next_to(new_limit, DOWN, buff=0.4)
        eval_step.set_backstroke(BLACK, 8)
        eval_step.fix_in_frame()

        result = Tex(R"= 1", font_size=66)
        result["1"].set_color(YELLOW)
        result.next_to(eval_step, DOWN, buff=0.4)
        result.set_backstroke(BLACK, 8)
        result.fix_in_frame()

        self.play(Write(eval_step))
        self.wait()
        self.play(Write(result))

        answer = result["1"]
        box = SurroundingRectangle(answer, color=YELLOW, buff=0.15)
        box.fix_in_frame()
        self.play(ShowCreation(box), FlashAround(answer, color=YELLOW, run_time=1.5))
        self.wait(2)
