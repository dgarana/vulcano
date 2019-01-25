# -* coding: utf-8 *-
"""
:py:mod:`vulcano.app.classes`
-----------------------------
Vulcano APP Classes
"""
# System imports
import sys

# Third-party imports
# Local imports
from vulcano.core.classes import Singleton
from vulcano.command.classes import CommandManager


class VulcanoApp(Singleton):
    def __init__(self):
        #: List of commands registered under this Vulcano APP
        self._manager = getattr(self, '_manager', CommandManager())  # type: CommandManager

    def register(self, *args, **kwargs):
        return self._manager.register(*args, **kwargs)

    def run(self):
        if len(sys.argv) >= 2:
            self._exec_from_args()
        else:
            self._exec_from_repl()

    def _exec_from_args(self):
        command = sys.argv[1]
        arguments = sys.argv[2:]
        self._manager.run(command, *arguments)

    def _exec_from_repl(self):
        pass