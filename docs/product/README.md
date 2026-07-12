# Vedic Reading Web App — Product Handoff

This folder is the implementation source of truth for turning `Phat-Po/vedic-reading-engine` into a Simplified Chinese, mobile-first consumer web app / mini-program.

## Read order for Codex or Claude Code

1. `PRD.md`
2. `UX-FLOWS.md`
3. `SCREEN-SPECS.md`
4. `DESIGN-REFERENCE.md`
5. Existing repository files: `AGENTS.md`, `RULES.md`, `README.md`, `src/vedic_engine/schemas.py`, and `src/vedic_engine/api.py`

## Reference images

- `references/direction-a-modern-chinese-editorial.png`
- `references/direction-b-modern-vedic-geometry.png`
- `references/direction-c-premium-digital-astrology.png`

The chosen direction is a hybrid:

- Overall system and report preview: Direction B
- Beautified chart screen: C1, simplified and made less decorative
- Agent screen information architecture: A3
- Share card: A4 information structure plus C4 social impact

Reference images are visual intent only. Never copy their generated chart data, Chinese text, QR code, or astrology claims into production.

## First implementation goal

Build a clickable mobile-first prototype covering birth input, free chart preview, report paywall, report generation state, web report reading, contextual agent Q&A, profile switching, and share-card preview. Do not connect real payment until the product flow and cost model are validated.

