"""Autocomplete logic for Vulcano REPL commands and arguments."""

# System imports
# Third-party imports
from prompt_toolkit.completion import Completer, Completion

# Local imports
from vulcano.exceptions import CommandNotFound


class CommandCompleter(Completer):
    def __init__(self, manager, ignore_case=True, flat_commands=None):
        """Initialize command completion behavior.

        Args:
            manager (Magma): Command manager instance.
            ignore_case (bool): Whether completion matching is case-insensitive.
            flat_commands (dict | None): Mapping of dot-path string to
                :class:`Command` for commands living inside groups, e.g.
                ``{"text.hi": cmd, "text.formal.dear": cmd}``.  When
                provided, these are offered as additional completions and
                used for argument / arg-value lookup.
        """
        self.manager = manager
        self.ignore_case = ignore_case
        self.flat_commands = flat_commands or {}

    def get_completions(self, document, complete_event):
        """Yield completion candidates for the current cursor context."""
        original_text = str(document.text_before_cursor)
        text_before_cursor = original_text
        if self.ignore_case:
            text_before_cursor = text_before_cursor.lower()
        text_arr = text_before_cursor.split(" ")
        original_text_arr = original_text.split(" ")
        last_words = text_arr[-1]

        if "=" in last_words:
            partial_value = last_words.split("=", 1)[1]
            for value, meta in self.__get_arg_value_completions(
                text_arr, original_text_arr
            ):
                yield Completion(value, -len(partial_value), display_meta=meta or "")
        elif "." in last_words:
            # User is typing a dot-path command (e.g. "text." or "text.hi").
            # Only offer flat_commands whose full path starts with this prefix
            # so that root commands are never suggested mid-path.
            prefix = last_words
            for path, cmd in self.flat_commands.items():
                cmp = path.lower() if self.ignore_case else path
                if cmp.startswith(prefix) and path not in document.text_before_cursor:
                    yield Completion(
                        path, -len(prefix), display_meta=cmd.short_description or ""
                    )
        else:
            for completion, meta in self.__get_current_completions(text_arr[:-1]):
                if completion not in document.text_before_cursor:
                    yield Completion(
                        completion, -len(last_words), display_meta=meta or ""
                    )

    def __get_arg_value_completions(self, text_arr, original_text_arr=None):
        """Return value completion candidates for an arg=value context.

        Args:
            text_arr (list[str]): Lowercased tokens from the current input,
                where ``text_arr[0]`` is the command name and
                ``text_arr[-1]`` is the ``arg=partial_value`` token.
            original_text_arr (list[str] | None): Original-case tokens.
                Used to build the *filled_params* dict passed to callable
                ``arg_opts`` so that user-supplied values preserve casing.

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
            command_obj = self.flat_commands.get(command_name)
        if not command_obj:
            return []

        # Build a dict of already-filled params from tokens preceding the
        # current one.  Use the original (non-lowercased) tokens when
        # available so that values preserve their casing.
        filled_params = {}
        source_arr = original_text_arr or text_arr
        for token in source_arr[1:-1]:  # skip command name and current token
            if "=" in token:
                key, _, value = token.partition("=")
                if value:
                    filled_params[key] = value.strip("\"'")

        options = command_obj.get_arg_value_completions(arg_name, filled_params)
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
                # Fall back to flat dot-path commands (e.g. "text.formal.dear").
                command_obj = self.flat_commands.get(command)
            if command_obj:
                return command_obj.args_completion
            return []
        else:
            completions = list(self.manager.command_completions)
            for path, cmd in self.flat_commands.items():
                if cmd.visible:
                    completions.append((path, cmd.short_description or ""))
            return completions
