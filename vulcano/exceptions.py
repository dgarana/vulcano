"""Custom exception hierarchy used by Vulcano."""


class VulcanoException(Exception):
    """Base exception for all Vulcano-specific errors."""

    pass


class CommandNotFound(VulcanoException):
    """Raised when a command name is not registered."""

    pass


class CommandParseError(VulcanoException):
    """Raised when user input cannot be parsed into args/kwargs."""

    pass
