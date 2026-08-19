from manim_imports_ext import *


class F1Q27(MockTestShort):
    # Render with:
    #   ./render.sh "Calculus Mock Tests/Foundation Tests/F1/f1_27_trig_limit.py"
    test = "F1"
    question = 27
    step_buff = 1.00

    problem_tex = (
        R"\lim_{x \to 0} "
        R"\frac{2x^3 + 3 \sin x \, (1 - \cos 2x)}{x (1 - \cos 2x)} = \, ?"
    )

    sections = [
        "pose",
        "key_identity",
        "split_it",
        "each_piece",
        "finish",
        "outro",
    ]

    def key_identity(self):
        self.get_card()
        identity = self.add_step(
            R"1 - \cos 2x = 2 \sin^2 x",
            color=RULE_COLOR, font_size=46, wait=0.2,
        )
        box = SurroundingRectangle(identity, color=RULE_COLOR, buff=0.18)
        box.set_stroke(width=2)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(1.0)

    def split_it(self):
        self.get_card()
        # The second term cancels the awkward factor outright
        self.add_step(
            R"\frac{2x^3 + 3 \sin x (1 - \cos 2x)}{x(1 - \cos 2x)}"
            R"= \frac{2x^3}{x(1 - \cos 2x)} + \frac{3 \sin x}{x}",
            color=SETUP_COLOR, font_size=33, wait=1.1,
        )

    def each_piece(self):
        self.get_card()
        # `isolate` registers the answer digits as their own atoms so `finish`
        # can pick them out reliably (bare substring selection is unreliable
        # once a line carries exponents and \commands).
        first = self.add_step(
            R"\lim_{x \to 0}\frac{2x^3}{x \cdot 2\sin^2 x} = \lim_{x \to 0}\frac{x^2}{\sin^2 x}=1",
            font_size=42, wait=0.9, isolate=["1"],
        )
        second = self.transform_step(
            first,
            R"\lim_{x \to 0}\frac{3 \sin x}{x} \; = 3",
            font_size=42, wait=1.0, isolate=["3"],
        )
        # Kept so `finish` can lift each piece's answer into the final sum
        self.first_piece = first
        self.second_piece = second

    def finish(self):
        self.get_card()

        # The two limits' answers, where they sit in the pieces above.
        # "1" occurs once; "3" occurs twice (coefficient, then answer) -- take
        # the last, which is the answer.
        one = self.first_piece["1"][0]
        three = self.second_piece["3"][-1]

        # 1) Call them out in place
        self.play(
            one.animate.set_color(RESULT_COLOR),
            three.animate.set_color(RESULT_COLOR),
            run_time=0.5,
        )
        self.play(
            FlashAround(one, color=RESULT_COLOR, time_width=1.5, buff=0.12),
            FlashAround(three, color=RESULT_COLOR, time_width=1.5, buff=0.12),
            run_time=1.1,
        )
        self.wait(0.3)

        # 2) Assemble "1 + 3 = 4" underneath, flying the highlighted 1 and 3
        #    down into place so the sum is visibly built from the two pieces.
        total = Tex(R"1 + 3 = 4", font_size=52, isolate=["1", "3", "+", "=", "4"])
        total.set_color(RESULT_COLOR)
        self.place_step(total)
        self.steps().add(total)

        rest = VGroup(total["+"][0], total["="][0], total["4"][0])
        self.play(
            TransformFromCopy(one, total["1"][0]),
            TransformFromCopy(three, total["3"][0]),
            run_time=1.2,
        )
        self.play(Write(rest), run_time=0.7)
        self.wait(0.3)

        # 3) Box and flash the result, matching the series' closing beat
        box = SurroundingRectangle(total, color=RESULT_COLOR, buff=0.22)
        box.set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(total, color=RESULT_COLOR, time_width=1.5), run_time=1.4)
        self.wait(1.5)
