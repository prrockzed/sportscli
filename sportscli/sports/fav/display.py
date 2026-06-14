from rich.panel import Panel
from rich.table import Table

from sportscli.core.display import console

# Valid categories and their display labels
CATEGORIES: dict[str, str] = {
    "chess":          "Chess Players",
    "f1_driver":      "F1 Drivers",
    "f1_constructor": "F1 Constructors",
    "football":       "Football Leagues",
}


def render_favourites_list(favs: dict) -> None:
    """Display saved favourites without fetching any data."""
    if not any(favs.get(cat) for cat in CATEGORIES):
        console.print("[dim]No favourites saved. Run: sports fav add <category> <value>[/dim]")
        return

    for cat, label in CATEGORIES.items():
        items = favs.get(cat, [])
        if not items:
            continue
        table = Table(title=label, show_header=False, show_lines=False, box=None)
        table.add_column("item", style="cyan")
        for item in items:
            table.add_row(item)
        console.print(table)


def render_chess_section(profiles: list[tuple[str, dict]]) -> None:
    """profiles: list of (username, profile_dict)"""
    if not profiles:
        return

    table = Table(show_lines=True)
    table.add_column("Player", style="bold cyan")
    table.add_column("Blitz", justify="right", style="green")
    table.add_column("Rapid", justify="right", style="green")
    table.add_column("Classical", justify="right", style="green")
    table.add_column("Bullet", justify="right", style="dim")

    for username, profile in profiles:
        perfs = profile.get("perfs", {})
        blitz     = str(perfs.get("blitz",     {}).get("rating", "—"))
        rapid     = str(perfs.get("rapid",     {}).get("rating", "—"))
        classical = str(perfs.get("classical", {}).get("rating", "—"))
        bullet    = str(perfs.get("bullet",    {}).get("rating", "—"))
        table.add_row(username, blitz, rapid, classical, bullet)

    console.print(Panel(table, title="[bold]Chess Players[/bold]", border_style="cyan"))


def render_f1_drivers_section(entries: list[dict], wanted: list[str]) -> None:
    """entries: full DriverStandings list; wanted: list of driverRef strings."""
    if not wanted:
        return

    wanted_lower = {w.lower() for w in wanted}
    matched = [
        e for e in entries
        if e.get("Driver", {}).get("driverId", "").lower() in wanted_lower
    ]

    if not matched:
        console.print(Panel(
            "[dim]No standing data found for your F1 driver favourites.[/dim]",
            title="[bold]F1 Drivers[/bold]",
            border_style="red",
        ))
        return

    table = Table(show_lines=True)
    table.add_column("Pos", justify="right", style="dim")
    table.add_column("Driver", style="bold cyan")
    table.add_column("Team", style="white")
    table.add_column("Wins", justify="right", style="green")
    table.add_column("Points", justify="right", style="bold green")

    for entry in matched:
        driver = entry.get("Driver", {})
        name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
        constructors = entry.get("Constructors", [{}])
        team = constructors[0].get("name", "") if constructors else ""
        table.add_row(
            entry.get("position", ""),
            name,
            team,
            entry.get("wins", "0"),
            entry.get("points", "0"),
        )

    console.print(Panel(table, title="[bold]F1 Drivers[/bold]", border_style="red"))


def render_f1_constructors_section(entries: list[dict], wanted: list[str]) -> None:
    """entries: full ConstructorStandings list; wanted: list of constructorId strings."""
    if not wanted:
        return

    wanted_lower = {w.lower() for w in wanted}
    matched = [
        e for e in entries
        if e.get("Constructor", {}).get("constructorId", "").lower() in wanted_lower
    ]

    if not matched:
        console.print(Panel(
            "[dim]No standing data found for your F1 constructor favourites.[/dim]",
            title="[bold]F1 Constructors[/bold]",
            border_style="red",
        ))
        return

    table = Table(show_lines=True)
    table.add_column("Pos", justify="right", style="dim")
    table.add_column("Constructor", style="bold cyan")
    table.add_column("Nationality", style="yellow")
    table.add_column("Wins", justify="right", style="green")
    table.add_column("Points", justify="right", style="bold green")

    for entry in matched:
        constructor = entry.get("Constructor", {})
        table.add_row(
            entry.get("position", ""),
            constructor.get("name", ""),
            constructor.get("nationality", ""),
            entry.get("wins", "0"),
            entry.get("points", "0"),
        )

    console.print(Panel(table, title="[bold]F1 Constructors[/bold]", border_style="red"))


def render_football_league_section(league_code: str, data: dict) -> None:
    """Render top 5 of a football league standings."""
    competition = data.get("competition", {}).get("name", league_code.upper())
    standings_groups = data.get("standings", [])

    if not standings_groups:
        console.print(Panel(
            "[dim]No standings available.[/dim]",
            title=f"[bold]{competition}[/bold]",
            border_style="yellow",
        ))
        return

    table_rows = standings_groups[0].get("table", [])[:5]

    table = Table(show_lines=True)
    table.add_column("Pos", justify="right", style="dim")
    table.add_column("Team", style="bold cyan")
    table.add_column("P", justify="right")
    table.add_column("W", justify="right", style="green")
    table.add_column("D", justify="right")
    table.add_column("L", justify="right", style="red")
    table.add_column("GD", justify="right")
    table.add_column("Pts", justify="right", style="bold green")

    for row in table_rows:
        team = row.get("team", {}).get("name", "")
        table.add_row(
            str(row.get("position", "")),
            team,
            str(row.get("playedGames", "")),
            str(row.get("won", "")),
            str(row.get("draw", "")),
            str(row.get("lost", "")),
            str(row.get("goalDifference", "")),
            str(row.get("points", "")),
        )

    console.print(Panel(table, title=f"[bold]{competition}[/bold]", border_style="yellow"))
