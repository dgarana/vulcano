# -* coding: utf-8 *-
"""
:py:mod:`vulcano.app.classes`
-----------------------------
Vulcano APP Classes
"""
# System imports
from __future__ import print_function
import sys
import re

# Third-party imports
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyCompleter
from prompt_toolkit.lexers import PygmentsLexer

# Local imports
from vulcano.command import builtin
from vulcano.core.classes import Singleton
from vulcano.command.classes import Magma
from vulcano.command.completer import CommandCompleter
from vulcano.command.parser import inline_parser
from .lexer import create_lexer, MonokaiTheme


__all__ = ["VulcanoApp"]
_SPLIT_TOKEN_ = "___SPLIT_TOKEN___"


def split_list_by_arg(lst, separator):
    """ Separate a list by a given value into different lists

    :param list lst: List to separate
    :param str separator: String to use as separator
    :return:
    """

    def _what_to_return(match):
        if match.group(1):
            return match.group(1)
        if match.group(2):
            return match.group(2)
        return _SPLIT_TOKEN_

    commands = " ".join(lst)
    rx = r"(\"[^\"\\]*(?:\\.[^'\\]*)*\")|('[^'\\]*(?:\\.[^'\\]*)*')|\b{0}\b"
    res = re.sub(rx.format(separator), _what_to_return, commands)
    return [command.strip() for command in res.split(_SPLIT_TOKEN_)]


class VulcanoApp(Singleton):
    """ VulcanoApp is the class choosen for managing the application.

    It has the all the things needed to command/execute/manage commands."""

    def __init__(self):
        #: List of commands registered under this Vulcano APP
        self.manager = getattr(self, "manager", Magma())  # type: Magma
        self.context = getattr(self, "context", {})  # Type: dict
        self.print_result = True

    @property
    def request_is_for_args(self):
        """ Returns if the request is for running with args or in REPL mode

        :return: Request is to be run with args or not
        :rtype: bool
        """
        return len(sys.argv) >= 2

    def command(self, *args, **kwargs):
        """ Register a command under current Vulcano instance

        For more options take a look at `vulcano.command.classes.CommandManager.command`
        """
        return self.manager.command(*args, **kwargs)

    def module(self, module):
        """ Register a module under current Vulcano instance

        :param module: Module could be a string or a module object
        """
        return self.manager.module(module)

    def run(self, theme=MonokaiTheme, print_result=True):
        """ Start the application

        It will run the application in Args or REPL mode, depending on the
        parameters sent.

        :param theme: Theme to use for this application, NOTE: only used for the REPL.
        :param bool print_result: If True, results from functions will be printed.
        """
        self.print_result = print_result
        self._prepare_builtins()
        if self.request_is_for_args:
            self._exec_from_args()
        else:
            self._exec_from_repl(theme=theme)

    def _prepare_builtins(self):
        self.manager.register_command(builtin.exit, "exit")
        self.manager.register_command(builtin.help(self), "help")

    def _exec_from_args(self):
        commands = split_list_by_arg(lst=sys.argv[1:], separator="and")
        for command in commands:
            command_list = command.split()
            command_name = command_list[0]
            arguments = " ".join(command_list[1:])
            try:
                arguments = arguments.format(**self.context)
            except KeyError:
                pass
            args, kwargs = inline_parser(arguments)
            self._execute_command(command_name, *args, **kwargs)

    def _exec_from_repl(self, theme=MonokaiTheme):
        self.do_repl = True
        manager_completer = FuzzyCompleter(
            CommandCompleter(self.manager, ignore_case=True)
        )
        lexer = create_lexer(commands=self.manager.command_names)
        session = PromptSession(
            completer=manager_completer,
            lexer=PygmentsLexer(lexer),
            style=theme.pygments_style(),
        )
        while self.do_repl:
            try:
                user_input = u"{}".format(session.prompt(u">> "))
            except KeyboardInterrupt:
                continue  # Control-C pressed. Try again.
            except EOFError:
                break  # Control-D Pressed. Finish

            try:
                command_list = user_input.split()
                if not command_list:
                    continue
                command = command_list[0]
                arguments = " ".join(command_list[1:])
                try:
                    arguments = arguments.format(**self.context)
                except KeyError:
                    pass
                args, kwargs = inline_parser(arguments)
                self._execute_command(command, *args, **kwargs)
            except Exception as error:
                print("Error executing: {}. Error: {}".format(command, error))

    def _execute_command(self, command_name, *args, **kwargs):
        self.context["last_result"] = self.manager.run(command_name, *args, **kwargs)
        if self.print_result and self.context["last_result"]:
            print(self.context["last_result"])
        return self.context["last_result"]
