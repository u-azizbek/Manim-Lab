from __future__ import annotations

import os
from pathlib import Path


class Settings:
    """Everything the service needs, all overridable from the environment."""

    # Where the Manim-Lab checkout is mounted (read-only).  Generated scenes
    # import `manim_imports_ext` from here.
    repo_dir = Path(os.environ.get("REPO_DIR", "/repo"))
    # Writable scratch space: one directory per job.
    workspace_dir = Path(os.environ.get("WORKSPACE_DIR", "/workspace"))
    manim_config = Path(os.environ.get("MANIM_CONFIG", "/srv/manim_config.docker.yml"))
    # Where the user drops background-music files (read-only repo mount)
    music_dir = Path(os.environ.get("MUSIC_DIR", "/repo/BG Music"))

    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    max_problem_chars = int(os.environ.get("MAX_PROBLEM_CHARS", "4000"))
    # Sonnet handles this well and costs a fraction of Opus. Set
    # ANTHROPIC_MODEL=claude-haiku-4-5-20251001 to go cheaper still.
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
    max_tokens = int(os.environ.get("ANTHROPIC_MAX_TOKENS", "8000"))

    # 1080x1920 is the final Shorts size; 540x960 renders roughly 4x faster.
    default_resolution = os.environ.get("RENDER_RESOLUTION", "1080x1920")
    render_timeout = int(os.environ.get("RENDER_TIMEOUT", "900"))
    # Generated code often needs one small correction; feed the traceback back
    # to the model this many times before giving up.
    repair_attempts = int(os.environ.get("REPAIR_ATTEMPTS", "1"))

    @property
    def jobs_dir(self) -> Path:
        return self.workspace_dir / "jobs"


settings = Settings()
