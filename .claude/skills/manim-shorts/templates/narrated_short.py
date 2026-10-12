from manim_imports_ext import *
import itertools as it


# Render with:
#   ./render.sh .claude/skills/manim-shorts/templates/narrated_short.py
#
# TEMPLATE for a NARRATED short opened with a FIGURE HOOK.  Copy it to
# _2026/<Topic>/<snake_name>.py and replace everything.  The render also writes
# <Scene>.txt / .srt / .json next to the video: the voice-over script.
#
# Moser's circle problem.  Put n points on a circle and join every pair.  The
# pieces go 1, 2, 4, 8, 16 -- and then 31, not 32.
# Why: start with 1 piece.  Drawing a chord adds one piece, plus one more for
# every chord it crosses.  So pieces = 1 + (chords) + (crossings)
# = 1 + C(n, 2) + C(n, 4), since four points fix exactly one crossing.
# n = 6: 1 + 15 + 15 = 31.
# The points are in general position (no three chords through one point),
# with every pair of crossings at least 0.2 radii apart, so the picture shows
# exactly these counts.
# Checked: Euler count 1 + chords + crossings gives 1, 2, 4, 8, 16, 31 for
# n = 1..6 on these angles, matching 1 + C(n,2) + C(n,4).

ANGLES = [193, 6, 73, 310, 124, 245]     # in the order the points are added
RADIUS = 2.7
CENTER = 1.9 * UP
SEQ_Y = 5.5

RING_C = "#FF6B6B"
CHORD_C = GREY_B
POINT_C = "#58C4DD"       # the points (blue in the captions too)
CROSS_C = PURPLE_LIGHT    # the crossings (purple in the captions too)
COUNT_C = "#FFE14D"


def on_circle(deg):
    return CENTER + RADIUS * np.array([np.cos(deg * DEG), np.sin(deg * DEG), 0])


def crossing(p1, p2, p3, p4):
    """Where chords p1p2 and p3p4 cross, or None."""
    d1, d2 = p2 - p1, p4 - p3
    m = np.array([d1[:2], -d2[:2]]).T
    if abs(np.linalg.det(m)) < 1e-9:
        return None
    s, t = np.linalg.solve(m, (p3 - p1)[:2])
    return p1 + s * d1 if 0 < s < 1 and 0 < t < 1 else None


def glowing(circle, color):
    return VGroup(
        circle.copy().set_stroke(color, 18, opacity=0.08),
        circle.copy().set_stroke(color, 9, opacity=0.18),
        circle,
    )


class CirclePieces(NarrationMixin, BrandOutroMixin, ShortsScene):
    """1, 2, 4, 8, 16 ... 31: the circle pattern that breaks."""

    caption_y = -3.6
    sections = ["hook", "first_chord", "doubling", "the_break", "why", "outro"]
    upload = dict(
        title="This Pattern Breaks at 6",
        description="1, 2, 4, 8, 16... the next one is NOT 32. Moser's circle problem.",
        hashtags=["#math", "#shorts", "#geometry", "#puzzle"],
        pinned_comment="Did you guess 32 too?",
    )

    # Figure

    def make_ring(self):
        return glowing(Circle(radius=RADIUS).move_to(CENTER).set_stroke(RING_C, 3.5), RING_C)

    def make_dot(self, k):
        return Dot(on_circle(ANGLES[k]), radius=0.09).set_fill(WHITE)

    def make_chords(self, k):
        """The chords from point k back to every earlier point."""
        return VGroup(*[
            Line(on_circle(ANGLES[k]), on_circle(ANGLES[j])).set_stroke(CHORD_C, 2.5)
            for j in range(k)
        ])

    def make_full_figure(self, n=6):
        return VGroup(
            self.make_ring(),
            VGroup(*[self.make_chords(k) for k in range(n)]),
            VGroup(*[self.make_dot(k) for k in range(n)]),
        )

    def get_ring(self):
        return self.lazy("ring", self.make_ring)

    def get_drawn(self, n):
        """Dots and chords for the first n points, for sections run alone."""
        return self.lazy(f"drawn_{n}", lambda: VGroup(
            VGroup(*[self.make_chords(k) for k in range(n)]),
            VGroup(*[self.make_dot(k) for k in range(n)]),
        ))

    def make_number(self, value, color=WHITE):
        return Tex(str(value), font_size=64).set_color(color)

    def get_sequence(self, values=()):
        """The running list of piece counts across the top.  `values` is what
        the row holds when this section starts, for sections run alone."""
        def build():
            row = VGroup(*[self.make_number(v, COUNT_C if v == 31 else WHITE) for v in values])
            if len(row) > 0:
                row.arrange(RIGHT, buff=0.55).move_to(SEQ_Y * UP)
            return row
        return self.lazy("sequence", build)

    def add_point(self, k, extra=()):
        """Animate point k in, then its chords."""
        dot, chords = self.make_dot(k), self.make_chords(k)
        self.play(FadeIn(dot, scale=0.4), run_time=0.35)
        self.play(ShowCreation(chords, lag_ratio=0.25), *extra, run_time=0.9)
        return VGroup(chords, dot)

    def push_number(self, row, value, color=WHITE, run_time=0.5):
        """Add a number to the end of the row, re-centring the row as it grows."""
        number = self.make_number(value, color)
        if len(row) > 0:
            number.next_to(row[-1], RIGHT, buff=0.55)
        else:
            number.move_to(SEQ_Y * UP)
        left = row.get_left()[0] if len(row) > 0 else number.get_left()[0]
        shift = -0.5 * (left + number.get_right()[0]) * RIGHT
        number.shift(shift)
        moves = [row.animate.shift(shift)] if len(row) > 0 else []
        self.play(FadeIn(number, 0.3 * UP), *moves, run_time=run_time)
        row.add(number)
        return number

    # Sections

    def hook(self):
        """Frame 0 is a FIGURE HOOK: colourful title, the full figure, teaser."""
        teaser = Tex(R"2,\ 4,\ 8,\ 16,\ ?", t2c={"?": COUNT_C}, font_size=80)
        hook = figure_hook("The Pattern That Breaks", self.make_full_figure(), teaser)
        self.add(hook)
        self.narrate("Here is a pattern that fools almost everyone.")
        self.play(FadeOut(hook), run_time=0.6)

        ring = self.make_ring()
        self.play(FadeIn(ring), run_time=0.5)
        self.set_state("ring", ring)

    def first_chord(self):
        self.get_ring()
        row = self.set_state("sequence", VGroup())
        dots = VGroup(self.make_dot(0), self.make_dot(1))
        self.say("Put {b:two points} on a circle and {y:connect them.}", FadeIn(dots, scale=0.4, lag_ratio=0.3))
        chord = self.make_chords(1)
        self.play(ShowCreation(chord), run_time=0.6)
        self.say("Obviously, this divides {y:the circle into two.}", wait=False)
        self.push_number(row, 2)
        self.hold()
        self.set_state("drawn_2", VGroup(chord, dots))

    def doubling(self):
        self.get_ring()
        self.get_drawn(2)
        row = self.get_sequence([2])
        for k, value, text in [
            (2, 4, "A {b:third point,} joined to both: {y:four pieces.}"),
            (3, 8, "A {b:fourth:} {y:eight pieces.}"),
            (4, 16, "A {b:fifth:} {y:sixteen.} It {p:doubles} every time."),
        ]:
            self.say(text, wait=False)
            self.add_point(k)
            self.push_number(row, value)
            self.hold()
        self.set_state("drawn_5", Group())

    def the_break(self):
        self.get_ring()
        self.get_drawn(5)
        row = self.get_sequence([2, 4, 8, 16])

        self.say("So {b:six points} must give {y:thirty-two...} right?", wait=False)
        guess = self.push_number(row, 32, GREY_B)
        self.add_point(5)
        self.hold(0.3)

        # Count them: the counter stops one short
        counter = Integer(0, font_size=96).set_color(COUNT_C).move_to(CENTER)
        counter.set_backstroke(BLACK, 10)
        self.say("Count the pieces: there are only {y:thirty-one!}",
                 ChangeDecimalToValue(counter, 31), run_time=1.8)
        cross = Cross(guess).set_stroke(RING_C, 6)
        real = self.make_number(31, COUNT_C).move_to(guess)
        self.play(ShowCreation(cross), run_time=0.4)
        self.play(FadeOut(VGroup(guess, cross)), FadeIn(real, scale=1.3), FadeOut(counter), run_time=0.6)
        row.remove(guess)
        row.add(real)
        self.set_state("drawn_6", Group())

    def why(self):
        self.get_ring()
        self.get_drawn(6)
        self.get_sequence([2, 4, 8, 16, 31])

        # Each crossing comes from exactly four points
        points = [on_circle(a) for a in ANGLES]
        hits = [
            crossing(points[a], points[b], points[c], points[d])
            for (a, b), (c, d) in it.combinations(it.combinations(range(6), 2), 2)
            if len({a, b, c, d}) == 4
        ]
        crossings = VGroup(*[Dot(x, radius=0.07).set_fill(CROSS_C) for x in hits if x is not None])
        chords = VGroup(*[self.make_chords(k) for k in range(6)]).set_stroke(POINT_C, 4)

        self.say("Every {b:chord} adds one piece...", ShowCreationThenDestruction(chords, lag_ratio=0.03), run_time=1.6)
        self.say("...and every {p:crossing} adds one more.", LaggedStart(*[GrowFromCenter(d) for d in crossings], lag_ratio=0.08), run_time=1.4)

        formula = Tex(
            R"1 + \binom{n}{2} + \binom{n}{4}",
            t2c={R"\binom{n}{2}": POINT_C, R"\binom{n}{4}": CROSS_C}, font_size=60,
        ).move_to(1.75 * DOWN)
        self.say("Pieces = 1 + {b:chords} + {p:crossings.}", Write(formula),
                 speak="So the pieces are one, plus the chords, plus the crossings.")
        result = Tex(
            R"1 + 15 + 15 = 31", t2c={"31": COUNT_C}, font_size=60,
        ).move_to(formula)
        result["15"][0].set_color(POINT_C)
        result["15"][1].set_color(CROSS_C)
        self.say("For six points: {y:1 + 15 + 15 = 31.}",
                 TransformMatchingTex(formula, result), run_time=1.0,
                 speak="For six points, that is one plus fifteen plus fifteen: thirty-one.")
        box = SurroundingRectangle(result, buff=0.2).set_stroke(COUNT_C, 3.5)
        self.play(ShowCreation(box), FlashAround(result, color=COUNT_C, time_width=1.5), run_time=1.2)
        self.wait(1.0)
