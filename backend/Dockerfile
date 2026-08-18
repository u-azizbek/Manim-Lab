# Renders manimgl scenes headlessly, so this image carries the whole toolchain:
# OpenGL (software rasteriser), a LaTeX distribution and ffmpeg.
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # No GPU in the container, so make Mesa fall back to llvmpipe
    LIBGL_ALWAYS_SOFTWARE=1 \
    GALLIUM_DRIVER=llvmpipe \
    PYTHONPATH=/repo

RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg \
      git \
      # moderngl asks for a standalone GL context; these provide it headlessly
      libgl1 libegl1 libegl-mesa0 libgl1-mesa-dri libglib2.0-0 \
      # pyglet is imported at module scope and opens an X display even when
      # manim renders to a file, so a virtual one has to exist
      xvfb xauth \
      # manim shells out to latex and dvisvgm for every Tex mobject
      dvisvgm \
      texlive-latex-base \
      texlive-latex-recommended \
      texlive-latex-extra \
      texlive-fonts-recommended \
      texlive-fonts-extra \
      texlive-science \
      texlive-lang-english \
      tipa \
      # custom_config.yml renders Text in CMU Serif
      fonts-cmu \
      # manimpango ships no wheel for this platform, so it is built here
      build-essential pkg-config python3-dev \
      libpango1.0-dev libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Pinned to the exact commit the repo is developed against, so container
# renders match local ones.  Its own dependencies are installed from the
# vendored list first -- the package's pyproject.toml declares none.
COPY manim-requirements.txt /tmp/manim-requirements.txt
RUN pip install --no-cache-dir -r /tmp/manim-requirements.txt \
 && pip install --no-cache-dir --no-deps \
      "manimgl @ git+https://github.com/3b1b/manim.git@c5e23d93659d604ff495ffe300bf7d4ef890e538"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /srv
COPY manim_config.docker.yml /srv/manim_config.docker.yml
COPY app /srv/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
