from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Geometry/pentagon_cosine_identity.py
#
# cos(pi/5) - cos(2pi/5) = 1/2, read off a regular pentagon of side 1.
#
# Stand the pentagon on a side and box it between the vertical through its
# left vertex and the horizontal through its top vertex.  The symmetry axis
# meets the bottom side at its midpoint, so that half is 1/2.
#   top triangle:    hypotenuse 1 (a side), angle 36 = pi/5 at the top vertex
#                    (half of 108 is 54 from the axis, so 36 from the
#                    horizontal), so its top leg is cos(pi/5)
#   bottom triangle: hypotenuse 1, angle 180 - 108 = 72 = 2pi/5 at the bottom
#                    left vertex, so its bottom leg is cos(2pi/5)
# The box's top edge and bottom edge are the same width:
#   cos(pi/5) = cos(2pi/5) + 1/2.
# Numerically 0.80902 - 0.30902 = 0.5.

C36, S36 = np.cos(PI / 5), np.sin(PI / 5)
C72, S72 = np.cos(2 * PI / 5), np.sin(2 * PI / 5)

# Plane coordinates, side 1, bottom side from (0, 0) to (1, 0)
V0, V1 = (0, 0), (1, 0)
V2, V3, V4 = (1 + C72, S72), (0.5, S72 + S36), (-C72, S72)
MID = (0.5, 0)                      # foot of the symmetry axis
CORNER = (-C72, S72 + S36)          # top left corner of the box
FOOT = (-C72, 0)                    # bottom left corner of the box

UNIT = 3.35
FIG_Y = 0.75

EDGE = "#7FE3F0"
TOP = "#4FD1C5"
BOTTOM = "#A99BFF"
HALF = "#FFD166"
ARC_TOP = "#7FB3FF"
ARC_BOTTOM = "#FF6BD6"


def sp(point):
    x, y = point
    return np.array([UNIT * (x - 0.5), FIG_Y + UNIT * (y - (S72 + S36) / 2), 0])


class PentagonCosineIdentity(MockTestShort):
    """cos(pi/5) - cos(2pi/5) = 1/2 from a regular pentagon."""

    test = ""
    card_top_buff = 0.6
    step_buff = 0.42

    problem_tex = (
        R"\text{Show that:}\\"
        R"\cos\frac{\pi}{5} - \cos\frac{2\pi}{5} = \frac{1}{2}"
    )

    sections = [
        "pose",
        "pentagon",
        "axis",
        "top_triangle",
        "bottom_triangle",
        "compare",
        "outro",
    ]

    def make_card(self):
        card = super().make_card()
        self.steps_top_y = sp(V0)[1] - 1.25
        return card

    def seg(self, p, q, color=WHITE, width=3):
        return Line(sp(p), sp(q)).set_stroke(color, width)

    def corner(self, at, d1, d2, size=0.22, color=WHITE):
        at = sp(at)
        d1, d2 = np.array([*d1, 0]), np.array([*d2, 0])
        return VMobject().set_points_as_corners([
            at + size * d1, at + size * (d1 + d2), at + size * d2,
        ]).set_stroke(color, 2)

    def arc(self, at, start, end, color, radius=0.55):
        return Arc(
            start_angle=start * DEGREES, angle=(end - start) * DEGREES,
            radius=radius, arc_center=sp(at),
        ).set_stroke(color, 4)

    def arc_label(self, arc, tex, color, at, buff=0.32, font_size=30):
        label = Tex(tex, font_size=font_size).set_color(color)
        middle = arc.point_from_proportion(0.5)
        label.move_to(middle + buff * normalize(middle - sp(at)))
        return label

    def make_pentagon(self):
        pentagon = Polygon(*[sp(v) for v in (V0, V1, V2, V3, V4)]).set_stroke(EDGE, 4)
        ones = VGroup()
        for p, q in [(V0, V1), (V1, V2), (V2, V3), (V3, V4), (V4, V0)]:
            middle = (sp(p) + sp(q)) / 2
            inward = normalize(sp((0.5, 0.69)) - middle)
            ones.add(Tex("1", font_size=32).move_to(middle + 0.3 * inward))
        return VGroup(pentagon, ones)

    def get_pentagon(self):
        return self.lazy("pentagon", self.make_pentagon)

    # Sections

    def pentagon(self):
        self.get_card()
        pentagon, ones = self.make_pentagon()
        self.play(ShowCreation(pentagon), run_time=1.3)
        self.play(FadeIn(ones, lag_ratio=0.15), run_time=0.7)
        self.note("A regular pentagon with side 1:\nevery angle is 108°.", wait=1.2)
        self.set_state("pentagon", VGroup(pentagon, ones))

    def axis(self):
        pentagon, ones = self.get_pentagon()

        # The symmetry axis halves the bottom side
        axis = self.seg(V3, MID, WHITE, 3)
        square = self.corner(MID, (1, 0), (0, 1))
        self.play(ShowCreation(axis), run_time=0.8)
        self.play(ShowCreation(square), FadeOut(ones[0]), run_time=0.4)
        halves = VGroup(
            self.seg(V0, MID, HALF, 6),
            self.seg(MID, V1, HALF, 6),
        )
        half_labels = VGroup(*[
            Tex(R"\tfrac{1}{2}", font_size=34).set_color(HALF).next_to(h, UP, buff=0.14)
            for h in halves
        ])
        self.play(ShowCreation(halves, lag_ratio=0), FadeIn(half_labels), run_time=0.7)
        self.note("The symmetry axis meets the bottom\nside at its midpoint.", wait=1.1)
        self.play(FadeOut(halves[1]), FadeOut(half_labels[1]), run_time=0.4)
        self.set_state("axis", VGroup(axis, square))
        self.set_state("half", VGroup(halves[0], half_labels[0]))

    def top_triangle(self):
        pentagon, ones = self.get_pentagon()

        # Box the pentagon: across the top and down the left
        top_line = self.seg(CORNER, V3, WHITE, 3)
        left_line = self.seg(CORNER, FOOT, WHITE, 3)
        self.play(ShowCreation(top_line), ShowCreation(left_line), run_time=0.9)
        box_corner = self.corner(CORNER, (1, 0), (0, -1))
        tri = Polygon(sp(CORNER), sp(V3), sp(V4)).set_stroke(width=0).set_fill(TOP, 0.45)
        self.add(tri, pentagon, top_line, left_line)
        self.play(FadeIn(tri), ShowCreation(box_corner), run_time=0.6)

        # The angle at the top vertex: 108 split by the axis, 36 to the horizontal
        whole = self.arc(V3, 216, 324, WHITE, 0.6)
        whole_label = self.arc_label(whole, R"108^\circ", WHITE, V3, 0.34, 26)
        self.play(ShowCreation(whole), FadeIn(whole_label), run_time=0.7)
        halfs = VGroup(
            self.arc_label(self.arc(V3, 216, 270, WHITE, 0.6), R"54^\circ", WHITE, V3, 0.34, 24),
            self.arc_label(self.arc(V3, 270, 324, WHITE, 0.6), R"54^\circ", WHITE, V3, 0.34, 24),
        )
        self.play(ReplacementTransform(whole_label, halfs), run_time=0.6)
        angle = self.arc(V3, 180, 216, ARC_TOP, 0.75)
        angle_label = self.arc_label(angle, R"36^\circ", ARC_TOP, V3, 0.3, 28)
        self.play(ShowCreation(angle), FadeIn(angle_label), run_time=0.6)
        self.note("90° − 54° = 36° = π/5 from the horizontal.", wait=1.1)
        self.play(
            FadeOut(VGroup(whole, halfs)),
            Transform(angle_label, self.arc_label(angle, R"\tfrac{\pi}{5}", ARC_TOP, V3, 0.32, 32)),
            run_time=0.6,
        )

        # Hypotenuse 1, so the leg along the top is cos(pi/5)
        leg = self.seg(CORNER, V3, TOP, 7)
        leg_label = Tex(R"\cos\tfrac{\pi}{5}", font_size=36).set_color(TOP).next_to(leg, UP, buff=0.14)
        self.play(Indicate(ones[3], color=TOP, scale_factor=1.4), run_time=0.6)
        self.play(ShowCreation(leg), FadeIn(leg_label, 0.1 * UP), run_time=0.8)
        self.note("Hypotenuse 1: the side next to the angle is its cosine.", wait=1.1)
        self.set_state("top", VGroup(top_line, left_line, box_corner, tri, angle, angle_label, leg, leg_label))

    def bottom_triangle(self):
        pentagon, ones = self.get_pentagon()

        # Extend the bottom side left to the box's corner
        base = self.seg(FOOT, V0, WHITE, 3)
        foot_corner = self.corner(FOOT, (1, 0), (0, 1))
        tri = Polygon(sp(FOOT), sp(V0), sp(V4)).set_stroke(width=0).set_fill(BOTTOM, 0.45)
        self.play(ShowCreation(base), run_time=0.5)
        self.add(tri, pentagon)
        self.play(FadeIn(tri), ShowCreation(foot_corner), run_time=0.6)

        inside = self.arc(V0, 0, 108, WHITE, 0.45)
        inside_label = self.arc_label(inside, R"108^\circ", WHITE, V0, 0.3, 24)
        self.play(ShowCreation(inside), FadeIn(inside_label), run_time=0.6)
        angle = self.arc(V0, 108, 180, ARC_BOTTOM, 0.45)
        angle_label = self.arc_label(angle, R"72^\circ", ARC_BOTTOM, V0, 0.32, 26)
        self.play(ShowCreation(angle), FadeIn(angle_label), run_time=0.6)
        self.note("180° − 108° = 72° = 2π/5.", wait=1.0)
        self.play(
            FadeOut(VGroup(inside, inside_label)),
            Transform(angle_label, self.arc_label(angle, R"\tfrac{2\pi}{5}", ARC_BOTTOM, V0, 0.36, 30)),
            run_time=0.6,
        )

        leg = self.seg(FOOT, V0, BOTTOM, 7)
        leg_label = Tex(R"\cos\tfrac{2\pi}{5}", font_size=36).set_color(BOTTOM).next_to(leg, DOWN, buff=0.14)
        self.play(Indicate(ones[4], color=BOTTOM, scale_factor=1.4), run_time=0.6)
        self.play(ShowCreation(leg), FadeIn(leg_label, 0.1 * DOWN), run_time=0.8)
        self.wait(0.5)
        self.set_state("bottom", VGroup(base, foot_corner, tri, angle, angle_label, leg, leg_label))

    def compare(self):
        top = self.lazy("top", VGroup)
        bottom = self.lazy("bottom", VGroup)
        half = self.lazy("half", VGroup)
        top_leg, top_label = top[-2], top[-1]
        bottom_leg, bottom_label = bottom[-2], bottom[-1]

        # The box is as wide at the top as at the bottom
        self.note("The box has the same width at the top and the bottom.", wait=1.0)
        copy = top_leg.copy()
        self.play(copy.animate.move_to(sp(((FOOT[0] + MID[0]) / 2, -0.36))), run_time=1.3)
        self.play(
            Indicate(VGroup(bottom_leg, half[0]), color=WHITE, scale_factor=1.05),
            Indicate(copy, scale_factor=1.05),
            run_time=0.8,
        )

        # Read it off
        equal = Tex(
            R"\cos\frac{\pi}{5} = \cos\frac{2\pi}{5} + \frac{1}{2}",
            t2c={R"\cos\frac{\pi}{5}": TOP, R"\cos\frac{2\pi}{5}": BOTTOM, R"\frac{1}{2}": HALF},
            font_size=44,
        )
        self.place_step(equal)
        self.steps().add(equal)
        self.play(
            TransformFromCopy(top_label, equal[R"\cos\frac{\pi}{5}"][0]),
            TransformFromCopy(bottom_label, equal[R"\cos\frac{2\pi}{5}"][0]),
            TransformFromCopy(half[1], equal[R"\frac{1}{2}"][0]),
            FadeIn(equal["="]), FadeIn(equal["+"]),
            FadeOut(copy),
            run_time=1.3,
        )
        self.wait(0.6)
        final = self.replace_step(
            equal, R"\cos\frac{\pi}{5} - \cos\frac{2\pi}{5} = \frac{1}{2}",
            colors={R"\cos\frac{\pi}{5}": TOP, R"\cos\frac{2\pi}{5}": BOTTOM, R"\frac{1}{2}": HALF},
            key_map={"+": "-"}, font_size=48, wait=0.3,
        )
        box = SurroundingRectangle(final, color=RESULT_COLOR, buff=0.2).set_stroke(width=4)
        self.play(ShowCreation(box), run_time=0.5)
        self.play(FlashAround(final, color=RESULT_COLOR, time_width=1.5), run_time=1.2)
        self.add_step(R"0.809 - 0.309 = 0.5", color=GREY_B, font_size=30, wait=1.5)
