from __future__ import annotations

from manimlib import *

from custom.shorts import ShortsScene


# Down-right diagonals are added, up-right diagonals are subtracted
POS_COLOR = "#5B8FF9"
NEG_COLOR = "#FF6B6B"
BAND_OPACITY = 0.45
GHOST_OPACITY = 0.40


class LetterGrid(VGroup):
    """A grid of short tex entries, plus the diagonal bands a Sarrus-style
    rule sweeps through it.

    Each row is any sequence of tex strings, so both of these work:

        LetterGrid(["abc", "def"])                  # one character per cell
        LetterGrid([["x_1", "y_1"], ["x_2", "y_2"]])

    Band geometry is read off the placed entries rather than recomputed, so a
    grid can be moved or scaled before its bands are built.
    """

    def __init__(self, rows, cell_width=1.25, cell_height=1.15, font_size=54):
        super().__init__()
        self.n_rows = len(rows)
        self.n_cols = len(rows[0])
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.cells = VGroup(*[
            Tex(entry, font_size=font_size).move_to(self.home(i, j))
            for i, row in enumerate(rows)
            for j, entry in enumerate(row)
        ])
        self.add(self.cells)

    def home(self, i, j):
        return np.array([
            (j - (self.n_cols - 1) / 2) * self.cell_width,
            ((self.n_rows - 1) / 2 - i) * self.cell_height,
            0.0,
        ])

    def cell(self, i, j):
        return self.cells[i * self.n_cols + j]

    def sub_grid(self, rows, cols):
        return VGroup(*[self.cell(i, j) for i in rows for j in cols])

    def band(self, coords, color, thickness=0.68):
        """A translucent stripe running through the given cells."""
        start = self.cell(*coords[0]).get_center()
        end = self.cell(*coords[-1]).get_center()
        vect = end - start
        stripe = RoundedRectangle(
            width=get_norm(vect) + thickness,
            height=thickness,
            corner_radius=thickness / 2,
        )
        stripe.set_fill(color, BAND_OPACITY).set_stroke(width=0)
        stripe.rotate(angle_of_vector(vect))
        stripe.move_to((start + end) / 2)
        return stripe

    def bands(self, spec, color):
        return VGroup(*[self.band(coords, color) for coords, _ in spec])

    def bars(self, lo=0, hi=None, x_buff=0.34, y_buff=0.32):
        """The two vertical rules of determinant notation, around columns
        lo..hi but spanning every row."""
        hi = self.n_cols - 1 if hi is None else hi
        xs = (
            self.cell(0, lo).get_left()[0] - x_buff,
            self.cell(0, hi).get_right()[0] + x_buff,
        )
        top = self.cells.get_top()[1] + y_buff
        bottom = self.cells.get_bottom()[1] - y_buff
        return VGroup(*[
            Line(np.array([x, bottom, 0.0]), np.array([x, top, 0.0]))
            for x in xs
        ]).set_stroke(WHITE, 3)


def terms_of(spec, color, font_size=44, max_width=6.6):
    """The products a set of diagonals spells out, in the diagonals' colour."""
    line = Tex(R" \quad ".join(word for _, word in spec), font_size=font_size)
    line.set_color(color)
    line.set_max_width(max_width)
    return line


class BandDiagramScene(ShortsScene):
    """A short built around a LetterGrid with bands swept through it."""

    # YouTube's UI covers the bottom of a Short
    body_bottom = -5.0

    def center_body(self, *mobjects, under, buff=0.8):
        """Fill the space between an anchor and the safe bottom edge, rather
        than letting a section bunch up under the heading."""
        body = VGroup(*mobjects)
        top = under.get_bottom()[1] - buff
        available = top - self.body_bottom
        if body.get_height() > available:
            body.set_height(available)
        body.set_y((top + self.body_bottom) / 2)
        return body

    def reveal_bands(self, bands, grid, lag_ratio=0.35, run_time=1.5):
        """Fade bands in *behind* the entries, so they stay crisp."""
        bands.set_fill(opacity=0)
        self.add(bands)
        self.bring_to_front(grid.cells)
        self.play(
            LaggedStart(*[
                band.animate.set_fill(opacity=BAND_OPACITY) for band in bands
            ], lag_ratio=lag_ratio),
            run_time=run_time,
        )
