from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/matrix/rotation_axes_matrices.py
#
# Three rotation matrices with exact entries, each turning a cube about its axis,
# all at the same time:
#   90 deg about the x-axis             e_y -> e_z, e_z -> -e_y
#   120 deg about the diagonal (1,1,1)  e_x -> e_y -> e_z -> e_x (a permutation matrix)
#   180 deg about (1,1,0)               e_x <-> e_y, e_z -> -e_z
# The columns of each matrix are the images of e_x, e_y, e_z.
#
# The 3D is projected by hand from a fixed view, so each panel keeps its own
# viewpoint.  The cube is convex, so hiding the faces that point away from the
# viewer is all the depth sorting it needs; lines and circles outside it are
# split into the parts behind the cube (drawn first) and in front (drawn last).

VIEW = normalize(np.array([1.0, -0.6, 0.6]))    # 40+ degrees from every spin axis
SCREEN_X = normalize(np.cross(OUT, VIEW))
SCREEN_Y = np.cross(VIEW, SCREEN_X)

HALF = 0.62                 # half the cube's side
RIM = HALF * np.sqrt(3)     # everything drawn outside this radius clears the cube
AXIS_LEN = 1.7
SPIN_AXIS_LEN = 1.95
RING = 1.42
PANEL_SCALE = 0.86
STEPS = 5                   # how many times each matrix is applied

FACE_COLORS = {
    (1, 0, 0): "#FF6B6B", (-1, 0, 0): "#FF9F43",
    (0, 1, 0): "#5BD98A", (0, -1, 0): "#58C4DD",
    (0, 0, 1): "#F2F2F7", (0, 0, -1): "#FFD166",
}
CUBE_BODY = "#14141C"

PANELS = [
    dict(
        axis=np.array([1.0, 0, 0]), angle=PI / 2, color="#FF7A6B",
        tex=R"R_{x}(90^\circ) = \begin{pmatrix} 1 & 0 & 0 \\ 0 & 0 & -1 \\ 0 & 1 & 0 \end{pmatrix}",
    ),
    dict(
        axis=np.array([1.0, 1, 1]), angle=2 * PI / 3, color="#FFC857",
        tex=R"R_{(1,1,1)}(120^\circ) = \begin{pmatrix} 0 & 0 & 1 \\ 1 & 0 & 0 \\ 0 & 1 & 0 \end{pmatrix}",
    ),
    dict(
        axis=np.array([1.0, 1, 0]), angle=PI, color="#5CC8FF",
        tex=R"R_{(1,1,0)}(180^\circ) = \begin{pmatrix} 0 & 1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & -1 \end{pmatrix}",
    ),
]
ROW_Y = [3.35, -0.55, -4.45]
MATRIX_X = -1.85
CUBE_X = 2.15


AXIS_NAMES = {}


def axis_name(label):
    """Axis letters are rebuilt every frame, so copy one typeset template each."""
    if label not in AXIS_NAMES:
        AXIS_NAMES[label] = Tex(label, font_size=24).set_color(GREY_A)
    return AXIS_NAMES[label].copy()


def flat(p):
    return (np.dot(p, SCREEN_X) * RIGHT + np.dot(p, SCREEN_Y) * UP) * PANEL_SCALE


def depth(p):
    return np.dot(p, VIEW)


def tip(end, direction, color, size=0.2):
    """A filled arrowhead at `end`, pointing along the screen direction `direction`."""
    direction = normalize(direction)
    side = rotate_vector(direction, PI / 2)
    return Polygon(end, end - size * direction + 0.45 * size * side, end - size * direction - 0.45 * size * side) \
        .set_stroke(width=0).set_fill(color, 1)


def split_path(points3d, color, width):
    """A 3D polyline split into (behind, in front) screen paths by the sign of its depth."""
    back, front = VGroup(), VGroup()
    run, run_front = [points3d[0]], depth(points3d[0]) > 0
    for p in points3d[1:]:
        is_front = depth(p) > 0
        run.append(p)
        if is_front != run_front:
            (front if run_front else back).add(VMobject().set_points_as_corners([flat(q) for q in run]))
            run, run_front = [p], is_front
    (front if run_front else back).add(VMobject().set_points_as_corners([flat(q) for q in run]))
    for group in (back, front):
        group.set_stroke(color, width)
    return back, front


def cube_faces(rot):
    """The stickers of the faces that point towards the viewer."""
    faces = VGroup()
    for normal, color in FACE_COLORS.items():
        n = np.array(normal, dtype=float)
        if depth(rot @ n) <= 0:
            continue
        # Two directions spanning the face
        u = np.array([n[1], n[2], n[0]])
        w = np.cross(n, u)
        corner = lambda a, b: rot @ (HALF * n + a * u + b * w)
        body = Polygon(*[flat(corner(a, b)) for a, b in [(-HALF, -HALF), (HALF, -HALF), (HALF, HALF), (-HALF, HALF)]])
        faces.add(body.set_stroke(CUBE_BODY, 1).set_fill(CUBE_BODY, 1))
        cell = 2 * HALF / 3
        gap = 0.1 * cell
        for i in range(3):
            for j in range(3):
                a0, b0 = -HALF + i * cell + gap, -HALF + j * cell + gap
                a1, b1 = a0 + cell - 2 * gap, b0 + cell - 2 * gap
                sticker = Polygon(*[flat(corner(a, b)) for a, b in [(a0, b0), (a1, b0), (a1, b1), (a0, b1)]])
                faces.add(sticker.set_stroke(color, 1.5).set_fill(color, 0.82))
    return faces


def build_panel(axis, angle, color, t):
    n = normalize(axis)
    rot = rotation_matrix(angle * t, n)
    back, front = VGroup(), VGroup()

    # The world axes, outside the cube
    for k, label in enumerate("xyz"):
        e = np.identity(3)[k]
        for sign in (1, -1):
            b, f = split_path([sign * RIM * e, sign * AXIS_LEN * e], WHITE, 2.5)
            back.add(b)
            front.add(f)
        end = AXIS_LEN * e
        head = tip(flat(end), flat(end) - flat(0.8 * end), WHITE, size=0.16)
        name = axis_name(label).move_to(flat(1.16 * end) + 0.02 * UP)
        (front if depth(e) > 0 else back).add(head, name)

    # The axis of rotation, and a ring around it turning the positive way
    b1, f1 = split_path([RIM * n, SPIN_AXIS_LEN * n], color, 5)
    b2, f2 = split_path([-SPIN_AXIS_LEN * n, -RIM * n], color, 5)
    head = tip(flat(SPIN_AXIS_LEN * n), flat(n), color, size=0.24)
    u1 = normalize(np.cross(n, np.array([0.3, -0.5, 0.8])))
    u2 = np.cross(n, u1)
    phis = np.linspace(0.25, 2 * PI - 0.55, 90)
    ring = [RING * (np.cos(p) * u1 + np.sin(p) * u2) for p in phis]
    rb, rf = split_path(ring, color, 5)
    ring_head = tip(flat(ring[-1]), flat(ring[-1]) - flat(ring[-3]), color, size=0.28)
    back.add(b1, b2, rb)
    front.add(f1, f2, rf)
    (front if depth(SPIN_AXIS_LEN * n) > 0 else back).add(head)
    (front if depth(ring[-1]) > 0 else back).add(ring_head)

    return VGroup(back, cube_faces(rot), front)


class RotationAxesMatrices(BrandOutroMixin, ShortsScene):
    """Three rotation matrices about different axes, turning three cubes at once."""

    sections = ["spin", "outro"]

    def spin(self):
        title = Tex(R"\text{3D Rotation Matrices}", font_size=62).move_to(6.3 * UP)
        line = Line(LEFT, RIGHT).set_width(5.2).set_stroke(GREY_B, 2).next_to(title, DOWN, buff=0.2)

        t = ValueTracker(0)
        boxes, cubes = VGroup(), VGroup()
        for panel, y in zip(PANELS, ROW_Y):
            color = panel["color"]
            matrix = Tex(panel["tex"], font_size=40).set_color(color).set_max_width(3.25)
            box = SurroundingRectangle(matrix, buff=0.28).round_corners(0.2)
            box.set_stroke(color, 3).set_fill(color, 0.08)
            boxes.add(VGroup(box, matrix).move_to([MATRIX_X, y, 0]))

            center = np.array([CUBE_X, y, 0])
            cube = always_redraw(
                lambda p=panel, c=center: build_panel(p["axis"], p["angle"], p["color"], t.get_value()).shift(c)
            )
            cubes.add(cube)

        self.play(
            Write(title), ShowCreation(line),
            LaggedStart(*[FadeIn(b, 0.2 * RIGHT) for b in boxes], lag_ratio=0.2),
            LaggedStart(*[FadeIn(c) for c in cubes], lag_ratio=0.2),
            run_time=1.2,
        )
        self.wait(0.3)

        # Apply every matrix at once, several times over
        for k in range(STEPS):
            self.play(
                t.animate.set_value(k + 1),
                *[
                    UpdateFromAlphaFunc(b[0], lambda m, a: m.set_stroke(width=3 + 3 * there_and_back(a)))
                    for b in boxes
                ],
                run_time=1.45,
            )
            self.wait(0.25)
        self.wait(0.5)
