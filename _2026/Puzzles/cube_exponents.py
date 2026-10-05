from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Puzzles/cube_exponents.py
#
# 8^x = 27^y = 125^z = 30.  Find xyz / (xy + xz + yz).
# Raise each equation to the reciprocal power: 30^(1/x) = 8 = 2^3,
# 30^(1/y) = 27 = 3^3, 30^(1/z) = 125 = 5^3.  Multiply:
# 30^(1/x + 1/y + 1/z) = (2*3*5)^3 = 30^3, so 1/x + 1/y + 1/z = 3.
# Dividing top and bottom by xyz, xyz / (xy + xz + yz) = 1 / (1/x + 1/y + 1/z) = 1/3.
# No logarithms needed.

X_C = "#58C4DD"
Y_C = "#5BD98A"
Z_C = "#FF9F43"
COLORS = [X_C, Y_C, Z_C]
LETTERS = {"x": X_C, "y": Y_C, "z": Z_C}
SIDES = [2, 3, 5]
COL_X = [-2.55, 0.0, 2.55]
CUBE_UNIT = 0.3


def iso_cube(n, color, u=CUBE_UNIT):
    """An n x n x n block of unit cubes in isometric view: three faces with their grids."""
    ex, ey, ez = u * np.array([0.866, -0.5, 0]), u * np.array([-0.866, -0.5, 0]), u * UP

    def pt(x, y, z):
        return x * ex + y * ey + z * ez

    faces = VGroup(
        Polygon(pt(0, 0, n), pt(n, 0, n), pt(n, n, n), pt(0, n, n)),
        Polygon(pt(n, 0, 0), pt(n, n, 0), pt(n, n, n), pt(n, 0, n)),
        Polygon(pt(0, n, 0), pt(n, n, 0), pt(n, n, n), pt(0, n, n)),
    )
    for face, opacity in zip(faces, (0.6, 0.38, 0.22)):
        face.set_fill(color, opacity).set_stroke(color, 2.5)
    grid = VGroup(*[
        line
        for k in range(1, n)
        for line in (
            Line(pt(k, 0, n), pt(k, n, n)), Line(pt(0, k, n), pt(n, k, n)),
            Line(pt(n, 0, k), pt(n, n, k)), Line(pt(n, k, 0), pt(n, k, n)),
            Line(pt(0, n, k), pt(n, n, k)), Line(pt(k, n, 0), pt(k, n, n)),
        )
    ]).set_stroke(color, 1.2, opacity=0.7)
    return VGroup(faces, grid)


class CubeExponents(MockTestShort):
    """8^x = 27^y = 125^z = 30 without logarithms: 8, 27, 125 are cubes of 2, 3, 5."""

    test = ""
    step_buff = 0.55
    step_font_size = 46

    problem_tex = (
        R"8^x = 27^y = 125^z = 30\\"
        R"\text{Find}\ \ \frac{xyz}{xy + xz + yz}"
    )

    sections = ["pose", "invert", "multiply", "finish", "outro"]

    def tex(self, text, font_size=None, **kwargs):
        return Tex(text, t2c=LETTERS, font_size=font_size or self.step_font_size, **kwargs)

    def add_colored(self, text, font_size=None, wait=0.4):
        """`add_step` paints the whole line one colour; this keeps x, y, z coloured."""
        line = self.tex(text, font_size=font_size)
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.steps().add(line)
        self.play(FadeIn(line, 0.15 * DOWN), run_time=1.0)
        if wait:
            self.wait(wait)
        return line

    def swap_row(self, texs, key_maps=None, run_time=1.2, wait=0.5):
        """Rewrite the three columns in place, all at once."""
        old = self.row
        new = VGroup(*[self.tex(t, font_size=42) for t in texs])
        for col, src in zip(new, old):
            col.move_to(src)
        key_maps = key_maps or [{}] * 3
        self.play(*[
            TransformMatchingTex(src, dst, key_map=km) for src, dst, km in zip(old, new, key_maps)
        ], run_time=run_time)
        self.row = new
        self.steps().set_submobjects([new])
        if wait:
            self.wait(wait)

    # Sections

    def pose(self):
        # The thumbnail: title, problem card with the logo, the three cubes, the question
        card = self.make_card()
        home = card.get_center().copy()
        title = Text("No Logs Needed!", font_size=64, weight=BOLD)
        title.set_color_by_gradient(*COLORS)
        title.move_to(6.25 * UP)
        card.next_to(title, DOWN, buff=0.4)

        cubes = VGroup(*[iso_cube(n, c) for n, c in zip(SIDES, COLORS)])
        cubes.arrange(RIGHT, buff=0.45, aligned_edge=DOWN).next_to(card, DOWN, buff=0.75)
        values = VGroup(*[
            Tex(str(n ** 3), font_size=44).set_color(c).next_to(cube, DOWN, buff=0.2)
            for n, c, cube in zip(SIDES, COLORS, cubes)
        ])
        values.set_y(values[2].get_y())
        question = Tex(R"\frac{xyz}{xy + xz + yz} = \,?", t2c={**LETTERS, "?": YELLOW}, font_size=84)
        question.next_to(values, DOWN, buff=0.7)
        # The badge's synapse lines are a fixed width; thin them with the badge
        logo = NeuroEduLogo(height=1.9)
        logo.edges.set_stroke(width=2.2 * logo.get_height() / 2)
        brand = Group(
            logo, Text("@neuroeduz", font_size=48, weight=BOLD).set_color(WHITE),
        ).arrange(RIGHT, buff=0.4).next_to(question, DOWN, buff=0.75)

        self.add(title, card, cubes, values, question, brand)
        self.wait(2.6)

        # Card up to its pinned spot; the cubes shrink into three columns under it
        settled = card.copy().move_to(home)
        base_y = settled.get_bottom()[1] - 0.5 - 2.3
        targets = VGroup(*[cube.copy().set_height(2.3 * n / 5) for n, cube in zip(SIDES, cubes)])
        for target, x in zip(targets, COL_X):
            target.move_to([x, base_y, 0], aligned_edge=DOWN)
        value_targets = VGroup(*[
            value.copy().scale(0.95).next_to(target, DOWN, buff=0.15) for value, target in zip(values, targets)
        ])
        value_targets.set_y(value_targets[2].get_y())
        self.play(
            FadeOut(title, 0.5 * UP), FadeOut(question, 0.4 * DOWN), FadeOut(brand, 0.4 * DOWN),
            card.animate.move_to(home),
            *[Transform(cube, target) for cube, target in zip(cubes, targets)],
            *[Transform(value, target) for value, target in zip(values, value_targets)],
            run_time=1.3,
        )
        self.set_state("card", card)
        self.cubes, self.values = cubes, values
        # The children moved one by one, so read them rather than the group's stale box
        self.steps_top_y = min(value.get_bottom()[1] for value in values) - 0.6

    def invert(self):
        # One column per cube
        row = VGroup(*[self.tex(t, font_size=42) for t in (R"8^x = 30", R"27^y = 30", R"125^z = 30")])
        for col, x in zip(row, COL_X):
            col.set_x(x)
        row.set_y(self.steps_top_y - row.get_height() / 2)
        self.row = row
        self.steps().add(row)
        self.play(LaggedStart(*[FadeIn(col, 0.15 * DOWN) for col in row], lag_ratio=0.25), run_time=1.0)
        self.wait(0.4)

        # Raise each side to the reciprocal power: the exponent jumps across
        self.note("Raise both sides to the power 1/x (and 1/y, 1/z).", wait=0.9)
        self.swap_row([R"8 = 30^{1/x}", R"27 = 30^{1/y}", R"125 = 30^{1/z}"], wait=0.3)
        self.swap_row([R"30^{1/x} = 8", R"30^{1/y} = 27", R"30^{1/z} = 125"], wait=0.4)

        # 8, 27 and 125 are cubes
        cubes_as_powers = [R"2^3", R"3^3", R"5^3"]
        new_values = VGroup(*[
            Tex(t, font_size=38).set_color(c).move_to(v) for t, c, v in zip(cubes_as_powers, COLORS, self.values)
        ])
        self.play(
            LaggedStart(*[Indicate(cube, scale_factor=1.08, color=None) for cube in self.cubes], lag_ratio=0.3),
            *[TransformMatchingTex(v, nv) for v, nv in zip(self.values, new_values)],
            run_time=1.3,
        )
        self.values = new_values
        self.swap_row(
            [R"30^{1/x} = 2^3", R"30^{1/y} = 3^3", R"30^{1/z} = 5^3"],
            key_maps=[{"8": "2^3"}, {"27": "3^3"}, {"125": "5^3"}], wait=0.3,
        )
        self.note("8, 27, 125 are cubes of 2, 3, 5, and 2 · 3 · 5 = 30.", wait=1.2)

    def multiply(self):
        # Multiply the three columns together
        product = self.transform_step(
            self.row, R"30^{1/x} \cdot 30^{1/y} \cdot 30^{1/z} = 2^3 \cdot 3^3 \cdot 5^3",
            t2c=LETTERS, run_time=1.3, wait=0.4,
        )
        self.note("Same base: add the exponents.  Same power: multiply the bases.", wait=1.3)
        product = self.replace_step(
            product, R"30^{1/x + 1/y + 1/z} = (2 \cdot 3 \cdot 5)^3", colors=LETTERS, wait=0.5,
        )
        product = self.replace_step(
            product, R"30^{1/x + 1/y + 1/z} = 30^3", colors=LETTERS, wait=0.3,
        )
        self.play(Flash(product.get_right() + 0.3 * LEFT, color=YELLOW), run_time=0.7)
        self.note("Equal powers of 30: the exponents are equal.", wait=0.9)
        key = self.add_colored(R"\frac{1}{x} + \frac{1}{y} + \frac{1}{z} = 3", font_size=50, wait=0.2)
        box = SurroundingRectangle(key, buff=0.18).set_stroke(RULE_COLOR, 3)
        self.play(ShowCreation(box), run_time=0.5)
        self.wait(0.6)
        self.key = VGroup(key, box)

    def finish(self):
        # Keep only the key fact
        steps = [m for m in self.steps() if m is not self.key[0]]
        self.play(
            *[FadeOut(m, 0.2 * UP) for m in steps],
            self.key.animate.set_y(self.steps_top_y - self.key.get_height() / 2),
            run_time=0.7,
        )
        self.steps().set_submobjects([self.key])

        target = self.add_colored(R"\frac{xyz}{xy + xz + yz}", font_size=52, wait=0.3)
        self.note("Divide the top and the bottom by xyz.", wait=1.0)
        target = self.replace_step(
            target, R"\frac{xyz}{xy + xz + yz} = \frac{1}{\frac{1}{z} + \frac{1}{y} + \frac{1}{x}}",
            colors=LETTERS, font_size=52, wait=0.6,
        )
        self.play(Indicate(self.key[0], color=RULE_COLOR), run_time=0.8)
        self.replace_step(
            target, R"\frac{xyz}{xy + xz + yz} = \frac{1}{3}", colors=LETTERS, font_size=52, wait=0.2,
        )
        answer = self.steps()[-1]
        box = SurroundingRectangle(answer, buff=0.22).set_stroke(YELLOW, 4)
        self.play(ShowCreation(box), answer.animate.set_color(YELLOW), run_time=0.6)
        self.play(FlashAround(answer, color=YELLOW, time_width=1.5), run_time=1.3)
        self.wait(1.4)
