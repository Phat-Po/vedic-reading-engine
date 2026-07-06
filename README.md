# Vedic Reading Engine

Self-hosted Vedic astrology calculation and AI interpretation engine. Combines
Swiss Ephemeris astronomical precision with traditional Jyotish logic (Yoga,
Dasha, Shadbala, Ashtakavarga) and LLM-based structured chart interpretation.

## Quick Start

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
vedic-calculate --sample
uvicorn vedic_engine.api:app --reload
```

## Swiss Ephemeris

Place ephemeris files in `ephe/`:

- `sepl_18.se1`
- `semo_18.se1`
- `seas_18.se1`
- `fixstars.cat`

If files are absent, calculations fall back to Swiss Ephemeris' built-in Moshier
mode so tests can still run. `GET /api/v1/health` reports which files are present.

## LLM Interpretation

LLM-based chart interpretation follows anti-contamination rules defined in
[RULES.md](RULES.md) — the AI must derive every conclusion from chart data
only, never from external context about the person.

## Planning Docs

See [tasks/](tasks/) for PRD, architecture, data schema, and build reports.

