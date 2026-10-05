from manim_imports_ext import *


# Render with:
#   ./render.sh _2026/Physics/burgers_vortex.py
#
# The Burgers vortex, an exact steady solution of the Navier-Stokes equations:
#   u_r = -a r / 2,   u_z = a z,   u_theta = Gamma / (2 pi r) (1 - exp(-r^2 / delta^2)).
# The strain pulls fluid inward (u_r) and stretches it along the axis (u_z);
# viscosity balances the stretching and fixes the core radius delta.
# Fluid parcels follow r = r0 e^{-at/2}, z = z0 e^{at} exactly, and the swirl
# theta(t) is integrated numerically.  Parcels starting nearer the mid-plane
# (smaller |z0|) live longer, so they spiral further in before shooting up or
# down the core.
#
# The 3D is projected by hand from a camera circling the axis.  Streamlines
# are drawn thicker and brighter where they are nearer the viewer; bright
# pulses ride along them at the true flow speed.

A_STRAIN = 1.0
GAMMA = 40.0
DELTA = 0.65
Z_MAX = 3.4
DT = 0.02
N_LINES = 72
Z_SCALE = 1.42          # stretch the axis on screen so the figure fills the portrait frame
XY_SCALE = 1.12
ELEVATION = 12 * DEG
SPIN_RATE = 0.32        # camera turn, radians per second
FLOW_RATE = 1.6         # flow time per second of video
TAIL = 26

OUTER = "#35D0E6"
SPIRALS = ["#3A7BEA", "#4F6BFF", "#2F95F0"]
CORE = "#F5A742"


def radius_color(r, spiral, core):
    """Cyan out in the inflow, then the line's own colour: blue spiral or orange core."""
    if r > 1.4:
        return interpolate_color(spiral, OUTER, min((r - 1.4) / 0.8, 1.0))
    if core and r < 0.75:
        return interpolate_color(CORE, spiral, np.clip((r - 0.45) / 0.3, 0, 1))
    return Color(spiral)


def streamline(r0, theta0, z0, spiral, core):
    t = np.arange(0, np.log(Z_MAX / abs(z0)) / A_STRAIN, DT)
    r = r0 * np.exp(-A_STRAIN * t / 2)
    z = z0 * np.exp(A_STRAIN * t)
    omega = GAMMA / (2 * PI * r ** 2) * (1 - np.exp(-(r / DELTA) ** 2))
    theta = theta0 + np.cumsum(omega) * DT
    points = np.array([r * np.cos(theta), r * np.sin(theta), z]).T
    rgba = np.array([[*color_to_rgb(radius_color(ri, spiral, core)), 1.0] for ri in r])
    return points, rgba


def project(points, phi):
    """Camera circling the z-axis at a small elevation; returns screen points and depth in [0, 1]."""
    x, y, z = points.T
    toward = np.cos(phi) * x + np.sin(phi) * y
    across = -np.sin(phi) * x + np.cos(phi) * y
    sx = XY_SCALE * across
    sy = Z_SCALE * z * np.cos(ELEVATION) - XY_SCALE * toward * np.sin(ELEVATION)
    depth = toward * np.cos(ELEVATION) + z * np.sin(ELEVATION)
    return np.array([sx, sy, 0 * sx]).T, np.clip((depth + 3) / 6, 0, 1)


class BurgersVortex(BrandOutroMixin, ShortsScene):
    """Streamlines of the Burgers vortex: inward spiral, axial stretching, vortex core."""

    sections = ["vortex", "outro"]

    def vortex(self):
        rng = np.random.default_rng(7)
        # Parcels released nearer the mid-plane live longer and end up in the core
        seeds = [
            (
                rng.uniform(1.9, 3.0), rng.uniform(0, TAU),
                sign * 10 ** (rng.uniform(-2.0, -1.35) if core else rng.uniform(-1.2, -0.45)),
                SPIRALS[k % len(SPIRALS)], core,
            )
            for sign in (1, -1) for k in range(N_LINES // 2) for core in [k % 5 < 2]
        ]
        flows = [streamline(*seed) for seed in seeds]
        stagger = rng.uniform(0, 0.3, len(flows))
        phases = rng.uniform(0, 1, len(flows))

        lines = VGroup(*[VMobject().set_stroke(width=1.5) for _ in flows])
        comets = VGroup(*[VMobject().set_stroke(width=3.5) for _ in flows])
        clock = ValueTracker(0)
        grow = ValueTracker(0)
        glow = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def refresh(group):
            phi = 0.6 + SPIN_RATE * clock.get_value()
            g = grow.get_value()
            for k, ((points, rgba), line, comet) in enumerate(zip(flows, lines, comets)):
                count = len(points)
                shown = int(count * np.clip(1.3 * g - stagger[k], 0, 1))
                shown = max(shown, 2)
                flat, near = project(points[:shown], phi)
                line.set_points_as_corners(flat)
                colors = rgba[:shown].copy()
                colors[:, 3] = 0.3 + 0.6 * near
                line.set_rgba_array(resize_with_interpolation(colors, line.get_num_points()), name="stroke_rgba")
                line.set_stroke(width=0.9 + 1.9 * near)

                # A bright pulse riding the streamline at the flow speed
                head = int((phases[k] * (count + TAIL) + clock.get_value() * FLOW_RATE / DT) % (count + TAIL))
                lo, hi = max(head - TAIL, 0), min(head, shown)
                if hi - lo < 2 or glow.get_value() == 0:
                    comet.set_points_as_corners([flat[0], flat[0]]).set_stroke(opacity=0)
                    continue
                seg_flat, seg_near = project(points[lo:hi], phi)
                comet.set_points_as_corners(seg_flat)
                bright = rgba[lo:hi].copy()
                bright[:, :3] = 0.45 * bright[:, :3] + 0.55
                bright[:, 3] = glow.get_value() * np.linspace(0, 1, hi - lo) * (0.4 + 0.6 * seg_near)
                comet.set_rgba_array(resize_with_interpolation(bright, comet.get_num_points()), name="stroke_rgba")
                comet.set_stroke(width=1.6 + 3.0 * seg_near)

        field = VGroup(lines, comets)
        field.add_updater(refresh)

        # The axis the fluid is stretched along, pointing both ways
        top, bottom = 5.2 * UP, 5.2 * DOWN
        axis = VGroup(
            Line(bottom, top).set_stroke(GREY_B, 2, opacity=0.8),
            ArrowTip().set_fill(GREY_B).scale(0.6).rotate(PI / 2).move_to(top),
            ArrowTip().set_fill(GREY_B).scale(0.6).rotate(-PI / 2).move_to(bottom),
        )
        title = Text("Navier–Stokes Millennium Problem", font_size=46, weight=BOLD)
        title.set_color_by_gradient(OUTER, SPIRALS[1], CORE).set_max_width(7.4).move_to(6.5 * UP)
        self.add(axis, field, title)
        self.play(grow.animate.set_value(1), FadeIn(axis), Write(title), run_time=2.6, rate_func=smooth)
        self.play(glow.animate.set_value(1), run_time=0.8)

        # Labels, each with a leader line
        def label(text, spot, target):
            words = Text(text, font_size=34).set_color(GREY_A).move_to(spot)
            start = words.get_bottom() + 0.1 * DOWN if target[1] < spot[1] else words.get_top() + 0.1 * UP
            leader = Line(start, target).set_stroke(GREY_B, 1.5)
            return VGroup(words, leader)

        labels = [
            label("inward spiral", np.array([-2.35, 2.2, 0]), np.array([-2.55, 0.35, 0])),
            label("axial stretching", np.array([2.05, 5.55, 0]), np.array([0.15, 4.75, 0])),
            label("vortex core", np.array([2.2, -5.9, 0]), np.array([0.3, -3.1, 0])),
        ]
        for tag in labels:
            self.play(FadeIn(tag[0], 0.15 * DOWN), ShowCreation(tag[1]), run_time=0.7)
            self.wait(1.2)
        self.wait(4.0)

        # Freeze before the outro sweeps the frame
        field.clear_updaters()
        clock.clear_updaters()
