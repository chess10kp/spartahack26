from __future__ import annotations

import re
from pathlib import Path

import requests

from canvas_client import get_active_courses, get_canvas_headers, get_course_files


ALLOWED_EXTENSIONS = {".pdf", ".ppt", ".pptx", ".doc", ".docx"}


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned or "untitled"


def _file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def _download_file(url: str, dest: Path, headers: dict[str, str]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, headers=headers, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def download_lecture_files(
    course_id: int,
    course_name: str,
    headers: dict[str, str],
    output_dir: str | Path = "downloads",
) -> list[Path]:
    downloaded: list[Path] = []
    files = get_course_files(course_id)
    course_dir = Path(output_dir) / _safe_name(course_name)

    for f in files:
        filename = str(f.get("filename") or "")
        if not filename:
            continue
        if _file_extension(filename) not in ALLOWED_EXTENSIONS:
            continue

        download_url = f.get("download_url") or f.get("url")
        if not download_url:
            continue

        dest = course_dir / _safe_name(filename)
        if dest.exists():
            continue

        _download_file(str(download_url), dest, headers=headers)
        downloaded.append(dest)

    return downloaded


def download_lecture_files_for_active_courses(
    output_dir: str | Path = "downloads",
) -> dict[str, list[Path]]:
    results: dict[str, list[Path]] = {}
    headers = get_canvas_headers()
    for course in get_active_courses():
        course_id = course.get("id")
        if not course_id:
            continue
        course_name = course.get("name") or f"Course {course_id}"
        downloaded = download_lecture_files(
            int(course_id),
            course_name,
            headers=headers,
            output_dir=output_dir,
        )
        if downloaded:
            results[course_name] = downloaded
    return results
