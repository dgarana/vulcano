# -* coding: utf-8 *-
# System imports
from __future__ import unicode_literals
import unittest

# Third-party imports
from mock import MagicMock

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

        def test_function(what, happened, here):
            return what, happened, here

        def no_args_func():
            return None

        self.manager.register_command(test_function)
        self.manager.register_command(no_args_func)

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
