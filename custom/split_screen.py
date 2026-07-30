from __future__ import annotations

from manimlib import *

from custom.shorts import ShortsScene


class LabeledPanel(VGroup):
    """A rounded, colour-bordered box with a bold label sitting above it.

    `inner_width` / `inner_height` give the usable area once the padding is
    removed, so content can be scaled to fit without touching the border.
    """

    def __init__(
        self,
        label: str,
        color: ManimColor,
        width: float = 7.0,
        height: float = 4.1,
        corner_radius: float = 0.22,
        pad: float = 0.4,
        label_font_size: int = 48,
        tint: float = 0.06,
    ):
        super().__init__()
        self.panel_color = color
        self.pad = pad

        self.rect = RoundedRectangle(width=width, height=height, corner_radius=corner_radius)
        self.rect.set_stroke(color, width=4)
        self.rect.set_fill(color, tint)

        self.label = Text(label, font_size=label_font_size, weight=BOLD)
        self.label.set_color(color)
        self.label.next_to(self.rect, UP, buff=0.25)

        self.add(self.rect, self.label)

    @property
    def inner_width(self) -> float:
        return self.rect.get_width() - 2 * self.pad

    @property
    def inner_height(self) -> float:
        return self.rect.get_height() - 2 * self.pad

    def dim(self, opacity: float = 0.4):
        self.rect.set_stroke(opacity=opacity)
        self.label.set_opacity(opacity)
        return self


class SplitScreenScene(ShortsScene):
    """Reusable "Beginner vs Pro" split-screen short.

    Subclass it, set the two labels/colours if you like, and implement three
    methods: `get_problem_tex`, `beginner_lines`, `pro_lines`.  Each *_lines
    returns a list of mobjects (usually Tex); the base class boxes them, drops
    them into the right panel and writes them one at a time.  The top panel is
    filled first, then the bottom one, then both answers are highlighted.

    Render the whole thing, or one beat:
        ./render.sh -s solve_pro <file.py>
    """

    # Override these per video
    beginner_label = "BEGINNER"
    pro_label = "PRO"
    beginner_color = "#FF5C39"
    pro_color = "#39D353"
    credit = ""  # e.g. "@your_handle"; empty hides the credit line
    verdict = ""  # optional closing line shown under the pro panel

    # Shared styling
    problem_color = WHITE
    result_color = YELLOW
    problem_max_width = 6.9
    panel_width = 7.0
    panel_height = 4.1
    line_buff = 0.42

    sections = ["arena", "solve_beginner", "solve_pro", "conclude"]

    # ---- to override ----

    def get_problem_tex(self) -> str:
        raise NotImplementedError

    def beginner_lines(self) -> list[Mobject]:
        raise NotImplementedError

    def pro_lines(self) -> list[Mobject]:
        raise NotImplementedError

    # ---- layout ----

    def make_layout(self):
        problem = Tex(self.get_problem_tex(), font_size=46)
        problem.set_color(self.problem_color)
        problem.set_max_width(self.problem_max_width)

        beginner = LabeledPanel(
            self.beginner_label, self.beginner_color,
            self.panel_width, self.panel_height,
        )
        pro = LabeledPanel(
            self.pro_label, self.pro_color,
            self.panel_width, self.panel_height,
        )

        column = VGroup(problem, beginner, pro)
        column.arrange(DOWN, buff=0.5)
        self.pin_to_top(column, buff=0.55)

        column.problem = problem
        column.beginner = beginner
        column.pro = pro
        return column

    def get_layout(self):
        return self.lazy("layout", self.make_layout)

    def layout_lines(self, lines: VGroup, panel: LabeledPanel, align=LEFT) -> VGroup:
        lines.arrange(DOWN, buff=self.line_buff, aligned_edge=align)
        if lines.get_width() > panel.inner_width:
            lines.set_width(panel.inner_width)
        if lines.get_height() > panel.inner_height:
            lines.set_height(panel.inner_height)
        lines.move_to(panel.rect)
        return lines

    def make_credit(self):
        credit = Text(self.credit, font_size=26).set_color(GREY_B)
        credit.set_y(-self.frame_height / 2 + 0.55)
        return credit

    # ---- sections ----

    def arena(self):
        # A short beat of the bare problem, then the two empty arenas
        layout = self.make_layout()

        self.play(Write(layout.problem), run_time=1.2)
        self.wait(0.3)
        self.play(
            ShowCreation(layout.beginner.rect),
            FadeIn(layout.beginner.label, 0.2 * DOWN),
            run_time=0.9,
        )
        self.play(
            ShowCreation(layout.pro.rect),
            FadeIn(layout.pro.label, 0.2 * DOWN),
            run_time=0.9,
        )
        if self.credit:
            self.add(self.make_credit())
        self.wait(0.4)
        self.set_state("layout", layout)

    def fill_panel(self, panel: LabeledPanel, lines_factory, key: str, line_time=1.1):
        lines = VGroup(*lines_factory())
        self.layout_lines(lines, panel)

        self.play(FlashAround(panel.rect, color=panel.panel_color, time_width=1.5), run_time=1.0)
        for line in lines:
            self.play(Write(line), run_time=line_time)
            self.wait(0.45)
        self.wait(0.7)
        self.set_state(key, lines)
        return lines

    def make_beginner_content(self):
        lines = VGroup(*self.beginner_lines())
        return self.layout_lines(lines, self.get_layout().beginner)

    def get_beginner_content(self):
        return self.lazy("beginner_content", self.make_beginner_content)

    def make_pro_content(self):
        lines = VGroup(*self.pro_lines())
        return self.layout_lines(lines, self.get_layout().pro)

    def get_pro_content(self):
        return self.lazy("pro_content", self.make_pro_content)

    def solve_beginner(self):
        self.fill_panel(self.get_layout().beginner, self.beginner_lines, "beginner_content")

    def solve_pro(self):
        self.fill_panel(self.get_layout().pro, self.pro_lines, "pro_content")

    def conclude(self):
        beginner = self.get_beginner_content()
        pro = self.get_pro_content()

        self.play(
            FlashAround(beginner[-1], color=self.result_color, time_width=1.5),
            FlashAround(pro[-1], color=self.result_color, time_width=1.5),
            run_time=1.6,
        )
        self.wait(0.5)

        if self.verdict:
            banner = Text(self.verdict, font_size=34, weight=BOLD)
            banner.set_color(self.result_color)
            banner.set_max_width(6.8)
            banner.next_to(self.get_layout().pro, DOWN, buff=0.4)
            self.play(FadeIn(banner, 0.2 * UP), run_time=0.9)
            self.play(FlashAround(banner, color=self.result_color, time_width=1.5), run_time=1.3)
        self.wait(1.6)
