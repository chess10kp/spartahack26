from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import load_env
from canvas_client import get_active_courses, get_course_assignments
from scheduler import load_schedule, suggest_session
from sync_canvas import sync_canvas_state
from chat_agent import run_chat


def _parse_iso(dt: str | None) -> datetime | None:
    if not dt:
        return None
    return datetime.fromisoformat(dt.replace("Z", "+00:00"))


def _week_bounds(start: datetime) -> tuple[datetime, datetime]:
    week_start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    return week_start, week_end


def list_weekly_assignments(week_start: datetime, schedule_path: str | None) -> None:
    courses = get_active_courses()
    course_map = {c.get("id"): c.get("name") for c in courses}

    week_start, week_end = _week_bounds(week_start)

    schedule = load_schedule(schedule_path) if schedule_path else None

    rows: list[dict] = []
    for course_id, course_name in course_map.items():
        if not course_id:
            continue
        assignments = get_course_assignments(course_id)
        for a in assignments:
            due_at = _parse_iso(a.get("due_at"))
            if due_at is None:
                continue
            due_local = due_at.astimezone(week_start.tzinfo)
            if not (week_start <= due_local < week_end):
                continue
            row = {
                "course": course_name or f"Course {course_id}",
                "assignment": a.get("name") or "(Untitled)",
                "due_at": due_local,
            }
            if schedule:
                session = suggest_session(due_local, schedule)
                row["session"] = session
            rows.append(row)

    rows.sort(key=lambda r: r["due_at"])

    if not rows:
        print("No assignments due this week.")
        return

    print("Assignments due this week:")
    for row in rows:
        due_str = row["due_at"].strftime("%Y-%m-%d %I:%M %p %Z")
        line = f"- {row['course']} | {row['assignment']} | Due: {due_str}"
        if row.get("session"):
            session = row["session"]
            session_str = f"{session.starts_at.strftime('%Y-%m-%d %I:%M %p %Z')}"
            line += f" | Suggested session: {session_str}"
        print(line)


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description="simple-canvas")
    subparsers = parser.add_subparsers(dest="command", required=True)

    assignments = subparsers.add_parser("assignments", help="List assignments due this week")
    assignments.add_argument("--week-start", type=str, default=None, help="YYYY-MM-DD")
    assignments.add_argument("--schedule", type=str, default=None, help="Path to schedule JSON")

    sync = subparsers.add_parser("sync", help="Sync Canvas data into a local workspace file")
    sync.add_argument(
        "--output",
        type=str,
        default="data/workspace.json",
        help="Path to write workspace JSON",
    )

    chat = subparsers.add_parser("chat", help="Chat with UniPilot using workspace data")
    chat.add_argument(
        "--workspace",
        type=str,
        default="data/workspace.json",
        help="Path to workspace JSON",
    )
    chat.add_argument(
        "--schedule",
        type=str,
        default=None,
        help="Path to schedule JSON",
    )

    args = parser.parse_args()

    if args.command == "assignments":
        if args.week_start:
            week_start = datetime.fromisoformat(args.week_start)
            if week_start.tzinfo is None:
                week_start = week_start.replace(tzinfo=datetime.now().astimezone().tzinfo)
        else:
            week_start = datetime.now().astimezone()
        list_weekly_assignments(week_start, args.schedule)
    elif args.command == "sync":
        state = sync_canvas_state(args.output)
        print(
            f"Synced {len(state.get('courses', []))} courses and "
            f"{len(state.get('assignments', []))} assignments to {args.output}"
        )
    elif args.command == "chat":
        run_chat(args.workspace, args.schedule)


if __name__ == "__main__":
    main()
