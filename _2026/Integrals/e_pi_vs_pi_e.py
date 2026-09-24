from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Integrals/e_pi_vs_pi_e.py
#
# Which is bigger, e^pi or pi^e?  On [e, pi] the curve y = 1/x stays below its
# value at the left end, 1/e, so the area under it is less than the rectangle
# of height 1/e:
#   ln(pi) - 1 = int_e^pi dx/x  <  (pi - e)/e = pi/e - 1,
# hence ln(pi) < pi/e, e ln(pi) < pi, ln(pi^e) < pi, and pi^e < e^pi.
# (22.459 < 23.141.)  The gap is only 7% of the rectangle, which is why the
# video zooms in to show it.

E = np.e
PI = np.pi
GRAPH_W = 6.6
GRAPH_H = 4.4
ZOOM = 4.5                  # how far the strip is blown up
ZOOM_SPOT = 0.4 * UP        # where the top of the strip lands while zoomed

CURVE = "#E8D594"
AREA = "#58C4DD"
RECT = YELLOW

AREA_KEY = R"\int_e^\pi \frac{1}{x}\,dx"
RECT_KEY = R"\frac{1}{e}(\pi - e)"


class EPiVsPiE(MockTestShort):
    """e^pi vs pi^e, settled by an area under 1/x and a rectangle."""

    test = ""
    card_top_buff = 0.85
    card_font_size = 52
    step_buff = 0.5

    # Two lines, so the exponents are not squeezed to fit one long one
    problem_tex = R"\text{Which is bigger?}\\ e^{\pi} \quad \text{or} \quad \pi^{e}"

    sections = [
        "pose",
        "draw_graph",
        "compare_areas",
        "zoom_in",
        "inequality",
        "finish",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        # Hang the graph off the card's real height, and the steps off the
        # graph, rather than pinning either per video
        self.graph_top = card.get_bottom()[1] - 0.45
        self.steps_top_y = self.graph_top - GRAPH_H - 0.95
        return card

    # Pieces

    def make_graph(self):
        axes = Axes(
            (0, 4.2, 1), (0, 1.25, 0.25),
            width=GRAPH_W, height=GRAPH_H,
            axis_config=dict(stroke_color=GREY_B, stroke_width=2, include_tip=False),
        )
        self.get_card()
        axes.move_to(0.15 * RIGHT + (self.graph_top - GRAPH_H / 2) * UP)
        curve = axes.get_graph(lambda x: 1 / x, x_range=(0.8, 4.2)).set_stroke(CURVE, 4)
        label = Tex(R"y = \frac{1}{x}", font_size=40).set_color(CURVE)
        label.move_to(axes.c2p(1.6, 1.05))
        marks = VGroup(*[
            VGroup(
                Line(axes.c2p(v, 0), axes.c2p(v, 1 / v)).set_stroke(WHITE, 2.5),
                Tex(tex, font_size=36).next_to(axes.c2p(v, 0), DOWN, buff=0.15),
            )
            for v, tex in [(E, "e"), (PI, R"\pi")]
        ])
        graph = VGroup(axes, curve, label, marks)
        graph.axes, graph.curve, graph.label, graph.marks = axes, curve, label, marks
        return graph

    def get_graph(self):
        return self.lazy("graph", self.make_graph)

    def make_shapes(self):
        """The area under the curve on [e, pi], and the rectangle of height 1/e
        over the same stretch -- which is that area plus a thin sliver."""
        axes = self.get_graph().axes
        top = [axes.c2p(x, 1 / x) for x in np.linspace(E, PI, 60)]
        area = Polygon(*top, axes.c2p(PI, 0), axes.c2p(E, 0))
        area.set_fill(AREA, 0.55).set_stroke(width=0)
        sliver = Polygon(axes.c2p(PI, 1 / E), *top[::-1])
        sliver.set_fill(RECT, 0.55).set_stroke(width=0)
        rect = Polygon(
            axes.c2p(E, 0), axes.c2p(PI, 0), axes.c2p(PI, 1 / E), axes.c2p(E, 1 / E),
        ).set_stroke(RECT, 3).set_fill(opacity=0)
        guide = DashedLine(axes.c2p(0, 1 / E), axes.c2p(E, 1 / E), dash_length=0.08)
        guide.set_stroke(RECT, 2)
        guide_label = Tex(R"\frac{1}{e}", font_size=32).set_color(RECT)
        guide_label.next_to(axes.c2p(0, 1 / E), LEFT, buff=0.15)

        shapes = VGroup(area, sliver, rect, guide, guide_label)
        shapes.area, shapes.sliver, shapes.rect = area, sliver, rect
        shapes.guide = VGroup(guide, guide_label)
        return shapes

    def get_shapes(self):
        return self.lazy("shapes", self.make_shapes)

    def rest_of(self, line, *parts):
        """Every glyph of `line` not in one of `parts`."""
        covered = set()
        for part in parts:
            covered.update(part.family_members_with_points())
        return VGroup(*[g for g in line.family_members_with_points() if g not in covered])

    # Sections

    def draw_graph(self):
        self.get_card()
        graph = self.make_graph()
        self.play(ShowCreation(graph.axes), run_time=0.9)
        self.play(ShowCreation(graph.curve), FadeIn(graph.label), run_time=1.2)
        self.play(
            LaggedStart(*[
                AnimationGroup(ShowCreation(line), FadeIn(tex, 0.2 * DOWN))
                for line, tex in graph.marks
            ], lag_ratio=0.4),
            run_time=0.9,
        )
        self.set_state("graph", graph)
        self.wait(0.3)

    def compare_areas(self):
        self.get_graph()
        shapes = self.make_shapes()

        # Fills go underneath the curve and the lines at e and pi
        self.add(shapes.area)
        self.bring_to_back(shapes.area)
        self.play(FadeIn(shapes.area), run_time=0.8)
        self.play(ShowCreation(shapes.guide[0]), FadeIn(shapes.guide[1]), run_time=0.7)
        self.play(ShowCreation(shapes.rect), run_time=0.8)
        self.add(shapes.sliver)
        self.bring_to_back(shapes.sliver)
        self.play(FadeIn(shapes.sliver), run_time=0.6)
        self.set_state("shapes", shapes)
        self.wait(0.4)

    def zoom_in(self):
        card = self.get_card()
        graph = self.get_graph()
        shapes = self.get_shapes()

        # Blow the picture up about the top of the strip, rather than moving
        # the camera: the card stays exactly where it is, and stroke widths do
        # not scale, so the magnified lines stay crisp.  Regroup first so each
        # piece is drawn once, with the fills beneath the curve.
        picture = VGroup(shapes.area, shapes.sliver, graph, shapes.rect, shapes.guide)
        self.remove(graph, shapes)
        self.add(picture, card)
        picture.save_state()
        target = graph.axes.c2p((E + PI) / 2, 1 / E - 0.03)
        self.play(
            picture.animate.scale(ZOOM, about_point=target).shift(ZOOM_SPOT - target),
            run_time=1.8,
        )

        caption = Text(
            "The curve drops below the rectangle's top,\n"
            "so the area is less than the rectangle.",
            font_size=30,
        )
        backing = BackgroundRectangle(caption, fill_opacity=0.85, buff=0.18)
        note = VGroup(backing, caption).move_to(2.6 * DOWN)
        self.play(
            FadeIn(note),
            shapes.sliver.animate.set_fill(opacity=0.95),
            run_time=0.8,
        )
        self.wait(1.6)
        self.play(FadeOut(note), Restore(picture), run_time=1.6)
        self.set_state("picture", picture)

    def inequality(self):
        self.get_graph()
        shapes = self.get_shapes()

        # Area < rectangle, each side in the colour of what it measures
        ineq = Tex(
            AREA_KEY + " < " + RECT_KEY,
            font_size=42, isolate=[AREA_KEY, RECT_KEY],
        )
        area_part, rect_part = ineq[AREA_KEY][0], ineq[RECT_KEY][0]
        area_part.set_color(AREA)
        rect_part.set_color(RECT)
        ineq.set_max_width(self.step_max_width)
        self.place_step(ineq)
        self.steps().add(ineq)

        self.play(
            FadeIn(area_part, 0.15 * DOWN),
            shapes.area.animate.set_fill(opacity=0.9),
            run_time=0.8,
        )
        self.play(
            FadeIn(self.rest_of(ineq, area_part, rect_part)),
            shapes.area.animate.set_fill(opacity=0.55),
            run_time=0.4,
        )
        self.play(
            FadeIn(rect_part, 0.15 * DOWN),
            shapes.rect.animate.set_stroke(width=7),
            shapes.sliver.animate.set_fill(opacity=0.9),
            run_time=0.8,
        )
        self.play(
            shapes.rect.animate.set_stroke(width=3),
            shapes.sliver.animate.set_fill(opacity=0.55),
            run_time=0.4,
        )

        self.note("The area under 1/x is a log:  ln π − ln e = ln π − 1", wait=1.3)
        ln_line = self.replace_step(
            ineq, R"\ln\pi - 1 < \frac{\pi}{e} - 1",
            font_size=42,
            key_map={AREA_KEY: R"\ln\pi - 1", RECT_KEY: R"\frac{\pi}{e} - 1"},
            colors={R"\ln\pi - 1": AREA, R"\frac{\pi}{e} - 1": RECT},
            wait=0.8,
        )
        chain = self.transform_step(ln_line, R"\ln\pi < \frac{\pi}{e}", font_size=44, wait=0.6)
        self.set_state("chain", chain)

    def finish(self):
        self.get_graph()
        self.get_shapes()
        chain = self.lazy_state.get("chain")
        if chain is None:
            chain = Tex(R"\ln\pi < \frac{\pi}{e}", font_size=44)
            self.place_step(chain)
            self.steps().add(chain)
            self.add(chain)

        chain = self.replace_step(chain, R"e\ln\pi < \pi", font_size=44, wait=0.5)
        chain = self.replace_step(chain, R"\ln(\pi^e) < \pi", font_size=44, wait=0.5)
        self.note("Exponentiate both sides (exp is increasing).", wait=1.0)
        chain = self.replace_step(
            chain, R"\pi^e < e^{\pi}",
            font_size=60, color=RESULT_COLOR, wait=0.3,
        )
        box = SurroundingRectangle(chain, color=RESULT_COLOR, buff=0.22).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(chain, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.add_step(
            R"22.459\ldots < 23.141\ldots",
            color=GREY_B, font_size=32, wait=1.6,
        )
