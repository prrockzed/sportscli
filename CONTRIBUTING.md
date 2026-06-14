# Contributing to sportscli

Thanks for taking the time to contribute. All contributions are welcome — bug fixes, new sports, new commands, documentation improvements, or anything else that makes the project better.

## Getting Started

```bash
git clone https://github.com/prrockzed/sportscli.git
cd sportscli
pip install -e .
```

This installs the package in editable mode, so changes to the source are reflected immediately without reinstalling.

## Project Structure

```
sportscli/
├── core/
│   ├── exceptions.py   # Exception hierarchy
│   ├── http.py         # BaseAPIClient (retry, error mapping)
│   └── display.py      # Shared Rich console and helpers
├── sports/
│   ├── chess/          # app.py, client.py, display.py
│   ├── cricket/        # app.py, client.py, display.py
│   └── football/       # app.py, client.py, display.py
├── cli.py              # Root Typer app, registers all sub-apps
└── config.py           # Read/write ~/.config/sportscli/config.json
```

Each sport is a self-contained module. Adding a new sport does not require touching any existing file except `cli.py` (one line to register the sub-app).

## Adding a New Sport

1. Create the directory and files:

```
sportscli/sports/<sport>/
├── __init__.py
├── client.py    # Extends BaseAPIClient
├── display.py   # Rich tables/panels, no business logic
└── app.py       # Typer sub-app, imports client + display
```

2. Follow the existing pattern in `app.py`:

```python
app = typer.Typer(help="...")

@app.command()
def live():
    try:
        client = SportClient()
        data = client.get_live(...)
        display.render_live(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)
```

3. Register it in `cli.py`:

```python
from sportscli.sports.<sport>.app import app as <sport>_app
app.add_typer(<sport>_app, name="<sport>", help="...")
```

4. Add the commands to the README command reference.

## Reporting Bugs

Open an issue at [github.com/prrockzed/sportscli/issues](https://github.com/prrockzed/sportscli/issues) with:

- What command you ran
- What you expected to happen
- What actually happened (paste the full error output)
- Your OS and Python version (`python --version`)

## Submitting a Pull Request

The `main` branch is protected — no direct pushes are allowed. Every change goes through a PR.

1. **Open an issue first** describing what you want to fix or build:
   [github.com/prrockzed/sportscli/issues/new](https://github.com/prrockzed/sportscli/issues/new)

2. **Create a branch** referencing the issue number:
   ```bash
   git checkout -b feat/issue-12-add-tennis
   git checkout -b fix/issue-15-chess-crash
   ```

3. **Make your changes** and write or update tests for them.

4. **Run the test suite locally** before pushing:
   ```bash
   pytest
   ```
   All 185 tests must pass. PRs with failing tests cannot be merged.

5. **Push the branch and open a PR:**
   ```bash
   git push origin feat/issue-12-add-tennis
   ```
   In the PR description, write `Closes #12` to link it to the issue.

6. **Tests run automatically** — the CI workflow tests against Python 3.10, 3.11, and 3.12. All three must be green.

7. **Wait for review** — the maintainer (prrockzed) will review and approve before the PR can be merged.

Keep pull requests focused. One feature or fix per PR makes review faster.

## Code Style

- Follow the patterns already established in the codebase.
- Keep display logic in `display.py` and API logic in `client.py` — don't mix them.
- All errors raised from `client.py` must be subclasses of `SportsCLIError`.
- No new dependencies without a good reason — the goal is a lightweight tool.

## Versioning

This project uses semantic versioning (`MAJOR.MINOR.PATCH`):

- `PATCH` — bug fixes, small improvements
- `MINOR` — new commands, new sports, new features
- `MAJOR` — breaking changes to the CLI interface

Version is set in two places: `pyproject.toml` and `sportscli/__init__.py`.
