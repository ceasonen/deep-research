# Contributing

## Development setup
1. Fork and clone.
2. `cp .env.example .env`
3. `pip install -e ".[all]"`
4. `cd frontend && npm install`

## Quality checks
- `ruff check backend`
- `pytest -q`
- `cd frontend && npm run build`

## Pull request checklist
- Keep PR focused on one goal.
- Add or update tests where behavior changes.
- Update docs when API or setup changes.
