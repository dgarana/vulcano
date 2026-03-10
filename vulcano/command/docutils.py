"""Docstring parsing utilities for Vulcano commands.

Provides a drop-in replacement for pynspector's :func:`sphinx_doc_parser` that
can handle any common docstring convention — Google, NumPy, Sphinx, Epytext —
as well as plain prose docstrings with no parameter sections at all.
"""

# System imports
# Third-party imports
from docstring_parser import parse as _parse_docstring

# Local imports

__all__ = ["multi_doc_parser"]


def multi_doc_parser(docstring):
    """Parse a docstring written in any common convention.

    Supports Google, NumPy, Sphinx/reStructuredText, and Epytext styles.
    Style detection is automatic.  The return format is compatible with the
    ``doc_parser`` interface expected by :func:`pynspector.func_inspections.\
get_func_inspect_result`.

    Args:
        docstring (str | None): Raw docstring to parse.

    Returns:
        tuple: A four-element tuple of
            ``(short_description, long_description, params, returns)`` where
            *params* is a ``dict`` mapping parameter names to
            ``{"doc": ..., "type": ...}`` dicts and *returns* is a ``str``
            description of the return value or ``None``.
    """
    if not docstring:
        return None, None, {}, None

    parsed = _parse_docstring(docstring)

    short_description = parsed.short_description or None
    long_description = parsed.long_description or None

    params = {}
    for param in parsed.params:
        params[param.arg_name] = {
            "doc": param.description or "None",
            "type": param.type_name or None,
        }

    returns = parsed.returns.description if parsed.returns else None

    return short_description, long_description, params, returns
