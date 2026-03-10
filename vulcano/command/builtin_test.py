# -* coding: utf-8 *-
# System imports
import unittest

# Third-party imports
from unittest.mock import MagicMock, patch

# Local imports
from . import builtin

console_path = "vulcano.command.builtin.console"


class TestBuiltin(unittest.TestCase):
    """
    Test builtin methods
    """

    @patch(console_path)
    def test_help(self, console_mock):
        app = MagicMock()
        command_mock = MagicMock()
        app.manager._commands.get.return_value = command_mock
        help_func = builtin.help(app)
        help_func("fake_name")
        console_mock.print.assert_called_once_with(command_mock.rich_panel)

    @patch(console_path)
    def test_help_unknown_command(self, console_mock):
        app = MagicMock()
        app.manager._commands.get.return_value = None
        help_func = builtin.help(app)
        help_func("Unknown command")
        console_mock.print.assert_called_once()

    @patch(console_path)
    def test_exit(self, console_mock):
        app = MagicMock()
        app.do_repl = True
        exit_func = builtin.exit(app)
        exit_func()
        self.assertFalse(app.do_repl)
        console_mock.print.assert_called_once()

    @patch(console_path)
    def test_help_without_command(self, console_mock):
        app = MagicMock()
        fake_command = MagicMock()
        fake_command.name = "fake"
        fake_command.short_description = "Does fake things"
        fake_command.visible = True
        fake2_command = MagicMock()
        fake2_command.name = "fake2"
        fake2_command.short_description = "Does more fake things"
        fake2_command.visible = True
        app.manager._commands = {"fake": fake_command, "fake2": fake2_command}
        help_func = builtin.help(app)
        help_func()
        console_mock.print.assert_called_once()
