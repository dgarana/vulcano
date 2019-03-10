from __future__ import print_function
from vulcano.app.classes import VulcanoApp
from vulcano.app.lexer import dark_theme


app = VulcanoApp()
app.module('my_module.my_funcs')


if __name__ == '__main__':
    app.run(theme=dark_theme)
