import sys

import typer

from sportscli.core.display import print_error, select_from_menu, status_spinner
from sportscli.core.exceptions import ApiError, NetworkError
from sportscli.sports.f1 import display
from sportscli.sports.f1.client import F1Client, OpenF1Client

app = typer.Typer(
    help="Formula 1 schedule, standings, results, and live session data (no key required).",
    no_args_is_help=False,
)


@app.command()
def schedule():
    """Show the current F1 season race calendar."""
    try:
        with status_spinner("Fetching F1 schedule..."):
            data = F1Client().get_schedule()
        display.render_schedule(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def standings():
    """Show the current F1 driver championship standings."""
    try:
        with status_spinner("Fetching driver standings..."):
            data = F1Client().get_driver_standings()
        display.render_driver_standings(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def constructors():
    """Show the current F1 constructor championship standings."""
    try:
        with status_spinner("Fetching constructor standings..."):
            data = F1Client().get_constructor_standings()
        display.render_constructor_standings(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def results():
    """Show the results of the most recent F1 race."""
    try:
        with status_spinner("Fetching race results..."):
            data = F1Client().get_race_results()
        display.render_race_results(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def live():
    """Show live position data for the current or most recent F1 session."""
    try:
        client = OpenF1Client()
        with status_spinner("Fetching live session..."):
            sessions = client.get_latest_session()
            if not sessions:
                print_error("No session data available.")
                raise typer.Exit(1)
            session = sessions[0]
            session_key = session.get("session_key")
            positions = client.get_positions(session_key)
            drivers = client.get_drivers(session_key)
        display.render_live_session(session, positions, drivers)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


def _show_menu() -> None:
    choice = select_from_menu("Formula 1 — Select a command", [
        ("schedule",     "Current season race calendar"),
        ("standings",    "Driver championship standings"),
        ("constructors", "Constructor championship standings"),
        ("results",      "Last race results"),
        ("live",         "Live session positions"),
    ])
    if choice == 1:
        schedule()
    elif choice == 2:
        standings()
    elif choice == 3:
        constructors()
    elif choice == 4:
        results()
    elif choice == 5:
        live()


@app.callback(invoke_without_command=True)
def _main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None and sys.stdin.isatty():
        _show_menu()
