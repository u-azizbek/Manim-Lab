from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/square_pinwheel_area.py
#
# ABCD is a square of area 120; M, N, Q are the midpoints of AB, BC, AD.  The
# lines AC, MD, ND, CQ bound a shaded quadrilateral.  Its area?
#
# MD and CQ are two blades of a pinwheel; adding BR and AN (R the midpoint of
# CD) completes it, boxing in a tilted square S.  Turning the four small corner
# triangles half a turn about the midpoints completes four more copies of S,
# so 5S = 120 and S = 24.  The shaded region lives inside S: AC passes through
# the centre and halves it (12), and ND cuts off a corner triangle with legs
# 1/3 and 1/4 of the side (area S/24 = 1).  So the shaded area is 12 - 1 = 11.
# All of it checked with exact fractions.

SIDE = 4.6                  # side of ABCD on screen

# Positions with the square's side taken as 2, A at the origin
PTS = {
    "A": (0, 0), "B": (0, 2), "C": (2, 2), "D": (2, 0),
    "M": (0, 1), "N": (1, 2), "Q": (1, 0), "R": (2, 1), "O": (1, 1),
    # the tilted square
    "K1": (0.4, 0.8), "K2": (1.2, 0.4), "K3": (1.6, 1.2), "K4": (0.8, 1.6),
    # where each corner triangle's inner vertex lands after its half turn
    "Mp": (-0.4, 1.2), "Qp": (0.8, -0.4), "Rp": (2.4, 0.8), "Np": (1.2, 2.4),
    # the shaded quadrilateral is P1 P2 P3 K2
    "P1": (2 / 3, 2 / 3), "P2": (4 / 3, 4 / 3), "P3": (1.5, 1),
}

GIVEN_LINES = [("A", "C"), ("M", "D"), ("N", "D"), ("C", "Q")]
PIN_LINES = [("B", "R"), ("A", "N")]

# (corner triangle, the midpoint it turns about, the square it completes)
ARMS = [
    (("Q", "D", "K2"), "Q", ("K1", "K2", "Qp", "A")),
    (("R", "C", "K3"), "R", ("K2", "K3", "Rp", "D")),
    (("N", "B", "K4"), "N", ("K4", "K3", "C", "Np")),
    (("M", "A", "K1"), "M", ("K1", "K4", "B", "Mp")),
]
ARM_TRAPEZOIDS = [("A", "Q", "K2", "K1"), ("D", "R", "K3", "K2"),
                  ("C", "N", "K4", "K3"), ("B", "M", "K1", "K4")]

LINE = GREY_B
SHADE = "#F4A259"
PIN = "#4FD1C5"
SQUARE = YELLOW
ARM = "#6BD18C"
CORNER = "#FF6B6B"


class SquarePinwheelArea(MockTestShort):
    """Shaded quadrilateral in a square, via the five-squares pinwheel."""

    test = ""
    card_top_buff = 0.85
    step_buff = 0.4

    problem_tex = (
        R"\text{Square } ABCD, \text{ area } 120.\\"
        R"M, N, Q \text{ midpoints. Shaded area?}"
    )

    sections = [
        "pose",
        "draw_figure",
        "pinwheel",
        "complete_squares",
        "thirds",
        "quarter",
        "areas",
        "finish",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        # The completed squares stick out past the sides by a fifth of a side,
        # so leave that much room above and below the square
        overhang = 0.2 * SIDE
        self.square_top = card.get_bottom()[1] - 0.35 - overhang
        square_bottom = self.square_top - SIDE
        self.steps_top_y = square_bottom - overhang - 0.4
        self.steps_top_tight = square_bottom - 0.6
        return card

    # Geometry

    def p(self, name):
        x, y = PTS[name]
        self.get_card()
        center = (self.square_top - SIDE / 2) * UP
        return center + (SIDE / 2) * ((x - 1) * RIGHT + (y - 1) * UP)

    def poly(self, *names):
        return Polygon(*[self.p(n) for n in names])

    def seg(self, a, b):
        return Line(self.p(a), self.p(b))

    def tick(self, point, along, size=0.1):
        """A short mark across a side, at `point`, perpendicular to `along`."""
        across = rotate_vector(normalize(along), PI / 2) * size
        return Line(point - across, point + across).set_stroke(SQUARE, 5)

    # Pieces carried between sections

    def make_figure(self):
        square = self.poly("A", "B", "C", "D").set_stroke(GREY_A, 3)
        corners = VGroup(*[
            Tex(n, font_size=36).next_to(self.p(n), side, buff=0.12)
            for n, side in [("A", DL), ("B", UL), ("C", UR), ("D", DR)]
        ])
        mids = VGroup(*[Dot(self.p(n), radius=0.06) for n in "MNQ"])
        mid_labels = VGroup(*[
            Tex(n, font_size=32).next_to(self.p(n), side, buff=0.12)
            for n, side in [("M", LEFT), ("N", UP), ("Q", DOWN)]
        ])
        lines = VGroup(*[self.seg(a, b) for a, b in GIVEN_LINES]).set_stroke(LINE, 2.5)
        shaded = self.poly("P1", "P2", "P3", "K2").set_fill(SHADE, 0.85).set_stroke(SHADE, 2)
        figure = VGroup(shaded, square, lines, mids, corners, mid_labels)
        figure.shaded, figure.square, figure.lines = shaded, square, lines
        figure.points = VGroup(mids, corners, mid_labels)
        return figure

    def get_figure(self):
        return self.lazy("figure", self.make_figure)

    def make_pins(self):
        r_dot = Dot(self.p("R"), radius=0.06).set_color(PIN)
        r_label = Tex("R", font_size=32).set_color(PIN).next_to(self.p("R"), RIGHT, buff=0.12)
        lines = VGroup(*[self.seg(a, b) for a, b in PIN_LINES]).set_stroke(PIN, 3)
        tilted = self.poly("K1", "K2", "K3", "K4").set_fill(SQUARE, 0.5).set_stroke(SQUARE, 2.5)
        pins = VGroup(tilted, lines, r_dot, r_label)
        pins.tilted, pins.lines, pins.r = tilted, lines, VGroup(r_dot, r_label)
        return pins

    def get_pins(self):
        return self.lazy("pins", self.make_pins)

    def keep_on_top(self):
        """Lines and letters above every fill added since."""
        figure = self.get_figure()
        self.add(figure.square, figure.lines, self.get_pins().lines, figure.points, self.get_pins().r)

    # Sections

    def draw_figure(self):
        self.get_card()
        figure = self.make_figure()
        self.play(ShowCreation(figure.square), run_time=0.8)
        self.play(FadeIn(figure.points, lag_ratio=0.1), run_time=0.6)
        self.play(LaggedStart(*[ShowCreation(l) for l in figure.lines], lag_ratio=0.25), run_time=1.3)
        self.add(figure.shaded)
        self.bring_to_back(figure.shaded)
        self.play(FadeIn(figure.shaded), run_time=0.6)
        self.set_state("figure", figure)
        self.wait(0.8)

    def pinwheel(self):
        figure = self.get_figure()
        pins = self.make_pins()

        # Keep the shaded region's outline in view while the construction runs
        self.play(figure.shaded.animate.set_fill(opacity=0).set_stroke(SHADE, 4), run_time=0.5)
        self.play(FadeIn(pins.r, scale=0.5), run_time=0.4)
        self.play(LaggedStart(*[ShowCreation(l) for l in pins.lines], lag_ratio=0.4), run_time=1.1)
        self.add(pins.tilted)
        self.bring_to_back(pins.tilted)
        self.play(FadeIn(pins.tilted), run_time=0.6)
        self.set_state("pins", pins)
        self.note("Add the two matching lines BR and AN:\nthey box in a tilted square S.", wait=1.3)

    def complete_squares(self):
        figure = self.get_figure()
        pins = self.get_pins()

        triangles = VGroup(*[self.poly(*t).set_fill(ARM, 0.55).set_stroke(width=0) for t, _, _ in ARMS])
        trapezoids = VGroup(*[self.poly(*q).set_fill(ARM, 0.55).set_stroke(width=0) for q in ARM_TRAPEZOIDS])
        self.add(trapezoids, triangles)
        self.bring_to_back(trapezoids, triangles)
        self.play(FadeIn(trapezoids), FadeIn(triangles), run_time=0.6)

        # Half a turn about each midpoint carries a corner triangle outside,
        # where it completes the trapezoid next to it into a copy of S
        self.play(
            LaggedStart(*[
                Rotate(tri, PI, about_point=self.p(pivot))
                for tri, (_, pivot, _) in zip(triangles, ARMS)
            ], lag_ratio=0.2),
            run_time=2.0,
        )
        outlines = VGroup(*[self.poly(*sq) for _, _, sq in ARMS]).set_stroke(ARM, 3)
        centers = [np.mean([self.p(n) for n in sq], axis=0) for _, _, sq in ARMS]
        s_labels = VGroup(*[
            Tex("S", font_size=40).move_to(point)
            for point in [self.p("O"), *centers]
        ])
        self.play(ShowCreation(outlines, lag_ratio=0.1), run_time=0.7)
        self.play(FadeIn(s_labels, lag_ratio=0.15, scale=0.6), run_time=0.8)
        self.add_step(R"5S = 120 \quad\Rightarrow\quad S = 24", font_size=42, wait=0.9)
        self.set_state("arms", VGroup(trapezoids, triangles, outlines, s_labels))

    def thirds(self):
        self.get_figure()
        self.get_pins()
        arms = self.lazy("arms", VGroup)
        # AC runs corner to corner across a row of three of the squares
        row = self.poly("A", "Qp", "C", "Np").set_stroke(WHITE, 5).set_fill(opacity=0)
        diagonal = self.seg("A", "C").set_stroke(SQUARE, 6)
        self.play(ShowCreation(row), arms[3].animate.set_opacity(0.25), run_time=0.9)
        self.play(ShowCreation(diagonal), run_time=0.8)

        k1, k2, k3, k4 = [self.p(n) for n in ("K1", "K2", "K3", "K4")]
        marks = VGroup(*[
            self.tick(start + t * (end - start), k3 - k2, size=0.16)
            for start, end in [(k2, k1), (k3, k4)]
            for t in (1 / 3, 2 / 3)
        ])
        dots = VGroup(*[Dot(self.p(n), radius=0.07).set_color(SQUARE) for n in ("P1", "P2")])
        self.play(ShowCreation(marks, lag_ratio=0.2), FadeIn(dots, scale=0.5), run_time=0.7)
        self.note("AC is the diagonal of a row of 3 squares,\nso it crosses the middle one at the 1/3 marks.", wait=1.3)
        self.play(FadeOut(VGroup(row, diagonal)), run_time=0.4)
        self.set_state("thirds", VGroup(marks, dots))

    def quarter(self):
        figure = self.get_figure()
        self.get_pins()
        arms = self.lazy("arms", VGroup)
        # The protruding squares are gone, so the working can close up
        first = self.steps()[0] if len(self.steps()) else VGroup()
        self.play(
            FadeOut(arms),
            first.animate.set_y(self.steps_top_tight - first.get_height() / 2),
            run_time=0.6,
        )
        self.steps_top_y = self.steps_top_tight

        # CQ and ND are the diagonals of the right half of the square
        half = self.poly("C", "N", "Q", "D").set_stroke(PIN, 4).set_fill(PIN, 0.12)
        diagonals = VGroup(self.seg("C", "Q"), self.seg("N", "D")).set_stroke(PIN, 5)
        center = Dot(self.p("P3"), radius=0.08).set_color(PIN)
        self.add(half)
        self.bring_to_back(half)
        self.play(FadeIn(half), ShowCreation(diagonals, lag_ratio=0.3), run_time=0.9)
        self.play(FadeIn(center, scale=0.4), Flash(center, color=PIN), run_time=0.7)

        # Along CQ the pinwheel marks off 1, 1, then 1/2 of the square's side
        c, k3, k2, q = [self.p(n) for n in ("C", "K3", "K2", "Q")]
        away = rotate_vector(normalize(q - c), -PI / 2) * 0.34
        lengths = VGroup(*[
            Tex(tex, font_size=34).set_color(PIN).move_to(midpoint(a, b) + away)
            for tex, a, b in [("1", c, k3), ("1", k3, k2), (R"\frac12", k2, q)]
        ])
        self.play(FadeIn(lengths, lag_ratio=0.3), run_time=0.8)
        self.note("CQ and ND cross at the centre of rectangle CNQD,\nhalfway along CQ: a quarter side past the corner.", wait=1.6)
        self.play(FadeOut(VGroup(half, diagonals, lengths)), run_time=0.5)
        self.set_state("quarter", center)

    def areas(self):
        self.get_figure()
        pins = self.get_pins()
        self.lazy("thirds", VGroup)
        self.lazy("quarter", VGroup)

        # AC passes through the centre, so it cuts S exactly in half
        half = self.poly("P1", "K2", "K3", "P2").set_fill(SQUARE, 0.7).set_stroke(width=0)
        o_dot = Dot(self.p("O"), radius=0.07).set_color(WHITE)
        self.add(half)
        self.bring_to_back(half)
        self.play(
            FadeIn(half),
            pins.tilted.animate.set_fill(opacity=0.12),
            FadeIn(o_dot, scale=0.5),
            run_time=0.8,
        )
        self.add_step(R"\frac{S}{2} = 12", font_size=40, wait=1.0)

        # ND trims a small right triangle off the corner: legs 1/3 and 1/4
        corner = self.poly("P2", "K3", "P3").set_fill(CORNER, 0.9).set_stroke(CORNER, 2)
        k2, k3, k4 = self.p("K2"), self.p("K3"), self.p("K4")
        p2, p3 = self.p("P2"), self.p("P3")
        legs = VGroup(
            Tex(R"\frac13", font_size=34).move_to(midpoint(k3, p2) + 0.4 * normalize(k3 - k2)),
            Tex(R"\frac14", font_size=34).move_to(midpoint(k3, p3) + 0.4 * normalize(k3 - k4)),
        ).set_color(CORNER)
        self.play(FadeIn(corner), FadeIn(legs, lag_ratio=0.3), run_time=0.8)
        self.add_step(
            R"\frac12 \cdot \frac13 \cdot \frac14 \cdot S = 1",
            color=CORNER, font_size=40, wait=1.8,
        )
        self.set_state("pieces", VGroup(half, corner, legs, o_dot))

    def finish(self):
        figure = self.get_figure()
        pieces = self.lazy_state.get("pieces")

        steps = self.steps()
        if len(steps) >= 3:
            self.play(FadeOut(VGroup(*steps[1:]), 0.3 * UP), run_time=0.5)
            steps.set_submobjects(list(steps[:1]))

        # Trim the corner off the half: what is left is the shaded region
        shaded = figure.shaded.copy().set_fill(SHADE, 0.9).set_stroke(SHADE, 3)
        if pieces is not None:
            half, corner, legs, o_dot = pieces
            self.play(
                Transform(half, shaded),
                FadeOut(corner), FadeOut(legs), FadeOut(o_dot),
                run_time=1.1,
            )
        else:
            self.play(FadeIn(shaded), run_time=0.8)

        answer = self.add_step(
            R"\text{Shaded} = 12 - 1 = 11",
            font_size=50, wait=0.2, isolate=["11"],
        )
        answer["11"][0].set_color(RESULT_COLOR)
        box = SurroundingRectangle(answer, color=RESULT_COLOR, buff=0.2).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(
            FlashAround(answer, color=RESULT_COLOR, time_width=1.5),
            Indicate(half if pieces is not None else shaded, color=SHADE, scale_factor=1.08),
            run_time=1.3,
        )
        self.wait(1.6)
