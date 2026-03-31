from __future__ import print_function
"""Example showing how to expose an existing module through Vulcano.

Assuming you already have functions in ``my_module/my_funcs.py``, this example
registers them without modifying the original module.

Run it with:

    python module_example.py

Then use commands from the imported module inside the Vulcano prompt.
"""

from vulcano.app import VulcanoApp
from vulcano.themes import MonokaiTheme


app = VulcanoApp('modules_example')
app.module('my_module.my_funcs')


if __name__ == '__main__':
    app.run(theme=MonokaiTheme)
