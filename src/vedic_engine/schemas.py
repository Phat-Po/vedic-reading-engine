"""Pydantic input models for the API and CLI."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BirthData(BaseModel):
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(pattern=r"^\d{2}:\d{2}:\d{2}$")
    timezone: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude_m: float = 0


class CalculateRequest(BaseModel):
    name: str | None = None
    birth: BirthData
    analysis_type: Literal["natal", "dasha", "investment", "relationship", "career", "health", "prashna"] = "natal"
    ayanamsa: Literal["lahiri"] = "lahiri"
    dasha_depth: int = Field(default=2, ge=2, le=4)


class InterpretRequest(CalculateRequest):
    chart: dict | None = None


class TransitRequest(BaseModel):
    birth: BirthData
    target_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    target_time: str = Field(default="12:00:00", pattern=r"^\d{2}:\d{2}:\d{2}$")


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
