"""Syntax highlighting styles and lexer helpers for the REPL."""

# System imports
import re
from typing import Any

from prompt_toolkit.styles import style_from_pygments_dict
from pygments.lexer import RegexLexer
from pygments.style import Style

# Third-party imports
from pygments.styles.monokai import MonokaiStyle
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
)

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

    styles: dict[Any, str] = {}

    @classmethod
    def pygments_style(cls) -> Any:
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


# Snapshot of the base token list captured before any create_lexer call so
# that each invocation always starts from a clean, unmodified state.
_BASE_ROOT_TOKENS = list(VulcanoLexer.tokens["root"])


def create_lexer(commands: list[str] | None = None) -> type[VulcanoLexer]:
    """Return a fresh lexer subclass enriched with registered command keywords.

    A new subclass is created on every call so that Pygments' metaclass
    compiles a clean ``_tokens`` cache for each REPL context (main or group).
    Mutating the shared ``VulcanoLexer`` class in-place is avoided entirely.

    Args:
        commands (list[str] | None): Command names to highlight as keywords.
            Dot-path names such as ``"text.formal.dear"`` are supported;
            their dots are escaped so the regex matches them literally.

    Returns:
        type[VulcanoLexer]: Fresh lexer subclass configured for current commands.
    """
    root_tokens = list(_BASE_ROOT_TOKENS)
    if commands:
        # Sort longest-first so more-specific dot-paths (e.g. "text.formal.dear")
        # are tried before their shorter prefixes ("text.formal", "text").
        sorted_cmds = sorted(commands, key=len, reverse=True)
        commands_list = "|".join(re.escape(cmd) for cmd in sorted_cmds)
        regex_commands = r"^({})\b".format(commands_list)
        root_tokens = [(regex_commands, Keyword)] + root_tokens
    return type(
        "VulcanoLexer",
        (VulcanoLexer,),
        {"tokens": {"root": root_tokens}},
    )
