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
