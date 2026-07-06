"""SVG renderers for Vedic charts and timelines."""

from __future__ import annotations

from html import escape
from typing import Any


class ChartRenderer:
    def render(self, chart: dict[str, Any], style: str = "south") -> str:
        if style == "south":
            return self.south_indian(chart)
        if style == "north":
            return self.north_indian(chart)
        if style == "east":
            return self.east_indian(chart)
        raise ValueError(f"Unsupported chart style: {style}")

    def south_indian(self, chart: dict[str, Any]) -> str:
        positions = {
            10: (0, 0), 11: (1, 0), 12: (2, 0), 1: (3, 0),
            9: (0, 1), 2: (3, 1),
            8: (0, 2), 3: (3, 2),
            7: (0, 3), 6: (1, 3), 5: (2, 3), 4: (3, 3),
        }
        return self._grid_svg(chart, positions, 4, 4, "South Indian D1")

    def east_indian(self, chart: dict[str, Any]) -> str:
        positions = {
            11: (0, 0), 12: (1, 0), 1: (2, 0),
            10: (0, 1), 2: (2, 1),
            9: (0, 2), 8: (1, 2), 3: (2, 2),
            4: (0, 3), 5: (1, 3), 6: (2, 3), 7: (3, 3),
        }
        return self._grid_svg(chart, positions, 4, 4, "East Indian D1")

    def north_indian(self, chart: dict[str, Any]) -> str:
        bodies = self._bodies_by_house(chart)
        cells = []
        for house in range(1, 13):
            angle = (house - 1) * 30 - 90
            x = 220 + 145 * __import__("math").cos(__import__("math").radians(angle))
            y = 220 + 145 * __import__("math").sin(__import__("math").radians(angle))
            cells.append(
                f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-size="12">'
                f'H{house} {escape(", ".join(bodies.get(house, [])))}</text>'
            )
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="440" height="440" viewBox="0 0 440 440">'
            '<rect width="100%" height="100%" fill="white"/>'
            '<path d="M220 20 L420 220 L220 420 L20 220 Z" fill="none" stroke="#222" stroke-width="2"/>'
            '<path d="M20 220 H420 M220 20 V420 M80 80 L360 360 M360 80 L80 360" '
            'fill="none" stroke="#777" stroke-width="1"/>'
            '<text x="220" y="30" text-anchor="middle" font-size="16" font-weight="700">North Indian D1</text>'
            + "".join(cells)
            + "</svg>"
        )

    def dasha_timeline(self, chart: dict[str, Any]) -> str:
        periods = chart["dashas"]["periods"][:9]
        width = 920
        x = 20
        blocks = []
        total_years = sum(p["years"] for p in periods)
        for period in periods:
            block_w = (width - 40) * period["years"] / total_years
            blocks.append(
                f'<rect x="{x:.1f}" y="50" width="{block_w:.1f}" height="42" fill="#e8eef8" stroke="#344"/>'
                f'<text x="{x + block_w / 2:.1f}" y="75" text-anchor="middle" font-size="12">'
                f'{period["planet"]}</text>'
            )
            x += block_w
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="130" viewBox="0 0 {width} 130">'
            '<rect width="100%" height="100%" fill="white"/>'
            '<text x="20" y="28" font-size="16" font-weight="700">Vimshottari Dasha Timeline</text>'
            + "".join(blocks)
            + "</svg>"
        )

    def shadbala_bar(self, chart: dict[str, Any]) -> str:
        rows = chart["shadbala"]["planets"]
        bars = []
        y = 40
        for planet, data in rows.items():
            width = min(320, data["total_rupa"] * 45)
            bars.append(
                f'<text x="20" y="{y + 14}" font-size="12">{planet.title()}</text>'
                f'<rect x="110" y="{y}" width="{width:.1f}" height="18" fill="#d7e7c5"/>'
                f'<text x="{120 + width:.1f}" y="{y + 14}" font-size="12">{data["total_rupa"]}</text>'
            )
            y += 32
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="520" height="{y + 20}" viewBox="0 0 520 {y + 20}">'
            '<rect width="100%" height="100%" fill="white"/>'
            '<text x="20" y="24" font-size="16" font-weight="700">Shadbala</text>'
            + "".join(bars)
            + "</svg>"
        )

    def _grid_svg(self, chart: dict[str, Any], positions: dict[int, tuple[int, int]], cols: int, rows: int, title: str) -> str:
        size = 120
        bodies = self._bodies_by_sign(chart)
        asc_sign = chart["planets"]["ascendant"]["sign"]["index"]
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{cols * size}" height="{rows * size + 34}" '
            f'viewBox="0 0 {cols * size} {rows * size + 34}">',
            '<rect width="100%" height="100%" fill="white"/>',
            f'<text x="{cols * size / 2}" y="22" text-anchor="middle" font-size="16" font-weight="700">{title}</text>',
        ]
        for sign, (col, row) in positions.items():
            x = col * size
            y = row * size + 34
            label = f'{sign}{" ASC" if sign == asc_sign else ""}'
            body_text = escape(", ".join(bodies.get(sign, [])))
            parts.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="none" stroke="#222"/>')
            parts.append(f'<text x="{x + 8}" y="{y + 20}" font-size="12" font-weight="700">{label}</text>')
            parts.append(f'<text x="{x + 8}" y="{y + 44}" font-size="12">{body_text}</text>')
        parts.append("</svg>")
        return "".join(parts)

    def _bodies_by_sign(self, chart: dict[str, Any]) -> dict[int, list[str]]:
        result: dict[int, list[str]] = {}
        short = {"ascendant": "Asc", "rahu": "Ra", "ketu": "Ke"}
        for key, payload in chart["planets"].items():
            sign = payload["sign"]["index"]
            label = short.get(key, key[:2].title())
            if payload.get("retrograde"):
                label += "(R)"
            result.setdefault(sign, []).append(label)
        return result

    def _bodies_by_house(self, chart: dict[str, Any]) -> dict[int, list[str]]:
        result: dict[int, list[str]] = {}
        for key, payload in chart["planets"].items():
            house = payload["house"]
            label = "Asc" if key == "ascendant" else key[:2].title()
            result.setdefault(house, []).append(label)
        return result

