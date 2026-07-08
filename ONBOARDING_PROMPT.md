# Onboarding Prompt

Send this to your AI agent:

```text
Clone this repository, read README.md first, then install dependencies, run the main smoke test, start the primary entrypoint, and tell me exactly how to verify the project is working. Prefer the simplest supported path first. If ONBOARDING_PROMPT.md, SETUP.md, or docs/INDEX.md exist, use them. If setup fails, stop at the first concrete blocker and report it clearly.
```

## Expected Flow

1. Read `README.md`
2. Read `SETUP.md`
3. Install dependencies
4. Run `pytest`
5. Run `vedic-calculate --sample`
6. Start `uvicorn vedic_engine.api:app --reload`
7. Confirm the API docs load at `http://127.0.0.1:8000/docs`

## Notes

- If Swiss Ephemeris files are missing, fallback Moshier mode is acceptable for first setup.
- Do not assume local secret files are needed.
- Report the exact verification path back to the operator.
