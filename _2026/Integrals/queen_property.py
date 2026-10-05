from manim_imports_ext import *
import os


# Render with:
#   ./render.sh _2026/Integrals/queen_property.py
#
# Queen's rule:  int_0^{2a} f(x) dx = int_0^a ( f(x) + f(2a - x) ) dx.
# Split [0, 2a] at a.  On the right half put x = 2a - u: as x runs a -> 2a,
# u runs a -> 0, and dx = -du, so int_a^{2a} f(x) dx = int_0^a f(2a - u) du.
# On the graph: the right half folds over x = a and stacks onto the left.
#
# Example: I = int_0^pi sin^6 / (sin^6 + cos^6).  With a = pi/2, f(pi - x) = f(x),
# so I = 2J with J = int_0^{pi/2} f.  King on [0, pi/2] swaps sin and cos, and
# the two integrands add to 1, so 2J = pi/2, J = pi/4 and I = pi/2.

QUEEN_PNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Images", "queen.png")

F_COLOR = "#58C4DD"
G_COLOR = "#FF6B9A"
MIRROR = "#E6EDF5"
ROSE = "#FF8FB1"

A_HALF = 2.2                      # a, so the graph runs over [0, 2a]


def f(x):
    return 1.2 + 0.8 * np.sin(1.4 * x) + 0.15 * x


def s6(x):
    s, c = np.sin(x) ** 6, np.cos(x) ** 6
    return s / (s + c)


class QueenProperty(BrandOutroMixin, StepListMixin, ShortsScene):
    """Queen's rule for definite integrals, by folding, and an example."""

    step_font_size = 38
    step_buff = 0.36
    steps_top_y = -1.0
    sections = ["title", "fold", "substitute", "example", "outro"]

    def queen_formula(self, font_size=46):
        return Tex(
            R"\int_0^{2a} f(x)\,dx = \int_0^{a} \big(f(x) + f(2a - x)\big)\,dx",
            t2c={"f(x)": F_COLOR, "f(2a - x)": G_COLOR},
            font_size=font_size,
        )

    def get_pinned(self):
        def build():
            formula = self.queen_formula(38)
            box = SurroundingRectangle(formula, buff=0.22).set_stroke(ROSE, 3).set_fill(BLACK, 1)
            tag = Text("Queen's rule", font_size=26, weight=BOLD).set_color(ROSE).next_to(box, UP, buff=0.12)
            return VGroup(box, formula, tag).move_to(5.7 * UP)
        return self.lazy("pinned", build)

    def make_axes(self, x_max, y_max, width=6.6, height=3.3, center=1.65 * UP):
        axes = Axes(
            x_range=(0, x_max, 1), y_range=(0, y_max, 1), width=width, height=height,
            axis_config=dict(include_ticks=False, stroke_color=GREY_B, stroke_width=2),
        )
        return axes.move_to(center)

    def band(self, axes, lower, upper, x0, x1, color, opacity=0.4):
        """The region between two functions, as one filled shape."""
        xs = np.linspace(x0, x1, 80)
        pts = [axes.c2p(x, lower(x)) for x in xs] + [axes.c2p(x, upper(x)) for x in xs[::-1]]
        return Polygon(*pts).set_stroke(width=0).set_fill(color, opacity)

    # Sections

    def title(self):
        title = Text("Queen's Rule", font_size=66, weight=BOLD).set_color(ROSE).move_to(5.5 * UP)
        line = Line(LEFT, RIGHT).set_width(title.get_width() * 0.6).set_stroke(ROSE, 4).next_to(title, DOWN, buff=0.2)
        formula = self.queen_formula(52).set_max_width(7.3).next_to(line, DOWN, buff=0.55)
        queen = ImageMobject(QUEEN_PNG).set_height(6.3).next_to(formula, DOWN, buff=0.45)

        # The thumbnail frame: title, rule and the card
        self.add(title, line, formula, queen)
        self.wait(1.6)

        # The queen card reads the same after a half turn, like the two halves of [0, 2a]
        self.play(Rotate(queen, PI), run_time=1.6)
        self.wait(0.5)

        pinned = self.get_pinned()
        self.play(
            FadeOut(queen, 0.5 * DOWN), FadeOut(title, 0.4 * UP), FadeOut(line),
            ReplacementTransform(formula, pinned[1]), FadeIn(pinned[0]), FadeIn(pinned[2]),
            run_time=1.2,
        )

    def fold(self):
        self.get_pinned()
        a = A_HALF
        axes = self.make_axes(2 * a + 0.3, 4.2)
        graph = axes.get_graph(f, x_range=(0, 2 * a)).set_stroke(F_COLOR, 4)
        left = self.band(axes, lambda x: 0, f, 0, a, F_COLOR, 0.4)
        right = self.band(axes, lambda x: 0, f, a, 2 * a, G_COLOR, 0.4)
        ticks = VGroup(*[
            Tex(t, font_size=32).next_to(axes.c2p(x, 0), DOWN, buff=0.12) for x, t in [(0, "0"), (a, "a"), (2 * a, "2a")]
        ])
        name = Tex("f(x)", font_size=32).set_color(F_COLOR).next_to(axes.c2p(0.5, f(0.5)), UP, buff=0.12)
        self.play(ShowCreation(axes), FadeIn(ticks), run_time=0.7)
        self.play(ShowCreation(graph), FadeIn(name), run_time=1.1)
        self.play(FadeIn(left), FadeIn(right), run_time=0.6)
        self.note("Split [0, 2a] at the middle, x = a.", wait=1.0)

        # Fold the right half over the line x = a
        hinge = DashedLine(axes.c2p(a, 0), axes.c2p(a, 4.2), dash_length=0.1).set_stroke(MIRROR, 2)
        self.play(ShowCreation(hinge), run_time=0.5)
        right_graph = axes.get_graph(f, x_range=(a, 2 * a)).set_stroke(G_COLOR, 4)
        flap = VGroup(right.copy(), right_graph)
        self.play(Rotate(flap, PI, axis=UP, about_point=axes.c2p(a, 0)), right.animate.set_fill(opacity=0.08), run_time=1.8)

        # ...and stack it on top of the left half
        stacked = self.band(axes, f, lambda x: f(x) + f(2 * a - x), 0, a, G_COLOR, 0.45)
        top = axes.get_graph(lambda x: f(x) + f(2 * a - x), x_range=(0, a)).set_stroke(G_COLOR, 4)
        top_name = Tex("f(x) + f(2a - x)", font_size=30).set_color(G_COLOR).next_to(top.get_end(), UP, buff=0.1).shift(0.4 * LEFT)
        self.play(ReplacementTransform(flap[0], stacked), ReplacementTransform(flap[1], top), run_time=1.3)
        self.play(FadeIn(top_name), run_time=0.4)
        self.note("The right half, folded over, sits on the left half.", wait=1.2)
        self.set_state("graph", Group(axes, graph, left, right, ticks, name, hinge, stacked, top, top_name))

    def substitute(self):
        self.get_pinned()
        self.lazy("graph", Group)
        self.add_step(R"\int_0^{2a} f\,dx = \int_0^{a} f\,dx + \int_a^{2a} f\,dx", wait=0.5)
        self.add_step(R"x = 2a - u:\quad x = a \to u = a,\quad x = 2a \to u = 0", font_size=34, wait=0.5)
        work = self.add_step(R"\int_a^{2a} f(x)\,dx = -\int_a^{0} f(2a-u)\,du", color=G_COLOR, wait=0.5)
        self.replace_step(work, R"\int_a^{2a} f(x)\,dx = \int_0^{a} f(2a-u)\,du\ \checkmark", color=G_COLOR, wait=0.4)
        self.note("Add the two halves: that is Queen's rule.", wait=1.0)
        self.play(FlashAround(self.get_pinned()[1], color=ROSE, time_width=1.5), run_time=1.2)

    def example(self):
        self.get_pinned()
        graph = self.lazy("graph", Group)
        self.clear_steps()
        self.play(FadeOut(graph), run_time=0.5)

        problem = Tex(
            R"I = \int_0^{\pi} \frac{\sin^6 x}{\sin^6 x + \cos^6 x}\,dx", font_size=44,
        ).move_to(3.4 * UP)
        self.play(Write(problem), run_time=1.2)

        # The graph over [0, pi] is symmetric about pi/2
        axes = self.make_axes(PI + 0.2, 2.3, width=6.6, height=3.3, center=0.65 * UP)
        curve = axes.get_graph(s6, x_range=(0, PI)).set_stroke(F_COLOR, 4)
        left = self.band(axes, lambda x: 0, s6, 0, PI / 2, F_COLOR, 0.4)
        right = self.band(axes, lambda x: 0, s6, PI / 2, PI, G_COLOR, 0.4)
        ticks = VGroup(*[
            Tex(t, font_size=28).next_to(axes.c2p(x, 0), DOWN, buff=0.1)
            for x, t in [(0, "0"), (PI / 2, R"\tfrac{\pi}{2}"), (PI, R"\pi")]
        ], Tex("1", font_size=28).next_to(axes.c2p(0, 1), LEFT, buff=0.1))
        self.play(ShowCreation(axes), FadeIn(ticks), run_time=0.6)
        self.play(ShowCreation(curve), FadeIn(left), FadeIn(right), run_time=1.0)
        self.steps_top_y = axes.get_bottom()[1] - 0.55
        self.note("Queen with a = π/2: f(π − x) = f(x).", wait=1.0)

        # Fold the right half over pi/2: the left half, counted twice
        flap = VGroup(right.copy(), axes.get_graph(s6, x_range=(PI / 2, PI)).set_stroke(G_COLOR, 4))
        self.play(Rotate(flap, PI, axis=UP, about_point=axes.c2p(PI / 2, 0)), right.animate.set_fill(opacity=0.08), run_time=1.5)
        stacked = self.band(axes, s6, lambda x: 2 * s6(x), 0, PI / 2, G_COLOR, 0.45)
        self.play(ReplacementTransform(flap[0], stacked), FadeOut(flap[1]), run_time=1.0)
        self.add_step(R"I = 2J,\qquad J = \int_0^{\pi/2} \frac{\sin^6 x}{\sin^6 x + \cos^6 x}\,dx", font_size=34, wait=0.6)
        self.play(FadeOut(VGroup(stacked, right)), FadeOut(curve), FadeOut(left), run_time=0.5)

        # King on [0, pi/2]: sin and cos swap, and the two add to 1
        half = self.band(axes, lambda x: 0, s6, 0, PI / 2, F_COLOR, 0.5)
        mirror = self.band(axes, s6, lambda x: 1, 0, PI / 2, "#FF9F43", 0.5)
        roof = axes.get_graph(lambda x: 1, x_range=(0, PI / 2)).set_stroke(WHITE, 2)
        self.play(FadeIn(half), run_time=0.5)
        self.play(FadeIn(mirror, 0.3 * DOWN), ShowCreation(roof), run_time=0.9)
        self.note("King swaps sin and cos: together they fill\na 1 × π/2 rectangle, so 2J = π/2.", wait=1.4)
        self.add_step(R"J = \frac{\pi}{4} \quad\Rightarrow\quad I = 2J", wait=0.4)
        answer = self.add_step(R"I = \frac{\pi}{2}", color=YELLOW, font_size=54, wait=0.2)
        box = SurroundingRectangle(answer, buff=0.2).set_stroke(YELLOW, 4)
        self.play(ShowCreation(box), FlashAround(answer, color=YELLOW, time_width=1.5), run_time=1.2)
        self.wait(1.4)
