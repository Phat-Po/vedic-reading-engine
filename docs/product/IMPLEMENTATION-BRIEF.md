# Implementation Brief for Codex / Claude Code

## Mission

Turn `Phat-Po/vedic-reading-engine` into a mobile-first Simplified Chinese PWA using the specifications in this folder. Preserve the deterministic calculation engine and `RULES.md` boundaries.

## Required first pass

1. Audit current FastAPI schemas and output data against the PRD.
2. Produce a gap matrix: existing / missing / needs change.
3. Propose the smallest frontend architecture that supports PWA first and later mini-program adaptation.
4. Build a clickable prototype with fixture data before connecting payment or production LLM calls.
5. Implement the beautified/professional chart toggle with real structured fixture data.
6. Verify every core state at 375px, 390px, 430px, and desktop.

## Do not do yet

- Do not implement real payment before purchase flow approval.
- Do not add subscriptions.
- Do not create a public social feed.
- Do not generate all locked report content during free preview.
- Do not use a static AI-generated chart image as production UI.
- Do not expose birth data on share cards.

## Recommended delivery slices

### Slice 1 — Product shell

Mobile navigation, profile switcher, fixture profiles, birth input, free chart, preview sections.

### Slice 2 — Agent

Single-profile chat, suggestions, quota display, credit confirmation, report CTA, evidence drawer.

### Slice 3 — Report

Purchase confirmation mock, asynchronous progress mock, web report, section-to-agent transition.

### Slice 4 — Profiles and sharing

Profile manager, dual-profile selection shell, share-card code renderer, privacy checks.

### Slice 5 — Real integration

FastAPI connection, persistent database, auth, job queue, LLM cost controls, credit ledger, payment.

## Definition of done for the prototype

- Core flow is clickable end-to-end.
- No mobile overflow at target widths.
- Profile switching never leaks previous profile data.
- Beautified/professional mode preserves the same underlying chart.
- Free preview contains only generated one-line sections, not hidden full content.
- Agent works before report purchase and contains contextual report CTA.
- Chapter question carries the correct section context and asks for confirmation before consuming credit.
- Share card contains no birth date, time, or place.
- Concept reference and implementation screenshot are compared before signoff.

