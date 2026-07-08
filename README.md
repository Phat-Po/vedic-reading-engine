# Vedic Reading Engine

Self-hosted Vedic astrology engine with Swiss Ephemeris calculations, SVG chart
rendering, offline interpretation, and Codex/Claude skill integration.

## What This Repo Provides

- Deterministic Vedic chart calculation with Lahiri ayanamsa by default
- SVG chart rendering for South Indian, North Indian, East Indian, dasha, and shadbala views
- FastAPI endpoints for calculate, chart, dasha, transit, and full reading flows
- Offline interpretation constrained by [RULES.md](RULES.md)
- A reusable `india-vedic` skill for Codex and Claude-style agent workflows

## Local Compatibility

This repository is prepared for public GitHub release without changing the local
workflow already used on this machine:

- `vedic-calculate` stays the primary CLI entrypoint
- existing FastAPI routes stay unchanged
- local `.venv` usage stays valid
- local `output/`, `profiles/`, and `ephe/` folders can still exist, but they are no longer tracked in git

## Quick Start

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
vedic-calculate --sample
uvicorn vedic_engine.api:app --reload
```

Open the API docs at `http://127.0.0.1:8000/docs`.

## CLI Usage

Run the bundled sample:

```bash
vedic-calculate --sample
```

Run a direct birth-chart calculation:

```bash
vedic-calculate \
  --date 1995-07-21 \
  --time 11:35:00 \
  --tz Asia/Taipei \
  --lat 25.0378 \
  --lon 121.5650 \
  --gender male \
  --type natal \
  --depth 3 \
  --output-dir output
```

This prints chart JSON to stdout and writes SVG files to `output/`.

## API Surface

- `GET /api/v1/health`
- `POST /api/v1/calculate`
- `POST /api/v1/chart/{style}`
- `POST /api/v1/dasha`
- `POST /api/v1/transit`
- `POST /api/v1/interpret`
- `POST /api/v1/full`

## Skill Installation

This repo ships the same `india-vedic` skill in two layouts for compatibility:

- `.agents/skills/india-vedic/`
- `.claude/skills/india-vedic/`

Use the path that matches your host tool. After copying the skill into your own
skills directory, the agent can accept natural-language requests such as:

- `帮我看这个 Vedic 本命盘`
- `1995-07-21 11:35 台北 男，重点看事业`
- `Run a Vedic relationship reading for 1993-02-04 08:00 Asia/Shanghai`

The skill expects the repo to be installed locally and uses the existing
`vedic-calculate` CLI plus this repository's anti-contamination rules.

## Swiss Ephemeris Data

Place Swiss Ephemeris files in `ephe/` if you want full local ephemeris data:

- `sepl_18.se1`
- `semo_18.se1`
- `seas_18.se1`
- `fixstars.cat`

If they are absent, the engine falls back to Moshier mode so tests and local
development still work. `GET /api/v1/health` reports which files are present.

The ephemeris data files are intentionally not tracked in git. Keep them local.

## License And Commercial Use

This repository is released under `AGPL-3.0-or-later`.

That choice is deliberate because the project depends on `pyswisseph`, which is
distributed under AGPL terms. If you plan to embed this engine in a closed-source
product or a commercially hosted service, review Swiss Ephemeris licensing
requirements carefully before shipping.

## Suggested GitHub Metadata

- Repository name: `vedic-reading-engine`
- Description: `Self-hosted Vedic astrology engine with Swiss Ephemeris calculations, SVG chart rendering, offline interpretation, and Codex/Claude skill integration.`
- Topics: `vedic-astrology`, `jyotish`, `astrology`, `swiss-ephemeris`, `fastapi`, `python`, `svg`, `llm`, `agent-skill`, `codex`, `claude-code`, `self-hosted`

## Planning Docs

See [tasks/](tasks/) for PRD, architecture, data schema, and release prep notes.
