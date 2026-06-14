# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sportscli is a Python CLI tool for fetching real-time sports data from the terminal. It is published as a PyPI package (`pip install sportscli`) and exposes a `sports` command. Currently supports Chess (Lichess), Cricket (cricketdata.org), and Football (football-data.org).

## Development Setup

```bash
pip install -e ".[dev]"   # Editable install with test dependencies
```

The project uses a `.venv` directory for local development. If `pip` is not available on the system Python, use `.venv/bin/pip` directly.

## Key Commands

```bash
sports                        # Welcome screen
sports chess live             # Live Lichess TV games (no key needed)
sports cricket live           # Live cricket scores (requires API key)
sports football standings pl  # Premier League table (requires API key)
sports config set cricket <key>
sports config set football <key>
sports config show
```

## Running Tests

```bash
pytest                        # Run all 185 tests
pytest tests/core/            # Run only core tests
pytest tests/sports/chess/    # Run only chess tests
pytest -v                     # Verbose output
```

All tests are fully mocked — no network calls are made. Tests must pass before any PR can be merged.

## Developer Workflow

**Main branch is protected. No direct pushes allowed.**

The full workflow for every change, no matter how small:

```
1. Create a GitHub issue describing the change
   → github.com/prrockzed/sportscli/issues/new

2. Create a branch locally (reference the issue number)
   git checkout -b feat/issue-12-add-tennis
   git checkout -b fix/issue-15-chess-display-crash

3. Make changes and write/update tests

4. Run tests locally before pushing
   pytest

5. Push the branch
   git push origin feat/issue-12-add-tennis

6. Open a PR on GitHub
   → Link it to the issue (write "Closes #12" in the PR description)
   → Tests run automatically on the PR (3.10, 3.11, 3.12)

7. Wait for all 3 test matrix jobs to go green

8. Merge the PR
   → Owner (prrockzed) can merge their own PRs directly
   → External contributors need owner approval before merging
```

Branch naming convention:
- `feat/issue-<n>-<short-description>` — new feature
- `fix/issue-<n>-<short-description>` — bug fix
- `docs/issue-<n>-<short-description>` — documentation only
- `test/issue-<n>-<short-description>` — tests only

## CI / Branch Protection

Two workflows run on every push and PR to `main`:

- **`python-package.yml`** — runs the full test suite against Python 3.10, 3.11, 3.12 in parallel. All three must pass before a PR can be merged.
- **`python-publish.yml`** — runs tests and publishes to PyPI automatically when a GitHub Release is created (uses trusted publishing, no token needed).

Branch protection rules on `main`:
- Direct pushes blocked for everyone
- PR required for all changes
- 1 approval required (owner can bypass for their own PRs)
- Stale reviews dismissed when new commits are pushed
- All 3 test matrix jobs must be green

## Releasing to PyPI

### Automated (recommended)

1. Bump version in `pyproject.toml` and `sportscli/__init__.py`
2. Commit and merge to `main` via PR
3. Go to GitHub → Releases → Draft a new release
4. Tag it `v0.x.x`, write release notes, click Publish
5. The `python-publish.yml` workflow runs automatically: builds the package, runs tests, and uploads to PyPI

### Manual (fallback)

```bash
# 1. Bump version in pyproject.toml and sportscli/__init__.py
# 2. Clean and rebuild
rm -rf dist build
pyproject-build
# 3. Upload (requires ~/.pypirc with API token)
twine upload dist/*
```

PyPI does not allow re-uploading the same version — always bump before building.

## Architecture

- **Entry point:** `sportscli/cli.py` — root Typer app, registers sport sub-apps and config sub-app
- **CLI framework:** Typer for commands, Rich for terminal output, requests for HTTP
- **Command structure:** `sports <sport> <command> [args]`

```
sportscli/
├── core/
│   ├── exceptions.py   # SportsCLIError hierarchy
│   ├── http.py         # BaseAPIClient (session, retry, error mapping)
│   └── display.py      # Shared Rich console, print_error/warning/success
├── sports/
│   ├── chess/          # app.py, client.py, display.py
│   ├── cricket/        # app.py, client.py, display.py
│   └── football/       # app.py, client.py, display.py
├── cli.py              # Root app + config sub-app
└── config.py           # Read/write ~/.config/sportscli/config.json
```

## Data Sources

- **Chess:** Lichess.org API — free, no key required
- **Cricket:** cricketdata.org — free API key, 100 req/day
- **Football:** football-data.org — free API key, 10 req/min

## Versioning Strategy

Semantic versioning (MAJOR.MINOR.PATCH):
- Patch: bugfixes and small improvements
- Minor: new features or new sport support
- Major: breaking changes to the CLI interface

Version must be updated in two places: `pyproject.toml` and `sportscli/__init__.py`.
