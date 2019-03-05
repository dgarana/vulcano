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
        self.description = description or func.__doc__ or ''  # type: str
        self.args = self.get_function_args(func)  # type: list

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
    def help(self):
        return '{} -- {} // {}'.format(self.name, self.description, ', '.join(self.args) or '')

    def run(self, *args, **kwargs):
        """
        Execute this command and return it's result

        :param args: Arguments to pass the function
        :param kwargs: Known arguments to pass the function
        :return: The result of the function execution
        """
        return self.func(*args, **kwargs)
