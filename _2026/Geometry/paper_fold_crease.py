from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/paper_fold_crease.py
#
# A 9 x 12 sheet; its corner O is folded onto the far long side, landing at
# P = (9, p).  Which fold makes the crease L shortest?
#
# The crease is the perpendicular bisector of OP, so as P slides along the
# edge d every crease is tangent to the parabola with focus O and directrix d
# (y^2 = 81 - 18x, vertex V = (9/2, 0)).  The foot M of the perpendicular from
# the focus always lands on the tangent at V, which gives OM = (9/2)/cos(t),
# and since OM is the altitude of right triangle AOB,
#   L = OM / (sin t cos t) = 9 / (2 sin t cos^2 t).
# sin t cos^2 t = s - s^3 peaks at s = 1/sqrt(3):  x = 27/4,  L = 27 sqrt(3)/4.
# All of this was checked symbolically, including that the optimal fold is a
# real one (the crease meets the left edge at height 9.55 <= 12).

SHEET_W = 9
SHEET_H = 12
SCALE = 0.47                # scene units per unit of the sheet
FIG_CENTER = 1.18 * UP      # centre of the sheet on screen
STEPS_TOP = -2.65           # step lines and the graph hang from here
GRAPH_W = 5.2
GRAPH_H = 1.6

P_INTRO = 5.4               # an ordinary fold, for the opening picture
P_OPT = 9 / np.sqrt(2)      # the shortest crease
P_LOW = 4.07                # below this the crease leaves through the top edge
P_HIGH = 8.95               # above 9 it would leave through the right edge
X_OPT = 27 / 4
L_OPT = 27 * np.sqrt(3) / 4

PAPER = "#C9D3DF"
PAPER_EDGE = "#9AA7B8"
FLAP = "#3E6A9E"
GRID = "#26303C"
CREASE = YELLOW
DIRECTRIX = "#FF7B7B"
PARABOLA = "#58C4DD"
PEDAL = "#83C167"

TRACE_VALUES = np.linspace(1.0, 11.8, 34)


def fold_x(p):
    """OB: where the crease meets the bottom edge, once O lands at (9, p)."""
    return (81 + p * p) / 18


def fold_a(p):
    """OA: where the crease meets the left edge."""
    return (81 + p * p) / (2 * p)


def crease_length(p):
    return np.hypot(fold_x(p), fold_a(p))


def length_from_x(x):
    return np.sqrt(2 * x ** 3 / (2 * x - 9))


def touch_point(p):
    """Where the crease touches the parabola: level with P."""
    return (4.5 - p * p / 18, p)


def crease_ends(p):
    """The perpendicular bisector of OP, clipped to the sheet.  Returns the
    lower-right end first."""
    mid = np.array([4.5, p / 2])
    along = np.array([-p, 9.0])          # perpendicular to OP = (9, p)
    lo, hi = -np.inf, np.inf
    for k, top in enumerate([SHEET_W, SHEET_H]):
        t1, t2 = sorted([-mid[k] / along[k], (top - mid[k]) / along[k]])
        lo, hi = max(lo, t1), min(hi, t2)
    return mid + lo * along, mid + hi * along


class PaperFoldCrease(MockTestShort):
    """Shortest crease when a corner is folded onto the far long side, solved
    with the parabola the creases envelope."""

    test = ""
    card_top_buff = 0.85
    card_font_size = 40
    step_buff = 0.40

    problem_tex = (
        R"\text{Fold corner } O \text{ onto the long side.}\\"
        R"\text{a) } x \text{ for the shortest } L \quad \text{b) } L_{\min}"
    )

    sections = [
        "pose",
        "draw_fold",
        "reflect",
        "envelope",
        "pedal",
        "watch_crease",
        "exact",
        "finish",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        # The steps hang below the figure rather than straight off the card
        self.steps_top_y = STEPS_TOP
        return card

    # Coordinates

    def pt(self, u, v):
        """Sheet coordinates to the screen.  O = (0, 0) is the folded corner."""
        return FIG_CENTER + SCALE * ((u - SHEET_W / 2) * RIGHT + (v - SHEET_H / 2) * UP)

    def get_tracker(self):
        """Height of P on the far edge; everything live is drawn from it."""
        if not hasattr(self, "_p_tracker"):
            self._p_tracker = ValueTracker(P_INTRO)
        return self._p_tracker

    def p_now(self):
        return self.get_tracker().get_value()

    def right_angle(self, corner, a, b, size=0.2, color=GREY_A):
        u = normalize(a - corner) * size
        v = normalize(b - corner) * size
        mark = VMobject().set_points_as_corners([corner + u, corner + u + v, corner + v])
        return mark.set_stroke(color, 2)

    def away(self, a, b, c):
        """Unit normal to segment ab, on the side away from c."""
        normal = rotate_vector(normalize(b - a), PI / 2)
        return normal if np.dot(normal, c - a) < 0 else -normal

    # The paper picture

    def make_sheet(self):
        sheet = Polygon(*[self.pt(u, v) for u, v in [(0, 0), (9, 0), (9, 12), (0, 12)]])
        return sheet.set_fill(PAPER, 0.16).set_stroke(PAPER_EDGE, 2)

    def make_dims(self):
        def dim(start, end, label, side):
            line = Line(start, end).set_stroke(GREY_B, 2)
            line.add_tip(width=0.14, length=0.14)
            line.add_tip(at_start=True, width=0.14, length=0.14)
            tex = Tex(label, font_size=32).set_color(GREY_A)
            tex.next_to(line, side, buff=0.12)
            return VGroup(line, tex)

        gap = 0.42
        return VGroup(
            dim(self.pt(0, 0) + gap * LEFT, self.pt(0, 12) + gap * LEFT, "12", LEFT),
            dim(self.pt(0, 0) + gap * DOWN, self.pt(9, 0) + gap * DOWN, "9", DOWN),
        )

    def make_flap(self):
        """The corner triangle AOB, as fill plus its two outer edges -- the
        third edge is the fold, which gets drawn on its own."""
        A, O, B = self.pt(0, fold_a(P_INTRO)), self.pt(0, 0), self.pt(fold_x(P_INTRO), 0)
        body = Polygon(A, O, B).set_fill(PAPER, 0.16).set_stroke(width=0)
        edges = VMobject().set_points_as_corners([A, O, B]).set_stroke(PAPER_EDGE, 2)
        return VGroup(body, edges)

    def set_fold(self, flap, unfolded, alpha):
        """Turn the flap `alpha` of the way over the fold, in 3D, darkening it
        as its underside comes into view."""
        A = self.pt(0, fold_a(P_INTRO))
        B = self.pt(fold_x(P_INTRO), 0)
        flap.become(unfolded)
        flap.rotate(alpha * PI, axis=normalize(B - A), about_point=A)
        flap[0].set_fill(interpolate_color(PAPER, FLAP, alpha), interpolate(0.16, 0.6, alpha))
        return flap

    def make_fold_view(self):
        """The problem's own picture, for the fold at P_INTRO, fully folded.
        Parts are exposed so the sections can reveal and retire them."""
        p = P_INTRO
        O, A = self.pt(0, 0), self.pt(0, fold_a(p))
        B, P = self.pt(fold_x(p), 0), self.pt(9, p)

        rest = Polygon(B, self.pt(9, 0), self.pt(9, 12), self.pt(0, 12), A)
        rest.set_fill(PAPER, 0.16).set_stroke(width=0)
        edge = VMobject().set_points_as_corners([B, self.pt(9, 0), self.pt(9, 12), self.pt(0, 12), A])
        edge.set_stroke(PAPER_EDGE, 2)
        flap = self.make_flap()
        self.set_fold(flap, flap.copy(), 1)

        ghost = VGroup(
            DashedLine(A, O, dash_length=0.1),
            DashedLine(O, B, dash_length=0.1),
        ).set_stroke(GREY_B, 2)
        crease = Line(A, B).set_stroke(CREASE, 5)
        L_label = Tex("L", font_size=38).set_color(CREASE)
        L_label.move_to(midpoint(A, B) - 0.3 * normalize(P - O))
        x_bottom = Tex("x", font_size=34).next_to(midpoint(O, B), UP, buff=0.12)
        x_side = Tex("x", font_size=34).move_to(midpoint(B, P) + 0.25 * self.away(B, P, A))
        corner = self.right_angle(P, A, B)

        view = VGroup(rest, edge, flap, ghost, crease, L_label, x_bottom, x_side, corner)
        view.rest, view.edge, view.flap, view.ghost = rest, edge, flap, ghost
        view.crease, view.L_label, view.corner = crease, L_label, corner
        view.x_labels = VGroup(x_bottom, x_side)
        return view

    def make_o_label(self):
        O = self.pt(0, 0)
        dot = Dot(O, radius=0.07).set_color(WHITE)
        label = Tex("O", font_size=34).next_to(O, DL, buff=0.08)
        return VGroup(dot, label)

    # The coordinate picture

    def make_frame(self):
        return self.make_sheet().set_fill(opacity=0)

    def make_grid(self):
        return VGroup(
            *[Line(self.pt(u, 0), self.pt(u, 12)) for u in range(1, 9)],
            *[Line(self.pt(0, v), self.pt(9, v)) for v in range(1, 12)],
        ).set_stroke(GRID, 1.5)

    def make_directrix(self):
        line = Line(self.pt(9, 0), self.pt(9, 12)).set_stroke(DIRECTRIX, 5)
        label = Tex("d", font_size=36).set_color(DIRECTRIX)
        label.next_to(self.pt(9, 0.5), RIGHT, buff=0.16)
        return VGroup(line, label)

    def make_live(self):
        """Everything that follows P as it slides along d."""
        O = self.pt(0, 0)

        def P():
            return self.pt(9, self.p_now())

        def M():
            return self.pt(4.5, self.p_now() / 2)

        crease = Line(ORIGIN, RIGHT).set_stroke(CREASE, 5)
        crease.add_updater(lambda m: m.put_start_and_end_on(
            *[self.pt(*end) for end in crease_ends(self.p_now())]
        ))
        chord = always_redraw(
            lambda: DashedLine(O, P(), dash_length=0.08).set_stroke(GREY_A, 2)
        )
        p_dot = Dot(radius=0.08).set_color(DIRECTRIX)
        p_dot.add_updater(lambda m: m.move_to(P()))
        p_label = Tex("P", font_size=34).set_color(DIRECTRIX)
        p_label.add_updater(lambda m: m.next_to(P(), RIGHT, buff=0.14))
        m_dot = Dot(radius=0.07).set_color(PEDAL)
        m_dot.add_updater(lambda m: m.move_to(M()))
        live = VGroup(chord, crease, p_dot, p_label, m_dot)
        live.update()
        live.crease, live.chord, live.m_dot = crease, chord, m_dot
        return live

    def make_parabola(self):
        curve = ParametricCurve(
            lambda t: self.pt(4.5 - t * t / 18, t),
            t_range=(0, 9, 0.05),
        ).set_stroke(PARABOLA, 5)
        vertex = Dot(self.pt(4.5, 0), radius=0.07).set_color(PARABOLA)
        label = Tex("V", font_size=32).set_color(PARABOLA)
        label.next_to(vertex, DOWN, buff=0.1)
        group = VGroup(curve, vertex, label)
        group.curve = curve
        return group

    def make_pedal_line(self):
        line = DashedLine(self.pt(4.5, 0), self.pt(4.5, 12), dash_length=0.1)
        return line.set_stroke(PEDAL, 3)

    def make_foot(self):
        """OM, the perpendicular from the focus onto the crease."""
        O = self.pt(0, 0)

        def draw():
            p = self.p_now()
            M = self.pt(4.5, p / 2)
            A = self.pt(*crease_ends(p)[1])
            return VGroup(
                Line(O, M).set_stroke(PEDAL, 4),
                self.right_angle(M, self.pt(9, p), A, color=PEDAL),
            )

        return always_redraw(draw)

    def make_touch(self):
        dot = Dot(radius=0.075).set_color(PARABOLA)
        dot.add_updater(lambda m: m.move_to(self.pt(*touch_point(self.p_now()))))
        return dot.update()

    def coordinate_view(self):
        """The sheet as a coordinate picture.  Built silently when the section
        that animates it in was skipped, so any later section renders alone."""
        self.get_card()
        return [
            self.lazy("grid", self.make_grid),
            self.lazy("frame", self.make_frame),
            self.lazy("directrix", self.make_directrix),
            self.lazy("live", self.make_live),
            self.lazy("o_label", self.make_o_label),
        ]

    # Sections

    def draw_fold(self):
        self.get_card()
        p = P_INTRO
        A, B = self.pt(0, fold_a(p)), self.pt(fold_x(p), 0)

        sheet = self.make_sheet()
        dims = self.make_dims()
        self.play(DrawBorderThenFill(sheet), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(d) for d in dims], lag_ratio=0.4), run_time=0.8)
        self.set_state("dims", dims)

        fold_line = DashedLine(A, B, dash_length=0.1).set_stroke(GREY_A, 2)
        self.play(ShowCreation(fold_line), run_time=0.6)

        # Split the sheet along the fold line, then turn the corner over
        view = self.make_fold_view()
        flap = self.make_flap()
        unfolded = flap.copy()
        self.remove(sheet)
        self.add(view.rest, view.edge, flap, fold_line)
        self.play(
            UpdateFromAlphaFunc(flap, lambda m, a: self.set_fold(m, unfolded, a)),
            run_time=1.6,
        )
        self.remove(flap)
        self.add(view.flap)

        self.play(
            FadeIn(view.ghost),
            ShowCreation(view.crease),
            FadeOut(fold_line),
            run_time=0.8,
        )
        self.play(
            FadeIn(view.L_label, scale=0.6),
            LaggedStart(*[FadeIn(x, scale=0.6) for x in view.x_labels], lag_ratio=0.4),
            ShowCreation(view.corner),
            run_time=0.9,
        )
        self.wait(1.0)
        self.set_state("fold", view)

    def reflect(self):
        self.get_card()
        self.lazy("dims", self.make_dims)
        view = self.lazy("fold", self.make_fold_view)
        p = P_INTRO
        O, P = self.pt(0, 0), self.pt(9, p)
        M, A = self.pt(4.5, p / 2), self.pt(0, fold_a(p))

        o_label = self.make_o_label()
        p_dot = Dot(P, radius=0.08).set_color(DIRECTRIX)
        p_label = Tex("P", font_size=34).set_color(DIRECTRIX).next_to(P, RIGHT, buff=0.14)
        self.play(FadeIn(o_label), FadeIn(p_dot, scale=0.5), FadeIn(p_label), run_time=0.6)
        self.set_state("o_label", o_label)

        chord = DashedLine(O, P, dash_length=0.08).set_stroke(GREY_A, 2)
        m_dot = Dot(M, radius=0.07).set_color(PEDAL)
        corner = self.right_angle(M, P, A)
        self.play(ShowCreation(chord), run_time=0.7)
        self.play(FadeIn(m_dot, scale=0.5), ShowCreation(corner), run_time=0.6)
        self.note("Fold O onto P: the crease is the\nperpendicular bisector of OP.")

        marks = VGroup(p_dot, p_label, chord, m_dot, corner)
        marks.stand_ins = VGroup(p_dot, p_label, chord, m_dot)
        marks.corner = corner
        self.set_state("reflect", marks)

    def envelope(self):
        self.get_card()
        tracker = self.get_tracker()
        tracker.set_value(P_INTRO)

        # Retire the paper picture for a coordinate picture of the same sheet.
        # The live crease, chord and dots are drawn exactly where the static
        # ones sit, so swapping them is invisible.
        view = self.lazy_state.pop("fold", None)
        marks = self.lazy_state.pop("reflect", None)
        dims = self.lazy_state.pop("dims", None)
        grid, frame = self.make_grid(), self.make_frame()
        live = self.make_live()
        o_label = self.lazy("o_label", self.make_o_label)

        leaving = []
        if view is not None:
            self.remove(view.crease)
            leaving += [m for m in view if m is not view.crease]
        if marks is not None:
            self.remove(*marks.stand_ins)
            leaving.append(marks.corner)
        if dims is not None:
            leaving.append(dims)
        self.add(grid, frame, live, o_label)
        self.play(
            FadeIn(grid), FadeIn(frame),
            *[FadeOut(m) for m in leaving],
            run_time=0.9,
        )
        for name, mob in [("grid", grid), ("frame", frame), ("live", live)]:
            self.set_state(name, mob)

        directrix = self.make_directrix()
        self.play(ShowCreation(directrix[0]), FadeIn(directrix[1]), run_time=0.8)
        self.add(live, o_label)
        self.set_state("directrix", directrix)

        # Slide P the length of d, leaving every crease behind
        traces = VGroup(*[
            Line(*[self.pt(*end) for end in crease_ends(value)])
            for value in TRACE_VALUES
        ]).set_stroke(CREASE, 1.5, opacity=0)
        self.add(traces, live, o_label)
        self.play(tracker.animate.set_value(TRACE_VALUES[0]), run_time=1.0)

        def reveal(group, alpha):
            now = tracker.get_value()
            for line, value in zip(group, TRACE_VALUES):
                line.set_stroke(opacity=0.35 if value <= now + 1e-6 else 0)

        self.play(
            tracker.animate.set_value(TRACE_VALUES[-1]),
            UpdateFromAlphaFunc(traces, reveal),
            run_time=4.0,
            rate_func=linear,
        )

        parabola = self.make_parabola()
        self.play(ShowCreation(parabola.curve), run_time=1.5)
        self.play(FadeIn(parabola[1:], scale=0.5), run_time=0.4)
        self.set_state("parabola", parabola)
        self.play(
            FadeOut(traces),
            tracker.animate.set_value(P_INTRO),
            run_time=1.0,
        )
        self.note("Every crease is tangent to one parabola:\nfocus O, directrix d.")

    def pedal(self):
        live, o_label = self.coordinate_view()[3:]
        self.lazy("parabola", self.make_parabola)
        tracker = self.get_tracker()

        pedal_line = self.make_pedal_line()
        foot = self.make_foot()
        touch = self.make_touch()
        self.add(pedal_line, live, o_label)
        self.play(ShowCreation(pedal_line), run_time=0.8)
        self.play(FadeIn(foot), FadeIn(touch, scale=0.5), run_time=0.6)
        self.add(foot, touch, live, o_label)
        for name, mob in [("pedal", pedal_line), ("foot", foot), ("touch", touch)]:
            self.set_state(name, mob)

        # M rides up and down the tangent at V; the crease keeps touching
        self.play(tracker.animate.set_value(8.6), run_time=1.3)
        self.play(tracker.animate.set_value(P_LOW + 0.2), run_time=1.6)
        self.play(tracker.animate.set_value(P_INTRO), run_time=0.9)
        self.note("Pedal locus: the foot M from the focus\nalways lies on the tangent at V.")

    def watch_crease(self):
        self.coordinate_view()
        for name, factory in [
            ("parabola", self.make_parabola), ("pedal", self.make_pedal_line),
            ("foot", self.make_foot), ("touch", self.make_touch),
        ]:
            self.lazy(name, factory)
        tracker = self.get_tracker()

        # With ranges that leave out 0, Axes still pins each axis line at the
        # other one's zero -- far off screen here -- so it is used only to map
        # coordinates, anchored by its plot corner, and the frame is drawn
        # by hand
        axes = Axes((5, 9, 1), (11.5, 13.5, 0.5), width=GRAPH_W, height=GRAPH_H)
        corner = 2.45 * LEFT + (STEPS_TOP - 0.4 - GRAPH_H) * UP
        axes.shift(corner - axes.c2p(5, 11.5))
        frame_lines = VGroup(
            Line(axes.c2p(5, 11.5), axes.c2p(9, 11.5)),
            Line(axes.c2p(5, 11.5), axes.c2p(5, 13.5)),
            *[Line(axes.c2p(v, 11.5), axes.c2p(v, 11.5) + 0.08 * DOWN) for v in range(5, 10)],
            *[Line(axes.c2p(5, v), axes.c2p(5, v) + 0.08 * LEFT) for v in (12, 13)],
        ).set_stroke(GREY_B, 2)
        x_numbers = VGroup(*[
            Tex(str(v), font_size=22).set_color(GREY_B).next_to(axes.c2p(v, 11.5), DOWN, buff=0.14)
            for v in range(5, 10)
        ])
        y_numbers = VGroup(*[
            Tex(str(v), font_size=22).set_color(GREY_B).next_to(axes.c2p(5, v), LEFT, buff=0.14)
            for v in (12, 13)
        ])
        x_name = Tex("x", font_size=30).next_to(axes.c2p(9, 11.5), RIGHT, buff=0.15)
        y_name = Tex("L", font_size=30).set_color(CREASE).next_to(axes.c2p(5, 13.5), UP, buff=0.1)

        x_low = fold_x(P_LOW)
        curve = axes.get_graph(length_from_x, x_range=(x_low, 9)).set_stroke(CREASE, 3)
        full_curve = curve.copy()
        curve.pointwise_become_partial(full_curve, 0, 0)

        dot = Dot(radius=0.07).set_color(CREASE)
        dot.add_updater(lambda m: m.move_to(axes.c2p(fold_x(self.p_now()), crease_length(self.p_now()))))
        value = DecimalNumber(0, num_decimal_places=2, font_size=30)
        value.add_updater(lambda m: m.set_value(crease_length(self.p_now())))
        readout = VGroup(Tex("L =", font_size=30), value).arrange(RIGHT, buff=0.12)
        readout.set_color(CREASE)
        readout.move_to(axes.c2p(8.1, 13.25))
        value.add_updater(lambda m: m.next_to(readout[0], RIGHT, buff=0.12))

        frame_parts = VGroup(frame_lines, x_numbers, y_numbers, x_name, y_name)
        self.play(
            FadeIn(frame_parts),
            tracker.animate.set_value(P_LOW),
            run_time=1.0,
        )
        dot.update()
        value.update()
        self.play(FadeIn(dot, scale=0.5), FadeIn(readout), run_time=0.4)
        self.add(curve)

        # Sweep the fold through every valid position, drawing L as we go
        def draw(mob, alpha):
            frac = np.clip((fold_x(self.p_now()) - x_low) / (9 - x_low), 0, 1)
            mob.pointwise_become_partial(full_curve, 0, frac)

        self.play(
            tracker.animate.set_value(P_HIGH),
            UpdateFromAlphaFunc(curve, draw),
            run_time=3.2,
            rate_func=linear,
        )
        self.play(tracker.animate.set_value(P_OPT), run_time=1.8)

        drop = DashedLine(axes.c2p(X_OPT, L_OPT), axes.c2p(X_OPT, 11.5), dash_length=0.06)
        drop.set_stroke(CREASE, 2)
        self.play(ShowCreation(drop), Flash(dot, color=CREASE, flash_radius=0.25), run_time=0.8)
        self.wait(0.8)
        self.set_state("graph", VGroup(frame_parts, curve, dot, readout, drop))

    def exact(self):
        self.coordinate_view()
        parabola = self.lazy("parabola", self.make_parabola)
        for name, factory in [
            ("pedal", self.make_pedal_line), ("foot", self.make_foot), ("touch", self.make_touch),
        ]:
            self.lazy(name, factory)
        self.get_tracker().set_value(P_OPT)

        graph = self.lazy_state.pop("graph", None)
        touch = self.lazy_state.pop("touch")
        self.play(
            *([FadeOut(graph)] if graph is not None else []),
            FadeOut(touch),
            parabola.curve.animate.set_stroke(opacity=0.35),
            run_time=0.6,
        )

        p = P_OPT
        O, V, M = self.pt(0, 0), self.pt(4.5, 0), self.pt(4.5, p / 2)
        A, B = self.pt(0, fold_a(p)), self.pt(fold_x(p), 0)
        angle = np.arctan2(p / 2, 4.5)

        arc = Arc(start_angle=0, angle=angle, radius=0.5, arc_center=O).set_stroke(WHITE, 3)
        theta = Tex(R"\theta", font_size=30).move_to(O + 0.72 * rotate_vector(RIGHT, angle / 2))
        ov = Line(O, V).set_stroke(PEDAL, 6)
        ov_label = Tex(R"\frac{9}{2}", font_size=26).set_color(PEDAL)
        ov_label.move_to(O + 0.6 * (V - O) + 0.4 * UP)
        v_corner = self.right_angle(V, O, M, color=PEDAL)
        self.play(ShowCreation(arc), FadeIn(theta), run_time=0.6)
        self.play(ShowCreation(ov), FadeIn(ov_label), ShowCreation(v_corner), run_time=0.7)
        self.add_step(R"OM = \frac{9/2}{\cos\theta}", color=PEDAL, font_size=38, wait=0.8)

        triangle = Polygon(A, O, B).set_fill(CREASE, 0.12).set_stroke(width=0)
        a_label = Tex("A", font_size=32).next_to(A, LEFT, buff=0.12)
        b_label = Tex("B", font_size=32).next_to(B, DOWN, buff=0.12)
        self.add(triangle)
        self.play(FadeIn(triangle), FadeIn(a_label), FadeIn(b_label), run_time=0.6)
        self.note("OM is the altitude of right triangle AOB.", wait=1.2)

        length = self.add_step(
            R"L = \frac{OM}{\sin\theta\cos\theta}",
            color=CREASE, font_size=38, wait=0.6,
        )
        length = self.replace_step(
            length, R"L = \frac{9}{2\sin\theta\cos^2\theta}",
            color=CREASE, font_size=38, wait=0.9,
        )

        # Keep only the formula for L, then maximise its denominator
        first = self.steps()[0]
        self.play(
            FadeOut(first, 0.3 * UP),
            length.animate.set_y(STEPS_TOP - length.get_height() / 2),
            run_time=0.6,
        )
        self.steps().set_submobjects([length])
        self.note("L is shortest when sin θ cos²θ is largest.", wait=1.1)

        work = self.add_step(
            R"\sin\theta\cos^2\theta = s - s^3, \quad s = \sin\theta",
            font_size=36, wait=0.7,
        )
        work = self.replace_step(work, R"(s - s^3)' = 1 - 3s^2 = 0", font_size=36, wait=0.6)
        self.replace_step(
            work, R"\sin\theta = \frac{1}{\sqrt3}, \quad \cos^2\theta = \frac23",
            font_size=36, wait=1.0,
        )
        self.set_state("theta_marks", VGroup(arc, theta, ov, ov_label, v_corner, triangle, a_label, b_label))

    def finish(self):
        live = self.coordinate_view()[3]
        self.get_tracker().set_value(P_OPT)
        self.clear_steps()

        x_line = self.add_step(
            R"x = \frac{9/2}{\cos^2\theta} = \frac{9/2}{2/3} = \frac{27}{4}",
            font_size=38, wait=0.5, isolate=[R"\frac{27}{4}"],
        )
        L_line = self.add_step(
            R"L_{\min} = \frac{9}{4/(3\sqrt3)} = \frac{27\sqrt3}{4}",
            font_size=38, wait=0.5, isolate=[R"\frac{27\sqrt3}{4}"],
        )
        answers = [x_line[R"\frac{27}{4}"][0], L_line[R"\frac{27\sqrt3}{4}"][0]]

        # On the figure: the answer's crease, and the x it lands at
        p = P_OPT
        glow = VGroup(
            Line(*[self.pt(*end) for end in crease_ends(p)]).set_stroke(WHITE, 10),
            Line(self.pt(0, 0), self.pt(fold_x(p), 0)).set_stroke(WHITE, 10),
        )
        self.play(
            *[a.animate.set_color(RESULT_COLOR) for a in answers],
            ShowPassingFlash(glow, time_width=0.6),
            run_time=1.0,
        )
        boxes = VGroup(*[
            SurroundingRectangle(a, color=RESULT_COLOR, buff=0.12).set_stroke(width=3)
            for a in answers
        ])
        self.play(ShowCreation(boxes), run_time=0.6)
        self.play(
            *[FlashAround(a, color=RESULT_COLOR, time_width=1.5) for a in answers],
            run_time=1.4,
        )
        self.wait(1.5)
