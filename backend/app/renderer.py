from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .settings import settings


class RenderError(RuntimeError):
    def __init__(self, message: str, log: str = ""):
        super().__init__(message)
        self.log = log


def render_scene(scene_file: Path, scene_name: str, out_dir: Path,
                 resolution: str | None = None) -> tuple[Path, str]:
    """Render one scene and return the mp4 plus the render log.

    manimgl imports pyglet at module scope, which opens an X display even
    though nothing is shown, so it runs under a virtual server.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    resolution = resolution or settings.default_resolution

    command = [
        "xvfb-run", "-a", "-s", "-screen 0 1280x1024x24",
        "manimgl",
        "--config_file", str(settings.manim_config),
        str(scene_file), scene_name,
        "-w",
        "-r", resolution,
        "--video_dir", str(out_dir),
    ]
    env = {**os.environ, "PYTHONPATH": str(settings.repo_dir)}

    try:
        finished = subprocess.run(
            command,
            cwd=str(settings.repo_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=settings.render_timeout,
        )
    except subprocess.TimeoutExpired as err:
        raise RenderError(
            f"render timed out after {settings.render_timeout}s", str(err)
        ) from err

    log = (finished.stdout or "") + (finished.stderr or "")
    video = out_dir / f"{scene_name}.mp4"

    if finished.returncode != 0 or not video.exists():
        raise RenderError(_summarise(log) or "manimgl failed", log)
    # A partial file is left behind when ffmpeg is interrupted
    if video.stat().st_size < 1024:
        raise RenderError("manimgl produced an empty video", log)
    return video, log


def _summarise(log: str) -> str:
    """Pull the interesting line out of a very noisy progress-bar log."""
    lines = [line.rstrip() for line in log.splitlines() if line.strip()]
    for line in reversed(lines):
        if any(word in line for word in ("Error", "error:", "Exception", "Traceback")):
            return line.strip()
    return lines[-1].strip() if lines else ""
