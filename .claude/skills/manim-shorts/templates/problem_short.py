from manim_imports_ext import *


# Render with:
#   ./render.sh .claude/skills/manim-shorts/templates/problem_short.py
#
# TEMPLATE for a "problem card + figure + steps" short (the channel's most
# common format).  Copy it to _2026/<Topic>/<snake_name>.py, then replace the
# problem, the figure, the palette and the sections.
#
# A square has diagonal 6.  Find its area.
# The diagonal cuts the square into two right isosceles triangles with legs s,
# so by Pythagoras s^2 + s^2 = 6^2, 2 s^2 = 36 and the area is s^2 = 18.
# Checked: s = 6 / sqrt 2 = 4.2426, s^2 = 18.0000.

FIG_WIDTH = 4.4          # the square while the solution runs
FIG_CENTER = 1.6 * UP

# One colour per quantity, used for it everywhere -- figure, labels and Tex
SIDE_C = "#58C4DD"       # the side s
DIAG_C = "#FF9F43"       # the diagonal, 6
AREA_C = "#5BD98A"       # the area


class SquareDiagonalArea(MockTestShort):
    """Area of a square from its diagonal, by Pythagoras."""

    test = ""                # "F1" here (and question = 21) tags the card F1:21
    step_font_size = 40
    step_buff = 0.45

    problem_tex = R"\text{A square has diagonal } 6.\\ \text{Find its area.}"

    sections = ["pose", "split", "solve", "outro"]
    upload = dict(
        title="Only One Line Needed",
        description="A square has diagonal 6. What is its area? One line of Pythagoras.",
        hashtags=["#math", "#shorts", "#geometry"],
        pinned_comment="Did you get 18?",
    )

    # The figure

    def make_figure(self):
        fig = GeoFigure({"A": (0, 1), "B": (1, 1), "C": (1, 0), "D": (0, 0)})
        fig.normalize(width=FIG_WIDTH, center=FIG_CENTER)
        self.fig = fig

        fill = fig.region("A", "B", "C", "D", color=AREA_C, opacity=0.18)
        square = fig.polygon("A", "B", "C", "D")
        diag = fig.segment("A", "C", stroke_color=DIAG_C, stroke_width=5)
        names = fig.labels({"A": UL, "B": UR, "C": DR, "D": DL})
        six = Tex("6", font_size=40).set_color(DIAG_C)
        six.move_to(fig.midpoint("A", "C") + 0.32 * UR)

        figure = VGroup(fill, square, diag, names, six)
        figure.fill, figure.diag = fill, diag
        return figure

    def get_figure(self):
        figure = self.lazy("figure", self.make_figure)
        self.steps_top_y = figure.get_bottom()[1] - 0.6
        return figure

    # Sections

    def pose(self):
        """Frame 0 is a CARD HOOK: title, card, the figure big and the question,
        stacked inside the grid-safe band.  Hold it, then settle into the
        working layout."""
        card = self.make_card()
        home = card.get_center().copy()
        figure = self.make_figure()
        question = Tex(R"\text{Area} = \,?", t2c={"?": YELLOW}, font_size=96)
        hook = card_hook("One Line Is Enough", card, figure.copy(), question)

        self.add(hook)
        self.wait(2.4)

        self.play(
            FadeOut(hook.title, 0.5 * UP), FadeOut(hook.question, 0.4 * DOWN),
            card.animate.move_to(home),
            ReplacementTransform(hook.figure, figure),
            run_time=1.2,
        )
        self.remove(hook)
        self.add(card, figure)
        self.set_state("card", card)
        self.set_state("figure", figure)
        self.get_figure()

    def split(self):
        self.get_card()
        self.get_figure()
        fig = self.fig

        # The diagonal cuts the square into two right triangles
        halves = VGroup(
            fig.region("A", "B", "C", color=SIDE_C, opacity=0.35),
            fig.region("A", "D", "C", color=AREA_C, opacity=0.35),
        )
        corner = fig.right_angle("A", "D", "C", size=0.32)
        legs = VGroup(
            Tex("s", font_size=44).set_color(SIDE_C).next_to(fig.midpoint("A", "D"), LEFT, buff=0.15),
            Tex("s", font_size=44).set_color(SIDE_C).next_to(fig.midpoint("D", "C"), DOWN, buff=0.15),
        )
        self.play(ShowCreationThenDestruction(self.get_figure().diag.copy().set_stroke(WHITE, 8)), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(h) for h in halves], lag_ratio=0.4), run_time=0.9)
        self.play(FadeIn(corner, scale=0.4), FadeIn(legs, lag_ratio=0.3), run_time=0.6)
        self.note("The diagonal makes two right triangles\nwith legs s: use Pythagoras.", wait=1.6)
        self.set_state("split", VGroup(halves, corner, legs))

    def solve(self):
        self.get_card()
        self.get_figure()
        self.lazy("split", VGroup)

        line = self.add_step(R"s^2 + s^2 = 6^2", wait=0.4)
        line = self.replace_step(line, R"2s^2 = 36", wait=0.4)
        self.replace_step(line, R"s^2 = 18", wait=0.3)
        self.note("A square's area is s², so we are done.", wait=1.2)
        self.play(Indicate(self.get_figure().fill, color=AREA_C), run_time=0.8)
        self.conclude(R"\text{Area} = 18")
