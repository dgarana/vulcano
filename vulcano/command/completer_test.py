# -* coding: utf-8 *-
# System imports
import unittest

# Third-party imports
from unittest.mock import MagicMock

# Local imports
from vulcano.app.classes import Magma

from .completer import CommandCompleter


class TestCommandCompleter(unittest.TestCase):
    """
    Test the CommandCompleter
    """

    def setUp(self):
        self.manager = Magma()
        self.completer = CommandCompleter(self.manager)

        self.manager.register_command(
            lambda what, happened, here: None, "test_function"
        )
        self.manager.register_command(lambda: None, "no_args")
        self.manager.register_command(
            lambda name, title="Mr.": None,
            "greet",
            arg_opts={"name": ["bob", "rob", "alice"]},
        )
        self.manager.register_command(
            lambda role="user": None,
            "set_role",
            arg_opts={"role": ["power admin", "regular user", "guest"]},
        )

    @staticmethod
    def assertListSameItems(L1, L2):
        return len(L1) == len(L2) and sorted(L1) == sorted(L2)

    def test_it_should_return_commands_first(self):
        """
        CommandCompleter should be returning commands first
        """
        document_mock = MagicMock()
        document_mock.text_before_cursor = ""
        complete_event = MagicMock()
        results = list(self.completer.get_completions(document_mock, complete_event))
        expected_commands = ["test_function", "no_args_func"]
        self.assertListSameItems(expected_commands, [result.text for result in results])

    def test_it_should_return_arguments_for_a_command(self):
        document_mock = MagicMock()
        document_mock.text_before_cursor = "test_function "
        complete_event = MagicMock()
        results = list(self.completer.get_completions(document_mock, complete_event))
        expected_args = ["what", "happened", "here"]
        self.assertListSameItems(expected_args, [result.text for result in results])

    def test_it_should_not_return_already_typed_arguments(self):
        document_mock = MagicMock()
        document_mock.text_before_cursor = "test_function what"
        complete_event = MagicMock()
        results = list(self.completer.get_completions(document_mock, complete_event))
        expected_args = ["happened", "here"]
        self.assertListSameItems(expected_args, [result.text for result in results])

    def test_it_should_not_fail_if_command_not_found(self):
        document_mock = MagicMock()
        document_mock.text_before_cursor = "non_existent "
        complete_event = MagicMock()
        results = list(self.completer.get_completions(document_mock, complete_event))
        self.assertListEqual([], results)

    def test_it_should_return_all_arg_opts_when_no_prefix(self):
        document_mock = MagicMock()
        document_mock.text_before_cursor = "greet name="
        complete_event = MagicMock()
        results = list(self.completer.get_completions(document_mock, complete_event))
        self.assertListSameItems(["bob", "rob", "alice"], [r.text for r in results])

    def test_it_should_filter_arg_opts_by_prefix(self):
        document_mock = MagicMock()
        document_mock.text_before_cursor = "greet name=b"
        complete_event = MagicMock()
        results = list(self.completer.get_completions(document_mock, complete_event))
        self.assertListSameItems(["bob"], [r.text for r in results])

    def test_it_should_match_arg_opts_case_insensitively(self):
        document_mock = MagicMock()
        document_mock.text_before_cursor = "greet name=BOB"
        complete_event = MagicMock()
        results = list(self.completer.get_completions(document_mock, complete_event))
        self.assertListSameItems(["bob"], [r.text for r in results])

    def test_it_should_return_empty_for_unknown_arg_opts(self):
        document_mock = MagicMock()
        document_mock.text_before_cursor = "greet title="
        complete_event = MagicMock()
        results = list(self.completer.get_completions(document_mock, complete_event))
        self.assertListEqual([], results)

    def test_it_should_quote_arg_opts_values_with_spaces(self):
        document_mock = MagicMock()
        document_mock.text_before_cursor = "set_role role="
        complete_event = MagicMock()
        results = list(self.completer.get_completions(document_mock, complete_event))
        self.assertListSameItems(
            ['"power admin"', '"regular user"', '"guest"'],
            [r.text for r in results],
        )
