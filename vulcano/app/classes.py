"""Core application objects and execution flow for Vulcano."""

import os

# System imports
import sys
from difflib import SequenceMatcher

# Third-party imports
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer

from vulcano.command import builtin
from vulcano.command.classes import Magma
from vulcano.command.completer import CommandCompleter
from vulcano.command.parser import inline_parser, split_list_by_arg

# Local imports
from vulcano.exceptions import CommandNotFound, CommandParseError

from .lexer import MonokaiTheme, create_lexer

__all__ = ["VulcanoApp"]


def rq_is_for_repl(app):
    """Return a lazy predicate indicating REPL visibility context."""

    def _func():
        return not app.request_is_for_args

    return _func


def did_you_mean(command, possible_commands):
    """Return best fuzzy-matched command suggestion."""
    suggested_command = None
    ratio = 0
    for possible_command in possible_commands:
        possible_ratio = SequenceMatcher(None, command, possible_command).ratio()
        if possible_ratio > ratio:
            ratio = possible_ratio
            suggested_command = possible_command
    return suggested_command


class VulcanoApp(object):
    """Factory/singleton interface for creating named app instances."""

    __instances__ = {}

    def __new__(cls, app_name="vulcano_default", prompt="🌋  "):
        if app_name in cls.__instances__:
            return cls.__instances__.get(app_name)
        new_app = _VulcanoApp(app_name, prompt)
        cls.__instances__[app_name] = new_app
        return new_app


class _VulcanoApp(object):
    """Concrete app implementation with registration and execution state."""

    def __init__(self, app_name, prompt):
        self.app_name = app_name
        self.manager = Magma()  # type: Magma
        self.context = {}  # Type: dict
        self.print_result = True
        self.theme = None
        self.suggestions = None
        self.prompt = prompt  # Type: string or func

    @property
    def request_is_for_args(self):
        """Return whether execution should run from CLI args.

        Returns:
            bool: ``True`` when at least one CLI argument was provided.
        """
        return len(sys.argv) >= 2

    def command(self, *args, **kwargs):
        """Register a command via decorator in the current app instance."""
        return self.manager.command(*args, **kwargs)

    def module(self, module):
        """Register all public functions from a module.

        Args:
            module (str | module): Import path or imported module object.
        """
        return self.manager.module(module)

    def run(
        self,
        theme=MonokaiTheme,
        print_result=True,
        history_file=None,
        suggestions=did_you_mean,
    ):
        """Run the app in argument mode or interactive REPL mode.

        Args:
            theme (type[VulcanoStyle]): Theme used in REPL mode.
            print_result (bool): Print command return values when truthy.
            history_file (str | Path | None): Optional history file path.
            suggestions (callable | None): Suggestion callback for unknown
                commands.
        """
        self.theme = theme
        self.suggestions = suggestions
        self.print_result = print_result
        self._prepare_builtins()
        if self.request_is_for_args:
            self._exec_from_args()
        else:
            self._exec_from_repl(theme=theme, history_file=history_file)

    def _prepare_builtins(self):
        """Register built-in commands."""
        self.manager.register_command(
            builtin.exit(self), "exit", show_if=rq_is_for_repl(self)
        )
        self.manager.register_command(builtin.help(self), "help")

    @staticmethod
    def _quote_if_spaced(value):
        """Wrap a value in double quotes if it contains spaces.

        Args:
            value (str): Value to potentially quote.

        Returns:
            str: Original value, or double-quoted version when spaces are present.
        """
        if " " in str(value):
            return '"{}"'.format(str(value).replace('"', '\\"'))
        return value

    def _exec_from_args(self):
        """Execute one or more commands provided in CLI argument mode."""
        # Re-quote argv tokens that contain spaces so that multi-word shell
        # arguments (e.g. "Hello world") survive the join→split round-trip.
        quoted_args = [self._quote_if_spaced(a) for a in sys.argv[1:]]
        commands = split_list_by_arg(lst=quoted_args, separator="and")
        for command in commands:
            command_list = command.split()
            command_name = command_list[0]
            arguments = " ".join(command_list[1:])
            try:
                # Quote context values that contain spaces so that a substituted
                # multi-word result is still treated as a single argument.
                safe_context = {
                    k: self._quote_if_spaced(v) for k, v in self.context.items()
                }
                arguments = arguments.format(**safe_context)
            except KeyError:
                pass
            try:
                args, kwargs = inline_parser(arguments)
            except CommandParseError as error:
                print(
                    "🚨  Error parsing arguments for '{}': {}".format(
                        command_name, error
                    )
                )
                raise
            try:
                self._execute_command(command_name, *args, **kwargs)
            except CommandNotFound:
                print("🤔  Command '{}' not found".format(command_name))
                if self.suggestions:
                    possible_command = self.suggestions(
                        command_name, self.manager.command_names
                    )
                    if possible_command:
                        print('💡  Did you mean: "{}"?'.format(possible_command))

    def _exec_from_repl(self, theme=MonokaiTheme, history_file=None):
        """Execute the interactive REPL loop."""
        session_extra_options = {}
        if history_file:
            session_extra_options["history"] = FileHistory(
                os.path.expanduser(str(history_file))
            )
        self.do_repl = True
        manager_completer = FuzzyCompleter(
            CommandCompleter(self.manager, ignore_case=True)
        )
        lexer = create_lexer(commands=self.manager.command_names)
        session = PromptSession(
            completer=manager_completer,
            lexer=PygmentsLexer(lexer),
            style=theme.pygments_style(),
            **session_extra_options,
        )
        while self.do_repl:
            try:
                user_input = "{}".format(session.prompt(self.prompt))
            except KeyboardInterrupt:
                continue  # Control-C pressed. Try again.
            except EOFError:
                break  # Control-D Pressed. Finish

            if not user_input.strip():
                continue
            command = ""
            try:
                commands = split_list_by_arg(lst=[user_input], separator="and")
                for command_str in commands:
                    command_str = command_str.strip()
                    if not command_str:
                        continue
                    command_parts = command_str.split()
                    command = command_parts[0]
                    arguments = " ".join(command_parts[1:])
                    try:
                        arguments = arguments.format(**self.context)
                    except KeyError:
                        pass
                    args, kwargs = inline_parser(arguments)
                    self._execute_command(command, *args, **kwargs)
            except CommandNotFound:
                print("🤔  Command '{}' not found".format(command))
                if self.suggestions:
                    possible_command = self.suggestions(
                        command, self.manager.command_names
                    )
                    if possible_command:
                        print('💡  Did you mean: "{}"?'.format(possible_command))
            except Exception as error:
                print("💥  Error executing '{}': {}".format(command, error))

    def _execute_command(self, command_name, *args, **kwargs):
        """Execute a command and persist result in shared context."""
        self.context["last_result"] = self.manager.run(command_name, *args, **kwargs)
        if self.print_result and self.context["last_result"]:
            print(self.context["last_result"])
        return self.context["last_result"]
