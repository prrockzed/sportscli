import sys

import typer
from rich.prompt import Prompt

import sportscli.config as config
from sportscli.core.display import console, print_error, select_from_menu, status_spinner
from sportscli.core.exceptions import ApiError, AuthError, NetworkError
from sportscli.sports.cricket import display
from sportscli.sports.cricket.client import CricketDataClient

app = typer.Typer(
    help="Cricket live scores and schedules (cricketdata.org API key required).",
    no_args_is_help=False,
)

_SPORT = "cricket"


def _get_client() -> CricketDataClient:
    key = config.get_api_key(_SPORT)
    if not key:
        typer.echo("No Cricket API key found.")
        key = typer.prompt("Enter your cricketdata.org API key")
        config.set_api_key(_SPORT, key)
        typer.echo("Key saved.")
    return CricketDataClient(api_key=key)


@app.command()
def live():
    """Show currently live cricket matches."""
    try:
        client = _get_client()
        with status_spinner("Fetching live matches..."):
            data = client.get_live_matches()
        display.render_live_matches(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except AuthError:
        print_error("Invalid API key. Run: sports config set cricket <key>")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def scorecard(match_id: str = typer.Argument(..., help="Match ID from 'sports cricket live'")):
    """Show detailed scorecard for a match."""
    try:
        client = _get_client()
        with status_spinner(f"Fetching scorecard for {match_id}..."):
            data = client.get_scorecard(match_id)
        display.render_scorecard(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except AuthError:
        print_error("Invalid API key. Run: sports config set cricket <key>")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def schedule():
    """Show upcoming cricket matches."""
    try:
        client = _get_client()
        with status_spinner("Fetching schedule..."):
            data = client.get_schedule()
        display.render_schedule(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except AuthError:
        print_error("Invalid API key. Run: sports config set cricket <key>")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


def _show_menu() -> None:
    choice = select_from_menu("Cricket — Select a command", [
        ("live",      "Currently live matches"),
        ("scorecard", "Detailed scorecard for a match"),
        ("schedule",  "Upcoming matches"),
    ])
    if choice == 1:
        live()
    elif choice == 2:
        console.print("\n[dim]Fetching live matches so you can pick a match ID...[/dim]")
        live()
        match_id = Prompt.ask("\nEnter match ID from the list above")
        scorecard(match_id)
    elif choice == 3:
        schedule()


@app.callback(invoke_without_command=True)
def _main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None and sys.stdin.isatty():
        _show_menu()
