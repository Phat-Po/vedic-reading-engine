"""Command line entrypoint for sample calculations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .calculator import VedicCalculator
from .schemas import CalculateRequest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="Run the bundled 1995-07-21 sample.")
    parser.add_argument("--input", type=Path, help="Path to a CalculateRequest JSON file.")
    args = parser.parse_args()
    if not args.sample and not args.input:
        parser.error("Use --sample or --input.")

    if args.sample:
        data = {
            "name": "sample-1995",
            "birth": {
                "date": "1995-07-21",
                "time": "11:35:00",
                "timezone": "Asia/Taipei",
                "latitude": 25.0378,
                "longitude": 121.565,
            },
            "analysis_type": "natal",
            "ayanamsa": "lahiri",
        }
    else:
        data = json.loads(args.input.read_text(encoding="utf-8"))

    chart = VedicCalculator().calculate(CalculateRequest.model_validate(data))
    print(json.dumps(chart, ensure_ascii=False, indent=2))

