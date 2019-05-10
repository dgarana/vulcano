# -* coding: utf-8 *-
"""
:py:mod:`vulcano.command.builtin`
---------------------------------
Builtin commands that comes by default with vulcano.
"""
# System imports
from __future__ import print_function
import sys

# Third-party imports
# Local imports


__all__ = ["help", "exit"]


def help(app):
    def real_help(command=None):
        """ Print this help """
        if command:
            command = app.manager._commands.get(command)
            if command:
                print(command.help)
            else:
                print("Command `{}` not found".format(command))
        else:
            for command in app.manager._commands.values():
                print(command.help)

    return real_help


def exit():
    """ Exits from the cli """
    sys.exit(1)
