from rich.panel import Panel
from rich.table import Table

from sportscli.core.display import console


def render_live_matches(data: dict) -> None:
    matches = data.get("data", [])
    if not matches:
        console.print("[dim]No live matches at the moment.[/dim]")
        return

    table = Table(title="Live Cricket Matches", show_lines=True)
    table.add_column("Match", style="bold cyan")
    table.add_column("Teams", style="white")
    table.add_column("Status", style="yellow")
    table.add_column("ID", style="dim")

    for m in matches:
        teams = " vs ".join(m.get("teams", []))
        table.add_row(
            m.get("name", ""),
            teams,
            m.get("status", ""),
            m.get("id", ""),
        )

    console.print(table)


def render_scorecard(data: dict) -> None:
    info = data.get("data", {})
    if not info:
        console.print("[dim]No scorecard data available.[/dim]")
        return

    name = info.get("name", "Match")
    status = info.get("status", "")
    console.print(Panel(f"[bold]{name}[/bold]\n[yellow]{status}[/yellow]", border_style="cyan"))

    scores = info.get("score", [])
    if scores:
        table = Table(title="Innings", show_lines=True)
        table.add_column("Innings", style="bold cyan")
        table.add_column("Runs", justify="right", style="green")
        table.add_column("Wickets", justify="right", style="red")
        table.add_column("Overs", justify="right", style="yellow")
        for s in scores:
            table.add_row(
                s.get("inning", ""),
                str(s.get("r", "")),
                str(s.get("w", "")),
                str(s.get("o", "")),
            )
        console.print(table)

    scorecard = info.get("scorecard", [])
    for innings in scorecard:
        inning_name = innings.get("inning", "Innings")
        batters = innings.get("batting", [])
        if batters:
            bat_table = Table(title=f"{inning_name} — Batting", show_lines=True)
            bat_table.add_column("Batter", style="cyan")
            bat_table.add_column("Dismissal", style="dim")
            bat_table.add_column("R", justify="right", style="bold green")
            bat_table.add_column("B", justify="right")
            bat_table.add_column("4s", justify="right")
            bat_table.add_column("6s", justify="right")
            bat_table.add_column("SR", justify="right", style="yellow")
            for b in batters:
                bat_table.add_row(
                    b.get("batsman", ""),
                    b.get("dismissal-wicket", ""),
                    str(b.get("r", "")),
                    str(b.get("b", "")),
                    str(b.get("4s", "")),
                    str(b.get("6s", "")),
                    str(b.get("sr", "")),
                )
            console.print(bat_table)

        bowlers = innings.get("bowling", [])
        if bowlers:
            bowl_table = Table(title=f"{inning_name} — Bowling", show_lines=True)
            bowl_table.add_column("Bowler", style="cyan")
            bowl_table.add_column("O", justify="right")
            bowl_table.add_column("M", justify="right")
            bowl_table.add_column("R", justify="right", style="red")
            bowl_table.add_column("W", justify="right", style="bold green")
            bowl_table.add_column("Econ", justify="right", style="yellow")
            for bw in bowlers:
                bowl_table.add_row(
                    bw.get("bowler", ""),
                    str(bw.get("o", "")),
                    str(bw.get("m", "")),
                    str(bw.get("r", "")),
                    str(bw.get("w", "")),
                    str(bw.get("eco", "")),
                )
            console.print(bowl_table)


def render_schedule(data: dict) -> None:
    matches = data.get("data", [])
    if not matches:
        console.print("[dim]No upcoming matches found.[/dim]")
        return

    table = Table(title="Upcoming Cricket Matches", show_lines=True)
    table.add_column("Name", style="bold cyan")
    table.add_column("Teams", style="white")
    table.add_column("Date", style="green")
    table.add_column("Venue", style="yellow")
    table.add_column("Status", style="dim")

    for m in matches[:20]:
        teams = " vs ".join(m.get("teams", []))
        table.add_row(
            m.get("name", ""),
            teams,
            m.get("date", ""),
            m.get("venue", ""),
            m.get("status", ""),
        )

    console.print(table)
