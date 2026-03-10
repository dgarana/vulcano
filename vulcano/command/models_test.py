# -* coding: utf-8 *-
# System imports
import unittest

# Third-party imports
from unittest.mock import MagicMock, call, patch

from rich.panel import Panel

# Local imports
from vulcano.command import models


def sample_command(arg1, arg2=None, arg3="Hello"):
    """Here goes the short description

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
        gfunc_inspect_mock.assert_called_once()

    def test_help(self):
        command = models.Command(sample_command)
        self.assertEqual(
            command.help,
            "sample_command: \tHere goes the short description\n"
            "Here goes the long description\n"
            "\t 📋  Args:\n"
            "\t\t*arg1(str): Here goes the argument 1 desc\n"
            "\t\targ2(str): Here goes the argument 2 desc\n"
            "\t\targ3(default: Hello): None\n",
        )

    def test_rich_panel(self):
        command = models.Command(sample_command)
        panel = command.rich_panel
        self.assertIsInstance(panel, Panel)
        self.assertIn("sample_command", panel.title)

    def test_rich_panel_google_docstring(self):
        def google_func(name, count=1):
            """Do something cool.

            Args:
                name (str): The name to use.
                count (int): How many times.
            """
            pass  # pragma: no cover

        command = models.Command(google_func)
        self.assertEqual(command.short_description, "Do something cool.")
        # Arg type and description parsed from Google-style docstring
        arg_name = next(a for a in command.args if a.name == "name")
        self.assertEqual(arg_name.kind, "str")
        self.assertIn("name", arg_name.description)

    def test_rich_panel_numpy_docstring(self):
        def numpy_func(x, y=0):
            """
            Compute something.

            Parameters
            ----------
            x : float
                The input value.
            y : float, optional
                Offset, by default 0.
            """
            pass  # pragma: no cover

        command = models.Command(numpy_func)
        self.assertEqual(command.short_description, "Compute something.")
        arg_x = next(a for a in command.args if a.name == "x")
        self.assertEqual(arg_x.kind, "float")

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
                ("arg1", "Here goes the argument 1 desc"),
                ("arg2", "Here goes the argument 2 desc"),
                ("arg3", "None"),
            ],
        )

    def test_source_code_property(self):
        command = models.Command(sample_command)
        src = command.source_code
        self.assertIn("sample_command", src)

    def test_args_completion_with_arg_opts_includes_options_hint(self):
        def cmd_with_opts(role="user"):
            """Set role."""
            pass  # pragma: no cover

        command = models.Command(cmd_with_opts, arg_opts={"role": ["admin", "user"]})
        completions = dict(command.args_completion)  # {arg_name: description}
        self.assertIn("admin", completions["role"])
        self.assertIn("user", completions["role"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
