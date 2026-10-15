from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Puzzles/expand_count_terms.py
#
# Expand (xyz + xy + yz + zx + x + y + z)^10 and collect like terms.  How many
# terms are left?
#
# The seven pieces are exactly the non-empty subsets of {x, y, z}, so each
# bracket contributes an exponent vector in {0,1}^3 minus the zero vector.
# One term of the product is a choice of one piece from each of the 10
# brackets, so a term x^a y^b z^c corresponds to a sum of 10 such vectors.
#
#   Upper bound:  no piece carries x twice, so a <= 10, and likewise b, c <= 10.
#                 That leaves 11 * 11 * 11 = 1331 candidate triples.
#   Lower bound:  every piece carries at least one letter, and we pick 10 of
#                 them, so a + b + c >= 10.  The triples with a + b + c <= 9
#                 can never appear.
#   The gap:      a + b + c <= 9 with a, b, c >= 0 (then a, b, c <= 9 < 10 is
#                 automatic).  Add a slack d >= 0 to get a + b + c + d = 9, and
#                 stars and bars gives C(9 + 4 - 1, 4 - 1) = C(12, 3) = 220.
#
#   Answer: 1331 - 220 = 1111.
#
# Every remaining triple really does occur: lay the a ones, the b ones and the
# c ones in consecutive cyclic blocks over the 10 brackets starting at 0, a and
# a + b.  Each block has length <= 10 so it never reuses a bracket, and the
# three blocks cover all 10 residues because a + b + c >= 10 -- so no bracket
# is left empty, which is exactly the condition for a legal choice.
# Checked: a 10-step reachability expansion over the 7 vectors gives 1111
# distinct exponent triples, equal as a set to {a+b+c >= 10} inside the cube,
# with max exponent 10 and min total degree 10; C(12,3) = 220 directly.

EXPR = R"(xyz + xy + yz + zx + x + y + z)^{10}"
HOOK_EXPR = R"\left( \begin{array}{c} xyz + xy + yz + zx \\ {}+\, x + y + z \end{array} \right)^{10}"
PIECES = ["xyz", "xy", "yz", "zx", "x", "y", "z"]
PICKS = [0, 4, 1, 6, 3, 0, 5, 2, 6, 1]     # the ten pieces that fly together

CHIPS_Y = 4.35
TERM_Y = 2.6               # x^a y^b z^c while it is the centre of attention
TERM_HOME = 5.45           # where it parks once the cube takes over

CUBE_O = 2.6 * UP          # centre of the isometric cube
CUBE_R = 1.85
CORNER = 0.9               # a + b + c = 9 cuts at 9/10 along each axis

STARS_Y = 2.2
STAR_COUNT, BAR_COUNT = 9, 3
PATTERN = "SSSBSSBSSSBS"   # 3 | 2 | 3 | 1  ->  a + b + c + d = 9

TOTAL_C = "#58C4DD"        # the whole cube of candidates, and 1331
BAD_C = "#FF6B6B"          # the corner that cannot happen, and 220
ANSWER_C = "#FFE14D"       # 1111
PIECE_C = "#5BD98A"        # the seven pieces
SLACK_C = "#C39BFF"        # the slack variable d, and the bars
LINE_C = "#E8ECF4"

# Isometric axes seen down the main diagonal, from the origin corner, so the
# chunk that gets cut away sits nearest the viewer.
IA = np.array([np.cos(-30 * DEG), np.sin(-30 * DEG), 0])
IB = np.array([np.cos(210 * DEG), np.sin(210 * DEG), 0])
IC = np.array([0.0, 1.0, 0.0])


def iso(a, b, c):
    """Screen point of (a, b, c), each given as a fraction of the full edge."""
    return CUBE_O + CUBE_R * (a * IA + b * IB + c * IC)


def chip(tex, color=PIECE_C, font_size=34):
    label = Tex(tex, font_size=font_size).set_color(WHITE)
    box = RoundedRectangle(
        width=max(label.get_width() + 0.34, 0.74), height=0.64, corner_radius=0.13,
    )
    box.set_stroke(color, 2.5).set_fill(color, 0.14)
    return VGroup(box, label.move_to(box))


def star(radius=0.26, color=LINE_C):
    points = [
        (radius if i % 2 == 0 else 0.42 * radius)
        * np.array([np.cos(PI / 2 + i * PI / 5), np.sin(PI / 2 + i * PI / 5), 0])
        for i in range(10)
    ]
    return Polygon(*points).set_stroke(width=0).set_fill(color, 1)


def build_cube():
    """Wireframe unit cube in the isometric view, three visible faces shaded."""
    axes = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    faces = VGroup(*[
        Polygon(iso(0, 0, 0), iso(*u), iso(*np.add(u, v)), iso(*v))
        for u, v in [(axes[0], axes[1]), (axes[0], axes[2]), (axes[1], axes[2])]
    ])
    for face, opacity in zip(faces, [0.22, 0.14, 0.08]):
        face.set_stroke(width=0).set_fill(TOTAL_C, opacity)

    rim = Polygon(
        iso(1, 0, 0), iso(1, 1, 0), iso(0, 1, 0),
        iso(0, 1, 1), iso(0, 0, 1), iso(1, 0, 1),
    ).set_stroke(TOTAL_C, 3.5).set_fill(opacity=0)
    spokes = VGroup(*[Line(iso(0, 0, 0), iso(*u)) for u in axes])
    spokes.set_stroke(TOTAL_C, 2.5)

    labels = VGroup(*[
        Tex(name, font_size=38).set_color(TOTAL_C).next_to(
            iso(*u), normalize(iso(*u) - CUBE_O), buff=0.2,
        )
        for name, u in zip("abc", axes)
    ])
    cube = VGroup(faces, rim, spokes, labels)
    cube.faces, cube.rim, cube.spokes, cube.labels = faces, rim, spokes, labels
    return cube


def build_corner():
    """The tetrahedron a + b + c <= 9: a near corner sliced off the cube."""
    tips = [iso(*(CORNER * np.array(u))) for u in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]]
    cut = Polygon(*tips).set_stroke(BAD_C, 3.5).set_fill(BAD_C, 0.3)
    edges = VGroup(*[Line(iso(0, 0, 0), tip) for tip in tips]).set_stroke(BAD_C, 2.5)
    return VGroup(cut, edges)


class ExpandCountTerms(NarrationMixin, BrandOutroMixin, StepListMixin, ShortsScene):
    """Counting the terms of a 10th power without expanding anything."""

    caption_y = -3.35
    steps_top_y = -0.35
    step_buff = 0.5
    step_font_size = 44
    sections = ["hook", "pick", "cube", "floor", "stars", "finish", "outro"]
    upload = dict(
        title="The Terms That Can't Exist",
        description=(
            "Expand this 10th power and collect like terms. You would guess 11 "
            "cubed, but 220 of those triples are impossible. Stars and bars "
            "finishes it off."
        ),
        hashtags=["#math", "#shorts", "#algebra", "#combinatorics"],
        pinned_comment="Did you guess 1331?",
    )

    # Coloured step lines (add_step would wipe the colours)

    def make_step(self, tex, colors, font_size=None):
        line = Tex(tex, font_size=font_size or self.step_font_size, isolate=list(colors))
        for key, color in colors.items():
            line[key].set_color(color)
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.steps().add(line)
        return line

    def add_colored(self, tex, colors, run_time=0.9, wait=0.0):
        line = self.make_step(tex, colors)
        self.play(FadeIn(line, 0.15 * DOWN), run_time=run_time)
        if wait:
            self.wait(wait)
        return line

    # Shared pieces

    def make_header(self):
        header = Tex(EXPR, t2c={"10": ANSWER_C}).set_width(6.4)
        return self.pin_to_top(header, buff=0.5)

    def get_header(self):
        return self.lazy("header", self.make_header)

    def make_chips(self):
        chips = VGroup(*[chip(piece) for piece in PIECES])
        return chips.arrange(RIGHT, buff=0.15).move_to(CHIPS_Y * UP)

    def make_term(self, y=TERM_HOME, font_size=56):
        term = Tex(R"x^a y^b z^c", t2c={"a": TOTAL_C, "b": TOTAL_C, "c": TOTAL_C})
        return term.scale(font_size / 48).move_to(y * UP)

    def get_term(self):
        return self.lazy("term", self.make_term)

    def get_cube(self):
        return self.lazy("cube", build_cube)

    def get_corner(self):
        return self.lazy("corner", build_corner)

    def get_total_line(self):
        return self.lazy(
            "total", lambda: self.make_step(
                R"11 \times 11 \times 11 = 1331", {"1331": TOTAL_C},
            ),
        )

    def get_gap_line(self, tex, colors):
        return self.lazy("gap", lambda: self.make_step(tex, colors))

    def make_stars(self):
        """Nine stars split by three bars into a + b + c + d = 9."""
        row = VGroup(*[
            star() if kind == "S" else Line(0.32 * DOWN, 0.32 * UP).set_stroke(SLACK_C, 5)
            for kind in PATTERN
        ])
        row.arrange(RIGHT, buff=0.2).move_to(STARS_Y * UP)

        groups, current = [], []
        for kind, mob in zip(PATTERN, row):
            if kind == "B":
                groups.append(current)
                current = []
            else:
                current.append(mob)
        groups.append(current)

        labels = VGroup(*[
            Tex(name, font_size=38).set_color(SLACK_C if name == "d" else WHITE).next_to(
                VGroup(*group), DOWN, buff=0.32,
            )
            for name, group in zip("abcd", groups)
        ])
        stars = VGroup(row, labels)
        stars.row, stars.labels = row, labels
        return stars

    def get_stars(self):
        return self.lazy("stars", self.make_stars)

    # Sections

    def hook(self):
        """Frame 0: the expression itself, huge, with the question under it."""
        teaser = Text(
            "How many terms?", font="Avenir Next", weight=BOLD, font_size=52,
            t2c={(14, 15): ANSWER_C},
        )
        hook = formula_hook(
            hook_title("Don't Expand It", mode="gradient", font_size=64),
            Tex(HOOK_EXPR, t2c={"10": ANSWER_C}), teaser,
            formula_width=7.3, buff=1.3,
        )
        self.add(hook)
        self.narrate("Nobody expands this by hand. So let's count instead.")

        self.play(FadeOut(hook.title, 0.4 * UP), FadeOut(hook.teaser, 0.4 * DOWN), run_time=0.5)
        self.play(Transform(hook.formula, self.make_header()), run_time=0.9)
        self.remove(hook)
        self.add(hook.formula)
        self.set_state("header", hook.formula)

    def pick(self):
        """One piece from each of ten brackets makes one term."""
        self.get_header()
        chips = self.make_chips()
        self.say("Each bracket offers these {g:seven pieces.}",
                 FadeIn(chips, lag_ratio=0.12, shift=0.2 * DOWN), run_time=1.1)

        # Ten copies stream together into a single monomial
        term = self.make_term(y=TERM_Y, font_size=72)
        darts = VGroup(*[chips[i].copy() for i in PICKS])
        self.say("Ten picks multiply into {y:one single term.}", wait=False)
        self.play(
            LaggedStart(*[
                dart.animate.scale(0.3).move_to(term).set_opacity(0) for dart in darts
            ], lag_ratio=0.07),
            run_time=1.5,
        )
        self.remove(darts)
        self.play(FadeIn(term, scale=1.2), run_time=0.6)
        self.hold()

        # Park it under the header, out of the cube's way
        self.play(
            FadeOut(chips, 0.3 * UP, lag_ratio=0.08),
            Transform(term, self.make_term()),
            run_time=0.9,
        )
        self.set_state("term", term)

    def cube(self):
        """Each exponent runs 0 to 10, so 1331 triples are on the table."""
        self.get_header()
        self.get_term()
        cube = build_cube()

        self.say(
            "Each bracket adds {b:at most one x.}",
        )
        self.say(
            "So a, b and c run {y:zero to ten.}",
            ShowCreation(cube.rim), FadeIn(cube.faces), run_time=1.2, wait=False,
        )
        self.play(ShowCreation(cube.spokes), Write(cube.labels), run_time=0.9)
        self.hold()
        self.set_state("cube", cube)

        self.say("Eleven choices each: {y:eleven cubed.}", wait=False)
        self.add_colored(R"11 \times 11 \times 11 = 1331", {"1331": TOTAL_C})
        self.set_state("total", self.steps()[-1])
        self.hold()

    def floor(self):
        """No piece is empty, so the total degree can never drop below 10."""
        self.get_header()
        self.get_term()
        self.get_cube()
        self.get_total_line()

        self.say("Every piece carries {b:at least one} letter.")
        corner = build_corner()
        self.say(
            "Ten picks, so {y:the total is at least ten.}", wait=False,
        )
        self.add_colored(R"a + b + c {}\ge 10", {R"{}\ge 10": PIECE_C})
        self.set_state("gap", self.steps()[-1])
        self.hold()

        self.say(
            "That whole {r:corner} of the cube is impossible.",
            ShowCreation(corner, lag_ratio=0), run_time=1.1,
        )
        self.set_state("corner", corner)

    def stars(self):
        """Count the dead corner with stars and bars."""
        self.get_header()
        self.get_term()
        cube = self.get_cube()
        self.get_total_line()
        self.get_corner()
        line = self.get_gap_line(R"a + b + c {}\ge 10", {R"{}\ge 10": PIECE_C})

        self.say("Throw away the ones summing to {r:nine or less.}", wait=False)
        line = self.replace_step(
            line, R"a + b + c {}\le 9", isolate=["a", "b", "c"],
            colors={R"{}\le 9": BAD_C}, run_time=1.1, wait=0,
        )
        self.hold()

        self.say("Add a {p:slack} d, and it becomes an equation.", wait=False)
        line = self.replace_step(
            line, R"a + b + c + d = 9", isolate=["a", "b", "c"],
            colors={"d": SLACK_C}, run_time=1.2, wait=0,
        )
        self.set_state("gap", line)
        self.hold()

        # Stars and bars, with the cube out of the way
        stars = self.make_stars()
        self.play(FadeOut(VGroup(cube, self.get_corner())), run_time=0.5)
        self.lazy_state.pop("corner", None)
        self.say(
            "Nine stars, three bars: {y:choose three of twelve.}",
            FadeIn(stars.row, lag_ratio=0.1), run_time=1.2, wait=False,
        )
        self.play(Write(stars.labels), run_time=0.7)
        self.set_state("stars", stars)
        self.hold()

        line = self.replace_step(
            line, R"\binom{12}{3} = 220", colors={"220": BAD_C}, run_time=1.2, wait=0,
        )
        self.set_state("gap", line)

    def finish(self):
        """Subtract, and the answer assembles out of the two results."""
        self.get_header()
        total = self.get_total_line()
        gap = self.get_gap_line(R"\binom{12}{3} = 220", {"220": BAD_C})
        leftovers = Group(self.get_term(), self.get_stars())

        self.play(FadeOut(leftovers, 0.3 * UP), run_time=0.5)
        self.lazy_state.pop("stars", None)
        self.lazy_state.pop("term", None)

        answer = Tex(
            R"1331 - 220 = 1111", isolate=["1331", "220", "1111"], font_size=68,
        ).move_to(3.0 * UP)
        answer["1331"].set_color(TOTAL_C)
        answer["220"].set_color(BAD_C)
        answer["1111"].set_color(ANSWER_C)

        flights = [
            TransformFromCopy(total["1331"], answer["1331"]),
            TransformFromCopy(gap["220"], answer["220"]),
        ]
        self.say(
            "That leaves exactly {y:1111 terms.}",
            *flights, FadeIn(answer), run_time=1.3,
            speak="That leaves exactly one thousand one hundred eleven terms.",
        )
        self.remove(*[flight.mobject for flight in flights])

        box = SurroundingRectangle(answer, buff=0.28).set_stroke(ANSWER_C, 3.5)
        self.play(ShowCreation(box), FlashAround(answer, color=ANSWER_C, time_width=1.5),
                  run_time=1.1)
        self.wait(0.4)
