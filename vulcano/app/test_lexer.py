from unittest import TestCase
from vulcano.app.lexer import create_lexer


class TestCreateLexer(TestCase):

    def test_should_have_commands_inside(self):
        commands = ['help', 'exit', 'command_1']
        expected_regex = r'^(help|exit|command_1)\b'
        lexer = create_lexer(commands)
        root_tokens = lexer.tokens['root']
        command_tokens, _ = root_tokens[0]
        self.assertEquals(expected_regex, command_tokens)
