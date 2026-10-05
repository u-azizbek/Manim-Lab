from manim_imports_ext import *
from scipy.spatial.transform import Rotation


# Render with:
#   ./render.sh _2026/Series/sum_of_squares.py
#
# 1^2 + 2^2 + ... + n^2 = (1/3) n (n+1) (n + 1/2), without words (after Man-Keung Siu).
# A staircase pyramid of square layers n^2, (n-1)^2, ..., 1^2 holds the sum.
# Three copies fit (found by exhaustive search, n = 4) into the (n+1) x n x n
# box topped by the staircase of cells x > y:
#   A = (4, 3, 0) + (-i, -j,  k)   flat, turned half a turn about the vertical
#   B = (4, 0, 4) + (-j,  k, -i)   on its side, facing front; its top row is the staircase
#   C = (0, 3, 3) + ( k, -i, -j)   on its side, facing left
# for the cells i, j >= 0, max(i, j) + k <= n - 1.  Cut the staircase at height
# n + 1/2 and turn the upper half a half turn about the vertical: cell (x, y)
# lands on (n - x, n - 1 - y), exactly the empty cells x <= y.  The result is
# a flat (n+1) x n x (n + 1/2) box, so 3 (1^2 + ... + n^2) = n (n+1) (n + 1/2).
#
# The cubes are drawn by hand: each face is a dark quad with the coloured quad
# inset on it (fills only, so drawing order is exactly painter's order), and
# cubes are sorted back to front every frame.

N = 4
PIECE_COLORS = ["#5A96EE", "#F2B90F", "#1FD01F"]      # A, B, C
BOX_CENTER = np.array([(N + 1) / 2, N / 2, (N + 1) / 2])
SCREEN_CENTER = np.array([0, 0.3, 0])

VIEW = normalize(np.array([0.5, -1.0, 0.62]))
SCREEN_UP = normalize(OUT - np.dot(OUT, VIEW) * VIEW)
SCREEN_RIGHT = np.cross(SCREEN_UP, VIEW)
LIGHT = normalize(np.array([-0.35, -0.7, 1.0]))

LOCAL = np.array([(i, j, k) for k in range(N) for i in range(N - k) for j in range(N - k)], dtype=float)
FINAL = [  # corner, rotation (columns = where the local axes go)
    (np.array([4, 3, 0]), np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]]).T),
    (np.array([4, 0, 4]), np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0]]).T),
    (np.array([0, 3, 3]), np.array([[0, -1, 0], [0, 0, -1], [1, 0, 0]]).T),
]
FACES = [(np.array(n, dtype=float), idx) for n, idx in [
    ((1, 0, 0), [1, 3, 7, 5]), ((-1, 0, 0), [0, 4, 6, 2]),
    ((0, 1, 0), [2, 6, 7, 3]), ((0, -1, 0), [0, 1, 5, 4]),
    ((0, 0, 1), [4, 5, 7, 6]), ((0, 0, -1), [0, 2, 3, 1]),
]]
CORNERS = np.array([(x, y, z) for z in (-1, 1) for y in (-1, 1) for x in (-1, 1)], dtype=float)


EDGE_RGBA = np.array([0.0, 0.0, 0.0, 1.0])


def shade(color, normal):
    light = 0.5 + 0.5 * max(np.dot(normal, LIGHT), 0)
    return np.array([*color_to_rgb(interpolate_color(BLACK, color, light)), 1.0])


def draw_boxes(boxes, scale, shift):
    """boxes: (centre, rotation, half sizes, colour) -> (quad, rgba) list, back to front.

    Each visible face is a dark quad with the coloured quad inset on it, so the
    cell edges come from fills alone and painter's order holds exactly.
    """
    quads = []
    for centre, rot, half, color in sorted(boxes, key=lambda b: np.dot(b[0], VIEW)):
        corners = centre + (CORNERS * half) @ rot.T - BOX_CENTER
        flat = SCREEN_CENTER + shift + scale * np.array([corners @ SCREEN_RIGHT, corners @ SCREEN_UP, 0 * corners[:, 0]]).T
        for normal, idx in FACES:
            n = rot @ normal
            if np.dot(n, VIEW) <= 0:
                continue
            quad = flat[idx]
            mid = quad.mean(axis=0)
            quads.append((quad, EDGE_RGBA))
            quads.append((mid + 0.86 * (quad - mid), shade(color, n)))
    return quads


class FaceCanvas(VGroup):
    """A fixed pool of quads repainted every frame; far cheaper than building new polygons."""

    def __init__(self, size=660):
        super().__init__(*[VMobject().set_stroke(width=0).set_fill(BLACK, 0) for _ in range(size)])

    def paint(self, quads):
        for mob, (quad, rgba) in zip(self.submobjects, quads):
            mob.set_points_as_corners([*quad, quad[0]])
            mob.set_rgba_array(rgba, name="fill_rgba")
        for mob in self.submobjects[len(quads):]:
            mob.set_points_as_corners([ORIGIN, ORIGIN + 1e-4 * RIGHT, ORIGIN])
            mob.set_rgba_array(np.zeros(4), name="fill_rgba")
        return self


class Piece:
    """One pyramid: canonical cells, turned and moved from a start pose to its place in the box."""

    def __init__(self, index):
        self.color = PIECE_COLORS[index]
        corner, rot = FINAL[index]
        self.centroid = LOCAL.mean(axis=0) + 0.5
        self.rotvec = Rotation.from_matrix(rot).as_rotvec()
        self.final_rot = rot
        self.final_pos = corner + 0.5 + rot @ (self.centroid - 0.5)
        self.start_pos = BOX_CENTER.copy()
        self.intro_shift = 1.2 * UP     # where the first pyramid is built
        self.spot = ORIGIN              # its place in the row of three
        self.spread = ValueTracker(0)
        self.t = ValueTracker(0)
        self.layers = ValueTracker(N)     # how many layers are shown, for building the first pyramid
        self.visible = True

    def pose(self):
        t = self.t.get_value()
        rot = Rotation.from_rotvec(t * self.rotvec).as_matrix()
        pos = interpolate(self.start_pos, self.final_pos, t) + 1.6 * np.sin(PI * t) * OUT
        start_shift = interpolate(self.intro_shift, self.spot, self.spread.get_value())
        shift = interpolate(start_shift, ORIGIN, smooth(t))
        return rot, pos, shift

    def boxes(self):
        if not self.visible:
            return [], ORIGIN
        rot, pos, shift = self.pose()
        shown = self.layers.get_value()
        cells = [c for c in LOCAL if c[2] < shown]
        return [(pos + rot @ (c + 0.5 - self.centroid), rot, 0.5 * np.ones(3), self.color) for c in cells], shift


class SumOfSquares(BrandOutroMixin, ShortsScene):
    """Three staircase pyramids make an n x (n+1) x (n+1/2) box."""

    sections = ["proof", "outro"]

    def proof(self):
        title = Text("Proof without words", font_size=58, weight=BOLD)
        title.set_color_by_gradient(*PIECE_COLORS).move_to(6.35 * UP)
        self.play(Write(title), run_time=1.0)

        pieces = [Piece(k) for k in range(3)]
        for p in pieces[1:]:
            p.visible = False
        scale = ValueTracker(0.8)
        flip = dict(active=False, angle=ValueTracker(0), lift=ValueTracker(0), static=[], moving=[])

        def build():
            if flip["active"]:
                return self.draw_flip(flip, scale.get_value())
            quads = []
            for p in pieces:
                boxes, shift = p.boxes()
                quads += draw_boxes(boxes, scale.get_value(), shift)
            return quads

        stage = FaceCanvas()
        stage.add_updater(lambda m: m.paint(build()))
        a = pieces[0]
        a.layers.set_value(0)
        self.add(stage)

        # One pyramid, layer by layer: 4^2, 3^2, 2^2, 1^2
        layer_labels = VGroup()
        for k in range(N):
            side = N - k
            label = Tex(Rf"{side}^2", font_size=40).set_color(interpolate_color(a.color, WHITE, 0.3))
            # Just left of the layer's front-left edge
            edge = a.start_pos + np.array([0, 0, k + 0.5]) - a.centroid + np.array([0, 0.5, 0])
            label.next_to(self.to_screen(edge, scale.get_value()) + a.intro_shift, LEFT, buff=0.3)
            layer_labels.add(label)
            self.play(a.layers.animate.set_value(k + 1), FadeIn(label, 0.2 * RIGHT), run_time=0.55)
        total = Tex(R"1^2 + 2^2 + 3^2 + 4^2", font_size=52).move_to(4.35 * DOWN)
        # Each layer's label flies down into the sum
        self.play(
            *[TransformFromCopy(label, total[Rf"{N - k}^2"][0], path_arc=30 * DEG) for k, label in enumerate(layer_labels)],
            FadeIn(total["+"]),
            run_time=1.1,
        )
        self.add(total)
        self.wait(0.5)

        # Three copies spread out
        spots = [np.array([0, -2.1, 0]), np.array([-2.05, 2.05, 0]), np.array([2.05, 2.05, 0])]
        for p, spot in zip(pieces, spots):
            p.spot = spot
            p.visible = True
        triple = Tex(R"3 \times (1^2 + 2^2 + 3^2 + 4^2)", font_size=52).move_to(total)
        self.play(
            FadeOut(layer_labels), scale.animate.set_value(0.58),
            *[p.spread.animate.set_value(1) for p in pieces],
            TransformMatchingTex(total, triple),
            run_time=1.3,
        )
        self.wait(0.4)

        # Each copy turns and slides into the box
        for p in (pieces[2], pieces[1], pieces[0]):
            self.play(p.t.animate.set_value(1), run_time=1.7)
        self.play(scale.animate.set_value(0.78), run_time=0.7)
        self.wait(0.3)

        # Cut the staircase at n + 1/2; the upper half turns over into the gaps
        for x in range(N + 1):
            for y in range(N):
                for z in range(N + 1):
                    owner = self.owner(x, y, z)
                    if owner is None:
                        continue
                    color = PIECE_COLORS[owner]
                    if z == N:
                        flip["static"].append((np.array([x + 0.5, y + 0.5, N + 0.25]), np.eye(3), np.array([0.5, 0.5, 0.25]), color))
                        flip["moving"].append((np.array([x + 0.5, y + 0.5, N + 0.75]), color))
                    else:
                        flip["static"].append((np.array([x + 0.5, y + 0.5, z + 0.5]), np.eye(3), 0.5 * np.ones(3), color))
        flip["scale"] = scale
        flip["active"] = True
        cut = self.cut_outline(scale.get_value())
        self.play(ShowCreation(cut), run_time=0.6)
        self.play(flip["lift"].animate.set_value(1.1), FadeOut(cut), run_time=0.6)
        self.play(flip["angle"].animate.set_value(PI), run_time=1.3)
        self.play(flip["lift"].animate.set_value(-0.5), run_time=0.7)

        # The box: (n+1) by n by (n + 1/2)
        dims = self.dimension_labels(scale.get_value())
        self.play(LaggedStart(*[FadeIn(d, 0.1 * DOWN) for d in dims], lag_ratio=0.25), run_time=1.0)
        product = Tex(R"3\,(1^2 + 2^2 + \cdots + n^2) = n\,(n+1)\,(n + \tfrac12)", font_size=46)
        product.set_max_width(7.4).move_to(triple)
        self.play(TransformMatchingTex(triple, product), run_time=1.2)
        self.wait(0.5)
        formula = Tex(R"1^2 + 2^2 + \cdots + n^2 = \tfrac13\, n\,(n+1)\,(n + \tfrac12)", font_size=48)
        formula.set_max_width(7.4).move_to(product)
        self.play(TransformMatchingTex(product, formula), run_time=1.2)
        box = SurroundingRectangle(formula, buff=0.2).set_stroke(YELLOW, 3)
        self.play(ShowCreation(box), FlashAround(formula, color=YELLOW, time_width=1.5), run_time=1.2)
        self.wait(1.5)
        stage.clear_updaters()

    # Helpers

    def owner(self, x, y, z):
        cell = np.array([x, y, z])
        for index, (corner, rot) in enumerate(FINAL):
            local = np.linalg.solve(rot, cell - corner)
            i, j, k = np.round(local).astype(int)
            if min(i, j, k) >= 0 and max(i, j) + k <= N - 1:
                return index
        return None

    def to_screen(self, p, scale):
        return SCREEN_CENTER + scale * np.array([np.dot(p - BOX_CENTER, SCREEN_RIGHT), np.dot(p - BOX_CENTER, SCREEN_UP), 0])

    def draw_flip(self, flip, scale):
        angle, lift = flip["angle"].get_value(), flip["lift"].get_value()
        rot = rotation_matrix(angle, OUT)
        axis = np.array([(N + 1) / 2, N / 2, 0])
        moving = [
            (axis + rot @ (c - axis) + (lift - 0) * OUT, rot, np.array([0.5, 0.5, 0.25]), color)
            for c, color in flip["moving"]
        ]
        return draw_boxes(flip["static"] + moving, scale, ORIGIN)

    def cut_outline(self, scale):
        z = N + 0.5
        corners = [(0, 0), (N + 1, 0), (N + 1, N), (0, N)]
        pts = [self.to_screen(np.array([x, y, z]), scale) for x, y in corners]
        return DashedLine(pts[0], pts[1], dash_length=0.1).set_stroke(WHITE, 3).add(
            DashedLine(pts[1], pts[2], dash_length=0.1).set_stroke(WHITE, 3)
        )

    def dimension_labels(self, scale):
        s = lambda p: self.to_screen(np.array(p, dtype=float), scale)
        h = N + 0.5
        width = Tex("n+1", font_size=40).next_to(s([(N + 1) / 2, 0, 0]), DOWN, buff=0.25)
        depth = Tex("n", font_size=40).next_to(s([N + 1, N / 2, 0]), DR, buff=0.12)
        height = Tex(R"n+\tfrac12", font_size=40).next_to(s([0, 0, h / 2]), LEFT, buff=0.2)
        return VGroup(width, depth, height).set_color(GREY_A)
