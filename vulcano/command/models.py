# -* coding: utf-8 *-
"""
:py:mod:`vulcano.command.models`
--------------------------------
Vulcano models
"""
# System imports
import inspect

# Third-party imports
# Local imports


__all__ = ["Command"]


class Command(object):
    """
    Vulcano Command

    This represents a Command registered for Vulcano

    :param str name: Name for this command
    :param str description: Description of this command
    :param function func: Function that has been registered to be executed
    """

    __slots__ = ("name", "description", "func", "args")

    def __init__(self, func, name=None, description=None):
        self.func = func  # type: callable
        self.name = name or func.__name__  # type: str
        self.description = (
            description or func.__doc__ or "No description provided"
        )  # type: str
        self.args = [
            u"{}".format(arg) for arg in self.get_function_args(func)
        ]  # type: list

    @staticmethod
    def get_function_args(func):
        """ Return all the arguments defined on the function

        :param func func: Function to inspect
        :return: List of arguments
        :rtype: list
        """
        arg_spec = inspect.getargspec(func)
        return arg_spec.args

    @property
    def source_code(self):
        return inspect.getsource(self.func)

    @property
    def help(self):
        """ Returns the help for this command

        There should be 2 kind of helps, one for args and another one for REPL mode.

        :return: Help to print
        :rtype: str
        """
        title = "{}\t\t{}".format(self.name, self.description)
        arguments_help = ", ".join(["{}".format(arg) for arg in self.args])
        if arguments_help:
            arguments_help = "\n\tArgs: {}".format(arguments_help)
        return "{}{}".format(title, arguments_help)

    def run(self, *args, **kwargs):
        """
        Execute this command and return it's result

        :param args: Arguments to pass the function
        :param kwargs: Known arguments to pass the function
        :return: The result of the function execution
        """
        return self.func(*args, **kwargs)
