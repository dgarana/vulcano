from __future__ import print_function
from vulcano.app import VulcanoApp
from vulcano.app.lexer import MonokaiTheme


app = VulcanoApp('modules_example')
app.module('my_module.my_funcs')


if __name__ == '__main__':
    app.run(theme=MonokaiTheme)
