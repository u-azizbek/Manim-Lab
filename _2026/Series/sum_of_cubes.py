from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Series/sum_of_cubes.py
#
# Nicomachus: 1^3 + 2^3 + ... + n^3 = (1 + 2 + ... + n)^2, without words.
# Cut the cube k^3 into k slabs k x k x 1.  Laid flat they fill the L-shaped
# band (gnomon) between the squares of side T(k-1) and T(k), T(k) = k(k+1)/2:
# a k x k corner and two arms of length T(k-1) = k (k-1)/2, i.e. (k-1)/2 slabs
# each.  For even k that is half a slab per arm, so one slab is cut in two.
# The bands for k = 1..n build the square of side T(n).
#
# Everything is drawn in isometric projection; boxes are painted back to front.

UNIT = 0.27
EX = UNIT * np.array([np.cos(-PI / 6), np.sin(-PI / 6), 0])
EY = UNIT * np.array([np.cos(PI / 6), np.sin(PI / 6), 0])
EZ = UNIT * UP
N = 5
COLORS = ["#E8111A", "#F2B90F", "#1FD01F", "#5A96EE", "#A64FD6"]
FLOOR_OFFSET = np.array([-12.99 * UNIT, -1.55, 0])


def tri(k):
    return k * (k + 1) // 2


def iso(x, y, z):
    return x * EX + y * EY + z * EZ


def box(x0, y0, z0, dx, dy, dz, color, offset=ORIGIN):
    """A solid box with its unit grid: top, the +x face and the -y face (the three we see)."""
    x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
    pt = lambda x, y, z: iso(x, y, z) + offset
    top = Polygon(pt(x0, y0, z1), pt(x1, y0, z1), pt(x1, y1, z1), pt(x0, y1, z1))
    side = Polygon(pt(x1, y0, z0), pt(x1, y1, z0), pt(x1, y1, z1), pt(x1, y0, z1))
    front = Polygon(pt(x0, y0, z0), pt(x1, y0, z0), pt(x1, y0, z1), pt(x0, y0, z1))
    for face, shade in ((top, interpolate_color(color, WHITE, 0.18)), (side, color),
                        (front, interpolate_color(color, BLACK, 0.3))):
        face.set_fill(shade, 1).set_stroke(BLACK, 1.6)
    grid_color = interpolate_color(color, BLACK, 0.45)
    top_grid = VGroup(
        *[Line(pt(x0 + i, y0, z1), pt(x0 + i, y1, z1)) for i in range(1, int(dx))],
        *[Line(pt(x0, y0 + j, z1), pt(x1, y0 + j, z1)) for j in range(1, int(dy))],
    ).set_stroke(grid_color, 0.9)
    side_grid = VGroup(
        *[Line(pt(x1, y0 + j, z0), pt(x1, y0 + j, z1)) for j in range(1, int(dy))],
        *[Line(pt(x1, y0, z0 + h), pt(x1, y1, z0 + h)) for h in range(1, int(dz))],
        *[Line(pt(x0 + i, y0, z0), pt(x0 + i, y0, z1)) for i in range(1, int(dx))],
        *[Line(pt(x0, y0, z0 + h), pt(x1, y0, z0 + h)) for h in range(1, int(dz))],
    ).set_stroke(grid_color, 0.9)
    # Sides before the top, so a box can be split into a "sides" and a "tops" layer
    return VGroup(side, front, side_grid, top, top_grid)


def gnomon_tiles(k):
    """(x0, y0, dx, dy) of the tiles in band k, in the order the cube's slabs fill them."""
    s, t = tri(k - 1), tri(k)
    tiles = [(s, s, k, k)]
    x_arm, y_arm = [], []
    edge = s
    while edge > 0:
        width = min(k, edge)
        x_arm.append((edge - width, s, width, k))
        y_arm.append((s, edge - width, k, width))
        edge -= width
    for a, b in zip(x_arm, y_arm):
        tiles += [a, b]
    return tiles


def layered(parts):
    """manimgl draws all of a group's fills before any of its strokes, so edges
    of hidden faces would show through.  An invisible point of another kind
    between parts splits them into separate draws, painted in order."""
    items = []
    for part in parts:
        items += [part, DotCloud([part.get_center()], radius=0.001).set_opacity(0)]
    return Group(*items)


def flat_floor(tiles):
    """Flat boxes of equal height: every side face first, then every top, so no top is overdrawn."""
    boxes = [box(x0, y0, 0, dx, dy, 1, color, offset=FLOOR_OFFSET) for (x0, y0, dx, dy), color in tiles]
    return layered([VGroup(*[VGroup(*b[:3]) for b in boxes]), VGroup(*[VGroup(*b[3:]) for b in boxes])])


class SumOfCubes(BrandOutroMixin, ShortsScene):
    """1^3 + ... + 5^3 = (1 + ... + 5)^2: cubes sliced and laid flat as L-shaped bands."""

    sections = ["proof", "outro"]

    def cube_slabs(self, k):
        """The cube k^3 as k slabs; for even k the top slab comes in two halves."""
        color = COLORS[k - 1]
        slabs = [box(0, 0, h, k, k, 1, color) for h in range(k)]
        if k % 2 == 0:
            slabs[-1:] = [box(0, 0, k - 1, k / 2, k, 1, color), box(k / 2, 0, k - 1, k / 2, k, 1, color)]
        return slabs

    def proof(self):
        title = Text("Proof without words", font_size=58, weight=BOLD)
        title.set_color_by_gradient(*COLORS).move_to(6.35 * UP)
        self.play(Write(title), run_time=1.1)

        # The five cubes, in a row
        slab_lists = [self.cube_slabs(k) for k in range(1, N + 1)]
        cubes = Group(*[layered(slabs) for slabs in slab_lists])
        cubes.arrange(RIGHT, buff=0.14, aligned_edge=DOWN).move_to(3.95 * UP)
        labels = VGroup(*[
            Tex(Rf"{k}^3", font_size=38).set_color(interpolate_color(c, WHITE, 0.25)).next_to(cube, DOWN, buff=0.14)
            for k, c, cube in zip(range(1, N + 1), COLORS, cubes)
        ])
        labels.set_y(labels[-1].get_y())
        self.play(
            LaggedStart(*[
                LaggedStart(*[FadeIn(slab, 0.3 * UP) for slab in slabs], lag_ratio=0.15) for slabs in slab_lists
            ], lag_ratio=0.18),
            LaggedStart(*[FadeIn(label) for label in labels], lag_ratio=0.18),
            run_time=2.0,
        )
        self.wait(0.4)

        # Each cube is unstacked and laid flat around the square so far
        placed = []
        floor = VGroup()
        floor_labels = VGroup()
        for k, cube in zip(range(1, N + 1), slab_lists):
            tiles = gnomon_tiles(k)
            color = COLORS[k - 1]
            # Lift the slabs apart first, so the slicing reads
            if k > 1:
                self.play(*[
                    slab.animate.shift(0.07 * i * UP) for i, slab in enumerate(cube)
                ], run_time=0.45)
            # Top slab first: pieces taken off the stack in reverse
            pieces = list(cube)
            order = [*range(len(tiles))]
            moves = []
            for piece_index, tile_index in zip(reversed(range(len(pieces))), reversed(order)):
                x0, y0, dx, dy = tiles[tile_index]
                target = box(x0, y0, 0, dx, dy, 1, color, offset=FLOOR_OFFSET)
                moves.append(Transform(pieces[piece_index], target, path_arc=-20 * DEG))
                placed.append((tiles[tile_index], color))
            s = tri(k - 1)
            label = Tex(str(k), font_size=36).set_color(interpolate_color(color, WHITE, 0.25))
            label.move_to(iso(s + k / 2, -1.25, 0) + FLOOR_OFFSET)
            floor_labels.add(label)
            self.play(
                LaggedStart(*moves, lag_ratio=0.35),
                FadeIn(label),
                labels[k - 1].animate.set_opacity(0.35),
                run_time=1.0 + 0.3 * k,
            )
            # Swap the landed pieces for the same floor, drawn sides first and tops last
            self.remove(floor, *pieces)
            floor = flat_floor(placed)
            self.add(floor)
            self.wait(0.25)

        # The whole square: side 1 + 2 + 3 + 4 + 5
        self.play(FadeOut(labels, 0.2 * UP), run_time=0.5)
        cubes_sum = Tex(R"1^3 + 2^3 + 3^3 + 4^3 + 5^3", font_size=60)
        side_sum = Tex(R"= (1 + 2 + 3 + 4 + 5)^2", font_size=60)
        for line, pattern in ((cubes_sum, "{}^3"), (side_sum, "{}")):
            for k in range(1, N + 1):
                part = line[pattern.format(k)]
                (part[0] if pattern == "{}" else part).set_color(COLORS[k - 1])
        side_sum[")^2"].set_color(WHITE)
        identity = VGroup(cubes_sum, side_sum).arrange(DOWN, buff=0.3).move_to(5.35 * DOWN)
        rim = VGroup(
            Line(iso(0, 0, 0), iso(tri(N), 0, 0)), Line(iso(0, 0, 1), iso(0, tri(N), 1)),
        ).shift(FLOOR_OFFSET).set_stroke(YELLOW, 5)
        self.play(ShowCreation(rim), run_time=0.8)
        self.play(Write(cubes_sum), run_time=1.1)
        self.play(
            TransformFromCopy(floor_labels, VGroup(*[side_sum[str(k)][0] for k in range(1, N + 1)])),
            Write(side_sum),
            run_time=1.2,
        )
        self.play(FlashAround(identity, color=YELLOW, time_width=1.5), FadeOut(rim), run_time=1.3)
        self.wait(1.5)
