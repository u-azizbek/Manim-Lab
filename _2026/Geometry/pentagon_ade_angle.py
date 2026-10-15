from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/pentagon_ade_angle.py
#
# Convex pentagon ABCDE with angle EAB = angle ABC = 108, angle BCD = 168 and
# EA = AB = BC = CD = a.  Find angle ADE.
#
# Setup.  Triangle ABC is isosceles with apex 108, so angle BAC = angle BCA = 36
# and angle EAC = 108 - 36 = 72.  Since EA = BC and the angles at A and B are
# equal, EABC is an isosceles trapezoid with AB || EC, so angle AEC = 180 - 108
# = 72.  Triangle AEC therefore has two 72 base angles: CA = CE = d, with apex
# angle ACE = 36.  Round C that leaves angle BCE = 36 + 36 = 72 and
# angle ECD = 168 - 72 = 96, hence angle DCA = 96 + 36 = 132.
#
# Construction.  Erect the equilateral triangle CEK on CE, on the far side from
# A, so CK = EK = CE = d and angle ECK = 60.
#
# Step 1.  CA = CE = CK = d, so C is the circumcentre of triangle AEK.  The
# inscribed angle EAK on arc EK is half the central angle ECK: 30.  Directly,
# angle AEK = angle AEC + angle CEK = 72 + 60 = 132.
# Step 2.  Triangles AEK and DCA: AE = DC = a, EK = CA = d and the included
# angles AEK = DCA = 132, so SAS gives congruence -- in fact a 156 rotation
# carries one onto the other -- and angle CDA = angle EAK = 30.
# Step 3.  Triangles KCD and ACB: CK = CA = d, CD = CB = a and
# angle KCD = angle ECD - angle ECK = 96 - 60 = 36 = angle ACB, so SAS again
# (here a reflection in the line through C at -12 degrees), giving KD = AB = a
# and angle CDK = angle CBA = 108.
# Step 4.  In ECDK, CE = KE = d and CD = KD = a, so ECDK is a kite with axis
# ED; the axis bisects angle CDK, so angle CDE = 108 / 2 = 54.
#
#   angle ADE = angle CDE - angle CDA = 54 - 30 = 24.
#
# Checked numerically from the coordinates below: the four sides are 1, the
# three given angles are 108/108/168, the interior angles sum to 540, the
# pentagon is convex, and every intermediate value above is exact to 1e-9 --
# including CA = CE = CK = EK = phi, angle ADE = 24, and both rigid motions
# (rotation by 156 about (0.5, 1.123018); reflection in the line through C at
# -12 degrees).

ROT_ANGLE = 156          # carries triangle AEK onto triangle DCA
MIRROR_DEG = -12         # axis through C that folds triangle KCD onto ACB

FIG_CENTER = 3.2 * UP
FIG_WIDTH, FIG_HEIGHT = 4.6, 5.3
OLD_SCALE = 1.998        # the scale every radius below was tuned at

LINE_C = "#E8ECF4"       # the pentagon itself
SIDE_C = "#FFD166"       # the four equal sides, length a
DIAG_C = "#58C4DD"       # everything of length d: CA, CE, CK, EK
GIVEN_C = GREY_B         # the three angles we are handed
CHASE_C = "#5BD98A"      # angles we work out
EQUI_C = "#C39BFF"       # the equilateral triangle, the kite, the folds
MOVE_C = "#FF6B9A"       # a triangle in flight, landing on its twin
ANSWER_C = "#FFE14D"     # the question mark, and 24 degrees


def pentagon_points():
    """Walk the pentagon from A, turning by the exterior angle at each vertex."""
    def step(deg):
        return np.array([np.cos(deg * DEG), np.sin(deg * DEG)])

    A = np.zeros(2)
    B = A + step(0)
    C = B + step(72)             # exterior angle 180 - 108 at B
    D = C + step(84)             # exterior angle 180 - 168 at C
    E = A + step(108)            # interior angle 108 at A
    K = C + rotate_vector_2d(E - C, -60 * DEG)
    return dict(A=A, B=B, C=C, D=D, E=E, K=K, O=(0.5, 1.123018))


def chevrons(fig, a, b, n=2, size=0.12, gap=0.1, color=CHASE_C):
    """Double arrowheads marking a pair of parallel segments."""
    u = normalize(fig.p(b) - fig.p(a))
    perp = rotate_vector(u, PI / 2)
    mid = fig.midpoint(a, b)
    marks = VGroup(*[
        VMobject().set_points_as_corners([
            base - size * u + size * perp, base + size * u, base - size * u - size * perp,
        ])
        for base in [mid + (i - (n - 1) / 2) * gap * u for i in range(n)]
    ])
    return marks.set_stroke(color, 3).set_fill(opacity=0)


class PentagonAngleADE(NarrationMixin, BrandOutroMixin, StepListMixin, ShortsScene):
    """Four equal sides, three given angles, and a 24 degree answer."""

    caption_y = -3.1
    steps_top_y = -0.15
    step_buff = 0.45
    step_font_size = 42
    sections = ["hook", "setup_chase", "circle", "match", "fold", "finish", "outro"]
    upload = dict(
        title="Four Equal Sides, One Angle",
        description=(
            "A convex pentagon with EA = AB = BC = CD and angles 108, 108, 168. "
            "An equilateral triangle turns it into two congruent pairs and a kite."
        ),
        hashtags=["#math", "#shorts", "#geometry", "#olympiad"],
        pinned_comment="Did you find a shorter route to 24 degrees?",
    )

    # The figure: one set of normalised points everything else is built from

    def figure(self):
        if not hasattr(self, "_fig"):
            fig = GeoFigure(
                pentagon_points(), line_color=LINE_C, line_width=4.0,
                label_font_size=34, angle_font_size=28,
            )
            fig.normalize(width=FIG_WIDTH, height=FIG_HEIGHT, center=FIG_CENTER)
            self._fig = fig
        return self._fig

    def r(self, radius):
        """A radius tuned for the old figure, grown with the figure."""
        return radius * self.figure().scale_factor / OLD_SCALE

    def arc_label(self, a, b, c, tex, radius=0.5, color=CHASE_C, out=0.88, offset=ORIGIN,
                  label_deg=None, **kwargs):
        """An angle arc plus its value, as one group.

        The value sits on the bisector unless `label_deg` sends it along another
        direction from the vertex -- needed wherever a drawn line runs close to
        a bisector, or two angles at one vertex share most of a wedge.  The
        figure is only scaled and shifted, so directions are the raw ones.
        """
        fig = self.figure()
        label = fig.angle_label(a, b, c, tex, radius=self.r(out), color=color, offset=offset)
        if label_deg is not None:
            direction = np.array([np.cos(label_deg * DEG), np.sin(label_deg * DEG), 0])
            label.move_to(fig.p(b) + self.r(out) * direction + offset)
        return VGroup(fig.angle(a, b, c, radius=self.r(radius), color=color, **kwargs), label)

    def seg(self, a, b, color, width=3.5):
        return self.figure().segment(a, b).set_stroke(color, width)

    def marks(self, pairs, color, n=1, nudge={}):
        """Congruence ticks.  `nudge` slides a pair's tick along its side, as a
        fraction of the side, off the spot an angle label needs."""
        fig = self.figure()
        return VGroup(*[
            fig.ticks(a, b, n=n).shift(nudge.get((a, b), 0) * (fig.p(b) - fig.p(a)))
            for a, b in pairs
        ]).set_stroke(color, 3)

    # Coloured step lines (add_step would wipe the colours)

    def make_step(self, tex, colors, font_size=None):
        line = Tex(tex, font_size=font_size or self.step_font_size, isolate=list(colors))
        for key, color in colors.items():
            line[key].set_color(color)
        line.set_max_width(self.step_max_width)
        self.place_step(line)
        self.steps().add(line)
        return line

    def add_colored(self, tex, colors, run_time=0.9):
        line = self.make_step(tex, colors)
        self.play(FadeIn(line, 0.15 * DOWN), run_time=run_time)
        return line

    # Lazily built layers, so any section renders on its own

    def make_base(self):
        """The pentagon as it is handed to us, plus the question mark at D."""
        fig = self.figure()
        poly = fig.polygon("A", "B", "C", "D", "E")
        labels = fig.labels({"A": DL, "B": DR, "C": RIGHT, "D": UR, "E": LEFT})
        ticks = self.marks(
            [("E", "A"), ("A", "B"), ("B", "C"), ("C", "D")], SIDE_C,
            nudge={("E", "A"): 0.14, ("C", "D"): 0.1},     # clear of the 30 at A and the 96 at C
        )
        given = VGroup(
            self.arc_label("E", "A", "B", R"108^\circ", color=GIVEN_C, out=0.8),
            self.arc_label("A", "B", "C", R"108^\circ", color=GIVEN_C, out=0.8),
            VGroup(
                fig.angle("B", "C", "D", radius=self.r(0.5), color=GIVEN_C),
                fig.angle_label("B", "C", "D", R"168^\circ", radius=self.r(0.78),
                                color=GIVEN_C, outside=True),
            ),
        )
        target = VGroup(
            fig.angle("A", "D", "E", radius=self.r(0.38), color=ANSWER_C, stroke_width=4),
            fig.angle_label("A", "D", "E", "?", radius=self.r(0.62), color=ANSWER_C, font_size=40),
        )
        base = VGroup(poly, labels, ticks, given, target)
        base.poly, base.labels, base.ticks = poly, labels, ticks
        base.given, base.target = given, target
        return base

    def get_base(self):
        return self.lazy("base", self.make_base)

    def make_chase(self):
        """AC and EC drawn, with every angle the opening chase pins down."""
        return VGroup(
            self.seg("A", "C", DIAG_C), self.seg("E", "C", DIAG_C),
            self.marks([("C", "A"), ("C", "E")], DIAG_C, n=2),
            chevrons(self.figure(), "A", "B"), chevrons(self.figure(), "E", "C"),
            self.arc_label("B", "A", "C", R"36^\circ", radius=0.62, out=0.95),
            self.arc_label("B", "C", "A", R"36^\circ", radius=0.62, out=0.95),
            self.arc_label("E", "A", "C", R"72^\circ", radius=0.44, out=0.8, label_deg=55),
            self.arc_label("A", "E", "C", R"72^\circ", radius=0.44, out=0.78),
            self.arc_label("A", "C", "E", R"36^\circ", radius=0.95, out=1.3),
            self.arc_label("E", "C", "D", R"96^\circ", radius=0.44, out=0.85, label_deg=105),
        )

    def get_chase(self):
        chase = self.lazy("chase", self.make_chase)
        self.lazy("hidden", lambda: VGroup())     # the split-up givens, once gone
        return chase

    def make_equi(self):
        """The equilateral triangle CEK hung on CE."""
        fig = self.figure()
        return VGroup(
            self.seg("E", "K", DIAG_C), self.seg("C", "K", DIAG_C),
            fig.label("K", direction=UP, color=EQUI_C),
            self.marks([("E", "K"), ("C", "K")], DIAG_C, n=2, nudge={("E", "K"): 0.15, ("C", "K"): 0.12}),
            self.arc_label("E", "C", "K", R"60^\circ", radius=0.5, color=EQUI_C, out=0.8),
        )

    def get_equi(self):
        return self.lazy("equi", self.make_equi)

    def make_circle(self):
        """The arc of the circle centred at C through A, E and K."""
        fig = self.figure()
        radius = fig.dist("C", "A")
        starts = [np.arctan2(*(fig.p(n) - fig.p("C"))[1::-1]) for n in ("K", "A")]
        # arctan2 wraps, so the raw difference is -264; the arc K -> E -> A is +96
        sweep = (starts[1] - starts[0]) % TAU
        arc = Arc(
            start_angle=starts[0], angle=sweep,
            radius=radius, arc_center=fig.p("C"),
        ).set_stroke(DIAG_C, 2.5, opacity=0.8)
        return VGroup(arc, self.seg("A", "K", EQUI_C, width=3))

    def get_circle(self):
        return self.lazy("circle", self.make_circle)

    def get_cda(self):
        return self.lazy("cda", lambda: self.arc_label(
            "C", "D", "A", R"30^\circ", radius=0.5, color=DIAG_C, out=0.5,
            label_deg=264, offset=0.42 * RIGHT,
        ))

    def get_dk(self):
        return self.lazy("dk", lambda: VGroup(
            self.seg("D", "K", EQUI_C, width=3),
            self.marks([("D", "K")], SIDE_C),
        ))

    def get_cde(self):
        return self.lazy("cde", lambda: self.arc_label(
            "C", "D", "E", R"54^\circ", radius=1.0, color=CHASE_C, out=1.0,
            label_deg=264, offset=0.42 * RIGHT + 0.12 * DOWN,
        ))

    def get_line_cda(self):
        return self.lazy("l1", lambda: self.make_step(
            R"\angle CDA = 30^\circ", {R"30^\circ": DIAG_C}))

    def get_line_cde(self):
        return self.lazy("l2", lambda: self.make_step(
            R"\angle CDE = 54^\circ", {R"54^\circ": CHASE_C}))

    def trace(self, *outlines, color=YELLOW):
        """Run a bright stroke along the given shapes and let it vanish."""
        glow = VGroup(*outlines).copy().set_stroke(color, 8).set_fill(opacity=0)
        return ShowCreationThenDestruction(glow, lag_ratio=0)

    def flying(self, *names, color=MOVE_C):
        """A filled copy of a triangle, ready to be carried onto its twin."""
        tri = self.figure().region(*names, color=color, opacity=0.4)
        return tri.set_stroke(color, 5)

    # Sections

    def hook(self):
        """Frame 0: the pentagon, its givens, and the angle we want."""
        teaser = Tex(R"\angle ADE = \, ?", isolate=["?"], font_size=64)
        teaser["?"].set_color(ANSWER_C)
        hook = figure_hook(
            "Four Equal Sides", self.make_base(), teaser,
            figure_height=5.9, buff=0.55,
        )
        self.add(hook)
        self.narrate("Four equal sides, three known angles. Find this angle.")

        self.play(FadeOut(hook.title, 0.4 * UP), FadeOut(hook.teaser, 0.4 * DOWN), run_time=0.5)
        base = self.make_base()
        self.play(ReplacementTransform(hook.figure, base), run_time=1.0)
        self.remove(hook)
        self.add(base)
        self.set_state("base", base)

    def setup_chase(self):
        """Angle chase: 36s, 72s, and the two equal segments CA = CE."""
        base = self.get_base()
        fig = self.figure()
        chase = self.make_chase()
        ac, ec, dticks, chev_ab, chev_ec = chase[:5]
        bac, bca, eac, aec, ace, ecd = chase[5:]

        # Triangle ABC is isosceles, so its base angles are 36
        self.say(
            "Triangle ABC is isosceles: {y:36 and 36.}",
            ShowCreation(ac), run_time=0.8, wait=False,
        )
        self.play(
            FadeOut(base.given[0]), FadeIn(bac), FadeIn(bca),
            self.trace(fig.polygon("A", "B", "C"), color=SIDE_C),
            run_time=1.2,
        )
        self.hold()

        # EA = BC with equal angles at A and B makes EABC an isosceles trapezoid
        self.say(
            "So angle EAC is {y:72,} and {b:AB is parallel to EC.}",
            FadeIn(eac), ShowCreation(ec), run_time=0.9, wait=False,
        )
        self.play(FadeIn(chev_ab), FadeIn(chev_ec), run_time=0.5)
        self.hold()

        # Two 72s in triangle AEC, so it is isosceles: CA = CE
        self.say(
            "Angle AEC is {y:72 too, so CA = CE.}",
            FadeIn(aec), run_time=0.6, wait=False,
        )
        self.play(FadeIn(dticks, lag_ratio=0.2),
                  self.trace(ac.copy(), ec.copy(), color=DIAG_C), run_time=1.1)
        # The rest of the chase round C, filled in without narration
        self.play(FadeOut(base.given[2]), FadeIn(ace), FadeIn(ecd), run_time=0.7)
        self.hold()

        self.set_state("chase", chase)
        self.set_state("hidden", VGroup())

    def circle(self):
        """An equilateral triangle on CE makes C a circumcentre."""
        self.get_base()
        self.get_chase()
        equi = self.make_equi()
        circle = self.make_circle()

        self.say(
            "Build the {p:equilateral} triangle CEK.",
            ShowCreation(VGroup(equi[0], equi[1])), run_time=1.0, wait=False,
        )
        self.play(FadeIn(equi[2]), FadeIn(equi[3]), FadeIn(equi[4]), run_time=0.6)
        self.hold()
        self.say("Now {y:CA = CE = CK.}", self.trace(
            self.seg("C", "A", DIAG_C), self.seg("C", "E", DIAG_C), self.seg("C", "K", DIAG_C),
            color=DIAG_C,
        ), run_time=1.0)
        self.set_state("equi", equi)

        eak = self.arc_label("E", "A", "K", R"30^\circ", radius=0.78,
                             color=EQUI_C, out=1.0, label_deg=93)
        self.say(
            "C is a {b:circumcentre,} so {y:angle EAK is 30.}",
            ShowCreation(circle[0]), run_time=1.1, wait=False,
        )
        self.play(ShowCreation(circle[1]), run_time=0.5)
        self.play(FadeIn(eak), run_time=0.5)
        self.hold()
        self.set_state("circle", circle)
        self.set_state("eak", eak)

    def match(self):
        """Triangle AEK is triangle DCA, rotated."""
        self.get_base()
        self.get_chase()
        self.get_equi()
        self.get_circle()
        self.lazy("eak", lambda: self.arc_label(
            "E", "A", "K", R"30^\circ", radius=0.78, color=EQUI_C, out=1.0, label_deg=93))
        fig = self.figure()

        aek = self.arc_label("A", "E", "K", R"132^\circ", radius=1.4,
                             color=MOVE_C, out=1.75, label_deg=45)
        dca = self.arc_label("D", "C", "A", R"132^\circ", radius=1.1,
                             color=MOVE_C, out=1.45, label_deg=142)
        self.say("Both of these angles are {y:132 degrees.}",
                 FadeIn(aek), FadeIn(dca), run_time=0.9)

        # 72 + 60 at E, 96 + 36 at C -- and the triangles they sit in agree
        flier = self.flying("A", "E", "K")
        self.say("Rotate AEK: it {b:lands on DCA.}", wait=False)
        self.play(FadeIn(flier), run_time=0.5)
        self.play(Rotate(flier, ROT_ANGLE * DEG, about_point=fig.p("O")), run_time=1.7)
        self.hold()
        self.say("So {y:angle CDA is 30.}", FadeOut(flier), FadeIn(self.get_cda()), run_time=0.6, wait=False)
        self.play(FadeOut(VGroup(aek, dca)), run_time=0.4)
        self.hold()

        self.get_line_cda()
        self.set_state("l1", self.steps()[-1])

    def fold(self):
        """Triangle KCD folds onto ACB, and ECDK turns out to be a kite."""
        self.get_base()
        self.get_chase()
        self.get_equi()
        self.get_circle()
        self.get_cda()
        self.get_line_cda()
        fig = self.figure()

        spent = VGroup(
            self.get_chase()[7][1], self.get_chase()[8][1],
            self.lazy("eak", lambda: self.arc_label(
                "E", "A", "K", R"30^\circ", radius=0.78, color=EQUI_C, out=1.0, label_deg=93)),
        )
        self.play(FadeOut(spent), run_time=0.4)

        dk = self.get_dk()
        flier = self.flying("K", "C", "D")
        cdk = self.arc_label("C", "D", "K", R"108^\circ", radius=1.1,
                             color=EQUI_C, out=1.45, label_deg=190)
        self.say("Fold KCD onto {b:ACB:} {y:angle CDK is 108.}", wait=False)
        self.play(FadeIn(flier), run_time=0.4)
        self.play(
            Rotate(flier, PI, axis=np.array([np.cos(MIRROR_DEG * DEG),
                                             np.sin(MIRROR_DEG * DEG), 0]),
                   about_point=fig.p("C")),
            run_time=1.7,
        )
        self.play(FadeOut(flier), FadeIn(cdk), run_time=0.6)
        self.hold()

        # CE = KE and CD = KD, so ED is an axis of symmetry
        wing = self.flying("E", "C", "D", color=EQUI_C)
        self.say("ECDK is a {p:kite,} so ED bisects {y:108 into 54.}", wait=False)
        self.play(FadeIn(wing), run_time=0.4)
        self.play(
            Rotate(wing, PI, axis=normalize(fig.p("D") - fig.p("E")),
                   about_point=fig.p("E")),
            run_time=1.5,
        )
        self.play(FadeOut(wing), FadeOut(cdk), FadeIn(self.get_cde()), run_time=0.6)
        self.hold()

        self.get_line_cde()
        self.set_state("l2", self.steps()[-1])

    def finish(self):
        """54 minus 30."""
        base = self.get_base()
        self.get_chase()
        self.get_equi()
        self.get_circle()
        self.get_cda()
        self.get_cde()
        line1 = self.get_line_cda()
        line2 = self.get_line_cde()

        answer = Tex(
            R"\angle ADE = 54^\circ - 30^\circ = 24^\circ",
            isolate=[R"54^\circ", R"30^\circ", R"24^\circ"], font_size=50,
        ).move_to(VGroup(line1, line2))
        answer[R"54^\circ"].set_color(CHASE_C)
        answer[R"30^\circ"].set_color(DIAG_C)
        answer[R"24^\circ"].set_color(ANSWER_C)

        flights = [
            TransformFromCopy(line2[R"54^\circ"], answer[R"54^\circ"]),
            TransformFromCopy(line1[R"30^\circ"], answer[R"30^\circ"]),
        ]
        flown = VGroup(answer[R"54^\circ"], answer[R"30^\circ"]).family_members_with_points()
        rest = VGroup(*[m for m in answer.family_members_with_points() if m not in flown])
        value = self.figure().angle_label(
            "A", "D", "E", R"24^\circ", radius=self.r(0.72), color=ANSWER_C, font_size=32,
        )
        self.say(
            "{y:54 minus 30 is 24 degrees.}",
            *flights, FadeIn(rest), FadeOut(VGroup(line1, line2)), run_time=1.3,
        )
        self.remove(*[flight.mobject for flight in flights])
        self.add(answer)
        self.play(
            FadeOut(base.target[1]), FadeIn(value),
            self.trace(base.target[0], color=ANSWER_C), run_time=0.9,
        )

        box = SurroundingRectangle(answer, buff=0.26).set_stroke(ANSWER_C, 3.5)
        self.play(ShowCreation(box), FlashAround(answer, color=ANSWER_C, time_width=1.5),
                  run_time=1.1)
        self.wait(0.5)
