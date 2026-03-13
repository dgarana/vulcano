"""Built-in commands automatically registered by Vulcano."""

# System imports
from collections.abc import Callable
from typing import Any

# Third-party imports
from rich import box
from rich.console import Console
from rich.table import Table

# Local imports

console = Console()

__all__ = ["help", "exit"]


def help(app: Any) -> Callable[..., None]:
    """Create the built-in `help` command bound to an app instance.

    Args:
        app (_VulcanoApp): Current app instance.

    Returns:
        callable: Command function printing global or per-command help.
    """

    def real_help(command: str | None = None) -> None:
        """Print global help or details for a specific command.

        Args:
            command (str | None): Optional command name.
        """
        if command:
            cmd_obj = app.manager._commands.get(command)
            if cmd_obj:
                console.print(cmd_obj.rich_panel)
            else:
                console.print("🤔  Command '{}' not found".format(command))
        else:
            table = Table(
                title="📖  Available Commands",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan",
                border_style="blue",
            )
            table.add_column("Command", style="cyan bold", no_wrap=True)
            table.add_column("Description")
            for cmd in app.manager._commands.values():
                if cmd.visible:
                    table.add_row(
                        cmd.name,
                        cmd.short_description or "",
                    )
            console.print(table)

    return real_help


def exit(app: Any) -> Callable[[], None]:
    """Create the built-in `exit` command bound to an app instance.

    Args:
        app (_VulcanoApp): Current app instance.

    Returns:
        callable: Command function that stops the REPL loop.
    """

    def _exit() -> None:
        """Exit the interactive REPL session."""
        console.print("👋  See you soon!")
        app.do_repl = False

    return _exit
