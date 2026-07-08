# Onboarding Prompt

Send this to your AI agent:

```text
You are onboarding this repository for local use.

Your job is not to explain the repo in abstract terms. Your job is to get the project running locally with the simplest supported path, verify the main flows, and report the exact result.

Repository instructions:
1. Read README.md first.
2. Then read ONBOARDING_PROMPT.md, SETUP.md, and docs/INDEX.md if they exist.
3. Do not assume secrets are required unless the docs explicitly say so.
4. Do not refactor or rewrite project code unless setup is blocked by a concrete fix that is clearly necessary.
5. Stop at the first real blocker and report it precisely.

Execution task:
1. Install the project with the simplest supported local setup path.
2. Run the primary test or smoke-test path.
3. Run the sample CLI flow.
4. Start the main API entrypoint.
5. Verify the project is working.

Minimum commands to attempt unless repo docs override them:
- create and activate a virtualenv
- pip install -e ".[dev]"
- pytest
- vedic-calculate --sample
- uvicorn vedic_engine.api:app --reload

What counts as success:
- dependencies install successfully
- tests pass or the repo clearly documents an expected exception
- the sample CLI run completes
- the API starts locally
- you can verify GET /api/v1/health or load /docs successfully

Required final output:
- exact commands you ran
- whether each step passed or failed
- the local URL or command a human should use to verify success
- any missing optional assets such as Swiss Ephemeris files
- if blocked, the first blocker only, with the exact error text and the file or command where it happened

Important project-specific notes:
- Moshier fallback mode is acceptable if Swiss Ephemeris files are missing
- do not invent a cloud dependency
- do not ask the operator vague questions if the repo already documents the next step
```

## Expected Flow

1. Read `README.md`
2. Read `SETUP.md`
3. Install dependencies in a local virtualenv
4. Run `pytest`
5. Run `vedic-calculate --sample`
6. Start `uvicorn vedic_engine.api:app --reload`
7. Confirm `http://127.0.0.1:8000/docs` or `GET /api/v1/health`

## Notes

- If Swiss Ephemeris files are missing, fallback Moshier mode is acceptable for first setup.
- Do not assume local secret files are needed.
- Report exact commands, outputs, and the first concrete blocker if setup fails.
