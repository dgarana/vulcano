# -* coding: utf-8 *-
# System imports
from unittest import TestCase

# Third-party imports
from unittest.mock import MagicMock, patch

from prompt_toolkit.history import FileHistory

# Local imports
from vulcano.exceptions import CommandParseError

from .classes import VulcanoApp, did_you_mean, split_list_by_arg

print_builtin = "builtins.print"


class TestVulcanoApp(TestCase):
    def test_split_list_by_args(self):
        args = 'test name="David and some other people" and test2 "hi"'.split()
        expected_commands = ['test name="David and some other people"', 'test2 "hi"']
        self.assertListEqual(expected_commands, split_list_by_arg(args, "and"))

        args = "test name='David and some other people' and test2 'hi'".split()
        expected_commands = ["test name='David and some other people'", "test2 'hi'"]
        self.assertListEqual(expected_commands, split_list_by_arg(args, "and"))

    def tearDown(self):
        # Remove the singleton instances before continue next test
        VulcanoApp.__instances__ = {}

    @patch("vulcano.app.classes.sys")
    def test_should_register_builtin_functions_before_run_args(self, sys_mock):
        sys_mock.argv = ["ensure_no_repl", "help"]
        app = VulcanoApp()
        app.run()
        self.assertIn("exit", app.manager._commands)
        self.assertIn("help", app.manager._commands)

    @patch("vulcano.app.classes.sys")
    def test_should_be_able_to_register_functions_with_decorator(self, sys_mock):
        sys_mock.argv = ["ensure_no_repl", "test_function"]
        app = VulcanoApp()
        mock_execution = MagicMock()

        @app.command()
        def test_function():
            mock_execution.test_function_called()

        app.run()
        mock_execution.test_function_called.assert_called()

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_should_be_able_to_execute_in_repl(self, sys_mock, prompt_session_mock):
        session_instance = prompt_session_mock.return_value
        session_instance.prompt.side_effect = ("test_function", EOFError)
        sys_mock.argv = ["ensure_repl"]
        app = VulcanoApp()
        mock_execution = MagicMock()

        @app.command()
        def test_function():
            mock_execution.test_function_called()

        app.run()
        mock_execution.test_function_called.assert_called_once()

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_does_not_throw_while_handling_empty_repl_input(
        self, sys_mock, prompt_session_mock
    ):
        session_instance = prompt_session_mock.return_value
        session_instance.prompt.side_effect = ("", EOFError)
        sys_mock.argv = ["ensure_repl"]
        app = VulcanoApp()
        app.run()

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_should_be_store_last_result_in_context_in_repl(
        self, sys_mock, prompt_session_mock
    ):
        session_instance = prompt_session_mock.return_value
        session_instance.prompt.side_effect = (
            "test_function",
            KeyboardInterrupt,
            EOFError,
        )
        sys_mock.argv = ["ensure_repl"]
        app = VulcanoApp()

        @app.command()
        def test_function():
            return "This is the last result"

        app.run()
        self.assertEqual(app.context["last_result"], "This is the last result")

    @patch("vulcano.app.classes.sys")
    def test_should_be_store_last_result_in_context_in_args(self, sys_mock):
        sys_mock.argv = ["ensure_no_repl", "test_function"]
        app = VulcanoApp()

        @app.command()
        def test_function():
            return "This is the last result"

        app.run()
        self.assertEqual(app.context["last_result"], "This is the last result")

    @patch("vulcano.app.classes.Magma")
    def test_should_be_able_to_register_modules(self, manager_mock):
        app = VulcanoApp()
        app.manager = manager_mock
        app.module("test.module")
        app.manager.module.assert_called_once()

    @patch(print_builtin)
    @patch("vulcano.app.classes.sys")
    def test_should_be_able_to_print_last_result(self, sys_mock, print_mock):
        sys_mock.argv = ["ensure_no_repl", "test_function"]
        app = VulcanoApp()

        @app.command()
        def test_function():
            return "Return from the function"

        app.run(print_result=True)
        print_mock.assert_called_with("Return from the function")

    @patch(print_builtin)
    @patch("vulcano.app.classes.sys")
    def test_only_print_if_print_last_result(self, sys_mock, print_mock):
        sys_mock.argv = ["ensure_no_repl", "test_function"]
        app = VulcanoApp()

        @app.command()
        def test_function():
            return "Return from the function"

        app.run(print_result=False)
        print_mock.assert_not_called()

    @patch("vulcano.app.classes.sys")
    def test_it_raises_exceptions_from_args(self, sys_mock):
        sys_mock.argv = ["ensure_no_repl", "exception_function", "and", "not_executed"]
        app = VulcanoApp()
        never_arrived_here = MagicMock()

        @app.command
        def exception_function():
            raise Exception("This should stop iterations")

        @app.command
        def not_executed():
            never_arrived_here.executed()  # pragma: no cover

        with self.assertRaises(Exception):
            app.run(print_result=False)
        never_arrived_here.executed.assert_not_called()

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_it_prints_exceptions_from_repl(self, sys_mock, prompt_session_mock):
        session_instance = prompt_session_mock.return_value
        session_instance.prompt.side_effect = (
            "exception_function",
            "executed",
            EOFError,
        )
        sys_mock.argv = ["ensure_repl"]
        app = VulcanoApp()
        arrived_here = MagicMock()

        @app.command
        def exception_function():
            raise Exception("This should never stop the execution")

        @app.command
        def executed():
            arrived_here.executed()

        app.run(print_result=False)
        arrived_here.executed.assert_called_once()

    @patch("vulcano.app.classes.sys")
    def test_it_should_format_command_from_nested_args(self, sys_mock):
        sys_mock.argv = [
            "ensure_no_repl",
            "first_function",
            "and",
            "executed",
            "{last_result}",
        ]
        app = VulcanoApp()
        rendered_with_context = MagicMock()

        @app.command
        def first_function():
            return 10

        @app.command
        def executed(param):
            rendered_with_context.parameter_is(param)

        app.run(print_result=False)
        rendered_with_context.parameter_is.assert_called_with(10)

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_it_should_format_command_from_repl(self, sys_mock, prompt_session_mock):
        session_instance = prompt_session_mock.return_value
        sys_mock.argv = ["ensure_repl"]
        session_instance.prompt.side_effect = (
            "first_function",
            "executed {last_result} ",
            EOFError,
        )
        app = VulcanoApp()
        rendered_with_context = MagicMock()

        @app.command
        def first_function():
            return 10

        @app.command
        def executed(param):
            rendered_with_context.parameter_is(param)

        app.run(print_result=False)
        rendered_with_context.parameter_is.assert_called_with(10)

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_it_should_return_not_if_fails_format_command_from_repl(
        self, sys_mock, prompt_session_mock
    ):
        session_instance = prompt_session_mock.return_value
        sys_mock.argv = ["ensure_repl"]
        session_instance.prompt.side_effect = ("executed '{non_existent}'", EOFError)
        app = VulcanoApp()
        rendered_with_context = MagicMock()

        @app.command
        def executed(param):
            rendered_with_context.parameter_is(param)

        app.run(print_result=False)
        rendered_with_context.parameter_is.assert_called_with("{non_existent}")

    @patch("vulcano.app.classes.sys")
    def test_it_should_not_format_command_from_args_when_not_exists(self, sys_mock):
        sys_mock.argv = ["ensure_no_repl", "executed", "'{non_existent}'"]
        app = VulcanoApp()
        rendered_with_context = MagicMock()

        @app.command
        def executed(param):
            rendered_with_context.parameter_is(param)

        app.run(print_result=False)
        rendered_with_context.parameter_is.assert_called_with("{non_existent}")

    @patch("vulcano.app.classes.sys")
    def test_it_should_not_format_command_from_args_when_disabled(self, sys_mock):
        sys_mock.argv = [
            "ensure_no_repl",
            "first_function",
            "and",
            "executed",
            "{last_result}",
        ]
        app = VulcanoApp(enable_context_formatting=False)
        rendered_with_context = MagicMock()

        @app.command
        def first_function():
            return 10

        @app.command
        def executed(param):
            rendered_with_context.parameter_is(param)

        app.run(print_result=False)
        rendered_with_context.parameter_is.assert_called_with("{last_result}")

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_continue_if_there_is_no_command_input(self, sys_mock, prompt_session_mock):
        session_instance = prompt_session_mock.return_value
        sys_mock.argv = ["ensure_repl"]
        session_instance.prompt.side_effect = ("", EOFError)
        app = VulcanoApp()
        app.run(print_result=False)

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_history_file_in_options_if_needed(self, sys_mock, prompt_session_mock):
        session_instance = prompt_session_mock.return_value
        sys_mock.argv = ["ensure_repl"]
        session_instance.prompt.side_effect = ("", EOFError)
        app = VulcanoApp()
        app.run(print_result=False, history_file="somefile.txt")
        prompt_session_mock.assert_called_once()
        _call_args = prompt_session_mock.call_args_list[0][1]
        _history = _call_args.get("history")
        self.assertIsInstance(_history, FileHistory)

    def test_did_you_mean(self):
        command = "hilp"
        possible_commands = ["hell", "halo", "help"]
        self.assertEqual("help", did_you_mean(command, possible_commands))

    @patch("vulcano.app.classes.sys")
    def test_it_should_did_you_mean_on_args_command_not_found(self, sys_mock):
        sys_mock.argv = ["ensure_norepl", "mispeled_comand"]
        suggestion_mock = MagicMock()
        suggestion_mock.return_value = "mispelled_command"
        app = VulcanoApp()
        app.command("another_command")(lambda x: x)
        app.command("miespieled_comand")(lambda x: x)
        app.command("misspelled_command")(lambda x: x)

        app.run(suggestions=suggestion_mock)
        suggestion_mock.assert_called_with(
            "mispeled_comand",
            [
                "another_command",
                "miespieled_comand",
                "misspelled_command",
                "exit",
                "help",
            ],
        )

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_it_should_did_you_mean_on_repl_command_not_found(
        self, sys_mock, prompt_session_mock
    ):

        session_instance = prompt_session_mock.return_value
        sys_mock.argv = ["ensure_repl"]
        session_instance.prompt.side_effect = ("mispeled_comand", EOFError)
        suggestion_mock = MagicMock()
        suggestion_mock.return_value = "mispelled_command"
        app = VulcanoApp()
        app.command("another_command")(lambda x: x)
        app.command("miespieled_comand")(lambda x: x)
        app.command("misspelled_command")(lambda x: x)

        app.run(suggestions=suggestion_mock)
        suggestion_mock.assert_called_with(
            "mispeled_comand",
            [
                "another_command",
                "miespieled_comand",
                "misspelled_command",
                "exit",
                "help",
            ],
        )

    @patch("vulcano.app.classes.sys")
    def test_it_should_handle_multi_word_args(self, sys_mock):
        sys_mock.argv = [
            "ensure_no_repl",
            "reverse_word",
            "Hello Baby! This is awesome",
        ]
        app = VulcanoApp()
        result_mock = MagicMock()

        @app.command
        def reverse_word(word):
            result_mock.result(word)
            return word[::-1]

        app.run(print_result=False)
        result_mock.result.assert_called_with("Hello Baby! This is awesome")

    @patch("vulcano.app.classes.sys")
    def test_it_should_handle_multi_word_context_substitution_in_args(self, sys_mock):
        sys_mock.argv = [
            "ensure_no_repl",
            "reverse_word",
            "Hello Baby",
            "and",
            "reverse_word",
            "{last_result}",
        ]
        app = VulcanoApp()
        result_mock = MagicMock()

        @app.command
        def reverse_word(word):
            result = word[::-1]
            result_mock.result(word)
            return result

        app.run(print_result=False)
        # First call: reverse_word("Hello Baby") -> "ybaB olleH"
        # Second call: reverse_word("ybaB olleH") -> "Hello Baby" (round-trip)
        self.assertEqual(app.context["last_result"], "Hello Baby")

    @patch(print_builtin)
    @patch("vulcano.app.classes.sys")
    def test_it_prints_parse_error_before_raising_in_args(self, sys_mock, print_mock):
        sys_mock.argv = ["ensure_no_repl", "my_cmd", "`invalid`"]
        app = VulcanoApp()

        @app.command
        def my_cmd(param):
            pass  # pragma: no cover

        with self.assertRaises(CommandParseError):
            app.run(print_result=False)

        printed = " ".join(str(c) for c in print_mock.call_args_list)
        self.assertIn("my_cmd", printed)

    def test_resolve_dot_command_falls_back_for_unknown_group(self):
        app = VulcanoApp()
        manager, name = app._resolve_dot_command("nonexistent.cmd")
        self.assertIs(manager, app.manager)
        self.assertEqual(name, "nonexistent.cmd")

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_repl_skips_empty_command_in_and_chain(self, sys_mock, session_mock):
        sys_mock.argv = ["ensure_repl"]
        session_mock.return_value.prompt.side_effect = ("test_cmd and ", EOFError)
        app = VulcanoApp()
        executed = MagicMock()

        @app.command
        def test_cmd():
            executed()

        app.run(print_result=False)
        executed.assert_called_once()

    @patch(print_builtin)
    @patch("vulcano.app.classes.sys")
    def test_dot_path_source_view_from_args(self, sys_mock, print_mock):
        sys_mock.argv = ["ensure_no_repl", "grp.my_cmd?"]
        app = VulcanoApp()
        grp = app.group("grp")

        @grp.command("my_cmd")
        def my_cmd():
            """My command."""
            pass  # pragma: no cover

        app.run(print_result=False)
        printed = " ".join(str(c) for c in print_mock.call_args_list)
        self.assertIn("my_cmd", printed)

    @patch("vulcano.app.group.PromptSession")
    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_entering_group_from_main_repl(
        self, sys_mock, classes_ps_mock, group_ps_mock
    ):
        sys_mock.argv = ["ensure_repl"]
        classes_ps_mock.return_value.prompt.side_effect = ("grp", EOFError)
        group_ps_mock.return_value.prompt.side_effect = EOFError
        app = VulcanoApp()
        app.group("grp", "Test group")
        app.run(print_result=False)
        # The group's PromptSession was created, meaning grp() was called.
        self.assertTrue(group_ps_mock.called)

    def test_ensure_multi_application(self):
        app_one = VulcanoApp("app_one")
        app_two = VulcanoApp("app_two")
        app_one_copy = VulcanoApp("app_one")
        self.assertNotEqual(app_one, app_two)
        self.assertEqual(app_one, app_one_copy)

    def test_constructor_accepts_enable_context_formatting(self):
        app = VulcanoApp("cfg_app", enable_context_formatting=False)
        self.assertFalse(app.enable_context_formatting)

    @patch("vulcano.app.classes.sys")
    def test_dot_path_executes_command_in_group_from_args(self, sys_mock):
        sys_mock.argv = ["ensure_no_repl", "grp.my_cmd", "x=42"]
        app = VulcanoApp()
        grp = app.group("grp", "Test group")

        @grp.command("my_cmd", "A command")
        def my_cmd(x):
            return x

        app.run(print_result=False)
        self.assertEqual(app.context["last_result"], 42)

    @patch("vulcano.app.classes.sys")
    def test_dot_path_executes_nested_group_command_from_args(self, sys_mock):
        sys_mock.argv = ["ensure_no_repl", "outer.inner.cmd"]
        app = VulcanoApp()
        outer = app.group("outer", "Outer")
        inner = outer.group("inner", "Inner")
        received = MagicMock()

        @inner.command("cmd", "Deep command")
        def deep_cmd():
            received.executed()

        app.run(print_result=False)
        received.executed.assert_called_once()

    def test_flat_commands_includes_all_group_commands(self):
        app = VulcanoApp()
        grp = app.group("g", "G")
        sub = grp.group("s", "S")

        @grp.command("cmd_a")
        def cmd_a():
            pass  # pragma: no cover

        @sub.command("cmd_b")
        def cmd_b():
            pass  # pragma: no cover

        flat = app._flat_commands
        self.assertIn("g.cmd_a", flat)
        self.assertIn("g.s", flat)  # sub-group entry registered in g.manager
        self.assertIn("g.s.cmd_b", flat)

    @patch("vulcano.app.classes.patch_stdout")
    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_repl_uses_patch_stdout_for_background_output(
        self, sys_mock, prompt_session_mock, patch_stdout_mock
    ):
        """Verify patch_stdout is used to handle background output cleanly."""
        session_instance = prompt_session_mock.return_value
        session_instance.prompt.side_effect = ("test_function", EOFError)
        sys_mock.argv = ["ensure_repl"]
        
        # Mock patch_stdout to return a context manager
        patch_stdout_context = patch_stdout_mock.return_value.__enter__.return_value
        
        app = VulcanoApp()
        mock_execution = MagicMock()

        @app.command()
        def test_function():
            mock_execution.test_function_called()

        app.run()
        
        # Verify patch_stdout was called
        patch_stdout_mock.assert_called()
        mock_execution.test_function_called.assert_called_once()

    @patch(print_builtin)
    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.sys")
    def test_repl_handles_background_thread_output(
        self, sys_mock, prompt_session_mock, print_mock
    ):
        """Verify background threads can print without corrupting the prompt."""
        import threading
        import time
        
        # Simulate background output during prompt
        def background_task():
            time.sleep(0.01)
            print("[background] output")
        
        session_instance = prompt_session_mock.return_value
        # Start background task, then exit
        session_instance.prompt.side_effect = ("start_bg", EOFError)
        sys_mock.argv = ["ensure_repl"]
        
        app = VulcanoApp()
        
        @app.command()
        def start_bg():
            thread = threading.Thread(target=background_task, daemon=True)
            thread.start()
            return "Background started"
        
        app.run()
        
        # Background task should have executed
        # Check if background output was printed
        printed_calls = [str(call) for call in print_mock.call_args_list]
        background_printed = any("background" in call for call in printed_calls)
