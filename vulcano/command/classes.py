"""Command manager and registration helpers."""

# System imports
import importlib
from collections import OrderedDict
from functools import partial
from inspect import getmembers, isfunction

# Third-party imports
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer

from vulcano.app.lexer import MonokaiTheme
from vulcano.exceptions import CommandNotFound

# Local imports
from .models import Command

__all__ = ["Magma"]


def get_module_functions(module):
    """Yield public functions defined in a module."""
    return (
        func_obj
        for func_name, func_obj in getmembers(module)
        if not func_name.startswith("_") and isfunction(func_obj)
    )


class Magma(object):
    """Manage command registration, lookup, completion, and execution."""

    def __init__(self):
        self._commands = OrderedDict()  # type: OrderedDict

    @property
    def command_names(self):
        """Return registered command names as strings."""
        return ["{}".format(command) for command in self._commands.keys()]

    @property
    def command_completions(self):
        """Return completion tuples for visible commands."""
        return [
            command.command_completer
            for command in self._commands.values()
            if command.visible
        ]

    def command(
        self, name_or_function=None, description=None, show_if=True, arg_opts=None
    ):
        """Decorator-based command registration entrypoint.

        Args:
            name_or_function (str | callable | None): Command name or decorated
                function.
            description (str | None): Optional command description.
            show_if (bool | callable): Visibility rule.
            arg_opts (dict | None): Mapping of argument name to a list of
                predefined values offered as autocomplete options.

        Returns:
            callable: Decorator or wrapped function.
        """

        def decorator_register(func, name=None):
            """Wrap a function and register it as a command."""
            self.register_command(func, name, description, show_if, arg_opts)

            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return func_wrapper

        if isfunction(name_or_function):
            function = name_or_function
            return decorator_register(function)
        name = name_or_function
        return partial(decorator_register, name=name)

    def module(self, module):
        """Register all public functions from a module as commands."""
        if isinstance(module, str):
            module = importlib.import_module(module)
        for func in get_module_functions(module):
            self.register_command(func)

    def register_command(
        self, func, name=None, description=None, show_if=True, arg_opts=None
    ):
        """Register one function as a command.

        Args:
            func (callable): Function to execute.
            name (str | None): Optional command name override.
            description (str | None): Optional command description.
            show_if (bool | callable): Visibility rule.
            arg_opts (dict | None): Mapping of argument name to a list of
                predefined values offered as autocomplete options.

        Raises:
            NameError: If a command with the same name already exists.
        """
        name = name or func.__name__
        if name in self._commands:
            raise NameError("This command already exists")
        self._commands[name] = Command(func, name, description, show_if, arg_opts)

    def get(self, command_name):
        """Return a registered command by name.

        Args:
            command_name (str): Command name.

        Returns:
            Command: Registered command object.

        Raises:
            CommandNotFound: If command is not registered.
        """
        if command_name not in self._commands:
            raise CommandNotFound("Command {} not found".format(command_name))
        return self._commands[command_name]

    def run(self, command_name, *args, **kwargs):
        """Execute a registered command.

        Args:
            command_name (str): Command name.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Any: Command result, if any.
        """
        if command_name.endswith("?"):
            command = self.get(command_name[:-1])
            print(
                highlight(
                    command.source_code,
                    PythonLexer(),
                    Terminal256Formatter(style=MonokaiTheme),
                )
            )
            return
        command = self.get(command_name)
        return command.run(*args, **kwargs)
