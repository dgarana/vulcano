# -* coding: utf-8 *-
# System imports
from unittest import TestCase

# Local imports
from .docutils import multi_doc_parser


class TestMultiDocParserNullInputs(TestCase):
    def test_none_returns_empty_tuple(self):
        result = multi_doc_parser(None)
        self.assertEqual(result, (None, None, {}, None))

    def test_empty_string_returns_empty_tuple(self):
        result = multi_doc_parser("")
        self.assertEqual(result, (None, None, {}, None))


class TestMultiDocParserPlainProse(TestCase):
    def test_plain_short_description_only(self):
        short, long, params, returns = multi_doc_parser("Do something useful.")
        self.assertEqual(short, "Do something useful.")
        self.assertIsNone(long)
        self.assertEqual(params, {})
        self.assertIsNone(returns)

    def test_short_and_long_description_no_params(self):
        docstring = "Short line.\n\nLonger explanation here."
        short, long, params, returns = multi_doc_parser(docstring)
        self.assertEqual(short, "Short line.")
        self.assertIn("Longer", long)
        self.assertEqual(params, {})
        self.assertIsNone(returns)


class TestMultiDocParserGoogleStyle(TestCase):
    def test_google_style_params(self):
        docstring = """Compute the sum.

        Args:
            x (int): First number.
            y (int): Second number.

        Returns:
            int: The sum.
        """
        short, long, params, returns = multi_doc_parser(docstring)
        self.assertEqual(short, "Compute the sum.")
        self.assertIn("x", params)
        self.assertIn("y", params)
        self.assertEqual(params["x"]["doc"], "First number.")
        self.assertEqual(params["x"]["type"], "int")
        self.assertEqual(params["y"]["doc"], "Second number.")
        self.assertIsNotNone(returns)

    def test_google_style_param_without_type(self):
        docstring = """Do a thing.

        Args:
            name: A name string.
        """
        _, _, params, _ = multi_doc_parser(docstring)
        self.assertIn("name", params)
        self.assertIsNone(params["name"]["type"])
        self.assertEqual(params["name"]["doc"], "A name string.")

    def test_google_style_no_returns(self):
        docstring = """Prints something.

        Args:
            msg (str): The message.
        """
        _, _, _, returns = multi_doc_parser(docstring)
        self.assertIsNone(returns)


class TestMultiDocParserSphinxStyle(TestCase):
    def test_sphinx_style_params(self):
        docstring = """Fetch a resource.

        :param str url: The URL to fetch.
        :param int timeout: Seconds before timeout.
        :returns: The response body.
        """
        short, _, params, returns = multi_doc_parser(docstring)
        self.assertEqual(short, "Fetch a resource.")
        self.assertIn("url", params)
        self.assertEqual(params["url"]["type"], "str")
        self.assertIn("timeout", params)
        self.assertEqual(params["timeout"]["type"], "int")
        self.assertIsNotNone(returns)

    def test_sphinx_style_type_via_type_directive(self):
        docstring = """:param name: A name.
        :type name: str
        """
        _, _, params, _ = multi_doc_parser(docstring)
        self.assertIn("name", params)
        self.assertEqual(params["name"]["type"], "str")


class TestMultiDocParserNumpyStyle(TestCase):
    def test_numpy_style_params(self):
        docstring = """Add two numbers.

        Parameters
        ----------
        a : int
            First operand.
        b : int
            Second operand.

        Returns
        -------
        int
            The result.
        """
        short, _, params, returns = multi_doc_parser(docstring)
        self.assertEqual(short, "Add two numbers.")
        self.assertIn("a", params)
        self.assertEqual(params["a"]["type"], "int")
        self.assertIn("b", params)
        self.assertIsNotNone(returns)


class TestMultiDocParserReturnValues(TestCase):
    def test_returns_description_is_string(self):
        docstring = """Get a value.

        Returns:
            str: The value string.
        """
        _, _, _, returns = multi_doc_parser(docstring)
        self.assertIsInstance(returns, str)
        self.assertTrue(len(returns) > 0)

    def test_no_return_section_yields_none(self):
        docstring = """Just do stuff."""
        _, _, _, returns = multi_doc_parser(docstring)
        self.assertIsNone(returns)
