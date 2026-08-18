from __future__ import annotations

import subprocess
from pathlib import Path

from .settings import settings


AUDIO_SUFFIXES = {".mp3", ".m4a", ".aac", ".wav", ".ogg", ".flac", ".opus"}


class MusicError(RuntimeError):
    pass


def _duration(path: Path) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nk=1:nw=1", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return round(float(out.stdout.strip()), 2)
    except (ValueError, subprocess.SubprocessError):
        return 0.0


def list_tracks() -> list[dict]:
    """Every audio file currently in the music folder, newest listing each
    call so a freshly-dropped file shows up without a restart."""
    directory = settings.music_dir
    if not directory.exists():
        return []
    tracks = []
    for path in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if path.is_file() and path.suffix.lower() in AUDIO_SUFFIXES:
            tracks.append({
                "id": path.name,
                "name": path.stem,
                "duration": _duration(path),
                "size": path.stat().st_size,
            })
    return tracks


def resolve_track(track_id: str) -> Path:
    """Map a track id to a file, refusing anything outside the music folder."""
    name = Path(track_id).name          # strip any path components
    path = settings.music_dir / name
    if not path.is_file() or path.suffix.lower() not in AUDIO_SUFFIXES:
        raise MusicError(f"no such track: {track_id}")
    return path


def mix_onto_video(
    video: Path,
    track_id: str,
    out: Path,
    start: float = 0.0,
    volume: float = 0.6,
    fade_in: float = 0.5,
    fade_out: float = 1.5,
    loop: bool = False,
) -> Path:
    """Lay a music track under a silent video.

    The video is never re-encoded (`-c:v copy`), so this returns in about a
    second and can be re-run as the user tweaks the controls.

    - `start` seeks into the track, so a long track can begin at its best part.
    - The result is trimmed to the video's length (`-t`).
    - A short track is padded with silence, or looped if `loop` is set.
    """
    music = resolve_track(track_id)
    duration = _duration(video)
    if duration <= 0:
        raise MusicError("could not read the video duration")

    volume = max(0.0, min(volume, 2.0))
    fade_in = max(0.0, min(fade_in, duration))
    fade_out = max(0.0, min(fade_out, duration))
    fade_out_start = max(0.0, duration - fade_out)
    out.parent.mkdir(parents=True, exist_ok=True)

    command = ["ffmpeg", "-y", "-hide_banner"]
    if loop:
        command += ["-stream_loop", "-1"]      # repeat a short track to fill
        start = 0.0
    if start > 0:
        command += ["-ss", f"{start}"]
    command += ["-i", str(music), "-i", str(video)]

    chain = f"volume={volume}"
    if fade_in > 0:
        chain += f",afade=t=in:st=0:d={fade_in}"
    if fade_out > 0:
        chain += f",afade=t=out:st={fade_out_start}:d={fade_out}"
    if not loop:
        chain += ",apad"                       # silence past the end of a short track

    command += [
        "-filter_complex", f"[0:a]{chain}[a]",
        "-map", "1:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-t", f"{duration}",
        "-movflags", "+faststart",
        str(out),
    ]

    finished = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if finished.returncode != 0 or not out.exists() or out.stat().st_size < 1024:
        tail = (finished.stderr or finished.stdout or "")[-1200:]
        raise MusicError(f"ffmpeg could not add the music.\n{tail}")
    return out
