"""FastAPI application for Vedic Engine."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Response

from .calculator import VedicCalculator
from .interpreter import InterpretationEngine
from .renderer import ChartRenderer
from .schemas import CalculateRequest, InterpretRequest, TransitRequest
from .utils import package_root

app = FastAPI(title="Vedic Engine", version="0.2.0")
calculator = VedicCalculator()
renderer = ChartRenderer()
interpreter = InterpretationEngine()


@app.get("/api/v1/health")
def health() -> dict[str, object]:
    ephe = package_root() / "ephe"
    files = ["sepl_18.se1", "semo_18.se1", "seas_18.se1", "fixstars.cat"]
    return {
        "ok": True,
        "ephemeris_mode": calculator._ephemeris_mode(),
        "ephemeris_files": {name: (ephe / name).exists() for name in files},
    }


@app.post("/api/v1/calculate")
def calculate(request: CalculateRequest) -> dict[str, object]:
    try:
        return calculator.calculate(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/chart/{style}")
def chart(style: str, request: CalculateRequest) -> Response:
    try:
        chart_data = calculator.calculate(request)
        svg = renderer.render(chart_data, style)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/dasha")
def dasha(request: CalculateRequest) -> dict[str, object]:
    chart_data = calculator.calculate(request)
    return {"dashas": chart_data["dashas"], "timeline_svg": renderer.dasha_timeline(chart_data)}


@app.post("/api/v1/transit")
def transit(request: TransitRequest) -> dict[str, object]:
    try:
        return calculator.calculate_transit(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/interpret")
async def interpret(request: InterpretRequest) -> dict[str, str]:
    try:
        chart_data = request.chart or calculator.calculate(request)
        report = interpreter.interpret_offline(chart_data, request.analysis_type)
        return {"markdown": report}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/full")
async def full(request: InterpretRequest) -> dict[str, object]:
    chart_data = request.chart or calculator.calculate(request)
    return {
        "chart": chart_data,
        "svg": {
            "south": renderer.south_indian(chart_data),
            "north": renderer.north_indian(chart_data),
            "east": renderer.east_indian(chart_data),
            "dasha": renderer.dasha_timeline(chart_data),
            "shadbala": renderer.shadbala_bar(chart_data),
        },
        "interpretation": interpreter.interpret_offline(chart_data, request.analysis_type),
    }
