# -* coding: utf-8 *-
# System imports
from unittest import TestCase

# Third-party imports
# Local imports
from .parser import inline_parser, CommandParseError


class TestInlineParser(TestCase):
    def test_should_parse_args(self):
        command = "1 2 3 hello bye=True hello=1"
        args, kwargs = inline_parser(command)
        self.assertListEqual(args, [1, 2, 3, "hello"])
        self.assertDictEqual(kwargs, {"hello": 1, "bye": True})

    def test_should_parse_kwargs(self):
        command = "argument_1=1 argument_2=2 argument_3='hello mate'"
        args, kwargs = inline_parser(command)
        self.assertListEqual(args, [])
        self.assertDictEqual(
            kwargs, {"argument_1": 1, "argument_2": 2, "argument_3": "hello mate"}
        )

    def test_should_parse_args_and_kwargs(self):
        command = "1 kwarg_1=2"
        args, kwargs = inline_parser(command)
        self.assertListEqual(args, [1])
        self.assertDictEqual(kwargs, {"kwarg_1": 2})

    def test_should_parse_one_or_more_args(self):
        command = "argument argument2"
        args, kwargs = inline_parser(command)
        self.assertListEqual(args, ["argument", "argument2"])
        self.assertDictEqual(kwargs, {})

    def test_should_parse_when_nothing(self):
        command = ""
        args, kwargs = inline_parser(command)
        self.assertListEqual(args, [])
        self.assertDictEqual(kwargs, {})

    def test_should_handle_exceptions_nicely(self):
        command = "`´"
        with self.assertRaises(CommandParseError):
            inline_parser(command)
