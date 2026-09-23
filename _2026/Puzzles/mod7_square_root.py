from manim_imports_ext import *


class ModSquareRoot(MockTestShort):
    # Render with:
    #   ./render.sh _2026/Puzzles/mod7_square_root.py
    #
    # Solve x^2 = 2 (mod 7) by the "add multiples of the modulus" trick:
    # 2 + 7 = 9 is a perfect square, so x = +-3, i.e. x = 3 or 4 (mod 7).

    test = ""                       # not a mock-test question, so no F1:xx tag
    card_top_buff = 0.85            # a little breathing room above the card
    step_buff = 0.95

    problem_tex = R"x^2 \equiv 2 \pmod 7"
    card_font_size = 60

    sections = [
        "pose",
        "add_multiple",
        "square_root",
        "finish",
        "outro",
    ]

    def add_multiple(self):
        self.get_card()
        self.note(
            "Trick: add multiples of 7 to the right side\n"
            "until it becomes a perfect square."
        )
        # 2 + 7 = 9 lands us on a square; then fold it back into the congruence
        bump = self.add_step(
            R"2 + 7 = 9",
            color=RULE_COLOR, font_size=48, wait=1.0, isolate=["9"],
        )
        self.replace_step(
            bump,
            R"x^2 \equiv 9 \pmod 7",
            color=RULE_COLOR, font_size=48,
            isolate=["9"], matched_keys=["9"], wait=1.0,
        )

    def square_root(self):
        self.get_card()
        self.note("9 is a perfect square, so take the square root.")
        self.add_step(
            R"x \equiv \pm 3 \pmod 7",
            color=SETUP_COLOR, font_size=48, wait=1.0,
        )

    def finish(self):
        self.get_card()
        self.note(R"Write both roots as residues in {0, 1, ..., 6}.")

        first = self.add_step(
            R"x_1 \equiv 3 \pmod 7",
            color=self.step_color, font_size=44, wait=0.6, isolate=["3"],
        )
        second = self.add_step(
            R"x_2 \equiv -3 \equiv 7 - 3 \equiv 4 \pmod 7",
            color=self.step_color, font_size=44, wait=0.9, isolate=["4"],
        )

        # Highlight the two answers where they sit
        ans1 = first["3"][0]
        ans2 = second["4"][0]
        self.play(
            ans1.animate.set_color(RESULT_COLOR),
            ans2.animate.set_color(RESULT_COLOR),
            run_time=0.5,
        )
        boxes = VGroup(
            SurroundingRectangle(ans1, color=RESULT_COLOR, buff=0.16),
            SurroundingRectangle(ans2, color=RESULT_COLOR, buff=0.16),
        )
        boxes.set_stroke(width=3)
        self.play(ShowCreation(boxes), run_time=0.6)
        self.play(
            FlashAround(ans1, color=RESULT_COLOR, time_width=1.5),
            FlashAround(ans2, color=RESULT_COLOR, time_width=1.5),
            run_time=1.4,
        )
        self.wait(1.5)

        first1 = self.add_step(
                    R"x_1 \equiv 3 \pmod 7",
                    color=self.step_color, font_size=44, wait=0.6,
                )
        first2 = self.add_step(
                            R"x_2 \equiv 4 \pmod 7",
                            color=self.step_color, font_size=44, wait=0.6,
                        )
        self.play(
                    FlashAround(first1, color=RESULT_COLOR, time_width=1.5),
                    FlashAround(first2, color=RESULT_COLOR, time_width=1.5),
                    run_time=1.4,
                )
        
