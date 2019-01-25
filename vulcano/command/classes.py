# -* coding: utf-8 *-
"""
:py:mod:`vulcano.command.classes`
---------------------------------
Vulcano command classes are active classes that handles with commands.
"""
# System imports
# Third-party imports
# Local imports
from .models import Command


class CommandManager(object):
    """
    Command Manager

    The command manager is the choosen one to handle with registration of each
    command you want to use on your command line application.
    """

    def __init__(self):
        self._commands = {}  # type: dict

    def register(self, name=None, description=None):
        """
        Register decorator used to register functions directly on vulcano app

        :param str name: Name for the command
        :param str description: Description for the command
        :return:
        """
        def decorator_register(func):
            self.register_command(func, name, description)

            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return func_wrapper
        return decorator_register

    def register_command(self, func, name=None, description=None):
        """
        Register a function under this Vulcano app instance

        :param function func: Executable function to register
        :param str name: Name for this function
        :param str description: Help for displaying to the user
        :raises NameError: If there's a command already registered with
                                this name
        """
        name = name or func.__name__
        if name in self._commands:
            raise NameError('This command already exists')
        self._commands[name] = Command(func, name, description)

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
