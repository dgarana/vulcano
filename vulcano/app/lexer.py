"""Syntax highlighting styles and lexer helpers for the REPL."""

# System imports
import re

from prompt_toolkit.styles import style_from_pygments_dict
from pygments.lexer import RegexLexer
from pygments.style import Style

# Third-party imports
from pygments.styles.monokai import MonokaiStyle
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text

# Local imports


__all__ = [
    "MonokaiTheme",
    "DraculaTheme",
    "NordTheme",
    "SolarizedDarkTheme",
    "OneDarkTheme",
    "create_lexer",
]


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


class DraculaTheme(VulcanoStyle):
    """Dracula color theme for Vulcano REPL output.

    Palette: https://draculatheme.com/contribute
    """

    styles = {
        Comment: "#6272a4",
        Keyword: "bold #ff79c6",
        Name: "#f8f8f2",
        Number: "#bd93f9",
        Number.Integer: "#bd93f9",
        Operator: "#ff79c6",
        Punctuation: "#f8f8f2",
        String: "#f1fa8c",
        String.Single: "#f1fa8c",
        Text: "#f8f8f2",
    }


class NordTheme(VulcanoStyle):
    """Nord color theme for Vulcano REPL output.

    Palette: https://www.nordtheme.com/docs/colors-and-palettes
    """

    styles = {
        Comment: "#616e88",
        Keyword: "bold #81a1c1",
        Name: "#88c0d0",
        Number: "#b48ead",
        Number.Integer: "#b48ead",
        Operator: "#81a1c1",
        Punctuation: "#eceff4",
        String: "#a3be8c",
        String.Single: "#a3be8c",
        Text: "#d8dee9",
    }


class SolarizedDarkTheme(VulcanoStyle):
    """Solarized Dark color theme for Vulcano REPL output.

    Palette: https://ethanschoonover.com/solarized/
    """

    styles = {
        Comment: "#586e75",
        Keyword: "bold #268bd2",
        Name: "#859900",
        Number: "#d33682",
        Number.Integer: "#d33682",
        Operator: "#cb4b16",
        Punctuation: "#586e75",
        String: "#2aa198",
        String.Single: "#2aa198",
        Text: "#839496",
    }


class OneDarkTheme(VulcanoStyle):
    """Atom One Dark color theme for Vulcano REPL output.

    Palette inspired by Atom's One Dark UI theme.
    """

    styles = {
        Comment: "#5c6370",
        Keyword: "bold #c678dd",
        Name: "#e06c75",
        Number: "#d19a66",
        Number.Integer: "#d19a66",
        Operator: "#56b6c2",
        Punctuation: "#abb2bf",
        String: "#98c379",
        String.Single: "#98c379",
        Text: "#abb2bf",
    }


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
