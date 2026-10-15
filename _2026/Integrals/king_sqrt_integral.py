from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Integrals/king_sqrt_integral.py
#
# I = int_0^1 x^2 / (x + sqrt(1 - x^2)) dx.
# Substitute x = sin t: dx = cos t dt, sqrt(1 - x^2) = cos t (cos t >= 0 on
# [0, pi/2]), and the limits 0, 1 become 0, pi/2:
#   (1)  I = int_0^{pi/2} sin^2 t cos t / (sin t + cos t) dt.
# King's property, t -> pi/2 - t, swaps sin and cos:
#   (2)  I = int_0^{pi/2} cos^2 t sin t / (cos t + sin t) dt.
# Add (1) and (2): the numerator is sin t cos t (sin t + cos t), the
# denominator cancels, 2I = int_0^{pi/2} sin t cos t dt = 1/2, so I = 1/4.
# Checked (scipy quad): the original, (1) and (2) are each 0.250000, their sum
# is 0.500000, and int_0^{pi/2} sin t cos t dt = 0.500000.

SIN_C = "#58C4DD"          # sin t, everywhere
COS_C = "#FF9F43"          # cos t, everywhere
KING_C = "#FFD166"         # King's property
CANCEL_C = "#FF6B6B"
RESULT_C = YELLOW

ORIGINAL = R"\int_0^1 \frac{x^2}{x + \sqrt{1 - x^2}}\,dx"
SUB = R"I = \int_0^{\pi/2} \frac{\sin^2 t\,\cos t}{\sin t + \cos t}\,dt"
KING = R"I = \int_0^{\pi/2} \frac{\cos^2 t\,\sin t}{\cos t + \sin t}\,dt"
SUM = R"2I = \int_0^{\pi/2} \frac{\sin^2 t\,\cos t + \cos^2 t\,\sin t}{\sin t + \cos t}\,dt"
FACTORED = R"2I = \int_0^{\pi/2} \frac{\sin t\,\cos t\,(\sin t + \cos t)}{\sin t + \cos t}\,dt"
CANCELLED = R"2I = \int_0^{\pi/2} \sin t\,\cos t\,dt"
HALF = R"2I = \frac{1}{2}"

TRIG = {R"\sin^2 t": SIN_C, R"\sin t": SIN_C, R"\cos^2 t": COS_C, R"\cos t": COS_C}
DENOMINATORS = [R"\sin t + \cos t", R"\cos t + \sin t", R"(\sin t + \cos t)"]
ORIGINAL_KEYS = ["x^2", R"\sqrt{1 - x^2}", "dx", "^1", "{x}"]

HEADER_Y = 5.4
RULES_Y = 4.1
ROW_Y = [2.4, 0.1, -2.2]          # (1), (2), and the line they add up to
LINE_SIZE = 54


class KingSqrtIntegral(NarrationMixin, BrandOutroMixin, ShortsScene):
    """int_0^1 x^2 / (x + sqrt(1 - x^2)) dx = 1/4: sine substitution, then King's property."""

    speech_wps = 2.7
    caption_y = -4.2
    sections = ["hook", "substitute", "king", "combine", "finish", "outro"]
    upload = dict(
        title="One Swap Kills This Integral",
        description="A square root that looks impossible, gone in 20 seconds: x = sin t, then King's property.",
        hashtags=["#math", "#shorts", "#calculus", "#integral"],
        pinned_comment="Had you seen King's property before?",
    )

    # Lines

    def trig_line(self, tex, font_size=LINE_SIZE):
        line = Tex(tex, t2c=TRIG, isolate=[d for d in DENOMINATORS if d in tex], font_size=font_size)
        line.set_max_width(6.7)       # room for the (1) / (2) tags
        return line

    def make_original(self, prefix=""):
        return Tex(prefix + ORIGINAL, isolate=ORIGINAL_KEYS, font_size=72)

    def make_header(self):
        header = self.make_original("I = ").set_height(1.3)
        return header.move_to(HEADER_Y * UP)

    def get_header(self):
        return self.lazy("header", self.make_header)

    def get_row(self, index, tex):
        """Row (1) or (2) as VGroup(line, number), for sections run alone."""
        def build():
            line = self.trig_line(tex).move_to(ROW_Y[index] * UP)
            return VGroup(line, self.tag(line, f"({index + 1})"))
        return self.lazy(f"row{index}", build)

    def tag(self, line, label, color=GREY_B):
        """The (1) / (2) equation number beside a line."""
        number = Tex(label, font_size=34).set_color(color)
        number.next_to(line, LEFT, buff=0.15).align_to(line, DOWN)
        return number

    # Sections

    def hook(self):
        """Frame 0 is a FORMULA HOOK: title, the integral huge, the teaser."""
        hook = formula_hook("Looks Impossible?", self.make_original(), "One swap solves it.")
        self.add(hook)
        self.narrate("This integral looks impossible. One swap solves it.")
        self.play(FadeOut(hook.title, 0.4 * UP), FadeOut(hook.teaser, 0.4 * DOWN), run_time=0.4)
        header = self.make_header()
        self.play(TransformMatchingTex(hook.formula, header), run_time=0.8)
        self.remove(hook)
        self.add(header)
        self.set_state("header", header)

    def substitute(self):
        """x = sin t: each piece of the integrand turns into its trig form where it sits."""
        header = self.get_header()
        rules = Tex(
            R"x = \sin t \qquad dx = \cos t\,dt \qquad \sqrt{1 - x^2} = \cos t",
            t2c=TRIG, font_size=36,
        ).move_to(RULES_Y * UP)
        self.say("Let {b:x = sin t,} so the root becomes {o:cos t.}", FadeIn(rules, 0.2 * DOWN),
                 speak="Let x be sine t, so the square root becomes cosine t.", run_time=0.6, wait=False)

        source = header.copy()
        line = self.trig_line(SUB).move_to(ROW_Y[0] * UP)
        self.play(
            source.animate.move_to(ROW_Y[0] * UP).scale(line.get_height() / header.get_height()),
            run_time=0.6,
        )
        self.play(TransformMatchingTex(
            source, line,
            matched_pairs=[
                (source["^1"], line[R"^{\pi/2}"]),
                (source["x^2"][0], line[R"\sin^2 t"]),
                (source["x"][1], line[R"\sin t"]),
                (source[R"\sqrt{1 - x^2}"], line[R"\cos t"][1]),
                (source["dx"], VGroup(line[R"\cos t"][0], line["dt"])),
            ],
        ), run_time=1.4)
        number = self.tag(line, "(1)")
        self.play(FadeIn(number), run_time=0.3)
        self.hold()
        self.play(FadeOut(rules), run_time=0.3)
        self.set_state("row0", VGroup(line, number))

    def king(self):
        """t -> pi/2 - t swaps sin and cos in place: the colours trade places."""
        self.get_header()
        first = self.get_row(0, SUB)[0]

        rule = Tex(R"t \to \tfrac{\pi}{2} - t", font_size=36).set_color(KING_C)
        rule.move_to(np.mean([ROW_Y[0], ROW_Y[1]]) * UP).shift(2.4 * RIGHT)
        self.say("{y:King's property:} swap {b:sine} and {o:cosine.}", FadeIn(rule, 0.2 * LEFT),
                 speak="King's property: swap sine and cosine.", run_time=0.4, wait=False)

        source = first.copy()
        line = self.trig_line(KING).move_to(ROW_Y[1] * UP)
        self.play(source.animate.move_to(line), run_time=0.6)
        self.play(TransformMatchingTex(
            source, line,
            matched_pairs=[
                (source[R"\sin^2 t"], line[R"\cos^2 t"]),
                (source[R"\cos t"][0], line[R"\sin t"][0]),
                (source[R"\sin t"], line[R"\cos t"]),
                (source[R"\cos t"][1], line[R"\sin t"][1]),
            ],
        ), run_time=1.2)
        number = self.tag(line, "(2)")
        self.play(FadeIn(number), run_time=0.3)
        self.hold()
        self.set_state("row1", VGroup(line, number, rule))

    def combine(self):
        """(1) + (2): the numerators stack over the one shared denominator."""
        self.get_header()
        first, second = self.get_row(0, SUB), self.get_row(1, KING)
        one, two = first[0], second[0]

        self.say("Add them, and {y:the bottom cancels!}", speak="Add the two, and the bottom cancels!", wait=False)
        total = self.trig_line(SUM).move_to(ROW_Y[2] * UP)
        # Everything shared comes down from (1); only the numerator of (2)
        # flies in, and the rest of its copy fades where it stands
        a, b = one.copy(), two.copy()
        b_top = VGroup(b[R"\cos^2 t"], b[R"\sin t"][0])
        b_rest = VGroup(*[m for m in b.family_members_with_points() if m not in b_top.family_members_with_points()])
        self.play(
            TransformMatchingShapes(
                VGroup(a, b_top), total,
                matched_pairs=[
                    (VGroup(a[R"\sin^2 t"], a[R"\cos t"][0]), VGroup(total[R"\sin^2 t"], total[R"\cos t"][0])),
                    (b_top, VGroup(total[R"\cos^2 t"], total[R"\sin t"][0])),
                    (a[R"\sin t + \cos t"], total[R"\sin t + \cos t"]),
                    (a["I"], total["I"]),
                ],
            ),
            FadeOut(b_rest),
            first.animate.set_opacity(0.4), second.animate.set_opacity(0.4),
            run_time=1.3,
        )

        # Factor sin t cos t out of the top, then strike the common factor
        factored = self.trig_line(FACTORED).move_to(total)
        self.play(TransformMatchingTex(total, factored), run_time=1.0)
        strikes = VGroup(*[
            Line(part.get_corner(DL), part.get_corner(UR)).set_stroke(CANCEL_C, 5)
            for part in (factored[R"(\sin t + \cos t)"], factored[R"\sin t + \cos t"][-1])
        ])
        self.play(ShowCreation(strikes, lag_ratio=0.3), run_time=0.5)
        cancelled = self.trig_line(CANCELLED).move_to(total)
        self.play(
            TransformMatchingTex(factored, cancelled),
            FadeOut(strikes),
            run_time=0.9,
        )
        self.hold()
        self.set_state("row2", cancelled)

    def finish(self):
        """The last integral is 1/2, so I is a quarter: boxed, flashed."""
        self.get_header()
        first, second = self.get_row(0, SUB), self.get_row(1, KING)
        line = self.lazy("row2", lambda: self.trig_line(CANCELLED).move_to(ROW_Y[2] * UP))

        self.say("That is one half, so {y:I = 1/4.}", speak="That is one half, so I is one quarter.", wait=False)
        half = Tex(HALF, font_size=56).move_to(line)
        self.play(TransformMatchingTex(line, half), run_time=0.8)
        answer = Tex(R"I = \frac{1}{4}", font_size=84).set_color(RESULT_C).move_to(line)
        self.play(
            TransformMatchingTex(half, answer),
            FadeOut(VGroup(first, second), 0.3 * UP),
            run_time=0.8,
        )
        box = SurroundingRectangle(answer, buff=0.25).set_stroke(RESULT_C, 4)
        self.play(ShowCreation(box), FlashAround(answer, color=RESULT_C, time_width=1.5), run_time=1.0)
        self.hold(0.5)
