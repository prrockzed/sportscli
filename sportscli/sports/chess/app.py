import typer

from sportscli.core.display import print_error, status_spinner
from sportscli.core.exceptions import ApiError, NetworkError
from sportscli.sports.chess import display
from sportscli.sports.chess.client import LichessClient

app = typer.Typer(help="Chess data from Lichess (no API key required).")


@app.command()
def tournaments():
    """Show current and upcoming Lichess tournaments."""
    try:
        with status_spinner("Fetching tournaments..."):
            data = LichessClient().get_tournaments()
        display.render_tournaments(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def live():
    """Show live games currently featured on Lichess TV."""
    try:
        with status_spinner("Fetching live games..."):
            games = LichessClient().get_live_games()
        display.render_live_games(games)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def broadcasts():
    """Show ongoing chess broadcasts and major events."""
    try:
        with status_spinner("Fetching broadcasts..."):
            data = LichessClient().get_broadcasts()
        display.render_broadcasts(data)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)


@app.command()
def player(username: str = typer.Argument(..., help="Lichess username")):
    """Show a player's profile, ratings, and recent games."""
    try:
        client = LichessClient()
        with status_spinner(f"Fetching profile for {username}..."):
            profile = client.get_player(username)
            games = client.get_player_games(username)
        display.render_player(profile, games)
    except NetworkError as e:
        print_error(f"Network error: {e}")
        raise typer.Exit(1)
    except ApiError as e:
        print_error(f"API error: {e}")
        raise typer.Exit(1)
