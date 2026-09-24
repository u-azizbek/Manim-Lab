from manim_imports_ext import *
from itertools import product


# Render with:
#   ./render.sh _2026/Series/binomial_blocks.py
#
# (a+b)^n as blocks, up to n = 4.  A segment a + b rises into a square, the
# square is pushed back into a cube, and each time every piece splits into an
# "a" part and a "b" part.  A piece's colour says how many b's it has, which
# is what makes the like terms line up.  There is no fourth direction to draw,
# so (a+b)^4 is the cube taken twice: one copy for the extra a, one for the
# extra b.  Counting colours across the two copies gives 1, 3+1, 3+3, 1+3, 1:
# the rows of Pascal's triangle.
#
# Colours follow the reference figure.

A, B = 1.6, 0.8
S = A + B
PARTS = [(0, A, 0), (A, B, 1)]           # (start, length, number of b's)
DEPTH = np.array([0.45, 0.45, 0])        # screen offset per unit of depth

RED_ = "#FF2A2A"
BLUE_ = "#3348FF"
PALETTES = {
    1: [RED_, BLUE_],
    2: [RED_, "#00C800", BLUE_],
    3: [RED_, "#D4D400", "#00C878", BLUE_],
    4: [RED_, "#FF9A00", "#00C800", "#0A9BFF", BLUE_],
}
TERMS = {
    1: ["a", "b"],
    2: ["a^2", "2ab", "b^2"],
    3: ["a^3", "3a^2b", "3ab^2", "b^3"],
    4: ["a^4", "4a^3b", "6a^2b^2", "4ab^3", "b^4"],
}
LINKS = "#B040FF"                        # the dashed lines of the fourth direction

ORIGIN_PT = np.array([-1.74, -0.55, 0])  # front bottom left corner of the square / cube
EQ_Y = 3.95
ROW_Y = -2.35
LABEL_Y = -3.55
CAPTION_Y = -4.55


def face_colors(color):
    return color, interpolate_color(color, WHITE, 0.3), interpolate_color(color, BLACK, 0.3)


def block(origin, corner, size, color):
    """An axis-aligned box in oblique projection: front, top and right faces."""
    x0, d0, z0 = corner
    sx, sd, sz = size
    P = lambda x, d, z: origin + x * RIGHT + z * UP + d * DEPTH
    front_c, top_c, side_c = face_colors(color)
    front = Polygon(P(x0, d0, z0), P(x0 + sx, d0, z0), P(x0 + sx, d0, z0 + sz), P(x0, d0, z0 + sz))
    top = Polygon(P(x0, d0, z0 + sz), P(x0 + sx, d0, z0 + sz), P(x0 + sx, d0 + sd, z0 + sz), P(x0, d0 + sd, z0 + sz))
    side = Polygon(P(x0 + sx, d0, z0), P(x0 + sx, d0 + sd, z0), P(x0 + sx, d0 + sd, z0 + sz), P(x0 + sx, d0, z0 + sz))
    faces = VGroup(side, top, front) if sd > 1e-3 else VGroup(front)
    for face, c in zip([side, top, front], [side_c, top_c, front_c]):
        face.set_fill(c, 1).set_stroke(BLACK, 2)
    return faces


def cube_cells(origin, colors):
    """The (a+b)^3 cube as 8 blocks, far ones first; `colors(nb)` colours a
    block by its number of b's.  Returns [(nb, block)]."""
    cells = []
    for (x0, sx, bx), (d0, sd, bd), (z0, sz, bz) in product(PARTS, repeat=3):
        cells.append(((-d0, x0, z0), bx + bd + bz, block(origin, (x0, d0, z0), (sx, sd, sz), colors(bx + bd + bz))))
    cells.sort(key=lambda c: c[0])
    return [(nb, mob) for key, nb, mob in cells]


def recolor(blk, color):
    """Animations taking a block's three faces to a new colour."""
    front_c, top_c, side_c = face_colors(color)
    return [face.animate.set_fill(c) for face, c in zip(blk, [side_c, top_c, front_c])]


def layered(blocks):
    """Blocks that paint over each other in the order given.

    manimgl draws a whole group's fills first and all its strokes after, so
    in one VGroup the edges of the back blocks would show through the faces
    of the front ones.  An invisible point of another kind between blocks
    splits them into separate draws.
    """
    parts = []
    for blk in blocks:
        parts += [blk, DotCloud([blk.get_center()], radius=0.001).set_opacity(0)]
    return Group(*parts)


def redrawn(build):
    """always_redraw for a layered Group: `become` cannot morph a group that
    mixes shape types, so swap its parts for freshly built ones each frame."""
    group = build()

    def update(g):
        g.set_submobjects(build().submobjects)
        g.note_changed_data()

    return group.add_updater(update)


def by_count(cells, n):
    return [layered([mob for nb, mob in cells if nb == k]) for k in range(n + 1)]


class BinomialBlocks(MockTestShort):
    """(a+b)^n for n = 1..4, built from blocks."""

    test = ""
    card_top_buff = 0.6

    problem_tex = (
        R"\text{Why is } (a+b)^4 = a^4 + 4a^3b\\"
        R"+\, 6a^2b^2 + 4ab^3 + b^4\, ?"
    )

    sections = [
        "pose",
        "level_one",
        "level_two",
        "level_three",
        "level_four",
        "pascal",
        "outro",
    ]

    def caption(self, message, wait=1.3):
        text = Text(message, font_size=26).set_color(self.note_color)
        text.set_max_width(7.4).move_to(CAPTION_Y * UP)
        self.play(FadeIn(text, 0.15 * UP), run_time=0.4)
        self.wait(wait)
        self.play(FadeOut(text), run_time=0.3)

    def equation(self, n):
        terms = TERMS[n]
        tex = f"(a+b)^{n} = " + " + ".join(terms)
        eq = Tex(tex, isolate=terms, font_size=42)
        for term, color in zip(terms, PALETTES[n]):
            eq[term][-1].set_color(color)
        eq.set_max_width(7.6).move_to(EQ_Y * UP)
        eq.terms = [eq[term][-1] for term in terms]
        eq.head = VGroup(*[g for g in eq.family_members_with_points()
                           if not any(g in t.family_members_with_points() for t in eq.terms)])
        return eq

    def explode(self, groups, n, scale, buff):
        """Copies of the like-term groups fly out into a labelled row, and the
        labels then complete the equation."""
        targets = Group(*[g.copy().scale(scale) for g in groups]).arrange(RIGHT, buff=buff, aligned_edge=DOWN)
        targets.set_width(min(targets.get_width(), 7.4)).move_to(ROW_Y * UP)
        pieces = Group(*[g.copy() for g in groups])
        self.play(
            LaggedStart(*[Transform(p, t) for p, t in zip(pieces, targets)], lag_ratio=0.15),
            run_time=1.3,
        )
        labels = VGroup(*[
            Tex(term, font_size=40).set_color(color).move_to([t.get_x(), LABEL_Y, 0])
            for term, color, t in zip(TERMS[n], PALETTES[n], targets)
        ])
        self.play(LaggedStart(*[FadeIn(l, 0.15 * UP) for l in labels], lag_ratio=0.15), run_time=0.8)
        return pieces, labels

    def set_equation(self, n, labels):
        old = self.lazy_state.get("equation")
        eq = self.equation(n)
        anims = [FadeOut(old, 0.2 * UP)] if old is not None else []
        self.play(*anims, FadeIn(eq.head), run_time=0.5)
        self.play(
            LaggedStart(*[TransformFromCopy(l, t) for l, t in zip(labels, eq.terms)], lag_ratio=0.12),
            run_time=1.1,
        )
        self.set_state("equation", eq)
        return eq

    # Sections

    def level_one(self):
        self.get_card()
        start = ORIGIN_PT
        seg_a = Line(start, start + A * RIGHT).set_stroke(RED_, 10)
        seg_b = Line(start + A * RIGHT, start + S * RIGHT).set_stroke(BLUE_, 10)
        names = VGroup(
            Tex("a", font_size=36).set_color(RED_).next_to(seg_a, DOWN, buff=0.18),
            Tex("b", font_size=36).set_color(BLUE_).next_to(seg_b, DOWN, buff=0.18),
        )
        self.play(ShowCreation(seg_a), FadeIn(names[0]), run_time=0.7)
        self.play(ShowCreation(seg_b), FadeIn(names[1]), run_time=0.5)
        self.set_equation(1, names)
        self.wait(0.5)
        self.set_state("segment", VGroup(seg_a, seg_b))
        self.set_state("names", names)

    def square(self, height, mix):
        """The square rising from the segment: the bottom row starts in the
        segment's colours and takes on (a+b)^2 colours as `mix` goes to 1."""
        cells = []
        for (x0, sx, bx), (z0, sz, bz) in product(PARTS, repeat=2):
            h = min(max(height - z0, 0), sz)
            if h <= 1e-3:
                continue
            if bz == 0:
                color = interpolate_color(PALETTES[1][bx], PALETTES[2][bx], mix)
            else:
                color = PALETTES[2][bx + 1]
            cells.append((bx + bz, block(ORIGIN_PT, (x0, 0, z0), (sx, 0, h), color)))
        return cells

    def level_two(self):
        segment = self.lazy("segment", VGroup)
        rise, mix = ValueTracker(0), ValueTracker(0)
        square = redrawn(lambda: layered([m for nb, m in self.square(rise.get_value(), mix.get_value())]))
        self.add(square, segment)
        self.play(
            rise.animate.set_value(S), mix.animate.set_value(1),
            FadeOut(segment), run_time=1.6,
        )
        side = VGroup(
            Tex("a", font_size=36).set_color(RED_).next_to(ORIGIN_PT + A / 2 * UP, LEFT, buff=0.18),
            Tex("b", font_size=36).set_color(BLUE_).next_to(ORIGIN_PT + (A + B / 2) * UP, LEFT, buff=0.18),
        )
        self.play(FadeIn(side), run_time=0.4)
        self.caption("Sides a + b: the square splits into a², two ab's and b².", wait=1.1)

        cells = self.square(S, 1)
        pieces, labels = self.explode(by_count(cells, 2), 2, 1.0, 0.7)
        self.set_equation(2, labels)
        self.wait(0.8)
        self.play(FadeOut(pieces), FadeOut(labels), FadeOut(side), FadeOut(self.lazy("names", VGroup)), run_time=0.5)
        square.clear_updaters()
        self.set_state("square", square)

    def cube(self, depth, mix):
        """The cube pushed back from the square: the front layer takes on
        (a+b)^3 colours as `mix` goes to 1."""
        cells = []
        for (x0, sx, bx), (d0, sd, bd), (z0, sz, bz) in product(PARTS, repeat=3):
            d = min(max(depth - d0, 0), sd)
            if d0 > 0 and d <= 1e-3:
                continue
            flat = bx + bz
            if bd == 0:
                color = interpolate_color(PALETTES[2][flat], PALETTES[3][flat], mix)
            else:
                color = PALETTES[3][flat + 1]
            cells.append(((-d0, x0, z0), flat + bd, block(ORIGIN_PT, (x0, d0, z0), (sx, d, sz), color)))
        cells.sort(key=lambda c: c[0])
        return [(nb, m) for key, nb, m in cells]

    def level_three(self):
        square = self.lazy("square", lambda: layered([m for nb, m in self.square(S, 1)]))
        push, mix = ValueTracker(0), ValueTracker(0)
        cube = redrawn(lambda: layered([m for nb, m in self.cube(push.get_value(), mix.get_value())]))
        self.remove(square)
        self.add(cube)
        self.play(push.animate.set_value(S), mix.animate.set_value(1), run_time=2.0)
        self.caption("Push it back by a + b: every piece gains an a or a b.", wait=1.1)

        cells = self.cube(S, 1)
        pieces, labels = self.explode(by_count(cells, 3), 3, 0.55, 0.45)
        self.set_equation(3, labels)
        self.wait(0.9)
        self.play(FadeOut(pieces), FadeOut(labels), run_time=0.5)
        cube.clear_updaters()
        self.set_state("cube", cube)

    def level_four(self):
        cube = self.lazy("cube", lambda: layered([m for nb, m in self.cube(S, 1)]))

        # No room for a fourth direction: one copy of the cube per choice
        self.caption("No 4th direction to draw: one copy\nof the cube for a, one for b.", wait=1.2)
        shift = np.array([-0.75, 0.3, 0])
        offset = np.array([1.5, -2.4, 0])
        with_a = cube_cells(ORIGIN_PT, lambda nb: PALETTES[3][nb])
        slab_a = layered([m for nb, m in with_a])
        self.remove(cube)
        self.add(slab_a)
        self.play(slab_a.animate.shift(shift), run_time=0.7)
        cube_origin = ORIGIN_PT + shift
        with_b = cube_cells(cube_origin, lambda nb: PALETTES[3][nb])
        slab_b = layered([m for nb, m in with_b])
        corners = [(0, 0, 0), (S, 0, 0), (0, S, S), (S, S, S)]
        P = lambda o, c: o + c[0] * RIGHT + c[2] * UP + c[1] * DEPTH
        self.add(slab_b)
        self.play(slab_b.animate.shift(offset), run_time=1.4)
        links = VGroup(*[
            DashedLine(P(cube_origin, c), P(cube_origin + offset, c), dash_length=0.1).set_stroke(LINKS, 2.5)
            for c in corners
        ])
        tags = VGroup(
            Tex(R"\times\, a", font_size=36).set_color(RED_).next_to(slab_a, LEFT, buff=0.1).shift(0.9 * UP),
            Tex(R"\times\, b", font_size=36).set_color(BLUE_).next_to(slab_b, RIGHT, buff=0.1).shift(0.9 * DOWN),
        )
        self.add(links, slab_b)
        self.play(ShowCreation(links, lag_ratio=0.2), FadeIn(tags), run_time=0.8)

        # Recolour by the number of b's: the b copy moves one colour along
        self.play(
            *[anim for nb, blk in with_a for anim in recolor(blk, PALETTES[4][nb])],
            *[anim for nb, blk in with_b for anim in recolor(blk, PALETTES[4][nb + 1])],
            run_time=0.9,
        )

        # Count each colour across both copies
        counts = [(1, 0), (3, 1), (3, 3), (1, 3), (0, 1)]
        slots = np.linspace(-3.0, 3.0, 5)
        labels, sums = VGroup(), VGroup()
        for k, (ca, cb) in enumerate(counts):
            color = PALETTES[4][k]
            members = [nb_blk for nb, nb_blk in with_a if nb == k] + [nb_blk for nb, nb_blk in with_b if nb + 1 == k]
            label = Tex(TERMS[4][k], font_size=38).set_color(color).move_to([slots[k], LABEL_Y, 0])
            parts = [str(c) for c in (ca, cb) if c]
            total = Tex(" + ".join(parts), font_size=30).set_color(color).next_to(label, DOWN, buff=0.15)
            self.play(
                *[Indicate(blk, color=WHITE, scale_factor=1.06) for blk in members],
                FadeIn(label, 0.15 * UP), FadeIn(total),
                run_time=0.75,
            )
            labels.add(label)
            sums.add(total)
        self.set_equation(4, labels)
        self.wait(0.8)
        self.set_state("four", Group(slab_a, slab_b, links, tags, labels, sums))

    def pascal(self):
        four = self.lazy("four", Group)
        self.play(FadeOut(four), run_time=0.5)

        rows = [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]
        triangle = VGroup()
        for n, entries in enumerate(rows):
            palette = PALETTES.get(n, [WHITE])
            line = VGroup(*[
                Tex(str(v), font_size=64).set_color(palette[k] if n else WHITE)
                for k, v in enumerate(entries)
            ]).arrange(RIGHT, buff=1.0)
            triangle.add(line)
        triangle.arrange(DOWN, buff=0.55).move_to(0.6 * UP)
        self.play(LaggedStart(*[FadeIn(r, 0.2 * DOWN) for r in triangle], lag_ratio=0.25), run_time=1.4)

        # 4 = 3 + 1 and 6 = 3 + 3: the a copy and the b copy
        three, four_row = triangle[3], triangle[4]
        for k in (1, 2, 3):
            pair = VGroup(three[k - 1], three[k])
            self.play(
                Indicate(pair, color=WHITE, scale_factor=1.2),
                Indicate(four_row[k], color=YELLOW, scale_factor=1.3),
                run_time=0.6,
            )
        self.caption("Each count is the sum of the two above:\nPascal's triangle, the binomial coefficients.", wait=1.6)
        eq = self.lazy_state.get("equation")
        if eq is not None:
            box = SurroundingRectangle(eq, buff=0.15).set_stroke(YELLOW, 3)
            self.play(ShowCreation(box), FlashAround(eq, color=YELLOW, time_width=1.5), run_time=1.2)
        self.wait(1.2)
