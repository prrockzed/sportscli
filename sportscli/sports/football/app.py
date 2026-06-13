import typer

import sportscli.config as config
from sportscli.core.display import print_error, status_spinner
from sportscli.core.exceptions import ApiError, AuthError, NetworkError
from sportscli.sports.football import display
from sportscli.sports.football.client import LEAGUE_IDS, FootballDataClient

app = typer.Typer(help="Football scores, standings, and fixtures (football-data.org API key required).")

_SPORT = "football"

_LEAGUE_HINT = (
    "League codes: pl (Premier League), bl1 (Bundesliga), sa (Serie A), "
    "pd (La Liga), fl1 (Ligue 1), ucl (Champions League)"
)


def _get_client() -> FootballDataClient:
    key = config.get_api_key(_SPORT)
    if not key:
        typer.echo("No Football API key found.")
        typer.echo("Get a free key at: https://www.football-data.org/client/register")
        key = typer.prompt("Enter your football-data.org API key")
        config.set_api_key(_SPORT, key)
        typer.echo("Key saved.")
    return FootballDataClient(api_key=key)


@app.command()
def live():
    """Show all currently live football matches."""
    try:
        client = _get_client()
        with status_spinner("Fetching live matches..."):
            data = client.get_live_matches()
        display.render_live_matches(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except AuthError:
        print_error("Invalid API key. Run: sports config set football <key>")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def standings(
    league: str = typer.Argument(..., help=f"League code. {_LEAGUE_HINT}"),
):
    """Show the league table for a competition."""
    try:
        client = _get_client()
        with status_spinner(f"Fetching standings for {league.upper()}..."):
            data = client.get_standings(league)
        display.render_standings(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except AuthError:
        print_error("Invalid API key. Run: sports config set football <key>")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def fixtures(
    league: str = typer.Argument(..., help=f"League code. {_LEAGUE_HINT}"),
):
    """Show upcoming fixtures for a competition."""
    try:
        client = _get_client()
        with status_spinner(f"Fetching fixtures for {league.upper()}..."):
            data = client.get_fixtures(league)
        display.render_fixtures(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except AuthError:
        print_error("Invalid API key. Run: sports config set football <key>")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)
