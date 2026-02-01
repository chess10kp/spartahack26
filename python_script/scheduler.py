from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo


DAY_INDEX = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}


@dataclass
class AvailabilityBlock:
    weekday: int
    start: time
    end: time


@dataclass
class ScheduleConfig:
    timezone: ZoneInfo
    session_minutes: int
    availability: list[AvailabilityBlock]


@dataclass
class SuggestedSession:
    starts_at: datetime
    ends_at: datetime


def load_schedule(path: str) -> ScheduleConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    tz_name = raw.get("timezone") or "UTC"
    tz = ZoneInfo(tz_name)
    session_minutes = int(raw.get("session_minutes") or 60)

    availability: list[AvailabilityBlock] = []
    for block in raw.get("availability", []):
        day = str(block.get("day", "")).strip().lower()[:3]
        if day not in DAY_INDEX:
            continue
        start_str = str(block.get("start", "")).strip()
        end_str = str(block.get("end", "")).strip()
        if not start_str or not end_str:
            continue
        start = _parse_time(start_str)
        end = _parse_time(end_str)
        availability.append(AvailabilityBlock(DAY_INDEX[day], start, end))

    return ScheduleConfig(timezone=tz, session_minutes=session_minutes, availability=availability)


def _parse_time(value: str) -> time:
    parts = value.split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    return time(hour=hour, minute=minute)


def suggest_session(
    due_at: datetime,
    schedule: ScheduleConfig,
) -> SuggestedSession | None:
    if not schedule.availability:
        return None

    due_at = due_at.astimezone(schedule.timezone)
    session_length = timedelta(minutes=schedule.session_minutes)
    search_start = due_at - timedelta(days=7)

    best_start: datetime | None = None

    for day_offset in range(0, 8):
        day = (search_start + timedelta(days=day_offset)).date()
        weekday = day.weekday()
        for block in schedule.availability:
            if block.weekday != weekday:
                continue
            start_dt = datetime.combine(day, block.start, tzinfo=schedule.timezone)
            end_dt = datetime.combine(day, block.end, tzinfo=schedule.timezone)
            if start_dt + session_length > end_dt:
                continue
            if start_dt + session_length > due_at:
                continue
            if start_dt >= due_at:
                continue
            if best_start is None or start_dt > best_start:
                best_start = start_dt

    if best_start is None:
        return None

    return SuggestedSession(starts_at=best_start, ends_at=best_start + session_length)
