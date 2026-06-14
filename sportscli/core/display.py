from contextlib import contextmanager

from rich.console import Console
from rich.prompt import IntPrompt

console = Console()


def print_error(msg: str) -> None:
    console.print(f"[bold red]Error:[/bold red] {msg}")


def print_warning(msg: str) -> None:
    console.print(f"[bold yellow]Warning:[/bold yellow] {msg}")


def print_success(msg: str) -> None:
    console.print(f"[bold green]✓[/bold green] {msg}")


@contextmanager
def status_spinner(msg: str):
    with console.status(f"[bold cyan]{msg}[/bold cyan]"):
        yield


def select_from_menu(title: str, options: list[tuple[str, str]]) -> int:
    """Display a numbered menu and return the 1-based selection."""
    console.print()
    console.print(f"[bold cyan]{title}[/bold cyan]")
    for i, (name, desc) in enumerate(options, 1):
        console.print(f"  [bold cyan][{i}][/bold cyan]  [bold]{name:<14}[/bold] [dim]{desc}[/dim]")
    console.print()
    return IntPrompt.ask(
        "Choose",
        choices=[str(i) for i in range(1, len(options) + 1)],
        show_choices=False,
    )
