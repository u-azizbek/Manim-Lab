from manim_imports_ext import *


A_ENTRIES = [[3, 1], [-7, -2]]

A_COLOR = BLUE_B
I_COLOR = GREEN_B
RESULT_COLOR = YELLOW


class MatrixPower2024(ShortsScene):
    # 9:16 portrait for YouTube Shorts.  Render with:
    #   ./render.sh _2026/matrix/matrix_power_2024.py
    # or a single beat with:
    #   ./render.sh -s find_the_cycle _2026/matrix/matrix_power_2024.py
    sections = [
        "show_problem",
        "rule_out_brute_force",
        "apply_cayley_hamilton",
        "find_the_cycle",
        "reduce_the_exponent",
        "compute_the_answer",
    ]

    # State shared between sections

    def make_A_group(self):
        A_group = VGroup(Tex("A = ", font_size=72), IntegerMatrix(A_ENTRIES, height=1.7))
        A_group[1].set_color(A_COLOR)
        A_group.arrange(RIGHT, buff=0.25)
        return A_group

    def make_header(self):
        header = self.make_A_group()
        header.set_height(0.75)
        return self.pin_to_top(header, buff=0.5)

    def get_header(self):
        return self.lazy("header", self.make_header)

    def make_key_eq(self):
        key_eq = Tex(
            R"A^2 = A - I",
            font_size=64,
            t2c={"A^2": RESULT_COLOR, "I": I_COLOR},
        )
        group = VGroup(key_eq, SurroundingRectangle(key_eq, color=RESULT_COLOR, buff=0.25))
        return group.next_to(self.get_header(), DOWN, buff=0.6)

    def get_key_eq(self):
        return self.lazy("key_eq", self.make_key_eq)

    def make_punchline(self):
        punchline = Tex(R"A^{2024} = A^2", font_size=72).set_color(RESULT_COLOR)
        group = VGroup(
            punchline,
            SurroundingRectangle(punchline, color=RESULT_COLOR, buff=0.25),
        )
        return group.next_to(self.get_header(), DOWN, buff=0.6)

    def get_punchline(self):
        return self.lazy("punchline", self.make_punchline)

    # Sections

    def show_problem(self):
        title = Text("A 2024th Power", font_size=54).set_color(A_COLOR)
        self.pin_to_top(title, buff=1.5)
        underline = Underline(title, stroke_color=A_COLOR)

        A_group = self.make_A_group()
        A_label, A_matrix = A_group

        question = TexText(
            R"Find the sum of all\\entries of $A^{2024}$",
            font_size=48,
            t2c={"A^{2024}": RESULT_COLOR},
        )
        question.set_width(6.5)

        VGroup(A_group, question).arrange(DOWN, buff=1.4).move_to(0.5 * UP)

        self.play(Write(title), ShowCreation(underline), run_time=1.2)
        self.play(FadeIn(A_label), Write(A_matrix), run_time=1.5)
        self.wait(0.3)
        self.play(FadeIn(question, 0.3 * DOWN), run_time=1.2)
        self.wait(1.0)

        # Shrink the definition into a header pinned for the rest of the video
        self.play(
            FadeOut(title, UP),
            FadeOut(underline, UP),
            FadeOut(question, 0.3 * DOWN),
            Transform(A_group, self.make_header()),
            run_time=1.2,
        )
        self.set_state("header", A_group)

    def rule_out_brute_force(self):
        brute = Tex(
            R"A^{2024} = \underbrace{A \cdot A \cdots A}_{2024 \text{ times}}",
            font_size=44,
        )
        brute.set_width(6.8)

        better = Text("But there is a pattern hiding here.", font_size=34).set_color(GREY_A)
        better.set_width(6.5)

        VGroup(brute, better).arrange(DOWN, buff=1.4).move_to(0.5 * UP)
        cross = Cross(brute)

        self.play(Write(brute), run_time=1.5)
        self.wait(0.4)
        self.play(ShowCreation(cross), run_time=0.7)
        self.wait(0.4)
        self.play(FadeIn(better, 0.2 * DOWN), run_time=1.0)
        self.wait(0.7)
        self.play(
            FadeOut(VGroup(brute, cross), UP),
            FadeOut(better, UP),
            run_time=0.8,
        )

    def apply_cayley_hamilton(self):
        name = Text("Cayley–Hamilton", font_size=40).set_color(A_COLOR)
        name.next_to(self.get_header(), DOWN, buff=0.7)
        name_box = SurroundingRectangle(name, color=A_COLOR, buff=0.2)
        name_box.set_stroke(width=2)

        facts = VGroup(
            Tex(R"\text{tr}(A) = 3 + (-2) = 1", font_size=42),
            Tex(R"\det(A) = (3)(-2) - (1)(-7) = 1", font_size=42),
        )
        facts.arrange(DOWN, buff=0.45)
        facts.set_width(6.8)
        facts.next_to(name_box, DOWN, buff=0.8)

        char_eq = Tex(R"A^2 - \text{tr}(A) \, A + \det(A) \, I = 0", font_size=40)
        char_eq.set_width(6.8)
        char_eq.next_to(facts, DOWN, buff=1.0)

        simple_eq = Tex(R"A^2 - A + I = 0", font_size=52)
        simple_eq.next_to(char_eq, DOWN, buff=0.6)

        key_group = self.make_key_eq()
        key_eq, key_box = key_group
        key_group.next_to(simple_eq, DOWN, buff=0.8)

        self.play(FadeIn(name), ShowCreation(name_box), run_time=0.9)
        self.play(FadeIn(facts[0], 0.2 * DOWN), run_time=0.9)
        self.play(FadeIn(facts[1], 0.2 * DOWN), run_time=0.9)
        self.wait(0.4)
        self.play(Write(char_eq), run_time=1.4)
        self.wait(0.5)
        self.play(TransformMatchingTex(char_eq.copy(), simple_eq), run_time=1.2)
        self.wait(0.5)
        self.play(TransformMatchingTex(simple_eq.copy(), key_eq), run_time=1.2)
        self.play(ShowCreation(key_box), run_time=0.6)
        self.wait(0.7)

        # Keep only the key identity, moved up out of the way
        self.play(
            FadeOut(VGroup(name, name_box, facts, char_eq, simple_eq), UP),
            key_group.animate.next_to(self.get_header(), DOWN, buff=0.6),
            run_time=1.0,
        )
        self.set_state("key_eq", key_group)

    def find_the_cycle(self):
        cube_steps = Tex(R"A^3 = A \cdot A^2 = A(A - I) = A^2 - A", font_size=40)
        cube_steps.set_width(6.8)
        cube_steps.next_to(self.get_key_eq(), DOWN, buff=0.9)

        cube_finish = Tex(R"= (A - I) - A = -I", font_size=44)
        cube_finish.set_width(5.0)
        cube_finish.next_to(cube_steps, DOWN, buff=0.45)

        cube_result = Tex(R"A^3 = -I", font_size=72, t2c={"-I": I_COLOR})
        cube_result.next_to(cube_finish, DOWN, buff=0.9)
        cube_box = SurroundingRectangle(cube_result, color=I_COLOR, buff=0.25)

        self.play(Write(cube_steps), run_time=1.6)
        self.wait(0.4)
        self.play(Write(cube_finish), run_time=1.4)
        self.wait(0.4)
        self.play(
            FadeTransform(cube_finish.copy(), cube_result),
            ShowCreation(cube_box),
            run_time=1.2,
        )
        self.wait(0.8)

        sixth = Tex(R"A^6 = (A^3)^2 = (-I)^2 = I", font_size=44)
        sixth.set_width(6.0)
        sixth.next_to(cube_result, DOWN, buff=0.9)

        self.play(Write(sixth), run_time=1.5)
        self.wait(0.5)

        self.play(
            FadeOut(VGroup(cube_steps, cube_finish, cube_result, cube_box), UP),
            FadeOut(self.get_key_eq(), UP),
            sixth.animate.next_to(self.get_header(), DOWN, buff=0.7),
            run_time=1.0,
        )
        self.show_cycle_wheel(sixth)

    def show_cycle_wheel(self, sixth):
        radius = 1.9
        center = 1.3 * DOWN
        angles = [PI / 2 - i * TAU / 6 for i in range(6)]
        points = [
            center + radius * np.array([np.cos(a), np.sin(a), 0])
            for a in angles
        ]

        circle = Circle(radius=radius)
        circle.set_stroke(GREY_D, 2)
        circle.move_to(center)

        colors = color_gradient([A_COLOR, TEAL_A, GREEN_A], 6)
        dots = Group(*[
            GlowDot(point, color=color)
            for point, color in zip(points, colors)
        ])
        labels = VGroup(*[
            Tex(tex, font_size=42).set_color(color).move_to(
                center + (radius + 0.7) * normalize(point - center)
            )
            for tex, point, color in zip(
                ["A", "A^2", "-I", "-A", "-A^2", "I"], points, colors
            )
        ])

        tracer = TrueDot(points[0], radius=0.08, color=RESULT_COLOR)

        self.play(ShowCreation(circle), FadeIn(tracer), run_time=0.8)
        for i in range(6):
            anims = [FadeIn(dots[i]), FadeIn(labels[i], scale=0.7)]
            if i > 0:
                arc = Arc(
                    start_angle=angles[i - 1],
                    angle=-TAU / 6,
                    radius=radius,
                    arc_center=center,
                )
                anims.append(MoveAlongPath(tracer, arc))
            self.play(*anims, run_time=0.55)

        # One more step lands back where it started
        self.play(
            MoveAlongPath(
                tracer,
                Arc(
                    start_angle=angles[5],
                    angle=-TAU / 6,
                    radius=radius,
                    arc_center=center,
                ),
            ),
            run_time=0.55,
        )

        period = Text("Back to the start every 6 steps", font_size=34).set_color(RESULT_COLOR)
        period.set_width(6.5)
        period.next_to(circle, DOWN, buff=1.2)

        self.play(FadeIn(period, 0.2 * DOWN), run_time=1.0)
        self.play(LaggedStartMap(FlashAround, labels, lag_ratio=0.15), run_time=1.6)
        self.wait(0.4)

        # Each section clears what it put on screen, so any one of them can
        # be rendered on its own
        wheel = Group(circle, dots, labels, tracer, period, sixth)
        self.play(FadeOut(wheel, UP), run_time=0.8)

    def reduce_the_exponent(self):
        division = Tex(R"2024 = 6 \times 337 + 2", font_size=52)
        division.set_width(6.2)
        division.next_to(self.get_header(), DOWN, buff=1.0)

        reduction = Tex(R"A^{2024} = (A^6)^{337} \cdot A^2 = I \cdot A^2", font_size=42)
        reduction.set_width(6.8)
        reduction.next_to(division, DOWN, buff=1.1)

        punchline_group = self.make_punchline()
        punchline, punchline_box = punchline_group
        punchline_group.next_to(reduction, DOWN, buff=1.1)

        self.play(Write(division), run_time=1.4)
        self.wait(0.5)
        self.play(Write(reduction), run_time=1.6)
        self.wait(0.5)
        self.play(
            FadeTransform(reduction.copy(), punchline),
            ShowCreation(punchline_box),
            run_time=1.2,
        )
        self.wait(0.7)

        self.play(
            FadeOut(VGroup(division, reduction), UP),
            punchline_group.animate.next_to(self.get_header(), DOWN, buff=0.6),
            run_time=1.0,
        )
        self.set_state("punchline", punchline_group)

    def compute_the_answer(self):
        recall = Tex(R"A^2 = A - I", font_size=48)
        recall.next_to(self.get_punchline(), DOWN, buff=0.9)

        subtraction = Tex(
            R"\begin{bmatrix} 3 & 1 \\ -7 & -2 \end{bmatrix}"
            R"-"
            R"\begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}"
            R"=",
            font_size=44,
        )
        subtraction.set_width(6.0)
        subtraction.next_to(recall, DOWN, buff=0.8)

        result = IntegerMatrix([[2, 1], [-7, -3]], height=1.5)
        result.set_color(RESULT_COLOR)
        result.next_to(subtraction, DOWN, buff=0.7)

        self.play(FadeIn(recall, 0.2 * DOWN), run_time=0.9)
        self.play(Write(subtraction), run_time=1.6)
        self.play(Write(result), run_time=1.2)
        self.wait(0.5)

        # Build "2 + 1 - 7 - 3" out of separate pieces so each number can fly
        # out of its matrix entry
        terms = [R"2", R"+\,1", R"-\,7", R"-\,3"]
        sum_eq = Tex(R"\;".join(terms), font_size=56, isolate=terms)
        sum_eq.next_to(result, DOWN, buff=1.0)

        self.play(
            LaggedStart(*[
                TransformFromCopy(entry, sum_eq[term])
                for entry, term in zip(result.get_entries(), terms)
            ], lag_ratio=0.3),
            run_time=2.0,
        )
        self.wait(0.4)

        answer = Tex(R"= -7", font_size=88).set_color(RESULT_COLOR)
        answer.next_to(sum_eq, DOWN, buff=0.8)
        answer_box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.3)
        answer_box.set_stroke(width=4)

        self.play(FadeTransform(sum_eq.copy(), answer), run_time=1.0)
        self.play(ShowCreation(answer_box), run_time=0.6)
        self.play(FlashAround(answer, time_width=1.5), run_time=1.5)
        self.wait(1.5)
