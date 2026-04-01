# -* coding: utf-8 *-
import unittest
from unittest.mock import MagicMock, patch

from vulcano.app.classes import VulcanoApp
from vulcano.app.lexer import MonokaiTheme

print_builtin = "builtins.print"


class TestCommandGroup(unittest.TestCase):
    def setUp(self):
        VulcanoApp.__instances__ = {}
        self.app = VulcanoApp()
        # Set attributes that __call__ reads from the root app.
        self.app.theme = MonokaiTheme
        self.app.print_result = False
        self.app.suggestions = None

    def tearDown(self):
        VulcanoApp.__instances__ = {}

    # ------------------------------------------------------------------
    # _build_prompt
    # ------------------------------------------------------------------

    def test_build_prompt_returns_stored_prompt(self):
        """When _prompt is already set, _build_prompt returns it unchanged."""
        grp = self.app.group("grp")
        grp._prompt = "custom > "
        self.assertEqual(grp._build_prompt(), "custom > ")

    # ------------------------------------------------------------------
    # _flat_commands
    # ------------------------------------------------------------------

    def test_flat_commands_includes_sub_group_commands(self):
        """_flat_commands yields relative-path entries for nested groups."""
        grp = self.app.group("grp", "G")
        sub = grp.group("sub", "S")

        @sub.command("cmd")
        def cmd():
            pass  # pragma: no cover

        flat = grp._flat_commands
        self.assertIn("sub.cmd", flat)

    # ------------------------------------------------------------------
    # _resolve_dot_command
    # ------------------------------------------------------------------

    def test_resolve_dot_command_found(self):
        """A valid relative path resolves to the correct manager and name."""
        grp = self.app.group("grp", "G")
        sub = grp.group("sub", "S")

        @sub.command("cmd")
        def cmd():
            pass  # pragma: no cover

        manager, name = grp._resolve_dot_command("sub.cmd")
        self.assertEqual(name, "cmd")
        self.assertIs(manager, sub.manager)

    def test_resolve_dot_command_falls_back_for_unknown_path(self):
        """An unknown path falls back to the group's own manager."""
        grp = self.app.group("grp", "G")
        manager, name = grp._resolve_dot_command("nonexistent.cmd")
        self.assertIs(manager, grp.manager)
        self.assertEqual(name, "nonexistent.cmd")

    # ------------------------------------------------------------------
    # __call__  (group sub-REPL)
    # ------------------------------------------------------------------

    @patch("vulcano.app.group.PromptSession")
    def test_call_executes_command(self, PromptSessionMock):
        """__call__ runs the group sub-REPL and executes a typed command."""
        PromptSessionMock.return_value.prompt.side_effect = ("my_cmd", EOFError)
        grp = self.app.group("grp")
        executed = MagicMock()

        @grp.command("my_cmd")
        def my_cmd():
            executed()

        grp()
        executed.assert_called_once()

    @patch("vulcano.app.group.PromptSession")
    def test_call_exit_stops_repl(self, PromptSessionMock):
        """Typing 'exit' in the group REPL stops the loop."""
        PromptSessionMock.return_value.prompt.side_effect = ("exit", EOFError)
        grp = self.app.group("grp")
        grp()  # should return without raising

    @patch("vulcano.app.group.PromptSession")
    def test_call_keyboard_interrupt_continues(self, PromptSessionMock):
        """KeyboardInterrupt (Ctrl-C) in the group REPL is swallowed."""
        PromptSessionMock.return_value.prompt.side_effect = (
            KeyboardInterrupt,
            EOFError,
        )
        grp = self.app.group("grp")
        grp()  # should not raise

    @patch("vulcano.app.group.PromptSession")
    def test_call_empty_input_is_skipped(self, PromptSessionMock):
        """Empty input in the group REPL loops back without executing anything."""
        PromptSessionMock.return_value.prompt.side_effect = ("", EOFError)
        grp = self.app.group("grp")
        grp()  # should not raise

    @patch(print_builtin)
    @patch("vulcano.app.group.PromptSession")
    def test_call_command_not_found_prints_error(self, PromptSessionMock, print_mock):
        """An unknown command prints a 'not found' message."""
        PromptSessionMock.return_value.prompt.side_effect = ("no_such_cmd", EOFError)
        grp = self.app.group("grp")
        grp()
        printed = " ".join(str(c) for c in print_mock.call_args_list)
        self.assertIn("no_such_cmd", printed)

    @patch(print_builtin)
    @patch("vulcano.app.group.PromptSession")
    def test_call_exception_is_caught_and_printed(self, PromptSessionMock, print_mock):
        """Exceptions raised by a command are caught and printed."""
        PromptSessionMock.return_value.prompt.side_effect = ("boom", EOFError)
        grp = self.app.group("grp")

        @grp.command("boom")
        def boom():
            raise RuntimeError("kaboom")

        grp()
        printed = " ".join(str(c) for c in print_mock.call_args_list)
        self.assertIn("kaboom", printed)

    @patch("vulcano.app.group.PromptSession")
    def test_call_stores_result_in_app_context(self, PromptSessionMock):
        """Command return values are stored in the root app's context."""
        PromptSessionMock.return_value.prompt.side_effect = ("my_cmd", EOFError)
        grp = self.app.group("grp")

        @grp.command("my_cmd")
        def my_cmd():
            return 42

        self.app.print_result = True
        grp()
        self.assertEqual(self.app.context["last_result"], 42)

    @patch("vulcano.app.group.PromptSession")
    def test_call_dot_path_command_resolved_in_group_repl(self, PromptSessionMock):
        """Dot-path commands are resolved and executed inside the group sub-REPL."""
        PromptSessionMock.return_value.prompt.side_effect = ("sub.cmd", EOFError)
        grp = self.app.group("grp")
        sub = grp.group("sub")
        executed = MagicMock()

        @sub.command("cmd")
        def cmd():
            executed()

        grp()
        executed.assert_called_once()

    @patch("vulcano.app.group.PromptSession")
    def test_call_empty_part_in_and_chain_is_skipped(self, PromptSessionMock):
        """An empty command part produced by 'cmd and ' is silently skipped."""
        PromptSessionMock.return_value.prompt.side_effect = ("my_cmd and ", EOFError)
        grp = self.app.group("grp")
        executed = MagicMock()

        @grp.command("my_cmd")
        def my_cmd():
            executed()

        grp()
        executed.assert_called_once()

    @patch("vulcano.app.group.PromptSession")
    def test_call_context_templating(self, PromptSessionMock):
        """Context values are substituted into command arguments."""
        self.app.context["item"] = "world"
        PromptSessionMock.return_value.prompt.side_effect = ("greet {item}", EOFError)
        grp = self.app.group("grp")
        received = MagicMock()

        @grp.command("greet")
        def greet(item):
            received(item)

        grp()
        received.assert_called_once_with("world")

    @patch("vulcano.app.group.PromptSession")
    def test_call_context_templating_can_be_disabled(self, PromptSessionMock):
        """Context placeholders remain literal when formatting is disabled."""
        self.app.enable_context_formatting = False
        self.app.context["item"] = "world"
        PromptSessionMock.return_value.prompt.side_effect = ("greet '{item}'", EOFError)
        grp = self.app.group("grp")
        received = MagicMock()

        @grp.command("greet")
        def greet(item):
            received(item)

        grp()
        received.assert_called_once_with("{item}")

    @patch("vulcano.app.group.PromptSession")
    def test_call_enters_nested_child_group(self, PromptSessionMock):
        """Typing a child-group name inside the parent group enters it."""
        # Sequence: parent gets "child" → child gets EOFError (exits child) →
        # parent gets EOFError (exits parent).
        PromptSessionMock.return_value.prompt.side_effect = (
            "child",
            EOFError,
            EOFError,
        )
        grp = self.app.group("grp")
        grp.group("child", "Child group")
        # Should not raise; the child's _enter_child closure calls child()
        grp()
        # PromptSession was instantiated at least twice (parent + child).
        self.assertGreaterEqual(PromptSessionMock.call_count, 2)

    @patch(print_builtin)
    @patch("vulcano.app.group.PromptSession")
    def test_call_context_format_key_error_is_silenced(
        self, PromptSessionMock, print_mock
    ):
        """A missing context key in format args is silently ignored (no exception)."""
        # {missing_key} is not in app.context → KeyError is swallowed;
        # the raw argument string then fails to parse and is swallowed too.
        PromptSessionMock.return_value.prompt.side_effect = (
            "greet {missing_key}",
            EOFError,
        )
        grp = self.app.group("grp")

        @grp.command("greet")
        def greet(arg):
            pass  # pragma: no cover

        grp()  # should not raise

    @patch(print_builtin)
    @patch("vulcano.app.group.PromptSession")
    def test_call_dot_path_source_view_in_group_repl(
        self, PromptSessionMock, print_mock
    ):
        """Typing 'sub.cmd?' inside the group REPL prints command source."""
        PromptSessionMock.return_value.prompt.side_effect = ("sub.cmd?", EOFError)
        grp = self.app.group("grp")
        sub = grp.group("sub")

        @sub.command("cmd")
        def cmd():
            """A sub-command."""
            pass  # pragma: no cover

        grp()
        printed = " ".join(str(c) for c in print_mock.call_args_list)
        self.assertIn("cmd", printed)

    @patch(print_builtin)
    @patch("vulcano.app.group.PromptSession")
    def test_call_suggestions_shown_on_unknown_command(
        self, PromptSessionMock, print_mock
    ):
        """When suggestions is set and returns a match, the hint is printed."""
        PromptSessionMock.return_value.prompt.side_effect = ("unknwon_cmd", EOFError)
        self.app.suggestions = MagicMock(return_value="my_cmd")
        grp = self.app.group("grp")

        @grp.command("my_cmd")
        def my_cmd():
            pass  # pragma: no cover

        grp()
        printed = " ".join(str(c) for c in print_mock.call_args_list)
        self.assertIn("my_cmd", printed)

    @patch("vulcano.app.group.patch_stdout")
    @patch("vulcano.app.group.PromptSession")
    def test_call_uses_patch_stdout_for_background_output(
        self, PromptSessionMock, patch_stdout_mock
    ):
        """Verify patch_stdout is used in group sub-REPL for background output."""
        PromptSessionMock.return_value.prompt.side_effect = ("my_cmd", EOFError)
        grp = self.app.group("grp")
        executed = MagicMock()

        @grp.command("my_cmd")
        def my_cmd():
            executed()

        grp()

        # Verify patch_stdout was called
        patch_stdout_mock.assert_called()
        executed.assert_called_once()
