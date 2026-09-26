from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/spheres_in_box.py
#
# An open 4 x 4 x h box holds a sphere of radius 2 and eight of radius 1.
# The small ones sit in the corners, four at the bottom and four at the top,
# centres (+-1, +-1, 1) and (+-1, +-1, h - 1); the big one sits in the middle
# at (0, 0, h/2) and touches all eight.
#   horizontal distance from the axis to a small centre:  sqrt(1 + 1) = sqrt 2
#   big centre to small centre:                            R + r = 3
#   so the vertical gap is sqrt(9 - 2) = sqrt 7, and
#   h = 1 + sqrt 7 + sqrt 7 + 1 = 2 + 2 sqrt 7  (about 7.29).
# Checked: every centre distance is 3, neighbouring small spheres are 2 apart,
# and the big sphere just reaches the side walls.

R_BIG, R_SMALL = 2.0, 1.0
DZ = np.sqrt(7)
H = 2 + 2 * DZ
MID = H / 2

BIG = np.array([0.0, 0.0, MID])
SMALL = [np.array([sx, sy, z]) for z in (1.0, H - 1) for sx in (-1, 1) for sy in (-1, 1)]
BOX = {(i, j, k): np.array([2 * i, 2 * j, H * k]) for i in (-1, 1) for j in (-1, 1) for k in (0, 1)}
BOX_EDGES = [(a, b) for a in BOX for b in BOX if a < b and sum(x != y for x, y in zip(a, b)) == 1]

FIG_CENTER = 1.05 * UP
VIEWS = {  # turn, tilt, zoom, look-at
    "start": (-30, 17, 0.6, (0, 0, MID)),
    "top": (0, 90, 0.95, (0, 0, MID)),
    "side": (-45, 0, 0.62, (0.4, 0.4, MID)),
    "close": (-45, 0, 0.85, (0.4, 0.4, 2.3)),
}

BIG_COLOR = "#58C4DD"
SMALL_COLOR = "#FF9F43"
BOX_COLOR = "#E6EDF5"
FLAT = "#5BD98A"          # the horizontal leg, sqrt 2
RISE = "#FF6BD6"          # the vertical leg, sqrt 7
LINK = YELLOW             # centre to centre, 3


class SpheresInBox(MockTestShort):
    """Height of a box holding one big and eight small spheres."""

    test = ""
    card_top_buff = 0.6
    step_buff = 0.34

    problem_tex = (
        R"\text{Open box } 4 \times 4 \times h:\\"
        R"\text{one sphere } R = 2,\ \text{eight spheres } r = 1.\\"
        R"\text{Small ones touch the walls,}\\"
        R"\text{the big one touches all eight. Find } h."
    )

    sections = ["pose", "build", "top_view", "contact", "triangle", "stack", "outro"]

    def make_card(self):
        card = super().make_card()
        card.set_z_index(10)
        self.steps_top_y = -2.35
        return card

    # The camera

    def cam(self):
        if not hasattr(self, "_cam"):
            turn, tilt, zoom, look = VIEWS["start"]
            self._cam = [ValueTracker(turn), ValueTracker(tilt), ValueTracker(zoom),
                         *[ValueTracker(c) for c in look]]
            self._shown = ValueTracker(0)          # how many spheres are in
            self._fade = ValueTracker(1)           # sphere opacity scale
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
        self.play(*[t.animate.set_value(v) for t, v in zip(self.cam(), [turn, tilt, zoom, *look])], *extra, run_time=run_time)

    def seg(self, a, b, color, width=4):
        return always_redraw(lambda: Line(self.sp(a), self.sp(b)).set_stroke(color, width))

    def tag(self, tex, point, offset, color=WHITE, font_size=32):
        label = Tex(tex, font_size=font_size).set_color(color)
        label.add_updater(lambda m: m.move_to(self.sp(point) + offset))
        return label.update()

    def dot(self, p, color=WHITE, radius=0.06):
        return always_redraw(lambda: Dot(self.sp(p), radius=radius).set_fill(color).set_stroke(BLACK, 1))

    # The solid: box edges and spheres, painted back to front

    def ball(self, center, radius, color, opacity):
        screen = self.sp(center)
        size = radius * self.cam()[2].get_value()
        body = Circle(radius=size).move_to(screen).set_stroke(color, 2.5, min(1, 2.2 * opacity)).set_fill(color, opacity)
        glow = Circle(radius=0.55 * size).move_to(screen + 0.3 * size * (UP + LEFT))
        glow.set_stroke(width=0).set_fill(WHITE, 0.18 * opacity / 0.4)
        return VGroup(body, glow)

    def make_solid(self):
        self.cam()

        def build():
            fade = self._fade.get_value()
            shown = self._shown.get_value()
            order = [(BIG, R_BIG, BIG_COLOR, 0.32)] + [(c, R_SMALL, SMALL_COLOR, 0.42) for c in SMALL]
            # Spheres come in: bottom four, the big one, then the top four
            reveal = [1, 2, 3, 4, 0, 5, 6, 7, 8]
            visible = []
            for rank, index in enumerate(reveal):
                k = np.clip(shown - rank, 0, 1)
                if k > 0:
                    center, radius, color, opacity = order[index]
                    drop = (1 - k) * 2.5 * np.array([0, 0, 1])
                    visible.append((center + drop, radius, color, opacity * k * fade))
            items = [(self.project(c)[1], self.ball(c, r, col, op)) for c, r, col, op in visible]
            box_center_depth = self.project((0, 0, MID))[1]
            edges = []
            for a, b in BOX_EDGES:
                mid = (BOX[a] + BOX[b]) / 2
                behind = self.project(mid)[1] > box_center_depth + 1e-6
                line = Line(self.sp(BOX[a]), self.sp(BOX[b]))
                if behind:
                    line = DashedLine(self.sp(BOX[a]), self.sp(BOX[b]), dash_length=0.08).set_stroke(BOX_COLOR, 2, 0.55)
                else:
                    line.set_stroke(BOX_COLOR, 3)
                edges.append((behind, line))
            back = VGroup(*[line for behind, line in edges if behind])
            front = VGroup(*[line for behind, line in edges if not behind])
            balls = VGroup(*[mob for depth, mob in sorted(items, key=lambda t: -t[0])])
            return VGroup(back, balls, front)

        return always_redraw(build)

    def get_solid(self):
        def build():
            solid = self.make_solid()
            self._shown.set_value(9)
            self.add(solid)
            return solid
        return self.lazy("solid", build)

    # Sections

    def build(self):
        self.get_card()
        solid = self.make_solid()
        self.add(solid)
        self.play(ShowCreation(solid), run_time=0.8)
        self.play(self._shown.animate.set_value(9), run_time=4.0, rate_func=linear)
        turn = self.cam()[0]
        self.play(turn.animate.increment_value(360), run_time=4.5, rate_func=smooth)
        self.set_state("solid", solid)

    def top_view(self):
        solid = self.get_solid()

        # Straight down: the base is 4 x 4, two small spheres side by side fill it
        self.view("top", 2.2)
        side = VGroup(
            self.tag("4", (0, -2, H), 0.3 * DOWN, WHITE, 34),
            self.tag("4", (2, 0, H), 0.3 * RIGHT, WHITE, 34),
        )
        widths = VGroup(
            self.seg((-2, -2.35, H), (0, -2.35, H), SMALL_COLOR, 4),
            self.seg((0, -2.35, H), (2, -2.35, H), SMALL_COLOR, 4),
        )
        twos = VGroup(self.tag("2", (-1, -2.35, H), 0.25 * DOWN, SMALL_COLOR, 30),
                      self.tag("2", (1, -2.35, H), 0.25 * DOWN, SMALL_COLOR, 30))
        self.play(FadeIn(side), run_time=0.5)
        self.play(FadeOut(side[0]), ShowCreation(widths, lag_ratio=0.5), FadeIn(twos), run_time=0.9)
        self.note("Two diameters make 2 + 2 = 4: the small\nspheres sit tight in the four corners.", wait=1.4)

        # From the axis to a corner sphere's centre
        axis_dot = self.dot((0, 0, H), BIG_COLOR, 0.07)
        corner_dot = self.dot((1, 1, H), SMALL_COLOR, 0.07)
        leg = self.seg((0, 0, H), (1, 1, H), FLAT, 6)
        leg_label = self.tag(R"\sqrt{2}", (0.5, 0.5, H), 0.3 * UL, FLAT, 34)
        steps_1 = VGroup(
            self.seg((0, 0, H), (1, 0, H), WHITE, 2), self.seg((1, 0, H), (1, 1, H), WHITE, 2),
        )
        self.play(FadeIn(axis_dot), FadeIn(corner_dot), ShowCreation(steps_1, lag_ratio=0.5), run_time=0.8)
        self.play(ShowCreation(leg), FadeIn(leg_label), run_time=0.7)
        self.add_step(R"d_{xy} = \sqrt{1^2 + 1^2} = \sqrt{2}", color=FLAT, wait=0.8)
        self.play(FadeOut(VGroup(side[1], widths, twos, axis_dot, corner_dot, steps_1, leg, leg_label)), run_time=0.4)

    def contact(self):
        solid = self.get_solid()

        # Back to the solid: the big sphere touches a small one
        self.view("start", 2.0)
        s = SMALL[3]                       # top-right corner of the bottom layer
        link = self.seg(BIG, s, LINK, 6)
        centers = VGroup(self.dot(BIG, BIG_COLOR, 0.08), self.dot(s, SMALL_COLOR, 0.08))
        touch = BIG + R_BIG * (s - BIG) / np.linalg.norm(s - BIG)
        self.play(self._fade.animate.set_value(0.55), FadeIn(centers), run_time=0.6)
        self.play(ShowCreation(link), run_time=0.8)
        self.play(Flash(self.sp(touch), color=LINK, flash_radius=0.3), run_time=0.7)
        parts = VGroup(
            self.tag("2", (BIG + touch) / 2, 0.3 * UL, BIG_COLOR, 30),
            self.tag("1", (touch + s) / 2, 0.3 * UL, SMALL_COLOR, 30),
        )
        self.play(FadeIn(parts), run_time=0.5)
        self.add_step(R"D = R + r = 2 + 1 = 3", color=LINK, wait=0.4)
        self.note("Touching spheres: the centres are\nR + r apart.", wait=1.2)
        self.play(FadeOut(parts), run_time=0.3)
        self.set_state("link", VGroup(link, centers))

    def triangle(self):
        solid = self.get_solid()
        link = self.lazy("link", VGroup)
        s = SMALL[3]
        foot = np.array([0, 0, s[2]])

        # Side-on along the diagonal: the triangle lies flat in the screen
        self.view("close", 2.3, self._fade.animate.set_value(0.35))
        flat = self.seg(foot, s, FLAT, 6)
        rise = self.seg(foot, BIG, RISE, 6)
        corner = always_redraw(lambda: VMobject().set_points_as_corners([
            self.sp(foot + 0.35 * np.array([0, 0, 1])),
            self.sp(foot + 0.35 * np.array([0, 0, 1]) + 0.35 * (s - foot) / np.linalg.norm(s - foot)),
            self.sp(foot + 0.35 * (s - foot) / np.linalg.norm(s - foot)),
        ]).set_stroke(WHITE, 2.5))
        fill = always_redraw(lambda: Polygon(self.sp(foot), self.sp(s), self.sp(BIG)).set_stroke(width=0).set_fill(LINK, 0.18))
        labels = VGroup(
            self.tag(R"\sqrt{2}", (foot + s) / 2, 0.3 * DOWN, FLAT, 34),
            self.tag(R"\Delta z", (foot + BIG) / 2, 0.45 * LEFT, RISE, 34),
            self.tag("3", (s + BIG) / 2, 0.3 * UR, LINK, 36),
        )
        self.add(fill, *link)
        self.play(FadeIn(fill), ShowCreation(flat), ShowCreation(rise), ShowCreation(corner), FadeIn(labels), run_time=1.2)
        self.note("A right triangle: Pythagoras.", wait=0.9)

        steps = self.steps()
        self.play(FadeOut(VGroup(*steps)), run_time=0.3)
        steps.set_submobjects([])
        line = self.add_step(R"(\sqrt{2})^2 + (\Delta z)^2 = 3^2", font_size=40, wait=0.5)
        line = self.replace_step(line, R"(\Delta z)^2 = 9 - 2 = 7", font_size=40, wait=0.4)
        self.replace_step(line, R"\Delta z = \sqrt{7}", color=RISE, font_size=42, wait=0.6)
        labels[1].clear_updaters()
        new_label = self.tag(R"\sqrt{7}", (foot + BIG) / 2, 0.45 * LEFT, RISE, 34)
        self.play(ReplacementTransform(labels[1], new_label), run_time=0.5)
        self.set_state("triangle", VGroup(fill, flat, rise, corner, labels[0], labels[2], new_label, link))

    def stack(self):
        solid = self.get_solid()
        triangle = self.lazy("triangle", VGroup)
        self.play(FadeOut(triangle), self._fade.animate.set_value(0.6), run_time=0.6)
        self.view("side", 1.4)

        # Measure up the side: 1, sqrt 7, sqrt 7, 1
        rail = np.array([2.45, 2.45, 0])
        levels = [0, 1, 1 + DZ, 1 + 2 * DZ, H]
        colors = [SMALL_COLOR, RISE, RISE, SMALL_COLOR]
        texts = ["1", R"\sqrt{7}", R"\sqrt{7}", "1"]
        bars, tags = VGroup(), VGroup()
        for (z0, z1), color, text in zip(zip(levels, levels[1:]), colors, texts):
            bars.add(self.seg(rail + z0 * OUT, rail + z1 * OUT, color, 8))
            tags.add(self.tag(text, rail + (z0 + z1) / 2 * OUT, 0.45 * RIGHT, color, 34))
        guides = VGroup(*[
            always_redraw(lambda z=z: DashedLine(self.sp((0, 0, z)), self.sp(rail + z * OUT), dash_length=0.07).set_stroke(GREY_B, 1.5))
            for z in levels[1:-1]
        ])
        self.play(ShowCreation(guides, lag_ratio=0.3), run_time=0.8)
        for bar, tag in zip(bars, tags):
            self.play(ShowCreation(bar), FadeIn(tag, 0.1 * RIGHT), run_time=0.55)
        self.note("Bottom to bottom centres, up to the big\ncentre, up to the top centres, to the rim.", wait=1.4)

        steps = self.steps()
        self.play(FadeOut(VGroup(*steps)), run_time=0.3)
        steps.set_submobjects([])
        self.add_step(R"h = 1 + \sqrt{7} + \sqrt{7} + 1", font_size=42, wait=0.5)
        self.conclude(R"h = 2 + 2\sqrt{7}", font_size=48, wait=0.5)

        # Out and around once more
        self.play(FadeOut(VGroup(guides, bars, tags)), self._fade.animate.set_value(1), run_time=0.5)
        self.view("start", 1.8)
        self.play(self.cam()[0].animate.increment_value(180), run_time=3.0, rate_func=smooth)
        self.wait(0.6)
