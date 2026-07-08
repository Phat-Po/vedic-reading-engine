# Vedic Reading Engine

[![License](https://img.shields.io/badge/License-AGPL--3.0--or--later-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#requirements)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688.svg)](#api-surface)
[![Charts](https://img.shields.io/badge/Output-SVG-orange.svg)](#features)
[![Mode](https://img.shields.io/badge/Mode-Self--Hosted-lightgrey.svg)](#why-this-repo)

**Self-hosted Vedic astrology engine with Swiss Ephemeris calculations, SVG chart rendering, offline interpretation, and Codex/Claude skill integration.**

This repository is for builders who want a local-first Jyotish engine they can run as a CLI, API, or agent skill without turning the core chart calculation into a black-box SaaS dependency.

中文入口： [README.zh.md](README.zh.md)

---

## Quick Start

### Option 1. Send This To Your AI Agent

Use this if you want an agent to install the repo, run the main checks, start the API, and tell you exactly how to verify it works.

Copy this into Codex, Claude Code, or another coding agent:

```text
You are onboarding this repository for local use.

Your job is to get the project running locally with the simplest supported path, verify the main flows, and report the exact result.

Read README.md first. Then read ONBOARDING_PROMPT.md, SETUP.md, and docs/INDEX.md if they exist. Install dependencies, run the main test path, run the sample CLI flow, start the API, and verify the project is working.

Minimum success target:
- `pip install -e ".[dev]"`
- `pytest`
- `vedic-calculate --sample`
- `uvicorn vedic_engine.api:app --reload`
- verify `http://127.0.0.1:8000/docs` or `GET /api/v1/health`

Rules:
- use the simplest supported setup path first
- do not assume secrets are needed unless the docs say so
- do not rewrite project code unless blocked by a concrete setup issue
- stop at the first real blocker and report it precisely

Required final output:
- exact commands run
- pass/fail status for each step
- exact human verification steps
- missing optional assets, if any
- first blocker only, with exact error text, if setup fails
```

Direct prompt file:

- [ONBOARDING_PROMPT.md](ONBOARDING_PROMPT.md)

### Option 2. Manual Setup

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
vedic-calculate --sample
uvicorn vedic_engine.api:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

Recommended first test:

1. Run `vedic-calculate --sample` to confirm chart generation works.
2. Open `http://127.0.0.1:8000/docs` and call `GET /api/v1/health`.
3. Add Swiss Ephemeris files to `ephe/` if you want full local ephemeris mode instead of fallback Moshier mode.

For a step-by-step setup path, see [SETUP.md](SETUP.md).

---

## Why This Repo?

Most astrology demos stop at one of two shallow endpoints:

- prompt-only interpretation with weak chart mechanics
- accurate chart calculation without a reusable agent-facing interface

This repo is designed to sit in the middle: deterministic calculation first, then structured local interfaces on top.

| | Vedic Reading Engine | Prompt-only astrology demo | Generic chart library |
|---|:---:|:---:|:---:|
| Swiss Ephemeris based calculation | ✅ | ❌ | ⚠️ |
| SVG chart rendering | ✅ | ❌ | ⚠️ |
| FastAPI endpoints | ✅ | ⚠️ | ❌ |
| CLI sample flow | ✅ | ❌ | ⚠️ |
| Agent skill packaging | ✅ | ❌ | ❌ |
| Anti-contamination interpretation rules | ✅ | ❌ | ❌ |

---

## Features

- Deterministic Vedic chart calculation with Lahiri ayanamsa by default
- South Indian, North Indian, East Indian, dasha, and shadbala SVG rendering
- FastAPI endpoints for calculate, chart, dasha, transit, interpret, and full reading flows
- Offline interpretation constrained by [RULES.md](RULES.md)
- Local CLI entrypoints for chart generation and PDF export
- Dual skill packaging for `.claude/` and `.agents/` compatibility

---

## Requirements

- Python `3.10+`
- macOS / Linux environment for local development
- Optional: Swiss Ephemeris data files in `ephe/`
- Optional: Chrome installed if you use PDF export

---

## Installation

```bash
git clone <your-repo-url>
cd vedic-reading-engine
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

Docker path:

```bash
docker compose up --build
```

The Docker image exposes the API on port `8000`.

---

## CLI Usage

Run the bundled sample:

```bash
vedic-calculate --sample
```

Run a direct chart calculation:

```bash
vedic-calculate \
  --date 1992-11-03 \
  --time 06:20:00 \
  --tz Asia/Singapore \
  --lat 1.3521 \
  --lon 103.8198 \
  --gender female \
  --type natal \
  --depth 3 \
  --output-dir output
```

This prints chart JSON to stdout and writes SVG files to `output/`.

---

## API Surface

- `GET /api/v1/health`
- `POST /api/v1/calculate`
- `POST /api/v1/chart/{style}`
- `POST /api/v1/dasha`
- `POST /api/v1/transit`
- `POST /api/v1/interpret`
- `POST /api/v1/full`

Minimal example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/calculate \
  -H 'Content-Type: application/json' \
  -d @tests/fixtures/sample_birth_1995.json
```

---

## Skill Usage

This repo ships the same `india-vedic` skill in two layouts for compatibility:

- `.claude/skills/india-vedic/`
- `.agents/skills/india-vedic/`

After copying the matching folder into your own agent skills directory, the agent can accept prompts such as:

- `帮我看这个 Vedic 本命盘`
- `1992-11-03 06:20 新加坡 女，重点看事业`
- `Run a Vedic relationship reading for 1993-02-04 08:00 Asia/Shanghai`

The skill expects a local installation of this repo and uses the existing `vedic-calculate` CLI plus the repository's anti-contamination rules.

---

## Modes And Boundaries

| Mode | What it does |
|---|---|
| CLI | Generate chart JSON and SVG assets locally |
| API | Serve chart calculation and interpretation endpoints over FastAPI |
| Skill | Let Codex/Claude-style agents call the repo through natural language |
| Moshier fallback | Works without local `.se1` files, useful for tests and lightweight setup |
| Full Swiss Ephemeris mode | Uses local ephemeris files in `ephe/` for fuller local data |

Local compatibility is preserved:

- `vedic-calculate` stays the primary CLI entrypoint
- existing FastAPI routes stay unchanged
- local `.venv` usage stays valid
- local `output/`, `profiles/`, and `ephe/` folders can still exist, but they are no longer tracked in git

---

## Swiss Ephemeris Data

Place these files in `ephe/` if you want full local ephemeris data:

- `sepl_18.se1`
- `semo_18.se1`
- `seas_18.se1`
- `fixstars.cat`

If they are absent, the engine falls back to Moshier mode so tests and local development still work. `GET /api/v1/health` reports which files are present.

These files are intentionally not tracked in git. Keep them local.

---

## Docs Map

- [README.zh.md](README.zh.md): Chinese entry
- [ONBOARDING_PROMPT.md](ONBOARDING_PROMPT.md): copy-paste prompt for AI-agent-assisted setup
- [SETUP.md](SETUP.md): install and first-run guide
- [docs/INDEX.md](docs/INDEX.md): documentation hub
- [CONTRIBUTING.md](CONTRIBUTING.md): development workflow and local-only artifact boundaries
- [RULES.md](RULES.md): anti-contamination rules for interpretation output

Maintainer-oriented planning artifacts remain under `tasks/` and are not part of the primary user-facing docs path.

---

## Architecture

```text
birth input -> calculator -> chart JSON -> renderer/interpreter -> CLI/API/skill output
```

Core components:

- `src/vedic_engine/calculator.py`: astronomical and chart logic
- `src/vedic_engine/renderer.py`: SVG output for charts and timelines
- `src/vedic_engine/interpreter.py`: rule-bound interpretation layer
- `src/vedic_engine/api.py`: FastAPI entrypoint
- `.claude/skills/india-vedic/` and `.agents/skills/india-vedic/`: agent-facing natural-language layer

---

## Project Structure

```text
src/vedic_engine/         # core package
tests/                    # pytest coverage
templates/                # interpretation prompt templates
ephe/                     # local Swiss Ephemeris data, not tracked
output/                   # generated assets, local only
profiles/                 # local reading archives, local only
tasks/                    # planning and release artifacts
```

---

## Troubleshooting

**`GET /api/v1/health` shows Moshier mode**
→ Add the `.se1` and `fixstars.cat` files into `ephe/`.

**Sample chart works but SVG files are missing**
→ Re-run without `--json-only` and check `output/`.

**PDF export fails**
→ Confirm Chrome is installed at the expected local path used by the exporter.

**Agent skill runs but produces over-specific conclusions**
→ Check [RULES.md](RULES.md); the interpretation layer should only use chart data.

---

## License And Commercial Use

- License: `AGPL-3.0-or-later`
- Dependency note: this project depends on `pyswisseph`
- Distribution note: review Swiss Ephemeris licensing before embedding this engine into a closed-source or commercially hosted product

Suggested GitHub metadata:

- Repository name: `vedic-reading-engine`
- Description: `Self-hosted Vedic astrology engine with Swiss Ephemeris calculations, SVG chart rendering, offline interpretation, and Codex/Claude skill integration.`
- Topics: `vedic-astrology`, `jyotish`, `astrology`, `swiss-ephemeris`, `fastapi`, `python`, `svg`, `llm`, `agent-skill`, `codex`, `claude-code`, `self-hosted`
