from rich.panel import Panel
from rich.table import Table

from sportscli.core.display import console


def render_tournaments(data: dict) -> None:
    created = data.get("created", [])
    started = data.get("started", [])
    finished = data.get("finished", [])

    if started:
        table = Table(title="Live Tournaments", show_lines=True)
        table.add_column("Name", style="bold cyan")
        table.add_column("Variant", style="yellow")
        table.add_column("Clock", style="green")
        table.add_column("Players", justify="right")
        table.add_column("Status", style="bold green")
        for t in started:
            clock = t.get("clock", {})
            clock_str = f"{clock.get('limit', 0) // 60}+{clock.get('increment', 0)}"
            table.add_row(
                t.get("fullName", t.get("id", "")),
                t.get("variant", {}).get("name", "Standard"),
                clock_str,
                str(t.get("nbPlayers", 0)),
                "LIVE",
            )
        console.print(table)

    if created:
        table = Table(title="Upcoming Tournaments", show_lines=True)
        table.add_column("Name", style="bold cyan")
        table.add_column("Variant", style="yellow")
        table.add_column("Clock", style="green")
        table.add_column("Players", justify="right")
        for t in created[:10]:
            clock = t.get("clock", {})
            clock_str = f"{clock.get('limit', 0) // 60}+{clock.get('increment', 0)}"
            table.add_row(
                t.get("fullName", t.get("id", "")),
                t.get("variant", {}).get("name", "Standard"),
                clock_str,
                str(t.get("nbPlayers", 0)),
            )
        console.print(table)

    if not started and not created:
        console.print("[dim]No tournaments found.[/dim]")


def render_live_games(games: list[dict]) -> None:
    if not games:
        console.print("[dim]No live games found.[/dim]")
        return

    table = Table(title="Lichess TV — Live Games by Channel", show_lines=True)
    table.add_column("Channel", style="bold cyan")
    table.add_column("White", style="white")
    table.add_column("Black", style="white")
    table.add_column("Game ID", style="dim")

    for g in games:
        players = g.get("players", [])
        white = players[0].get("user", {}).get("name", "?") if len(players) > 0 else "?"
        black = players[1].get("user", {}).get("name", "?") if len(players) > 1 else "?"
        table.add_row(
            g.get("channel", ""),
            white,
            black,
            g.get("gameId", ""),
        )

    console.print(table)


def render_broadcasts(data: dict) -> None:
    rounds = data if isinstance(data, list) else data.get("currentRound", [])

    if not rounds:
        console.print("[dim]No active broadcasts.[/dim]")
        return

    table = Table(title="Lichess Broadcasts", show_lines=True)
    table.add_column("Name", style="bold cyan")
    table.add_column("Slug / ID", style="dim")

    items = rounds if isinstance(rounds, list) else [rounds]
    for b in items[:20]:
        tour = b.get("tour", b)
        table.add_row(
            tour.get("name", ""),
            tour.get("slug", tour.get("id", "")),
        )

    console.print(table)


def render_player(profile: dict, games: list[dict]) -> None:
    username = profile.get("username", "")
    perfs = profile.get("perfs", {})
    title = profile.get("title", "")
    display_name = f"{title} {username}".strip() if title else username

    lines = []
    for variant, info in perfs.items():
        if "rating" in info:
            lines.append(f"  [cyan]{variant:<12}[/cyan] {info['rating']} ({info.get('games', 0)} games)")

    ratings_text = "\n".join(lines) if lines else "  [dim]No rated games.[/dim]"
    panel_content = f"[bold]{display_name}[/bold]\n\n{ratings_text}"
    console.print(Panel(panel_content, title="Player Profile", border_style="cyan"))

    if games:
        table = Table(title="Recent Games", show_lines=True)
        table.add_column("Speed", style="yellow")
        table.add_column("White", style="white")
        table.add_column("Black", style="white")
        table.add_column("Result", justify="center")
        table.add_column("Moves", justify="right", style="dim")

        for g in games:
            players = g.get("players", {})
            white_user = players.get("white", {}).get("user", {}).get("name", "?")
            black_user = players.get("black", {}).get("user", {}).get("name", "?")
            winner = g.get("winner", "")
            if winner == "white":
                result = "1-0"
            elif winner == "black":
                result = "0-1"
            else:
                result = "½-½"
            table.add_row(
                g.get("speed", ""),
                white_user,
                black_user,
                result,
                str(g.get("moves", "").count(" ") + 1) if g.get("moves") else "?",
            )
        console.print(table)
