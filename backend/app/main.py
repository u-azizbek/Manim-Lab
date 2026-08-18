from __future__ import annotations

import re
from dataclasses import asdict

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse

from .jobs import store
from .music import MusicError, list_tracks, resolve_track
from .settings import settings

app = FastAPI(title="Manim-Lab Shorts Studio", version="1.0.0")

# The frontend is served same-origin through nginx in the compose stack; this
# is here so `npm run dev` on the host can talk to the container too.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ACCEPTED_IMAGES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
TEST_PATTERN = re.compile(r"^[A-Za-z]{1,3}\d{1,2}$")
MAX_IMAGE_BYTES = 12 * 1024 * 1024


def _payload(job) -> dict:
    data = asdict(job)
    data["label"] = job.label
    data["video_url"] = f"/api/jobs/{job.id}/video" if job.status == "done" else None
    data["music_video_url"] = (
        f"/api/jobs/{job.id}/music-video" if job.has_music else None
    )
    return data


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "model": settings.model,
        "resolution": settings.default_resolution,
        "api_key_configured": bool(settings.anthropic_api_key),
    }


@app.post("/api/jobs")
async def create_job(
    background: BackgroundTasks,
    test: str = Form(...),
    question: int = Form(...),
    # A problem arrives either as a screenshot or typed out as LaTeX. Both are
    # optional individually; at least one has to be there.
    image: UploadFile | None = File(None),
    problem: str = Form(""),
    notes: str = Form(""),
    resolution: str = Form(""),
) -> dict:
    if not TEST_PATTERN.match(test):
        raise HTTPException(422, "test should look like F1, A2 or E3")
    if not 1 <= question <= 999:
        raise HTTPException(422, "question should be between 1 and 999")

    problem = problem.strip()
    if len(problem) > settings.max_problem_chars:
        raise HTTPException(413, f"problem is longer than {settings.max_problem_chars} characters")

    data: bytes | None = None
    media_type = ""
    # An empty file input still arrives as an UploadFile with no filename
    if image is not None and image.filename:
        if image.content_type not in ACCEPTED_IMAGES:
            raise HTTPException(415, f"unsupported image type: {image.content_type}")
        data = await image.read()
        if not data:
            raise HTTPException(422, "the uploaded image is empty")
        if len(data) > MAX_IMAGE_BYTES:
            raise HTTPException(413, "image is larger than 12 MB")
        media_type = image.content_type

    if data is None and not problem:
        raise HTTPException(422, "upload a screenshot or type the problem in LaTeX")

    job = store.create(
        test.upper(), question, data, media_type, problem, notes, resolution,
    )
    background.add_task(store.run, job.id, data, media_type, notes)
    return _payload(job)


@app.get("/api/jobs")
def list_jobs() -> list[dict]:
    return [_payload(job) for job in store.list()]


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(404, "no such job")
    return _payload(job)


@app.get("/api/jobs/{job_id}/video")
def get_video(job_id: str):
    job = store.get(job_id)
    if job is None:
        raise HTTPException(404, "no such job")
    path = store.video_path(job_id)
    if job.status != "done" or not path.exists():
        raise HTTPException(409, "this job has no video yet")
    return FileResponse(
        path,
        media_type="video/mp4",
        filename=f"{job.test}Q{job.question}.mp4",
    )


@app.get("/api/jobs/{job_id}/code", response_class=PlainTextResponse)
def get_code(job_id: str) -> str:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(404, "no such job")
    return job.code or "# not generated yet"


# --- Background music ------------------------------------------------------

@app.get("/api/music")
def get_music() -> list[dict]:
    return list_tracks()


@app.get("/api/music/{track_id}/audio")
def stream_track(track_id: str):
    try:
        path = resolve_track(track_id)
    except MusicError as err:
        raise HTTPException(404, str(err))
    return FileResponse(path, filename=path.name)


@app.post("/api/jobs/{job_id}/music")
def add_music(
    job_id: str,
    track: str = Form(...),
    start: float = Form(0.0),
    volume: float = Form(0.6),
    fade_in: float = Form(0.5),
    fade_out: float = Form(1.5),
    loop: bool = Form(False),
) -> dict:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(404, "no such job")
    try:
        job = store.apply_music(
            job_id, track,
            start=max(0.0, start),
            volume=max(0.0, min(volume, 2.0)),
            fade_in=max(0.0, fade_in),
            fade_out=max(0.0, fade_out),
            loop=loop,
        )
    except MusicError as err:
        raise HTTPException(422, str(err))
    return _payload(job)


@app.delete("/api/jobs/{job_id}/music")
def drop_music(job_id: str) -> dict:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(404, "no such job")
    return _payload(store.remove_music(job_id))


@app.get("/api/jobs/{job_id}/music-video")
def get_music_video(job_id: str):
    job = store.get(job_id)
    if job is None:
        raise HTTPException(404, "no such job")
    path = store.music_video_path(job_id)
    if not job.has_music or not path.exists():
        raise HTTPException(409, "this job has no music track yet")
    return FileResponse(
        path, media_type="video/mp4", filename=f"{job.test}Q{job.question}_music.mp4",
    )
