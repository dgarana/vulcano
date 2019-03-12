import sys


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
