import sys

import typer

import sportscli.config as config
from sportscli.core.display import print_error, print_success, print_warning, select_from_menu, status_spinner
from sportscli.core.exceptions import ApiError, AuthError, NetworkError
from sportscli.sports.chess.client import LichessClient
from sportscli.sports.f1.client import F1Client
from sportscli.sports.football.client import FootballDataClient
from sportscli.sports.fav import display

app = typer.Typer(
    help="Save and view updates for your favourite players, drivers, and leagues.",
    no_args_is_help=False,
)

# Maps the CLI-facing category name to the config key
_CATEGORY_MAP: dict[str, str] = {
    "chess":          "chess",
    "f1-driver":      "f1_driver",
    "f1-constructor": "f1_constructor",
    "football":       "football",
}

_CATEGORY_HINT = "chess | f1-driver | f1-constructor | football"


def _resolve_category(raw: str) -> str | None:
    return _CATEGORY_MAP.get(raw.lower())


@app.command()
def add(
    category: str = typer.Argument(..., help=f"Category: {_CATEGORY_HINT}"),
    value: str = typer.Argument(..., help="Username, driver ref, constructor ref, or league code"),
):
    """Add an item to your favourites."""
    key = _resolve_category(category)
    if key is None:
        print_warning(f"Unknown category '{category}'. Valid: {_CATEGORY_HINT}")
        raise typer.Exit(1)
    config.add_favourite(key, value.lower())
    print_success(f"Added '{value.lower()}' to {category} favourites.")


@app.command()
def remove(
    category: str = typer.Argument(..., help=f"Category: {_CATEGORY_HINT}"),
    value: str = typer.Argument(..., help="Item to remove"),
):
    """Remove an item from your favourites."""
    key = _resolve_category(category)
    if key is None:
        print_warning(f"Unknown category '{category}'. Valid: {_CATEGORY_HINT}")
        raise typer.Exit(1)
    removed = config.remove_favourite(key, value.lower())
    if removed:
        print_success(f"Removed '{value.lower()}' from {category} favourites.")
    else:
        print_warning(f"'{value.lower()}' was not in your {category} favourites.")


@app.command(name="list")
def list_favs():
    """List all saved favourites (no network calls)."""
    favs = config.get_favourites()
    display.render_favourites_list(favs)


@app.command()
def show():
    """Fetch live data for all your favourites and show a dashboard."""
    favs = config.get_favourites()

    chess_users: list[str] = favs.get("chess", [])
    f1_drivers: list[str] = favs.get("f1_driver", [])
    f1_constructors: list[str] = favs.get("f1_constructor", [])
    football_leagues: list[str] = favs.get("football", [])

    if not any([chess_users, f1_drivers, f1_constructors, football_leagues]):
        print_warning("No favourites saved. Run: sports fav add <category> <value>")
        return

    # --- Chess ---
    if chess_users:
        profiles: list[tuple[str, dict]] = []
        client = LichessClient()
        for username in chess_users:
            try:
                with status_spinner(f"Fetching chess profile: {username}..."):
                    profile = client.get_player(username)
                profiles.append((username, profile))
            except NetworkError as e:
                print_error(f"Network error fetching {username}: {e}")
            except ApiError as e:
                print_error(f"Could not fetch {username}: {e}")
        display.render_chess_section(profiles)

    # --- F1 drivers + constructors (one standings call each) ---
    if f1_drivers or f1_constructors:
        f1 = F1Client()

        if f1_drivers:
            try:
                with status_spinner("Fetching F1 driver standings..."):
                    data = f1.get_driver_standings()
                entries = (
                    data.get("MRData", {})
                    .get("StandingsTable", {})
                    .get("StandingsLists", [{}])[0]
                    .get("DriverStandings", [])
                )
                display.render_f1_drivers_section(entries, f1_drivers)
            except (NetworkError, ApiError) as e:
                print_error(f"Could not fetch F1 driver standings: {e}")

        if f1_constructors:
            try:
                with status_spinner("Fetching F1 constructor standings..."):
                    data = f1.get_constructor_standings()
                entries = (
                    data.get("MRData", {})
                    .get("StandingsTable", {})
                    .get("StandingsLists", [{}])[0]
                    .get("ConstructorStandings", [])
                )
                display.render_f1_constructors_section(entries, f1_constructors)
            except (NetworkError, ApiError) as e:
                print_error(f"Could not fetch F1 constructor standings: {e}")

    # --- Football leagues ---
    if football_leagues:
        key = config.get_api_key("football")
        if not key:
            print_warning(
                "No football API key found. Run: sports config set football <key>\n"
                "Get a free key at: https://www.football-data.org/client/register"
            )
        else:
            client_fb = FootballDataClient(api_key=key)
            for code in football_leagues:
                try:
                    with status_spinner(f"Fetching standings for {code.upper()}..."):
                        data = client_fb.get_standings(code)
                    display.render_football_league_section(code, data)
                except AuthError:
                    print_error("Invalid football API key. Run: sports config set football <key>")
                    break
                except (NetworkError, ApiError) as e:
                    print_error(f"Could not fetch {code.upper()} standings: {e}")


def _show_menu() -> None:
    choice = select_from_menu("Favourites — Select a command", [
        ("show",   "Dashboard with live data for all favourites"),
        ("list",   "List saved favourites (no network calls)"),
        ("add",    "Add a favourite"),
        ("remove", "Remove a favourite"),
    ])
    if choice == 1:
        show()
    elif choice == 2:
        list_favs()
    elif choice == 3:
        from rich.prompt import Prompt as _Prompt
        cat = _Prompt.ask(f"Category ({_CATEGORY_HINT})")
        val = _Prompt.ask("Value")
        add(cat, val)
    elif choice == 4:
        from rich.prompt import Prompt as _Prompt
        cat = _Prompt.ask(f"Category ({_CATEGORY_HINT})")
        val = Prompt.ask("Value")
        remove(cat, val)


@app.callback(invoke_without_command=True)
def _main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None and sys.stdin.isatty():
        _show_menu()
