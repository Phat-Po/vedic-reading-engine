"""Shared angle, date, and file helpers."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


def norm360(value: float) -> float:
    return value % 360.0


def sign_index(longitude: float) -> int:
    return int(norm360(longitude) // 30) + 1


def degree_in_sign(longitude: float) -> float:
    return norm360(longitude) % 30.0


def dms_short(degrees: float) -> str:
    total_minutes = round(degrees * 60)
    deg, minute = divmod(total_minutes, 60)
    return f"{deg}\u00b0{minute}'"


def local_to_utc(date_text: str, time_text: str, tz_name: str) -> datetime:
    local = datetime.combine(date.fromisoformat(date_text), time.fromisoformat(time_text))
    return local.replace(tzinfo=ZoneInfo(tz_name)).astimezone(timezone.utc)


def package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def experiment_root() -> Path:
    return Path(__file__).resolve().parents[3]
