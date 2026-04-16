# -* coding: utf-8 *-
# System imports
from unittest import TestCase

# Third-party imports
from pygments.token import Keyword, Name, Number, Operator, String, Text

# Local imports
from .lexer import (
    DraculaTheme,
    MonokaiTheme,
    NordTheme,
    OneDarkTheme,
    SolarizedDarkTheme,
    VulcanoStyle,
    create_lexer,
)


class TestThemesModule(TestCase):
    def test_themes_module_exports_all_themes(self):
        """Importing vulcano.themes re-exports all built-in theme classes."""
        import vulcano.themes as themes

        for name in [
            "VulcanoStyle",
            "MonokaiTheme",
            "DraculaTheme",
            "NordTheme",
            "SolarizedDarkTheme",
            "OneDarkTheme",
        ]:
            self.assertTrue(hasattr(themes, name), "Missing: {}".format(name))


class TestCreateLexer(TestCase):
    def test_should_have_commands_inside(self):
        # Commands are sorted longest-first; names are re.escape()-d.
        commands = ["help", "exit", "command_1"]
        expected_regex = r"^(command_1|help|exit)\b"
        lexer = create_lexer(commands)
        root_tokens = lexer.tokens["root"]
        command_tokens, _ = root_tokens[0]
        self.assertEqual(expected_regex, command_tokens)

    def test_dot_path_commands_are_escaped_and_ordered(self):
        commands = ["text", "text.hi", "text.formal.dear"]
        lexer = create_lexer(commands)
        root_tokens = lexer.tokens["root"]
        command_tokens, _ = root_tokens[0]
        # Longest first; dots must be re.escape()-d to "\." in the pattern.
        self.assertTrue(command_tokens.startswith(r"^("))
        parts = command_tokens[len(r"^(") : -len(r"\b")].rstrip(")").split("|")
        self.assertEqual(parts[0], r"text\.formal\.dear")
        self.assertEqual(parts[1], r"text\.hi")
        self.assertEqual(parts[2], "text")

    def test_create_lexer_with_no_commands_returns_base_token_count(self):
        lexer_none = create_lexer(None)
        lexer_empty = create_lexer([])
        self.assertEqual(
            len(lexer_none.tokens["root"]),
            len(lexer_empty.tokens["root"]),
        )

    def test_each_create_lexer_call_returns_fresh_subclass(self):
        lexer_a = create_lexer(["foo"])
        lexer_b = create_lexer(["bar"])
        self.assertIsNot(lexer_a, lexer_b)

    def test_command_keyword_token_is_first_in_root(self):
        lexer = create_lexer(["mycmd"])
        token_type = lexer.tokens["root"][0][1]
        self.assertEqual(token_type, Keyword)

    def test_no_commands_does_not_prepend_keyword_token(self):
        lexer = create_lexer(None)
        first_token_type = lexer.tokens["root"][0][1]
        self.assertNotEqual(first_token_type, Keyword)


class TestVulcanoLexerTokenization(TestCase):
    def _lex(self, text, commands=None):
        lexer_cls = create_lexer(commands or [])
        lexer = lexer_cls()
        return list(lexer.get_tokens(text))

    def test_integer_tokenized_as_number(self):
        tokens = self._lex("42")
        token_types = [t for t, _ in tokens]
        self.assertIn(Number.Integer, token_types)

    def test_boolean_true_tokenized_as_operator(self):
        tokens = self._lex("True")
        token_types = [t for t, _ in tokens]
        self.assertIn(Operator, token_types)

    def test_boolean_false_tokenized_as_operator(self):
        tokens = self._lex("False")
        token_types = [t for t, _ in tokens]
        self.assertIn(Operator, token_types)

    def test_lowercase_boolean_tokenized_as_operator(self):
        tokens = self._lex("true false")
        token_types = [t for t, _ in tokens]
        self.assertIn(Operator, token_types)

    def test_double_quoted_string_tokenized_as_string(self):
        tokens = self._lex('"hello world"')
        token_types = [t for t, _ in tokens]
        self.assertIn(String.Single, token_types)

    def test_single_quoted_string_tokenized_as_string(self):
        tokens = self._lex("'hello'")
        token_types = [t for t, _ in tokens]
        self.assertIn(String.Single, token_types)

    def test_identifier_tokenized_as_name(self):
        tokens = self._lex("myvar")
        token_types = [t for t, _ in tokens]
        self.assertIn(Name, token_types)

    def test_registered_command_tokenized_as_keyword(self):
        tokens = self._lex("greet", commands=["greet"])
        token_types = [t for t, _ in tokens]
        self.assertIn(Keyword, token_types)

    def test_unregistered_command_not_tokenized_as_keyword(self):
        tokens = self._lex("unknown", commands=["greet"])
        token_types = [t for t, _ in tokens]
        self.assertNotIn(Keyword, token_types)

    def test_whitespace_tokenized_as_text(self):
        tokens = self._lex("  ")
        token_types = [t for t, _ in tokens]
        self.assertIn(Text, token_types)


class TestThemeStyles(TestCase):
    def test_dracula_theme_has_styles(self):
        self.assertTrue(len(DraculaTheme.styles) > 0)

    def test_nord_theme_has_styles(self):
        self.assertTrue(len(NordTheme.styles) > 0)

    def test_solarized_dark_theme_has_styles(self):
        self.assertTrue(len(SolarizedDarkTheme.styles) > 0)

    def test_one_dark_theme_has_styles(self):
        self.assertTrue(len(OneDarkTheme.styles) > 0)

    def test_all_themes_are_subclasses_of_vulcano_style(self):
        themes = [
            MonokaiTheme, DraculaTheme, NordTheme, SolarizedDarkTheme, OneDarkTheme
        ]
        for theme in themes:
            self.assertTrue(
                issubclass(theme, VulcanoStyle),
                "{} not a VulcanoStyle".format(theme.__name__),
            )

    def test_pygments_style_returns_callable(self):
        style = DraculaTheme.pygments_style()
        self.assertIsNotNone(style)

    def test_keyword_style_defined_in_color_themes(self):
        themes = [DraculaTheme, NordTheme, SolarizedDarkTheme, OneDarkTheme]
        for theme in themes:
            self.assertIn(
                Keyword,
                theme.styles,
                "{} missing Keyword style".format(theme.__name__),
            )
