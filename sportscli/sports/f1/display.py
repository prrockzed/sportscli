from rich.panel import Panel
from rich.table import Table

from sportscli.core.display import console

# Map Jolpica round status to display strings
_TYRE = {"soft": "S", "medium": "M", "hard": "H", "intermediate": "I", "wet": "W"}


def render_schedule(data: dict) -> None:
    races = (
        data.get("MRData", {})
        .get("RaceTable", {})
        .get("Races", [])
    )
    if not races:
        console.print("[dim]No schedule data available.[/dim]")
        return

    season = data.get("MRData", {}).get("RaceTable", {}).get("season", "")
    table = Table(title=f"Formula 1 — {season} Season Calendar", show_lines=True)
    table.add_column("Rd", justify="right", style="dim")
    table.add_column("Grand Prix", style="bold cyan")
    table.add_column("Circuit", style="white")
    table.add_column("Location", style="yellow")
    table.add_column("Date", style="green")
    table.add_column("Time (UTC)", style="dim")

    for race in races:
        table.add_row(
            race.get("round", ""),
            race.get("raceName", ""),
            race.get("Circuit", {}).get("circuitName", ""),
            race.get("Circuit", {}).get("Location", {}).get("country", ""),
            race.get("date", ""),
            race.get("time", "—").replace("Z", ""),
        )

    console.print(table)


def render_driver_standings(data: dict) -> None:
    standings_list = (
        data.get("MRData", {})
        .get("StandingsTable", {})
        .get("StandingsLists", [])
    )
    if not standings_list:
        console.print("[dim]No driver standings available.[/dim]")
        return

    entries = standings_list[0].get("DriverStandings", [])
    season = standings_list[0].get("season", "")
    round_no = standings_list[0].get("round", "")

    table = Table(
        title=f"F1 Driver Championship — {season} (after round {round_no})",
        show_lines=True,
    )
    table.add_column("Pos", justify="right", style="dim")
    table.add_column("Driver", style="bold cyan")
    table.add_column("Nationality", style="yellow")
    table.add_column("Team", style="white")
    table.add_column("Wins", justify="right", style="green")
    table.add_column("Points", justify="right", style="bold green")

    for entry in entries:
        driver = entry.get("Driver", {})
        constructs = entry.get("Constructors", [{}])
        name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
        table.add_row(
            entry.get("position", ""),
            name,
            driver.get("nationality", ""),
            constructs[0].get("name", "") if constructs else "",
            entry.get("wins", "0"),
            entry.get("points", "0"),
        )

    console.print(table)


def render_constructor_standings(data: dict) -> None:
    standings_list = (
        data.get("MRData", {})
        .get("StandingsTable", {})
        .get("StandingsLists", [])
    )
    if not standings_list:
        console.print("[dim]No constructor standings available.[/dim]")
        return

    entries = standings_list[0].get("ConstructorStandings", [])
    season = standings_list[0].get("season", "")
    round_no = standings_list[0].get("round", "")

    table = Table(
        title=f"F1 Constructor Championship — {season} (after round {round_no})",
        show_lines=True,
    )
    table.add_column("Pos", justify="right", style="dim")
    table.add_column("Constructor", style="bold cyan")
    table.add_column("Nationality", style="yellow")
    table.add_column("Wins", justify="right", style="green")
    table.add_column("Points", justify="right", style="bold green")

    for entry in entries:
        constructor = entry.get("Constructor", {})
        table.add_row(
            entry.get("position", ""),
            constructor.get("name", ""),
            constructor.get("nationality", ""),
            entry.get("wins", "0"),
            entry.get("points", "0"),
        )

    console.print(table)


def render_race_results(data: dict) -> None:
    races = (
        data.get("MRData", {})
        .get("RaceTable", {})
        .get("Races", [])
    )
    if not races:
        console.print("[dim]No race results available.[/dim]")
        return

    race = races[0]
    race_name = race.get("raceName", "Race")
    race_date = race.get("date", "")
    circuit = race.get("Circuit", {}).get("circuitName", "")
    results = race.get("Results", [])

    console.print(Panel(
        f"[bold]{race_name}[/bold]  [dim]{circuit} — {race_date}[/dim]",
        border_style="cyan",
    ))

    table = Table(show_lines=True)
    table.add_column("Pos", justify="right", style="dim")
    table.add_column("Driver", style="bold cyan")
    table.add_column("Team", style="white")
    table.add_column("Grid", justify="right", style="dim")
    table.add_column("Laps", justify="right")
    table.add_column("Time / Status", style="yellow")
    table.add_column("Pts", justify="right", style="bold green")

    for result in results:
        driver = result.get("Driver", {})
        name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}"
        constructor = result.get("Constructor", {}).get("name", "")
        time_info = result.get("Time", {}).get("time", result.get("status", ""))
        pos = result.get("position", "")
        pos_display = {"1": "🥇 1", "2": "🥈 2", "3": "🥉 3"}.get(pos, pos)
        table.add_row(
            pos_display,
            name,
            constructor,
            result.get("grid", ""),
            result.get("laps", ""),
            time_info,
            result.get("points", "0"),
        )

    console.print(table)


def render_live_session(session: dict, positions: list, drivers: list) -> None:
    session_name = session.get("session_name", "Session")
    session_type = session.get("session_type", "")
    location = session.get("location", "")
    country = session.get("country_name", "")

    console.print(Panel(
        f"[bold]{session_name}[/bold]  [dim]{location}, {country}[/dim]",
        border_style="red",
        subtitle=f"[dim]{session_type}[/dim]",
    ))

    if not positions:
        console.print("[dim]No live position data available.[/dim]")
        return

    # Build driver number → name map
    driver_map = {
        str(d.get("driver_number", "")): d.get("name_acronym", "???")
        for d in drivers
    }
    team_map = {
        str(d.get("driver_number", "")): d.get("team_name", "")
        for d in drivers
    }

    # Latest position per driver (last entry wins)
    latest: dict[str, dict] = {}
    for p in positions:
        num = str(p.get("driver_number", ""))
        latest[num] = p

    sorted_positions = sorted(latest.values(), key=lambda x: x.get("position", 99))

    table = Table(title="Current Positions", show_lines=True)
    table.add_column("Pos", justify="right", style="dim")
    table.add_column("Driver", style="bold cyan")
    table.add_column("Team", style="white")

    for p in sorted_positions:
        num = str(p.get("driver_number", ""))
        pos = str(p.get("position", ""))
        pos_display = {"1": "🥇 1", "2": "🥈 2", "3": "🥉 3"}.get(pos, pos)
        table.add_row(
            pos_display,
            driver_map.get(num, num),
            team_map.get(num, ""),
        )

    console.print(table)
