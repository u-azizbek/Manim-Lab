from manim_imports_ext import *



# ── Geometry helpers ──────────────────────────────────────────────────────────

def angle_arc(vertex, p1, p2, radius=0.45, color=WHITE, stroke_width=2.0):
    """Return an Arc centred at vertex, sweeping from the direction of p1 to p2."""
    start_angle = angle_of_vector(p1 - vertex)
    end_angle   = angle_of_vector(p2 - vertex)
    # Always sweep the smaller arc (interior angle)
    diff = (end_angle - start_angle) % TAU
    if diff > PI:
        start_angle, end_angle = end_angle, start_angle
        diff = TAU - diff
    arc = Arc(
        radius=radius,
        start_angle=start_angle,
        angle=diff,
        arc_center=vertex,
    )
    arc.set_stroke(color, stroke_width)
    return arc


def tick_mark(p1, p2, n=1, size=0.15, color=WHITE, gap=0.08):
    """Return tick marks on the segment p1→p2 (n = number of ticks)."""
    mid = (p1 + p2) / 2
    direction = normalize(p2 - p1)
    perp = rotate_vector(direction, PI / 2)
    marks = VGroup()
    offsets = np.linspace(-(n - 1) * gap / 2, (n - 1) * gap / 2, n)
    for offset in offsets:
        centre = mid + offset * direction
        marks.add(
            Line(centre - size * perp, centre + size * perp,
                 stroke_color=color, stroke_width=2.5)
        )
    return marks

def vertex_dot(point, radius=0.07, color=WHITE):
    """Return a Dot at the given vertex point."""
    return Dot(point, radius=radius, color=color)


def AngleTriangle(base_length, angle_A_degrees, angle_B_degrees, vertex_dots=False):
    # Convert angles from degrees to radians for Python's math functions
    alpha = math.radians(angle_A_degrees)
    beta = math.radians(angle_B_degrees)

    # Point A is the bottom left, Point B is the bottom right
    A = ORIGIN
    B = RIGHT * base_length

    # Calculate the X and Y coordinates for the top point (C)
    # Using the intersection of two lines based on the tangent of the angles
    tan_alpha = math.tan(alpha)
    tan_beta = math.tan(beta)

    c_x = (base_length * tan_beta) / (tan_alpha + tan_beta)
    c_y = c_x * tan_alpha

    C = np.array([c_x, c_y, 0])

    polygon = Polygon(A, B, C)

    if vertex_dots:
        dots = VGroup(vertex_dot(A), vertex_dot(B), vertex_dot(C))
        return VGroup(polygon, dots)

    return polygon

# ── Scene ─────────────────────────────────────────────────────────────────────

class IsoscelesTriangle(InteractiveScene):
    """
    Problem: ABC is isosceles with AB = AC.
    Base BC.  Angles:  ∠A = 20°,  ∠B = ∠C = 80°.
    Animate the full construction and label all angles.
    """

    def construct(self):
        # Create our triangle
        my_triangle = AngleTriangle(base_length=2.0, angle_A_degrees=80, angle_B_degrees=80, vertex_dots=True)
        my_triangle.move_to(ORIGIN)
        
        # 1. NO FILL COLOR: Set the outline stroke, but keep fill opacity at 0
        my_triangle.set_stroke(color=WHITE, width=4)
        my_triangle.set_fill(opacity=0) 
        
        # 2. ADD LABELS:
        # Get the list of the three coordinate points [Point A, Point B, Point C]
        polygon = my_triangle[0] if isinstance(my_triangle, VGroup) else my_triangle
        vertices = polygon.get_vertices()
        A = vertices[0]
        C = vertices[1]
        B = vertices[2]
        
        # Create the text and position it relative to each vertex
        # We use buffer directions so the text doesn't overlap the lines
        label_A = Tex("A").next_to(A, DL, buff=0.12)
        # label_A.set_color(BLUE)
        label_B = Tex("B").next_to(B, UP, buff=0.12)
        # label_B.set_color(BLUE)
        label_C = Tex("C").next_to(C, DR,  buff=0.12)
        # label_C.set_color(BLUE)

        ticks_AB = tick_mark(A, B, n=2, color=GREEN)
        ticks_BC = tick_mark(B, C, n=2, color=GREEN)

        tick_marks = VGroup(ticks_AB, ticks_BC)
        
        # Group the labels so we can animate them easily together
        labels = VGroup(label_A, label_B, label_C)

        triangle_label = VGroup(my_triangle, labels, tick_marks)
        
        # Animate the outline drawing, then write the labels
        self.play(ShowCreation(my_triangle))
        self.play(Write(labels))
        self.wait(1)

        self.play(
            FadeIn(ticks_AB, lag_ratio=0.4),
            FadeIn(ticks_BC, lag_ratio=0.4),
            run_time=0.8,
        )

        # self.play(triangle_label.animate.shift(LEFT*5.5), run_time=1.5)
        # self.wait()


        # base_line = Line(B, C, stroke_color=COLOR_TRIANGLE, stroke_width=3)

        # B_dot = Dot(B, radius=0.07, color=COLOR_VERTEX)
        # C_dot = Dot(C, radius=0.07, color=COLOR_VERTEX)
        # B_label = Tex("B").next_to(B, DL, buff=0.12)
        # C_label = Tex("C").next_to(C, DR, buff=0.12)

        # # self.play(Write(step1), run_time=0.5)
        # self.play(
        #     ShowCreation(base_line),
        #     run_time=1.0,
        # )
        # self.play(
        #     FadeIn(B_dot), FadeIn(C_dot),
        #     Write(B_label), Write(C_label),
        #     run_time=0.6,
        # )
        # self.wait(0.4)

        # # ─── Step 2 – Construct apex A using base angles 80° ─────────────────
        # step2 = Text("Step 2: Construct apex A  (base angles = 80°)", font_size=25, color=GREY_B)
        # step2.to_corner(DR).shift(UP * 0.1)

        # # Show the two equal-leg lines appearing
        # side_AB = Line(A, B, stroke_color=COLOR_TRIANGLE, stroke_width=3)
        # side_AC = Line(A, C, stroke_color=COLOR_TRIANGLE, stroke_width=3)
        # A_dot   = Dot(A, radius=0.07, color=COLOR_VERTEX)
        # A_label = Tex("A").next_to(A, UP, buff=0.14)

        # self.play(
        #     ShowCreation(side_AB),
        #     ShowCreation(side_AC),
        #     run_time=1.4,
        # )
        # self.play(
        #     FadeIn(A_dot),
        #     Write(A_label),
        #     run_time=0.5,
        # )
        # self.wait(0.4)

        # # ─── Step 3 – Equal-side tick marks (AB = AC) ─────────────────────────
        # step3 = Text("Step 3: Mark equal sides  AB = AC", font_size=25, color=GREY_B)
        # step3.to_corner(DR).shift(UP * 0.1)

        # ticks_AB = tick_mark(A, B, n=2, color=COLOR_EQUAL_TICK)
        # ticks_AC = tick_mark(A, C, n=2, color=COLOR_EQUAL_TICK)

        # equal_note = Text("AB = AC", font_size=24, color=COLOR_EQUAL_TICK)
        # equal_note.to_corner(UL).shift(DOWN * 0.1 + RIGHT * 0.2)

        # self.play(
        #     FadeOut(step2),
        #     Write(step3),
        #     run_time=0.5,
        # )
        # self.play(
        #     FadeIn(ticks_AB, lag_ratio=0.4),
        #     FadeIn(ticks_AC, lag_ratio=0.4),
        #     run_time=0.8,
        # )
        # self.play(Write(equal_note), run_time=0.5)
        # self.wait(0.4)

        # # ─── Step 4 – Label and animate angles ───────────────────────────────
        # step4 = Text("Step 4: Label all angles", font_size=25, color=GREY_B)
        # step4.to_corner(DR).shift(UP * 0.1)

        # self.play(
        #     FadeOut(step3),
        #     Write(step4),
        #     run_time=0.5,
        # )

        # # Angle arcs
        # arc_A = angle_arc(A, B, C, radius=0.55, color=COLOR_ANGLE_A, stroke_width=2.5)
        # arc_B = angle_arc(B, C, A, radius=0.50, color=COLOR_ANGLE_B, stroke_width=2.5)
        # arc_C = angle_arc(C, A, B, radius=0.50, color=COLOR_ANGLE_C, stroke_width=2.5)

        # # Angle labels – nudge each away from its arc
        # def arc_label_pos(vertex, p1, p2, dist=0.78):
        #     mid_dir = normalize(normalize(p1 - vertex) + normalize(p2 - vertex))
        #     return vertex + dist * mid_dir

        # label_A = Tex(R"20^\circ", font_size=32, color=COLOR_ANGLE_A)
        # label_A.move_to(arc_label_pos(A, B, C, dist=0.80))

        # label_B = Tex(R"80^\circ", font_size=32, color=COLOR_ANGLE_B)
        # label_B.move_to(arc_label_pos(B, C, A, dist=0.85))

        # label_C = Tex(R"80^\circ", font_size=32, color=COLOR_ANGLE_C)
        # label_C.move_to(arc_label_pos(C, A, B, dist=0.85))

        # self.play(
        #     ShowCreation(arc_A),
        #     ShowCreation(arc_B),
        #     ShowCreation(arc_C),
        #     run_time=1.4,
        # )
        # self.play(
        #     Write(label_A),
        #     Write(label_B),
        #     Write(label_C),
        #     run_time=0.8,
        # )
        # self.wait(0.4)

    