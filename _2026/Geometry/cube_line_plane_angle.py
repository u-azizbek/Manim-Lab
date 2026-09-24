from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/cube_line_plane_angle.py
#
# Cube ABCDA1B1C1D1 with K, P, M the midpoints of AD, DC, A1B1.  Find the
# angle between the line AA1 and the plane through K perpendicular to MP.
#
# With edge 1 and A at the origin: K(0, 1/2, 0), P(1/2, 1, 0), M(1/2, 0, 1).
# The plane is perpendicular to MP, so n = MP = (0, 1, -1) is its normal, and
# with s = AA1 = (0, 0, 1),  sin(phi) = |s.n| / (|s||n|) = 1/sqrt(2), phi = 45.
#
# The plane is y - z = 1/2.  It cuts the cube in the rectangle K, mid BC,
# mid CC1, mid DD1 (= Q), MP pierces it at the rectangle's centre, and it
# contains the x direction.  So seen along x it is edge-on as the segment KQ,
# and the angle is visible directly: DD1 is parallel to AA1 and meets the
# plane at Q, in the right isosceles triangle KDQ (DK = DQ = 1/2), so 45.
# (The foot of the perpendicular from D is the midpoint of KQ, so QK really
# is the projection of QD onto the plane.)
#
# The cube is drawn with a hand-rolled projection driven by a turn angle and a
# tilt, so it can spin and then swing round to that edge-on side view.

CUBE = {
    "A": (0, 0, 0), "B": (1, 0, 0), "C": (1, 1, 0), "D": (0, 1, 0),
    "A_1": (0, 0, 1), "B_1": (1, 0, 1), "C_1": (1, 1, 1), "D_1": (0, 1, 1),
}
EDGES = [
    ("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"),
    ("A_1", "B_1"), ("B_1", "C_1"), ("C_1", "D_1"), ("D_1", "A_1"),
    ("A", "A_1"), ("B", "B_1"), ("C", "C_1"), ("D", "D_1"),
]
POINTS = {
    **CUBE,
    "K": (0, 0.5, 0), "P": (0.5, 1, 0), "M": (0.5, 0, 1), "Q": (0, 1, 0.5),
}
CENTER = np.array([0.5, 0.5, 0.5])

FIG_CENTER = 0.95 * UP
VIEWS = {                  # (turn, tilt, size of one edge on screen)
    "oblique": (-25, 18, 2.45),
    "side": (-90, 0, 2.7),
}

EDGE_COLOR = "#D9E2EC"
PLANE = "#4FD1C5"
NORMAL = "#FF9F43"         # MP, and the normal vector n
LINE = "#FF6B9A"           # AA1, and its direction s
POINT = {"K": "#7FB3FF", "P": "#FFD166", "M": "#C39BFF"}
ANGLE = YELLOW
AXIS = "#8FB4E3"


def section(d):
    """The cube's cut by the plane y - z = d, as a rectangle."""
    y0, z0 = max(d, 0), max(-d, 0)
    y1, z1 = min(1, 1 + d), min(1, 1 - d)
    return [(0, y0, z0), (1, y0, z0), (1, y1, z1), (0, y1, z1)]


def pierce(d):
    """Where MP crosses the plane y - z = d."""
    t = (1 + d) / 2
    return np.array([0.5, t, 1 - t])


class CubeLinePlaneAngle(MockTestShort):
    """Angle between an edge of a cube and a plane given by its normal."""

    test = ""
    card_top_buff = 0.6
    step_buff = 0.34

    problem_tex = (
        R"\text{Cube } ABCDA_1B_1C_1D_1\\"
        R"K,\ P,\ M:\ \text{midpoints of}\\"
        R"AD,\ DC,\ A_1B_1\\"
        R"\text{Angle between } AA_1 \text{ and}\\"
        R"\text{the plane through } K \perp MP?"
    )

    sections = [
        "pose",
        "draw_cube",
        "build_plane",
        "coordinates",
        "vectors",
        "formula",
        "see_it",
        "finish",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = -1.5
        return card

    # The projection

    def trackers(self):
        if not hasattr(self, "_view"):
            self._view = [ValueTracker(v) for v in VIEWS["oblique"]]
            self._offset = ValueTracker(0.5)      # the plane is y - z = offset
        return self._view

    def turned(self, p):
        turn, tilt, size = [t.get_value() for t in self.trackers()]
        th, ph = turn * DEGREES, tilt * DEGREES
        x, y, z = np.array(p, dtype=float) - CENTER
        u = x * np.cos(th) - y * np.sin(th)
        w = x * np.sin(th) + y * np.cos(th)
        return u, z * np.cos(ph) + w * np.sin(ph), w * np.cos(ph) - z * np.sin(ph), size

    def sp(self, p):
        """A point of the cube on screen, from the current turn and tilt."""
        u, v, _, size = self.turned(p)
        return FIG_CENTER + size * (u * RIGHT + v * UP)

    def depth(self, p):
        return self.turned(p)[2]

    def at(self, name):
        return self.sp(POINTS[name])

    def view(self, name, run_time=2.0, *extra):
        self.play(
            *[t.animate.set_value(v) for t, v in zip(self.trackers(), VIEWS[name])],
            *extra,
            run_time=run_time,
        )

    def offset(self):
        self.trackers()
        return self._offset.get_value()

    def label(self, name, color=WHITE, font_size=30, buff=0.27):
        """A letter that stays just outside the cube however it turns."""
        tex = Tex(name, font_size=font_size).set_color(color)

        def place(m):
            spot = self.at(name)
            away = spot - self.sp(CENTER)
            m.move_to(spot + buff * (normalize(away) if get_norm(away) > 1e-3 else UP))

        tex.add_updater(place)
        return tex.update()

    def segment(self, p, q, color, width=6):
        return always_redraw(lambda: Line(self.sp(p), self.sp(q)).set_stroke(color, width))

    def dot(self, name, color, radius=0.075):
        return always_redraw(
            lambda: Dot(self.at(name), radius=radius).set_fill(color).set_stroke(BLACK, 1.5)
        )

    def corner_mark(self, at, dir1, dir2, size=0.1, color=WHITE):
        """A right-angle mark drawn in 3D, so it turns with the cube."""
        at, dir1, dir2 = map(np.array, (at, dir1, dir2))
        return VMobject().set_points_as_corners([
            self.sp(at + size * dir1),
            self.sp(at + size * (dir1 + dir2)),
            self.sp(at + size * dir2),
        ]).set_stroke(color, 2.5)

    # Pieces

    def make_cube(self):
        def edges():
            turn, tilt, size = [t.get_value() for t in self.trackers()]
            # From above, the one vertex facing away is hidden, with its edges
            hidden = max(CUBE, key=lambda n: self.depth(CUBE[n])) if tilt > 3 else None
            back = VGroup(*[
                DashedLine(self.at(a), self.at(b), dash_length=0.09).set_stroke(EDGE_COLOR, 2, 0.55)
                for a, b in EDGES if hidden in (a, b)
            ])
            front = VGroup(*[
                Line(self.at(a), self.at(b)).set_stroke(EDGE_COLOR, 3)
                for a, b in EDGES if hidden not in (a, b)
            ])
            return VGroup(back, front)

        cube = always_redraw(edges)
        cube.letter_of = {name: self.label(name) for name in CUBE}
        cube.letters = VGroup(*cube.letter_of.values())
        return cube

    def get_cube(self):
        def build():
            cube = self.make_cube()
            self.add(cube.letters)
            return cube
        return self.lazy("cube", build)

    def make_points(self):
        points = VGroup(*[self.dot(name, POINT[name]) for name in "KPM"])
        points.letters = VGroup(*[
            self.label(name, POINT[name], font_size=32) for name in "KPM"
        ])
        return points

    def get_points(self):
        def build():
            points = self.make_points()
            self.add(points.letters)
            return points
        return self.lazy("points", build)

    def make_plane(self):
        grow = ValueTracker(1)
        self.trackers()

        def rectangle():
            corners = [np.array(c) for c in section(self._offset.get_value())]
            anchor = np.array(POINTS["K"])
            s = grow.get_value()
            return Polygon(*[self.sp(anchor + s * (c - anchor)) for c in corners]).set_fill(
                PLANE, 0.32).set_stroke(PLANE, 3)

        plane = always_redraw(rectangle)
        plane.grow = grow
        plane.name = Tex(R"\alpha", font_size=38).set_color(PLANE)
        plane.name.add_updater(lambda m: m.move_to(
            self.sp((0.85, 0.5 + self._offset.get_value() + 0.4, 0.4))
        ))
        plane.name.update()
        return plane

    def get_plane(self):
        def build():
            plane = self.make_plane()
            self.add(plane.name)
            return plane
        return self.lazy("plane", build)

    def make_mp(self):
        mp = self.segment(POINTS["M"], POINTS["P"], NORMAL, 5)
        crossing = always_redraw(lambda: Dot(self.sp(pierce(self.offset())), radius=0.05).set_fill(WHITE))
        square = always_redraw(lambda: self.corner_mark(
            pierce(self.offset()), np.array([0, 1, -1]) / np.sqrt(2), np.array([0, 1, 1]) / np.sqrt(2), size=0.12,
        ))
        return VGroup(mp, crossing, square)

    def get_mp(self):
        return self.lazy("mp", self.make_mp)

    def get_line(self):
        return self.lazy("line", lambda: self.segment(CUBE["A"], CUBE["A_1"], LINE, 7))

    # Sections

    def draw_cube(self):
        self.get_card()
        cube = self.make_cube()
        self.play(ShowCreation(cube), run_time=1.3)
        self.play(FadeIn(cube.letters, lag_ratio=0.08), run_time=0.8)
        self.set_state("cube", cube)

        # The three edges, and their midpoints
        points = self.make_points()
        edges = VGroup(
            self.segment(CUBE["A"], CUBE["D"], POINT["K"]),
            self.segment(CUBE["D"], CUBE["C"], POINT["P"]),
            self.segment(CUBE["A_1"], CUBE["B_1"], POINT["M"]),
        )
        for edge, dot, letter in zip(edges, points, points.letters):
            self.play(ShowCreation(edge), run_time=0.35)
            self.play(FadeIn(dot, scale=0.5), FadeIn(letter), run_time=0.35)
        self.play(FadeOut(edges), run_time=0.4)
        self.set_state("points", points)

    def build_plane(self):
        cube = self.get_cube()
        self.get_points()

        # MP, then the plane through K that meets it square on
        mp = self.make_mp()
        self.play(ShowCreation(mp[0]), run_time=0.8)
        plane = self.make_plane()
        plane.grow.set_value(0)
        self.add(plane, cube, *self.lazy_state["points"])
        self.play(plane.grow.animate.set_value(1), FadeIn(mp[1:]), run_time=1.3)
        self.play(FadeIn(plane.name), run_time=0.4)
        self.set_state("plane", plane)
        self.set_state("mp", mp)

        line = self.get_line()
        self.add(line, *self.lazy_state["points"])
        self.play(ShowCreation(line), run_time=0.6)
        goal = self.add_step(
            R"\varphi = \angle(AA_1,\ \alpha) = \ ?",
            t2c={R"AA_1": LINE, R"\alpha": PLANE}, font_size=40, wait=0.2,
        )
        self.set_state("goal", goal)

        # One full turn, to see it as a solid
        turn = self.trackers()[0]
        self.play(turn.animate.increment_value(360), run_time=4.4)
        self.wait(0.3)

    def coordinates(self):
        self.get_cube()
        points = self.get_points()
        self.get_plane()
        self.get_mp()
        self.get_line()

        axes = VGroup(*[
            Arrow(self.at("A"), self.sp(end), buff=0).set_color(AXIS)
            for end in [(1.45, 0, 0), (0, 1.45, 0), (0, 0, 1.45)]
        ])
        axis_names = VGroup(*[
            Tex(name, font_size=32).set_color(AXIS).move_to(self.sp(spot))
            for name, spot in [("x", (1.62, 0, 0)), ("y", (0, 1.62, 0)), ("z", (0, 0, 1.6))]
        ])
        self.play(LaggedStartMap(GrowArrow, axes, lag_ratio=0.25), FadeIn(axis_names), run_time=0.9)
        self.note("Edge 1, A at the origin.\nA midpoint is the average of its ends.", wait=1.1)

        # Each midpoint's coordinates, read off the figure...
        coords = {
            "K": R"(0,\tfrac{1}{2},0)",
            "P": R"(\tfrac{1}{2},1,0)",
            "M": R"(\tfrac{1}{2},0,1)",
        }
        sides = {"K": LEFT, "P": RIGHT, "M": UP}
        tags = VGroup(*[
            Tex(coords[name], font_size=28).set_color(POINT[name]).next_to(
                points.letters[i], sides[name], buff=0.08)
            for i, name in enumerate("KPM")
        ])
        self.play(FadeIn(tags, lag_ratio=0.3), run_time=0.9)
        self.wait(0.5)

        # ...then collected into one line
        row = Tex(
            R"\quad ".join(name + coords[name] for name in "KPM"),
            isolate=list(coords.values()), font_size=36,
        )
        for name in "KPM":
            row[name].set_color(POINT[name])
            row[coords[name]].set_color(POINT[name])
        row.set_max_width(self.step_max_width)
        self.place_step(row)
        self.steps().add(row)
        self.play(
            *[ReplacementTransform(tag, row[coords[name]]) for tag, name in zip(tags, "KPM")],
            *[FadeIn(row[name]) for name in "KPM"],
            FadeOut(axis_names),
            FadeOut(axes),
            run_time=1.1,
        )
        self.wait(0.4)

    def vectors(self):
        self.get_cube()
        self.get_points()
        plane = self.get_plane()
        mp = self.get_mp()
        line = self.get_line()
        steps = self.steps()

        # The line's direction
        s_arrow = always_redraw(
            lambda: Arrow(self.at("A"), self.at("A_1"), buff=0, thickness=5).set_color(LINE)
        )
        self.play(FadeOut(line), FadeIn(s_arrow), run_time=0.5)
        self.add_step(R"\vec{s} = \overrightarrow{AA_1} = (0,0,1)", color=LINE, wait=0.4)

        # The plane's normal
        n_arrow = always_redraw(
            lambda: Arrow(self.at("M"), self.at("P"), buff=0, thickness=5).set_color(NORMAL)
        )
        self.play(FadeOut(mp[0]), FadeIn(n_arrow), run_time=0.5)
        self.note("The plane is perpendicular to MP,\nso MP is its normal vector.", wait=1.2)
        self.add_step(
            R"\vec{n} = \overrightarrow{MP} = P - M = (0,1,-1)", color=NORMAL, wait=0.4,
        )

        # K only says where the plane sits: sliding it never changes its tilt
        caption = Text("K fixes where the plane sits, not its tilt.", font_size=28)
        caption.set_color(self.note_color).set_max_width(self.step_max_width)
        self.place_step(caption)
        self.play(FadeIn(caption, 0.15 * DOWN), run_time=0.5)
        self.play(self._offset.animate.set_value(0.05), run_time=1.1)
        self.play(self._offset.animate.set_value(0.5), run_time=1.0)
        self.play(FadeOut(caption, 0.15 * UP), run_time=0.4)

        # The coordinates have done their job
        if len(steps) >= 3:
            self.play(
                FadeOut(steps[1]),
                VGroup(*steps[2:]).animate.shift(steps[1].get_top() - steps[2].get_top()),
                run_time=0.6,
            )
            steps.set_submobjects([steps[0], *steps[2:]])
        self.set_state("s_arrow", s_arrow)
        self.set_state("n_arrow", n_arrow)

    def formula(self):
        self.get_cube()
        self.get_points()
        self.get_plane()
        self.lazy("s_arrow", lambda: always_redraw(
            lambda: Arrow(self.at("A"), self.at("A_1"), buff=0, thickness=5).set_color(LINE)))
        self.lazy("n_arrow", lambda: always_redraw(
            lambda: Arrow(self.at("M"), self.at("P"), buff=0, thickness=5).set_color(NORMAL)))

        self.note("A line meets a plane at 90° minus its\nangle with the normal, so use sine.", wait=1.5)
        rule = self.add_step(
            R"\sin\varphi = \frac{|\vec{s}\cdot\vec{n}|}{|\vec{s}|\,|\vec{n}|}",
            font_size=40, wait=0.9,
        )
        self.replace_step(
            rule,
            R"\sin\varphi = \frac{|0+0-1|}{1\cdot\sqrt{2}} = \frac{1}{\sqrt{2}}",
            font_size=40, wait=1.0,
        )

    def see_it(self):
        cube = self.get_cube()
        self.get_points()
        plane = self.get_plane()
        mp = self.get_mp()
        s_arrow = self.lazy("s_arrow", VGroup)
        n_arrow = self.lazy("n_arrow", VGroup)

        # Carry AA1 over to DD1, which is parallel and actually meets the plane
        slide = ValueTracker(0)
        edge = always_redraw(lambda: Line(
            self.sp((0, slide.get_value(), 0)), self.sp((0, slide.get_value(), 1)),
        ).set_stroke(LINE, 7))
        self.add(edge)
        self.play(FadeOut(s_arrow), run_time=0.4)
        self.play(slide.animate.set_value(1), run_time=1.2)

        q_dot = self.dot("Q", ANGLE)
        q_name = self.label("Q", ANGLE, font_size=32)
        triangle = always_redraw(lambda: Polygon(
            self.at("D"), self.at("Q"), self.at("K"),
        ).set_fill(ANGLE, 0.28).set_stroke(ANGLE, 3))
        at_d = always_redraw(lambda: self.corner_mark(
            CUBE["D"], (0, 0, 1), (0, -1, 0), size=0.1, color=ANGLE,
        ))
        self.play(FadeIn(q_dot, scale=0.5), FadeIn(q_name), run_time=0.5)
        self.add(triangle, edge, cube, q_dot)
        self.play(FadeIn(triangle), ShowCreation(at_d), run_time=0.7)

        # Swing round until the plane is seen edge-on
        # Seen from the side the far face hides behind the near one, and P
        # and M sit on top of D and A1, so only the face x = 0 keeps its names
        points = self.get_points()
        dim = VGroup(
            *[cube.letter_of[name] for name in ("B", "C", "B_1", "C_1")],
            points[1:], points.letters[1:], plane.name, n_arrow, mp[1:],
        )
        self.view("side", 2.4, FadeOut(dim))

        halves = VGroup(
            Tex(R"\tfrac{1}{2}", font_size=32).set_color(ANGLE).next_to(
                midpoint(self.at("D"), self.at("Q")), RIGHT, buff=0.14),
            Tex(R"\tfrac{1}{2}", font_size=32).set_color(ANGLE).next_to(
                midpoint(self.at("D"), self.at("K")), DOWN, buff=0.14),
        )
        q, d, k = self.at("Q"), self.at("D"), self.at("K")
        start = angle_of_vector(d - q)
        arc = Arc(start_angle=start, angle=angle_of_vector(k - q) - start, radius=0.55, arc_center=q)
        arc.set_stroke(ANGLE, 4)
        degrees = Tex(R"45^\circ", font_size=34).set_color(ANGLE)
        degrees.move_to(q + 0.9 * normalize(rotate_vector(d - q, (angle_of_vector(k - q) - start) / 2)))
        self.play(FadeIn(halves, lag_ratio=0.3), run_time=0.6)
        self.play(ShowCreation(arc), FadeIn(degrees, scale=0.6), run_time=0.8)
        self.note("Edge-on, it is a right isosceles triangle.", wait=1.3)
        self.set_state("angle", VGroup(arc, degrees))

    def finish(self):
        self.get_card()
        goal = self.lazy("goal", lambda: self.add_step(
            R"\varphi = \angle(AA_1,\ \alpha) = \ ?", font_size=40, wait=0,
        ))
        angle = self.lazy("angle", VGroup)

        # The question line becomes the answer
        answer = self.replace_step(
            goal, R"\varphi = 45^\circ", color=RESULT_COLOR, font_size=52, wait=0.1,
        )
        box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.2).set_stroke(width=4)
        self.play(ShowCreation(box), Indicate(angle, color=RESULT_COLOR), run_time=0.7)
        self.play(FlashAround(answer, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.wait(1.2)
