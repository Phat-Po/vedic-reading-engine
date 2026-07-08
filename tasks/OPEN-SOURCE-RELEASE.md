# Open Source Release Notes

## GitHub Metadata

- Repository name: `vedic-reading-engine`
- Description: `Self-hosted Vedic astrology engine with Swiss Ephemeris calculations, SVG chart rendering, offline interpretation, and Codex/Claude skill integration.`
- Topics:
  - `vedic-astrology`
  - `jyotish`
  - `astrology`
  - `swiss-ephemeris`
  - `fastapi`
  - `python`
  - `svg`
  - `llm`
  - `agent-skill`
  - `codex`
  - `claude-code`
  - `self-hosted`

## Release Boundary

- Keep local `profiles/`, `output/`, and `ephe/` directories working
- Stop tracking generated reports and personal chart artifacts in git
- Keep both skill layouts for compatibility: `.claude/` and `.agents/`
- Preserve existing CLI and API entrypoints

## License Decision

- Repository license: `AGPL-3.0-or-later`
- Reason: the project depends on `pyswisseph`, so permissive relicensing would
  not be safe without changing dependency and redistribution assumptions
