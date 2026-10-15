from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/cut_cylinder_unrolled.py
#
# A cylinder cut by a slanted plane: what does its lateral surface unroll into?
# The usual guess is a rectangle with a triangle on top.  It is wrong -- the
# top edge is a sine wave.
#
# Put the axis along z and the base circle at z = 0.  A point of the wall at
# angle t is (r cos t, r sin t, z).  The cutting plane z = h0 + m x meets the
# wall at height  H(t) = h0 + m r cos t  above the base.  Unrolling sends the
# point at angle t to arc length s = r t, so t = s / r and the top edge becomes
#
#       h(s) = h0 + r tan(alpha) cos(s / r),        m = tan(alpha)
#
# one full cosine period across the circumference 2 pi r.  The height above the
# base depends only on x = r cos t, the point's sideways position, and a circle
# traced at constant speed projects onto a cosine -- that is the whole reason.
#
# The seam is cut at t = pi, the lowest point of the cut, so the unrolled edge
# runs low -> high -> low: a single smooth hump, directly comparable with the
# triangle people expect.  The wrong "house" outline and the true wave agree at
# exactly three points (the two low corners and the peak) and cross again at
# the quarter points; in between the wave bulges 0.18 units clear of the
# straight lines, and at the peak it is round where the guess has a corner.
#
# The drawing uses one oblique projection, (x, y, z) -> (x, z + DEPTH * y), so
# the wall at angle t is a *vertical* segment on screen in both the rolled and
# the flat state, of the same length H(t) in both.  Unrolling is therefore an
# exact linear interpolation of each segment's foot, with nothing faked.
# Checked: rib heights identical rolled vs flat; cut-ellipse half-height
# sqrt(A^2 + (DEPTH r)^2) matches the drawn extent; wave - line = 0 at
# s = 0, +-pi r / 2, +-pi r with extrema +-0.181 between them.

R = 1.05                 # cylinder radius (circumference 6.60 fits the frame)
H = 2.55                 # height of the cut over the axis
SLOPE = 0.82             # tan of the cut angle, 39.4 degrees
AMPLITUDE = SLOPE * R    # 0.861: how far the cut rises above / below H
DEPTH = 0.40             # foreshortening of the base circle in the oblique view
BASE_Y = 0.25            # screen height of the base, rolled and unrolled alike

SAMPLES = 97
RIB_STEP = 3             # every third sample gets a wall rib: 33 of them

TOP_C = 5.3 * UP         # the "looking down the tube" circle in the why beat
TOP_R = 0.95

WALL_C = "#58C4DD"       # the lateral surface
BASE_C = "#E8ECF4"       # the base circle / baseline
EDGE_C = "#FFE14D"       # the cut edge, and the wave it becomes: the answer
WRONG_C = "#FF6B6B"      # the triangle everybody expects
BAR_C = "#FF9F43"        # sideways position, in the top view and on the wave


def rolled_foot(theta):
    """Where the wall at angle theta meets the base, on the rolled cylinder."""
    return np.array([R * np.cos(theta), BASE_Y + DEPTH * R * np.sin(theta), 0])


def flat_foot(theta):
    """The same point once the seam at theta = pi is cut and laid out flat."""
    return np.array([R * (theta - TAU), BASE_Y, 0])


def height_at(theta, amp=1.0):
    """Height of the cut above the base. amp = 0 is the uncut cylinder."""
    return H + amp * AMPLITUDE * np.cos(theta)


def ramp(x):
    return float(np.clip(x, 0, 1))


def build_surface(t, amp):
    """The lateral surface, t = 0 rolled up, t = 1 unrolled flat.

    Every rib is vertical in both states and keeps its length, so the whole
    unrolling is a straight interpolation of the feet.
    """
    thetas = np.linspace(PI, 3 * PI, SAMPLES)
    feet = [interpolate(rolled_foot(th), flat_foot(th), t) for th in thetas]
    tops = [foot + height_at(th, amp) * UP for foot, th in zip(feet, thetas)]

    # Solid once flat; the cut face reads as a lid while it is still rolled
    sheet = VMobject().set_points_as_corners([*feet, *reversed(tops), feet[0]])
    sheet.set_stroke(width=0).set_fill(WALL_C, 0.16 * ramp(2 * t - 1))
    face = VMobject().set_points_as_corners([*tops, tops[0]])
    face.set_stroke(width=0).set_fill(EDGE_C, 0.22 * ramp(1 - 2.2 * t))

    ribs = VGroup(*[Line(feet[i], tops[i]) for i in range(0, SAMPLES, RIB_STEP)])
    ribs.set_stroke(WALL_C, 2.0, opacity=0.4)
    base = VMobject().set_points_smoothly(feet).set_stroke(BASE_C, 3.5)
    edge = VMobject().set_points_smoothly(tops).set_stroke(EDGE_C, 5)

    surface = VGroup(sheet, face, ribs, base, edge)
    surface.sheet, surface.face, surface.ribs = sheet, face, ribs
    surface.base, surface.edge = base, edge
    return surface


def build_house():
    """The wrong answer: a rectangle with a triangle sitting on top of it."""
    low, high = height_at(PI), height_at(TAU)
    corners = [
        flat_foot(PI), flat_foot(PI) + low * UP,
        flat_foot(TAU) + high * UP,
        flat_foot(3 * PI) + low * UP, flat_foot(3 * PI),
    ]
    house = VMobject().set_points_as_corners(corners)
    return house.set_stroke(WRONG_C, 5).set_fill(WRONG_C, 0.12)


def bar(start, end, color, width=9):
    """A Line that survives its own degenerate case."""
    if get_norm(end - start) < 1e-2:
        end = start + 1e-2 * RIGHT
    return Line(start, end).set_stroke(color, width)


class CutCylinderUnrolled(NarrationMixin, BrandOutroMixin, ShortsScene):
    """Slice a cylinder on a slant, unroll it, and get a sine wave."""

    caption_y = -3.0
    sections = ["hook", "uncut", "guess", "truth", "why", "finish", "outro"]
    upload = dict(
        title="It's Not a Triangle",
        description=(
            "Cut a cylinder on a slant and unroll the side. The top edge is not "
            "two straight lines meeting at a peak -- it is a perfect sine wave."
        ),
        hashtags=["#math", "#shorts", "#geometry", "#calculus"],
        pinned_comment="Did you think it was a triangle too?",
    )

    def setup(self):
        super().setup()
        self.unroll = ValueTracker(0.0)      # 0 rolled, 1 flat
        self.amp = ValueTracker(1.0)         # 0 uncut, 1 slanted
        self.sweep = ValueTracker(PI)        # the moving point in the why beat

    # The surface and the state each section starts from

    def enter(self, unroll, amp):
        """Put the trackers and the surface into this section's entry state,
        building the surface from scratch when the section runs on its own."""
        self.unroll.set_value(unroll)
        self.amp.set_value(amp)
        surface = self.lazy("surface", lambda: build_surface(unroll, amp))
        surface.become(build_surface(unroll, amp))
        return surface

    def drive(self, surface):
        surface.add_updater(lambda m: m.become(
            build_surface(self.unroll.get_value(), self.amp.get_value())
        ))
        return surface

    def morph(self, surface, run_time=2.0, **targets):
        """Animate the trackers with the surface following, then let go."""
        self.drive(surface)
        self.play(*[
            getattr(self, name).animate.set_value(value)
            for name, value in targets.items()
        ], run_time=run_time)
        surface.clear_updaters()

    def get_house(self):
        return self.lazy("house", build_house)

    def get_ghost(self):
        return self.lazy("ghost", lambda: DashedVMobject(
            build_house().set_fill(opacity=0), num_dashes=72
        ).set_stroke(GREY_C, 2.5))

    # Labels

    def make_width_label(self):
        """A dimension line under the sheet: 2 pi r, label between the arrows."""
        left = flat_foot(PI) + 0.5 * DOWN
        right = flat_foot(3 * PI) + 0.5 * DOWN
        label = Tex(R"2\pi r", font_size=46).set_color(WALL_C)
        label.move_to(midpoint(left, right))
        marks = VGroup(
            Arrow(label.get_left() + 0.25 * LEFT, left, buff=0, thickness=3),
            Arrow(label.get_right() + 0.25 * RIGHT, right, buff=0, thickness=3),
            *[Line(end + 0.14 * DOWN, end + 0.14 * UP) for end in (left, right)],
        )
        return VGroup(marks.set_color(WALL_C), label)

    # Sections

    def hook(self):
        """Frame 0: the cut cylinder, an arrow, and what it really unrolls to."""
        parts = Group(
            build_surface(0.0, 1.0),
            Arrow(ORIGIN, 0.7 * DOWN, buff=0).set_color(GREY_B),
            build_surface(1.0, 1.0),
        ).arrange(DOWN, buff=0.22)
        hook = figure_hook(
            hook_title("Not A Triangle", font_size=62), parts,
            teaser_text("Most people get this wrong.", color=WRONG_C),
            figure_height=6.6, buff=0.42,
        )
        self.add(hook)
        self.narrate("Cut a cylinder at a slant, then unroll it.")

        surface = build_surface(0.0, 0.0)
        self.play(FadeOut(hook.title), FadeOut(hook.teaser), run_time=0.4)
        self.play(FadeOut(hook.figure), FadeIn(surface), run_time=0.6)
        self.remove(hook)
        self.unroll.set_value(0.0)
        self.amp.set_value(0.0)
        self.set_state("surface", surface)

    def uncut(self):
        """Everyone already knows this one: a plain cylinder gives a rectangle."""
        surface = self.enter(0, 0)
        self.say("First, a {b:plain cylinder.}", FlashAround(surface, color=WALL_C, time_width=1.2))

        self.say("Unroll the side, and you get a {y:rectangle.}", wait=False)
        self.morph(surface, run_time=1.8, unroll=1.0)
        self.hold()

        width = self.make_width_label()
        self.say("Its width is the whole {b:circumference.}",
                 FadeIn(width, 0.2 * DOWN), run_time=0.7)
        self.play(FadeOut(width), run_time=0.4)

    def guess(self):
        """Slant the cut, then show the shape almost everybody draws."""
        surface = self.enter(1, 0)

        self.say("Now cut the top at an {b:angle.}", wait=False)
        self.morph(surface, run_time=1.1, unroll=0.0)
        self.morph(surface, run_time=1.0, amp=1.0)
        self.hold()

        house = build_house()
        self.say(
            "Unroll it, and most people draw {r:this:}",
            surface.animate.set_opacity(0), FadeIn(house), run_time=0.8,
        )
        self.set_state("house", house)

        self.say("Rectangle, {r:triangle} on top.",
                 ShowCreationThenDestruction(house.copy().set_fill(opacity=0).set_stroke(WHITE, 7)),
                 run_time=1.2)

        cross = Cross(house).set_stroke(WRONG_C, 9)
        self.say("But that is {r:wrong.}", ShowCreation(cross), run_time=0.6)
        self.set_state("cross", cross)

    def truth(self):
        """The aha: unroll it for real and watch the edge bend into a wave."""
        house = self.get_house()
        cross = self.lazy("cross", lambda: Cross(house).set_stroke(WRONG_C, 9))
        ghost = self.get_ghost()
        surface = self.enter(0, 1)

        self.remove(ghost)
        self.say(
            "Here is what really happens.",
            FadeOut(cross), FadeOut(house), FadeIn(surface), run_time=0.8,
        )

        self.say("Unroll it, edge and all.", wait=False)
        self.morph(surface, run_time=2.3, unroll=1.0)
        self.hold()

        self.say(
            "The top edge is a {y:sine wave.}",
            ShowCreationThenDestruction(surface.edge.copy().set_stroke(WHITE, 8)),
            run_time=1.3,
        )

        # The guess laid back over the truth: round where it had a corner
        peak = flat_foot(TAU) + height_at(TAU) * UP
        self.say(
            "Round where the guess had a {r:corner.}",
            FadeIn(ghost),
            ShowCreationThenDestruction(Circle(radius=0.6).move_to(peak).set_stroke(WRONG_C, 5)),
            run_time=1.2,
        )
        self.play(FadeOut(ghost), run_time=0.4)
        self.lazy_state.pop("ghost", None)

    def why(self):
        """Why a wave: height follows the sideways position, around a circle."""
        surface = self.enter(1, 1)
        self.lazy("ghost", VGroup)

        def theta():
            return self.sweep.get_value()

        circle = Circle(radius=TOP_R).move_to(TOP_C).set_stroke(GREY_B, 3)
        middle = Dot(TOP_C, radius=0.06).set_fill(GREY_B)
        caption = Text("looking down\nthe tube", font_size=26, alignment="CENTER")
        caption.set_color(GREY_B).next_to(circle, LEFT, buff=0.4)
        top_view = VGroup(circle, middle, caption)

        mean = DashedLine(
            flat_foot(PI) + H * UP, flat_foot(3 * PI) + H * UP, dash_length=0.1,
        ).set_stroke(GREY_C, 2)

        across = always_redraw(lambda: bar(
            TOP_C, TOP_C + TOP_R * np.cos(theta()) * RIGHT, BAR_C,
        ))
        drop = always_redraw(lambda: DashedLine(
            TOP_C + TOP_R * np.array([np.cos(theta()), np.sin(theta()), 0]),
            TOP_C + TOP_R * np.cos(theta()) * RIGHT, dash_length=0.07,
        ).set_stroke(GREY_B, 2))
        walker = always_redraw(lambda: Dot(
            TOP_C + TOP_R * np.array([np.cos(theta()), np.sin(theta()), 0]), radius=0.11,
        ).set_fill(EDGE_C))
        rise = always_redraw(lambda: bar(
            flat_foot(theta()) + H * UP,
            flat_foot(theta()) + height_at(theta()) * UP, BAR_C,
        ))
        tracer = always_redraw(lambda: Dot(
            flat_foot(theta()) + height_at(theta()) * UP, radius=0.11,
        ).set_fill(EDGE_C))
        live = VGroup(across, drop, walker, rise, tracer)

        self.sweep.set_value(PI)
        self.say("Why? Walk around the {b:base circle.}",
                 FadeIn(top_view), FadeIn(mean), run_time=0.8)
        self.add(live)
        self.say("Your height just follows your {o:sideways position.}", wait=False)
        self.play(self.sweep.animate.set_value(3 * PI), run_time=2.9, rate_func=linear)
        self.hold()

        self.say("And around a circle, that is a {y:cosine.}",
                 FlashAround(surface.edge, color=EDGE_C, time_width=1.5), run_time=1.4)

        live.clear_updaters()
        self.play(FadeOut(live), FadeOut(top_view), FadeOut(mean), run_time=0.5)

    def finish(self):
        """The formula, boxed."""
        self.enter(1, 1)
        self.lazy("ghost", VGroup)

        formula = Tex(R"h(s) = h_0 + r\tan\alpha \, \cos(s/r)", font_size=56)
        formula.set_color(EDGE_C).move_to(0.95 * DOWN)
        box = SurroundingRectangle(formula, buff=0.25).set_stroke(EDGE_C, 3.5)
        legend = Text("s = distance around the base", font_size=28).set_color(GREY_B)
        legend.next_to(box, DOWN, buff=0.22)

        self.say(
            "Every slanted cut gives a {y:perfect sine curve.}",
            Write(formula), FadeIn(legend), run_time=1.2,
        )
        self.play(ShowCreation(box), FlashAround(formula, color=EDGE_C, time_width=1.5), run_time=1.1)
        self.wait(0.6)

    def outro(self):
        for mobject in self.mobjects:
            mobject.clear_updaters()
        super().outro()
