from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/cube_in_sphere.py
#
# A cube of edge 4 hangs with one vertical edge PQ on the sphere's vertical
# axis: P, the bottom of that edge, is the sphere's lowest point, and V, the
# top vertex diagonally opposite Q, is also on the sphere.
#   OP = R, PQ = 4, so OQ = R - 4 (vertical)
#   QV = face diagonal = sqrt(4^2 + 4^2) = 4 sqrt 2 (horizontal)
#   OV = R, so (R - 4)^2 + (4 sqrt 2)^2 = R^2  ->  8R = 48  ->  R = 6.
# Check: V = (-4, -4, -2) is sqrt(16 + 16 + 4) = 6 from O.
#
# Drawn with a hand-rolled projection (turn, tilt, zoom and a look-at point)
# so the camera can spin the figure, look down on the top face, and turn
# side-on to the triangle OQV.

R = 6.0
EDGE = 4.0
O = np.array([0.0, 0.0, 0.0])
P = np.array([0.0, 0.0, -R])                 # lowest point of the sphere
Q = np.array([0.0, 0.0, -R + EDGE])          # top of the edge on the axis
V = np.array([-EDGE, -EDGE, -R + EDGE])      # opposite top vertex, on the sphere

CUBE = {
    (i, j, k): np.array([-EDGE * i, -EDGE * j, -R + EDGE * k])
    for i in (0, 1) for j in (0, 1) for k in (0, 1)
}
CUBE_EDGES = [
    (a, b) for a in CUBE for b in CUBE
    if a < b and sum(x != y for x, y in zip(a, b)) == 1
]

FIG_CENTER = 0.55 * UP
VIEWS = {  # turn, tilt, zoom, look-at point
    "start": (-20, 16, 0.5, (0, 0, 0)),
    "top": (-45, 88, 0.8, (-2, -2, -2)),
    "side": (-45, 0, 0.9, (-1.94, -1.94, -2.5)),
}

SPHERE = "#58C4DD"
CUBE_COLOR = "#FF9F43"
ON_SPHERE = YELLOW
RADIUS = YELLOW
HEIGHT = "#7FB3FF"
DIAGONAL = "#FF6BD6"
TRIANGLE = "#5BD98A"


class CubeInSphere(MockTestShort):
    """The radius of a sphere through two vertices of a cube, by Pythagoras."""

    test = ""
    card_top_buff = 0.6
    step_buff = 0.34

    problem_tex = (
        R"\text{A cube of edge } 4 \text{ and a sphere: two}\\"
        R"\text{vertices of the cube lie on the sphere.}\\"
        R"\text{Find the radius } R."
    )

    sections = ["pose", "build", "height", "diagonal", "triangle", "solve", "outro"]

    def make_card(self):
        card = super().make_card()
        card.set_z_index(10)             # the zoomed sphere slides behind it
        self.steps_top_y = -3.35
        return card

    # The camera

    def cam(self):
        if not hasattr(self, "_cam"):
            turn, tilt, zoom, look = VIEWS["start"]
            self._cam = [ValueTracker(turn), ValueTracker(tilt), ValueTracker(zoom),
                         *[ValueTracker(c) for c in look]]
            self._sphere_opacity = ValueTracker(1)
        return self._cam

    def project(self, p):
        turn, tilt, zoom, lx, ly, lz = [t.get_value() for t in self.cam()]
        a, e = turn * DEGREES, tilt * DEGREES

        def flat(q):
            x, y, z = q
            u = x * np.cos(a) - y * np.sin(a)
            w = x * np.sin(a) + y * np.cos(a)
            return np.array([u, z * np.cos(e) + w * np.sin(e)]), w * np.cos(e) - z * np.sin(e)

        xy, depth = flat(p)
        look, _ = flat((lx, ly, lz))
        return FIG_CENTER + zoom * np.array([*(xy - look), 0]), depth

    def sp(self, p):
        return self.project(p)[0]

    def view(self, name, run_time=2.0, *extra):
        turn, tilt, zoom, look = VIEWS[name]
        targets = [turn, tilt, zoom, *look]
        self.play(*[t.animate.set_value(v) for t, v in zip(self.cam(), targets)], *extra, run_time=run_time)

    def seg(self, a, b, color, width=4, dashed=False):
        def build():
            line = DashedLine(self.sp(a), self.sp(b), dash_length=0.08) if dashed else Line(self.sp(a), self.sp(b))
            return line.set_stroke(color, width)
        return always_redraw(build)

    def dot(self, p, color, radius=0.08):
        return always_redraw(lambda: VGroup(
            Dot(self.sp(p), radius=radius * 2.2).set_fill(color, 0.2),
            Dot(self.sp(p), radius=radius).set_fill(color).set_stroke(BLACK, 1),
        ))

    def tag(self, tex, point, offset, color=WHITE, font_size=32):
        """A label that follows a point of space, nudged on screen."""
        label = Tex(tex, font_size=font_size).set_color(color)
        label.add_updater(lambda m: m.move_to(self.sp(point() if callable(point) else point) + offset))
        return label.update()

    # Pieces

    def make_sphere(self):
        def build():
            center = self.sp(O)
            zoom = self.cam()[2].get_value()
            k = self._sphere_opacity.get_value()
            outline = Circle(radius=R * zoom).move_to(center).set_stroke(SPHERE, 3, k).set_fill(SPHERE, 0.06 * k)
            ring = [self.project(np.array([R * np.cos(t), R * np.sin(t), 0])) for t in np.linspace(0, TAU, 121)]
            front = VGroup(*[
                Line(ring[i][0], ring[i + 1][0]).set_stroke(SPHERE, 2, k)
                for i in range(120) if ring[i][1] <= 0
            ])
            back = VGroup(*[
                Line(ring[i][0], ring[i + 1][0]).set_stroke(SPHERE, 2, 0.5 * k)
                for i in range(0, 120, 2) if ring[i][1] > 0
            ])
            return VGroup(outline, back, front)
        return always_redraw(build)

    def make_cube(self):
        def build():
            tilt = self.cam()[1].get_value()
            hidden = max(CUBE, key=lambda k: self.project(CUBE[k])[1]) if 3 < tilt < 85 else None
            lines = VGroup()
            for a, b in CUBE_EDGES:
                if hidden in (a, b):
                    lines.add(DashedLine(self.sp(CUBE[a]), self.sp(CUBE[b]), dash_length=0.08).set_stroke(CUBE_COLOR, 2, 0.6))
                else:
                    lines.add(Line(self.sp(CUBE[a]), self.sp(CUBE[b])).set_stroke(CUBE_COLOR, 4))
            return lines
        return always_redraw(build)

    def get_scene_parts(self):
        def build():
            parts = dict(
                sphere=self.make_sphere(), cube=self.make_cube(),
                axis=self.seg(O, P, WHITE, 2.5), center=self.dot(O, WHITE, 0.07),
                o_name=self.tag("O", O, 0.25 * UR),
                touch=VGroup(self.dot(P, ON_SPHERE), self.dot(V, ON_SPHERE)),
                touch_names=VGroup(self.tag("P", P, 0.3 * DR, ON_SPHERE), self.tag("V", V, 0.3 * LEFT, ON_SPHERE)),
            )
            self.add(*parts.values())
            return parts
        return self.lazy("parts", build)

    # Sections

    def build(self):
        self.get_card()
        sphere, cube = self.make_sphere(), self.make_cube()
        axis = self.seg(O, P, WHITE, 2.5)
        center = self.dot(O, WHITE, 0.07)
        o_name = self.tag("O", O, 0.25 * UR)
        self.play(ShowCreation(sphere), FadeIn(center), FadeIn(o_name), run_time=1.4)
        self.play(ShowCreation(axis), run_time=0.6)
        self.play(ShowCreation(cube, lag_ratio=0.1), run_time=1.3)

        # One slow turn, to see it as a solid
        turn = self.cam()[0]
        self.play(turn.animate.increment_value(360), run_time=4.5, rate_func=smooth)

        touch = VGroup(self.dot(P, ON_SPHERE), self.dot(V, ON_SPHERE))
        touch_names = VGroup(self.tag("P", P, 0.3 * DR, ON_SPHERE), self.tag("V", V, 0.3 * LEFT, ON_SPHERE))
        self.play(FadeIn(touch, scale=0.4), FadeIn(touch_names), run_time=0.7)
        self.play(*[Flash(self.sp(p), color=ON_SPHERE, flash_radius=0.3) for p in (P, V)], run_time=0.8)
        self.note("The two vertices on the sphere: P at the\nvery bottom, and V diagonally across the top.", wait=1.5)
        self.set_state("parts", dict(sphere=sphere, cube=cube, axis=axis, center=center, o_name=o_name,
                                     touch=touch, touch_names=touch_names))

    def height(self):
        parts = self.get_scene_parts()

        # Down the axis: O to P is a radius, P to Q is an edge
        op = self.seg(O, P, RADIUS, 6)
        r_label = self.tag("R", (O + P) / 2, 0.35 * RIGHT, RADIUS)
        self.play(ShowCreation(op), FadeIn(r_label), run_time=0.9)
        self.note("P is the lowest point of the sphere: OP = R.", wait=1.1)

        q_dot = self.dot(Q, WHITE, 0.07)
        q_name = self.tag("Q", Q, 0.3 * RIGHT)
        pq = self.seg(Q, P, CUBE_COLOR, 7)
        oq = self.seg(O, Q, HEIGHT, 7)
        four = self.tag("4", (Q + P) / 2, 0.35 * RIGHT, CUBE_COLOR)
        rest = self.tag("R - 4", (O + Q) / 2, 0.55 * RIGHT, HEIGHT, 30)
        self.play(FadeOut(op), FadeOut(r_label), FadeIn(q_dot), FadeIn(q_name), run_time=0.5)
        self.play(ShowCreation(pq), FadeIn(four), run_time=0.7)
        self.play(ShowCreation(oq), FadeIn(rest), run_time=0.7)
        self.add_step(R"OQ = OP - PQ = R - 4", color=HEIGHT, wait=0.8)
        self.set_state("height", VGroup(q_dot, q_name, pq, oq, four, rest))

    def diagonal(self):
        parts = self.get_scene_parts()
        height = self.lazy("height", VGroup)

        # Look straight down on the top face; the labels stacked on the axis would pile up
        stacked = VGroup(height[4], height[5], parts["touch_names"][0])
        self.play(FadeOut(stacked), run_time=0.3)
        self.view("top", 2.2, self._sphere_opacity.animate.set_value(0.15))
        top_face = always_redraw(lambda: Polygon(*[
            self.sp(CUBE[k]) for k in [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
        ]).set_stroke(width=0).set_fill(CUBE_COLOR, 0.28))
        diag = self.seg(Q, V, DIAGONAL, 7)
        sides = VGroup(
            self.tag("4", (CUBE[(0, 0, 1)] + CUBE[(1, 0, 1)]) / 2, 0.3 * DOWN, CUBE_COLOR),
            self.tag("4", (CUBE[(1, 0, 1)] + CUBE[(1, 1, 1)]) / 2, 0.3 * LEFT, CUBE_COLOR),
        )
        diag_label = self.tag(R"4\sqrt{2}", (Q + V) / 2, 0.4 * UR, DIAGONAL)
        self.play(FadeIn(top_face), FadeIn(sides), run_time=0.6)
        self.play(ShowCreation(diag), FadeIn(diag_label), run_time=0.9)
        self.add_step(R"QV = \sqrt{4^2 + 4^2} = 4\sqrt{2}", color=DIAGONAL, wait=0.4)
        self.note("Seen from above: the diagonal of the top face.", wait=1.1)
        self.play(FadeOut(sides), run_time=0.3)
        self.set_state("diagonal", VGroup(top_face, diag, diag_label))

    def triangle(self):
        parts = self.get_scene_parts()
        height = self.lazy("height", VGroup)

        # Turn side-on: O, Q and V now lie in the screen
        self.cam()
        stacked = VGroup(height[4], height[5], parts["touch_names"][0])
        self.view("side", 2.4, self._sphere_opacity.animate.set_value(1), FadeIn(stacked))
        tri = always_redraw(lambda: Polygon(self.sp(O), self.sp(Q), self.sp(V)).set_stroke(width=0).set_fill(TRIANGLE, 0.28))
        ov = self.seg(O, V, RADIUS, 6)
        r_label = self.tag("R", (O + V) / 2, 0.35 * UL, RADIUS, 36)
        corner = always_redraw(lambda: VMobject().set_points_as_corners([
            self.sp(Q + 0.55 * np.array([0, 0, 1])),
            self.sp(Q + 0.55 * np.array([0, 0, 1]) + 0.55 * (V - Q) / np.linalg.norm(V - Q)),
            self.sp(Q + 0.55 * (V - Q) / np.linalg.norm(V - Q)),
        ]).set_stroke(WHITE, 2.5))
        self.add(tri, parts["axis"], *height, *self.lazy("diagonal", VGroup))
        self.play(FadeIn(tri), ShowCreation(ov), FadeIn(r_label), ShowCreation(corner), run_time=1.1)
        self.note("V is on the sphere: OV = R. Triangle OQV\nhas a right angle at Q.", wait=1.5)
        self.set_state("triangle", VGroup(tri, ov, r_label, corner))

    def solve(self):
        steps = self.steps()
        if len(steps) >= 2:
            self.play(FadeOut(VGroup(*steps)), run_time=0.4)
            steps.set_submobjects([])
        line = self.add_step(R"(R-4)^2 + (4\sqrt{2})^2 = R^2", font_size=42, wait=0.6)
        line = self.replace_step(line, R"R^2 - 8R + 16 + 32 = R^2", font_size=42, wait=0.6)
        self.replace_step(line, R"8R = 48", font_size=42, wait=0.4)
        self.conclude(R"R = 6", font_size=54, wait=0.6)

        # Back out and around, with the answer in place
        self.view("start", 2.2)
        self.play(self.cam()[0].animate.increment_value(120), run_time=2.5, rate_func=smooth)
        self.wait(0.8)
