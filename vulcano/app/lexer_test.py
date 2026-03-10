# -* coding: utf-8 *-
# System imports
from unittest import TestCase

# Third-party imports
# Local imports
from .lexer import create_lexer


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
