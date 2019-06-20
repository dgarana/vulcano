# -* coding: utf-8 *-
"""
:py:mod:`vulcano.command.models`
--------------------------------
Vulcano models
"""
# System imports
import inspect
import re
import sys

# Third-party imports
# Local imports


__all__ = ["Command", "Argument"]


PARAM_OR_RETURNS_REGEX = re.compile(r":(?:param|returns)")
RETURNS_REGEX = re.compile(
    r":returns: (?P<doc>.*)(?:(?=:param)|(?=:return)|(?=:raises)|(?=:rtype)|\Z)", re.S
)
PARAM_REGEX = re.compile(
    r":param (?P<type>.*?)(?P<name>[\*\w]+): (?P<doc>.*?)(?:(?=:param)|"
    r"(?=:return)|(?=:raises)|(?=:rtype)|\Z)", re.S
)


def trim(docstring):
    """trim function from PEP-257"""
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    # Current code/unittests expects a line return at
    # end of multiline docstrings
    # workaround expected behavior from unittests
    if "\n" in docstring:
        trimmed.append("")

    # Return a single string:
    return "\n".join(trimmed)


def reindent(string):
    """Reindent string"""
    return "\n".join(l.strip() for l in string.strip().split("\n"))


def parse_docstring(func):
    """Parse docstring and return short, long and arguments for this function"""
    docstring = func.__doc__
    short_description = long_description = returns = ""
    params = []

    if docstring:
        docstring = trim(docstring)

        lines = docstring.split("\n", 1)
        short_description = lines[0]

        if len(lines) > 1:
            long_description = lines[1].strip()

            params_returns_desc = None

            match = PARAM_OR_RETURNS_REGEX.search(long_description)
            if match:
                long_desc_end = match.start()
                params_returns_desc = long_description[long_desc_end:].strip()
                long_description = long_description[:long_desc_end].rstrip()

            if params_returns_desc:
                params = {}
                for type_, name, doc in PARAM_REGEX.findall(params_returns_desc):
                    params[name] = {'doc': ' '.join(trim(doc).split('\n')),
                                    'type': type_.strip() if type_ else None}

                match = RETURNS_REGEX.search(params_returns_desc)
                if match:
                    returns = reindent(match.group("doc"))

    return {
        "short_description": short_description,
        "long_description": long_description,
        "params": params,
        "returns": returns
    }


class Argument(object):
    """
    Vulcano command argument

    This represent an Argument of a Command registered for Vulcano

    :param str name: Name of the argument
    :param str description: Description of this argument
    :param str type_: Type of this value in string format
    """

    __slots__ = ("name", "description", "type_")

    def __init__(self, name, description=None, type_=None):
        self.name = name
        self.description = description
        self.type_ = type_


class Command(object):
    """
    Vulcano Command

    This represents a Command registered for Vulcano

    :param str name: Name for this command
    :param str description: Description of this command
    :param function func: Function that has been registered to be executed
    """

    __slots__ = ("name", "description", "func", "args", "long_description", "short_description")

    def __init__(self, func, name=None, description=None):
        self.func = func  # type: callable
        self.name = name or func.__name__  # type: str
        func_specs = parse_docstring(func)
        self.short_description = description or func_specs['short_description']
        self.long_description = func_specs['long_description']
        self.args = {}
        if func_specs['params']:
            for param_name, param_opts in func_specs['params'].items():
                self.args[u'{}'.format(param_name)] = Argument(
                    name=param_name,
                    type_=param_opts['type'],
                    description=param_opts['doc']
                )
        else:
            for arg in self.get_function_args(func):
                self.args[u'{}'.format(arg)] = Argument(name=arg)

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
        description_item = "{}: \t{}".format(self.name, self.short_description)
        if self.long_description:
            description_item += "\n{}".format(self.long_description)
        if self.args:
            description_item += "\n\t Args:"
            for arg in self.args.values():
                arg_description = "\n\t\t{arg.name}"
                if arg.type_:
                    arg_description += "({arg.type_})"
                arg_description += ": {arg.description}"
                description_item += arg_description.format(arg=arg)
        return description_item + "\n"

    def run(self, *args, **kwargs):
        """
        Execute this command and return it's result

        :param args: Arguments to pass the function
        :param kwargs: Known arguments to pass the function
        :return: The result of the function execution
        """
        return self.func(*args, **kwargs)
