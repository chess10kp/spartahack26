from __future__ import annotations

import requests

from config import require_env


def _headers() -> dict[str, str]:
    token = require_env("CANVAS_ACCESS_TOKEN")
    return {"Authorization": f"Bearer {token}"}


def get_canvas_headers() -> dict[str, str]:
    return _headers()


def _base_url() -> str:
    base = require_env("CANVAS_BASE_URL").rstrip("/")
    return base


def _get_all_pages(url: str, params: dict | None = None) -> list[dict]:
    items: list[dict] = []
    while url:
        resp = requests.get(url, headers=_headers(), params=params, timeout=30)
        resp.raise_for_status()
        items.extend(resp.json())
        params = None
        url = resp.links.get("next", {}).get("url")
    return items


def get_active_courses() -> list[dict]:
    url = f"{_base_url()}/api/v1/courses"
    return _get_all_pages(url, params={"per_page": 100, "enrollment_state": "active"})


def get_courses() -> list[dict]:
    return get_active_courses()


def get_course_assignments(course_id: int) -> list[dict]:
    url = f"{_base_url()}/api/v1/courses/{course_id}/assignments"
    return _get_all_pages(url, params={"per_page": 100})


def get_course_files(course_id: int) -> list[dict]:
    url = f"{_base_url()}/api/v1/courses/{course_id}/files"
    return _get_all_pages(url, params={"per_page": 100})


def get_course_detail(course_id: int) -> dict:
    url = f"{_base_url()}/api/v1/courses/{course_id}"
    params = {
        "include[]": [
            "syllabus_body",
            "public_description",
            "term",
            "total_students",
            "teacher",
        ]
    }
    resp = requests.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()
