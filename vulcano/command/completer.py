"""Autocomplete logic for Vulcano REPL commands and arguments."""

# System imports
# Third-party imports
from prompt_toolkit.completion import Completer, Completion

# Local imports
from vulcano.exceptions import CommandNotFound


class CommandCompleter(Completer):
    def __init__(self, manager, ignore_case=True):
        """Initialize command completion behavior.

        Args:
            manager (Magma): Command manager instance.
            ignore_case (bool): Whether completion matching is case-insensitive.
        """
        self.manager = manager
        self.ignore_case = ignore_case

    def get_completions(self, document, complete_event):
        """Yield completion candidates for the current cursor context."""
        text_before_cursor = str(document.text_before_cursor)
        if self.ignore_case:
            text_before_cursor = text_before_cursor.lower()
        text_arr = text_before_cursor.split(" ")
        last_words = text_arr[-1]

        if "=" in last_words:
            partial_value = last_words.split("=", 1)[1]
            for value, meta in self.__get_arg_value_completions(text_arr):
                yield Completion(value, -len(partial_value), display_meta=meta or "")
        else:
            for completion, meta in self.__get_current_completions(text_arr[:-1]):
                if completion not in document.text_before_cursor:
                    yield Completion(completion, -len(last_words), display_meta=meta or "")

    def __get_arg_value_completions(self, text_arr):
        """Return value completion candidates for an arg=value context.

        Args:
            text_arr (list[str]): Lowercased tokens from the current input,
                where ``text_arr[0]`` is the command name and
                ``text_arr[-1]`` is the ``arg=partial_value`` token.

        Returns:
            list[tuple[str, str]]: ``(value, meta)`` pairs for matching options.
        """
        if len(text_arr) < 2:
            return []
        command_name = text_arr[0]
        last_word = text_arr[-1]
        arg_name, partial_value = last_word.split("=", 1)
        try:
            command_obj = self.manager.get(command_name)
        except CommandNotFound:
            return []
        options = command_obj.get_arg_value_completions(arg_name)
        return [
            ('"{}"'.format(opt) if " " in opt else opt, "")
            for opt in options
            if (opt.lower() if self.ignore_case else opt).startswith(partial_value)
        ]

    def __get_current_completions(self, text_arr):
        """Return command or argument completion items for current tokens."""
        if len(text_arr) >= 1:
            command = text_arr[0]
            try:
                command_obj = self.manager.get(command)
            except CommandNotFound:
                return []
            if command_obj:
                return command_obj.args_completion
        else:
            return self.manager.command_completions
