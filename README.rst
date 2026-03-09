Vulcano
=======

|PyPI version| |Code style: black| |Build Status| |codecov| |readthedocs| |Downloads|

Vulcano is a Python framework for building interactive command-line
applications with minimal boilerplate.

`Support the project on Patreon <https://www.patreon.com/dgarana>`__


What is Vulcano?
----------------

Built on top of
`prompt\_toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`__,
Vulcano turns plain Python functions into fully featured CLI commands —
complete with autocompletion, inline help, syntax highlighting, and
command history — with no extra configuration required.

Its simplicity makes it suitable for a wide range of scenarios where you
need to expose existing functions through a REPL or a one-shot argument
interface.

.. figure:: https://github.com/dgarana/vulcano/raw/master/docs/_static/repl_demo.gif?raw=true
   :alt: REPL demo

.. note::
   Vulcano is under active development. The public API may change
   between minor versions while we work toward a stable 1.x release.
   For production use, pin to a specific version.


Key Features
------------

- **Autocomplete** — Vulcano inspects every registered function and
  automatically builds a completion list that includes command names
  and their arguments.
- **Inline help** — Help text is derived from docstrings or from the
  description provided at registration time.
- **History** — Use the up and down arrow keys to navigate through
  previous commands.
- **Module registration** — Register all public functions from an
  existing module without modifying its source.
- **Syntax highlighting** — Powered by Pygments and prompt\_toolkit for
  a polished REPL experience.
- **Concatenated commands** — Chain multiple commands in argument mode
  using ``and``:

  .. code:: bash

      python your_script.py my_func arg="something" and my_func_2 arg="another thing"

- **Context** — Share data between commands through ``VulcanoApp.context``,
  a plain dictionary available to all registered functions.
- **Command templating** — Use any value stored in the context to
  parameterise commands at runtime.
- **Autosuggestion** — When an unknown command is entered, Vulcano
  suggests the closest match:

  .. code:: text

      >> niu
      Command niu not found
      Did you mean: "new"?
      >>

- **Source inspection** — Append ``?`` to any command name to view its
  source code with syntax highlighting:

  .. code:: text

      >> bye?
      @app.command
      def bye(name="User"):
          """ Say goodbye to someone """
          return "Bye {}!".format(name)
      >>


Installation
------------

Install the latest release from PyPI:

.. code:: bash

    pip install vulcano

To install a development version directly from the repository:

.. code:: bash

    git clone https://github.com/dgarana/vulcano.git
    cd vulcano
    pip install -e .


Getting Started
---------------

The repository includes a complete example in ``examples/simple_example.py``.
The snippet below covers the most common features:

.. code:: python

    import random
    from vulcano.app import VulcanoApp
    from vulcano.app.lexer import MonokaiTheme


    app = VulcanoApp()


    @app.command("hi", "Greet someone by name")
    def salute_method_here(name, title="Mr."):
        """Greet a person.

        Args:
            name (str): Name of the person to greet.
            title (str): Honorific title.
        """
        print("Hi! {} {} — glad to see you.".format(title, name))


    def has_context_name():
        """Return True only when a name has been set in the context."""
        return "name" in app.context


    @app.command
    def i_am(name):
        """Store your name in the context.

        Args:
            name (str): Your name.
        """
        app.context["name"] = name


    @app.command(show_if=has_context_name)
    def whoami():
        """Return your name from the context.

        Only shown after ``i_am`` has been called.
        """
        return app.context["name"]


    @app.command
    def bye(name="User"):
        """Say goodbye to someone."""
        return "Bye {}!".format(name)


    @app.command
    def sum_numbers(*args):
        """Return the sum of all provided numbers."""
        return sum(args)


    @app.command
    def multiply(number1, number2):
        """Multiply two numbers."""
        return number1 * number2


    @app.command
    def reverse_word(word):
        """Return the word reversed."""
        return word[::-1]


    @app.command
    def random_upper_word(word):
        """Return the word with randomly capitalised letters."""
        return "".join(random.choice([letter.upper(), letter]) for letter in word)


    if __name__ == "__main__":
        app.run(theme=MonokaiTheme)

The snippet above registers the following commands:
``hi``, ``bye``, ``i_am``, ``whoami``, ``sum_numbers``, ``multiply``,
``reverse_word``, and ``random_upper_word``.

Commands that ``return`` a value have their result printed automatically
and stored in ``context["last_result"]``, making it available for
subsequent commands via templating.

**REPL mode**

.. figure:: https://github.com/dgarana/vulcano/raw/master/docs/_static/repl_demo.gif?raw=true
   :alt: REPL demo

.. code:: bash

    $ python simple_example.py
    >> reverse_word "Hello Baby! This is awesome"
    emosewa si sihT !ybaB olleH
    >> random_upper_word "{last_result}"
    EMosEWa si SiHT !ybAB OlLEH
    >> exit

**Argument mode**

.. figure:: https://github.com/dgarana/vulcano/raw/master/docs/_static/args_demo.gif?raw=true
   :alt: Args mode demo

.. code:: bash

    $ python simple_example.py reverse_word "Hello Baby! This is awesome" and random_upper_word "{last_result}"
    emosewa si sihT !ybaB olleH
    EMOSEWa Si siHT !YbAB olLeH


Contributing
------------

Contributions of all kinds are welcome — bug reports, feature requests,
documentation improvements, and pull requests.

Before submitting a pull request, please ensure that:

1. All existing tests pass (``pytest``).
2. New functionality is covered by tests.
3. The code is formatted with ``black`` and ``isort``.
4. There are no ``flake8`` or ``bandit`` warnings.

Open an issue first if you are planning a significant change, so the
approach can be discussed before implementation.


.. |PyPI version| image:: https://badge.fury.io/py/vulcano.svg
   :target: https://badge.fury.io/py/vulcano
.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
.. |Build Status| image:: https://github.com/dgarana/vulcano/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/dgarana/vulcano/actions/workflows/ci.yml
.. |codecov| image:: https://codecov.io/gh/dgarana/vulcano/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/dgarana/vulcano
.. |readthedocs| image:: https://readthedocs.org/projects/vulcano/badge/?version=latest
   :target: https://vulcano.readthedocs.org
.. |Downloads| image:: https://pepy.tech/badge/vulcano
   :target: https://pepy.tech/project/vulcano
