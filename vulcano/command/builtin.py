# -* coding: utf-8 *-
"""
:py:mod:`vulcano.command.builtin`
---------------------------------
Builtin commands that comes by default with vulcano.
"""
# System imports
from __future__ import print_function

# Third-party imports
# Local imports


__all__ = ["help", "exit"]


def help(app):
    def real_help(command=None):
        """ Print help about the application or for a given command

        :param str command: Command to retrieve it's help
        """
        if command:
            command = app.manager._commands.get(command)
            if command:
                print(command.help)
            else:
                print("Command `{}` not found".format(command))
        else:
            for command in app.manager._commands.values():
                if command.visible:
                    print(command.help)

    return real_help


def exit(app):
    def _exit():
        """ Exits from the cli """
        app.do_repl = False
    return _exit
