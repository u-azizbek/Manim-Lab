from manim_imports_ext import *
from scipy.optimize import minimize


# Render with:
#   ./render.sh _2026/Geometry/snub_triheptagonal.py
#
# The snub triheptagonal tiling sr{7,3} of the hyperbolic plane (Poincare disk),
# vertex figure 3.3.3.3.7: a heptagon and four equilateral triangles at every vertex.
#
# Construction.  Start from the heptagonal tiling {7,3}: heptagon centre O at 0,
# a vertex V on the real axis, an edge midpoint M.  The rotations
#   a: 2pi/7 about O,   b: 2pi/3 about V,   c: pi about M
# generate its rotation group.  Pick the one point p whose three images a(p),
# b(p), c(p) all lie the same hyperbolic distance away; the orbit of p is the
# vertex set.  The faces are then the images of
#   the heptagon {a^k p}          -- one per {7,3} face, shrunk and twisted  (red)
#   the triangle {b^k p}          -- one per {7,3} vertex                    (yellow)
#   the three other triangles at p -- two per {7,3} edge                     (cyan)
# The edge p -- c(p) between the two cyan triangles of a {7,3} edge is drawn black.
# Edges are hyperbolic geodesics, sampled by mapping one end to 0, where the
# geodesic is a straight segment, and mapping back.

P_SIDES, Q_SIDES = 7, 3
CUT = 0.985                 # keep faces whose centre is this close to the rim
DISK_R = 3.85
DISK_CENTER = np.array([0, -0.1, 0])

RED = "#FF0000"
CYAN = "#00FFFF"
YELLOW_T = "#FFFF00"
GRID_LIGHT = "#E6E6E6"


# Mobius maps of the disk, as 2x2 complex matrices

def to_zero(z0):
    return np.array([[1, -z0], [-np.conj(z0), 1]], dtype=complex)


def from_zero(z0):
    return np.array([[1, z0], [np.conj(z0), 1]], dtype=complex)


def rotation_about(z0, angle):
    spin = np.array([[np.exp(0.5j * angle), 0], [0, np.exp(-0.5j * angle)]])
    return from_zero(z0) @ spin @ to_zero(z0)


def apply(m, z):
    return (m[0, 0] * z + m[0, 1]) / (m[1, 0] * z + m[1, 1])


def hdist(z, w):
    return 2 * np.arctanh(abs(z - w) / abs(1 - np.conj(z) * w))


def geodesic(z1, z2, samples):
    """Points along the geodesic from z1 towards z2 (z2 excluded)."""
    w = apply(to_zero(z1), z2)
    back = from_zero(z1)
    return [apply(back, s * w) for s in np.linspace(0, 1, samples, endpoint=False)]


def build_tiling():
    circum = np.arccosh(1 / np.tan(PI / P_SIDES) / np.tan(PI / Q_SIDES))
    to_mid = np.arccosh(np.cos(PI / Q_SIDES) / np.sin(PI / P_SIDES))
    V = np.tanh(circum / 2)
    M = np.tanh(to_mid / 2) * np.exp(1j * PI / P_SIDES)
    a, b, c = rotation_about(0, TAU / P_SIDES), rotation_about(V, TAU / Q_SIDES), rotation_about(M, PI)

    def spread(x):
        z = x[0] + 1j * x[1]
        return np.var([hdist(z, apply(g, z)) for g in (a, b, c)])

    x = minimize(spread, [0.2, 0.03], method="Nelder-Mead", options=dict(xatol=1e-12, fatol=1e-18, maxiter=4000)).x
    p = x[0] + 1j * x[1]

    # The faces at p, in angular order: heptagon, yellow triangle, three cyan triangles
    nbrs = [apply(g, p) for g in (a, np.linalg.inv(a), b, np.linalg.inv(b), c)]
    angle_of = lambda z: np.angle(apply(to_zero(p), z))
    nbrs.sort(key=angle_of)
    base_cyan = []
    for n1, n2 in zip(nbrs, nbrs[1:] + nbrs[:1]):
        pair = {np.round(n1, 9), np.round(n2, 9)}
        if pair in ({np.round(apply(a, p), 9), np.round(apply(np.linalg.inv(a), p), 9)},
                    {np.round(apply(b, p), 9), np.round(apply(np.linalg.inv(b), p), 9)}):
            continue
        base_cyan.append([p, n1, n2])

    hept = [apply(np.linalg.matrix_power(a, k), p) for k in range(P_SIDES)]
    grid_face = [apply(np.linalg.matrix_power(a, k), V) for k in range(P_SIDES)]
    yellow = [apply(np.linalg.matrix_power(b, k), p) for k in range(Q_SIDES)]

    # Walk the group, keeping elements that stay inside the disk
    probe = 0.013 + 0.007j
    key = lambda z: (round(z.real, 7), round(z.imag, 7))
    group = {key(probe): np.eye(2, dtype=complex)}
    frontier = list(group.values())
    gens = (a, b, np.linalg.inv(a), np.linalg.inv(b))
    while frontier:
        fresh = []
        for g in frontier:
            for h in gens:
                m = g @ h
                m /= np.sqrt(np.linalg.det(m))
                z = apply(m, probe)
                if abs(z) > 0.997 or key(z) in group:
                    continue
                group[key(z)] = m
                fresh.append(m)
        frontier = fresh

    tiles = dict(hept={}, yellow={}, cyan={}, edges={}, seams={})
    partner = apply(c, p)
    for g in group.values():
        centre = apply(g, 0)
        if abs(centre) < CUT:
            k = key(centre)
            if k not in tiles["hept"]:
                tiles["hept"][k] = ([apply(g, z) for z in hept], [apply(g, z) for z in grid_face], centre)
        centre = apply(g, V)
        if abs(centre) < CUT and key(centre) not in tiles["yellow"]:
            tiles["yellow"][key(centre)] = ([apply(g, z) for z in yellow], centre)
        for tri in base_cyan:
            pts = [apply(g, z) for z in tri]
            centre = np.mean(pts)
            if abs(centre) < CUT and key(centre) not in tiles["cyan"]:
                tiles["cyan"][key(centre)] = (pts, centre)
        e1, e2 = apply(g, V), apply(g, apply(a, V))
        mid = 0.5 * (e1 + e2)
        if abs(mid) < CUT and key(mid) not in tiles["edges"]:
            tiles["edges"][key(mid)] = (e1, e2, mid)
        # The edge p -- c(p), shared by two cyan triangles: drawn in black, as in the classic picture
        e1, e2 = apply(g, p), apply(g, partner)
        mid = 0.5 * (e1 + e2)
        if abs(mid) < CUT and key(mid) not in tiles["seams"]:
            tiles["seams"][key(mid)] = (e1, e2, mid)
    return tiles


def samples_for(centre):
    r = abs(centre)
    return 7 if r < 0.75 else 3 if r < 0.92 else 1


def to_frame(zs):
    return [DISK_CENTER + DISK_R * np.array([z.real, z.imag, 0]) for z in zs]


def polygon(vertices, samples, color, opacity=1.0):
    pts = []
    for z1, z2 in zip(vertices, vertices[1:] + vertices[:1]):
        pts += geodesic(z1, z2, samples)
    shape = VMobject().set_points_as_corners(to_frame(pts + pts[:1]))
    return shape.set_fill(color, opacity).set_stroke(color, 0.6)


def ring(centre):
    """How far out a face is, in hyperbolic distance, for staggering the build."""
    return 2 * np.arctanh(min(abs(centre), 0.9999))


def by_ring(items, centres, chunks=14):
    """Group mobjects into rings, from the centre outward."""
    d = np.array([ring(c) for c in centres])
    edges = np.linspace(0, d.max() + 1e-6, chunks + 1)
    return [VGroup(*[m for m, di in zip(items, d) if lo <= di < hi]) for lo, hi in zip(edges, edges[1:])]


class SnubTriheptagonal(BrandOutroMixin, ShortsScene):
    """sr{7,3} built from the heptagonal tiling: twist the heptagons, add the triangles."""

    sections = ["build", "outro"]

    def build(self):
        tiles = build_tiling()

        title = Text("Snub Triheptagonal Tiling", font_size=56, weight=BOLD)
        title.set_color_by_gradient("#FF5A5A", "#FFFF66", "#33FFFF").set_max_width(7.5).move_to(5.1 * UP)
        rim = Circle(radius=DISK_R).move_to(DISK_CENTER).set_stroke(GREY_B, 2)
        self.play(Write(title), ShowCreation(rim), run_time=1.3)

        # 1. The heptagonal tiling {7,3}
        edge_items, edge_centres = [], []
        for e1, e2, mid in tiles["edges"].values():
            width = 0.3 + 1.9 * (1 - abs(mid) ** 2)
            line = VMobject().set_points_as_corners(to_frame(geodesic(e1, e2, max(samples_for(mid), 2)) + [e2]))
            edge_items.append(line.set_stroke(GRID_LIGHT, width))
            edge_centres.append(mid)
        grid = by_ring(edge_items, edge_centres)
        self.play(LaggedStart(*[ShowCreation(g, lag_ratio=0) for g in grid], lag_ratio=0.35), run_time=3.0)
        self.wait(0.3)

        # 2. Each heptagon of the grid shrinks and twists into a red heptagon
        starts, hepts, hept_centres = [], [], []
        for snub, face, centre in tiles["hept"].values():
            n = samples_for(centre)
            starts.append(polygon(face, n, RED, 0.15))
            hepts.append(polygon(snub, n, RED))
            hept_centres.append(centre)
        start_rings, hept_rings = by_ring(starts, hept_centres), by_ring(hepts, hept_centres)
        self.play(
            LaggedStart(*[FadeIn(s) for s in start_rings], lag_ratio=0.2),
            run_time=1.2,
        )
        self.play(
            LaggedStart(*[ReplacementTransform(s, h) for s, h in zip(start_rings, hept_rings)], lag_ratio=0.25),
            run_time=3.2,
        )

        # 3. A yellow triangle at every vertex of the grid, twisting in
        yellows, yellow_centres, yellow_anims = [], [], []
        for pts, centre in tiles["yellow"].values():
            tri = polygon(pts, samples_for(centre), YELLOW_T)
            seed = tri.copy().scale(0.05).rotate(-PI / 2)
            yellows.append(tri)
            yellow_centres.append(centre)
            yellow_anims.append((seed, tri))
        yellow_rings = by_ring(yellows, yellow_centres)
        seed_rings = by_ring([s for s, _ in yellow_anims], yellow_centres)
        self.play(
            LaggedStart(*[Transform(s, y, remover=True) for s, y in zip(seed_rings, yellow_rings)], lag_ratio=0.25),
            run_time=2.8,
        )
        self.add(*yellow_rings)

        # 4. Cyan triangles fill the gaps; the grid lines settle in black on top
        cyans, cyan_centres = [], []
        for pts, centre in tiles["cyan"].values():
            cyans.append(polygon(pts, samples_for(centre), CYAN))
            cyan_centres.append(centre)
        cyan_rings = by_ring(cyans, cyan_centres)
        self.play(
            LaggedStart(*[FadeIn(c, scale=0.9) for c in cyan_rings], lag_ratio=0.25),
            run_time=2.8,
        )
        # The scaffolding grid goes; the seams between cyan pairs are drawn in black
        seam_items, seam_centres = [], []
        for e1, e2, mid in tiles["seams"].values():
            width = 0.3 + 1.6 * (1 - abs(mid) ** 2)
            line = VMobject().set_points_as_corners(to_frame(geodesic(e1, e2, max(samples_for(mid), 2)) + [e2]))
            seam_items.append(line.set_stroke(BLACK, width))
            seam_centres.append(mid)
        seams = by_ring(seam_items, seam_centres)
        grid_group = VGroup(*grid)
        self.add(grid_group)
        self.play(
            FadeOut(grid_group),
            LaggedStart(*[ShowCreation(s, lag_ratio=0) for s in seams], lag_ratio=0.2),
            rim.animate.set_stroke(CYAN, 2),
            run_time=1.6,
        )
        self.wait(0.6)

        # The finished tiling turns through one seventh, onto itself
        tiling = VGroup(*hept_rings, *yellow_rings, *cyan_rings, *seams)
        self.play(Rotate(tiling, TAU / P_SIDES, about_point=DISK_CENTER), run_time=3.5)
        self.wait(1.0)
