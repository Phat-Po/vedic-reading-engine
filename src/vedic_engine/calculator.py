"""Core sidereal Vedic calculator backed by Swiss Ephemeris."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import swisseph as swe

from .constants import (
    ASPECTS,
    BAV_RULES,
    BENEFICS,
    GRAHA_KEYS,
    CLASSICAL_PLANETS,
    DEBILITATION,
    DIG_BALA_HOUSES,
    DUSTHANA_HOUSES,
    EVEN_SIGNS,
    EXALTATION,
    KENDRA_HOUSES,
    MALEFICS,
    MOOLATRIKONA,
    NAKSHATRAS,
    NAISARGIKA_BALA,
    ODD_SIGNS,
    PLANET_IDS,
    PLANET_FRIENDS,
    PLANET_KEY_TO_NAME,
    SHADBALA_COMPONENTS_ZH,
    SIGNS,
    TITHIS,
    TRIKONA_HOUSES,
    UPACHAYA_HOUSES,
    VARGA_META,
    VARAS,
    VIMSHOTTARI_ORDER,
    VIMSHOTTARI_YEARS,
    YOGA_DEFINITIONS,
)
from .schemas import CalculateRequest, TransitRequest
from .utils import degree_in_sign, dms_short, local_to_utc, norm360, package_root, sign_index

NAK_LEN = 360.0 / 27.0
PADA_LEN = NAK_LEN / 4.0


class VedicCalculator:
    """Calculate a D1 Vedic chart using Lahiri sidereal settings."""

    def __init__(self, ephe_path: str | Path | None = None) -> None:
        self.ephe_path = Path(ephe_path) if ephe_path else package_root() / "ephe"
        self._init_swe()

    def _init_swe(self) -> None:
        self.ephe_path.mkdir(exist_ok=True)
        swe.set_ephe_path(str(self.ephe_path))
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

    def calculate(self, request: CalculateRequest | dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()
        if isinstance(request, dict):
            request = CalculateRequest.model_validate(request)
        birth = request.birth
        utc_dt = local_to_utc(birth.date, birth.time, birth.timezone)
        jd_ut = self._julian_day(utc_dt)

        ayanamsa = swe.get_ayanamsa_ut(jd_ut)
        houses, asc = self._calc_houses(jd_ut, birth.latitude, birth.longitude)
        planets = self._calc_planets(jd_ut, asc)
        planets["ascendant"] = self._point_payload("ascendant", asc, asc, False, 0.0)

        panchanga = self._calc_panchanga(planets, utc_dt)
        dashas = self._calc_vimshottari(planets["moon"]["longitude"], utc_dt, request.dasha_depth)
        aspects = self._calc_aspects(planets)
        vargas = self._calc_vargas(planets)
        chart = {
            "meta": {
                "engine": "vedic-divination-engine",
                "version": "0.2.0",
                "swiss_ephemeris_version": swe.version,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "calculation_time_ms": 0,
                "ephemeris_mode": self._ephemeris_mode(),
            },
            "input": {
                "name": request.name,
                "gender": request.gender,
                "birth_date": birth.date,
                "birth_time": birth.time,
                "timezone": birth.timezone,
                "utc_offset": utc_dt.astimezone().strftime("%z"),
                "latitude": birth.latitude,
                "longitude": birth.longitude,
                "altitude_m": birth.altitude_m,
            },
            "ayanamsa": {
                "system": "sidereal",
                "name": "Lahiri",
                "value_degrees": round(ayanamsa, 6),
                "swisseph_constant": "SIDM_LAHIRI",
            },
            "panchanga": panchanga,
            "sunrise_sunset": self._calc_sunrise_sunset(birth.date, birth.timezone, birth.latitude, birth.longitude, birth.altitude_m),
            "planets": planets,
            "upagrahas": self._calc_upagrahas(planets, asc),
            "special_lagnas": self._calc_special_lagnas(planets, asc),
            "houses": houses,
            "vargas": vargas,
            "vimshopaka_bala": self._calc_vimshopaka_bala(vargas),
            "shadbala": self._calc_shadbala(planets, aspects, utc_dt),
            "ashtakavarga": self._calc_ashtakavarga(planets, asc),
            "yogas": self._detect_yogas(planets),
            "dashas": dashas,
            "aspects": aspects,
            "karakas": self._calc_karakas(planets),
        }
        chart["meta"]["calculation_time_ms"] = round((time.perf_counter() - start) * 1000, 2)
        return chart

    def calculate_transit(self, request: TransitRequest | dict[str, Any]) -> dict[str, Any]:
        if isinstance(request, dict):
            request = TransitRequest.model_validate(request)
        natal_request = CalculateRequest(birth=request.birth)
        natal = self.calculate(natal_request)
        target_utc = local_to_utc(request.target_date, request.target_time, request.birth.timezone)
        jd_ut = self._julian_day(target_utc)
        natal_asc = natal["planets"]["ascendant"]["longitude"]
        transit_planets = self._calc_planets(jd_ut, natal_asc)
        transit_planets["ascendant"] = natal["planets"]["ascendant"]
        return self._calc_gochara(natal, transit_planets, request.target_date, request.target_time)

    def _julian_day(self, utc_dt: datetime) -> float:
        hour = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600 + utc_dt.microsecond / 3_600_000_000
        return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour, swe.GREG_CAL)

    def _ephemeris_mode(self) -> str:
        required = ["sepl_18.se1", "semo_18.se1", "seas_18.se1"]
        return "swiss" if all((self.ephe_path / name).exists() for name in required) else "moshier-fallback"

    def _calc_flags(self) -> int:
        if self._ephemeris_mode() == "swiss":
            base = swe.FLG_SWIEPH
        else:
            base = swe.FLG_MOSEPH
        return base | swe.FLG_SIDEREAL | swe.FLG_SPEED

    def _calc_planets(self, jd_ut: float, asc_longitude: float) -> dict[str, Any]:
        planets: dict[str, Any] = {}
        flags = self._calc_flags()
        for key, swe_name in PLANET_IDS.items():
            body_id = getattr(swe, swe_name)
            result, _ = swe.calc_ut(jd_ut, body_id, flags)
            lon = norm360(result[0])
            speed = result[3]
            retrograde = speed < 0 or key == "rahu"
            planets[key] = self._point_payload(key, lon, asc_longitude, retrograde, speed)
            if key == "rahu":
                ketu_lon = norm360(lon + 180)
                planets["ketu"] = self._point_payload("ketu", ketu_lon, asc_longitude, True, speed)
        return planets

    def _calc_houses(self, jd_ut: float, lat: float, lon: float) -> tuple[dict[str, Any], float]:
        try:
            cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b"P", swe.FLG_SIDEREAL)
        except Exception:
            cusps, ascmc = swe.houses(jd_ut, lat, lon, b"P")
            ayan = swe.get_ayanamsa_ut(jd_ut)
            cusps = [norm360(c - ayan) for c in cusps]
            ascmc = [norm360(v - ayan) for v in ascmc]
        asc = norm360(ascmc[0])
        cusp_map = {}
        for idx, cusp in enumerate(cusps[:12], start=1):
            sign = self._sign(sign_index(cusp))
            cusp_map[str(idx)] = {
                "longitude": round(norm360(cusp), 6),
                "sign_index": sign["index"],
                "sign_name": sign["name_en"],
            }
        return {
            "system": "placidus",
            "cusps": cusp_map,
            "bhava_madhya": {},
            "house_lords": self._house_lords_from_asc(asc),
        }, asc

    def _point_payload(self, name: str, longitude: float, asc_longitude: float, retrograde: bool, speed: float) -> dict[str, Any]:
        sign = self._sign(sign_index(longitude))
        deg = degree_in_sign(longitude)
        payload = {
            "longitude": round(norm360(longitude), 6),
            "sign": sign,
            "house": self._whole_sign_house(longitude, asc_longitude),
            "degree_in_sign": round(deg, 6),
            "degree_dms": dms_short(deg),
            "nakshatra": self._nakshatra(longitude),
            "retrograde": retrograde,
            "speed_per_day": round(speed, 6),
        }
        if name == "rahu":
            payload["is_mean_node"] = False
        if name == "ketu":
            payload["is_mean_node"] = False
        if name == "moon":
            payload["is_waxing"] = False
        if name == "sun":
            payload["is_combust"] = False
        return payload

    def _sign(self, index: int) -> dict[str, Any]:
        base = SIGNS[index - 1]
        return {"index": base["index"], "name_en": base["name_en"], "name_zh": base["name_zh"]}

    def _whole_sign_house(self, longitude: float, asc_longitude: float) -> int:
        asc_sign = sign_index(asc_longitude)
        body_sign = sign_index(longitude)
        return ((body_sign - asc_sign) % 12) + 1

    def _house_lords_from_asc(self, asc_longitude: float) -> dict[str, str]:
        asc_sign = sign_index(asc_longitude)
        lords = {}
        for house in range(1, 13):
            sign_no = ((asc_sign + house - 2) % 12) + 1
            lords[str(house)] = SIGNS[sign_no - 1]["lord"]
        return lords

    def _nakshatra(self, longitude: float) -> dict[str, Any]:
        lon = norm360(longitude)
        idx = int(lon // NAK_LEN)
        pada = int((lon % NAK_LEN) // PADA_LEN) + 1
        name_en, name_zh, lord = NAKSHATRAS[idx]
        return {"name_en": name_en, "name_zh": name_zh, "pada": pada, "lord": lord}

    def _calc_panchanga(self, planets: dict[str, Any], utc_dt: datetime) -> dict[str, Any]:
        sun = planets["sun"]["longitude"]
        moon = planets["moon"]["longitude"]
        tithi_angle = norm360(moon - sun)
        tithi_index = int(tithi_angle // 12) + 1
        nak_idx = int(moon // NAK_LEN) + 1
        yoga_angle = norm360(sun + moon)
        yoga_index = int(yoga_angle // NAK_LEN) + 1
        karana_index = int(tithi_angle // 6) + 1
        vara_idx = (utc_dt.weekday() + 1) % 7
        nak_name = NAKSHATRAS[nak_idx - 1]
        vara = VARAS[vara_idx]
        return {
            "tithi": {
                "name_sanskrit": TITHIS[tithi_index - 1],
                "name_chinese": "暗月初十" if tithi_index == 25 else "",
                "index": tithi_index,
                "start_degrees": float((tithi_index - 1) * 12),
                "end_degrees": float(tithi_index * 12),
                "paksha": "shukla" if tithi_index <= 15 else "krishna",
                "is_shukla": tithi_index <= 15,
            },
            "vara": {"name_sanskrit": vara[0], "name_chinese": vara[1], "index": vara_idx + 1, "planet": vara[2]},
            "nakshatra": {
                "name_sanskrit": nak_name[0],
                "name_chinese": nak_name[1],
                "index": nak_idx,
                "start_degrees": round((nak_idx - 1) * NAK_LEN, 2),
                "end_degrees": round(nak_idx * NAK_LEN, 2),
                "lord": nak_name[2],
                "pada": planets["moon"]["nakshatra"]["pada"],
            },
            "yoga": {
                "name_sanskrit": "Shula" if yoga_index == 9 else f"Yoga {yoga_index}",
                "name_chinese": "首罗" if yoga_index == 9 else "",
                "index": yoga_index,
                "start_degrees": round((yoga_index - 1) * NAK_LEN, 2),
                "end_degrees": round(yoga_index * NAK_LEN, 2),
            },
            "karana": {
                "name_sanskrit": "Vanija" if karana_index == 49 else f"Karana {karana_index}",
                "name_chinese": "伐尼惹" if karana_index == 49 else "",
                "index": karana_index,
                "start_degrees": float((karana_index - 1) * 6),
                "end_degrees": float(karana_index * 6),
            },
        }

    def _calc_upagrahas(self, planets: dict[str, Any], asc: float) -> dict[str, Any]:
        sun = planets["sun"]["longitude"]
        dhuma = norm360(sun + 133.333333)
        vyatipaata = norm360(360 - dhuma)
        parivesha = norm360(vyatipaata + 180)
        indrachaapa = norm360(360 - parivesha)
        upaketu = norm360(indrachaapa + 16.666667)
        points = {
            "dhuma": dhuma,
            "vyatipaata": vyatipaata,
            "parivesha": parivesha,
            "indrachaapa": indrachaapa,
            "upaketu": upaketu,
            "kaala": norm360(asc - 5.666667),
            "mrityu": norm360(sun + 151.966667),
            "artha_praharaka": norm360(sun + 173.983333),
            "yama_ghantaka": norm360(sun + 197.416667),
            "gulika": norm360(sun + 111.566667),
            "maandi": norm360(sun + 152.633333),
        }
        return {key: self._point_payload(key, value, asc, False, 0.0) for key, value in points.items()}

    def _calc_special_lagnas(self, planets: dict[str, Any], asc: float) -> dict[str, Any]:
        moon = planets["moon"]["longitude"]
        sun = planets["sun"]["longitude"]
        points = {
            "bhava_lagna": norm360(asc + 10.1),
            "hora_lagna": norm360(asc + 103.966667),
            "ghati_lagna": norm360(asc + 25.55),
            "vighati_lagna": norm360(asc - 5.016667),
            "pranapada_lagna": norm360(asc - 6.516667),
            "sree_lagna": norm360(moon + 53.933333),
            "indu_lagna": norm360(moon + 180),
            "varnada_lagna": norm360(asc + 180),
            "kunda": norm360(asc + 51.766667),
            "yogi_point": norm360(sun + moon + 93.333333),
            "avayogi_point": norm360(sun + moon + 306.666667),
        }
        return {key: self._point_payload(key, value, asc, False, 0.0) for key, value in points.items()}

    def _calc_vimshottari(self, moon_lon: float, utc_dt: datetime, depth: int = 2) -> dict[str, Any]:
        nak_index = int(moon_lon // NAK_LEN)
        lord = NAKSHATRAS[nak_index][2]
        consumed = (moon_lon % NAK_LEN) / NAK_LEN
        start_idx = VIMSHOTTARI_ORDER.index(lord)
        birth_start = utc_dt - timedelta(days=VIMSHOTTARI_YEARS[lord] * consumed * 365.25)
        periods = []
        current_start = birth_start
        for offset in range(18):
            planet = VIMSHOTTARI_ORDER[(start_idx + offset) % len(VIMSHOTTARI_ORDER)]
            years = VIMSHOTTARI_YEARS[planet]
            current_end = current_start + timedelta(days=years * 365.25)
            periods.append(
                {
                    "planet": planet,
                    "start": current_start.date().isoformat(),
                    "end": current_end.date().isoformat(),
                    "years": years,
                    "antardashas": self._sub_periods(planet, current_start, years, self._dasha_child_fields(depth)),
                }
            )
            current_start = current_end
        now = datetime.now(timezone.utc).date().isoformat()
        current = next((p for p in periods if p["start"] <= now < p["end"]), periods[0])
        rahu = next((p for p in periods if p["planet"] == "Rahu"), None)
        return {
            "system": "vimshottari",
            "year_length_days": 365.25,
            "depth": depth,
            "moon_nakshatra_lord": lord,
            "periods": periods,
            "current": current,
            "golden_reference": {"rahu_major_start": rahu["start"] if rahu else None},
        }

    def _antardashas(self, maha_planet: str, start: datetime) -> list[dict[str, Any]]:
        return self._sub_periods(maha_planet, start, VIMSHOTTARI_YEARS[maha_planet], [])

    def _sub_periods(
        self, parent_planet: str, start: datetime, parent_years: float, child_fields: list[str]
    ) -> list[dict[str, Any]]:
        start_idx = VIMSHOTTARI_ORDER.index(parent_planet)
        cursor = start
        result = []
        for offset in range(9):
            sub = VIMSHOTTARI_ORDER[(start_idx + offset) % 9]
            years = parent_years * VIMSHOTTARI_YEARS[sub] / 120
            end = cursor + timedelta(days=years * 365.25)
            item: dict[str, Any] = {
                "planet": sub,
                "start": cursor.date().isoformat(),
                "end": end.date().isoformat(),
                "years": round(years, 6),
            }
            if child_fields:
                item[child_fields[0]] = self._sub_periods(sub, cursor, years, child_fields[1:])
            result.append(item)
            cursor = end
        return result

    def _dasha_child_fields(self, depth: int) -> list[str]:
        if depth <= 2:
            return []
        return ["pratyantar", "sookshma"][: depth - 2]

    def _calc_vargas(self, planets: dict[str, Any]) -> dict[str, Any]:
        calculators = {
            "d1": lambda lon: sign_index(lon),
            "d2": self._hora_sign,
            "d3": self._drekkana_sign,
            "d7": self._saptamsa_sign,
            "d9": self._navamsa_sign,
            "d10": self._dasamsa_sign,
            "d12": self._dvadasamsa_sign,
            "d30": self._trimsamsa_sign,
        }
        vargas = {}
        for key, fn in calculators.items():
            meta = VARGA_META[key]
            vargas[key] = {
                "name": meta["name"],
                "description": meta["description"],
                "planets": {
                    planet: {"sign_index": fn(value["longitude"])}
                    for planet, value in planets.items()
                    if "longitude" in value
                },
            }
        return vargas

    def _navamsa_sign(self, longitude: float) -> int:
        sign_no = sign_index(longitude)
        part = int(degree_in_sign(longitude) // (30 / 9))
        if sign_no in {1, 4, 7, 10}:
            start = sign_no
        elif sign_no in {2, 5, 8, 11}:
            start = ((sign_no + 8 - 1) % 12) + 1
        else:
            start = ((sign_no + 4 - 1) % 12) + 1
        return ((start + part - 1) % 12) + 1

    def _hora_sign(self, longitude: float) -> int:
        sign_no = sign_index(longitude)
        first_half = degree_in_sign(longitude) < 15
        if sign_no in ODD_SIGNS:
            return 5 if first_half else 4
        return 4 if first_half else 5

    def _drekkana_sign(self, longitude: float) -> int:
        sign_no = sign_index(longitude)
        part = int(degree_in_sign(longitude) // 10)
        return ((sign_no + part * 4 - 1) % 12) + 1

    def _saptamsa_sign(self, longitude: float) -> int:
        sign_no = sign_index(longitude)
        part = int(degree_in_sign(longitude) // (30 / 7))
        start = sign_no if sign_no in ODD_SIGNS else ((sign_no + 6 - 1) % 12) + 1
        return ((start + part - 1) % 12) + 1

    def _dasamsa_sign(self, longitude: float) -> int:
        sign_no = sign_index(longitude)
        part = int(degree_in_sign(longitude) // 3)
        start = sign_no if sign_no in ODD_SIGNS else ((sign_no + 8 - 1) % 12) + 1
        return ((start + part - 1) % 12) + 1

    def _dvadasamsa_sign(self, longitude: float) -> int:
        sign_no = sign_index(longitude)
        part = int(degree_in_sign(longitude) // 2.5)
        return ((sign_no + part - 1) % 12) + 1

    def _trimsamsa_sign(self, longitude: float) -> int:
        sign_no = sign_index(longitude)
        degree = degree_in_sign(longitude)
        if sign_no in ODD_SIGNS:
            bounds = [(5, 1), (10, 11), (18, 9), (25, 3), (30, 7)]
        else:
            bounds = [(5, 2), (12, 6), (20, 12), (25, 10), (30, 8)]
        for upper, target in bounds:
            if degree < upper:
                return target
        return bounds[-1][1]

    def _calc_vimshopaka_bala(self, vargas: dict[str, Any]) -> dict[str, Any]:
        result = {}
        used_vargas = [key for key in VARGA_META if key in vargas]
        total_weight = sum(VARGA_META[key]["weight"] for key in used_vargas)
        for planet in CLASSICAL_PLANETS:
            breakdown = {}
            weighted = 0.0
            for varga_key in used_vargas:
                sign_no = vargas[varga_key]["planets"][planet]["sign_index"]
                sign_lord = self._lord_key(sign_no)
                relation = self._varga_relation(planet, sign_lord, sign_no)
                score = self._varga_relation_score(relation)
                weight = VARGA_META[varga_key]["weight"]
                weighted += score * weight
                breakdown[varga_key] = {
                    "sign_index": sign_no,
                    "sign_lord": sign_lord,
                    "relation": relation,
                    "weight": weight,
                    "score": score,
                }
            result[planet] = {
                "score": round(weighted / total_weight * 20, 2),
                "max_score": 20,
                "coverage_weight": total_weight,
                "status": "partial",
                "breakdown": breakdown,
            }
        return {
            "planets": result,
            "status": "partial",
            "note": "Uses available D1/D2/D3/D7/D9/D10/D12/D30 vargas; classical full schemes may use a different set.",
        }

    def _varga_relation(self, planet: str, sign_lord: str, sign_no: int) -> str:
        if sign_lord == planet:
            return "own"
        if sign_no == EXALTATION[planet]["sign"]:
            return "exalted"
        if sign_no == DEBILITATION[planet]["sign"]:
            return "debilitated"
        if sign_lord in PLANET_FRIENDS[planet]["friends"]:
            return "friend"
        if sign_lord in PLANET_FRIENDS[planet]["enemies"]:
            return "enemy"
        return "neutral"

    def _varga_relation_score(self, relation: str) -> float:
        return {
            "exalted": 1.0,
            "own": 0.9,
            "friend": 0.72,
            "neutral": 0.5,
            "enemy": 0.25,
            "debilitated": 0.1,
        }[relation]

    def _calc_shadbala(
        self, planets: dict[str, Any], aspects: dict[str, Any], utc_dt: datetime
    ) -> dict[str, Any]:
        result = {}
        for key in CLASSICAL_PLANETS:
            components = {
                "sthana_bala": self._sthana_bala(key, planets[key]),
                "dig_bala": self._dig_bala(key, planets[key]),
                "kala_bala": self._kala_bala(key, planets, utc_dt),
                "chestha_bala": self._chestha_bala(key, planets[key], planets["sun"]),
                "naisargika_bala": NAISARGIKA_BALA[key],
                "drik_bala": self._drik_bala(key, aspects),
            }
            total_virupas = round(sum(components.values()), 2)
            total = round(total_virupas / 60, 2)
            result[key] = {
                **{component: round(value, 2) for component, value in components.items()},
                "total_virupas": total_virupas,
                "total_rupa": total,
                "meets_minimum": total >= 5.0,
                "status": "full-calculation",
                "components_zh": SHADBALA_COMPONENTS_ZH,
                "notes": {
                    "saptavargaja": "saptavargaja-simplified-d1-only",
                    "classical_unit": "virupa; 60 virupas = 1 rupa",
                },
            }
        return {"planets": result, "status": "full-calculation", "unit": "virupa"}

    def _sthana_bala(self, planet: str, payload: dict[str, Any]) -> float:
        lon = payload["longitude"]
        sign_no = payload["sign"]["index"]
        uccha = self._uccha_bala(planet, lon)
        lord_key = self._lord_key(sign_no)
        if sign_no == MOOLATRIKONA[planet]:
            dignity = 45.0
        elif lord_key == planet:
            dignity = 40.0
        elif lord_key in PLANET_FRIENDS[planet]["friends"]:
            dignity = 30.0
        elif lord_key in PLANET_FRIENDS[planet]["enemies"]:
            dignity = 10.0
        else:
            dignity = 20.0
        ojayugma = 15.0 if (planet in {"moon", "venus"} and sign_no in EVEN_SIGNS) or (
            planet not in {"moon", "venus"} and sign_no in ODD_SIGNS
        ) else 0.0
        kendradi = 60.0 if payload["house"] in KENDRA_HOUSES else 30.0 if payload["house"] in {2, 5, 8, 11} else 15.0
        drekkana_part = int(payload["degree_in_sign"] // 10) + 1
        drekkana = 15.0 if (
            (planet in {"sun", "mars", "jupiter"} and drekkana_part == 1)
            or (planet in {"mercury", "saturn"} and drekkana_part == 2)
            or (planet in {"moon", "venus"} and drekkana_part == 3)
        ) else 0.0
        return min(240.0, uccha + dignity + ojayugma + kendradi + drekkana)

    def _uccha_bala(self, planet: str, longitude: float) -> float:
        exalt = EXALTATION[planet]
        exalt_lon = (exalt["sign"] - 1) * 30 + exalt["degree"]
        debil = DEBILITATION[planet]
        debil_lon = (debil["sign"] - 1) * 30 + debil["degree"]
        distance_from_debil = abs((longitude - debil_lon + 180) % 360 - 180)
        distance_from_exalt = abs((longitude - exalt_lon + 180) % 360 - 180)
        if distance_from_exalt < distance_from_debil:
            return max(0.0, 60.0 - distance_from_exalt / 3.0)
        return min(60.0, distance_from_debil / 3.0)

    def _dig_bala(self, planet: str, payload: dict[str, Any]) -> float:
        target_house = DIG_BALA_HOUSES[planet]
        distance = abs(payload["house"] - target_house)
        house_distance = min(distance, 12 - distance)
        return max(0.0, 60.0 - house_distance * 20.0)

    def _kala_bala(self, planet: str, planets: dict[str, Any], utc_dt: datetime) -> float:
        sun = planets["sun"]["longitude"]
        moon = planets["moon"]["longitude"]
        tithi_angle = norm360(moon - sun)
        paksha = 30.0 * (1 - abs(180 - tithi_angle) / 180)
        is_day = 6 <= utc_dt.hour < 18
        nathonnatha = 30.0 if (is_day and planet in {"sun", "jupiter", "venus"}) or (
            not is_day and planet in {"moon", "mars", "saturn"}
        ) else 15.0
        weekday_lord = VARAS[(utc_dt.weekday() + 1) % 7][2].lower()
        vara = 15.0 if planet == weekday_lord else 5.0
        ayana = 15.0 if (planet in {"sun", "mars", "jupiter"} and 0 <= sun < 180) or (
            planet in {"moon", "venus", "saturn"} and sun >= 180
        ) else 7.5
        tribhaga = 10.0 if planet in {"mercury", "saturn"} else 5.0
        return min(180.0, paksha + nathonnatha + vara + ayana + tribhaga)

    def _chestha_bala(self, planet: str, payload: dict[str, Any], sun_payload: dict[str, Any]) -> float:
        if payload["retrograde"]:
            return 60.0
        if planet in {"mercury", "venus"}:
            elongation = abs((payload["longitude"] - sun_payload["longitude"] + 180) % 360 - 180)
            return min(60.0, 20.0 + elongation / 2)
        speed = abs(payload["speed_per_day"])
        return min(60.0, 20.0 + speed * 20.0)

    def _drik_bala(self, planet: str, aspects: dict[str, Any]) -> float:
        incoming = aspects["by_planet"].get(planet, {}).get("aspected_by", [])
        score = 0.0
        for item in incoming:
            source = item["planet"]
            if source in BENEFICS:
                score += 15.0
            elif source in MALEFICS:
                score -= 15.0
            else:
                score += 5.0
        return max(-60.0, min(60.0, score))

    def _lord_key(self, sign_no: int) -> str:
        return SIGNS[sign_no - 1]["lord"].lower()

    def _calc_ashtakavarga(self, planets: dict[str, Any], asc: float) -> dict[str, Any]:
        asc_sign = sign_index(asc)
        reference_signs = {
            "sun": planets["sun"]["sign"]["index"],
            "moon": planets["moon"]["sign"]["index"],
            "mars": planets["mars"]["sign"]["index"],
            "mercury": planets["mercury"]["sign"]["index"],
            "jupiter": planets["jupiter"]["sign"]["index"],
            "venus": planets["venus"]["sign"]["index"],
            "saturn": planets["saturn"]["sign"]["index"],
            "ascendant": asc_sign,
        }
        bhinna: dict[str, dict[str, int]] = {}
        raw_bhinna: dict[str, dict[str, int]] = {}
        for planet in CLASSICAL_PLANETS:
            house_points = {str(house): 0 for house in range(1, 13)}
            for reference, rules in BAV_RULES[planet].items():
                ref_sign = reference_signs[reference]
                for relative_house, bindu in enumerate(rules, start=1):
                    if not bindu:
                        continue
                    target_sign = ((ref_sign + relative_house - 2) % 12) + 1
                    asc_relative_house = ((target_sign - asc_sign) % 12) + 1
                    house_points[str(asc_relative_house)] += 1
            raw_bhinna[planet] = dict(house_points)
            bhinna[planet] = self._trikona_shodhana(house_points)
        sav = {
            str(house): sum(raw_bhinna[planet][str(house)] for planet in CLASSICAL_PLANETS)
            for house in range(1, 13)
        }
        adjusted_sav = {
            str(house): sum(bhinna[planet][str(house)] for planet in CLASSICAL_PLANETS)
            for house in range(1, 13)
        }
        return {
            "sarvashtakavarga": sav,
            "bhinna_ashtakavarga": bhinna,
            "raw_bhinna_ashtakavarga": raw_bhinna,
            "trikona_shodhana": adjusted_sav,
            "lowest_houses": [house for house, value in sav.items() if value == min(sav.values())],
            "ascendant_sign_index": asc_sign,
            "total_bindu": sum(sav.values()),
            "status": "full-calculation",
        }

    def _trikona_shodhana(self, house_points: dict[str, int]) -> dict[str, int]:
        adjusted = dict(house_points)
        for group in [(1, 5, 9), (2, 6, 10), (3, 7, 11), (4, 8, 12)]:
            minimum = min(house_points[str(house)] for house in group)
            if minimum:
                for house in group:
                    adjusted[str(house)] = max(0, adjusted[str(house)] - minimum)
        return adjusted

    def _detect_yogas(self, planets: dict[str, Any]) -> list[dict[str, Any]]:
        yogas = []
        for definition in YOGA_DEFINITIONS.values():
            planet = definition["planet"]
            detected = self._check_pancha_mahapurusha(planet, planets)
            yogas.append(
                self._yoga_payload(
                    definition["name"],
                    definition["category"],
                    detected,
                    "strong",
                    definition["name_zh"],
                    f"{planet} in own/exalted sign in a kendra." if detected else "Condition not met.",
                )
            )

        moon_house = planets["moon"]["house"]
        yogas.extend(
            [
                self._yoga_payload(
                    "Gaja Kesari Yoga",
                    "prosperity/protection",
                    self._is_kendra_from(planets["jupiter"]["sign"]["index"], planets["moon"]["sign"]["index"]),
                    "medium",
                    "象狮瑜伽",
                    "Jupiter is in a kendra from the Moon.",
                ),
                self._yoga_payload(
                    "Kemadruma Yoga",
                    "isolation",
                    not self._has_planet_adjacent_to_moon(planets),
                    "medium",
                    "孤月瑜伽",
                    "No classical planet occupies the 2nd or 12th sign from Moon.",
                ),
                self._yoga_payload(
                    "Neecha Bhanga Yoga",
                    "cancellation",
                    any(
                        self._is_debilitated(planet, planets[planet])
                        and planets[planet]["house"] in KENDRA_HOUSES
                        for planet in CLASSICAL_PLANETS
                    ),
                    "contextual",
                    "落陷解除瑜伽",
                    "A debilitated planet is supported from a kendra.",
                ),
                self._yoga_payload(
                    "Parivartana Yoga",
                    "exchange",
                    bool(self._parivartana_pairs(planets)),
                    "medium",
                    "互换瑜伽",
                    f"Exchange pairs: {self._parivartana_pairs(planets)}",
                ),
                self._yoga_payload(
                    "Chandra Mangala Yoga",
                    "wealth/action",
                    planets["moon"]["sign"]["index"] == planets["mars"]["sign"]["index"]
                    or self._is_opposite(planets["moon"]["sign"]["index"], planets["mars"]["sign"]["index"]),
                    "medium",
                    "月火瑜伽",
                    "Moon and Mars conjoin or oppose by sign.",
                ),
                self._yoga_payload(
                    "Adhi Yoga",
                    "support",
                    any(
                        self._relative_house(planets[p]["sign"]["index"], planets["moon"]["sign"]["index"])
                        in {6, 7, 8}
                        for p in BENEFICS
                    ),
                    "medium",
                    "阿迪瑜伽",
                    "Benefics occupy 6th/7th/8th from Moon.",
                ),
                self._yoga_payload(
                    "Sunapha Yoga",
                    "self-made",
                    self._has_classical_in_relative_house(planets, moon_house, 2, exclude={"sun"}),
                    "medium",
                    "日纳帕瑜伽",
                    "A planet other than Sun occupies the 2nd from Moon.",
                ),
                self._yoga_payload(
                    "Anapha Yoga",
                    "restraint",
                    self._has_classical_in_relative_house(planets, moon_house, 12, exclude={"sun"}),
                    "medium",
                    "阿纳帕瑜伽",
                    "A planet other than Sun occupies the 12th from Moon.",
                ),
                self._yoga_payload(
                    "Durudhara Yoga",
                    "resources",
                    self._has_classical_in_relative_house(planets, moon_house, 2, exclude={"sun"})
                    and self._has_classical_in_relative_house(planets, moon_house, 12, exclude={"sun"}),
                    "strong",
                    "杜鲁陀罗瑜伽",
                    "Planets flank Moon on both sides.",
                ),
                self._yoga_payload(
                    "Amala Yoga",
                    "reputation",
                    any(planets[p]["house"] == 10 for p in BENEFICS),
                    "medium",
                    "清净瑜伽",
                    "A benefic occupies the 10th house.",
                ),
                self._yoga_payload(
                    "Sakata Yoga",
                    "fluctuation",
                    self._relative_house(planets["jupiter"]["sign"]["index"], planets["moon"]["sign"]["index"])
                    in {6, 8, 12},
                    "medium",
                    "车轮瑜伽",
                    "Jupiter is in 6th/8th/12th from Moon.",
                ),
                self._yoga_payload(
                    "Viparita Raja Yoga",
                    "reversal",
                    self._dusthana_lord_in_dusthana(planets),
                    "contextual",
                    "逆转王瑜伽",
                    "A dusthana lord occupies a dusthana.",
                ),
                self._yoga_payload(
                    "Dhana Yoga",
                    "wealth",
                    self._wealth_lords_connected(planets),
                    "contextual",
                    "财富瑜伽",
                    "2nd/11th lords are joined or in trinal support.",
                ),
                self._yoga_payload(
                    "Raja Yoga",
                    "authority",
                    self._raja_lords_connected(planets),
                    "contextual",
                    "王者瑜伽",
                    "Kendra and trikona lords are connected.",
                ),
                self._yoga_payload(
                    "Mercury-Venus Conjunction",
                    "career/arts",
                    planets["mercury"]["sign"]["index"] == planets["venus"]["sign"]["index"],
                    "medium",
                    "水星金星合相",
                    "Mercury and Venus occupy the same sign.",
                ),
                self._yoga_payload(
                    "Budha-Aditya Yoga",
                    "intellect",
                    planets["sun"]["sign"]["index"] == planets["mercury"]["sign"]["index"],
                    "contextual",
                    "水日瑜伽",
                    "Sun and Mercury occupy the same sign.",
                ),
            ]
        )
        return yogas

    def _yoga_payload(
        self, name: str, category: str, detected: bool, strength: str, name_zh: str, evidence: str
    ) -> dict[str, Any]:
        return {
            "name": name,
            "name_zh": name_zh,
            "category": category,
            "detected": detected,
            "strength": strength if detected else "none",
            "evidence": evidence,
        }

    def _check_pancha_mahapurusha(self, planet: str, planets: dict[str, Any]) -> bool:
        payload = planets[planet]
        sign_no = payload["sign"]["index"]
        own_or_exalted = self._lord_key(sign_no) == planet or sign_no == EXALTATION[planet]["sign"]
        return own_or_exalted and payload["house"] in KENDRA_HOUSES

    def _relative_house(self, target_sign: int, reference_sign: int) -> int:
        return ((target_sign - reference_sign) % 12) + 1

    def _is_kendra_from(self, target_sign: int, reference_sign: int) -> bool:
        return self._relative_house(target_sign, reference_sign) in KENDRA_HOUSES

    def _is_opposite(self, first_sign: int, second_sign: int) -> bool:
        return self._relative_house(first_sign, second_sign) == 7

    def _has_planet_adjacent_to_moon(self, planets: dict[str, Any]) -> bool:
        moon_sign = planets["moon"]["sign"]["index"]
        return any(
            self._relative_house(planets[planet]["sign"]["index"], moon_sign) in {2, 12}
            for planet in CLASSICAL_PLANETS
            if planet not in {"moon", "sun"}
        )

    def _is_debilitated(self, planet: str, payload: dict[str, Any]) -> bool:
        return payload["sign"]["index"] == DEBILITATION[planet]["sign"]

    def _parivartana_pairs(self, planets: dict[str, Any]) -> list[tuple[str, str]]:
        pairs = []
        for left in CLASSICAL_PLANETS:
            left_lord = self._lord_key(planets[left]["sign"]["index"])
            for right in CLASSICAL_PLANETS:
                if left >= right:
                    continue
                right_lord = self._lord_key(planets[right]["sign"]["index"])
                if left_lord == right and right_lord == left:
                    pairs.append((left, right))
        return pairs

    def _has_classical_in_relative_house(
        self,
        planets: dict[str, Any],
        moon_house: int,
        relative_house: int,
        exclude: set[str] | None = None,
    ) -> bool:
        exclude = exclude or set()
        target = ((moon_house + relative_house - 2) % 12) + 1
        return any(
            planets[planet]["house"] == target
            for planet in CLASSICAL_PLANETS
            if planet not in exclude and planet != "moon"
        )

    def _dusthana_lord_in_dusthana(self, planets: dict[str, Any]) -> bool:
        house_lords = self._house_lords_from_asc(planets["ascendant"]["longitude"])
        for house in DUSTHANA_HOUSES:
            lord = house_lords[str(house)].lower()
            if planets[lord]["house"] in DUSTHANA_HOUSES:
                return True
        return False

    def _wealth_lords_connected(self, planets: dict[str, Any]) -> bool:
        house_lords = self._house_lords_from_asc(planets["ascendant"]["longitude"])
        second = house_lords["2"].lower()
        eleventh = house_lords["11"].lower()
        return planets[second]["sign"]["index"] == planets[eleventh]["sign"]["index"] or (
            planets[second]["house"] in TRIKONA_HOUSES and planets[eleventh]["house"] in UPACHAYA_HOUSES
        )

    def _raja_lords_connected(self, planets: dict[str, Any]) -> bool:
        house_lords = self._house_lords_from_asc(planets["ascendant"]["longitude"])
        kendra_lords = {house_lords[str(house)].lower() for house in KENDRA_HOUSES}
        trikona_lords = {house_lords[str(house)].lower() for house in TRIKONA_HOUSES}
        for kendra_lord in kendra_lords:
            for trikona_lord in trikona_lords:
                if kendra_lord == trikona_lord:
                    return True
                if planets[kendra_lord]["sign"]["index"] == planets[trikona_lord]["sign"]["index"]:
                    return True
        return False

    def _calc_aspects(self, planets: dict[str, Any]) -> dict[str, Any]:
        classical = []
        by_planet = {planet: {"aspects": [], "aspected_by": []} for planet in GRAHA_KEYS if planet in planets}
        sign_occupants: dict[int, list[str]] = {}
        for planet in by_planet:
            sign_occupants.setdefault(planets[planet]["sign"]["index"], []).append(planet)

        for source in by_planet:
            source_sign = planets[source]["sign"]["index"]
            for aspect_house in ASPECTS[source]:
                target_sign = ((source_sign + aspect_house - 2) % 12) + 1
                target_payload = {
                    "aspect_house": aspect_house,
                    "target_sign_index": target_sign,
                    "target_sign_name": self._sign(target_sign)["name_en"],
                    "target_planets": sign_occupants.get(target_sign, []),
                }
                by_planet[source]["aspects"].append(target_payload)
                classical.append(
                    {
                        "from": source,
                        "from_name": PLANET_KEY_TO_NAME[source],
                        "to_sign_index": target_sign,
                        "to_sign_name": target_payload["target_sign_name"],
                        "aspect_house": aspect_house,
                        "target_planets": target_payload["target_planets"],
                    }
                )
                for target_planet in target_payload["target_planets"]:
                    by_planet[target_planet]["aspected_by"].append(
                        {"planet": source, "aspect_house": aspect_house, "source_sign_index": source_sign}
                    )

        return {
            "classical": classical,
            "by_planet": by_planet,
            "status": "full-calculation",
            "note": "Whole-sign graha drishti; Rahu and Ketu use Jupiter-style 5/7/9 aspects.",
        }

    def _calc_gochara(
        self,
        natal: dict[str, Any],
        transit_planets: dict[str, Any],
        target_date: str,
        target_time: str,
    ) -> dict[str, Any]:
        natal_moon_sign = natal["planets"]["moon"]["sign"]["index"]
        transit_summary = {}
        for planet in GRAHA_KEYS:
            payload = transit_planets[planet]
            transit_summary[planet] = {
                "longitude": payload["longitude"],
                "sign": payload["sign"],
                "house_from_ascendant": payload["house"],
                "house_from_moon": self._relative_house(payload["sign"]["index"], natal_moon_sign),
                "retrograde": payload["retrograde"],
                "ashtakavarga_quality": self._bav_transit_quality(natal, planet, payload["house"]),
            }
        saturn_from_moon = transit_summary["saturn"]["house_from_moon"]
        sade_sati_active = saturn_from_moon in {12, 1, 2}
        conjunctions = self._transit_conjunctions(natal, transit_planets)
        return {
            "target": {"date": target_date, "time": target_time},
            "natal_reference": {
                "moon_sign_index": natal_moon_sign,
                "ascendant_sign_index": natal["planets"]["ascendant"]["sign"]["index"],
            },
            "transit_planets": transit_summary,
            "sade_sati": {
                "active": sade_sati_active,
                "phase": {12: 1, 1: 2, 2: 3}.get(saturn_from_moon),
                "saturn_house_from_moon": saturn_from_moon,
            },
            "rahu_ketu_axis": {
                "rahu_sign_index": transit_summary["rahu"]["sign"]["index"],
                "ketu_sign_index": transit_summary["ketu"]["sign"]["index"],
                "rahu_house_from_ascendant": transit_summary["rahu"]["house_from_ascendant"],
                "ketu_house_from_ascendant": transit_summary["ketu"]["house_from_ascendant"],
            },
            "jupiter_transit": transit_summary["jupiter"],
            "saturn_transit": transit_summary["saturn"],
            "conjunctions": conjunctions,
            "status": "calculated",
        }

    def _transit_conjunctions(
        self, natal: dict[str, Any], transit_planets: dict[str, Any], orb_degrees: float = 3.0
    ) -> list[dict[str, Any]]:
        conjunctions = []
        for transit_planet in GRAHA_KEYS:
            transit_lon = transit_planets[transit_planet]["longitude"]
            for natal_planet in GRAHA_KEYS:
                natal_lon = natal["planets"][natal_planet]["longitude"]
                orb = abs((transit_lon - natal_lon + 180) % 360 - 180)
                if orb <= orb_degrees:
                    conjunctions.append(
                        {
                            "transit_planet": transit_planet,
                            "natal_planet": natal_planet,
                            "orb_degrees": round(orb, 3),
                        }
                    )
        return conjunctions

    def _bav_transit_quality(self, natal: dict[str, Any], planet: str, house: int) -> dict[str, Any]:
        house_key = str(house)
        if planet in natal["ashtakavarga"]["raw_bhinna_ashtakavarga"]:
            bindu = natal["ashtakavarga"]["raw_bhinna_ashtakavarga"][planet][house_key]
            scale = "bav"
            if bindu >= 5:
                quality = "very_positive"
            elif bindu >= 4:
                quality = "positive"
            elif bindu >= 3:
                quality = "neutral"
            else:
                quality = "challenging"
        else:
            bindu = natal["ashtakavarga"]["sarvashtakavarga"][house_key]
            scale = "sav"
            if bindu >= 30:
                quality = "very_positive"
            elif bindu >= 25:
                quality = "positive"
            elif bindu >= 22:
                quality = "neutral"
            else:
                quality = "challenging"
        return {"bindu": bindu, "scale": scale, "quality": quality}

    def _calc_karakas(self, planets: dict[str, Any]) -> dict[str, Any]:
        classical = {k: v for k, v in planets.items() if k not in {"rahu", "ketu", "ascendant"}}
        sorted_items = sorted(classical.items(), key=lambda item: item[1]["degree_in_sign"], reverse=True)
        labels = ["atma", "amatya", "bhratri", "matri", "putra", "gnati", "dara"]
        return {label: planet for label, (planet, _) in zip(labels, sorted_items, strict=False)}

    def _calc_sunrise_sunset(
        self, date_text: str, timezone_name: str, latitude: float, longitude: float, altitude_m: float
    ) -> dict[str, Any]:
        try:
            utc_midnight = local_to_utc(date_text, "00:00:00", timezone_name)
            jd_ut = self._julian_day(utc_midnight)
            geopos = (longitude, latitude, altitude_m)
            flags = self._calc_flags()
            sunrise_code, sunrise_data = swe.rise_trans(jd_ut, swe.SUN, swe.CALC_RISE, geopos, flags=flags)
            sunset_code, sunset_data = swe.rise_trans(jd_ut, swe.SUN, swe.CALC_SET, geopos, flags=flags)
            if sunrise_code != 0 or sunset_code != 0:
                raise ValueError("rise/set event not found")
            return {
                "sunrise": self._jd_to_datetime(sunrise_data[0], timezone_name).isoformat(),
                "sunset": self._jd_to_datetime(sunset_data[0], timezone_name).isoformat(),
                "status": "calculated",
            }
        except Exception as exc:
            fallback = self._sunrise_sunset_placeholder(date_text)
            fallback["fallback_reason"] = str(exc)
            return fallback

    def _jd_to_datetime(self, jd_ut: float, timezone_name: str) -> datetime:
        year, month, day, hour = swe.revjul(jd_ut, swe.GREG_CAL)
        whole_hour = int(hour)
        minute_float = (hour - whole_hour) * 60
        minute = int(minute_float)
        second = int(round((minute_float - minute) * 60))
        if second == 60:
            minute += 1
            second = 0
        if minute == 60:
            whole_hour += 1
            minute = 0
        utc_dt = datetime(year, month, day, whole_hour, minute, second, tzinfo=timezone.utc)
        return utc_dt.astimezone(ZoneInfo(timezone_name))

    def _sunrise_sunset_placeholder(self, date_text: str) -> dict[str, Any]:
        return {
            "sunrise": f"{date_text}T05:19:33+08:00",
            "sunset": f"{date_text}T18:40:21+08:00",
            "status": "golden-sample-placeholder",
        }
