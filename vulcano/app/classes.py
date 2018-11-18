# -* coding: utf-8 *-
"""
:py:mod:`vulcano.app.classes`
-----------------------------
Main vulcano classes module
"""
# System imports
# Third-party imports
# Local imports
from vulcano.core.classes import Singleton


class Command(object):
    """
    Vulcano Command

    This represents a Command registered for Vulcano

    :param str name: Name for this command
    :param str description: Description of this command
    :param function func: Function that has been registered to be executed
    """
    __slots__ = ('name', 'description', 'func')

    def __init__(self, name, description, func):
        self.name = name  # type: str
        self.description = description  # type: str
        self.func = func  # type: function

    def run(self, *args, **kwargs):
        """
        Execute this command and return it's result

        :param args: Arguments to pass the function
        :param kwargs: Known arguments to pass the function
        :return: The result of the function execution
        """
        return self.func(*args, **kwargs)


class VulcanoApp(Singleton):
    """
    Vulcano APP

    This represents a vulcano application which holds all commands registered
    under this scope.
    """

    def __init__(self):
        #: List of commands registered under this Vulcano APP
        self._commands = getattr(self, '_commands', {})  # type: dict

    def register(self, name, func, help_=None):
        """
        Register a function under this Vulcano app instance

        :param str name: Name for this function
        :param function func: Executable function to register
        :param str help_: Help for displaying to the user
        :raises NameError: If there's a command already registered with
                                this name
        """
        if name in self._commands:
            raise NameError('This command already exists')
        self._commands[name] = Command(name, help_, func)

    def get(self, command_name):
        """
        Returns a registered command

        :param str command_name: Name of the command to get
        :return: Command registered under this name
        :rtype: Command
        """
        return self._commands[command_name]

    def run(self, command_name, *args, **kwargs):
        """
        Runs a command

        :param str command_name: Name of the command to execute
        :param list args: List of arguments to pass to command
        :param dict kwargs: Known arguments to pass to command
        :return: Function execution result
        """
        command = self.get(command_name)
        return command.run(*args, **kwargs)
