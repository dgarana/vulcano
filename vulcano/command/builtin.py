"""Built-in commands automatically registered by Vulcano."""

# System imports
# Third-party imports
# Local imports


__all__ = ["help", "exit"]


def help(app):
    """Create the built-in `help` command bound to an app instance.

    Args:
        app (_VulcanoApp): Current app instance.

    Returns:
        callable: Command function printing global or per-command help.
    """

    def real_help(command=None):
        """Print global help or details for a specific command.

        Args:
            command (str | None): Optional command name.
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
    """Create the built-in `exit` command bound to an app instance.

    Args:
        app (_VulcanoApp): Current app instance.

    Returns:
        callable: Command function that stops the REPL loop.
    """

    def _exit():
        """Exit the interactive REPL session."""
        app.do_repl = False

    return _exit
