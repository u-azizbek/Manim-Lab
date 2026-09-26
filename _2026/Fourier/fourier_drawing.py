"""Drawing pictures with circles: complex Fourier series.

After 3Blue1Brown, "But what is a Fourier series?" (youtu.be/r6sGWTCMz2k).
All of the machinery lives in custom/fourier_kit.py; each scene here only says
what to draw and how to pace it.

Render (landscape; render.sh picks hd from RENDER_QUALITY below):
    ./render.sh _2026/Fourier/fourier_drawing.py FourierEighthNote
    ./render.sh -s zoom _2026/Fourier/fourier_drawing.py FourierEighthNote
    ./render.sh -q 3840x2160 _2026/Fourier/fourier_drawing.py FourierEighthNote

To draw your own picture, drop an SVG into assets/images/vector/ and add:

    class FourierMyPicture(FourierDrawingScene):
        svg_file = "my_picture.svg"

Any SVG works: separate strokes are joined into one loop automatically,
nearest stroke first.  Pictures with lots of fine detail want more vectors
(n_vectors = 301 or so) and a longer cycle_duration.
"""
from manim_imports_ext import *


RENDER_QUALITY = "hd"


class FourierEighthNote(FourierDrawingScene):
    svg_file = "eighth_note.svg"
    title = "Complex Fourier series"
    n_vectors = 101


class FourierPi(FourierDrawingScene):
    """The same pipeline on a Tex glyph instead of an SVG file."""

    title = "Drawing with circles"
    n_vectors = 61
    drawing_height = 5.6
    cycle_duration = 12.0
    zoom_levels = (8.0,)
    sections = ["assemble", "draw", "zoom"]

    def get_source_mobject(self) -> VMobject:
        return Tex(R"\pi")

class FourierMyPicture(FourierDrawingScene):
    svg_file = "anime_myself.svg"
    title = "Complex Fourier series"
    n_vectors = 101
