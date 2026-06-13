import typer
from rich.columns import Columns
from rich.panel import Panel
from rich.text import Text

import sportscli.config as config
from sportscli import __version__
from sportscli.core.display import console, print_error, print_success, print_warning
from sportscli.sports.chess.app import app as chess_app
from sportscli.sports.cricket.app import app as cricket_app
from sportscli.sports.football.app import app as football_app

app = typer.Typer(
    name="sports",
    no_args_is_help=False,
    add_completion=False,
    help="Real-time sports data in your terminal.",
)

app.add_typer(chess_app,    name="chess",    help="Chess data from Lichess (no key needed).")
app.add_typer(cricket_app,  name="cricket",  help="Cricket live scores and schedules.")
app.add_typer(football_app, name="football", help="Football scores, standings, and fixtures.")

# ---------------------------------------------------------------------------
# Config sub-app
# ---------------------------------------------------------------------------

config_app = typer.Typer(help="Manage API keys and settings.")
app.add_typer(config_app, name="config", help="Manage API keys and settings.")

_KEYED_SPORTS = {
    "cricket": "cricketdata.org",
    "football": "football-data.org",
}


@config_app.command("setup")
def config_setup():
    """Interactive wizard to configure all API keys."""
    console.print(Panel("[bold cyan]sportscli setup[/bold cyan]", border_style="cyan"))
    for sport, source in _KEYED_SPORTS.items():
        existing = config.get_api_key(sport)
        if existing:
            console.print(f"[dim]{sport}:[/dim] already set ({existing[:6]}...)")
            replace = typer.confirm(f"Replace {sport} key?", default=False)
            if not replace:
                continue
        typer.echo(f"Get a free {sport} key at: https://{source}")
        key = typer.prompt(f"Enter {sport} API key")
        config.set_api_key(sport, key)
        print_success(f"{sport} key saved.")


@config_app.command("set")
def config_set(
    sport: str = typer.Argument(..., help="Sport name (cricket, football)"),
    key: str = typer.Argument(..., help="API key value"),
):
    """Set a single API key."""
    sport = sport.lower()
    if sport not in _KEYED_SPORTS:
        print_warning(f"Unknown sport '{sport}'. Known: {', '.join(_KEYED_SPORTS)}")
    config.set_api_key(sport, key)
    print_success(f"{sport} API key saved.")


@config_app.command("show")
def config_show():
    """Show stored configuration (keys partially masked)."""
    cfg = config.load()
    if not cfg:
        console.print("[dim]No config found. Run: sports config setup[/dim]")
        return

    api_keys = cfg.get("api_keys", {})
    if not api_keys:
        console.print("[dim]No API keys stored.[/dim]")
        return

    table_lines = []
    for sport, k in api_keys.items():
        masked = f"{k[:6]}{'*' * max(0, len(k) - 6)}" if k else "[dim]not set[/dim]"
        table_lines.append(f"  [cyan]{sport:<12}[/cyan] {masked}")

    console.print(Panel("\n".join(table_lines), title="Stored API Keys", border_style="cyan"))


# ---------------------------------------------------------------------------
# Welcome screen
# ---------------------------------------------------------------------------

def _show_welcome() -> None:
    logo = Text("⚽ 🏏 ♟  sportscli", style="bold white")

    sport_panels = [
        Panel(
            "[bold]chess[/bold]\n[dim]tournaments · live · broadcasts · player[/dim]",
            border_style="cyan",
            expand=True,
        ),
        Panel(
            "[bold]cricket[/bold]\n[dim]live · scorecard · schedule[/dim]",
            border_style="green",
            expand=True,
        ),
        Panel(
            "[bold]football[/bold]\n[dim]live · standings · fixtures[/dim]",
            border_style="yellow",
            expand=True,
        ),
    ]

    console.print()
    console.print(Panel(logo, border_style="bold white", subtitle=f"v{__version__}"))
    console.print(Columns(sport_panels, equal=True, expand=True))
    console.print()
    console.print("  Run [bold cyan]sports <sport> --help[/bold cyan] to get started.")
    console.print("  Run [bold cyan]sports config setup[/bold cyan] to configure API keys.")
    console.print()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        _show_welcome()


if __name__ == "__main__":
    app()
