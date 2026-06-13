# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sportscli is a Python CLI tool for fetching real-time sports data from the terminal. It is published as a PyPI package (`pip install sportscli`) and exposes a `sports` command. The project is in early MVP stage — only placeholder implementations exist so far.

## Development Setup

```bash
pip install -e .    # Editable install for local development (no version bumps needed)
```

## Key Commands

```bash
sports cricket      # Run cricket subcommand
sports chess        # Run chess subcommand
```

No lint, format, or test tooling is configured yet. The `tests/` directory exists but is empty.

## Releasing to PyPI

```bash
# 1. Bump version in pyproject.toml
# 2. Clean and rebuild
rm -rf dist build *.egg-info
python -m build
# 3. Upload
twine upload dist/*
```

PyPI does not allow re-uploading the same version, so always bump before building for release.

## Architecture

- **Entry point:** `sportscli/cli.py` — defines a `typer.Typer()` app. Each sport is a subcommand decorated with `@app.command()`.
- **CLI framework:** [Typer](https://typer.tiangolo.com/) for commands, [Rich](https://rich.readthedocs.io/) for terminal output formatting, `requests` for HTTP calls.
- **Intended command structure:** `sports [sport] [command] [args]` (e.g., `sports cricket ipl current`, `sports chess live`).

## Data Sources

- **Chess:** Lichess.org API — free, no key required. Example: `GET https://lichess.org/api/tournament`
- **Cricket:** CricketData API — requires a free API key. Keys are stored in the gitignored `information/` directory.

## Versioning Strategy

Semantic versioning (MAJOR.MINOR.PATCH):
- Patch: bugfixes and small improvements
- Minor: new features or new sport support
- Major: breaking changes
