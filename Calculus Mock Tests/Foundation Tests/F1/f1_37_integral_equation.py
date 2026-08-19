from manim_imports_ext import *


class F1Q37(MockTestShort):
    # Render with:
    #   ./render.sh "Calculus Mock Tests/Foundation Tests/F1/f1_37_integral_equation.py"
    test = "F1"
    question = 37
    step_buff = 1.00

    problem_tex = (
        R"\int_0^x (x - t) f(t) \, dt = 2e^{2x} + ax + b \\"
        R"f(0) + a + b = \, ?"
    )

    sections = [
        "pose",
        "name_it",
        "leibniz",
        "match_at_zero",
        "read_off_f",
        "finish",
        "outro",
    ]

    # The three lines whose values are collected in `finish`.  Each is keyed
    # so the closing section can point at it even when the section that
    # animates it is not part of the render.
    results = {
        "b": (R"F(0) = 0 = 2 + b \quad \Longrightarrow \quad b = -2", ["-2"]),
        "a": (R"F'(0) = 0 = 4 + a \quad \Longrightarrow \quad a = -4", ["-4"]),
        "f": (R"f(x) = F''(x) = 8e^{2x} \quad \Longrightarrow \quad f(0) = 8", ["8"]),
    }

    # Naming the function and differentiating it happen in one slot, which is
    # then rewritten in place -- the derivation is scaffolding, only the rule
    # it produces is worth keeping on screen.
    work_tex = R"F(x) = \int_0^x (x - t) f(t) \, dt = 2e^{2x} + ax + b"

    def build_step(self, tex, color, font_size, isolate=()):
        line = Tex(tex, font_size=font_size, isolate=list(isolate))
        line.set_color(color)
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.steps().add(line)
        return line

    def work_line(self):
        return self.lazy(
            "work",
            lambda: self.build_step(self.work_tex, SETUP_COLOR, 32),
        )

    def get_result(self, key):
        tex, isolate = self.results[key]
        color = SETUP_COLOR if key != "f" else self.step_color
        return self.lazy(
            "res_" + key,
            lambda: self.build_step(tex, color, 34, isolate),
        )

    def show_result(self, key, wait=0.9):
        tex, isolate = self.results[key]
        color = SETUP_COLOR if key != "f" else self.step_color
        line = self.build_step(tex, color, 34, isolate)
        self.play(FadeIn(line, 0.15 * DOWN), run_time=1.0)
        self.wait(wait)
        return self.set_state("res_" + key, line)

    def name_it(self):
        self.get_card()
        self.note("Give the left-hand side a name, F(x).")
        line = self.build_step(self.work_tex, SETUP_COLOR, 32)
        self.play(FadeIn(line, 0.15 * DOWN), run_time=1.0)
        self.wait(0.8)
        self.set_state("work", line)

    def leibniz(self):
        self.get_card()
        self.note(
            "Leibniz rule, for an integral whose limit is x.\n"
            "Its boundary term is f(x)(x - x), which is 0."
        )
        # The x inside the integrand comes out; the boundary term vanishes
        applied = self.replace_step(
            self.work_line(),
            R"F'(x) = f(x)\,(x - x) + \int_0^x f(t) \, dt",
            color=SETUP_COLOR, font_size=34,
        )
        rule = self.replace_step(
            applied,
            R"F'(x) = \int_0^x f(t) \, dt, \quad F''(x) = f(x)",
            color=RULE_COLOR, font_size=34, wait=0.3,
        )
        box = SurroundingRectangle(rule, color=RULE_COLOR, buff=0.18)
        box.set_stroke(width=2)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(1.0)

    def match_at_zero(self):
        self.get_card()
        self.note("Both integrals vanish at x = 0, which pins a and b.")
        self.show_result("b")
        self.show_result("a")

    def read_off_f(self):
        self.get_card()
        self.note("Differentiating twice more leaves f by itself.")
        self.show_result("f")

    def finish(self):
        self.get_card()

        # The three values, where they sit in the lines above.  "8" occurs
        # twice in the f line -- in 8e^{2x} and in f(0) = 8 -- so take the last
        f_val = self.get_result("f")["8"][-1]
        a_val = self.get_result("a")["-4"][0]
        b_val = self.get_result("b")["-2"][0]
        values = [f_val, a_val, b_val]

        # `{}` keeps each sign a binary operator; isolating one would otherwise
        # start a group with the sign and lose the space in front of it.  The
        # first `=` is deliberately left out of the isolate list -- grouping it
        # with the left-hand side costs that same space -- so the head is taken
        # as whatever the other parts do not cover.
        total = Tex(
            R"f(0) + a + b = 8 {}- 4 {}- 2 {}= 2",
            font_size=44,
            isolate=["f(0) + a + b", "8", "{}- 4", "{}- 2", "{}= 2"],
        )
        total.set_color(RESULT_COLOR)
        self.place_step(total)
        self.steps().add(total)

        landing = [total["8"][0], total["{}- 4"][0], total["{}- 2"][0]]
        tail = total["{}= 2"][0]
        covered = set()
        for part in (tail, *landing):
            covered.update(part.family_members_with_points())
        head = VGroup(*[
            glyph for glyph in total.family_members_with_points()
            if glyph not in covered
        ])

        # 1) Call the three values out where they were found
        self.play(*[v.animate.set_color(RESULT_COLOR) for v in values], run_time=0.5)
        self.play(
            *[
                FlashAround(v, color=RESULT_COLOR, time_width=1.5, buff=0.12)
                for v in values
            ],
            run_time=1.2,
        )
        self.wait(0.3)

        # 2) Fly them down into the sum, so the answer is visibly assembled
        #    from the three results rather than appearing on its own
        self.play(Write(head), run_time=0.8)
        self.play(
            *[
                TransformFromCopy(value, slot)
                for value, slot in zip(values, landing)
            ],
            lag_ratio=0.15,
            run_time=1.4,
        )
        self.play(Write(tail), run_time=0.6)
        self.wait(0.3)

        # 3) Close on the boxed answer, as every question in the series does
        box = SurroundingRectangle(total, color=RESULT_COLOR, buff=0.22)
        box.set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(total, color=RESULT_COLOR, time_width=1.5), run_time=1.4)
        self.wait(1.5)
