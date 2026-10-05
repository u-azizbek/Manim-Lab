from manim_imports_ext import *
from math import comb
from _2026.Series.binomial_blocks import block, layered


# Render with:
#   ./render.sh _2026/Series/binomial_blocks_six.py
#
# (a+b)^3 up to (a+b)^6 as blocks.  Past three dimensions each power is two
# copies of the one before, one times a and one times b:
#   (a+b)^3  one cube      (a+b)^4  two cubes
#   (a+b)^5  four cubes    (a+b)^6  eight cubes
# A block's colour counts its b's.  The a copy keeps its colours, the b copy
# moves every block one colour along, which is Pascal's rule
#   C(n, k) = C(n-1, k) + C(n-1, k-1),
# and the coefficient row under the cubes splits and adds in exactly that way.

BASE_COLORS = ["#FF3B3B", "#FF9F1C", "#FFD23F", "#3DDC5A", "#2EC4B6", "#3FA7FF", "#8A4DFF"]
FIG_CENTER = 0.75 * UP
EQ_Y = 4.2
ROW_Y = -3.05
NOTE_Y = -4.35

# stage k shows (a+b)^(3+k): 2^k cubes on a cols x rows grid, cube side S
STAGES = {0: (1, 1, 2.3), 1: (2, 1, 1.85), 2: (2, 2, 1.55), 3: (4, 2, 1.12)}


def palette(n):
    return color_gradient(BASE_COLORS, n + 1)


def cube(origin, side, colors_by_b):
    """(a+b)^3 as 8 blocks, a = 2/3 and b = 1/3 of the side, far blocks first."""
    a_len, b_len = 2 * side / 3, side / 3
    parts = [(0, a_len, 0), (a_len, b_len, 1)]
    cells = []
    for (x0, sx, bx) in parts:
        for (d0, sd, bd) in parts:
            for (z0, sz, bz) in parts:
                nb = bx + bd + bz
                cells.append(((-d0, x0, z0), nb, block(origin, (x0, d0, z0), (sx, sd, sz), colors_by_b(nb))))
    cells.sort(key=lambda c: c[0])
    return [(nb, blk) for key, nb, blk in cells]


def stage_layout(k):
    """Screen centres of the 2^k cubes at stage k, indexed by their extra letters."""
    cols, rows, side = STAGES[k]
    pitch = 1.45 * side + 0.3
    centers = {}
    for j in range(2 ** k):
        if k == 0:
            col, row = 0, 0
        elif k == 1:
            col, row = j, 0
        elif k == 2:
            col, row = j >> 1, j & 1
        else:
            col, row = j & 3, j >> 2      # aaa aab aba abb / baa bab bba bbb
        x = (col - (cols - 1) / 2) * pitch
        y = ((rows - 1) / 2 - row) * pitch
        centers[j] = FIG_CENTER + x * RIGHT + y * UP
    return centers, side


def letters(j, k):
    """The extra factors of cube j at stage k, oldest first: 0 -> a, 1 -> b."""
    return "".join("b" if (j >> (k - 1 - i)) & 1 else "a" for i in range(k))


def build_stage(k):
    n = 3 + k
    colors = palette(n)
    centers, side = stage_layout(k)
    cubes = []
    for j in range(2 ** k):
        extra = bin(j).count("1")
        origin = centers[j] - 0.725 * side * (RIGHT + UP)
        cells = cube(origin, side, lambda nb, e=extra: colors[nb + e])
        cubes.append(dict(group=layered([blk for nb, blk in cells]), cells=cells, extra=extra, j=j))
    return cubes


def term(n, k):
    coef = comb(n, k)
    tex = "" if coef == 1 else str(coef)
    for letter, power in (("a", n - k), ("b", k)):
        if power == 1:
            tex += letter
        elif power > 1:
            tex += f"{letter}^{{{power}}}"
    return tex


def equation(n):
    terms = [term(n, k) for k in range(n + 1)]
    eq = Tex(f"(a+b)^{{{n}}} = " + " + ".join(terms), isolate=terms, font_size=40)
    for k, (t, color) in enumerate(zip(terms, palette(n))):
        eq[t][-1].set_color(color)
    return eq.set_max_width(7.6).move_to(EQ_Y * UP)


def coefficient_row(n):
    items = VGroup()
    for k, color in enumerate(palette(n)):
        chip = Square(0.26).set_stroke(WHITE, 1).set_fill(color, 1)
        number = Integer(comb(n, k), font_size=40).set_color(color)
        items.add(VGroup(chip, number).arrange(DOWN, buff=0.12))
    return items.arrange(RIGHT, buff=0.42).move_to(ROW_Y * UP)


class BinomialBlocksSix(MockTestShort):
    """(a+b)^3 to (a+b)^6 as blocks: each power is two copies of the last."""

    test = ""
    card_top_buff = 0.6

    problem_tex = (
        R"\text{Binomial blocks beyond 3D:}\\"
        R"(a+b)^3 \ \to\ (a+b)^6"
    )

    sections = ["pose", "cube", "fourth", "fifth", "sixth", "finale", "outro"]

    def caption(self, text, wait=1.3):
        note = Text(text, font_size=26).set_color(GREY_A).move_to(NOTE_Y * UP)
        self.play(FadeIn(note, 0.15 * UP), run_time=0.4)
        self.wait(wait)
        self.play(FadeOut(note), run_time=0.3)

    def show(self, name, mob):
        old = self.lazy_state.get(name)
        self.set_state(name, mob)
        return old

    def tags(self, cubes, k):
        if k == 0:
            return VGroup()
        centers, side = stage_layout(k)
        return VGroup(*[
            Tex(Rf"\times\,{letters(c['j'], k)}", font_size=26).set_color(GREY_A)
            .next_to(centers[c["j"]] + 0.725 * side * DOWN, DOWN, buff=0.05)
            for c in cubes
        ])

    # Stages

    def cube(self):
        self.get_card()
        cubes = build_stage(0)
        blocks = cubes[0]["cells"]
        # The eight blocks drop in, far ones first
        for nb, blk in blocks:
            blk.save_state()
            blk.shift(1.2 * UP).set_opacity(0)
        self.add(cubes[0]["group"])
        self.play(LaggedStart(*[Restore(blk) for nb, blk in blocks], lag_ratio=0.12), run_time=2.0)
        eq, row = equation(3), coefficient_row(3)
        self.play(Write(eq), FadeIn(row, lag_ratio=0.15), run_time=1.2)
        self.caption("A block's colour counts its b's: 1, 3, 3, 1.", wait=1.2)
        self.set_state("cubes", cubes)
        self.set_state("equation", eq)
        self.set_state("row", row)

    def double(self, k):
        """Stage k-1 -> stage k: every cube splits into an a copy and a b copy."""
        n = 3 + k
        old_cubes = self.lazy_state["cubes"]
        new_cubes = build_stage(k)
        old_tags = self.lazy_state.get("tags", VGroup())

        moves = []
        copies = []
        for c in old_cubes:
            a_target = new_cubes[2 * c["j"]]["group"]
            b_target = new_cubes[2 * c["j"] + 1]["group"]
            twin = c["group"].copy()
            copies.append(twin)
            moves += [Transform(c["group"], a_target), Transform(twin, b_target)]
        self.play(*moves, FadeOut(old_tags), run_time=1.8)
        for c, twin in zip(old_cubes, copies):
            self.remove(c["group"], twin)
        for c in new_cubes:
            self.add(c["group"])
        tags = self.tags(new_cubes, k)
        self.play(FadeIn(tags, lag_ratio=0.05), run_time=0.5)

        # The coefficients do the same: each one goes to its own colour and the next
        old_row = self.lazy_state["row"]
        new_row = coefficient_row(n)
        flights = []
        for i, item in enumerate(old_row):
            for target in (new_row[i], new_row[i + 1]):
                twin = item[1].copy()
                flights.append(twin)
        self.play(*[
            twin.animate.move_to(new_row[i // 2 + i % 2][1]).set_color(palette(n)[i // 2 + i % 2]).set_opacity(0.6)
            for i, twin in enumerate(flights)
        ], FadeOut(VGroup(*[item[0] for item in old_row])), run_time=1.1)
        self.play(FadeOut(VGroup(*flights)), FadeOut(VGroup(*[item[1] for item in old_row])),
                  FadeIn(new_row, scale=1.2), run_time=0.6)

        old_eq = self.lazy_state["equation"]
        new_eq = equation(n)
        self.play(FadeOut(old_eq, 0.2 * UP), FadeIn(new_eq, 0.2 * UP), run_time=0.7)
        self.set_state("cubes", new_cubes)
        self.set_state("tags", tags)
        self.set_state("row", new_row)
        self.set_state("equation", new_eq)

    def fourth(self):
        self.double(1)
        self.caption("No 4th direction: one copy times a, one times b.\nThe b copy moves every colour one step.", wait=1.6)

    def fifth(self):
        self.double(2)
        self.caption("Each number = the two above it: 4 + 6 = 10.", wait=1.2)

    def sixth(self):
        self.double(3)
        self.caption("Eight cubes: 1, 6, 15, 20, 15, 6, 1.", wait=1.0)

        # Count one colour: every block with three a's and three b's
        cubes = self.lazy_state["cubes"]
        middle = [blk for c in cubes for nb, blk in c["cells"] if nb + c["extra"] == 3]
        counter = Integer(0, font_size=48).set_color(palette(6)[3])
        label = VGroup(Tex(R"a^3b^3:", font_size=44).set_color(palette(6)[3]), counter).arrange(RIGHT, buff=0.2)
        label.move_to(NOTE_Y * UP)
        self.play(FadeIn(label), run_time=0.3)
        for i, blk in enumerate(middle):
            counter.set_value(i + 1)
            self.play(Indicate(blk, color=WHITE, scale_factor=1.12), run_time=0.14)
        self.play(Flash(counter, color=palette(6)[3]), run_time=0.6)
        self.wait(0.5)
        self.play(FadeOut(label), run_time=0.3)

    def finale(self):
        # Pascal's triangle, rows 0 to 6, in the same colours
        eq = self.lazy_state.get("equation")
        box = SurroundingRectangle(eq, buff=0.14).set_stroke(YELLOW, 3)
        self.play(ShowCreation(box), FlashAround(eq, color=YELLOW, time_width=1.5), run_time=1.2)
        self.caption("Doubling the cubes builds Pascal's triangle:\nthe binomial coefficients C(n, k).", wait=1.8)
        self.wait(0.6)
