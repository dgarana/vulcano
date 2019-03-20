"""
Vulcano Command Line
--------------------
Vulcano uses itself for creating vulcano application from command line
"""
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
def new():
    """ This command helps people to create new command line applications
    by just using cookiecutter to create it through a scaffold."""
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
def version():
    """ Returns the vulcano version """
    return vulcano_version


def main():
    """ Main vulcano application excution """
    if not APP.request_is_for_args:
        print(
            """
             _
            | |
__   ___   _| | ___ __ _ _ __   ___
\ \ / / | | | |/ __/ _` | '_ \ / _ \\
 \ V /| |_| | | (_| (_| | | | | (_) |
  \_/  \__,_|_|\___\__,_|_| |_|\___/
=====================================
Version: {}
        """
        ).format(vulcano_version)
    APP.run()


if __name__ == "__name__":
    main()
