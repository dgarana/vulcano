# -* coding: utf-8 *-
"""
:py:mod:`vulcano.command.completer`
-----------------------------------
Vulcano APP command completer
"""
# System imports
# Third-party imports
from prompt_toolkit.completion import Completer, Completion

# Local imports


class CommandCompleter(Completer):
    def __init__(self, manager, ignore_case=True):
        """ Command completer

        This class is used to generate everything related with the completer
        for the REPL mode.


        :param CommandManager manager: Vulcano Command manager
        """
        self.manager = manager
        self.ignore_case = ignore_case

    def get_completions(self, document, complete_event):
        text_before_cursor = str(document.text_before_cursor)
        if self.ignore_case:
            text_before_cursor = text_before_cursor.lower()
        text_arr = text_before_cursor.split(" ")
        last_words = text_arr[-1]
        completions = self.__get_current_completions(text_arr[:-1])

        for completion, meta in completions:
            if completion not in document.text_before_cursor and "=" not in last_words:
                yield Completion(completion, -len(last_words), display_meta=meta or u"")

    def __get_current_completions(self, text_arr):
        if len(text_arr) >= 1:
            command = text_arr[0]
            command_obj = self.manager.get(command)
            if command_obj:
                return command_obj.args_completion
        else:
            return self.manager.command_completions
