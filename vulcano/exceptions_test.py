# -* coding: utf-8 *-
# System imports
from unittest import TestCase

# Local imports
from vulcano.exceptions import CommandNotFound, CommandParseError, VulcanoException


class TestVulcanoException(TestCase):
    def test_is_subclass_of_exception(self):
        self.assertTrue(issubclass(VulcanoException, Exception))

    def test_can_be_raised_and_caught(self):
        with self.assertRaises(VulcanoException):
            raise VulcanoException("something went wrong")

    def test_carries_message(self):
        msg = "boom"
        exc = VulcanoException(msg)
        self.assertEqual(str(exc), msg)

    def test_caught_as_base_exception(self):
        with self.assertRaises(Exception):
            raise VulcanoException("also an Exception")


class TestCommandNotFound(TestCase):
    def test_is_subclass_of_vulcano_exception(self):
        self.assertTrue(issubclass(CommandNotFound, VulcanoException))

    def test_is_subclass_of_exception(self):
        self.assertTrue(issubclass(CommandNotFound, Exception))

    def test_can_be_raised_and_caught_as_vulcano_exception(self):
        with self.assertRaises(VulcanoException):
            raise CommandNotFound("unknown_cmd")

    def test_carries_command_name(self):
        exc = CommandNotFound("my_command")
        self.assertIn("my_command", str(exc))


class TestCommandParseError(TestCase):
    def test_is_subclass_of_vulcano_exception(self):
        self.assertTrue(issubclass(CommandParseError, VulcanoException))

    def test_is_subclass_of_exception(self):
        self.assertTrue(issubclass(CommandParseError, Exception))

    def test_can_be_raised_and_caught_as_vulcano_exception(self):
        with self.assertRaises(VulcanoException):
            raise CommandParseError("bad input")

    def test_carries_parse_error_message(self):
        exc = CommandParseError("unexpected token !")
        self.assertIn("unexpected token", str(exc))

    def test_different_exception_types_are_distinct(self):
        self.assertIsNot(CommandNotFound, CommandParseError)
        with self.assertRaises(CommandNotFound):
            raise CommandNotFound("cmd")
        with self.assertRaises(CommandParseError):
            raise CommandParseError("parse")
