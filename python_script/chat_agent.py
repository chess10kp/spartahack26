from __future__ import annotations

import textwrap
from datetime import datetime

from openai import OpenAI

from scheduler import load_schedule
from state_store import load_state


def _truncate(text: str, limit: int = 400) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _format_assignments(assignments: list[dict]) -> str:
    lines: list[str] = []
    for a in assignments:
        due_at = a.get("due_at") or "No due date"
        name = a.get("name") or "(Untitled)"
        course = a.get("course_name") or f"Course {a.get('course_id')}"
        desc = a.get("description") or ""
        if desc:
            desc = _truncate(desc)
            line = f"- {course} | {name} | Due: {due_at}\n  About: {desc}"
        else:
            line = f"- {course} | {name} | Due: {due_at}"
        lines.append(line)
    return "\n".join(lines)


def _workspace_summary(workspace: dict, schedule_path: str | None, chat_started_at: str) -> str:
    courses = workspace.get("courses", [])
    assignments = workspace.get("assignments", [])
    schedule_summary = ""
    if schedule_path:
        schedule = load_schedule(schedule_path)
        blocks = [
            f"{b.weekday} {b.start.strftime('%H:%M')}-{b.end.strftime('%H:%M')}"
            for b in schedule.availability
        ]
        schedule_summary = (
            "\nUser availability:\n"
            f"- timezone: {schedule.timezone}\n"
            f"- session_minutes: {schedule.session_minutes}\n"
            f"- blocks: {', '.join(blocks) if blocks else 'none'}\n"
        )

    return (
        "StudentWorkspace snapshot:\n"
        f"- chat_started_at: {chat_started_at}\n"
        f"- courses: {len(courses)}\n"
        f"- assignments: {len(assignments)}\n\n"
        "Assignments:\n"
        f"{_format_assignments(assignments)}\n"
        f"{schedule_summary}"
    )


def _find_due_date_response(user_input: str, assignments: list[dict]) -> str | None:
    lowered = user_input.lower()
    if "due date" not in lowered and "when is" not in lowered and "due" not in lowered:
        return None

    best_match: dict | None = None
    for a in assignments:
        name = (a.get("name") or "").strip()
        if not name:
            continue
        if name.lower() in lowered:
            best_match = a
            break

    if best_match is None:
        return None

    course = best_match.get("course_name") or f"Course {best_match.get('course_id')}"
    name = best_match.get("name") or "(Untitled)"
    due_at = best_match.get("due_at") or "No due date"
    return f"{name} ({course}) is due: {due_at}"


def run_chat(workspace_path: str = "data/workspace.json", schedule_path: str | None = None) -> None:
    workspace = load_state(workspace_path)
    if not workspace:
        print(f"No workspace data found at {workspace_path}. Run `python main.py sync` first.")
        return

    client = OpenAI()
    chat_started_at = datetime.now().astimezone().isoformat()
    system_prompt = textwrap.dedent(
        """
        You are UniPilot, a study coach for college students using Canvas.
        Use the StudentWorkspace snapshot to suggest study sessions and priorities.
        Be concise, practical, and reference due dates.
        If the user asks what to work on today, suggest specific assignments and a plan.
        If user schedule is available, align suggestions to it.
        """
    ).strip()

    messages: list[dict] = [
        {
            "role": "system",
            "content": [
                {"type": "input_text", "text": system_prompt},
            ],
        },
        {
            "role": "system",
            "content": [
                {"type": "input_text", "text": _workspace_summary(workspace, schedule_path, chat_started_at)},
            ],
        },
    ]

    print("UniPilot chat started. Type 'terminate' to exit.")
    while True:
        user_input = input("> ").strip()
        if not user_input:
            continue
        if user_input.lower() == "terminate":
            print("Session ended.")
            break

        direct_due = _find_due_date_response(user_input, workspace.get("assignments", []))
        if direct_due:
            print(direct_due)
            messages.append(
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_input}],
                }
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": direct_due}],
                }
            )
            continue

        messages.append(
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_input}],
            }
        )

        response = client.responses.create(
            model="gpt-4.1",
            input=messages,
        )

        assistant_text = getattr(response, "output_text", None)
        if not assistant_text:
            print("(No response text returned.)")
            continue

        messages.append(
            {
                "role": "assistant",
                "content": [{"type": "output_text", "text": assistant_text}],
            }
        )
        print(assistant_text)
