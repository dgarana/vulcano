import sys



def help(app):
    def real_help():
        """ Print this help """
        for command in app._manager._commands.values():
            print('{} -- {}'.format(command.name, command.description))
    return real_help


def exit():
    """ Exits from the cli """
    sys.exit(1)
