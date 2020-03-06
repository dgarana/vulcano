# -* coding: utf-8 *-
# System imports
from __future__ import unicode_literals
import unittest

# Third-party imports
from mock import patch, MagicMock, call

# Local imports
from vulcano.command import models


def sample_command(arg1, arg2=None, arg3="Hello"):
    """ Here goes the short description

    Here goes the long description

    :param str arg1: Here goes the argument 1 desc
    :param arg2: Here goes the argument 2 desc
    :type arg2: str
    """
    return  # pragma: no cover


class MyTestCase(unittest.TestCase):
    @patch("vulcano.command.models.get_func_inspect_result")
    def test_assert_should_use_args_if_present(self, gfunc_inspect_mock):
        description = "Description"
        name = "Name"
        command = models.Command(
            func=sample_command, description=description, name=name
        )
        self.assertEqual(
            command.short_description,
            description,
            "Should use description from args whenever possible",
        )
        self.assertEqual(
            command.name, name, "Should use name from args whenever possible"
        )
        self.assertEqual(command.func, sample_command)
        self.assertTrue(command.visible)
        gfunc_inspect_mock.assert_called_with(sample_command)

    def test_help(self):
        command = models.Command(sample_command)
        self.assertEqual(
            command.help,
            "sample_command: \tHere goes the short description\nHere goes the long description\n\t Args:\n\t\t*arg1(str): Here goes the argument 1 desc \n\t\targ2(str): Here goes the argument 2 desc \n\t\targ3(default: Hello): None\n",
        )

    def test_visible_should_accept_a_function(self):
        visible_func = MagicMock()
        visible_func.visible.side_effect = [True, False]
        command = models.Command(sample_command, show_if=visible_func.visible)
        self.assertTrue(command.visible)
        self.assertFalse(command.visible)
        visible_func.visible.assert_has_calls([call(), call()])

    def test_command_completer(self):
        command = models.Command(sample_command)
        completer = command.command_completer
        self.assertIsInstance(completer, tuple)
        name, description = command.command_completer
        self.assertEqual(name, command.name)
        self.assertEqual(description, command.short_description)

    def test_args_completion(self):
        command = models.Command(sample_command)
        args_completer = command.args_completion
        self.assertIsInstance(args_completer, list)
        self.assertListEqual(
            args_completer,
            [
                ("arg1", "Here goes the argument 1 desc "),
                ("arg2", "Here goes the argument 2 desc "),
                ("arg3", "None"),
            ],
        )

    def test_args_opts_completion(self):
        def my_opts():
            return ["Opt1", "Opt2", "Opt3"]

        command = models.Command(sample_command, args_opts=my_opts)
        args_completer = command.args_completion
        self.assertIsInstance(args_completer, list)
        self.assertListEqual(
            args_completer, [("Opt1", None), ("Opt2", None), ("Opt3", None)]
        )


if __name__ == "__main__":
    unittest.main()
