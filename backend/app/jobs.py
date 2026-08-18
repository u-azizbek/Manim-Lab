from __future__ import annotations

import json
import threading
import traceback
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .generator import GenerationError, find_scene_class, generate_scene, repair_scene
from .music import MusicError, mix_onto_video
from .renderer import RenderError, render_scene
from .settings import settings


# generating -> rendering -> done | failed
@dataclass
class Job:
    id: str
    test: str
    question: int
    # "image", "latex", or "both" -- how the problem arrived
    source: str = "image"
    problem: str = ""
    status: str = "queued"
    stage: str = "queued"
    scene_name: str = ""
    code: str = ""
    error: str = ""
    log_tail: str = ""
    attempts: int = 0
    # What each automatic repair pass was reacting to, so a job that
    # eventually succeeded still shows what needed fixing.
    repairs: list[str] = field(default_factory=list)
    resolution: str = ""
    # Background music laid over the finished video (optional, re-runnable)
    has_music: bool = False
    music_track: str = ""
    music_settings: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str = ""

    @property
    def label(self) -> str:
        return f"{self.test}:{self.question}"


class JobStore:
    """Jobs live on disk under the workspace so they survive a restart, with
    an in-memory index for the API."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        settings.jobs_dir.mkdir(parents=True, exist_ok=True)
        self._load_existing()

    # Persistence

    def dir_for(self, job_id: str) -> Path:
        return settings.jobs_dir / job_id

    def _meta_path(self, job_id: str) -> Path:
        return self.dir_for(job_id) / "job.json"

    def _save(self, job: Job) -> None:
        self.dir_for(job.id).mkdir(parents=True, exist_ok=True)
        self._meta_path(job.id).write_text(json.dumps(asdict(job), indent=2))

    def _load_existing(self) -> None:
        for meta in sorted(settings.jobs_dir.glob("*/job.json")):
            try:
                data = json.loads(meta.read_text())
                job = Job(**data)
            except (OSError, TypeError, ValueError):
                continue
            # A job still marked running cannot be running after a restart
            if job.status in ("queued", "generating", "rendering"):
                job.status, job.error = "failed", "interrupted by a restart"
            self._jobs[job.id] = job

    # Queries

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def list(self) -> list[Job]:
        return sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)

    def video_path(self, job_id: str) -> Path:
        return self.dir_for(job_id) / "video" / f"{self._jobs[job_id].scene_name}.mp4"

    def music_video_path(self, job_id: str) -> Path:
        return self.dir_for(job_id) / "music" / f"{self._jobs[job_id].scene_name}.mp4"

    def apply_music(self, job_id: str, track: str, start: float, volume: float,
                    fade_in: float, fade_out: float, loop: bool) -> Job:
        """Mix a track onto a finished render. Fast enough to run inline."""
        job = self._jobs[job_id]
        if job.status != "done":
            raise MusicError("this job has no finished video yet")
        video = self.video_path(job_id)
        if not video.exists():
            raise MusicError("the rendered video is missing")

        mix_onto_video(
            video, track, self.music_video_path(job_id),
            start=start, volume=volume, fade_in=fade_in, fade_out=fade_out, loop=loop,
        )
        job.has_music = True
        job.music_track = track
        job.music_settings = {
            "start": start, "volume": volume,
            "fade_in": fade_in, "fade_out": fade_out, "loop": loop,
        }
        self._save(job)
        return job

    def remove_music(self, job_id: str) -> Job:
        job = self._jobs[job_id]
        path = self.music_video_path(job_id)
        if path.exists():
            path.unlink()
        job.has_music = False
        job.music_track = ""
        job.music_settings = {}
        self._save(job)
        return job

    # The pipeline

    def create(self, test: str, question: int, image: bytes | None,
               media_type: str, problem: str, notes: str, resolution: str) -> Job:
        job = Job(
            id=uuid.uuid4().hex[:12],
            test=test,
            question=question,
            source=("both" if image and problem else "latex" if problem else "image"),
            problem=problem,
            resolution=resolution or settings.default_resolution,
        )
        with self._lock:
            self._jobs[job.id] = job
        directory = self.dir_for(job.id)
        directory.mkdir(parents=True, exist_ok=True)
        # Keep whatever the problem came in as, next to the scene it produced
        if image:
            suffix = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
            (directory / f"problem{suffix.get(media_type, '.png')}").write_bytes(image)
        if problem:
            (directory / "problem.tex").write_text(problem)
        self._save(job)
        return job

    def run(self, job_id: str, image: bytes | None, media_type: str,
            notes: str) -> None:
        """Executed on a worker thread; never raises."""
        job = self._jobs[job_id]
        try:
            self._set(job, status="generating", stage="reading the problem")
            code = generate_scene(
                image, media_type, job.test, job.question, notes, job.problem,
            )

            for attempt in range(settings.repair_attempts + 1):
                job.attempts = attempt + 1
                scene_file = self.dir_for(job.id) / "scene.py"
                scene_file.write_text(code)
                job.code = code

                try:
                    scene_name = find_scene_class(code)
                    self._set(
                        job,
                        status="rendering",
                        stage=f"rendering {scene_name}"
                              + (f" (attempt {attempt + 1})" if attempt else ""),
                        scene_name=scene_name,
                    )
                    video, log = render_scene(
                        scene_file, scene_name,
                        self.dir_for(job.id) / "video",
                        job.resolution,
                    )
                except (GenerationError, RenderError) as err:
                    detail = getattr(err, "log", "") or str(err)
                    if attempt >= settings.repair_attempts:
                        self._set(
                            job, status="failed", stage="failed",
                            error=str(err), log_tail=detail[-4000:],
                            finished_at=_now(),
                        )
                        return
                    job.repairs.append(str(err))
                    self._set(job, status="generating", stage="fixing the code")
                    code = repair_scene(
                        code, detail, job.test, job.question, job.problem,
                    )
                    continue

                self._set(
                    job, status="done", stage="done",
                    log_tail=log[-4000:], error="",
                    finished_at=_now(),
                )
                return
        except Exception as err:                  # noqa: BLE001 - surfaced to the UI
            self._set(
                job, status="failed", stage="failed",
                error=str(err), log_tail=traceback.format_exc()[-4000:],
                finished_at=_now(),
            )

    def _set(self, job: Job, **fields) -> None:
        for key, value in fields.items():
            setattr(job, key, value)
        self._save(job)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


store = JobStore()
