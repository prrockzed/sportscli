from contextlib import contextmanager

from rich.console import Console

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
