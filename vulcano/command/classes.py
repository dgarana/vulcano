# -* coding: utf-8 *-
"""
:py:mod:`vulcano.command.classes`
---------------------------------
Vulcano command classes are active classes that handles with commands.
"""
# System imports
from __future__ import print_function
import importlib
from inspect import getmembers, isfunction
from functools import partial
from collections import OrderedDict

# Third-party imports
import six
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter

# Local imports
from .models import Command
from vulcano.app.lexer import MonokaiTheme
from vulcano.exceptions import CommandNotFound


__all__ = ["Magma"]


def get_module_functions(module):
    return (
        func_obj
        for func_name, func_obj in getmembers(module)
        if not func_name.startswith("_") and isfunction(func_obj)
    )


class Magma(object):
    """
    Magic Manager (A.K.A Magma)

    Magma is the choosen one to handle with registration of each
    command you want to use on your command line application.
    """

    def __init__(self):
        self._commands = OrderedDict()  # type: OrderedDict

    @property
    def command_names(self):
        return [u"{}".format(command) for command in self._commands.keys()]

    @property
    def command_completions(self):
        return [command.command_completer for command in self._commands.values() if command.visible]

    def command(self, name_or_function=None, description=None, show_if=True):
        """
        Register decorator used to command a command functions directly on vulcano app

        :param name_or_function: Name of the function or the function itself
        :param str description: Description for the command
        :param function show_if: Function that will determine when we should show this command or not
        :return:
        """

        def decorator_register(func, name=None):
            """ Function wrapper used as decorator

            As we need access to self, we cannot use wrap from functools.
            """
            self.register_command(func, name, description, show_if)

            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return func_wrapper

        if isfunction(name_or_function):
            function = name_or_function
            return decorator_register(function)
        name = name_or_function
        return partial(decorator_register, name=name)

    def module(self, module):
        """
        Register a module under this vulcano app instance
        """
        if isinstance(module, six.string_types):
            module = importlib.import_module(module)
        for func in get_module_functions(module):
            self.register_command(func)

    def register_command(self, func, name=None, description=None, show_if=True):
        """
        Register a function under this Vulcano app instance

        :param function func: Executable function to command
        :param str name: Name for this function
        :param str description: Help for displaying to the user
        :param function show_if: Function that will determine when we should show this command or not
        :raises NameError: If there's a command already registered with
                                this name
        """
        name = name or func.__name__
        if name in self._commands:
            raise NameError("This command already exists")
        self._commands[name] = Command(func, name, description, show_if)

    def get(self, command_name):
        """
        Returns a registered command

        :param str command_name: Name of the command to get
        :return: Command registered under this name
        :rtype: Command
        """
        if command_name not in self._commands:
            raise CommandNotFound('Command {} not found'.format(command_name))
        return self._commands[command_name]

    def run(self, command_name, *args, **kwargs):
        """
        Runs a command

        :param str command_name: Name of the command to execute
        :param list args: List of arguments to pass to command
        :param dict kwargs: Known arguments to pass to command
        :return: Function execution result
        """
        if command_name.endswith("?"):
            command = self.get(command_name[:-1])
            print(
                highlight(
                    command.source_code,
                    PythonLexer(),
                    Terminal256Formatter(style=MonokaiTheme),
                )
            )
            return
        command = self.get(command_name)
        return command.run(*args, **kwargs)
