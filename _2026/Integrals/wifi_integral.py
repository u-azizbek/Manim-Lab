import os

from manim_imports_ext import *


SIGN_COLOR = "#B4552A"
ODD_COLOR = BLUE_B
CIRCLE_COLOR = GREEN_B
RESULT_COLOR = YELLOW

INTEGRAL_TEX = R"\int_{-2}^{2} \left( x^3 \cos \frac{x}{2} + \frac{1}{2} \right) \sqrt{4 - x^2} \, dx"

# Drop a photo of the real sign here and the opening shot uses it instead of
# the drawn one
SIGN_IMAGE = os.path.join(os.path.dirname(__file__), "wifi_sign.jpg")


def odd_part(x):
    return x**3 * np.cos(x / 2) * np.sqrt(max(4 - x * x, 0))


def semicircle(x):
    return np.sqrt(max(4 - x * x, 0))


class WifiIntegral(ShortsScene):
    # 9:16 portrait for YouTube Shorts.  Render with:
    #   ./render.sh _2026/Integrals/wifi_integral.py
    # or a single beat with:
    #   ./render.sh -s kill_the_odd_part _2026/Integrals/wifi_integral.py
    sections = [
        "show_sign",
        "split_the_integral",
        "kill_the_odd_part",
        "measure_the_semicircle",
        "reveal_password",
    ]

    # State shared between sections

    def make_header(self):
        header = Tex(INTEGRAL_TEX, font_size=44)
        header.set_width(5.8)
        return self.pin_to_top(header, buff=0.5)

    def get_header(self):
        return self.lazy("header", self.make_header)

    # Pieces of the opening shot

    def get_wifi_icon(self, color=WHITE):
        icon = VGroup(*[
            Arc(start_angle=PI / 4, angle=PI / 2, radius=radius)
            for radius in [0.16, 0.30, 0.44]
        ])
        icon.set_stroke(color, 5)
        icon.add(Dot(radius=0.05, fill_color=color))
        return icon

    def make_sign(self):
        if os.path.exists(SIGN_IMAGE):
            sign = ImageMobject(SIGN_IMAGE)
            sign.set_width(7.0)
            return Group(sign), None

        title = Text("FREE WIFI", font_size=60, weight=BOLD)
        integral = Tex(INTEGRAL_TEX, font_size=40)
        integral.set_width(6.0)

        caption = Text(
            "The Wi-Fi password is the first digits of the answer",
            font_size=21,
        )
        caption.set_width(5.4)
        footer = VGroup(self.get_wifi_icon(), caption)
        footer.arrange(RIGHT, buff=0.25)

        contents = VGroup(title, integral, footer)
        contents.arrange(DOWN, buff=0.55)
        contents.set_color(WHITE)

        card = RoundedRectangle(
            width=contents.get_width() + 0.9,
            height=contents.get_height() + 0.9,
            corner_radius=0.12,
        )
        card.set_fill(SIGN_COLOR, 1).set_stroke(BLACK, 0)
        card.move_to(contents)

        return Group(card, contents), integral

    # Sections

    def show_sign(self):
        sign, integral = self.make_sign()
        sign.move_to(1.2 * UP)

        prompt = Text("Want the password?", font_size=46).set_color(RESULT_COLOR)
        prompt.next_to(sign, DOWN, buff=1.3)

        self.play(FadeIn(sign, scale=1.06), run_time=1.3)
        self.wait(1.2)
        self.play(FadeIn(prompt, 0.2 * UP), run_time=0.8)
        self.wait(1.2)

        # Lift the integral off the sign and pin it as the header
        if integral is None:
            self.play(FadeOut(sign, UP), FadeOut(prompt, UP), run_time=0.9)
            self.get_header()
            return

        integral_copy = integral.copy()
        self.add(integral_copy)
        self.play(
            FadeOut(sign, UP),
            FadeOut(prompt, UP),
            Transform(integral_copy, self.make_header()),
            run_time=1.2,
        )
        self.set_state("header", integral_copy)

    def split_the_integral(self):
        split = VGroup(
            Tex(R"= \int_{-2}^{2} x^3 \cos \frac{x}{2} \sqrt{4 - x^2} \, dx", font_size=44),
            Tex(R"+ \int_{-2}^{2} \frac{1}{2} \sqrt{4 - x^2} \, dx", font_size=44),
        )
        split[0].set_color(ODD_COLOR)
        split[1].set_color(CIRCLE_COLOR)
        split.arrange(DOWN, buff=0.9, aligned_edge=LEFT)
        split.set_width(6.9)
        split.next_to(self.get_header(), DOWN, buff=1.1)

        labels = VGroup(
            Text("odd function", font_size=34).set_color(ODD_COLOR),
            Text("half a circle", font_size=34).set_color(CIRCLE_COLOR),
        )
        for label, part in zip(labels, split):
            label.next_to(part, DOWN, buff=0.35)

        self.play(Write(split[0]), run_time=1.4)
        self.play(FadeIn(labels[0], 0.2 * DOWN), run_time=0.7)
        self.wait(0.5)
        self.play(Write(split[1]), run_time=1.2)
        self.play(FadeIn(labels[1], 0.2 * DOWN), run_time=0.7)
        self.wait(1.2)

        self.play(FadeOut(VGroup(split, labels), UP), run_time=0.8)

    def kill_the_odd_part(self):
        title = Text("Part 1", font_size=38).set_color(ODD_COLOR)
        title.next_to(self.get_header(), DOWN, buff=0.6)

        claim = Tex(R"f(-x) = -f(x)", font_size=56).set_color(ODD_COLOR)
        claim.next_to(title, DOWN, buff=0.5)

        reason = TexText(R"odd $\times$ even $\times$ even = odd", font_size=34)
        reason.set_color(GREY_B)
        reason.next_to(claim, DOWN, buff=0.35)

        axes = Axes(
            x_range=(-2.5, 2.5, 1),
            y_range=(-4, 4, 2),
            width=6.0,
            height=5.2,
            axis_config=dict(stroke_color=GREY_B, stroke_width=2),
        )
        axes.add_coordinate_labels(x_values=[-2, 2], y_values=[], font_size=24)
        axes.next_to(reason, DOWN, buff=0.5)

        graph = axes.get_graph(odd_part, x_range=(-2, 2, 0.01))
        graph.set_stroke(ODD_COLOR, 3)

        right_area = axes.get_area_under_graph(graph, [0, 2], fill_color=GREEN, fill_opacity=0.6)
        left_area = axes.get_area_under_graph(graph, [-2, 0], fill_color=RED, fill_opacity=0.6)

        self.play(FadeIn(title), run_time=0.5)
        self.play(Write(claim), run_time=1.0)
        self.play(FadeIn(reason, 0.2 * DOWN), run_time=0.7)
        self.play(ShowCreation(axes), run_time=0.8)
        self.play(ShowCreation(graph), run_time=1.5)
        self.play(
            FadeIn(right_area),
            FadeIn(left_area),
            run_time=1.0,
        )
        self.wait(0.6)

        # A half turn about the origin is exactly (x, y) -> (-x, -y), so the
        # left lobe lands on the right one: same area, opposite sign
        flipped = left_area.copy()
        self.add(flipped)
        self.play(
            Rotate(flipped, PI, about_point=axes.c2p(0, 0)),
            run_time=1.6,
        )
        self.wait(0.8)

        result = Tex(R"\int_{-2}^{2} f(x) \, dx = 0", font_size=56).set_color(RESULT_COLOR)
        result.next_to(axes, DOWN, buff=0.7)
        result_box = SurroundingRectangle(result, color=RESULT_COLOR, buff=0.2)
        result_box.set_stroke(width=2)

        self.play(
            FadeOut(VGroup(right_area, left_area, flipped)),
            Write(result),
            run_time=1.2,
        )
        self.play(ShowCreation(result_box), run_time=0.5)
        self.wait(1.0)

        self.play(
            FadeOut(VGroup(title, claim, reason, axes, graph, result, result_box), UP),
            run_time=0.8,
        )

    def measure_the_semicircle(self):
        title = Text("Part 2", font_size=38).set_color(CIRCLE_COLOR)
        title.next_to(self.get_header(), DOWN, buff=0.6)

        identity = VGroup(
            Tex(R"y = \sqrt{4 - x^2}", font_size=44),
            Tex(R"\Longleftrightarrow \quad x^2 + y^2 = 4, \; y \ge 0", font_size=44),
        )
        identity.set_color(CIRCLE_COLOR)
        identity.arrange(DOWN, buff=0.4)
        identity.set_width(6.6)
        identity.next_to(title, DOWN, buff=0.5)

        # Equal unit size on both axes, so the semicircle actually looks round
        axes = Axes(
            x_range=(-2.5, 2.5, 1),
            y_range=(-0.5, 2.5, 1),
            unit_size=1.2,
            axis_config=dict(stroke_color=GREY_B, stroke_width=2),
        )
        axes.add_coordinate_labels(x_values=[-2, 2], y_values=[2], font_size=24)
        axes.next_to(identity, DOWN, buff=0.7)

        graph = axes.get_graph(semicircle, x_range=(-2, 2, 0.01))
        graph.set_stroke(CIRCLE_COLOR, 3)
        area = axes.get_area_under_graph(graph, [-2, 2], fill_color=CIRCLE_COLOR, fill_opacity=0.4)

        radius = Line(axes.c2p(0, 0), axes.c2p(2, 0))
        radius.set_stroke(RESULT_COLOR, 4)
        radius_label = Tex("r = 2", font_size=34).set_color(RESULT_COLOR)
        radius_label.next_to(radius, UP, buff=0.15)

        self.play(FadeIn(title), run_time=0.5)
        self.play(Write(identity), run_time=1.4)
        self.play(ShowCreation(axes), run_time=0.8)
        self.play(ShowCreation(graph), run_time=1.4)
        self.play(FadeIn(area), run_time=0.8)
        self.play(ShowCreation(radius), FadeIn(radius_label), run_time=0.8)
        self.wait(0.8)

        half_disc = Tex(R"\frac{1}{2} \pi r^2 = \frac{1}{2} \pi (2)^2 = 2\pi", font_size=44)
        half_disc.set_width(6.0)
        half_disc.next_to(axes, DOWN, buff=0.8)

        halved = Tex(R"\frac{1}{2} \cdot 2\pi = \pi", font_size=52).set_color(RESULT_COLOR)
        halved.next_to(half_disc, DOWN, buff=0.7)
        halved_box = SurroundingRectangle(halved, color=RESULT_COLOR, buff=0.2)
        halved_box.set_stroke(width=2)

        self.play(Write(half_disc), run_time=1.5)
        self.wait(0.5)
        self.play(Write(halved), run_time=1.0)
        self.play(ShowCreation(halved_box), run_time=0.5)
        self.wait(1.0)

        self.play(
            FadeOut(VGroup(title, identity, axes, graph, area, radius, radius_label), UP),
            FadeOut(VGroup(half_disc, halved, halved_box), UP),
            run_time=0.8,
        )

    def reveal_password(self):
        total = Tex(R"0 + \pi = \pi", font_size=64, t2c={R"\pi": RESULT_COLOR})
        total.next_to(self.get_header(), DOWN, buff=1.2)

        digits = Tex(R"\pi = 3.14159 \ldots", font_size=56).set_color(RESULT_COLOR)
        digits.next_to(total, DOWN, buff=1.0)

        password = Text("3141", font_size=110, weight=BOLD).set_color(RESULT_COLOR)
        password.next_to(digits, DOWN, buff=1.1)
        password_box = SurroundingRectangle(password, color=RESULT_COLOR, buff=0.35)
        password_box.set_stroke(width=5)

        label = Text("password", font_size=32).set_color(GREY_A)
        label.next_to(password_box, DOWN, buff=0.4)

        self.play(Write(total), run_time=1.2)
        self.wait(0.5)
        self.play(FadeIn(digits, 0.2 * DOWN), run_time=1.0)
        self.wait(0.5)
        self.play(FadeTransform(digits.copy(), password), run_time=1.0)
        self.play(ShowCreation(password_box), FadeIn(label), run_time=0.6)
        self.play(FlashAround(password, time_width=1.5), run_time=1.5)
        self.wait(1.8)
