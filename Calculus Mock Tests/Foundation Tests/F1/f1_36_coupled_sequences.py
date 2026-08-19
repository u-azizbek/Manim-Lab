from manim_imports_ext import *


class F1Q36(MockTestShort):
    # Render with:
    #   ./render.sh "Calculus Mock Tests/Foundation Tests/F1/f1_36_coupled_sequences.py"
    test = "F1"
    question = 36
    step_buff = 0.85

    problem_tex = (
        R"a_1 = 5, \quad b_1 = 8 \\"
        R"a_{n+1} = 4b_n + 3, \quad b_{n+1} = 4a_n - 6 \\"
        R"\lim_{n \to \infty} \frac{a_n + b_n}{4^n} = \, ?"
    )

    sections = [
        "pose",
        "name_the_sum",
        "add_the_two",
        "solve_it",
        "finish",
        "outro",
    ]

    def name_the_sum(self):
        self.get_card()
        # Neither sequence is nice on its own, but their sum closes up
        self.add_step(
            R"c_n = a_n + b_n, \quad c_1 = 13",
            color=SETUP_COLOR, font_size=44, wait=0.9,
        )

    def add_the_two(self):
        self.get_card()
        added = self.add_step(
            R"c_{n+1} = (4b_n + 3) + (4a_n - 6) = 4c_n - 3",
            color=RULE_COLOR, font_size=38, wait=0.2,
        )
        box = SurroundingRectangle(added, color=RULE_COLOR, buff=0.18)
        box.set_stroke(width=2)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(1.0)

    def solve_it(self):
        self.get_card()
        shifted = self.add_step(
            R"c_{n+1} - 1 = 4 \, (c_n - 1)",
            font_size=42, wait=0.9,
        )
        # The empty `{}` before each sign is load-bearing: isolating "- 1" or
        # "+ 1" puts the sign at the start of its own group, where TeX reads it
        # as unary and drops the space in front of it.  `{}` gives it a left
        # operand so it stays a binary operator and the line keeps its proper
        # width.  The group renders as nothing.
        telescoped = self.transform_step(
            shifted,
            R"c_n {}- 1 = 12 \cdot 4^{\,n-1} = 3 \cdot 4^n",
            font_size=42, wait=1.0,
            isolate=["c_n", "{}- 1", R"3 \cdot 4^n"],
        )

        # The last two lines rearrange in the slot the telescoped line already
        # occupies rather than stacking, so the frame stays inside the card's
        # footprint and `finish` still has room beneath.
        #
        # Note the `12 \cdot 4^{n-1}` is dropped rather than carried across:
        # it was only a stepping stone to `3 \cdot 4^n`, and adding 1 to both
        # sides breaks the chain -- `12 \cdot 4^{n-1}` equals `3 \cdot 4^n`,
        # not `3 \cdot 4^n + 1`.
        solved = Tex(
            R"c_n = 3 \cdot 4^n {}+ 1",
            font_size=42, isolate=["c_n", "{}+ 1", R"3 \cdot 4^n"],
        )
        solved.set_color(self.step_color)
        solved.move_to(telescoped)

        # Carry the moved term in the answer colour so the eye follows it
        # across the equals sign, then let it settle back into the line.
        minus_one = telescoped["{}- 1"][0]
        plus_one = solved["{}+ 1"][0]
        plus_one.set_color(RESULT_COLOR)

        self.play(minus_one.animate.set_color(RESULT_COLOR), run_time=0.4)
        self.play(
            FlashAround(minus_one, color=RESULT_COLOR, time_width=1.5),
            run_time=1.0,
        )
        self.play(
            TransformMatchingTex(
                telescoped, solved,
                key_map={"{}- 1": "{}+ 1"},
                matched_keys=["c_n", R"3 \cdot 4^n"],
            ),
            run_time=1.3,
        )
        self.play(plus_one.animate.set_color(self.step_color), run_time=0.4)
        self.wait(0.6)

        # Put the sum back in terms of the original sequences, which is the
        # form the limit in `finish` is written against.
        final = Tex(
            R"a_n {}+ b_n = 3 \cdot 4^n {}+ 1",
            font_size=42, isolate=["a_n {}+ b_n", "{}+ 1", R"3 \cdot 4^n"],
        )
        final.set_color(self.step_color)
        final.move_to(solved)

        self.play(FlashAround(solved["c_n"][0], color=SETUP_COLOR, time_width=1.5), run_time=0.9)
        self.play(
            TransformMatchingTex(
                solved, final,
                key_map={"c_n": "a_n {}+ b_n"},
                matched_keys=[R"3 \cdot 4^n", "{}+ 1"],
            ),
            run_time=1.3,
        )
        self.wait(1.0)

        # Keep the step list pointing at what is actually on screen, so the
        # next section stacks below the rearranged line rather than the
        # telescoped one it replaced.
        self.steps().remove(telescoped)
        self.steps().add(final)

    def finish(self):
        self.get_card()
        self.add_step(
            R"\lim_{n \to \infty}\frac{a_n + b_n}{4^n} = \lim_{n \to \infty}\left(3 + \frac{1}{4^n}\right)",
            font_size=44, wait=0.9,
        )
        self.conclude(R"= 3")
