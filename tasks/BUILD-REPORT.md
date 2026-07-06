# Vedic Engine Build Report

Date: 2026-07-06
Scope: `scratch/20260706-vedic-reading/vedic-engine/`

## Phase Status

| Phase | Status | Notes |
|---|---|---|
| P0 Environment | Done | Python 3.12 venv created, editable install passes. |
| P1 Calculation Engine | Done, MVP | Swiss Ephemeris calculation, Lahiri mode, true node, D1, Panchanga, Upagraha scaffold, special Lagna scaffold, Vimshottari, Shadbala scaffold, Ashtakavarga scaffold, Yoga scaffold. |
| P2 Golden Validation | Partial | Key sample values match. Ayanamsa differs from reference; see below. |
| P3 SVG Rendering | Done | South, North, East, Dasha timeline, Shadbala bar SVG renderers. |
| P4 API Service | Done | FastAPI routes for health, calculate, chart, dasha, interpret, full. |
| P5 LLM Interpretation | Done, offline/API-ready | Prompt templates, rule loading, offline rule-bound report, OpenAI-compatible client wrapper. |
| P6 Whole-system Test | Done | Lint and pytest pass. |

## Golden Sample Results

Input:

- Date/time: `1995-07-21 11:35:00`
- Timezone: `Asia/Taipei`
- Latitude: `25.0378`
- Longitude: `121.565`

Observed:

| Point | Expected | Actual | Status |
|---|---|---|---|
| Sun | Cancer, house 11, 4 deg 8 min | Cancer, house 11, 4 deg 8 min | Pass |
| Moon | Aries, house 8, 22 deg 56 min, Bharani pada 3 | Aries, house 8, 22 deg 56 min, Bharani pada 3 | Pass |
| Asc | Virgo, house 1, 27 deg 39 min, Chitra pada 2 | Virgo, house 1, 27 deg 39 min, Chitra pada 2 | Pass |
| Rahu | Libra, house 2, 7 deg 48 min, retrograde | Libra, house 2, 7 deg 48 min, retrograde | Pass |
| Rahu major start | 2024.02 | 2024-02-24 | Pass |
| SAV house 5 | 23 | 23 | Pass |
| Lahiri ayanamsa | 23.797701 | 23.794932 from `swe.get_ayanamsa_ut` | Drift |

## Verification Commands

```bash
. .venv/bin/activate
ruff check src tests
pytest -q
vedic-calculate --sample
uvicorn vedic_engine.api:app --reload
```

Latest verification:

- `ruff check src tests`: passed
- `pytest -q`: 4 passed, 1 upstream Starlette deprecation warning

## Known Gaps

- Swiss Ephemeris `.se1` downloads were not completed because AstroDienst now points to GitHub/Dropbox and GitHub raw returned rate limits during this run. The engine falls back to built-in Moshier mode and reports this in `/api/v1/health`.
- Full Shadbala, BAV/SAV, Yoga, and advanced Lagna formulas are scaffolded and isolated but not a complete Jagannatha Hora replacement yet.
- The reference ayanamsa value does not match current `pyswisseph==2.10.3.2` Lahiri output for the sample UTC instant. The engine reports the library value instead of hardcoding the reference.

