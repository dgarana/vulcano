"""Data models used to represent registered Vulcano commands."""

# System imports
import inspect
from collections.abc import Callable
from typing import Any

from cached_property import cached_property

# Third-party imports
from pynspector.func_inspections import get_func_inspect_result
from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Local imports
from .docutils import multi_doc_parser

__all__ = ["Command"]


class Command(object):
    """Representation of a single registered command.

    Args:
        func (callable): Function to execute.
        name (str | None): Optional command name override.
        description (str | None): Optional short description override.
        show_if (bool | callable): Visibility rule for help/completion.
        arg_opts (dict | None): Mapping of argument name to a list of
            predefined values offered as autocomplete options, or a
            callable that receives a dict of already-filled parameter
            values and returns a list of options dynamically.
    """

    def __init__(
        self,
        func: Callable[..., Any],
        name: str | None = None,
        description: str | None = None,
        show_if: bool | Callable[[], bool] = True,
        arg_opts: (
            dict[str, list[str] | Callable[[dict[str, str]], list[str]]] | None
        ) = None,
    ) -> None:
        self.show_if = show_if
        self.func = func
        func_inspect = get_func_inspect_result(func, doc_parser=multi_doc_parser)
        self.name: str = name or func_inspect.name
        self.short_description: str | None = (
            description or func_inspect.short_description
        )
        self.long_description: str | None = func_inspect.long_description
        self.args = func_inspect.arguments
        self.arg_opts: dict[str, list[str] | Callable[[dict[str, str]], list[str]]] = (
            arg_opts or {}
        )

    @property
    def visible(self) -> bool:
        """Return whether the command should appear in UX surfaces."""
        if isinstance(self.show_if, bool):
            return self.show_if
        return self.show_if()

    @property
    def source_code(self) -> str:
        """Return original Python source code for the command function."""
        return inspect.getsource(self.func)

    @property
    def help(self) -> str:
        """Build a printable help string for the command.

        Returns:
            str: Multiline help text with description and arguments.
        """
        description_item = "{}: \t{}".format(self.name, self.short_description)
        if self.long_description:
            description_item += "\n{}".format(self.long_description)
        if self.args:
            description_item += "\n\t 📋  Args:"
            for arg in self.args:
                arg_description = "\n\t\t"
                if arg.is_mandatory:
                    arg_description += "*"
                arg_description += "{arg.name}"
                if arg.kind:
                    arg_description += "({arg.kind})"
                if arg.is_kwarg and arg.default is not None:
                    arg_description += "(default: {arg.default})"
                arg_description += ": {arg.description}"
                description_item += arg_description.format(arg=arg)
        return description_item + "\n"

    @cached_property
    def rich_panel(self) -> Panel:
        """Return a rich Panel with formatted command help.

        Returns:
            Panel: A rich renderable showing description and argument table.
        """
        lines = []

        if self.short_description:
            lines.append(Text(self.short_description, style="bold"))

        if self.long_description:
            lines.append(Text(""))
            lines.append(Text(self.long_description, style="dim"))

        if self.args:
            table = Table(
                show_header=True,
                box=box.SIMPLE,
                padding=(0, 1),
                style="dim",
                header_style="bold cyan",
            )
            table.add_column("Argument", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Default", style="yellow")
            table.add_column("Description")

            for arg in self.args:
                prefix = "\u26a1" if arg.is_mandatory else " "
                arg_name = Text(f"{prefix} {arg.name}")
                if arg.is_mandatory:
                    arg_name.stylize("bold")
                arg_type = Text(arg.kind or "")
                default = Text(
                    str(arg.default) if arg.is_kwarg and arg.default is not None else ""
                )
                description = Text(arg.description or "")
                table.add_row(arg_name, arg_type, default, description)

            lines.append(Text(""))
            lines.append(table)

        from rich.console import Group

        return Panel(
            Group(*lines),
            title=f"\u2699\ufe0f  {self.name}",
            border_style="blue",
            padding=(0, 1),
        )

    @cached_property
    def command_completer(self) -> tuple[str, str]:
        """Return tuple used by prompt_toolkit for command completion."""
        return ("{}".format(self.name), "{}".format(self.short_description or ""))

    def get_arg_value_completions(
        self, arg_name: str, filled_params: dict[str, str] | None = None
    ) -> list[str]:
        """Return value options for the given argument name.

        When the registered option is a callable, it is invoked with a
        dictionary of already-filled parameter values so that the
        available choices can depend on prior user input.

        Args:
            arg_name (str): Name of the argument to look up.
            filled_params (dict | None): Already-filled argument values
                from the current input line.  Passed to callable options.

        Returns:
            list: Option values, or an empty list if none defined.
        """
        opts = self.arg_opts.get(arg_name, [])
        if callable(opts):
            try:
                return opts(filled_params or {})
            except Exception:
                return []
        return opts

    @cached_property
    def args_completion(self) -> list[tuple[str, str]]:
        """Return completion metadata for command arguments."""
        result = []
        for arg in self.args:
            description = "{}".format(arg.description)
            options = self.arg_opts.get(arg.name, [])
            if callable(options):
                description = "{} [dynamic options]".format(description)
            elif options:
                opts_hint = "options: {}".format(", ".join(str(o) for o in options))
                description = "{} [{}]".format(description, opts_hint)
            result.append(("{}".format(arg.name), description))
        return result

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the command function.

        Args:
            *args: Positional args passed by parser/dispatcher.
            **kwargs: Keyword args passed by parser/dispatcher.

        Returns:
            Any: Function return value.
        """
        return self.func(*args, **kwargs)
