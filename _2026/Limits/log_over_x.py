from manim_imports_ext import *


F_COLOR = BLUE
G_COLOR = YELLOW
DERIV_COLOR = TEAL
BAD_COLOR = RED
ANSWER_COLOR = GREEN

# 9:16 portrait for YouTube Shorts (1080x1920)
SHORTS_CAMERA_CONFIG = dict(
    pixel_width=1080,
    pixel_height=1920,
    frame_width=8.0,
    frame_height=8.0 * 16 / 9,
)


class LnXOverX(InteractiveScene):
    camera_config = SHORTS_CAMERA_CONFIG

    def construct(self):
        # The limit in question, anchored at the top
        limit_tex = Tex(R"\lim_{x \to \infty} \frac{\ln(x)}{x}", font_size=54)
        limit_tex[R"\ln(x)"].set_color(F_COLOR)
        limit_tex["x"][-1].set_color(G_COLOR)
        limit_tex.set_backstroke(BLACK, 8)
        limit_tex.to_edge(UP, buff=0.6)
        limit_tex.fix_in_frame()

        self.play(Write(limit_tex))
        self.wait()

        # Substitution gives infinity over infinity
        inf_over_inf = Tex(R"\rightarrow \frac{\infty}{\infty}", font_size=54, color=BAD_COLOR)
        inf_over_inf.next_to(limit_tex, DOWN, buff=0.35)
        inf_over_inf.set_backstroke(BLACK, 8)
        inf_over_inf.fix_in_frame()

        self.play(
            FadeIn(inf_over_inf[R"\rightarrow"]),
            TransformFromCopy(limit_tex[R"\frac{\ln(x)}{x}"], inf_over_inf[R"\frac{\infty}{\infty}"]),
            run_time=1.5,
        )
        self.play(FlashAround(inf_over_inf[R"\frac{\infty}{\infty}"], color=BAD_COLOR, run_time=1.5))
        self.wait()

        # A race to infinity — graph in the lower band
        axes = Axes(
            x_range=(0, 60, 10),
            y_range=(0, 12, 2),
            width=7.2,
            height=6.0,
        )
        axes.to_edge(DOWN, buff=0.5)
        axes.add_coordinate_labels(
            x_values=np.arange(20, 70, 20),
            y_values=[],
            font_size=18,
        )

        ln_graph = axes.get_graph(math.log, x_range=(0.1, 60), color=F_COLOR)
        x_graph = axes.get_graph(lambda x: x, x_range=(0, 11.8), color=G_COLOR)

        ln_label = Tex(R"\ln(x)", font_size=36, color=F_COLOR)
        ln_label.next_to(axes.i2gp(20, ln_graph), UP, buff=0.25)
        x_label = Tex("x", font_size=36, color=G_COLOR)
        x_label.next_to(axes.i2gp(7, x_graph), RIGHT, buff=0.25)

        frame = self.frame
        frame.save_state()
        frame.set_height(4).move_to(axes.c2p(4, 2))

        self.play(
            FadeOut(inf_over_inf),
            Write(axes, run_time=1.5, lag_ratio=0.01),
        )
        self.play(
            ShowCreation(ln_graph, run_time=3),
            ShowCreation(x_graph, run_time=3),
        )
        self.wait()

        # Track the ratio while zooming out: x wins the race
        x_tracker = ValueTracker(3.0)
        get_x = x_tracker.get_value

        ln_dot = GlowDot(color=F_COLOR, radius=0.2)
        ln_dot.add_updater(lambda m: m.move_to(axes.i2gp(get_x(), ln_graph)))
        x_dot = GlowDot(color=G_COLOR, radius=0.2)
        x_dot.add_updater(lambda m: m.move_to(axes.c2p(get_x(), get_x())))
        v_line = always_redraw(
            lambda: axes.get_v_line_to_graph(get_x(), ln_graph, stroke_width=2)
        )

        ratio_label = Tex(R"\frac{\ln(x)}{x} = ", font_size=40)
        ratio_label[R"\ln(x)"].set_color(F_COLOR)
        ratio_label["x"][-1].set_color(G_COLOR)
        ratio_value = DecimalNumber(math.log(3) / 3, num_decimal_places=4, font_size=40)
        ratio_value.add_updater(lambda m: m.set_value(math.log(get_x()) / get_x()))
        readout = VGroup(ratio_label, ratio_value)
        readout.arrange(RIGHT, buff=0.25)
        readout.set_backstroke(BLACK, 8)
        readout.next_to(limit_tex, DOWN, buff=0.4)
        # Solid backing so the steep x-line never garbles the readout during the zoom-out
        readout_bg = BackgroundRectangle(readout, buff=0.12, fill_opacity=1.0)
        readout_group = Group(readout_bg, readout)
        readout_group.fix_in_frame()
        readout_group.set_z_index(20)

        self.play(
            FadeIn(ln_dot),
            FadeIn(x_dot),
            FadeIn(v_line),
            FadeIn(readout_group, 0.5 * DOWN),
        )
        self.play(
            Restore(frame),
            x_tracker.animate.set_value(55),
            FadeIn(ln_label, time_span=(4, 5)),
            FadeIn(x_label, time_span=(2, 3)),
            run_time=7,
        )
        self.play(FlashAround(readout, color=ANSWER_COLOR, run_time=2, time_width=1.5))
        self.wait()

        # L'Hopital: differentiate top and bottom, stacked vertically
        arrow = Tex(R"\Downarrow", font_size=54, color=DERIV_COLOR)
        arrow.next_to(readout, DOWN, buff=0.35)
        deriv_label = Tex(R"\frac{d}{dx}", font_size=30, color=DERIV_COLOR)
        deriv_label.next_to(arrow, RIGHT, buff=0.25)
        rule_name = Text("L'Hôpital", font_size=26, color=GREY_B)
        rule_name.next_to(arrow, LEFT, buff=0.35)
        VGroup(rule_name, arrow, deriv_label).fix_in_frame()

        new_limit = Tex(R"\lim_{x \to \infty} \frac{1 / x}{1}", font_size=54)
        new_limit["1 / x"].set_color(F_COLOR)
        new_limit["1"][-1].set_color(G_COLOR)
        new_limit.next_to(arrow, DOWN, buff=0.35)
        new_limit.set_backstroke(BLACK, 8)
        new_limit.fix_in_frame()

        self.play(
            Write(arrow), Write(deriv_label), FadeIn(rule_name),
            VGroup(ln_graph, x_graph).animate.set_stroke(opacity=0.3),
            axes.animate.set_opacity(0.3),
            FadeOut(ln_label),
            FadeOut(x_label),
        )
        self.play(
            TransformMatchingTex(
                limit_tex.copy(), new_limit,
                key_map={R"\ln(x)": "1 / x"},
                run_time=1.5,
            )
        )
        self.play(
            FlashAround(new_limit["1 / x"], color=F_COLOR),
            FlashAround(new_limit["1"][-1], color=G_COLOR),
            run_time=1.5,
        )
        self.wait()

        # One over infinity vanishes
        result = Tex(R"= 0", font_size=60)
        result["0"].set_color(ANSWER_COLOR)
        result.next_to(new_limit, DOWN, buff=0.35)
        result.set_backstroke(BLACK, 8)
        result.fix_in_frame()

        self.play(Write(result))
        box = SurroundingRectangle(result["0"], color=ANSWER_COLOR, buff=0.15)
        box.fix_in_frame()
        self.play(ShowCreation(box))
        self.wait()

        # The x-axis is the asymptote
        x_axis_flash = Line(axes.c2p(0, 0), axes.c2p(60, 0))
        x_axis_flash.set_stroke(ANSWER_COLOR, 6)
        self.play(
            VShowPassingFlash(x_axis_flash, time_width=1.5, run_time=3),
            x_tracker.animate.set_value(59).set_anim_args(run_time=3),
        )
        self.wait(2)
