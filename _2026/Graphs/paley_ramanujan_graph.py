from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Graphs/paley_ramanujan_graph.py
#
# The Paley graph of order 29: vertices 0..28, with i ~ j when j - i is a
# nonzero square mod 29.  Since 29 = 1 (mod 4), -1 is a square, so the rule is
# symmetric.  There are 14 squares, so the graph is 14-regular with
# 29 * 14 / 2 = 203 edges.  (The reference image calls it 7-regular; it is 14.)
#
# Its adjacency eigenvalues are 14 once and (-1 +- sqrt 29)/2 = 2.19, -3.19,
# 14 times each (checked with numpy).  A k-regular graph is Ramanujan when
# every eigenvalue other than +-k has |lambda| <= 2 sqrt(k - 1) = 2 sqrt 13
# = 7.21, and 3.19 is well inside that.
#
# Both drawings reuse the node positions of the reference image (pixel
# coordinates read off it), in its colours.

P = 29
SQUARES = sorted({k * k % P for k in range(1, P)})
EDGES = [(i, j) for i in range(P) for j in range(i + 1, P) if (j - i) % P in SQUARES]

GREEN_LAYOUT = {
    2: (365, 147), 8: (294, 165), 10: (230, 202), 14: (177, 255), 17: (140, 318),
    21: (121, 388), 26: (122, 462), 3: (140, 534), 11: (178, 598), 27: (230, 650),
    12: (293, 687), 18: (364, 706), 15: (438, 706), 19: (510, 687), 7: (487, 538),
    9: (514, 512), 13: (531, 480), 16: (541, 443), 20: (542, 408), 22: (531, 373),
    23: (514, 341), 24: (487, 314), 25: (456, 295), 28: (421, 286), 1: (290, 340),
    0: (402, 426), 4: (290, 512), 5: (365, 562), 6: (438, 562),
}
BLUE_LAYOUT = {
    8: (724, 168), 16: (832, 158), 9: (934, 155), 21: (1074, 204), 0: (994, 223),
    17: (792, 243), 22: (886, 281), 13: (1147, 311), 15: (623, 316), 28: (717, 306),
    12: (989, 325), 1: (798, 352), 5: (1148, 407), 4: (1021, 407), 14: (921, 413),
    10: (683, 415), 23: (585, 443), 6: (820, 456), 25: (1070, 483), 3: (732, 502),
    7: (883, 514), 24: (655, 546), 20: (1121, 549), 18: (958, 584), 26: (1043, 602),
    2: (716, 614), 11: (849, 620), 19: (801, 684), 27: (957, 692),
}

GREEN_EDGE = "#6B9B3A"
GREEN_NODE = "#B8702F"
BLUE_EDGE = "#6A8CC7"
BLUE_NODE = "#7F9CCB"
HIGHLIGHT = YELLOW
BAND = "#5BD98A"


def place(layout, height, center):
    """Pixel positions from the reference image, scaled to `height` and centred."""
    pts = np.array([layout[v] for v in range(P)], dtype=float)
    pts[:, 1] *= -1
    pts -= (pts.max(0) + pts.min(0)) / 2
    pts *= height / (pts[:, 1].max() - pts[:, 1].min())
    return {v: center + np.array([*pts[v], 0]) for v in range(P)}


class Graph29(VGroup):
    def __init__(self, positions, edge_color, node_color, node_radius=0.075, font_size=20):
        super().__init__()
        middle = np.mean(list(positions.values()), axis=0)
        self.edges = {
            (i, j): Line(positions[i], positions[j]).set_stroke(edge_color, 1.3, 0.8)
            for i, j in EDGES
        }
        self.nodes = VGroup(*[
            Dot(positions[v], radius=node_radius).set_fill(node_color).set_stroke(BLACK, 1)
            for v in range(P)
        ])
        self.labels = VGroup(*[
            Text(str(v), font_size=font_size).set_color(GREY_A).move_to(
                positions[v] + 0.2 * normalize(positions[v] - middle + 1e-6 * UP))
            for v in range(P)
        ])
        self.edge_group = VGroup(*self.edges.values())
        self.add(self.edge_group, self.nodes, self.labels)

    def edges_at(self, v):
        return VGroup(*[line for (i, j), line in self.edges.items() if v in (i, j)])


class PaleyRamanujanGraph(MockTestShort):
    """The Paley graph P(29), built from quadratic residues, and why it is Ramanujan."""

    test = ""
    card_top_buff = 0.6
    step_buff = 0.36

    problem_tex = (
        R"\text{A Ramanujan graph: the Paley}\\"
        R"\text{graph on 29 vertices}"
    )

    sections = [
        "pose",
        "squares",
        "green_graph",
        "blue_graph",
        "spectrum",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = -3.05
        return card

    # Sections

    def squares(self):
        self.get_card()

        # The nonzero squares mod 29
        ks = list(range(1, 15))
        table = VGroup(
            VGroup(*[Tex(str(k), font_size=30) for k in ks]),
            VGroup(*[Tex(str(k * k % P), font_size=30).set_color(HIGHLIGHT) for k in ks]),
        )
        for row in table:
            row.arrange(RIGHT, buff=0.22)
        for a, b in zip(*table):
            b.set_x(a.get_x())
        table.arrange(DOWN, buff=0.22)
        heads = VGroup(Tex("k", font_size=30), Tex(R"k^2", font_size=30).set_color(HIGHLIGHT))
        for head, row in zip(heads, table):
            head.next_to(row, LEFT, buff=0.3)
        block = VGroup(heads, table).move_to(3.55 * UP)
        self.play(FadeIn(heads), LaggedStart(*[FadeIn(m, 0.1 * DOWN) for m in table[0]], lag_ratio=0.05), run_time=0.8)
        self.play(LaggedStart(*[TransformFromCopy(a, b) for a, b in zip(*table)], lag_ratio=0.06), run_time=1.3)
        self.note("Squares mod 29: 14 of them.\nJoin i and j when j − i is a square.", wait=1.4)

        # Collapse into the rule
        rule = Tex(
            R"S = \{" + ",".join(map(str, SQUARES)) + R"\}",
            font_size=28,
        ).set_color(HIGHLIGHT).move_to(3.85 * UP)
        link = Tex(R"i \sim j \iff j - i \in S \pmod{29}", font_size=30).next_to(rule, DOWN, buff=0.14)
        self.play(
            ReplacementTransform(table[1], rule),
            FadeOut(VGroup(heads, table[0])),
            run_time=1.0,
        )
        self.play(FadeIn(link, 0.15 * DOWN), run_time=0.5)
        self.set_state("rule", VGroup(rule, link))

    def green_graph(self):
        self.lazy("rule", VGroup)
        positions = place(GREEN_LAYOUT, 5.6, 0.2 * UP)
        graph = Graph29(positions, GREEN_EDGE, GREEN_NODE, node_radius=0.08, font_size=22)
        self.play(
            LaggedStart(*[FadeIn(n, scale=0.5) for n in graph.nodes], lag_ratio=0.03),
            FadeIn(graph.labels, lag_ratio=0.03),
            run_time=1.2,
        )

        # Vertex 0 first: its 14 neighbours are exactly the squares
        star = graph.edges_at(0)
        self.play(
            graph.nodes[0].animate.set_fill(HIGHLIGHT).scale(1.4),
            LaggedStart(*[ShowCreation(line) for line in star], lag_ratio=0.08),
            run_time=1.5,
        )
        neighbours = VGroup(*[graph.nodes[s] for s in SQUARES])
        self.play(Indicate(neighbours, color=HIGHLIGHT, scale_factor=1.6), run_time=0.8)
        degree = self.add_step(R"\deg(0) = |S| = 14", color=HIGHLIGHT, wait=0.4)

        # Then everyone else, all at once
        rest = [line for line in graph.edge_group if line not in star]
        self.play(
            graph.nodes[0].animate.set_fill(GREEN_NODE).scale(1 / 1.4),
            LaggedStart(*[ShowCreation(line) for line in rest], lag_ratio=0.004),
            run_time=2.6,
        )
        self.add(graph)
        self.replace_step(
            degree, R"\text{14-regular},\quad 29 \cdot 14 / 2 = 203 \text{ edges}",
            color=HIGHLIGHT, wait=0.8,
        )
        self.set_state("green", graph)

    def blue_graph(self):
        green = self.lazy("green", lambda: Graph29(
            place(GREEN_LAYOUT, 5.6, 0.2 * UP), GREEN_EDGE, GREEN_NODE, node_radius=0.08, font_size=22))
        self.clear_steps()

        # Make room: the first drawing moves left, as in the reference
        self.play(green.animate.scale(0.62).move_to(1.75 * LEFT + 0.95 * UP), run_time=1.0)

        # The same graph, drawn again from scratch on the right
        positions = place(BLUE_LAYOUT, 3.25, 1.85 * RIGHT + 0.95 * UP)
        blue = Graph29(positions, BLUE_EDGE, BLUE_NODE, node_radius=0.055, font_size=14)
        self.play(
            LaggedStart(*[FadeIn(n, scale=0.5) for n in blue.nodes], lag_ratio=0.03),
            FadeIn(blue.labels, lag_ratio=0.03),
            run_time=1.0,
        )
        self.play(
            LaggedStart(*[
                LaggedStart(*[ShowCreation(blue.edges[(i, j)]) for i, j in EDGES if i == v], lag_ratio=0.02)
                for v in range(P - 1)
            ], lag_ratio=0.1),
            run_time=3.0,
        )
        self.add(blue)

        # Same vertices, same rule: pick one vertex and compare
        pair = VGroup(green.nodes[14], blue.nodes[14])
        self.play(
            *[m.animate.set_fill(HIGHLIGHT).scale(1.6) for m in pair],
            green.edges_at(14).animate.set_stroke(HIGHLIGHT, 2, 1),
            blue.edges_at(14).animate.set_stroke(HIGHLIGHT, 2, 1),
            run_time=0.9,
        )
        self.note("Same rule, two drawings: vertex 14 has\nthe same 14 neighbours in both.", wait=1.4)
        self.play(
            *[m.animate.scale(1 / 1.6) for m in pair],
            green.nodes[14].animate.set_fill(GREEN_NODE),
            blue.nodes[14].animate.set_fill(BLUE_NODE),
            green.edges_at(14).animate.set_stroke(GREEN_EDGE, 1.3, 0.8),
            blue.edges_at(14).animate.set_stroke(BLUE_EDGE, 1.3, 0.8),
            run_time=0.6,
        )
        self.set_state("blue", blue)

    def spectrum(self):
        # Eigenvalues of the adjacency matrix, on a number line
        self.clear_steps()
        self.steps_top_y = -3.75
        line = NumberLine((-8, 15, 1), width=7.2, include_tip=False, tick_size=0.05)
        line.set_stroke(GREY_B, 1.5).move_to(3.1 * DOWN)
        marks = VGroup(*[
            Tex(str(v), font_size=22).set_color(GREY_B).next_to(line.n2p(v), DOWN, buff=0.1)
            for v in (-7, 0, 7, 14)
        ])
        bound = 2 * np.sqrt(13)
        band = Rectangle(
            width=line.n2p(bound)[0] - line.n2p(-bound)[0], height=1.55,
        ).set_stroke(BAND, 2).set_fill(BAND, 0.15)
        band.move_to(line.n2p(0), aligned_edge=DOWN)
        band_label = Tex(R"|\lambda| \le 2\sqrt{k-1} = 2\sqrt{13} \approx 7.21", font_size=26).set_color(BAND)
        band_label.next_to(band, UP, buff=0.1)

        self.play(ShowCreation(line), FadeIn(marks), run_time=0.7)
        self.note("Ramanujan: every eigenvalue except k = 14\nlies within 2√(k − 1).", wait=1.3)
        self.play(FadeIn(band), FadeIn(band_label, 0.1 * UP), run_time=0.8)

        # Bars: height is multiplicity
        eigen = [(14, 1), ((-1 + np.sqrt(29)) / 2, 14), ((-1 - np.sqrt(29)) / 2, 14)]
        bars = VGroup(*[
            Rectangle(width=0.14, height=1.1 * m / 14).set_stroke(width=0).set_fill(
                HIGHLIGHT if m == 1 else BLUE_EDGE, 1).move_to(line.n2p(v), aligned_edge=DOWN)
            for v, m in eigen
        ])
        bars[0].set_height(0.25, stretch=True).move_to(line.n2p(14), aligned_edge=DOWN)
        names = VGroup(
            Tex(R"k = 14", font_size=24).set_color(HIGHLIGHT).next_to(bars[0], UP, buff=0.08),
            Tex(R"2.19\ (\times 14)", font_size=24).set_color(BLUE_EDGE).next_to(bars[1], UP, buff=0.08),
            Tex(R"-3.19\ (\times 14)", font_size=24).set_color(BLUE_EDGE).next_to(bars[2], UP, buff=0.08),
        )
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.3), FadeIn(names, lag_ratio=0.3), run_time=1.3)
        self.wait(0.6)
        self.conclude(R"|\lambda| \le 3.19 < 7.21 \ \checkmark", font_size=44, wait=1.6)
