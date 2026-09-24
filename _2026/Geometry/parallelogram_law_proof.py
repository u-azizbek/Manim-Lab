from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/parallelogram_law_proof.py
#
# Visual proof of the parallelogram law, c^2 + d^2 = 2a^2 + 2b^2.  Take the
# triangle cut off by each diagonal -- (a, b, d) and (a, b, c).  Scale the
# first by b, d, a and the second by b, c, a: the six copies glue along
# matching sides into two trapezoids, which join along ab into one big
# parallelogram.  Its top edge is d^2 + c^2 and its bottom b^2 + a^2 + b^2 + a^2,
# and opposite sides of a parallelogram are equal.
#
# Checked numerically: every copy has side ratios exactly b, d, a / b, c, a,
# the two blocks share the edge they join along, and top = bottom.  Three of
# the six copies are mirror images of their source (x d on the left, x b and
# x a on the right), so those flip over before they turn into place.

A_LEN, B_LEN = 1.2, 0.9
ANGLE = 60 * DEGREES        # the parallelogram's acute angle
C_LEN = np.sqrt(A_LEN ** 2 + B_LEN ** 2 - 2 * A_LEN * B_LEN * np.cos(ANGLE))
D_LEN = np.sqrt(A_LEN ** 2 + B_LEN ** 2 + 2 * A_LEN * B_LEN * np.cos(ANGLE))

SCALE = 1.34                # screen units per unit of length, while building
INTRO_SCALE = 2.6
INTRO_CENTER = 1.6 * UP
SOURCE_Y = 3.1              # the two source triangles wait up here
FINAL_Y = -0.4              # the big parallelogram is built here
GAP = 0.2                   # each block starts this far from the join
STAGE_Y = 1.15              # a copy is scaled here, in the open, before it moves in
STAGE_X = {"d": -1.3, "c": 1.6}

FACTORS = {"a": A_LEN, "b": B_LEN, "c": C_LEN, "d": D_LEN}

TRI_D = ["#7FC8FF", "#3D8BFF", "#A8DDFF"]      # copies of (a, b, d)
TRI_C = ["#FFC285", "#FF8C42", "#FFDCAE"]      # copies of (a, b, c)
FILL = 0.4


def pt(x, y):
    return np.array([x, y, 0.0])


def unit(angle):
    return pt(np.cos(angle), np.sin(angle))


# The parallelogram: P0 bottom-left, P1 bottom-right, then round
P0, P1 = pt(0, 0), pt(A_LEN, 0)
P3 = B_LEN * unit(ANGLE)
P2 = P1 + P3

# The big parallelogram's corners, bottom row X and top row Y
AB = A_LEN * B_LEN
X0 = pt(0, 0)
X1 = X0 + B_LEN ** 2 * RIGHT
X2 = X1 + A_LEN ** 2 * RIGHT
X3 = X2 + B_LEN ** 2 * RIGHT
X4 = X3 + A_LEN ** 2 * RIGHT
Y0 = AB * unit(PI - ANGLE)
Y1 = Y0 + D_LEN ** 2 * RIGHT
Y2 = Y1 + C_LEN ** 2 * RIGHT

SRC = {"P0": P0, "P1": P1, "P2": P2, "P3": P3}
SLOT = {"X0": X0, "X1": X1, "X2": X2, "X3": X3, "X4": X4, "Y0": Y0, "Y1": Y1, "Y2": Y2}
SIDE_NAME = {
    frozenset(("P0", "P1")): "a",
    frozenset(("P1", "P2")): "b", frozenset(("P0", "P2")): "d",      # triangle (a, b, d)
    frozenset(("P0", "P3")): "b", frozenset(("P1", "P3")): "c",      # triangle (a, b, c)
}

# (factor, the source triangle's corners, where each of them lands)
LEFT_PIECES = [
    ("b", ("P1", "P2", "P0"), ("X0", "X1", "Y0")),
    ("d", ("P2", "P1", "P0"), ("Y0", "X1", "Y1")),
    ("a", ("P0", "P1", "P2"), ("X1", "X2", "Y1")),
]
RIGHT_PIECES = [
    ("b", ("P0", "P3", "P1"), ("X2", "X3", "Y1")),
    ("c", ("P0", "P3", "P1"), ("X3", "Y1", "Y2")),
    ("a", ("P0", "P1", "P3"), ("X4", "X3", "Y2")),
]


def scaled_side(factor, side):
    """The length of `side` after scaling by `factor`: b*d -> bd, b*b -> b^2."""
    return f"{factor}^2" if factor == side else "".join(sorted((factor, side)))


def orientation(p, q, r):
    return np.sign((q - p)[0] * (r - p)[1] - (q - p)[1] * (r - p)[0])


class ParallelogramLawProof(MockTestShort):
    """c^2 + d^2 = 2a^2 + 2b^2, by gluing scaled copies of two triangles."""

    test = ""
    card_top_buff = 0.85
    card_font_size = 44
    step_buff = 0.4

    problem_tex = R"\text{Parallelogram law}\\ c^2 + d^2 = 2a^2 + 2b^2"

    sections = [
        "pose",
        "draw_parallelogram",
        "split",
        "left_block",
        "right_block",
        "join",
        "conclude",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = -2.65
        return card

    # Placement

    def intro(self, p):
        center = (P0 + P1 + P2 + P3) / 4
        return INTRO_CENTER + INTRO_SCALE * (p - center)

    def source(self, p, which):
        """The source triangles, side by side under the card."""
        tri = (P0, P1, P2) if which == "d" else (P0, P1, P3)
        x = -1.9 if which == "d" else 1.9
        return x * RIGHT + SOURCE_Y * UP + SCALE * (p - np.mean(tri, axis=0))

    def final(self, p, side):
        """The big parallelogram, centred, with its block pulled GAP from the join."""
        center = pt((Y0[0] + X4[0]) / 2, Y0[1] / 2)
        shift = GAP * (LEFT if side == "left" else RIGHT)
        return FINAL_Y * UP + SCALE * (p - center) + shift

    def edge_label(self, tex, p, q, offset, font_size=26, color=WHITE, backing=False):
        normal = rotate_vector(normalize(q - p), PI / 2)
        label = Tex(tex, font_size=font_size).set_color(color)
        label.move_to(midpoint(p, q) + offset * normal)
        if backing:
            return VGroup(BackgroundRectangle(label, fill_opacity=0.75, buff=0.05), label)
        return label

    # Pieces carried between sections

    def make_sources(self):
        groups = VGroup()
        for which, tri, colors, third in [
            ("d", (P0, P1, P2), TRI_D, "d"),
            ("c", (P0, P1, P3), TRI_C, "c"),
        ]:
            pts = [self.source(p, which) for p in tri]
            shape = Polygon(*pts).set_fill(colors[1], FILL).set_stroke(colors[1], 3)
            # label each side with its length, outside the triangle
            names = ("a", "b", third) if which == "d" else ("a", third, "b")
            labels = VGroup(*[
                self.edge_label(n, pts[i], pts[(i + 1) % 3], -0.22, font_size=30, color=colors[1])
                for i, n in enumerate(names)
            ])
            group = VGroup(shape, labels)
            group.shape, group.labels = shape, labels
            groups.add(group)
        return groups

    def get_sources(self):
        return self.lazy("sources", self.make_sources)

    # One scaled copy

    def place_piece(self, factor, src, dst, which, side, color):
        """Scale a copy of the source triangle out in the open, flip it if it
        is a mirror image of its slot, then turn and slide it into place.
        Every side carries its new length the whole way."""
        start = [self.source(SRC[n], which) for n in src]
        end = [self.final(SLOT[n], side) for n in dst]
        piece = Polygon(*start).set_fill(color, FILL + 0.1).set_stroke(color, 3)
        self.add(piece)
        self.play(FadeIn(piece), run_time=0.3)

        # 1. Scale by the factor, drawn down into open space.  Scaling plus a
        #    shift, so blending the corners linearly is exact the whole way.
        center = np.mean(start, axis=0)
        stage = STAGE_X[which] * RIGHT + STAGE_Y * UP
        start = [stage + FACTORS[factor] * (p - center) for p in start]
        self.play(Transform(piece, Polygon(*start).match_style(piece)), run_time=0.7)

        # Its three sides, now a, b, d (or a, b, c) times the factor
        names = [SIDE_NAME[frozenset((src[i], src[(i + 1) % 3]))] for i in range(3)]
        labels = VGroup(*[
            Tex(scaled_side(factor, n), font_size=26).set_color(color)
            for n in names
        ])
        labels.edges = [frozenset((dst[i], dst[(i + 1) % 3])) for i in range(3)]
        tag = Tex(R"\times " + factor, font_size=28).set_color(color)

        def follow(group):
            corners = piece.get_vertices()[:3].copy()
            corners[:, 2] = 0           # flat, even while the piece turns over
            middle = corners.mean(axis=0)
            for i, label in enumerate(group):
                p, q = corners[i], corners[(i + 1) % 3]
                if np.linalg.norm(q - p) < 1e-6:
                    continue
                normal = rotate_vector(normalize(q - p), PI / 2)
                if np.dot(normal, midpoint(p, q) - middle) < 0:
                    normal = -normal
                label.move_to(midpoint(p, q) + 0.2 * normal)
            tag.move_to(middle)

        labels.add_updater(follow)
        labels.update()
        self.play(FadeIn(labels, lag_ratio=0.2), FadeIn(tag, scale=0.6), run_time=0.4)

        # 2. A mirror image of its slot has to be turned over first
        if orientation(*start) != orientation(*end):
            self.play(Rotate(piece, PI, axis=RIGHT, about_point=stage), run_time=0.5)
            start = [stage + (p - stage) * np.array([1, -1, 1]) for p in start]

        # 3. Turn and slide into the slot, keeping the shape rigid in flight
        s = [complex(*p[:2]) for p in start]
        t = [complex(*p[:2]) for p in end]
        cs, ct = np.mean(s), np.mean(t)
        m = (t[0] - ct) / (s[0] - cs)

        def fly(mob, alpha):
            k = abs(m) ** alpha * np.exp(1j * np.angle(m) * alpha)
            c = cs + alpha * (ct - cs)
            pts = [c + k * (z - cs) for z in s]
            mob.set_points_as_corners([pt(z.real, z.imag) for z in pts + pts[:1]])

        # The factor has done its job by the time the piece lands -- its side
        # lengths carry it -- so let the tag go, clearing room for the labels
        # the neighbouring pieces push across the shared edges
        self.play(
            UpdateFromAlphaFunc(piece, fly),
            FadeOut(tag, rate_func=lambda t: smooth(max(0, 2 * t - 1))),
            run_time=1.0,
        )
        labels.clear_updaters()
        return VGroup(piece, VGroup(), labels)

    def flash_matches(self, labels, others):
        """Where a new side meets one already placed, their lengths match:
        that is what lets the pieces glue.  Flash each pair."""
        pairs = [
            (label, other)
            for edge, label in zip(labels.edges, labels)
            for other_labels in others
            for other_edge, other in zip(other_labels.edges, other_labels)
            if edge == other_edge
        ]
        if pairs:
            self.play(*[
                Indicate(m, color=WHITE, scale_factor=1.35)
                for pair in pairs for m in pair
            ], run_time=0.6)
        return pairs

    def build_block(self, pieces, which, side, colors):
        self.get_card()
        self.get_sources()
        placed = VGroup()
        for (factor, src, dst), color in zip(pieces, colors):
            piece = self.place_piece(factor, src, dst, which, side, color)
            self.flash_matches(piece[2], [p[2] for p in placed])
            placed.add(piece)
        return placed

    # Sections

    def draw_parallelogram(self):
        self.get_card()
        corners = [self.intro(p) for p in (P0, P1, P2, P3)]
        shape = Polygon(*corners).set_stroke(WHITE, 3)
        diag_d = Line(corners[0], corners[2]).set_stroke(TRI_D[1], 3)
        diag_c = Line(corners[3], corners[1]).set_stroke(TRI_C[1], 3)
        sides = VGroup(
            self.edge_label("a", corners[0], corners[1], -0.25, font_size=34),
            self.edge_label("a", corners[2], corners[3], -0.25, font_size=34),
            self.edge_label("b", corners[1], corners[2], -0.25, font_size=34),
            self.edge_label("b", corners[3], corners[0], -0.25, font_size=34),
        )
        diag_labels = VGroup(
            Tex("d", font_size=34).set_color(TRI_D[1]).move_to(
                interpolate(corners[0], corners[2], 0.72) + 0.22 * UP),
            Tex("c", font_size=34).set_color(TRI_C[1]).move_to(
                interpolate(corners[3], corners[1], 0.72) + 0.25 * RIGHT),
        )
        self.play(ShowCreation(shape), run_time=0.9)
        self.play(FadeIn(sides, lag_ratio=0.2), run_time=0.6)
        self.play(ShowCreation(diag_d), ShowCreation(diag_c), FadeIn(diag_labels), run_time=0.9)
        self.set_state("intro", VGroup(shape, diag_d, diag_c, sides, diag_labels))
        self.wait(0.6)

    def split(self):
        self.get_card()
        intro = self.lazy("intro", VGroup)
        sources = self.make_sources()

        # One triangle from each diagonal's cut, lifted out to wait up top
        for which, tri, colors, target in [
            ("d", (P0, P1, P2), TRI_D, sources[0]),
            ("c", (P0, P1, P3), TRI_C, sources[1]),
        ]:
            lifted = Polygon(*[self.intro(p) for p in tri]).set_fill(colors[1], FILL).set_stroke(colors[1], 3)
            self.play(FadeIn(lifted), run_time=0.4)
            self.play(ReplacementTransform(lifted, target.shape), run_time=1.0)
        self.play(FadeOut(intro), FadeIn(VGroup(*[s.labels for s in sources])), run_time=0.6)
        self.set_state("sources", sources)

    def left_block(self):
        self.note("Scale the (a, b, d) triangle by b, d and a.", wait=0.9)
        block = self.build_block(LEFT_PIECES, "d", "left", TRI_D)
        self.set_state("left", block)

    def right_block(self):
        self.note("Same with the (a, b, c) triangle: b, c, a.", wait=0.9)
        block = self.build_block(RIGHT_PIECES, "c", "right", TRI_C)
        self.set_state("right", block)

    def join(self):
        left = self.lazy("left", VGroup)
        right = self.lazy("right", VGroup)
        # Both blocks carry a side of length ab: slide them together along it
        self.play(left.animate.shift(GAP * RIGHT), right.animate.shift(GAP * LEFT), run_time=0.9)
        seam = Line(self.final(X2, "left") + GAP * RIGHT, self.final(Y1, "left") + GAP * RIGHT)
        seam.set_stroke(WHITE, 5)
        self.play(ShowPassingFlash(seam, time_width=0.8), run_time=0.8)
        if len(left) and len(right):
            # The two ab sides match; once shown, retire both labels -- they
            # sit in the narrowest piece and would crowd the seam
            pairs = self.flash_matches(right[0][2], [p[2] for p in left])
            if pairs:
                self.play(FadeOut(VGroup(*[m for pair in pairs for m in pair])), run_time=0.4)

    def conclude(self):
        self.get_card()
        sources = self.get_sources()
        left = self.lazy("left", VGroup)
        right = self.lazy("right", VGroup)

        def f(p):
            return self.final(p, "left") + GAP * RIGHT

        # Drop the scale tags and inner labels; read off the outer edges
        tags = VGroup(*[VGroup(g[1], g[2]) for g in [*left, *right]])
        outline = Polygon(f(X0), f(X4), f(Y2), f(Y0)).set_stroke(WHITE, 4)
        top = VGroup(
            self.edge_label("d^2", f(Y0), f(Y1), 0.25, font_size=32, color=TRI_D[1]),
            self.edge_label("c^2", f(Y1), f(Y2), 0.25, font_size=32, color=TRI_C[1]),
        )
        bottom = VGroup(*[
            self.edge_label(tex, f(p), f(q), -0.27, font_size=30, color=color)
            for tex, p, q, color in [
                ("b^2", X0, X1, TRI_D[1]), ("a^2", X1, X2, TRI_D[1]),
                ("b^2", X2, X3, TRI_C[1]), ("a^2", X3, X4, TRI_C[1]),
            ]
        ])
        sides = VGroup(
            self.edge_label("ab", f(X0), f(Y0), 0.26, font_size=28),
            self.edge_label("ab", f(X4), f(Y2), -0.26, font_size=28),
        )
        self.play(
            FadeOut(tags), sources.animate.set_opacity(0.3),
            ShowCreation(outline), run_time=0.8,
        )
        self.play(FadeIn(sides), FadeIn(top, lag_ratio=0.3), FadeIn(bottom, lag_ratio=0.2), run_time=1.0)

        # Equal, parallel outer sides: the whole shape is a parallelogram
        self.play(*[Indicate(s, color=YELLOW) for s in sides], run_time=0.9)
        self.note("A parallelogram: its top and bottom are equal.", wait=1.0)

        top_brace = Brace(Line(f(Y0), f(Y2)), UP, buff=0.4)
        bottom_brace = Brace(Line(f(X0), f(X4)), DOWN, buff=0.45)
        self.play(GrowFromCenter(top_brace), GrowFromCenter(bottom_brace), run_time=0.6)
        law = self.add_step(R"d^2 + c^2 = b^2 + a^2 + b^2 + a^2", font_size=40, wait=0.6)
        law = self.replace_step(
            law, R"c^2 + d^2 = 2a^2 + 2b^2",
            font_size=50, color=RESULT_COLOR, wait=0.3,
        )
        box = SurroundingRectangle(law, color=RESULT_COLOR, buff=0.2).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(law, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.wait(1.5)
