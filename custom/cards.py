from __future__ import annotations

from manimlib import *

from custom.outro import channel_mark
from custom.shorts import ShortsScene, StepListMixin


CARD_BG = "#EAF1FB"       # pale blue paper
CARD_EDGE = "#8FB4E3"
CARD_INK = "#101828"      # near-black, for text on the light card


class ProblemCard(VGroup):
    """A rounded, light-backed card holding the problem statement, with the
    channel mark tucked into a corner.

    The card sizes itself to the content, so a long expression widens the box
    rather than spilling out of it.
    """

    def __init__(
        self,
        tex: str,
        width: float = 7.2,
        pad_x: float = 0.42,
        pad_y: float = 0.46,
        font_size: int = 46,
        bg: ManimColor = CARD_BG,
        edge: ManimColor = CARD_EDGE,
        ink: ManimColor = CARD_INK,
        corner_radius: float = 0.26,
        logo_height: float = 0.62,
        label: str = "",
    ):
        super().__init__()

        self.body = Tex(tex, font_size=font_size)
        self.body.set_color(ink)

        self.logo = channel_mark(height=logo_height)
        logo_room = 0.0 if self.logo is None else self.logo.get_width() + 0.30

        self.body.set_max_width(width - 2 * pad_x - logo_room)

        self.tag = VGroup()
        if label:
            self.tag = Text(label, font_size=24, weight=BOLD).set_color("#5B6B85")

        height = self.body.get_height() + 2 * pad_y
        if self.logo is not None:
            height = max(height, self.logo.get_height() + 2 * pad_y)

        self.rect = RoundedRectangle(
            width=width, height=height, corner_radius=corner_radius,
        )
        self.rect.set_fill(bg, 1).set_stroke(edge, 3)

        self.body.move_to(self.rect)
        if self.logo is not None:
            # Sit the mark in the corner and nudge the statement off it
            self.logo.next_to(self.rect.get_corner(UR), DL, buff=0.26)
            self.body.shift(0.5 * logo_room * LEFT)
        if len(self.tag) > 0:
            self.tag.next_to(self.rect.get_corner(UL), DR, buff=0.24)

        self.add(self.rect, self.body)
        if self.logo is not None:
            self.add(self.logo)
        if len(self.tag) > 0:
            self.add(self.tag)


class CardSolutionScene(StepListMixin, ShortsScene):
    """A short built as: problem card pinned at the top, solution steps
    stacked underneath.  Set `problem_tex` and implement the sections."""

    problem_tex = ""
    problem_label = ""
    card_width = 7.2
    card_font_size = 46
    card_top_buff = 0.5
    steps_top_y = -1.2
    step_buff = 0.42

    def make_card(self) -> ProblemCard:
        card = ProblemCard(
            self.problem_tex,
            width=self.card_width,
            font_size=self.card_font_size,
            label=self.problem_label,
        )
        return self.pin_to_top(card, buff=self.card_top_buff)

    def get_card(self) -> ProblemCard:
        return self.lazy("card", self.make_card)

    def show_problem(self, run_time: float = 1.6):
        card = self.make_card()
        self.play(
            FadeIn(card.rect, scale=0.97),
            run_time=0.6,
        )
        self.play(Write(card.body), run_time=run_time)
        extras = [m for m in (card.logo, card.tag) if m is not None and len(m) > 0]
        if extras:
            self.play(*[FadeIn(m) for m in extras], run_time=0.5)
        self.wait(0.4)
        return self.set_state("card", card)
