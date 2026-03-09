"""Syntax highlighting styles and lexer helpers for the REPL."""

# System imports
import re

from prompt_toolkit.styles import style_from_pygments_dict
from pygments.lexer import RegexLexer
from pygments.style import Style

# Third-party imports
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Keyword, Name, Number, Operator, Punctuation, String, Text

# Local imports


__all__ = ["MonokaiTheme", "create_lexer"]


class VulcanoStyle(Style):
    """Base style class for Vulcano themes."""

    styles = {}

    @classmethod
    def pygments_style(cls):
        """Return a prompt-toolkit style object from pygments style mapping."""
        return style_from_pygments_dict(cls.styles)


class MonokaiTheme(MonokaiStyle, VulcanoStyle):
    """Monokai-based color theme for Vulcano REPL output."""

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
    """Return a lexer class enriched with registered command keywords.

    Args:
        commands (list[str] | None): Command names to mark as keywords.

    Returns:
        type[VulcanoLexer]: Lexer class configured for current commands.
    """
    lexer = VulcanoLexer
    if commands:
        commands_list = "|".join(commands)
        regex_commands = r"^({})\b".format(commands_list)
        lexer.tokens["root"].insert(0, (regex_commands, Keyword))
    return lexer
