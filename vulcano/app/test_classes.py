from unittest import TestCase
from mock import patch, MagicMock
from vulcano.app.classes import VulcanoApp


class TestVulcanoApp(TestCase):

    def tearDown(self):
        # Remove the singleton instances before continue next test
        VulcanoApp._instance = None

    @patch('vulcano.app.classes.sys')
    def test_should_register_builtin_functions_before_run_args(self, sys_mock):
        sys_mock.argv = ['ensure_no_repl', 'help']
        app = VulcanoApp()
        app.run()
        self.assertIn('exit', app._manager._commands)
        self.assertIn('help', app._manager._commands)

    @patch('vulcano.app.classes.sys')
    def test_should_be_able_to_register_functions_with_decorator(self, sys_mock):
        sys_mock.argv = ['ensure_no_repl', 'test_function']
        app = VulcanoApp()
        mock_execution = MagicMock()

        @app.register()
        def test_function():
            mock_execution.test_function_called()

        app.run()
        mock_execution.test_function_called.assert_called()

    @patch('vulcano.app.classes.PromptSession')
    @patch('vulcano.app.classes.sys')
    def test_should_be_able_to_execute_in_repl(self, sys_mock, prompt_session_mock):
        session_instance = prompt_session_mock.return_value
        session_instance.prompt.side_effect = ('test_function', EOFError)
        sys_mock.argv = ['ensure_repl']
        app = VulcanoApp()
        mock_execution = MagicMock()

        @app.register()
        def test_function():
            mock_execution.test_function_called()

        app.run()
        mock_execution.test_function_called.assert_called_once()