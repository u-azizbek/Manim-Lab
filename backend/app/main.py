from __future__ import annotations

import re
from dataclasses import asdict

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse

from .jobs import store
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
    image: UploadFile = File(...),
    test: str = Form(...),
    question: int = Form(...),
    notes: str = Form(""),
    resolution: str = Form(""),
) -> dict:
    if image.content_type not in ACCEPTED_IMAGES:
        raise HTTPException(415, f"unsupported image type: {image.content_type}")
    if not TEST_PATTERN.match(test):
        raise HTTPException(422, "test should look like F1, A2 or E3")
    if not 1 <= question <= 999:
        raise HTTPException(422, "question should be between 1 and 999")

    data = await image.read()
    if not data:
        raise HTTPException(422, "the uploaded image is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "image is larger than 12 MB")

    media_type = "image/jpeg" if image.content_type == "image/jpeg" else image.content_type
    job = store.create(test.upper(), question, data, media_type, notes, resolution)
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
