# sportscli

Real-time sports data in your terminal. Chess, Cricket, and Football — all from a single `sports` command.

## Requirements

- Python 3.10+

## Installation

```bash
pip install sportscli
```

Works the same on Linux, macOS, and Windows. On Windows, make sure your Python Scripts directory is on your PATH.

## Quick Start

```bash
sports                        # Welcome screen with all available commands
sports chess live             # Live games on Lichess TV (no API key needed)
sports chess tournaments      # Current and upcoming Lichess tournaments
sports cricket live           # Live cricket scores (prompts for API key on first run)
sports football standings pl  # Premier League table
```

## Configuration

### Chess
No API key required — Lichess is fully open.

### Cricket
Free API key from [cricketdata.org](https://cricketdata.org). You will be prompted automatically on first use, or set it manually:

```bash
sports config set cricket <your-key>
```

### Football
Free API key from [football-data.org](https://www.football-data.org/client/register). Set it with:

```bash
sports config set football <your-key>
```

Keys are stored in `~/.config/sportscli/config.json`.

## Commands

### Chess (no key required)

```bash
sports chess tournaments              # Current and upcoming tournaments
sports chess live                     # Live games by time control on Lichess TV
sports chess broadcasts               # Major chess broadcasts and events
sports chess player <username>        # Player profile, ratings, and recent games
```

### Cricket

```bash
sports cricket live                   # Live match scores
sports cricket scorecard <match-id>   # Detailed scorecard (get ID from 'cricket live')
sports cricket schedule               # Upcoming matches
```

### Football

| League code | Competition             |
|-------------|-------------------------|
| `pl`        | Premier League          |
| `bl1`       | Bundesliga              |
| `sa`        | Serie A                 |
| `pd`        | La Liga                 |
| `fl1`       | Ligue 1                 |
| `ucl`       | UEFA Champions League   |
| `ec`        | European Championship   |
| `wc`        | FIFA World Cup          |

```bash
sports football live                  # All currently live matches
sports football standings pl          # League table
sports football fixtures ucl          # Upcoming fixtures
```

### Config

```bash
sports config setup                   # Interactive wizard for all API keys
sports config set <sport> <key>       # Set a single API key
sports config show                    # Show stored keys (partially masked)
```

## Development Setup

```bash
git clone https://github.com/prrockzed/sportscli.git
cd sportscli
pip install -e .
```

## Release Process

```bash
# 1. Bump version in pyproject.toml and sportscli/__init__.py
# 2. Clean and rebuild
rm -rf dist build *.egg-info
python -m build
# 3. Upload to PyPI
twine upload dist/*
```

PyPI does not allow re-uploading the same version — always bump before building.

## Adding a New Sport

1. `mkdir sportscli/sports/<sport>`
2. Create `__init__.py`, `client.py`, `display.py`, `app.py` following the existing pattern
3. In `cli.py`: `app.add_typer(<sport>_app, name="<sport>", help="...")`
4. Done — no changes to any other existing file

## License

MIT
