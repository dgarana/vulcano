"""Command group support for nested sub-REPL contexts."""

from __future__ import annotations

# System imports
from collections.abc import Callable
from typing import Any

# Third-party imports
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyCompleter
from prompt_toolkit.lexers import PygmentsLexer

from vulcano.command import builtin
from vulcano.command.classes import Magma
from vulcano.command.completer import CommandCompleter
from vulcano.command.parser import inline_parser, split_list_by_arg
from vulcano.exceptions import CommandNotFound

# Local imports
from .lexer import create_lexer

__all__ = ["CommandGroup"]


class CommandGroup:
    """A named group of commands that opens a nested sub-REPL when invoked.

    Create groups via :meth:`VulcanoApp.group` rather than instantiating
    this class directly::

        text = app.group("text", "Text-related commands")

        @text.command("hi", "Greet someone")
        def say_hi(name):
            print("Hi", name)

        @text.command("greet", "Greet by role", arg_opts={"role": ["admin", "user"]})
        def greet(name, role="user"):
            return "Hello, {} {}!".format(role.capitalize(), name)

    Typing the group name in the REPL enters a nested session limited to
    that group's commands. Type ``exit`` to return to the parent session.
    All features available in the main REPL — ``and``-chaining, context
    templating, ``arg_opts`` autocomplete — work inside a group too.
    """

    def __init__(
        self,
        name: str,
        description: str | None,
        parent_app: Any,
        prompt: str | None = None,
        path: str | None = None,
    ) -> None:
        self.name: str = name
        self.description: str | None = description
        # Always store a reference to the root _VulcanoApp so nested groups
        # share the same theme, context, suggestions, and print_result.
        self._app = (
            parent_app._app if isinstance(parent_app, CommandGroup) else parent_app
        )
        # Full prompt string (e.g. "\U0001f30b  text > subtopic > ").
        # None means compute lazily from the root app's prompt in __call__.
        self._prompt: str | None = prompt
        # Dot-path from root, e.g. "text" or "text.formal".  Used for
        # resolving relative dot-path commands inside this group's sub-REPL.
        self._path: str = path or name
        self.manager: Magma = Magma()
        self.do_repl: bool = False

        def _exit_group() -> None:
            """Exit this command group and return to the parent."""
            self.do_repl = False

        self.manager.register_command(_exit_group, "exit")
        self.manager.register_command(builtin.help(self), "help")

    def command(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """Register a command within this group.

        Accepts the same arguments as :meth:`VulcanoApp.command`,
        including ``arg_opts``.
        """
        return self.manager.command(*args, **kwargs)

    def _build_prompt(self) -> str:
        """Return the full prompt string for this group's sub-REPL."""
        if self._prompt is not None:
            return self._prompt
        base = self._app.prompt if isinstance(self._app.prompt, str) else "🌋  "
        return "{}{} > ".format(base, self.name)

    def group(self, name: str, description: str | None = None) -> CommandGroup:
        """Create and register a nested command group within this group.

        The resulting sub-REPL prompt chains all ancestor names so the
        nesting depth is always visible, e.g. ``🌋  text > subtopic > ``.

        Args:
            name (str): Sub-group name — what the user types to enter it.
            description (str | None): Short description shown in help.

        Returns:
            CommandGroup: New nested group to use as a decorator factory.
        """
        child_path = "{}.{}".format(self._path, name)
        child_prompt = "{}{} > ".format(self._build_prompt(), name)
        child = CommandGroup(
            name, description, self._app, prompt=child_prompt, path=child_path
        )
        # Register in the root app's flat group registry so dot-path
        # commands can be resolved from anywhere.
        self._app._groups[child_path] = child

        def _enter_child():
            child()

        _enter_child.__doc__ = description or "Enter the {} command group.".format(name)
        self.manager.register_command(_enter_child, name, description)
        return child

    @property
    def _flat_commands(self) -> dict[str, Any]:
        """Return ``{relative.path: Command}`` for all sub-group commands.

        Paths are relative to this group — e.g. inside the ``text`` group,
        a nested ``formal.dear`` command is returned as ``"formal.dear"``.
        """
        result = {}
        my_prefix = self._path + "."
        for full_path, group in self._app._groups.items():
            if not full_path.startswith(my_prefix):
                continue
            rel_path = full_path[len(my_prefix) :]
            for cmd_name, cmd in group.manager._commands.items():
                if cmd_name not in ("exit", "help"):
                    result["{}.{}".format(rel_path, cmd_name)] = cmd
        return result

    def _resolve_dot_command(self, command_name: str) -> tuple[Magma, str]:
        """Resolve a relative dot-path (e.g. ``formal.dear``) to ``(manager, name)``.

        The group segment is resolved against this group's path in the root
        app's ``_groups`` registry.
        """
        parts = command_name.split(".")
        group_rel = ".".join(parts[:-1])
        simple_name = parts[-1]
        full_group_path = "{}.{}".format(self._path, group_rel)
        if full_group_path in self._app._groups:
            return self._app._groups[full_group_path].manager, simple_name
        return self.manager, command_name  # will raise CommandNotFound

    def __call__(self) -> None:
        """Enter the nested sub-REPL for this command group."""
        self.do_repl = True
        group_prompt = self._build_prompt()
        flat_cmds = self._flat_commands
        all_names = self.manager.command_names + list(flat_cmds.keys())
        lexer = create_lexer(commands=all_names)
        group_completer = FuzzyCompleter(
            CommandCompleter(self.manager, ignore_case=True, flat_commands=flat_cmds)
        )
        session = PromptSession(
            completer=group_completer,
            lexer=PygmentsLexer(lexer),
            style=self._app.theme.pygments_style(),
        )

        while self.do_repl:
            try:
                user_input = "{}".format(session.prompt(group_prompt))
            except KeyboardInterrupt:
                continue  # Ctrl-C — stay in group
            except EOFError:
                break  # Ctrl-D — leave group

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
                        arguments = arguments.format(**self._app.context)
                    except KeyError:
                        pass
                    args_list, kwargs = inline_parser(arguments)
                    base_cmd = command.rstrip("?")
                    if "." in base_cmd:
                        exec_mgr, exec_name = self._resolve_dot_command(base_cmd)
                        if command.endswith("?"):
                            exec_name += "?"
                    else:
                        exec_mgr, exec_name = self.manager, command
                    result = exec_mgr.run(exec_name, *args_list, **kwargs)
                    self._app.context["last_result"] = result
                    if self._app.print_result and result:
                        print(result)
            except CommandNotFound:
                print("🤔  Command '{}' not found".format(command))
                if self._app.suggestions:
                    possible_command = self._app.suggestions(
                        command, self.manager.command_names
                    )
                    if possible_command:
                        print('💡  Did you mean: "{}"?'.format(possible_command))
            except Exception as error:
                print("💥  Error executing '{}': {}".format(command, error))
