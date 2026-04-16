# -* coding: utf-8 *-
# System imports
from unittest import TestCase

# Third-party imports
# Local imports
from .parser import CommandParseError, inline_parser, split_list_by_arg


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

    def test_should_parse_a_string_with_colon(self):
        command = "git@github.com:dgarana/vulcano.git"
        args, kwargs = inline_parser(command)
        self.assertEqual(args, [command])

    def test_should_parse_list_value(self):
        """List values exercise the _no_transform path in _parse_type."""
        args, kwargs = inline_parser("items=[1, 2, 3]")
        self.assertEqual(kwargs["items"], [1, 2, 3])

    def test_should_parse_float_value(self):
        _, kwargs = inline_parser("rate=3.14")
        self.assertAlmostEqual(kwargs["rate"], 3.14)

    def test_should_parse_negative_int(self):
        args, _ = inline_parser("-5")
        self.assertEqual(args, [-5])

    def test_should_parse_negative_float(self):
        args, _ = inline_parser("-1.5")
        self.assertAlmostEqual(args[0], -1.5)

    def test_should_parse_boolean_false(self):
        _, kwargs = inline_parser("flag=False")
        self.assertFalse(kwargs["flag"])

    def test_should_parse_lowercase_true_false(self):
        _, kwargs = inline_parser("a=true b=false")
        self.assertTrue(kwargs["a"])
        self.assertFalse(kwargs["b"])

    def test_should_parse_empty_list(self):
        _, kwargs = inline_parser("items=[]")
        self.assertEqual(kwargs["items"], [])

    def test_should_parse_list_of_strings(self):
        _, kwargs = inline_parser("tags=['foo', 'bar']")
        self.assertEqual(kwargs["tags"], ["foo", "bar"])

    def test_dict_syntax_is_not_currently_supported(self):
        # The grammar defines dict_value but the rule has a known parse bug;
        # dict-style kwargs raise CommandParseError instead of being parsed.
        with self.assertRaises(CommandParseError):
            inline_parser("opts={key: value}")

    def test_should_parse_quoted_string_with_spaces(self):
        args, _ = inline_parser('"hello world"')
        self.assertEqual(args, ["hello world"])

    def test_should_parse_single_quoted_string(self):
        args, _ = inline_parser("'single quoted'")
        self.assertEqual(args, ["single quoted"])


class TestSplitListByArg(TestCase):
    def test_splits_on_separator(self):
        result = split_list_by_arg(["cmd1", "and", "cmd2"], "and")
        self.assertEqual(result, ["cmd1", "cmd2"])

    def test_no_separator_returns_single_chunk(self):
        result = split_list_by_arg(["cmd1", "arg=1"], "and")
        self.assertEqual(result, ["cmd1 arg=1"])

    def test_multiple_separators_split_into_multiple_chunks(self):
        result = split_list_by_arg(["a", "and", "b", "and", "c"], "and")
        self.assertEqual(result, ["a", "b", "c"])

    def test_quoted_separator_is_preserved(self):
        result = split_list_by_arg(['cmd', 'msg="hello and world"'], "and")
        self.assertEqual(len(result), 1)
        self.assertIn("and", result[0])

    def test_single_quoted_separator_is_preserved(self):
        result = split_list_by_arg(["cmd", "msg='one and two'"], "and")
        self.assertEqual(len(result), 1)

    def test_separator_is_word_boundary_only(self):
        result = split_list_by_arg(["android", "and", "band"], "and")
        self.assertEqual(result, ["android", "band"])

    def test_empty_list_returns_single_empty_string(self):
        result = split_list_by_arg([], "and")
        self.assertEqual(result, [""])

    def test_custom_separator(self):
        result = split_list_by_arg(["do", "then", "cleanup"], "then")
        self.assertEqual(result, ["do", "cleanup"])
