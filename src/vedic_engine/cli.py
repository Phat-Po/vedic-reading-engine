"""Command line entrypoint for Vedic chart calculations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .calculator import VedicCalculator
from .renderer import ChartRenderer
from .schemas import CalculateRequest


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="vedic-calculate",
        description="Calculate a Vedic birth chart and render SVG charts.",
    )
    parser.add_argument("--sample", action="store_true", help="Run the bundled 1995-07-21 sample.")
    parser.add_argument("--input", type=Path, help="Path to a CalculateRequest JSON file.")

    # Direct parameters — no JSON file needed
    parser.add_argument("--date", help="Birth date: YYYY-MM-DD")
    parser.add_argument("--time", default="12:00:00", help="Birth time: HH:MM:SS (default 12:00:00)")
    parser.add_argument("--tz", default="UTC", help="Timezone, e.g. Asia/Shanghai (default UTC)")
    parser.add_argument("--lat", type=float, default=0.0, help="Latitude (default 0)")
    parser.add_argument("--lon", type=float, default=0.0, help="Longitude (default 0)")
    parser.add_argument("--alt", type=float, default=0.0, help="Altitude in meters (default 0)")
    parser.add_argument("--gender", choices=["male", "female"], help="Gender: male or female")
    parser.add_argument("--name", help="Label for this chart")
    parser.add_argument(
        "--type", dest="analysis_type", default="natal",
        choices=["natal", "dasha", "investment", "relationship", "career", "health", "prashna"],
        help="Analysis type (default natal)",
    )
    parser.add_argument("--depth", type=int, default=2, help="Dasha depth 2–4 (default 2)")

    # Output control
    parser.add_argument("--json-only", action="store_true", help="Print chart JSON only, no SVG.")
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("output"),
        help="Directory for SVG output files (default output/).",
    )

    args = parser.parse_args()

    # --- Build request -------------------------------------------------------
    if args.sample:
        data = {
            "name": "sample-1995",
            "gender": "male",
            "birth": {
                "date": "1995-07-21",
                "time": "11:35:00",
                "timezone": "Asia/Taipei",
                "latitude": 25.0378,
                "longitude": 121.565,
            },
            "analysis_type": args.analysis_type,
            "ayanamsa": "lahiri",
            "dasha_depth": args.depth,
        }
    elif args.input:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    elif args.date:
        data = {
            "name": args.name or "cli-chart",
            "gender": args.gender,
            "birth": {
                "date": args.date,
                "time": args.time,
                "timezone": args.tz,
                "latitude": args.lat,
                "longitude": args.lon,
                "altitude_m": args.alt,
            },
            "analysis_type": args.analysis_type,
            "ayanamsa": "lahiri",
            "dasha_depth": args.depth,
        }
    else:
        parser.error("Use --sample, --input, or --date with direct parameters.")

    # --- Calculate -----------------------------------------------------------
    request = CalculateRequest.model_validate(data)
    chart = VedicCalculator().calculate(request)
    print(json.dumps(chart, ensure_ascii=False, indent=2))

    # --- Render SVGs ---------------------------------------------------------
    if args.json_only:
        return

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    renderer = ChartRenderer()
    slug = (args.name or "chart").replace(" ", "-")

    styles = {
        "south": renderer.south_indian,
        "north": renderer.north_indian,
        "east": renderer.east_indian,
    }
    for style, fn in styles.items():
        path = out / f"{slug}-{style}.svg"
        path.write_text(fn(chart), encoding="utf-8")
        print(f"[svg] {path}", file=sys.stderr)

    dasha_path = out / f"{slug}-dasha.svg"
    dasha_path.write_text(renderer.dasha_timeline(chart), encoding="utf-8")
    print(f"[svg] {dasha_path}", file=sys.stderr)

    shadbala_path = out / f"{slug}-shadbala.svg"
    shadbala_path.write_text(renderer.shadbala_bar(chart), encoding="utf-8")
    print(f"[svg] {shadbala_path}", file=sys.stderr)
