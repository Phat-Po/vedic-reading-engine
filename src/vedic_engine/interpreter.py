"""Rule-bound Markdown interpretation engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .utils import package_root

FORBIDDEN_CONTEXT_TERMS = [
    "Shopee",
    "Amazon",
    "AI tool",
    "cross-border ecommerce",
    "跨境电商",
    "电商",
    "Amazon",
    "Shopee",
]


class InterpretationEngine:
    def __init__(self, templates_dir: str | Path | None = None, rules_path: str | Path | None = None) -> None:
        self.templates_dir = Path(templates_dir) if templates_dir else package_root() / "templates"
        self.rules_path = Path(rules_path) if rules_path else package_root() / "RULES.md"
        self.rules = self.rules_path.read_text(encoding="utf-8") if self.rules_path.exists() else ""

    def build_prompt(self, chart: dict[str, Any], analysis_type: str = "natal") -> str:
        template = self._load_template(analysis_type)
        compact = self._compact_chart(chart)
        return template.replace("{{CHART_DATA}}", compact).replace("{{RULES}}", self.rules)

    def interpret_offline(self, chart: dict[str, Any], analysis_type: str = "natal") -> str:
        moon = chart["planets"]["moon"]
        asc = chart["planets"]["ascendant"]
        dasha = chart["dashas"]["current"]
        lines = [
            f"# 印度占星{analysis_type.title()}报告",
            "",
            "## Scope",
            "This offline report uses only chart data and does not use biographical context.",
            "",
            "## Core Pattern",
            f"- Identity and body focus: Ascendant in {asc['sign']['name_en']} {asc['degree_dms']} "
            f"({asc['nakshatra']['name_en']} pada {asc['nakshatra']['pada']}) <- ascendant data.",
            f"- Mind pattern: Moon in {moon['sign']['name_en']} house {moon['house']} "
            f"({moon['nakshatra']['name_en']} pada {moon['nakshatra']['pada']}) <- Moon sign, house, nakshatra.",
            f"- Current timing: {dasha['planet']} mahadasha from {dasha['start']} to {dasha['end']} <- Vimshottari timeline.",
            "",
            "## Compliance Self-check",
            "- No concrete industry, platform, product, company, person, or place is inferred.",
            "- Every recommendation must be traceable to chart factors above.",
        ]
        report = "\n".join(lines)
        self.validate_report(report)
        return report

    def validate_report(self, markdown: str) -> None:
        hits = [term for term in FORBIDDEN_CONTEXT_TERMS if term.lower() in markdown.lower()]
        if hits:
            raise ValueError(f"Interpretation appears polluted by non-chart terms: {', '.join(sorted(set(hits)))}")

    def _load_template(self, analysis_type: str) -> str:
        path = self.templates_dir / f"{analysis_type}.md"
        if not path.exists():
            path = self.templates_dir / "natal.md"
        return path.read_text(encoding="utf-8")

    def _compact_chart(self, chart: dict[str, Any]) -> str:
        planets = chart["planets"]
        rows = []
        for key in ["ascendant", "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "rahu", "ketu"]:
            p = planets[key]
            rows.append(
                f"- {key}: {p['sign']['name_en']} {p['degree_dms']}, house {p['house']}, "
                f"{p['nakshatra']['name_en']} pada {p['nakshatra']['pada']}"
            )
        return "\n".join(rows)
