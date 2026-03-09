# -* coding: utf-8 *-
# System imports
import re

# Third-party imports
import pyparsing as pp

# Local imports
from vulcano.exceptions import CommandParseError

__all__ = ["inline_parser", "split_list_by_arg"]


allowed_symbols_in_string = r"-_/#@£$€%*+~|<>?.:"


def _no_transform(x):
    return x


def _bool_transform(x):
    return x in ["True", "true"]


def _str_transform(x):
    return x.strip("\"'")


_TRANSFORMS = {
    "bool": _bool_transform,
    "str": _str_transform,
    "int": int,
    "float": float,
    "dict": dict,
}


def _parse_type(datatype):
    transform = _TRANSFORMS.get(datatype, _no_transform)

    def _parse(s, loc, toks):
        return list(map(transform, toks))

    return _parse


identifier = pp.Word(pp.alphas + "_-", pp.alphanums + "_-")

int_value = pp.Regex(r"\-?\d+").set_parse_action(_parse_type("int"))

float_value = pp.Regex(r"\-?\d+\.\d*([eE]\d+)?").set_parse_action(_parse_type("float"))

bool_value = (
    pp.Literal("True") ^ pp.Literal("true") ^ pp.Literal("False") ^ pp.Literal("false")
).set_parse_action(_parse_type("bool"))

# may have spaces
quoted_string = pp.quotedString.copy().set_parse_action(_parse_type("str"))
# cannot have spaces
unquoted_string = pp.Word(pp.alphanums + allowed_symbols_in_string).set_parse_action(
    _parse_type("str")
)

string_value = quoted_string | unquoted_string

single_value = bool_value | float_value | int_value | string_value

list_value = pp.Group(
    pp.Suppress("[") + pp.Opt(pp.DelimitedList(single_value)) + pp.Suppress("]")
).set_parse_action(_parse_type("list"))

# because this is a recursive construct, a dict can contain dicts in values
dict_value = pp.Forward()

value = list_value ^ single_value ^ dict_value

dict_key_value = pp.dict_of(string_value + pp.Suppress(":"), value)

dict_value <<= pp.Group(
    pp.Suppress("{") + pp.DelimitedList(dict_key_value) + pp.Suppress("}")
).set_parse_action(_parse_type("dict"))

# Positionals stop before keyword arguments (identifier=value patterns).
# This prevents "something=" from being treated as positional "something"
# and leaving the "=" as invalid on its own.
positionals = pp.ZeroOrMore(
    value, stop_on=identifier + pp.Literal("=")
).set_results_name("positionals")

key_value = pp.ZeroOrMore(
    pp.dict_of(identifier + pp.Suppress("="), value).set_results_name("kv")
)

subcommand = identifier.set_results_name("__subcommand__")

# Positionals will be passed as the first argument
command = positionals + key_value


def inline_parser(text):
    expected_pattern = command
    if not text:
        return [], {}
    try:
        result = expected_pattern.parse_string(text, parse_all=True)
        args = result.positionals.as_list() if result.positionals else []
        kwargs = result.kv.as_dict() if result.kv else {}
        return args, kwargs
    except pp.ParseException as e:
        exception = CommandParseError(str(e))
        remaining = e.mark_input_line()
        partial_result = expected_pattern.parse_string(text, parse_all=False)
        exception.remaining = remaining[(remaining.find(">!<") + 3) :]
        exception.partial_result = partial_result
        exception.col = e.col
        raise exception


_SPLIT_TOKEN_ = "___SPLIT_TOKEN___"


def split_list_by_arg(lst, separator):
    """Separate a list by a given value into different lists

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
