# Vedic Reading — Project Governance

## Purpose
Self-hosted Vedic astrology calculation engine with AI interpretation. Combines Swiss Ephemeris astronomical precision with traditional Jyotish logic (Yoga, Dasha, Shadbala, Ashtakavarga) and LLM-based structured chart interpretation.

## Stack
- Python 3.12+ · FastAPI · Uvicorn
- Swiss Ephemeris (pyswisseph 2.10)
- SVG chart rendering (matplotlib + svgwrite)
- Docker support
- LLM integration via httpx (OpenAI-compatible API)

## Project Structure
```
vedic-engine/
├── src/vedic_engine/   — core Python package
│   ├── calculator.py   — chart calculation (1126 lines, main engine)
│   ├── constants.py    — Vedic constants and reference data
│   ├── api.py          — FastAPI routes
│   ├── cli.py          — CLI entry point
│   ├── renderer.py     — SVG chart renderer
│   ├── interpreter.py  — rule-bound LLM interpreter
│   ├── llm_client.py   — LLM API client
│   ├── schemas.py      — Pydantic models
│   └── utils.py        — helpers
├── tests/              — pytest tests
├── templates/          — LLM prompt templates (natal, career, relationship, etc.)
├── ephe/               — Swiss Ephemeris data files
├── tasks/              — planning artifacts
└── output/             — generated charts and reports
```

## Key Constraints
- **Anti-contamination**: LLM interpretation MUST only use chart data, never operator context (see RULES.md)
- **Lahiri ayanamsa**: default for all calculations
- **Self-hosted**: no external API dependency for core calculation
- **Ephemeris fallback**: Moshier mode when .se1 files are absent

## Risk Gates
- `git push` — confirm before any remote push
- `.env` / credential files — never commit
- No production data — this is a local tool, no database

## Available Scripts
```bash
vedic-calculate --sample          # run sample calculation
uvicorn vedic_engine.api:app      # start API server
pytest                            # run tests
```
