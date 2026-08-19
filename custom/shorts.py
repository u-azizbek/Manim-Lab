from __future__ import annotations

import os

from manimlib.constants import BLACK, DOWN, GREY_B, UP, WHITE, YELLOW
from manimlib.animation.fading import FadeIn, FadeOut
from manimlib.animation.transform import TransformFromCopy
from manimlib.animation.transform_matching_parts import TransformMatchingTex
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.mobject import Mobject
from manimlib.scene.interactive_scene import InteractiveScene


class ShortsScene(InteractiveScene):
    """Base class for the 9:16 YouTube Shorts scenes.

    Handles two things a plain InteractiveScene does not:

    Portrait framing.  FRAME_WIDTH is derived from the output resolution, so
    rendering with -r 1080x1920 would otherwise leave a cramped 4.5 unit wide
    frame.  The frame is reshaped in setup.  Note that this makes `to_edge`
    and friends useless, since they position against the global frame
    constants rather than the camera frame -- use `pin_to_top` instead.

    Partial renders.  `construct` runs the methods named in `sections`, in
    order.  Set the SECTIONS environment variable (or pass --sections to
    render.sh) to animate only some of them.  Any state an earlier section
    would have built is filled in silently by `lazy`, so every section can be
    rendered on its own.
    """

    frame_width: float = 8.0
    frame_height: float = 8.0 * 16 / 9
    background_color = BLACK

    # Section methods, in the order construct should run them
    sections: list[str] = []

    def setup(self) -> None:
        super().setup()
        self.camera.background_color = self.background_color
        self.frame.set_shape(self.frame_width, self.frame_height)
        self.lazy_state: dict[str, Mobject] = dict()

    def construct(self) -> None:
        for name in self.get_requested_sections():
            getattr(self, name)()

    def get_requested_sections(self) -> list[str]:
        requested = os.environ.get("SECTIONS", "").strip()
        if not requested:
            return self.sections
        names = [name for name in requested.replace(",", " ").split()]
        unknown = [name for name in names if name not in self.sections]
        if unknown:
            raise ValueError(
                f"Unknown section(s) {unknown} for {type(self).__name__}.\n"
                f"Available sections: {', '.join(self.sections)}"
            )
        # Always play in declaration order, however they were listed
        return sorted(set(names), key=self.sections.index)

    # Carrying state between sections

    def lazy(self, name: str, factory) -> Mobject:
        """State handed from one section to the next.

        When the section that would have animated this into place is not part
        of the render, build it and drop it on screen with no animation.
        """
        if name not in self.lazy_state:
            mobject = factory()
            self.add(mobject)
            self.lazy_state[name] = mobject
        return self.lazy_state[name]

    def set_state(self, name: str, mobject: Mobject) -> Mobject:
        self.lazy_state[name] = mobject
        return mobject

    # Layout

    def pin_to_top(self, mobject: Mobject, buff: float = 0.5) -> Mobject:
        mobject.set_y(self.frame_height / 2 - buff - mobject.get_height() / 2)
        return mobject


class StepListMixin:
    """A running list of solution lines stacked down the lower part of the
    frame.  Call `add_step` once per line; positioning is handled."""

    step_color = WHITE
    result_color = YELLOW
    note_color = GREY_B      # the one-line "which rule is this" callouts
    steps_top_y = -0.7
    step_buff = 0.34
    step_font_size = 36
    step_max_width = 6.9

    def steps(self) -> VGroup:
        if not hasattr(self, "_step_lines"):
            self._step_lines = VGroup()
        return self._step_lines

    def place_step(self, mobject: Mobject) -> Mobject:
        lines = self.steps()
        if len(lines) == 0:
            mobject.set_y(self.steps_top_y - mobject.get_height() / 2)
        else:
            mobject.next_to(lines[-1], DOWN, buff=self.step_buff)
        mobject.set_x(0)
        return mobject

    def add_step(self, tex: str, color=None, font_size: int | None = None,
                 run_time: float = 1.0, wait: float = 0.45, **kwargs) -> Mobject:
        line = Tex(tex, font_size=font_size or self.step_font_size, **kwargs)
        line.set_color(color or self.step_color)
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.steps().add(line)
        self.play(FadeIn(line, 0.15 * DOWN), run_time=run_time)
        if wait:
            self.wait(wait)
        return line

    def transform_step(self, source: Mobject, tex: str, color=None,
                       font_size: int | None = None, run_time: float = 1.4,
                       wait: float = 0.6, **kwargs) -> Mobject:
        """Like `add_step`, but grows the new line out of an earlier one, so
        consecutive lines of algebra read as one continuous move."""
        line = Tex(tex, font_size=font_size or self.step_font_size, **kwargs)
        line.set_color(color or self.step_color)
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.steps().add(line)
        self.play(TransformFromCopy(source, line), run_time=run_time)
        if wait:
            self.wait(wait)
        return line

    def note(self, message: str, font_size: int = 28, run_time: float = 0.6,
             wait: float = 1.6, keep: bool = False) -> Mobject | None:
        """One short sentence naming the rule or theorem being applied.

        Every short should say *why* a step is allowed -- "Leibniz rule",
        "integrate by parts" -- not just show the algebra.  The sentence takes
        the next step slot while it is read and then clears itself, so naming
        the rule costs no permanent room in the frame.  Pass `keep=True` to
        leave it on screen as a normal step.
        """
        line = Text(message, font_size=font_size)
        line.set_color(self.note_color)
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.play(FadeIn(line, 0.15 * DOWN), run_time=run_time)
        if wait:
            self.wait(wait)
        if keep:
            self.steps().add(line)
            return line
        self.play(FadeOut(line, 0.15 * UP), run_time=0.4)
        return None

    def replace_step(self, source: Mobject, tex: str, color=None,
                     font_size: int | None = None, key_map: dict = {},
                     matched_keys=(), run_time: float = 1.3,
                     wait: float = 0.6, **kwargs) -> Mobject:
        """Rewrite a line where it already sits, rather than stacking a new
        one underneath it.

        Long derivations run out of frame fast in 9:16, so working that is
        only a stepping stone should be rewritten in place; only results worth
        keeping should earn their own slot.  Matching parts are carried across
        so the change reads as a move rather than a cut.
        """
        line = Tex(tex, font_size=font_size or self.step_font_size, **kwargs)
        line.set_color(color or self.step_color)
        line.set_max_width(self.step_max_width)
        line.move_to(source)
        self.play(
            TransformMatchingTex(
                source, line,
                key_map=key_map, matched_keys=list(matched_keys),
            ),
            run_time=run_time,
        )
        if wait:
            self.wait(wait)
        # Keep the step list pointing at what is on screen, in the same
        # position, so later steps stack under the replacement
        lines = list(self.steps().submobjects)
        if source in lines:
            lines[lines.index(source)] = line
            self.steps().set_submobjects(lines)
        return line

    def clear_steps(self, run_time: float = 0.6):
        if len(self.steps()) > 0:
            self.play(FadeOut(self.steps(), UP), run_time=run_time)
        self._step_lines = VGroup()
