from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

from vedic_engine.api import app
from vedic_engine.calculator import VedicCalculator
from vedic_engine.interpreter import InterpretationEngine
from vedic_engine.renderer import ChartRenderer


FIXTURE = Path(__file__).parent / "fixtures" / "sample_birth_1995.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_sample_chart_matches_key_golden_values() -> None:
    chart = VedicCalculator().calculate(load_fixture())

    assert chart["meta"]["version"] == "0.2.0"
    assert chart["ayanamsa"]["name"] == "Lahiri"
    assert abs(chart["ayanamsa"]["value_degrees"] - 23.797701) < 0.02

    sun = chart["planets"]["sun"]
    moon = chart["planets"]["moon"]
    asc = chart["planets"]["ascendant"]
    rahu = chart["planets"]["rahu"]

    assert sun["sign"]["index"] == 4
    assert sun["house"] == 11
    assert moon["sign"]["index"] == 1
    assert moon["house"] == 8
    assert moon["nakshatra"]["name_en"] == "Bharani"
    assert moon["nakshatra"]["pada"] == 3
    assert asc["sign"]["index"] == 6
    assert asc["house"] == 1
    assert rahu["sign"]["index"] == 7
    assert rahu["house"] == 2
    assert rahu["retrograde"] is True

    assert chart["ashtakavarga"]["sarvashtakavarga"]["5"] == 23
    assert chart["dashas"]["golden_reference"]["rahu_major_start"].startswith("2024")
    assert chart["shadbala"]["status"] == "full-calculation"
    assert chart["ashtakavarga"]["status"] == "full-calculation"


def test_svg_renderers_return_svg() -> None:
    chart = VedicCalculator().calculate(load_fixture())
    renderer = ChartRenderer()
    for style in ["south", "north", "east"]:
        svg = renderer.render(chart, style)
        assert svg.startswith("<svg")
        assert "</svg>" in svg
        assert len(svg.encode("utf-8")) < 100_000


def test_interpreter_offline_report_is_rule_bound() -> None:
    chart = VedicCalculator().calculate(load_fixture())
    report = InterpretationEngine().interpret_offline(chart, "natal")
    assert "offline report uses only chart data" in report
    assert "Shopee" not in report
    assert "Amazon" not in report


def test_api_health_and_calculate() -> None:
    client = TestClient(app)
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    response = client.post("/api/v1/calculate", json=load_fixture())
    assert response.status_code == 200
    assert response.json()["planets"]["moon"]["nakshatra"]["name_en"] == "Bharani"


def test_jupiter_whole_sign_drishti_targets() -> None:
    chart = VedicCalculator().calculate(load_fixture())
    jupiter_aspects = chart["aspects"]["by_planet"]["jupiter"]["aspects"]
    targets = {item["aspect_house"]: item["target_sign_index"] for item in jupiter_aspects}

    assert chart["planets"]["jupiter"]["sign"]["index"] == 8
    assert targets == {5: 12, 7: 2, 9: 4}


def test_shadbala_full_calculation_shape_and_sample_ranges() -> None:
    chart = VedicCalculator().calculate(load_fixture())
    shadbala = chart["shadbala"]

    assert shadbala["status"] == "full-calculation"
    sun = shadbala["planets"]["sun"]
    assert sun["status"] == "full-calculation"
    assert 3 <= sun["total_rupa"] <= 7
    assert abs(sun["total_virupas"] / 60 - sun["total_rupa"]) < 0.01
    assert sun["sthana_bala"] < 170
    assert "saptavargaja" in sun["notes"]


def test_ashtakavarga_bav_and_sav_are_rule_based() -> None:
    chart = VedicCalculator().calculate(load_fixture())
    ashtakavarga = chart["ashtakavarga"]

    assert ashtakavarga["status"] == "full-calculation"
    assert ashtakavarga["sarvashtakavarga"]["5"] == 23
    assert 320 <= ashtakavarga["total_bindu"] <= 340
    assert set(ashtakavarga["bhinna_ashtakavarga"]) == {
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    }
    for planet_houses in ashtakavarga["raw_bhinna_ashtakavarga"].values():
        assert len(planet_houses) == 12
        assert all(0 <= value <= 8 for value in planet_houses.values())


def test_yoga_detection_includes_detected_and_missed_rules() -> None:
    chart = VedicCalculator().calculate(load_fixture())
    yogas = {item["name"]: item for item in chart["yogas"]}

    assert len(yogas) >= 20
    assert yogas["Mercury-Venus Conjunction"]["detected"] is True
    assert yogas["Budha-Aditya Yoga"]["detected"] is False
    assert all("detected" in item and "evidence" in item for item in yogas.values())


def test_extended_vargas_include_planet_signs() -> None:
    chart = VedicCalculator().calculate(load_fixture())
    vargas = chart["vargas"]

    assert {"d1", "d2", "d3", "d7", "d9", "d10", "d12", "d30"}.issubset(vargas)
    assert vargas["d1"]["planets"]["sun"]["sign_index"] == 4
    assert vargas["d9"]["planets"]["sun"]["sign_index"] == 5
    assert vargas["d10"]["planets"]["sun"]["sign_index"] == 1
    assert all("planets" in vargas[key] for key in ["d2", "d3", "d7", "d12", "d30"])


def test_vimshopaka_bala_uses_varga_relationships() -> None:
    chart = VedicCalculator().calculate(load_fixture())
    vimshopaka = chart["vimshopaka_bala"]
    sun = vimshopaka["planets"]["sun"]

    assert vimshopaka["status"] == "partial"
    assert sun["score"] > 0
    assert sun["max_score"] == 20
    assert {"d1", "d9", "d10"}.issubset(sun["breakdown"])


def test_sunrise_sunset_uses_ephemeris_with_fallback_shape() -> None:
    chart = VedicCalculator().calculate(load_fixture())
    rise_set = chart["sunrise_sunset"]
    sunrise = datetime.fromisoformat(rise_set["sunrise"])
    sunset = datetime.fromisoformat(rise_set["sunset"])

    assert rise_set["status"] == "calculated"
    assert sunrise.hour == 5 and 15 <= sunrise.minute <= 25
    assert sunset.hour == 18 and 35 <= sunset.minute <= 45


def test_vimshottari_depth_adds_pratyantar_and_sookshma() -> None:
    request = load_fixture()
    request["dasha_depth"] = 3
    depth3 = VedicCalculator().calculate(request)
    first_antar = depth3["dashas"]["periods"][0]["antardashas"][0]
    assert depth3["dashas"]["depth"] == 3
    assert "pratyantar" in first_antar
    assert "sookshma" not in first_antar["pratyantar"][0]

    request["dasha_depth"] = 4
    depth4 = VedicCalculator().calculate(request)
    first_pratyantar = depth4["dashas"]["periods"][0]["antardashas"][0]["pratyantar"][0]
    assert depth4["dashas"]["depth"] == 4
    assert "sookshma" in first_pratyantar


def test_transit_endpoint_detects_sade_sati_phase_one() -> None:
    client = TestClient(app)
    request = {
        "birth": load_fixture()["birth"],
        "target_date": "2026-07-07",
        "target_time": "12:00:00",
    }
    response = client.post("/api/v1/transit", json=request)
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "calculated"
    assert data["saturn_transit"]["sign"]["index"] == 12
    assert data["sade_sati"] == {"active": True, "phase": 1, "saturn_house_from_moon": 12}
    assert data["saturn_transit"]["ashtakavarga_quality"]["scale"] == "bav"
    assert data["rahu_ketu_axis"]
    assert "conjunctions" in data
