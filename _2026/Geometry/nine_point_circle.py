from manim_imports_ext import *


# ── Helper functions ──────────────────────────────────────────────────────────

def get_orthocenter(A, B, C):
    """Return the orthocenter of triangle ABC (2D, z=0)."""
    BC = C - B
    AC = C - A
    perp_BC = np.array([-BC[1], BC[0], 0])
    perp_AC = np.array([-AC[1], AC[0], 0])
    mat = np.array([
        [perp_BC[0], -perp_AC[0]],
        [perp_BC[1], -perp_AC[1]],
    ])
    rhs = np.array([B[0] - A[0], B[1] - A[1]])
    try:
        t = np.linalg.solve(mat, rhs)[0]
        return A + t * perp_BC
    except np.linalg.LinAlgError:
        return (A + B + C) / 3


def get_circumcenter(A, B, C):
    """Return the circumcenter of triangle ABC."""
    ax, ay = A[0], A[1]
    bx, by = B[0], B[1]
    cx, cy = C[0], C[1]
    D = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(D) < 1e-10:
        return (A + B + C) / 3
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / D
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / D
    return np.array([ux, uy, 0])


def get_altitude_foot(vertex, p1, p2):
    """Return the foot of the perpendicular from vertex to the line through p1 and p2."""
    d = p2 - p1
    t = np.dot(vertex - p1, d) / np.dot(d, d)
    return p1 + t * d


def make_right_angle_mark(foot, v1, v2, size=0.18):
    """Return a small square at 'foot' between directions toward v1 and v2."""
    d1 = normalize(v1 - foot)
    d2 = normalize(v2 - foot)
    corner = foot + size * d1 + size * d2
    p1 = foot + size * d1
    p2 = foot + size * d2
    mark = VGroup(
        Line(p1, corner),
        Line(p2, corner),
    )
    mark.set_stroke(WHITE, 1.5)
    return mark


# ── Colors ────────────────────────────────────────────────────────────────────

MIDPOINT_COLOR  = YELLOW
ALTITUDE_COLOR  = TEAL_C
EULER_COLOR     = MAROON_B
NPC_COLOR       = BLUE_B


# ── Scene ─────────────────────────────────────────────────────────────────────

class NinePointCircle(InteractiveScene):
    # Triangle vertices — a clear, non-degenerate scalene triangle
    A = np.array([-3.0, -1.8, 0])
    B = np.array([2.8, -1.8, 0])
    C = np.array([0.4,  2.2, 0])

    def construct(self):
        A, B, C = self.A, self.B, self.C

        # Derived geometry
        H = get_orthocenter(A, B, C)
        O = get_circumcenter(A, B, C)

        M_a = (B + C) / 2          # midpoint of BC
        M_b = (A + C) / 2          # midpoint of AC
        M_c = (A + B) / 2          # midpoint of AB

        D = get_altitude_foot(A, B, C)   # foot from A → BC
        E = get_altitude_foot(B, A, C)   # foot from B → AC
        F = get_altitude_foot(C, A, B)   # foot from C → AB

        P = (A + H) / 2            # midpoint of AH
        Q = (B + H) / 2            # midpoint of BH
        R_pt = (C + H) / 2         # midpoint of CH

        N = (O + H) / 2            # nine-point center
        r9 = np.linalg.norm(N - M_a)    # nine-point radius

        # ─── Triangle ────────────────────────────────────────────────────────
        triangle = Polygon(A, B, C)
        triangle.set_stroke(WHITE, 3)
        triangle.set_fill(WHITE, opacity=0.04)

        vertex_dots = VGroup(*(Dot(v, radius=0.07, color=WHITE) for v in [A, B, C]))
        vertex_labels = VGroup(
            Tex("A").next_to(A, DL, buff=0.12),
            Tex("B").next_to(B, DR, buff=0.12),
            Tex("C").next_to(C, UP,  buff=0.12),
        )

        title = Text("Euler's Nine-Point Circle", font_size=40)
        title.to_edge(UP, buff=0.3)

        self.play(Write(title), run_time=0.8)
        self.play(
            ShowCreation(triangle),
            run_time=1.2,
        )
        self.play(
            FadeIn(vertex_dots, lag_ratio=0.3),
            Write(vertex_labels, lag_ratio=0.3),
            run_time=0.8,
        )
        self.wait(0.4)

        # ─── Three midpoints of sides ─────────────────────────────────────────
        mid_dots = VGroup(*(
            Dot(pt, radius=0.09, color=MIDPOINT_COLOR)
            for pt in [M_a, M_b, M_c]
        ))
        mid_label = Text("① Midpoints of sides", font_size=25, color=MIDPOINT_COLOR)
        mid_label.to_corner(UR).shift(DOWN * 0.5)

        self.play(
            FadeIn(mid_dots, lag_ratio=0.35),
            Write(mid_label),
            run_time=1.0,
        )
        self.wait(0.3)

        # ─── Altitudes and their feet ─────────────────────────────────────────
        altitudes = VGroup(
            DashedLine(A, D, dash_length=0.12, color=ALTITUDE_COLOR, stroke_width=1.8),
            DashedLine(B, E, dash_length=0.12, color=ALTITUDE_COLOR, stroke_width=1.8),
            DashedLine(C, F, dash_length=0.12, color=ALTITUDE_COLOR, stroke_width=1.8),
        )
        right_marks = VGroup(
            make_right_angle_mark(D, A, B),
            make_right_angle_mark(E, B, A),
            make_right_angle_mark(F, C, A),
        )
        alt_dots = VGroup(*(
            Dot(pt, radius=0.09, color=ALTITUDE_COLOR)
            for pt in [D, E, F]
        ))
        alt_label = Text("② Feet of altitudes", font_size=25, color=ALTITUDE_COLOR)
        alt_label.next_to(mid_label, DOWN, buff=0.25, aligned_edge=RIGHT)

        self.play(
            ShowCreation(altitudes, lag_ratio=0.35),
            run_time=1.4,
        )
        self.play(
            FadeIn(alt_dots, lag_ratio=0.3),
            FadeIn(right_marks, lag_ratio=0.3),
            Write(alt_label),
            run_time=0.9,
        )
        self.wait(0.3)

        # ─── Orthocenter and midpoints of AH / BH / CH ───────────────────────
        H_dot = Dot(H, radius=0.10, color=EULER_COLOR)
        H_label = Tex("H", color=EULER_COLOR).next_to(H, RIGHT, buff=0.12)

        euler_segs = VGroup(
            DashedLine(A, H, dash_length=0.12, color=EULER_COLOR, stroke_width=1.5),
            DashedLine(B, H, dash_length=0.12, color=EULER_COLOR, stroke_width=1.5),
            DashedLine(C, H, dash_length=0.12, color=EULER_COLOR, stroke_width=1.5),
        )
        euler_dots = VGroup(*(
            Dot(pt, radius=0.09, color=EULER_COLOR)
            for pt in [P, Q, R_pt]
        ))
        euler_label = Text("③ Midpoints to orthocenter", font_size=25, color=EULER_COLOR)
        euler_label.next_to(alt_label, DOWN, buff=0.25, aligned_edge=RIGHT)

        self.play(
            ShowCreation(euler_segs, lag_ratio=0.35),
            GrowFromCenter(H_dot),
            Write(H_label),
            run_time=1.4,
        )
        self.play(
            FadeIn(euler_dots, lag_ratio=0.3),
            Write(euler_label),
            run_time=0.9,
        )
        self.wait(0.3)

        # ─── Nine-point circle ────────────────────────────────────────────────
        nine_circle = Circle(radius=r9)
        nine_circle.move_to(N)
        nine_circle.set_stroke(NPC_COLOR, 3)

        N_dot = Dot(N, radius=0.07, color=NPC_COLOR)
        N_label = Tex("N_9", color=NPC_COLOR, font_size=30).next_to(N, UL, buff=0.1)

        npc_label = Text("Nine-Point Circle", font_size=28, color=NPC_COLOR)
        npc_label.to_edge(DOWN, buff=0.35)

        self.play(
            ShowCreation(nine_circle),
            FadeIn(N_dot),
            Write(N_label),
            Write(npc_label),
            run_time=2.0,
        )
        self.wait(0.5)

        # ─── Finale: flash all 9 points ───────────────────────────────────────
        all_nine = VGroup(*mid_dots, *alt_dots, *euler_dots)
        self.play(
            LaggedStart(*(
                Flash(dot.get_center(), color=WHITE, flash_radius=0.28, line_length=0.15)
                for dot in all_nine
            ), lag_ratio=0.12),
            run_time=2.5,
        )
        self.wait(0.8)
