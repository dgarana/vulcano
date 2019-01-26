# -* coding: utf-8 *-
"""
:py:mod:`vulcano.command.models`
--------------------------------
Vulcano models
"""
# System imports
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
    __slots__ = ('name', 'description', 'func')

    def __init__(self, func, name=None, description=None):
        self.func = func  # type: function
        self.name = name or func.__name__  # type: str
        self.description = description or func.__doc__  # type: str

    def run(self, *args, **kwargs):
        """
        Execute this command and return it's result

        :param args: Arguments to pass the function
        :param kwargs: Known arguments to pass the function
        :return: The result of the function execution
        """
        return self.func(*args, **kwargs)
