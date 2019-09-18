# -* coding: utf-8 *-
# System imports
import unittest

# Third-party imports
from mock import MagicMock, patch
import six

# Local imports
from . import builtin


# Builtins have different names depending on the python version
print_builtin = "builtins.print"
if six.PY2:
    print_builtin = "__builtin__.print"


class TestBuiltin(unittest.TestCase):
    """
    Test builtin methods
    """

    @patch(print_builtin)
    def test_help(self, print_mock):
        app = MagicMock()
        command_mock = MagicMock()
        command_mock.help = "Fake help"
        app.manager._commands.get.side_effect = [command_mock, None]
        help_func = builtin.help(app)
        help_func("fake_name")
        print_mock.assert_called_with("Fake help")

    @patch(print_builtin)
    def test_help_unknown_command(self, print_mock):
        app = MagicMock()
        app.manager._commands.get.return_value = None
        help_func = builtin.help(app)
        help_func("Unknown command")
        print_mock.assert_called_once()

    def test_exit(self):
        app = MagicMock()
        app.do_repl = True
        exit_func = builtin.exit(app)
        exit_func()
        self.assertFalse(app.do_repl)

    @patch(print_builtin)
    def test_help_without_command(self, print_mock):
        app = MagicMock()
        fake_command = MagicMock()
        fake_command.visible = True
        fake2_command = MagicMock()
        fake2_command.visible = True
        app.manager._commands = {'fake': fake_command,
                                 'fake2': fake2_command}
        help_func = builtin.help(app)
        help_func()
        print_mock.assert_called()