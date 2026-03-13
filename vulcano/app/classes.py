"""Core application objects and execution flow for Vulcano."""

from __future__ import annotations

import os

# System imports
import sys
from collections.abc import Callable
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

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


def rq_is_for_repl(app: _VulcanoApp) -> Callable[[], bool]:
    """Return a lazy predicate indicating REPL visibility context."""

    def _func() -> bool:
        return not app.request_is_for_args

    return _func


def did_you_mean(command: str, possible_commands: list[str]) -> str | None:
    """Return best fuzzy-matched command suggestion."""
    suggested_command: str | None = None
    ratio: float = 0
    for possible_command in possible_commands:
        possible_ratio = SequenceMatcher(None, command, possible_command).ratio()
        if possible_ratio > ratio:
            ratio = possible_ratio
            suggested_command = possible_command
    return suggested_command


class VulcanoApp(object):
    """Factory/singleton interface for creating named app instances."""

    __instances__ = {}

    def __new__(
        cls, app_name: str = "vulcano_default", prompt: str = "🌋  "
    ) -> _VulcanoApp:
        if app_name in cls.__instances__:
            return cls.__instances__.get(app_name)
        new_app = _VulcanoApp(app_name, prompt)
        cls.__instances__[app_name] = new_app
        return new_app


class _VulcanoApp(object):
    """Concrete app implementation with registration and execution state."""

    def __init__(self, app_name: str, prompt: str) -> None:
        self.app_name: str = app_name
        self.manager: Magma = Magma()
        self.context: dict[str, Any] = {}
        self.print_result: bool = True
        self.theme: Any = None
        self.suggestions: Callable[[str, list[str]], str | None] | None = None
        self.prompt: str = prompt
        # Flat registry of all CommandGroup objects keyed by their full
        # dot-path (e.g. {"text": grp, "text.formal": formal_grp}).
        self._groups: dict[str, Any] = {}

    @property
    def request_is_for_args(self) -> bool:
        """Return whether execution should run from CLI args.

        Returns:
            bool: ``True`` when at least one CLI argument was provided.
        """
        return len(sys.argv) >= 2

    def command(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """Register a command via decorator in the current app instance."""
        return self.manager.command(*args, **kwargs)

    def group(self, name: str, description: str | None = None) -> Any:
        """Create and register a named command group.

        Returns a :class:`CommandGroup` whose ``.command()`` decorator
        registers commands inside the group's isolated sub-REPL.
        Typing the group name in the main REPL enters the sub-REPL;
        ``exit`` returns to the parent session.

        Args:
            name (str): Group name — what the user types to enter it.
            description (str | None): Short description shown in help.

        Returns:
            CommandGroup: New group to use as a command decorator factory.
        """
        from .group import CommandGroup

        grp = CommandGroup(name, description, self)
        self._groups[name] = grp

        def _enter_group():
            grp()

        _enter_group.__doc__ = description or "Enter the {} command group.".format(name)
        self.manager.register_command(_enter_group, name, description)
        return grp

    @property
    def _flat_commands(self) -> dict[str, Any]:
        """Return ``{dot.path: Command}`` for every command in every group.

        Includes commands in nested sub-groups, e.g. ``"text.formal.dear"``.
        Built-ins (``exit``, ``help``) are excluded.
        """
        result = {}
        for group_path, group in self._groups.items():
            for cmd_name, cmd in group.manager._commands.items():
                if cmd_name not in ("exit", "help"):
                    result["{}.{}".format(group_path, cmd_name)] = cmd
        return result

    def _resolve_dot_command(self, command_name: str) -> tuple[Magma, str]:
        """Resolve ``group.subgroup.command`` to ``(manager, simple_name)``.

        Returns the root manager unchanged when the path cannot be resolved
        (the subsequent ``manager.run`` will raise ``CommandNotFound``).
        """
        parts = command_name.split(".")
        group_path = ".".join(parts[:-1])
        simple_name = parts[-1]
        if group_path in self._groups:
            return self._groups[group_path].manager, simple_name
        return self.manager, command_name

    def module(self, module: str | Any) -> None:
        """Register all public functions from a module.

        Args:
            module (str | module): Import path or imported module object.
        """
        return self.manager.module(module)

    def run(
        self,
        theme: Any = MonokaiTheme,
        print_result: bool = True,
        history_file: str | Path | None = None,
        suggestions: Callable[[str, list[str]], str | None] | None = did_you_mean,
    ) -> None:
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

    def _prepare_builtins(self) -> None:
        """Register built-in commands."""
        self.manager.register_command(
            builtin.exit(self), "exit", show_if=rq_is_for_repl(self)
        )
        self.manager.register_command(builtin.help(self), "help")

    @staticmethod
    def _quote_if_spaced(value: Any) -> str:
        """Wrap a value in double quotes if it contains spaces.

        Args:
            value (str): Value to potentially quote.

        Returns:
            str: Original value, or double-quoted version when spaces are present.
        """
        if " " in str(value):
            return '"{}"'.format(str(value).replace('"', '\\"'))
        return value

    def _exec_from_args(self) -> None:
        """Execute one or more commands provided in CLI argument mode."""
        # Re-quote argv tokens that contain spaces so that multi-word shell
        # arguments (e.g. "Hello world") survive the join→split round-trip.
        quoted_args = [self._quote_if_spaced(a) for a in sys.argv[1:]]
        commands = split_list_by_arg(lst=quoted_args, separator="and")
        flat_cmds = self._flat_commands
        all_names = self.manager.command_names + list(flat_cmds.keys())
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
                    possible_command = self.suggestions(command_name, all_names)
                    if possible_command:
                        print('💡  Did you mean: "{}"?'.format(possible_command))

    def _exec_from_repl(
        self, theme: Any = MonokaiTheme, history_file: str | Path | None = None
    ) -> None:
        """Execute the interactive REPL loop."""
        session_extra_options = {}
        if history_file:
            session_extra_options["history"] = FileHistory(
                os.path.expanduser(str(history_file))
            )
        self.do_repl = True
        flat_cmds = self._flat_commands
        all_names = self.manager.command_names + list(flat_cmds.keys())
        manager_completer = FuzzyCompleter(
            CommandCompleter(self.manager, ignore_case=True, flat_commands=flat_cmds)
        )
        lexer = create_lexer(commands=all_names)
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
                    possible_command = self.suggestions(command, all_names)
                    if possible_command:
                        print('💡  Did you mean: "{}"?'.format(possible_command))
            except Exception as error:
                print("💥  Error executing '{}': {}".format(command, error))

    def _execute_command(self, command_name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a command and persist result in shared context.

        Supports dot-path commands like ``text.formal.dear`` by resolving
        the group segment against ``self._groups``.
        """
        base_name = command_name.rstrip("?")
        if "." in base_name:
            manager, simple_name = self._resolve_dot_command(base_name)
            if command_name.endswith("?"):
                simple_name += "?"
        else:
            manager, simple_name = self.manager, command_name
        self.context["last_result"] = manager.run(simple_name, *args, **kwargs)
        if self.print_result and self.context["last_result"]:
            print(self.context["last_result"])
        return self.context["last_result"]
