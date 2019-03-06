# -* coding: utf-8 *-
"""
:py:mod:`vulcano.app.lexer`
---------------------------
This module contains needed classes with different lexers to use cross the
application.
"""
# System imports
import re

# Third-party imports
from prompt_toolkit.styles import style_from_pygments_dict
from pygments.lexer import RegexLexer
from pygments.token import Punctuation, Text, Operator, Keyword, Name, String, Number

# Local imports


__all__ = ["dark_theme", "light_theme", "create_lexer"]


dark_theme = style_from_pygments_dict(
    {
        Operator: "#89DDFF",
        Keyword: "#C792EA italic",
        Number.Integer: "#F78C6C",
        String.Single: "#C3E88D",
        Name: "#EEFFFF",
        Punctuation: "#89DDFF",
    }
)


light_theme = style_from_pygments_dict(
    {
        Operator: "#39ADB5",
        Keyword: "#7C4DFF italic",
        Number.Integer: "#F76D47",
        String.Single: "#91B859",
        Name: "#90A4AE",
        Punctuation: "#39ADB5",
    }
)


class VulcanoLexer(RegexLexer):
    name = "Vulcano"
    aliases = ["vulcano"]

    flags = re.IGNORECASE
    tokens = {
        "root": [
            (r"\s+", Text),
            (r"[+*/<>=~!@#%^&|`?^-]", Operator),
            (r"((T|t)rue|(F|f)alse)", Operator),
            (r"[0-9]+", Number.Integer),
            (r"'(''|[^'])*'", String.Single),
            (r'"(""|[^"])*"', String.Single),
            (r"[a-zA-Z_][a-zA-Z0-9_]*", Name),
            (r"[;:()\[\],\.{}]", Punctuation),
        ]
    }


def create_lexer(commands=None):
    """ Modifies the VulcanoLexer to add the commands generated through the
    vulcano application 
    
    :param list commands: List of commands to add to the lexer
    :return: VulcanoLexer class to use
    :rtype: VulcanoLexer
    """
    lexer = VulcanoLexer
    if commands:
        commands_list = "|".join(commands)
        regex_commands = r"^({})\b".format(commands_list)
        lexer.tokens["root"].insert(0, (regex_commands, Keyword))
    return lexer
