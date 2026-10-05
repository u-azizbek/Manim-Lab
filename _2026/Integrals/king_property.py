from manim_imports_ext import *
import os


# Render with:
#   ./render.sh _2026/Integrals/king_property.py
#
# King's property:  int_a^b f(x) dx = int_a^b f(a + b - x) dx.
# Visually: x -> a + b - x reflects [a, b] in its midpoint, so the graph of
# f(a + b - x) is the mirror image of f and bounds the same area.  In symbols:
# u = a + b - x, du = -dx, and the limits a, b swap, which the minus sign
# undoes.
#
# Example: I = int_0^{pi/2} sqrt(sin)/(sqrt(sin) + sqrt(cos)).  King turns sin
# into cos, so I = int_0^{pi/2} sqrt(cos)/(sqrt(cos) + sqrt(sin)); the two
# integrands add to 1, so 2I = pi/2 and I = pi/4.  On the graph f and its
# mirror stack to fill the 1 x pi/2 rectangle.

KING_PNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Images", "king.png")

F_COLOR = "#58C4DD"
G_COLOR = "#FF9F43"
MIRROR = "#E6EDF5"
GOLD = "#FFD166"

A_X, B_X = 0.8, 4.4


def f(x):
    return 1.2 + 0.8 * np.sin(1.4 * x) + 0.15 * x


def h(x):
    s, c = np.sqrt(max(np.sin(x), 0)), np.sqrt(max(np.cos(x), 0))
    return s / (s + c) if s + c > 0 else 0.5


class KingProperty(BrandOutroMixin, StepListMixin, ShortsScene):
    """King's property of definite integrals, by reflection, and an example."""

    step_font_size = 38
    step_buff = 0.36
    steps_top_y = -1.0
    sections = ["title", "reflect", "substitute", "example", "outro"]

    def king_formula(self, font_size=46):
        return Tex(
            R"\int_a^b f(x)\,dx = \int_a^b f(a + b - x)\,dx",
            t2c={"f(x)": F_COLOR, "f(a + b - x)": G_COLOR},
            font_size=font_size,
        )

    def get_pinned(self):
        def build():
            formula = self.king_formula(40)
            box = SurroundingRectangle(formula, buff=0.22).set_stroke(GOLD, 3).set_fill(BLACK, 1)
            tag = Text("King's property", font_size=26, weight=BOLD).set_color(GOLD)
            tag.next_to(box, UP, buff=0.12)
            pinned = VGroup(box, formula, tag).move_to(5.7 * UP)
            return pinned
        return self.lazy("pinned", build)

    def make_axes(self, x_max, y_max, width=6.6, height=3.3, center=1.65 * UP):
        axes = Axes(
            x_range=(0, x_max, 1), y_range=(0, y_max, 1), width=width, height=height,
            axis_config=dict(include_ticks=False, stroke_color=GREY_B, stroke_width=2),
        )
        return axes.move_to(center)

    # Sections

    def title(self):
        title = Text("King's Property", font_size=66, weight=BOLD).set_color(GOLD)
        title.move_to(5.5 * UP)
        line = Line(LEFT, RIGHT).set_width(title.get_width() * 0.6).set_stroke(GOLD, 4).next_to(title, DOWN, buff=0.2)
        formula = self.king_formula(54).set_max_width(7.2).next_to(line, DOWN, buff=0.55)
        king = ImageMobject(KING_PNG).set_height(6.4).next_to(formula, DOWN, buff=0.45)

        # The thumbnail frame: title, formula and the card, all at once
        self.add(title, line, formula, king)
        self.wait(1.6)

        # A king card reads the same upside down, as the integral does under x -> a + b - x
        self.play(Rotate(king, PI), run_time=1.6)
        self.wait(0.5)

        pinned = self.get_pinned()
        self.play(
            FadeOut(king, 0.5 * DOWN), FadeOut(title, 0.4 * UP), FadeOut(line),
            ReplacementTransform(formula, pinned[1]), FadeIn(pinned[0]), FadeIn(pinned[2]),
            run_time=1.2,
        )

    def reflect(self):
        self.get_pinned()
        axes = self.make_axes(5, 3)
        mid = (A_X + B_X) / 2
        graph = axes.get_graph(f, x_range=(A_X, B_X)).set_stroke(F_COLOR, 4)
        area = axes.get_area_under_graph(graph, fill_color=F_COLOR, fill_opacity=0.35)
        ends = VGroup(*[
            VGroup(DashedLine(axes.c2p(x, 0), axes.c2p(x, f(x)), dash_length=0.07).set_stroke(GREY_B, 1.5),
                   Tex(t, font_size=34).next_to(axes.c2p(x, 0), DOWN, buff=0.12))
            for x, t in [(A_X, "a"), (B_X, "b")]
        ])
        name = Tex("f(x)", font_size=34).set_color(F_COLOR).next_to(axes.c2p(1.2, f(1.2)), UP, buff=0.12)
        self.play(ShowCreation(axes), run_time=0.7)
        self.play(ShowCreation(graph), FadeIn(ends), FadeIn(name), run_time=1.2)
        self.play(FadeIn(area), run_time=0.5)

        # Flip it about the middle of [a, b]
        mirror = DashedLine(axes.c2p(mid, 0), axes.c2p(mid, 3), dash_length=0.1).set_stroke(MIRROR, 2)
        mid_label = Tex(R"\tfrac{a+b}{2}", font_size=28).next_to(axes.c2p(mid, 0), DOWN, buff=0.12)
        self.play(ShowCreation(mirror), FadeIn(mid_label), run_time=0.6)
        flip = VGroup(graph.copy(), area.copy())
        flip[0].set_stroke(G_COLOR)
        flip[1].set_fill(G_COLOR, 0.35)
        self.play(
            Rotate(flip, PI, axis=UP, about_point=axes.c2p(mid, 0)),
            graph.animate.set_stroke(opacity=0.35), area.animate.set_fill(opacity=0.1),
            run_time=1.8,
        )
        g_name = Tex("f(a+b-x)", font_size=34).set_color(G_COLOR).next_to(axes.c2p(B_X - 0.6, f(A_X + 0.6)), UP, buff=0.12)
        self.play(FadeIn(g_name), run_time=0.4)

        # Any x and its partner a + b - x swap heights
        t = ValueTracker(1.3)
        pair = always_redraw(lambda: VGroup(
            Line(axes.c2p(t.get_value(), 0), axes.c2p(t.get_value(), f(A_X + B_X - t.get_value()))).set_stroke(G_COLOR, 4),
            Line(axes.c2p(A_X + B_X - t.get_value(), 0), axes.c2p(A_X + B_X - t.get_value(), f(A_X + B_X - t.get_value()))).set_stroke(F_COLOR, 4),
            Dot(axes.c2p(t.get_value(), 0), radius=0.06).set_fill(G_COLOR),
            Dot(axes.c2p(A_X + B_X - t.get_value(), 0), radius=0.06).set_fill(F_COLOR),
        ))
        self.play(FadeIn(pair), run_time=0.4)
        self.play(t.animate.set_value(2.2), run_time=1.4)
        self.play(t.animate.set_value(1.0), run_time=1.2)
        self.play(FadeOut(pair), run_time=0.3)
        self.note("A mirror image of the graph: the same area.", wait=1.2)
        self.set_state("graph", Group(axes, graph, area, ends, name, mirror, mid_label, flip, g_name))

    def substitute(self):
        self.get_pinned()
        self.lazy("graph", Group)
        line = self.add_step(R"u = a + b - x,\quad du = -\,dx", wait=0.4)
        self.add_step(R"x = a \to u = b,\qquad x = b \to u = a", wait=0.5)
        work = self.add_step(R"\int_a^b f(a+b-x)\,dx = -\int_b^a f(u)\,du", color=G_COLOR, wait=0.6)
        self.replace_step(work, R"\int_a^b f(a+b-x)\,dx = \int_a^b f(u)\,du\ \checkmark", color=G_COLOR, wait=0.4)
        self.note("Swapping the limits cancels the minus sign.", wait=1.2)
        pinned = self.get_pinned()
        self.play(FlashAround(pinned[1], color=GOLD, time_width=1.5), run_time=1.2)

    def example(self):
        self.get_pinned()
        graph = self.lazy("graph", Group)
        self.clear_steps()
        self.play(FadeOut(graph), run_time=0.5)

        # The integral, and what King does to it
        problem = Tex(
            R"I = \int_0^{\pi/2} \frac{\sqrt{\sin x}}{\sqrt{\sin x} + \sqrt{\cos x}}\,dx",
            t2c={R"\sqrt{\sin x}}{": F_COLOR}, font_size=44,
        ).move_to(3.35 * UP)
        self.play(Write(problem), run_time=1.3)
        self.steps_top_y = problem.get_bottom()[1] - 0.35
        self.note("King with a + b = π/2 turns sin x into cos x.", wait=1.1)
        twin = self.add_step(
            R"I = \int_0^{\pi/2} \frac{\sqrt{\cos x}}{\sqrt{\cos x} + \sqrt{\sin x}}\,dx", color=G_COLOR, font_size=42, wait=0.6,
        )

        # The two integrands add to 1: on the graph they fill a rectangle
        axes = self.make_axes(PI / 2 + 0.15, 1.2, width=5.6, height=2.9, center=1.7 * DOWN)
        lower = axes.get_graph(h, x_range=(0.0001, PI / 2 - 0.0001)).set_stroke(F_COLOR, 3)
        low_area = axes.get_area_under_graph(lower, fill_color=F_COLOR, fill_opacity=0.45)
        top = axes.get_graph(lambda x: 1, x_range=(0, PI / 2)).set_stroke(WHITE, 2)
        between = VMobject().set_points_as_corners([
            *[axes.c2p(x, h(x)) for x in np.linspace(0.0001, PI / 2 - 0.0001, 80)],
            axes.c2p(PI / 2, 1), axes.c2p(0, 1),
        ]).close_path().set_stroke(width=0).set_fill(G_COLOR, 0.45)
        labels = VGroup(
            Tex("0", font_size=30).next_to(axes.c2p(0, 0), DOWN, buff=0.1),
            Tex(R"\tfrac{\pi}{2}", font_size=30).next_to(axes.c2p(PI / 2, 0), DOWN, buff=0.1),
            Tex("1", font_size=30).next_to(axes.c2p(0, 1), LEFT, buff=0.1),
        )
        self.play(ShowCreation(axes), FadeIn(labels), run_time=0.6)
        self.play(ShowCreation(lower), FadeIn(low_area), run_time=1.0)
        self.play(FadeIn(between, 0.3 * DOWN), ShowCreation(top), run_time=1.0)
        self.note("Blue + orange = 1 at every x: a 1 × π/2 rectangle.", wait=1.3)

        steps = self.steps()
        self.play(FadeOut(twin), run_time=0.3)
        steps.set_submobjects([])
        self.steps_top_y = axes.get_bottom()[1] - 0.6
        self.add_step(R"2I = \int_0^{\pi/2} 1\,dx = \frac{\pi}{2}", wait=0.5)
        answer = self.add_step(R"I = \frac{\pi}{4}", color=YELLOW, font_size=54, wait=0.2)
        box = SurroundingRectangle(answer, buff=0.2).set_stroke(YELLOW, 4)
        self.play(ShowCreation(box), FlashAround(answer, color=YELLOW, time_width=1.5), run_time=1.2)
        self.wait(1.5)
