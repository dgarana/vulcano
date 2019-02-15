# -* coding: utf-8 *-
"""
:py:mod:`vulcano.app.classes`
-----------------------------
Vulcano APP Classes
"""
# System imports
import sys

# Third-party imports
from prompt_toolkit import PromptSession

# Local imports
from vulcano.command import builtin
from vulcano.core.classes import Singleton
from vulcano.command.classes import CommandManager
from vulcano.command.parser import inline_parser


class VulcanoApp(Singleton):
    def __init__(self):
        #: List of commands registered under this Vulcano APP
        self._manager = getattr(self,
                                '_manager',
                                CommandManager())  # type: CommandManager

    @property
    def request_is_for_args(self):
        return len(sys.argv) >= 2

    def register(self, *args, **kwargs):
        return self._manager.register(*args, **kwargs)

    def run(self):
        self._prepare_builtins()
        if self.request_is_for_args:
            self._exec_from_args()
        else:
            self._exec_from_repl()

    def _prepare_builtins(self):
        self._manager.register_command(builtin.exit, "exit")
        self._manager.register_command(builtin.help(self), "help")

    def _exec_from_args(self):
        command = sys.argv[1]
        arguments = sys.argv[2:]
        self._manager.run(command, *arguments)

    def _exec_from_repl(self):
        self.do_repl = True
        session = PromptSession()
        while self.do_repl:
            try:
                user_input = session.prompt(u'>> ')
            except KeyboardInterrupt:
                continue  # Control-C pressed. Try again.
            except EOFError:
                break  # Control-D Pressed. Finish

            try:
                command = user_input.split()[0]
                arguments = ' '.join(user_input.split()[1:])
                args, kwargs = inline_parser(arguments)
                self._manager.run(command, *args, **kwargs)
            except Exception as error:
                print('Error executing: {}. Error: {}'.format(command, error))
