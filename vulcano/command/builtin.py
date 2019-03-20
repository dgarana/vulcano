# -* coding: utf-8 *-
"""
:py:mod:`vulcano.command.builtin`
---------------------------------
Builtin commands that comes by default with vulcano.
"""
# System imports
import sys

# Third-party imports
# Local imports


__all__ = ["help", "exit"]


def help(app):
    def real_help():
        """ Print this help """
        for command in app.manager._commands.values():
            print(command.help)

    return real_help


def exit():
    """ Exits from the cli """
    sys.exit(1)
