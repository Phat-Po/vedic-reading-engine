# Setup Guide

## Before You Start

- Python `3.10+` is required. The local development path used in this repo is Python `3.12`.
- If you want full local ephemeris mode, prepare the Swiss Ephemeris files for `ephe/`.
- If you want PDF export, keep Chrome installed locally.

## Step 1. Clone And Install

```bash
git clone <your-repo-url>
cd vedic-reading-engine
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## Step 2. Run The First Smoke Test

```bash
pytest
vedic-calculate --sample
```

Expected result:

- tests pass
- sample chart JSON prints to stdout
- if you run without `--json-only`, SVG assets appear in `output/`

## Step 3. Start The API

```bash
uvicorn vedic_engine.api:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Step 4. Optional Local Data Upgrade

Place these files in `ephe/`:

- `sepl_18.se1`
- `semo_18.se1`
- `seas_18.se1`
- `fixstars.cat`

Without them, the repo still works in fallback Moshier mode.

## Step 5. Optional Docker Path

```bash
docker compose up --build
```

The API is then exposed on port `8000`.

## Step 6. Optional Skill Installation

Use one of these folders depending on your host agent:

- `.claude/skills/india-vedic/`
- `.agents/skills/india-vedic/`

The skill expects this repo to be available locally and callable via `vedic-calculate`.
