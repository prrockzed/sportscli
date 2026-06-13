from rich.table import Table

from sportscli.core.display import console


def render_live_matches(data: dict) -> None:
    matches = data.get("matches", [])
    if not matches:
        console.print("[dim]No live football matches at the moment.[/dim]")
        return

    table = Table(title="Live Football Matches", show_lines=True)
    table.add_column("Competition", style="bold cyan")
    table.add_column("Home", style="white")
    table.add_column("Score", justify="center", style="bold green")
    table.add_column("Away", style="white")
    table.add_column("Minute", justify="right", style="yellow")

    for m in matches:
        comp = m.get("competition", {}).get("name", "")
        home = m.get("homeTeam", {}).get("shortName", m.get("homeTeam", {}).get("name", ""))
        away = m.get("awayTeam", {}).get("shortName", m.get("awayTeam", {}).get("name", ""))
        score = m.get("score", {})
        full = score.get("fullTime", {})
        h_score = full.get("home", "-")
        a_score = full.get("away", "-")
        score_str = f"{h_score} - {a_score}"
        minute = str(m.get("minute", "")) or "—"
        table.add_row(comp, home, score_str, away, minute)

    console.print(table)


def render_standings(data: dict) -> None:
    standings_list = data.get("standings", [])
    competition = data.get("competition", {}).get("name", "Standings")

    for standing in standings_list:
        stage = standing.get("stage", "")
        group = standing.get("group", "")
        heading = competition
        if group:
            heading = f"{competition} — {group}"

        table = Table(title=heading, show_lines=True)
        table.add_column("Pos", justify="right", style="dim")
        table.add_column("Team", style="bold cyan")
        table.add_column("P", justify="right")
        table.add_column("W", justify="right", style="green")
        table.add_column("D", justify="right", style="yellow")
        table.add_column("L", justify="right", style="red")
        table.add_column("GF", justify="right")
        table.add_column("GA", justify="right")
        table.add_column("GD", justify="right")
        table.add_column("Pts", justify="right", style="bold green")

        for row in standing.get("table", []):
            table.add_row(
                str(row.get("position", "")),
                row.get("team", {}).get("shortName", row.get("team", {}).get("name", "")),
                str(row.get("playedGames", "")),
                str(row.get("won", "")),
                str(row.get("draw", "")),
                str(row.get("lost", "")),
                str(row.get("goalsFor", "")),
                str(row.get("goalsAgainst", "")),
                str(row.get("goalDifference", "")),
                str(row.get("points", "")),
            )

        console.print(table)


def render_fixtures(data: dict) -> None:
    matches = data.get("matches", [])
    competition = data.get("competition", {}).get("name", "Fixtures")

    if not matches:
        console.print("[dim]No upcoming fixtures found.[/dim]")
        return

    table = Table(title=f"{competition} — Upcoming Fixtures", show_lines=True)
    table.add_column("Date", style="green")
    table.add_column("Home", style="bold cyan")
    table.add_column("Away", style="bold cyan")
    table.add_column("Matchday", justify="right", style="dim")

    for m in matches[:20]:
        utc_date = m.get("utcDate", "")[:10]
        home = m.get("homeTeam", {}).get("shortName", m.get("homeTeam", {}).get("name", ""))
        away = m.get("awayTeam", {}).get("shortName", m.get("awayTeam", {}).get("name", ""))
        matchday = str(m.get("matchday", ""))
        table.add_row(utc_date, home, away, matchday)

    console.print(table)
