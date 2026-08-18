# Shorts Studio

A small web app that turns a photo of a workbook problem into a rendered
YouTube Short. Upload a screenshot, Claude solves it and writes a scene file
against the `MockTestShort` template, manimgl renders it, and the video comes
back in the browser.

```
frontend/   Vite + Tailwind, served by nginx (also proxies /api)
backend/    FastAPI + the whole manimgl toolchain in one image
```

## Running it

```bash
cp .env.example .env      # then put your key in it
docker compose up --build
```

Open <http://localhost:8080>.

The first build takes a while: the backend image carries a LaTeX
distribution, ffmpeg and Mesa. After that it is cached.

To stop: `docker compose down`. Renders survive in the `studio-workspace`
volume; `docker compose down -v` discards them.

## Settings

All optional, in `.env`:

| Variable | Default | Notes |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | *required* | |
| `ANTHROPIC_MODEL` | `claude-sonnet-5` | `claude-haiku-4-5-20251001` is cheaper still |
| `RENDER_RESOLUTION` | `1080x1920` | the UI can override per job |
| `RENDER_TIMEOUT` | `900` | seconds |
| `REPAIR_ATTEMPTS` | `1` | retries after a failed render, feeding back the traceback |
| `STUDIO_PORT` | `8080` | host port |

## How a job runs

1. `POST /api/jobs` takes the image plus a test id (`F1`, `A2`, `E3`…) and a
   question number, and returns immediately with a job id.
2. The image goes to Claude with a system prompt assembled at request time
   from the real files in this repo — `custom/mock_tests.py`, the
   `StepListMixin`, and two finished F1 scenes as worked examples. Editing the
   template changes what the model writes; nothing is duplicated in the prompt.
3. The reply is written to `/workspace/jobs/<id>/scene.py`. The scene class is
   found by parsing the file for a `MockTestShort` subclass rather than
   trusting the name.
4. manimgl renders it under `xvfb-run`. If it fails, the traceback goes back to
   the model once and the corrected file is rendered again.
5. The browser polls `GET /api/jobs/<id>` and shows the mp4 from
   `GET /api/jobs/<id>/video`.

## Notes on the container

- **OpenGL.** manimgl needs a GL context. The image installs Mesa and forces
  software rasterising (`LIBGL_ALWAYS_SOFTWARE=1`). pyglet opens an X display
  at import time even when rendering to a file, so renders run under Xvfb.
- **manimgl version.** Pinned to the exact upstream commit this repo is
  developed against, so container renders match local ones. Its
  `pyproject.toml` declares no dependencies, so those are installed from
  `backend/manim-requirements.txt`, vendored from the same commit. Update both
  together.
- **LaTeX.** manim's default preamble pulls in `tipa`, which Debian ships as
  its own package rather than inside any `texlive-*` bundle.
- **The repo mount is read-only.** Model-written code executes in this
  container, so it cannot modify the checkout. Renders and the LaTeX cache go
  to a named volume. Treat the app as a local tool: it runs generated code by
  design, so do not expose the port to an untrusted network.

## Background music

Drop audio files (`.mp3`, `.m4a`, `.wav`, `.ogg`, `.flac`, `.opus`) into the
`BG Music/` folder at the repo root. They appear in the music picker under a
finished video automatically -- no restart.

The manim render itself stays **silent**; music is muxed on top afterwards as a
fast ffmpeg step (`-c:v copy`, ~1-2s), so you can tweak and re-apply freely.
Controls:

- **Track** -- any file in `BG Music/`, with its length shown.
- **Start in track** -- seek into a long track so it begins at its best part.
  The audio player above it has a *From player* button that copies its current
  playhead into this field.
- **Volume**, **Fade in**, **Fade out** -- the fade-out matters because the
  track is cut to the video's length.
- **Loop** -- repeat a track shorter than the video; otherwise it plays once and
  the rest is silence. Auto-suggested when the track is too short.

The result is trimmed to exactly the video's length and replaces the preview;
the download link then points at the version with music. *Remove* reverts to the
silent render. Nothing here re-renders the animation.

Endpoints: `GET /api/music`, `GET /api/music/{id}/audio`,
`POST /api/jobs/{id}/music`, `DELETE /api/jobs/{id}/music`,
`GET /api/jobs/{id}/music-video`.

## Adding it to the book series

Generated files land in the workspace volume, not the repo. To keep one, copy
it into `Calculus Mock Tests/<section> Tests/<test>/` and render it the usual
way:

```bash
docker cp manim-lab-backend-1:/workspace/jobs/<id>/scene.py "Calculus Mock Tests/Foundation Tests/F1/f1_42_something.py"
```
