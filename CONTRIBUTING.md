# Contributing

## Development

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Local-Only Artifacts

Do not commit local runtime data:

- `profiles/`
- `output/`
- `.venv/`
- `ephe/*.se1`
- `ephe/fixstars.cat`

Keep those files on your machine if you use this repo locally. Public git history
should contain source, tests, templates, and skill definitions only.

## Skill Compatibility

This repo keeps both `.claude/skills/india-vedic/` and `.agents/skills/india-vedic/`
so existing local usage does not break while the public repo remains easy to copy
into different agent environments.
