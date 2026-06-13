from manim_imports_ext import *


class SolveLimit(InteractiveScene):
    # 9:16 portrait for YouTube Shorts (1080x1920)
    camera_config = dict(
        pixel_width=1080,
        pixel_height=1920,
        frame_width=8.0,
        frame_height=8.0 * 16 / 9,
    )

    def construct(self):
        # Set background to black
        self.camera.background_color = BLACK

        # "To solve this:" label
        intro_text = Text("To solve this:", color=WHITE)
        intro_text.to_edge(UP, buff=0.8)

        # "Limit" label with peach background and yellow border
        limit_label = Text("Limit", color=BLACK)
        limit_box = SurroundingRectangle(
            limit_label,
            color=YELLOW,
            fill_color="#FFDAB9",
            fill_opacity=1.0,
            buff=0.15,
        )
        limit_group = VGroup(limit_box, limit_label)
        limit_group.next_to(intro_text, DOWN, buff=0.5)

        # LaTeX limit expression
        limit_tex = Tex(
            R"\lim_{x \to 0} \frac{e^x - 1 - x}{x^2}",
            font_size=52,
        )
        limit_tex.next_to(limit_group, DOWN, buff=0.6)

        # Display intro text with Write (2 seconds)
        self.play(Write(intro_text), run_time=2)
        self.wait(0.2)

        # Display limit_group and limit_tex with Add, 1 second delay between each
        self.add(limit_group)
        self.wait(1)
        self.add(limit_tex)
        self.wait(1)

        self.solve_limit(limit_tex)

        # "Made by GitHub Copilot" credit
        credit = Text("Made by GitHub Copilot", font_size=24, color=GREY_B)
        credit.to_corner(DR, buff=0.3)
        self.add(credit)
        self.wait(2)

    def solve_limit(self, limit_tex):
        # Portrait layout: stack each label above its LaTeX expression

        # --- Step header ---
        lhopital_title = Text("Apply L'Hôpital's Rule\n(0/0 indeterminate form)", font_size=36, color=BLUE_B)
        lhopital_title.set_width(7.0)
        lhopital_title.next_to(limit_tex, DOWN, buff=0.7)

        self.play(Write(lhopital_title), run_time=1)
        self.wait(1)

        # --- First application ---
        step1_label = Text("1st application:", font_size=32, color=WHITE)
        step1_tex = Tex(
            R"\lim_{x \to 0} \frac{e^x - 1}{2x}",
            font_size=52,
        )
        step1_label.next_to(lhopital_title, DOWN, buff=0.6)
        step1_tex.next_to(step1_label, DOWN, buff=0.3)

        self.play(Write(step1_label), run_time=1)
        self.wait(1)
        self.play(Write(step1_tex), run_time=1)
        self.wait(1)

        # --- Second application ---
        still_indeterminate = Text("Still 0/0 — apply again:", font_size=32, color=WHITE)
        still_indeterminate.next_to(step1_tex, DOWN, buff=0.6)

        step2_tex = Tex(
            R"\lim_{x \to 0} \frac{e^x}{2}",
            font_size=52,
        )
        step2_tex.next_to(still_indeterminate, DOWN, buff=0.3)

        self.play(Write(still_indeterminate), run_time=1)
        self.wait(1)
        self.play(Write(step2_tex), run_time=1)
        self.wait(1)

        # --- Evaluate ---
        evaluate_label = Text("Evaluate at x = 0:", font_size=32, color=WHITE)
        evaluate_label.next_to(step2_tex, DOWN, buff=0.6)

        self.play(Write(evaluate_label), run_time=1)
        self.wait(1)

        # --- Solution ---
        solution = Text("= 1/2", font_size=72, color=YELLOW)
        solution.next_to(evaluate_label, DOWN, buff=0.35)

        self.play(Write(solution), run_time=1)
        self.wait(1)

        # Highlight the result
        box = SurroundingRectangle(solution, color=YELLOW, buff=0.2)
        self.play(ShowCreation(box), run_time=0.6)
        self.wait(1)
