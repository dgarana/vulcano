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
from pygments.styles.monokai import MonokaiStyle
from pygments.style import Style
from prompt_toolkit.styles import style_from_pygments_dict
from pygments.lexer import RegexLexer
from pygments.token import Punctuation, Text, Operator, Keyword, Name, String, Number

# Local imports


__all__ = ["MonokaiTheme", "create_lexer"]


class VulcanoStyle(Style):
    """ All styles used on Vulcano must inherit from this class """

    styles = {}

    @classmethod
    def pygments_style(cls):
        return style_from_pygments_dict(cls.styles)


class MonokaiTheme(MonokaiStyle, VulcanoStyle):
    """ Implementation of the Monokai theme for Vulcano """

    pass


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
            (r"\"(\\.|[^\"])*\"", String.Single),
            (r"\'(\\.|[^\'])*\'", String.Single),
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
