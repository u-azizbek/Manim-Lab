from __future__ import annotations

import os

from manimlib.constants import BLACK
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
