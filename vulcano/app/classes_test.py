# -* coding: utf-8 *-
# System imports
from __future__ import unicode_literals
from unittest import TestCase

# Third-party imports
from mock import patch, MagicMock
from prompt_toolkit.history import FileHistory
import six

# Local imports
from .classes import VulcanoApp, split_list_by_arg, did_you_mean


# Builtins have different names depending on the python version
print_builtin = "builtins.print"
if six.PY2:
    print_builtin = "__builtin__.print"


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

        try:
            app.run()
        except:
            self.fail("Exception was raised unexpectedly")

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
            never_arrived_here.executed()

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
    def test_it_should_format_command_from_args(self, sys_mock):
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
    def test_it_should_format_command_from_args(self, sys_mock):
        sys_mock.argv = ["ensure_no_repl", "executed", "'{non_existent}'"]
        app = VulcanoApp()
        rendered_with_context = MagicMock()

        @app.command
        def executed(param):
            rendered_with_context.parameter_is(param)

        app.run(print_result=False)
        rendered_with_context.parameter_is.assert_called_with("{non_existent}")

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
        app.run(print_result=False, history_file='somefile.txt')
        prompt_session_mock.assert_called_once()
        _call_args = prompt_session_mock.call_args_list[0][1]
        _history = _call_args.get('history')
        self.assertIsInstance(_history, FileHistory)

    def test_did_you_mean(self):
        command = 'hilp'
        possible_commands = ['hell', 'halo', 'help']
        self.assertEqual('help', did_you_mean(command, possible_commands))

    @patch("vulcano.app.classes.did_you_mean")
    @patch("vulcano.app.classes.sys")
    def test_it_should_did_you_mean_on_args_command_not_found(self, sys_mock, did_you_mean_mock):
        def misspelled_command():
            return

        def miespieled_comand():
            return

        def another_command():
            return

        sys_mock.argv = ["ensure_norepl", "mispeled_comand"]
        did_you_mean_mock.return_value = 'mispelled_command'
        app = VulcanoApp()
        app.command(another_command)
        app.command(miespieled_comand)
        app.command(misspelled_command)

        app.run()
        did_you_mean_mock.assert_called_with(
            'mispeled_comand',
            [u'another_command', u'miespieled_comand', u'misspelled_command', u'exit', u'help']
        )

    @patch("vulcano.app.classes.PromptSession")
    @patch("vulcano.app.classes.did_you_mean")
    @patch("vulcano.app.classes.sys")
    def test_it_should_did_you_mean_on_repl_command_not_found(self, sys_mock, did_you_mean_mock,
                                                              prompt_session_mock):
        def misspelled_command():
            return

        def miespieled_comand():
            return

        def another_command():
            return

        session_instance = prompt_session_mock.return_value
        sys_mock.argv = ["ensure_repl"]
        session_instance.prompt.side_effect = ("mispeled_comand", EOFError)
        did_you_mean_mock.return_value = 'mispelled_command'
        app = VulcanoApp()
        app.command(another_command)
        app.command(miespieled_comand)
        app.command(misspelled_command)

        app.run()
        did_you_mean_mock.assert_called_with(
            'mispeled_comand',
            [u'another_command', u'miespieled_comand', u'misspelled_command', u'exit', u'help']
        )