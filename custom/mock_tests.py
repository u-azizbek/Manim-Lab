from __future__ import annotations

from manimlib import *

from custom.cards import CardSolutionScene
from custom.outro import BrandOutroMixin


# Shared palette for the mock-test series, so every video reads the same way
SETUP_COLOR = "#7FB3FF"    # restating the problem, naming things
RULE_COLOR = "#5BD98A"     # the key identity or trick
RESULT_COLOR = YELLOW      # the answer


class MockTestShort(BrandOutroMixin, CardSolutionScene):
    """One worked mock-test question as a 9:16 Short.

    The problem card is pinned to the top with a `test:question` tag in its
    corner, so a viewer can find the question in the book.  Subclasses set
    where the question came from and what it says:

        class F1Q21(MockTestShort):
            test = "F1"          # Foundation Mock Test 1
            question = 21
            problem_tex = R"..."
            sections = ["name_the_unknown", "invert", "finish"]

    Re-pointing a video at another part of the book -- Advanced Mock Test 2,
    Elite Mock Test 3 -- is then just `test = "A2"` or `test = "E3"`; nothing
    else in the file mentions the section.  Change `label_format` to restyle
    the tag across the whole series at once.

    List `outro` last in `sections`; it is appended automatically if it is
    missing, so every video in the series ends on the channel badge either
    way.  Spell it out anyway -- `render.sh -l` reads the list out of the
    source rather than importing it, so an implicit section is invisible
    there.
    """

    test = ""
    question = 0
    label_format = "{test}:{question}"

    card_font_size = 40
    card_width = 7.3
    step_buff = 0.50         # raise per file when a question needs fewer, larger steps
    step_font_size = 36
    steps_gap = 0.55          # between the bottom of the card and the first step

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        sections = cls.__dict__.get("sections")
        if sections and "outro" not in sections:
            cls.sections = [*sections, "outro"]

    def make_card(self):
        """Hang the step list off the bottom of the card, whatever its height.

        Questions differ a lot in how many lines they take, so pinning
        `steps_top_y` per file would mean re-tuning it for every video.
        """
        card = super().make_card()
        self.steps_top_y = card.get_bottom()[1] - self.steps_gap
        return card

    @property
    def problem_label(self) -> str:
        if not self.test:
            return ""
        return self.label_format.format(test=self.test, question=self.question)

    # Sections

    def pose(self):
        """Standard opening: the card writes itself in."""
        self.show_problem()
        self.wait(0.7)

    def conclude(self, tex: str, font_size: int = 52, wait: float = 1.5):
        """Standard closing: the answer, boxed and flashed."""
        answer = self.add_step(tex, color=RESULT_COLOR, font_size=font_size, wait=0.2)
        box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.22)
        box.set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(answer, color=RESULT_COLOR, time_width=1.5), run_time=1.4)
        self.wait(wait)
        return answer
