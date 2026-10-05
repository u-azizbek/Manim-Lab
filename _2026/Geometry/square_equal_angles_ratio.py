from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/square_equal_angles_ratio.py
#
# In square ABCD, M is the midpoint of CD and E sits on AD so that
# angle BEM = angle MED.  AM meets BE at P; find PE / BP.
#
# The midline through M parallel to AD bisects every segment running from AD
# to BC, so it meets BE at its midpoint K.  Since MK is parallel to ED, the
# alternate angles give angle KME = angle MED = angle KEM, so KEM is isosceles
# and KM = KE = KB: B, M, E all lie on the circle of diameter BE, hence
# angle BME = 90 degrees.  Then BMC and EMD are complementary, as are CBM and
# BMC, so triangles BCM and MDE are similar; with side 4k that forces
# DE = k and AE = 3k.  Extending AM to meet line BC at T turns ADM into TCM by
# a half turn about M, so CT = AD = 4k and BT = 8k.  Finally AD is parallel to
# BT, so APE ~ TPB and PE / BP = AE / BT = 3/8.
#
# Everything is drawn in the square's own coordinates, where the side is 4 and
# the square is [0, 4]^2, and `place` maps those to the screen.

MODEL = dict(
    A=(0, 4), B=(4, 4), C=(4, 0), D=(0, 0),
    M=(2, 0), E=(0, 1), K=(2, 2.5), N=(2, 4), T=(4, -4),
    P=(12 / 11, 20 / 11),
)
LABEL_DIRS = dict(A=LEFT, B=RIGHT, C=DR, D=DL, M=DOWN, E=LEFT)

SIDE = 3.4              # the square's side on screen, once the solution starts
FIG_GAP = 0.8           # from the bottom of the problem card to the square's top
BIG = 1.9               # blow-up for the opening figure, which doubles as the thumbnail
BIG_CENTER_Y = -1.2

SQ_COLOR = GREY_B
BE_COLOR = "#58C4DD"    # segment BE, and triangle BCM
EM_COLOR = "#5BD98A"    # segment EM, and triangle MDE
AM_COLOR = "#FF9F43"    # segment AM, extended to T
ANG_COLOR = "#FFD166"   # the two equal angles at E, and the pair at P
MID_COLOR = "#C77DFF"   # the midline, K, and the circle on BE
RIGHT_COLOR = "#FF6BD6" # the right angle at M
AE_COLOR = "#FF6B6B"
BT_COLOR = "#4ECDC4"


def side_label(tex, p, q, color, away, font_size=26, buff=0.12, along=0.5):
    """A length label beside segment pq, on the side away from `away`."""
    label = Tex(tex, font_size=font_size).set_color(color)
    spot = p + along * (q - p)
    normal = rotate_vector(normalize(q - p), PI / 2)
    if np.dot(normal, spot - away) < 0:
        normal = -normal
    reach = 0.5 * abs(normal[0]) * label.get_width() + 0.5 * abs(normal[1]) * label.get_height()
    return label.move_to(spot + (buff + reach) * normal)


class SquareEqualAnglesRatio(MockTestShort):
    """PE / BP in a square, from the midline on BE through to similar triangles."""

    test = ""
    card_font_size = 38
    card_width = 7.3
    step_buff = 0.42
    step_font_size = 34

    problem_tex = (
        R"ABCD \text{ is a square},\ \ M \text{ is the midpoint of } CD,\\"
        R"E \text{ lies on } AD \text{ with } \angle BEM = \angle MED,\\"
        R"\text{and } P = AM \cap BE. \quad \text{Find } PE / BP."
    )

    sections = ["pose", "midline", "right_angle", "similar", "extend", "ratio", "outro"]

    # Layout

    def fig_center(self):
        """The square's centre, hung off the bottom of the problem card."""
        if not hasattr(self, "_fig_center"):
            top = self.get_card().get_bottom()[1] - FIG_GAP
            self._fig_center = np.array([0.0, top - SIDE / 2, 0.0])
        return self._fig_center

    def place(self, xy):
        return self.fig_center() + (SIDE / 4) * np.array([xy[0] - 2, xy[1] - 2, 0.0])

    def big_shift(self):
        return (BIG_CENTER_Y - self.fig_center()[1]) * UP

    def at(self, name):
        return self.fig.p(name)

    def dismiss(self, *names, run_time=0.5):
        """Clear what earlier sections drew, skipping whatever a partial
        render never built."""
        leftovers = VGroup(*[getattr(self, n) for n in names if hasattr(self, n)])
        if len(leftovers) > 0:
            self.play(FadeOut(leftovers), run_time=run_time)

    def behind(self, *mobjects):
        """Fills belong under the figure's strokes and labels."""
        self.add(*mobjects)
        self.bring_to_back(*mobjects)
        return VGroup(*mobjects)

    # The figure

    def make_figure(self):
        fig = GeoFigure(
            {name: self.place(xy) for name, xy in MODEL.items()},
            line_color=SQ_COLOR, line_width=5, label_font_size=30, angle_font_size=26,
        )
        self.fig = fig

        self.square = fig.polygon("A", "B", "C", "D")
        self.shade = fig.region("B", "E", "M", color=BE_COLOR, opacity=0.10)
        self.be = fig.segment("B", "E", stroke_color=BE_COLOR, stroke_width=5)
        self.em = fig.segment("E", "M", stroke_color=EM_COLOR, stroke_width=5)
        self.am = fig.segment("A", "M", stroke_color=AM_COLOR, stroke_width=5)
        self.mid_ticks = VGroup(
            fig.ticks("C", "M", 1, stroke_color=WHITE, stroke_width=4),
            fig.ticks("M", "D", 1, stroke_color=WHITE, stroke_width=4),
        )
        self.ang_e = VGroup(*[
            fig.angle(*names, radius=0.46, color=ANG_COLOR, fill_opacity=0.22, stroke_width=3.5)
            for names in [("B", "E", "M"), ("M", "E", "D")]
        ])
        self.dots = {n: Dot(fig.p(n), radius=0.06).set_fill(WHITE) for n in "ABCDME"}
        self.names = {n: fig.label(n, direction=d) for n, d in LABEL_DIRS.items()}
        self.p_dot = Dot(fig.p("P"), radius=0.075).set_fill(YELLOW)
        self.p_name = fig.label("P", direction=UP, buff=0.26, color=YELLOW)

        self.steps_top_y = self.place((2, 0))[1] - 0.85
        return VGroup(
            self.shade, self.square, self.be, self.em, self.am, self.mid_ticks,
            self.ang_e, *self.dots.values(), self.p_dot,
            *self.names.values(), self.p_name,
        )

    def get_figure(self):
        return self.lazy("figure", self.make_figure)

    # Sections

    def pose(self):
        """Card at the top, the figure big in the middle -- the thumbnail frame."""
        card = self.set_state("card", self.make_card())
        self.play(FadeIn(card.rect, scale=0.97), run_time=0.5)
        self.play(Write(card.body), run_time=1.0)
        self.play(FadeIn(card.logo), run_time=0.3)

        figure = self.make_figure()
        figure.scale(BIG, about_point=self.fig_center()).shift(self.big_shift())

        self.play(ShowCreation(self.square), run_time=0.9)
        self.play(
            FadeIn(VGroup(*[self.dots[n] for n in "ABCD"]), lag_ratio=0.1),
            FadeIn(VGroup(*[self.names[n] for n in "ABCD"]), lag_ratio=0.1),
            run_time=0.6,
        )
        self.play(
            FadeIn(VGroup(*[self.dots[n] for n in "ME"])),
            FadeIn(VGroup(*[self.names[n] for n in "ME"])),
            ShowCreation(self.mid_ticks),
            ShowCreation(self.be), ShowCreation(self.em),
            run_time=0.9,
        )
        self.play(FadeIn(self.ang_e, lag_ratio=0.4), FadeIn(self.shade), run_time=0.6)
        self.play(ShowCreation(self.am), run_time=0.6)
        self.play(FadeIn(self.p_dot, scale=0.4), FadeIn(self.p_name), run_time=0.4)
        self.add(figure)
        self.wait(1.4)

        # Back down to working size, freeing the lower frame for the solution
        self.play(
            figure.animate.shift(-self.big_shift()).scale(1 / BIG, about_point=self.fig_center()),
            run_time=1.0,
        )
        self.set_state("figure", figure)

    def midline(self):
        """The midline through M cuts BE at its midpoint K."""
        self.get_figure()
        fig = self.fig

        self.midline_mob = fig.dashed(
            "M", "N", stroke_color=MID_COLOR, stroke_width=4, dash_length=0.08,
        )
        self.play(ShowCreation(self.midline_mob), run_time=0.7)

        self.k_dot = Dot(fig.p("K"), radius=0.07).set_fill(MID_COLOR)
        self.k_name = fig.label("K", direction=UL, buff=0.24, color=MID_COLOR)
        self.play(FadeIn(self.k_dot, scale=0.4), FadeIn(self.k_name), run_time=0.5)

        self.k_ticks = VGroup(*[
            fig.ticks(a, b, 2, stroke_color=MID_COLOR, stroke_width=4)
            for a, b in [("B", "K"), ("K", "E")]
        ])
        self.play(ShowCreation(self.k_ticks), run_time=0.6)
        self.note("The midline bisects every segment\nfrom AD to BC, so BK = KE.", wait=0.9)

    def right_angle(self):
        """Equal angles at E make KEM isosceles, which puts a right angle at M."""
        self.get_figure()
        fig = self.fig

        self.play(FlashAround(self.ang_e, color=ANG_COLOR, time_width=1.5), run_time=0.7)
        self.ang_m = fig.angle(
            "K", "M", "E", radius=0.46, color=ANG_COLOR, fill_opacity=0.22, stroke_width=3.5,
        )
        self.play(TransformFromCopy(self.ang_e[1], self.ang_m), run_time=1.0)

        self.km = fig.segment("K", "M", stroke_color=MID_COLOR, stroke_width=5)
        self.km_ticks = fig.ticks("K", "M", 2, stroke_color=MID_COLOR, stroke_width=4)
        self.play(ShowCreation(self.km), ShowCreation(self.km_ticks), run_time=0.6)
        self.note("MK is parallel to ED, so KME is isosceles:\nK is the centre of the circle on BE.", wait=1.0)
        self.add_step(R"KM = KB = KE = \tfrac12 BE", color=MID_COLOR, wait=0.3)

        self.circ = Arc(
            start_angle=angle_of_vector(self.at("B") - self.at("K")),
            angle=-PI,
            radius=get_norm(self.at("B") - self.at("K")),
            arc_center=self.at("K"),
        ).set_stroke(MID_COLOR, 3)
        self.play(ShowCreation(self.circ), run_time=1.0)

        self.rt_m = fig.right_angle(
            "B", "M", "E", size=0.18, color=RIGHT_COLOR, fill_opacity=0.9, stroke_width=2,
        )
        self.play(FadeIn(self.rt_m, scale=0.5), run_time=0.4)
        self.play(FlashAround(self.rt_m, color=RIGHT_COLOR), run_time=0.5)
        self.add_step(R"\angle BME = 90^\circ", color=RIGHT_COLOR, wait=0.4)

    def similar(self):
        """BCM and MDE are similar, which pins down DE and AE."""
        self.get_figure()
        fig = self.fig
        self.clear_steps()
        self.dismiss(
            "circ", "midline_mob", "km", "k_ticks", "km_ticks",
            "k_dot", "k_name", "ang_m", "ang_e", "shade",
        )

        # The three angles along CD add to a straight angle
        self.a_bmc = fig.angle("B", "M", "C", radius=0.55, color=BE_COLOR, fill_opacity=0.75, stroke_width=4)
        self.a_emd = fig.angle("E", "M", "D", radius=0.55, color=EM_COLOR, fill_opacity=0.75, stroke_width=4)
        self.play(FadeIn(self.a_bmc), FadeIn(self.a_emd), run_time=0.5)
        self.add_step(R"\angle BMC + \angle EMD = 90^\circ", wait=0.4)

        # And so do the two acute angles of right triangle BCM
        self.a_cbm = fig.angle("C", "B", "M", radius=0.55, color=EM_COLOR, fill_opacity=0.75, stroke_width=4)
        self.play(TransformFromCopy(self.a_emd, self.a_cbm), run_time=1.0)
        self.note("Both close the same 90 degrees,\nso angle CBM = angle EMD.", wait=0.9)

        self.tri_b = fig.region("B", "C", "M", color=BE_COLOR, opacity=0.28)
        self.tri_d = fig.region("M", "D", "E", color=EM_COLOR, opacity=0.28)
        self.rt_cd = VGroup(
            fig.right_angle("B", "C", "M", size=0.15, color=GREY_B),
            fig.right_angle("M", "D", "E", size=0.15, color=GREY_B),
        )
        self.behind(self.tri_b, self.tri_d)
        self.play(
            FadeIn(self.tri_b), FadeIn(self.tri_d), FadeIn(self.rt_cd),
            run_time=0.6,
        )

        # MDE grows into BCM: M -> B, D -> C, E -> M
        ghost = VGroup(
            self.tri_d.copy().set_fill(opacity=0.5),
            fig.polyline("M", "D", "E", stroke_color=EM_COLOR),
        )
        self.add(ghost)
        self.play(
            Transform(
                ghost,
                VGroup(
                    fig.region("B", "C", "M", color=EM_COLOR, opacity=0.5),
                    fig.polyline("B", "C", "M", stroke_color=EM_COLOR),
                ),
            ),
            run_time=1.2,
        )
        self.play(FadeOut(ghost), run_time=0.3)

        # The 2k labels sit off-centre so they clear the midpoint ticks
        self.len_labels = VGroup(
            side_label("4k", self.at("B"), self.at("C"), BE_COLOR, self.at("M"), font_size=28),
            side_label("2k", self.at("C"), self.at("M"), BE_COLOR, self.at("B"), font_size=28, along=0.3),
            side_label("2k", self.at("M"), self.at("D"), EM_COLOR, self.at("B"), font_size=28, along=0.3),
            side_label("k", self.at("D"), self.at("E"), EM_COLOR, self.at("M"), font_size=28),
        )
        self.play(FadeIn(self.len_labels[:3], lag_ratio=0.2), run_time=0.5)
        ratio = self.add_step(
            R"\triangle BCM \sim \triangle MDE \ \Rightarrow\ \frac{BC}{MD} = \frac{CM}{DE}",
            font_size=30, wait=0.4,
        )
        self.replace_step(
            ratio, R"\frac{4k}{2k} = \frac{2k}{DE} \ \Rightarrow\ DE = k, \ \ AE = 3k",
            font_size=32, wait=0.3,
        )
        self.play(FadeIn(self.len_labels[3], scale=0.6), run_time=0.4)
        self.wait(0.2)

    def extend(self):
        """Extending AM past M gives a copy of ADM on the far side of BC."""
        self.get_figure()
        fig = self.fig
        self.clear_steps()
        self.dismiss("tri_b", "tri_d", "a_bmc", "a_emd", "a_cbm", "rt_cd", "len_labels")
        self.steps_top_y = self.at("T")[1] - 0.5

        self.mt = fig.segment("M", "T", stroke_color=AM_COLOR, stroke_width=5)
        self.ct = fig.segment("C", "T", stroke_color=SQ_COLOR, stroke_width=4)
        self.t_dot = Dot(self.at("T"), radius=0.07).set_fill(AM_COLOR)
        self.t_name = fig.label("T", direction=RIGHT, buff=0.22, color=AM_COLOR)
        self.play(ShowCreation(self.ct), ShowCreation(self.mt), run_time=0.9)
        self.play(FadeIn(self.t_dot, scale=0.4), FadeIn(self.t_name), run_time=0.4)

        # A half turn about M carries ADM onto TCM
        adm = fig.region("A", "D", "M", color=AM_COLOR, opacity=0.35)
        self.behind(adm)
        self.play(FadeIn(adm), run_time=0.4)
        ghost = VGroup(adm.copy(), fig.polyline("A", "D", "M", stroke_color=AM_COLOR))
        self.add(ghost)
        self.play(Rotate(ghost, PI, about_point=self.at("M")), run_time=1.2)
        self.note("Half a turn about M: DM = MC,\nso ADM lands exactly on TCM.", wait=0.8)

        self.bt = fig.segment("B", "T", stroke_color=BT_COLOR, stroke_width=6)
        bt_label = side_label(
            "8k", self.at("B"), self.at("T"), BT_COLOR, self.at("D"), font_size=30, along=0.28,
        )
        self.play(ShowCreation(self.bt), FadeIn(bt_label), run_time=0.8)
        self.add_step(R"CT = AD = 4k \ \Rightarrow\ BT = 8k", color=BT_COLOR, wait=0.4)
        self.congruent = VGroup(adm, ghost)

    def ratio(self):
        """AD parallel to BT turns the crossing at P into the answer."""
        self.get_figure()
        fig = self.fig
        self.dismiss("congruent", run_time=0.4)

        ae = fig.segment("A", "E", stroke_color=AE_COLOR, stroke_width=6)
        ae_label = side_label("3k", self.at("A"), self.at("E"), AE_COLOR, self.at("M"), font_size=30)
        self.play(ShowCreation(ae), FadeIn(ae_label), run_time=0.6)

        ape = fig.region("A", "P", "E", color=AE_COLOR, opacity=0.4)
        tpb = fig.region("T", "P", "B", color=BT_COLOR, opacity=0.4)
        self.behind(ape, tpb)
        self.play(FadeIn(ape), FadeIn(tpb), run_time=0.6)

        ang_a = fig.angle("E", "A", "P", radius=0.55, color=ANG_COLOR, fill_opacity=0.4)
        ang_t = fig.angle("P", "T", "B", radius=0.55, color=ANG_COLOR, fill_opacity=0.4)
        self.play(FadeIn(ang_a), run_time=0.3)
        self.play(TransformFromCopy(ang_a, ang_t), run_time=0.9)
        self.play(Flash(self.p_dot, color=YELLOW, flash_radius=0.35), run_time=0.6)
        self.note("AD is parallel to BT, so the two\ntriangles at P are similar.", wait=0.8)

        self.add_step(R"\frac{PE}{BP} = \frac{AE}{BT} = \frac{3k}{8k}", wait=0.4)
        self.conclude(R"\frac{PE}{BP} = \frac{3}{8}", font_size=52, wait=1.1)
