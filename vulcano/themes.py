"""Built-in color themes for Vulcano REPL syntax highlighting.

All themes can be passed directly to :meth:`VulcanoApp.run`::

    from vulcano.app import VulcanoApp
    from vulcano.themes import DraculaTheme

    app = VulcanoApp()
    app.run(theme=DraculaTheme)

To create a custom theme, subclass :class:`VulcanoStyle` and define a
``styles`` dict using standard Pygments token types::

    from pygments.token import Keyword, Name, Number, String, Text
    from vulcano.themes import VulcanoStyle

    class MyTheme(VulcanoStyle):
        styles = {
            Text:    "#ffffff",
            Keyword: "bold #ff0000",
            Name:    "#00ff00",
            Number:  "#0000ff",
            String:  "#ffff00",
        }
"""

from vulcano.app.lexer import (  # noqa: F401
    DraculaTheme,
    MonokaiTheme,
    NordTheme,
    OneDarkTheme,
    SolarizedDarkTheme,
    VulcanoStyle,
)

__all__ = [
    "VulcanoStyle",
    "MonokaiTheme",
    "DraculaTheme",
    "NordTheme",
    "SolarizedDarkTheme",
    "OneDarkTheme",
]
