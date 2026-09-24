from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Puzzles/double_factorial_mod.py
#
# Remainder of 2025!! = 1 * 3 * 5 * ... * 2025 on division by 2026.
#
# 2026 = 2 * 1013 with 2 and 1013 coprime, so work mod each part:
#   mod 2:     every factor is odd, so N = 1 (mod 2)
#   mod 1013:  1013 is odd and at most 2025, so it is one of the factors,
#              and N = 0 (mod 1013)
# Chinese remainder theorem: one residue mod 2026 does both -- the multiple
# of 1013 that is odd, which is 1013 itself.  Checked by multiplying out
# mod 2026 directly.

MOD_TWO = "#4FD1C5"
MOD_BIG = "#FF9F43"
GOOD = "#5BD98A"
BAD = "#FF5C5C"
HIGHLIGHT = YELLOW

PRODUCT_Y = 4.05
SPLIT_Y = 3.05
PANEL_Y = 0.95
SYSTEM_Y = -1.45
LINE_Y = -2.95
ANSWER_Y = -4.1
CAPTION_Y = -4.9


def row(tokens, font_size=36, buff=0.12):
    """A line of math built from separate pieces, so each piece can be moved,
    coloured or swapped on its own."""
    return VGroup(*[Tex(t, font_size=font_size) for t in tokens]).arrange(RIGHT, buff=buff)


class DoubleFactorialMod(MockTestShort):
    """2025!! mod 2026, by splitting 2026 = 2 * 1013 and the CRT."""

    test = ""
    card_top_buff = 0.6

    problem_tex = (
        R"\text{Find the remainder when}\\"
        R"2025!! \text{ is divided by } 2026."
    )

    sections = [
        "pose",
        "example",
        "product",
        "split",
        "mod_two",
        "mod_big",
        "crt",
        "outro",
    ]

    def caption(self, message, wait=1.4):
        text = Text(message, font_size=26).set_color(self.note_color)
        text.set_max_width(7.4).move_to(CAPTION_Y * UP)
        self.play(FadeIn(text, 0.15 * UP), run_time=0.4)
        self.wait(wait)
        self.play(FadeOut(text), run_time=0.3)

    # Sections

    def example(self):
        self.get_card()

        # 5!: every number from 5 down to 1...
        full = row(["5!!", "=", "5", R"\cdot", "4", R"\cdot", "3", R"\cdot", "2", R"\cdot", "1"], 44)
        full.set_y(PRODUCT_Y)
        self.play(FadeIn(full[:2]), LaggedStartMap(FadeIn, full[2:], shift=0.2 * DOWN, lag_ratio=0.1), run_time=1.0)

        # ...but the double factorial skips every other one
        skipped = VGroup(full[4], full[5], full[8], full[9])
        self.play(VGroup(full[4], full[8]).animate.set_color(BAD), run_time=0.4)
        self.play(FadeOut(skipped, 0.6 * DOWN), run_time=0.6)
        short = row(["5!!", "=", "5", R"\cdot", "3", R"\cdot", "1", "=", "15"], 44).set_y(PRODUCT_Y)
        kept = [0, 1, 2, 3, 6, 7, 10]
        self.play(
            *[ReplacementTransform(full[i], short[j]) for j, i in enumerate(kept)],
            FadeIn(short[-2:], 0.2 * LEFT),
            run_time=0.9,
        )
        self.caption("Double factorial: multiply every other number down to 1.", wait=1.2)
        self.set_state("example", short)

    def product(self):
        example = self.lazy("example", VGroup)

        # 2025!! is every odd number up to 2025 -- and 1013 is one of them
        main = row([
            "N", "=", "2025!!", "=", "1", R"\cdot", "3", R"\cdot", "5",
            R"\cdots", "1013", R"\cdots", "2025",
        ], 38).set_y(PRODUCT_Y)
        self.play(FadeOut(example, 0.4 * UP), run_time=0.4)
        self.play(FadeIn(main[:3]), run_time=0.5)
        self.play(LaggedStartMap(FadeIn, main[3:], shift=0.2 * DOWN, lag_ratio=0.08), run_time=1.0)
        self.caption("All the odd numbers from 1 to 2025.", wait=0.9)
        self.set_state("main", main)

    def split(self):
        main = self.get_main()

        # Split the modulus into two coprime parts
        factors = row(["2026", "=", "2", R"\cdot", "1013"], 40).set_y(SPLIT_Y)
        factors[2].set_color(MOD_TWO)
        factors[4].set_color(MOD_BIG)
        self.play(Write(factors), run_time=0.9)

        panels = VGroup()
        for x, color, title in [(-1.88, MOD_TWO, R"\text{mod } 2"), (1.88, MOD_BIG, R"\text{mod } 1013")]:
            box = RoundedRectangle(width=3.6, height=2.75, corner_radius=0.2)
            box.set_stroke(color, 2.5).set_fill(color, 0.1).move_to([x, PANEL_Y, 0])
            heading = Tex(title, font_size=36).set_color(color)
            heading.move_to(box.get_top() + 0.4 * DOWN)
            panels.add(VGroup(box, heading))
        arrows = VGroup(
            Arrow(factors[2].get_bottom(), panels[0].get_top(), buff=0.12).set_color(MOD_TWO),
            Arrow(factors[4].get_bottom(), panels[1].get_top(), buff=0.12).set_color(MOD_BIG),
        )
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3),
            LaggedStart(*[FadeIn(p, 0.2 * DOWN) for p in panels], lag_ratio=0.3),
            run_time=1.1,
        )
        self.caption("2 and 1013 share no factor: solve mod each, then combine.", wait=1.3)
        self.set_state("factors", VGroup(factors, arrows))
        self.set_state("panels", panels)

    def get_main(self):
        return self.lazy("main", lambda: row([
            "N", "=", "2025!!", "=", "1", R"\cdot", "3", R"\cdot", "5",
            R"\cdots", "1013", R"\cdots", "2025",
        ], 38).set_y(PRODUCT_Y))

    def get_panels(self):
        return self.lazy("panels", VGroup)

    def mod_two(self):
        main = self.get_main()
        panel = self.get_panels()[0]
        box = panel[0]

        # Copy the factors down into the mod 2 panel
        factors = row(["1", R"\cdot", "3", R"\cdot", "5", R"\cdots", "2025"], 34)
        factors.move_to(box).shift(0.05 * UP)
        self.play(*[
            TransformFromCopy(main[i], factors[j])
            for j, i in enumerate([4, 5, 6, 7, 8, 9, 12])
        ], run_time=1.0)

        # Every one of them is odd, so every one is 1 mod 2
        odd = VGroup(factors[0], factors[2], factors[4], factors[6])
        self.play(LaggedStart(*[Indicate(m, color=MOD_TWO) for m in odd], lag_ratio=0.2), run_time=0.8)
        ones = row(["1", R"\cdot", "1", R"\cdot", "1", R"\cdots", "1"], 34).move_to(factors)
        ones.set_color(MOD_TWO)
        self.play(*[Transform(factors[k], ones[k]) for k in range(len(ones))], run_time=0.8)
        self.caption("Odd times odd is odd: each factor is 1 mod 2.", wait=1.0)

        result = Tex(R"N \equiv 1 \pmod{2}", font_size=34).set_color(MOD_TWO)
        result.move_to(box.get_bottom() + 0.45 * UP)
        self.play(TransformFromCopy(factors, result), run_time=0.8)
        self.set_state("result_two", result)

    def mod_big(self):
        main = self.get_main()
        panel = self.get_panels()[1]
        box = panel[0]

        factors = row(["1", R"\cdot", "3", R"\cdots", "1013", R"\cdots", "2025"], 34)
        factors.move_to(box).shift(0.05 * UP)
        self.play(*[
            TransformFromCopy(main[i], factors[j])
            for j, i in enumerate([4, 5, 6, 9, 10, 11, 12])
        ], run_time=1.0)

        # 1013 is odd and at most 2025, so it is one of the factors
        ring = SurroundingRectangle(main[10], buff=0.08).set_stroke(HIGHLIGHT, 3)
        self.play(ShowCreation(ring), factors[4].animate.set_color(HIGHLIGHT), run_time=0.6)
        self.caption("1013 is odd and below 2025: it is one of the factors.", wait=1.1)

        # Pull it out to the front
        pulled = row(["N", "=", "1013", R"\cdot", "k"], 34).move_to(factors)
        pulled[2].set_color(HIGHLIGHT)
        self.play(
            ReplacementTransform(factors[4], pulled[2]),
            FadeOut(VGroup(*factors[:4], *factors[5:]), 0.2 * DOWN),
            FadeIn(VGroup(pulled[:2], pulled[3:]), 0.2 * DOWN),
            FadeOut(ring),
            run_time=1.0,
        )
        result = Tex(R"N \equiv 0 \pmod{1013}", font_size=34).set_color(MOD_BIG)
        result.move_to(box.get_bottom() + 0.45 * UP)
        self.play(TransformFromCopy(pulled, result), run_time=0.8)
        self.wait(0.4)
        self.set_state("result_big", result)

    def crt(self):
        results = VGroup(
            self.lazy("result_two", VGroup),
            self.lazy("result_big", VGroup),
        )

        # Both conditions together
        system = VGroup(
            Tex(R"N \equiv 1 \pmod{2}", font_size=38).set_color(MOD_TWO),
            Tex(R"N \equiv 0 \pmod{1013}", font_size=38).set_color(MOD_BIG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        brace = Brace(system, LEFT, buff=0.12)
        VGroup(brace, system).move_to(SYSTEM_Y * UP)
        self.play(
            *[TransformFromCopy(r, s) for r, s in zip(results, system)],
            GrowFromCenter(brace),
            run_time=1.1,
        )
        self.caption("Chinese remainder theorem: exactly one N mod 2026 does both.", wait=1.3)

        # Multiples of 1013 below 2026: 0 and 1013.  Only one is odd.
        line = NumberLine((0, 2026, 1013), width=6.4, include_tip=False)
        line.set_stroke(GREY_A, 2).move_to(LINE_Y * UP)
        ends = VGroup(*[
            Tex(str(v), font_size=28).next_to(line.n2p(v), DOWN, buff=0.14) for v in (0, 1013, 2026)
        ])
        self.play(ShowCreation(line), FadeIn(ends, lag_ratio=0.2), run_time=0.8)
        dots = VGroup(*[Dot(line.n2p(v), radius=0.1).set_fill(MOD_BIG) for v in (0, 1013)])
        self.play(
            LaggedStart(*[FadeIn(d, scale=0.4) for d in dots], lag_ratio=0.4),
            Indicate(system[1], color=MOD_BIG, scale_factor=1.05),
            run_time=0.8,
        )
        verdicts = VGroup(
            Tex(R"\text{even}\ \times", font_size=30).set_color(BAD),
            Tex(R"\text{odd}\ \checkmark", font_size=30).set_color(GOOD),
        )
        for verdict, d in zip(verdicts, dots):
            verdict.next_to(d, UP, buff=0.2)
        verdicts[0].shift(max(0, -3.75 - verdicts[0].get_left()[0]) * RIGHT)
        self.play(Indicate(system[0], color=MOD_TWO, scale_factor=1.05), FadeIn(verdicts, 0.1 * UP, lag_ratio=0.4), run_time=0.8)
        self.play(dots[0].animate.set_fill(BAD, 0.4), dots[1].animate.scale(1.4).set_fill(GOOD), run_time=0.6)

        # The odd multiple is the answer
        answer = Tex(R"2025!! \equiv 1013 \pmod{2026}", isolate=["1013"], font_size=48)
        answer.move_to(ANSWER_Y * UP)
        head = VGroup(*[g for g in answer.family_members_with_points()
                        if g not in answer["1013"][0].family_members_with_points()])
        self.play(
            TransformFromCopy(ends[1], answer["1013"][0]),
            FadeIn(head),
            run_time=1.0,
        )
        self.play(answer.animate.set_color(RESULT_COLOR), run_time=0.3)
        box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.2).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(answer, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.wait(1.5)
