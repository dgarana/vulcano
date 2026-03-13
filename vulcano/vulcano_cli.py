"""Top-level command-line entrypoint for the Vulcano executable."""

# System imports
# Third-party imports
try:
    from cookiecutter.main import cookiecutter

    CK_SUPPORT = True
except ImportError:
    CK_SUPPORT = False

# Local imports
from vulcano import __version__ as vulcano_version

from .app.classes import VulcanoApp

APP = VulcanoApp()


@APP.command
def new() -> str | None:
    """Create a new CLI project from the official cookiecutter template."""
    if not CK_SUPPORT:
        return """
Seems that you don't have cookiecutter installed on your environment.
Cookiecutter is not needed on all scenarios, so we don't add it as a requirement
for running vulcano.

In case you want to create an app, execute the command:
`pip install cookiecutter`
And restart the command line.
        """
    return cookiecutter("https://github.com/dgarana/cookiecutter-vulcano")


@APP.command
def version() -> str:
    """Return the installed Vulcano version."""
    return vulcano_version


def main() -> None:
    """Run Vulcano's own CLI application."""
    if not APP.request_is_for_args:
        print(r"""
             _
            | |
__   ___   _| | ___ __ _ _ __   ___
\ \ / / | | | |/ __/ _` | '_ \ / _ \
 \ V /| |_| | | (_| (_| | | | | (_) |
  \_/  \__,_|_|\___\__,_|_| |_|\___/
=====================================""" + f"\nVersion: {vulcano_version}\n        ")
    APP.run()


if __name__ == "__name__":
    main()
