from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/conic_sections.py
#
# A double cone x^2 + y^2 = k^2 z^2 (|z| <= H) cut by a plane through Q,
# spanned by u = (1, 0, 0) and v = (0, cos phi, sin phi).  In plane coordinates
# (s, t) the section is |s| <= w(t) with
#   w(t)^2 = k^2 (Qz + t sin phi)^2 - (Qy + t cos phi)^2,
# so the true shape of the cut is drawn straight from w, and the same points
# mapped back to space give the cut on the cone.
#   phi = 0                      circle
#   0 < phi < 90 - alpha         ellipse    (tan alpha = k, the half angle)
#   phi = 90 - alpha             parabola   (plane parallel to a side)
#   phi > 90 - alpha             hyperbola  (both nappes)
# Colours follow the reference picture.

K = 0.6                                  # radius / height of the cone
H = 2.6                                  # half height
ALPHA = np.arctan(K)
PHI_PARABOLA = PI / 2 - ALPHA
PLANE_S, PLANE_T = 2.1, 2.7              # half sizes of the drawn plane

APEX = 1.0 * UP                         # the apex on screen
PANEL = 3.75 * DOWN

CONE = "#E6EDF5"
CONE_FILL = "#58C4DD"
PLANE = "#8FD3FF"
CIRCLE = "#FF5C5C"
ELLIPSE = "#FFE14D"
PARABOLA = "#3DDC5A"
HYPERBOLA = "#5B9BFF"


def section_runs(q, phi, samples=500):
    """The cut as runs of (t, w(t)), one run per connected piece."""
    ts = np.linspace(-PLANE_T, PLANE_T, samples)
    z = q[2] + ts * np.sin(phi)
    y = q[1] + ts * np.cos(phi)
    w2 = (K * z) ** 2 - y ** 2
    ok = (w2 >= 0) & (np.abs(z) <= H)
    runs, current = [], []
    for t, good, value in zip(ts, ok, w2):
        if good:
            current.append((t, np.sqrt(max(value, 0))))
        elif current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    return [r for r in runs if len(r) > 3]


def hull(points):
    """Convex hull of screen points (monotone chain), counterclockwise."""
    pts = sorted(map(tuple, np.round(np.array(points)[:, :2], 6)))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return [np.array([x, y, 0]) for x, y in lower[:-1] + upper[:-1]]


def outline(run):
    """Closed outline of one run, in plane coordinates (s, t)."""
    right = [(w, t) for t, w in run]
    left = [(-w, t) for t, w in reversed(run)]
    return right + left


class ConicSections(BrandOutroMixin, ShortsScene):
    """Circle, ellipse, parabola and hyperbola as plane cuts of a double cone."""

    sections = ["cone", "circle", "ellipse", "parabola", "hyperbola", "gallery", "outro"]

    # The camera: a turn about the axis and a small tilt from above

    def view(self):
        if not hasattr(self, "_view"):
            self._view = [ValueTracker(-25), ValueTracker(14), ValueTracker(1.12)]
            self._plane = [ValueTracker(0.0), ValueTracker(H + 1.2), ValueTracker(0.0)]   # Qy, Qz, phi
            self._plane_on = ValueTracker(0)
        return self._view

    def sp(self, p):
        turn, tilt, zoom = [t.get_value() for t in self.view()]
        a, e = turn * DEGREES, tilt * DEGREES
        x, y, z = p
        u = x * np.cos(a) - y * np.sin(a)
        w = x * np.sin(a) + y * np.cos(a)
        return APEX + zoom * (u * RIGHT + (z * np.cos(e) + w * np.sin(e)) * UP)

    def plane_state(self):
        self.view()
        qy, qz, phi = [t.get_value() for t in self._plane]
        return np.array([0.0, qy, qz]), phi

    def in_space(self, s, t):
        q, phi = self.plane_state()
        return q + s * np.array([1, 0, 0]) + t * np.array([0, np.cos(phi), np.sin(phi)])

    def section_color(self):
        q, phi = self.plane_state()
        if phi < 0.5 * DEGREES:
            return CIRCLE
        if phi < 8 * DEGREES:
            return interpolate_color(CIRCLE, ELLIPSE, (phi / DEGREES - 0.5) / 7.5)
        if phi < PHI_PARABOLA - 3 * DEGREES:
            return ELLIPSE
        if phi < PHI_PARABOLA + 0.5 * DEGREES:
            mix = np.clip((phi - (PHI_PARABOLA - 3 * DEGREES)) / (3 * DEGREES), 0, 1)
            return interpolate_color(ELLIPSE, PARABOLA, mix)
        mix = np.clip((phi - PHI_PARABOLA - 0.5 * DEGREES) / (6 * DEGREES), 0, 1)
        return interpolate_color(PARABOLA, HYPERBOLA, mix)

    # Pieces

    def make_cone(self):
        def rim(z):
            return [np.array([K * abs(z) * np.cos(a), K * abs(z) * np.sin(a), z]) for a in np.linspace(0, TAU, 90)]

        def nappe(z):
            points = [self.sp(p) for p in rim(z)]
            apex = self.sp((0, 0, 0))
            angles = [angle_of_vector(p - apex) for p in points]
            left, right = points[int(np.argmax(angles))], points[int(np.argmin(angles))]
            ring = VMobject().set_points_smoothly(points).set_stroke(CONE, 3)
            sides = VGroup(Line(apex, left), Line(apex, right)).set_stroke(CONE, 3)
            body = Polygon(*hull([apex, *points]))
            body.set_stroke(width=0).set_fill(CONE_FILL, 0.07)
            return VGroup(body, ring, sides)

        cone = always_redraw(lambda: VGroup(nappe(H), nappe(-H)))
        axis = always_redraw(lambda: DashedLine(
            self.sp((0, 0, -H - 0.35)), self.sp((0, 0, H + 0.35)), dash_length=0.1,
        ).set_stroke(GREY_A, 1.5))
        return cone, axis

    def make_plane(self):
        def build():
            corners = [self.in_space(s, t) for s, t in
                       [(-PLANE_S, -PLANE_T), (PLANE_S, -PLANE_T), (PLANE_S, PLANE_T), (-PLANE_S, PLANE_T)]]
            on = self._plane_on.get_value()
            return Polygon(*[self.sp(c) for c in corners]).set_stroke(PLANE, 2, 0.6 * on).set_fill(PLANE, 0.13 * on)
        self.view()
        return always_redraw(build)

    def make_cut(self):
        def build():
            q, phi = self.plane_state()
            color = self.section_color()
            pieces = VGroup()
            for run in section_runs(q, phi):
                points = [self.sp(self.in_space(s, t)) for s, t in outline(run)]
                pieces.add(Polygon(*points).set_stroke(WHITE, 2).set_fill(color, 0.85))
            return pieces
        return always_redraw(build)

    def make_panel(self):
        """The cut laid flat: its true shape, fitted into the panel."""
        def build():
            q, phi = self.plane_state()
            runs = section_runs(q, phi)
            if not runs:
                return VGroup()
            shapes = VGroup(*[
                Polygon(*[np.array([s, t, 0]) for s, t in outline(run)]).set_stroke(WHITE, 2).set_fill(
                    self.section_color(), 0.85)
                for run in runs
            ])
            shapes.set_height(min(1.9, 1.9 * shapes.get_height() / max(shapes.get_height(), 1e-3)))
            if shapes.get_width() > 3.2:
                shapes.set_width(3.2)
            return shapes.move_to(PANEL + 1.3 * RIGHT)
        return always_redraw(build)

    def name(self, text, rule, color):
        title = Text(text, font_size=44, weight=BOLD).set_color(color)
        sub = Text(rule, font_size=24).set_color(GREY_A)
        group = VGroup(title, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        return group.move_to(PANEL + 1.9 * LEFT)

    def switch_name(self, text, rule, color):
        new = self.name(text, rule, color)
        old = self.lazy_state.get("name")
        if old is not None:
            self.play(FadeOut(old, 0.2 * UP), FadeIn(new, 0.2 * UP), run_time=0.5)
        else:
            self.play(FadeIn(new, 0.2 * UP), run_time=0.5)
        self.set_state("name", new)

    def get_all(self):
        def build():
            cone, axis = self.make_cone()
            plane, cut, panel = self.make_plane(), self.make_cut(), self.make_panel()
            self.add(cone, axis, plane, cut, panel)
            return VGroup(cone, axis, plane, cut, panel)
        return self.lazy("all", build)

    # Sections

    def cone(self):
        title = Text("Conic sections", font_size=52, weight=BOLD)
        subtitle = Text("cut a double cone with a plane", font_size=28).set_color(GREY_B)
        line = Line(LEFT, RIGHT).set_width(title.get_width() * 0.5).set_stroke(HYPERBOLA, 4)
        header = VGroup(title, line, subtitle).arrange(DOWN, buff=0.18).move_to(5.55 * UP)
        header.set_z_index(5)            # the tilted plane slides behind it
        self.play(FadeIn(title, 0.2 * DOWN), ShowCreation(line), FadeIn(subtitle), run_time=0.9)

        cone, axis = self.make_cone()
        turn = self.view()[0]
        self.play(ShowCreation(cone, lag_ratio=0.2), ShowCreation(axis), run_time=1.6)
        self.play(turn.animate.set_value(20), run_time=2.0)
        plane, cut, panel = self.make_plane(), self.make_cut(), self.make_panel()
        self.add(plane, cut, panel, cone, axis)
        self.set_state("all", VGroup(cone, axis, plane, cut, panel))
        self.set_state("header", header)

    def circle(self):
        self.get_all()
        qy, qz, phi = self._plane
        turn = self.view()[0]

        # A level plane slides down onto the upper nappe
        self.play(self._plane_on.animate.set_value(1), run_time=0.5)
        self.play(qz.animate.set_value(1.25), turn.animate.set_value(0), run_time=1.8)
        self.switch_name("Circle", "plane at right angles\nto the axis", CIRCLE)
        self.wait(1.3)

    def ellipse(self):
        self.get_all()
        qy, qz, phi = self._plane
        turn = self.view()[0]
        self.play(phi.animate.set_value(32 * DEGREES), turn.animate.set_value(-20), run_time=2.2)
        self.switch_name("Ellipse", "tilted, but less steep\nthan the cone's side", ELLIPSE)
        self.wait(1.3)

    def parabola(self):
        self.get_all()
        qy, qz, phi = self._plane
        turn = self.view()[0]
        self.play(phi.animate.set_value(PHI_PARABOLA), turn.animate.set_value(-35), run_time=2.2)

        # The plane runs parallel to one side of the cone
        side = always_redraw(lambda: Line(
            self.sp((0, 0, 0)), self.sp((0, K * H, H)),
        ).set_stroke(PARABOLA, 6))
        self.play(ShowCreation(side), run_time=0.7)
        self.switch_name("Parabola", "parallel to a side\nof the cone", PARABOLA)
        self.wait(1.3)
        self.play(FadeOut(side), run_time=0.4)

    def hyperbola(self):
        self.get_all()
        qy, qz, phi = self._plane
        turn = self.view()[0]
        self.play(
            phi.animate.set_value(88 * DEGREES), qy.animate.set_value(1.0), qz.animate.set_value(0.0),
            turn.animate.set_value(-15), run_time=2.6,
        )
        self.switch_name("Hyperbola", "steeper than the side:\nit cuts both cones", HYPERBOLA)
        self.wait(1.5)

    def gallery(self):
        everything = self.get_all()
        name = self.lazy_state.get("name")
        panel = everything[-1]

        # All four, side by side
        def branch(sign):
            return VMobject().set_points_as_corners([
                np.array([sign * 0.28 * np.cosh(u), 0.4 * np.sinh(u), 0]) for u in np.linspace(-1.3, 1.3, 40)
            ]).close_path()

        parabola = VMobject().set_points_as_corners([
            np.array([x, 1.3 * x * x, 0]) for x in np.linspace(-0.75, 0.75, 40)
        ]).close_path()
        shapes = VGroup(
            Circle(radius=0.42).set_fill(CIRCLE, 0.85),
            Ellipse(width=1.1, height=0.62).set_fill(ELLIPSE, 0.85),
            parabola.set_fill(PARABOLA, 0.85),
            VGroup(branch(1), branch(-1)).set_fill(HYPERBOLA, 0.85),
        )
        for shape in shapes:
            shape.set_stroke(WHITE, 2)
        names = ["Circle", "Ellipse", "Parabola", "Hyperbola"]
        colors = [CIRCLE, ELLIPSE, PARABOLA, HYPERBOLA]
        cards = VGroup(*[
            VGroup(shape.set_height(0.85), Text(n, font_size=24, weight=BOLD).set_color(c)).arrange(DOWN, buff=0.18)
            for shape, n, c in zip(shapes, names, colors)
        ]).arrange(RIGHT, buff=0.45).move_to(PANEL)
        panel.clear_updaters()
        self.play(FadeOut(panel), FadeOut(name), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(c, 0.2 * UP) for c in cards], lag_ratio=0.2), run_time=1.2)
        turn = self.view()[0]
        self.play(turn.animate.set_value(30), run_time=2.5)
        self.wait(1.0)
