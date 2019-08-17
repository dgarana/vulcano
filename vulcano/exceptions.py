# -* coding: utf-8 *-
"""
:py:mod:`vulcano.exceptions`
----------------------------
Exceptions raised by Vulcano
"""
# System imports
# Third-party imports
# Local imports


class VulcanoException(Exception):
    """Main vulcano exceptions"""
    pass


class CommandNotFound(VulcanoException):
    """Raised when there's no command"""
    pass


class CommandParseError(VulcanoException):
    """Raised when there's an error parsing a command"""
    pass