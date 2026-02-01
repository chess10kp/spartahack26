from __future__ import annotations

from datetime import datetime

from canvas_client import get_active_courses, get_course_assignments, get_course_detail
from state_store import save_state


TERM_FILTER = "Spring Semester 2026"


def _parse_iso(dt: str | None) -> str | None:
    if not dt:
        return None
    return datetime.fromisoformat(dt.replace("Z", "+00:00")).astimezone().isoformat()


def sync_canvas_state(output_path: str = "data/workspace.json") -> dict:
    courses = get_active_courses()
    normalized_courses: list[dict] = []
    assignments: list[dict] = []
    course_details: dict[str, dict] = {}

    for course in courses:
        course_id = course.get("id")
        if not course_id:
            continue

        course_id_int = int(course_id)
        detail = get_course_detail(course_id_int)
        term = detail.get("term") or {}
        term_name = term.get("name")
        if term_name != TERM_FILTER:
            continue

        course_details[str(course_id_int)] = {
            "id": course_id_int,
            "name": detail.get("name") or course.get("name"),
            "course_code": detail.get("course_code") or course.get("course_code"),
            "term": term,
            "teacher": detail.get("teacher"),
            "total_students": detail.get("total_students"),
            "public_description": detail.get("public_description"),
            "syllabus_body": detail.get("syllabus_body"),
        }

        normalized_courses.append(
            {
                "id": course_id_int,
                "name": course.get("name") or detail.get("name"),
                "course_code": course.get("course_code") or detail.get("course_code"),
            }
        )

        course_assignments = get_course_assignments(course_id_int)
        for a in course_assignments:
            due_at = _parse_iso(a.get("due_at"))
            assignments.append(
                {
                    "id": a.get("id"),
                    "course_id": course_id_int,
                    "course_name": course.get("name") or detail.get("name"),
                    "name": a.get("name"),
                    "description": a.get("description"),
                    "due_at": due_at,
                    "points_possible": a.get("points_possible"),
                    "submission_types": a.get("submission_types"),
                }
            )

    state = {
        "courses": normalized_courses,
        "course_details": course_details,
        "assignments": assignments,
    }
    save_state(output_path, state)
    return state
