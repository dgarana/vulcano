"""Data models used to represent registered Vulcano commands."""

# System imports
import inspect

from cached_property import cached_property

# Third-party imports
from pynspector.func_inspections import get_func_inspect_result

# Local imports


__all__ = ["Command"]


class Command(object):
    """Representation of a single registered command.

    Args:
        func (callable): Function to execute.
        name (str | None): Optional command name override.
        description (str | None): Optional short description override.
        show_if (bool | callable): Visibility rule for help/completion.
    """

    def __init__(self, func, name=None, description=None, show_if=True):
        self.show_if = show_if
        self.func = func  # type: callable
        func_inspect = get_func_inspect_result(func)
        self.name = name or func_inspect.name  # type: str
        self.short_description = description or func_inspect.short_description
        self.long_description = func_inspect.long_description
        self.args = func_inspect.arguments

    @property
    def visible(self):
        """Return whether the command should appear in UX surfaces."""
        if isinstance(self.show_if, bool):
            return self.show_if
        return self.show_if()

    @property
    def source_code(self):
        """Return original Python source code for the command function."""
        return inspect.getsource(self.func)

    @property
    def help(self):
        """Build a printable help string for the command.

        Returns:
            str: Multiline help text with description and arguments.
        """
        description_item = "{}: \t{}".format(self.name, self.short_description)
        if self.long_description:
            description_item += "\n{}".format(self.long_description)
        if self.args:
            description_item += "\n\t Args:"
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
    def command_completer(self):
        """Return tuple used by prompt_toolkit for command completion."""
        return ("{}".format(self.name), "{}".format(self.short_description or ""))

    @cached_property
    def args_completion(self):
        """Return completion metadata for command arguments."""
        return [
            ("{}".format(arg.name), "{}".format(arg.description)) for arg in self.args
        ]

    def run(self, *args, **kwargs):
        """Execute the command function.

        Args:
            *args: Positional args passed by parser/dispatcher.
            **kwargs: Keyword args passed by parser/dispatcher.

        Returns:
            Any: Function return value.
        """
        return self.func(*args, **kwargs)
