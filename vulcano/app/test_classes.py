from unittest import TestCase
from mock import patch
from vulcano.app.classes import VulcanoApp


class TestVulcanoApp(TestCase):

    @patch('vulcano.app.classes.sys')
    def test_should_register_builtin_functions_before_run_args(self, sys_mock):
        sys_mock.argv = ['ensure_no_repl', 'help']
        app = VulcanoApp()
        app.run()
        self.assertIn('exit', app._manager._commands)
        self.assertIn('help', app._manager._commands)