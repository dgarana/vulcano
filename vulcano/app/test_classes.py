# -* coding: utf-8 *-
# System imports
from unittest import TestCase

# Third-party imports
from mock import patch, MagicMock
import six

# Local imports
from .classes import VulcanoApp, split_list_by_arg


# Builtins have different names depending on the python version
print_builtin = 'builtins.print'
if six.PY2:
    print_builtin = '__builtin__.print'


class TestVulcanoApp(TestCase):

    def test_split_list_by_args(self):
        args = ["test", 'name="David"', "and", "test2", '"hi"']
        expected_commands = [["test", 'name="David"'], ["test2", '"hi"']]
        self.assertListEqual(expected_commands, split_list_by_arg(args, "and"))

    def tearDown(self):
        # Remove the singleton instances before continue next test
        VulcanoApp._instance = None

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
    def test_should_be_store_last_result_in_context_in_repl(self, sys_mock, prompt_session_mock):
        session_instance = prompt_session_mock.return_value
        session_instance.prompt.side_effect = ("test_function", KeyboardInterrupt, EOFError)
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
        app.module('test.module')
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
        session_instance.prompt.side_effect = ("exception_function", "executed", EOFError)
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
