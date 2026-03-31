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

.. code:: text

    $ python your_app.py help

                               📖  Available Commands
    ╭───────────────────┬──────────────────────────────────────────────────────╮
    │ Command           │ Description                                          │
    ├───────────────────┼──────────────────────────────────────────────────────┤
    │ reverse_word      │ Return the word reversed.                            │
    │ random_upper_word │ Return the word with randomly capitalised letters.   │
    │ multiply          │ Multiply two numbers.                                │
    │ bye               │ Say goodbye to someone.                              │
    │ help              │ Print global help or details for a specific command. │
    ╰───────────────────┴──────────────────────────────────────────────────────╯

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
- **Argument value options** — Attach a list of predefined choices to any
  argument with ``arg_opts``; the autocompleter offers them and quotes
  values that contain spaces automatically:

  .. code:: python

      @app.command("greet", "Greet by role", arg_opts={"role": ["admin", "user", "guest"]})
      def greet(name, role="user"):
          return "Hello, {} {}!".format(role.capitalize(), name)

- **Concatenated commands** — Chain multiple commands with ``and``, both
  in argument mode and in the interactive REPL:

  .. code:: bash

      python your_script.py my_func arg="something" and my_func_2 arg="another thing"

- **Context**
  a plain dictionary available to all registered functions.
- **Command templating** — Use any value stored in the context to
  parameterise commands at runtime.
- **Autosuggestion** — When an unknown command is entered, Vulcano
  suggests the closest match:

  .. code:: text

      🌋   niu
      🤔  Command 'niu' not found
      💡  Did you mean: "new"?
      🌋

- **Command groups** — Organise commands into named sub-contexts with
  ``app.group()``.  Typing the group name in the REPL enters an isolated
  sub-session; ``exit`` returns to the parent.  Commands in any group can
  also be run directly with dot-path syntax — both in REPL and argument
  modes — without entering the sub-session at all:

  .. code:: text

      🌋   text.hi name=Alice
      Hi! Mr. Alice :) Glad to see you.
      🌋

  Groups can be nested to any depth.  The prompt chains all ancestor
  names so the current nesting level is always visible:

  .. code:: text

      🌋   text
      🌋  text > formal
      🌋  text > formal > dear name=Alice
      Dear Dr. Alice, I trust this finds you well.
      🌋  text > formal > exit
      🌋  text > exit
      🌋

- **Source inspection** — Append ``?`` to any command name to view its
  source code with syntax highlighting.  Dot-path commands are supported
  too:

  .. code:: text

      🌋   bye?
      @app.command
      def bye(name="User"):
          """ Say goodbye to someone """
          return "Bye {}!".format(name)
      🌋


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
If you just want to see Vulcano working quickly, start there.

Quick start
~~~~~~~~~~~\n
1. Install the package:

.. code:: bash

    pip install vulcano

2. Save the example app below as ``simple_example.py`` (or use the version in
   ``examples/simple_example.py``).

3. Run it in interactive mode:

.. code:: bash

    python simple_example.py

4. Try a few realistic commands:

.. code:: text

    🌋   hi name=Alice title=Dr.
    Hi! Dr. Alice — glad to see you.
    🌋   i_am name=Alice
    🌋   whoami
    Alice
    🌋   greet name=Alice role=admin
    Hello, Admin Alice!
    🌋   multiply number1=6 number2=7
    42
    🌋   text.formal.dear name=Alice title="Prof."
    Dear Prof. Alice, I trust this finds you well.

5. Or run one-shot commands directly from the shell:

.. code:: bash

    python simple_example.py multiply number1=6 number2=7
    python simple_example.py text.formal.dear name=Alice title="Prof."
    python simple_example.py multiply number1=6 number2=7 and reverse_word word=vulcano

The longer snippet below covers the most common features:

.. code:: python

    import random
    from vulcano.app import VulcanoApp
    from vulcano.themes import MonokaiTheme


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


    @app.command("greet", "Greet someone by role", arg_opts={"role": ["admin", "user", "guest"]})
    def greet_by_role(name, role="user"):
        """Greet someone and mention their role.

        Args:
            name (str): Name of the person to greet.
            role (str): Role of the person.
        """
        return "Hello, {} {}!".format(role.capitalize(), name)


    if __name__ == "__main__":
        app.run(theme=MonokaiTheme)


Command Groups
--------------

Groups let you organise commands into named sub-contexts, each with its
own isolated sub-REPL.  Create a group with ``app.group()`` and register
commands on it the same way you would on the main app:

.. code:: python

    from vulcano.app import VulcanoApp

    app = VulcanoApp()

    # Create a group — its name is what the user types to enter it.
    text = app.group("text", "Text-related commands")


    @text.command("hi", "Greet someone")
    def say_hi(name, title="Mr."):
        print("Hi! {} {}!".format(title, name))


    @text.command("greet", "Greet by role", arg_opts={"role": ["admin", "user"]})
    def greet_by_role(name, role="user"):
        return "Hello, {} {}!".format(role.capitalize(), name)


    if __name__ == "__main__":
        app.run()

Typing the group name in the REPL enters the sub-session, where only
that group's commands — plus a local ``help`` and ``exit`` — are
available.  The prompt reflects the current depth:

.. code:: text

    🌋   text
    🌋  text > hi name=Alice
    Hi! Mr. Alice!
    🌋  text > exit
    🌋

**Nested groups** — Groups can contain other groups to any depth:

.. code:: python

    formal = text.group("formal", "Formal greetings")


    @formal.command("dear", "Send a formal greeting")
    def formal_dear(name, title="Dr."):
        return "Dear {} {}, I trust this finds you well.".format(title, name)

The prompt chains all ancestor names:

.. code:: text

    🌋   text
    🌋  text > formal
    🌋  text > formal > dear name=Alice title=Prof.
    Dear Prof. Alice, I trust this finds you well.
    🌋  text > formal > exit
    🌋  text > exit
    🌋

**Dot-path syntax** — Run any group command directly without entering
the sub-session, using ``group.command`` notation.  This works in both
REPL and argument modes and can cross multiple nesting levels:

.. code:: text

    🌋   text.hi name=Alice
    Hi! Mr. Alice!
    🌋   text.formal.dear name=Alice title="Prof."
    Dear Prof. Alice, I trust this finds you well.

.. code:: bash

    $ python your_app.py text.hi name=Alice
    Hi! Mr. Alice!
    $ python your_app.py text.formal.dear name=Alice and bye
    Dear Dr. Alice, I trust this finds you well.
    Bye User!

Autocomplete is dot-path aware: typing ``text.`` offers ``text.hi``,
``text.greet``, ``text.formal``; typing ``text.formal.`` narrows to
``text.formal.dear``.  Argument and ``arg_opts`` completions work the
same as for top-level commands once the full path is typed.


Themes
------

Vulcano ships five built-in themes, all importable from
``vulcano.themes``:

+---------------------+--------------------------------------------------+
| Theme               | Description                                      |
+=====================+==================================================+
| ``MonokaiTheme``    | Classic Monokai (default).                       |
+---------------------+--------------------------------------------------+
| ``DraculaTheme``    | Dracula — pink keywords, purple numbers,         |
|                     | yellow strings.                                  |
+---------------------+--------------------------------------------------+
| ``NordTheme``       | Nord — muted blues and greens on a dark          |
|                     | background.                                      |
+---------------------+--------------------------------------------------+
| ``SolarizedDarkTheme`` | Solarized Dark — blue keywords, cyan          |
|                     | strings, magenta numbers.                        |
+---------------------+--------------------------------------------------+
| ``OneDarkTheme``    | Atom One Dark — purple keywords, green strings,  |
|                     | orange numbers.                                  |
+---------------------+--------------------------------------------------+

Pass any theme to ``app.run()``:

.. code:: python

    from vulcano.app import VulcanoApp
    from vulcano.themes import DraculaTheme

    app.run(theme=DraculaTheme)

To create a custom theme, subclass ``VulcanoStyle`` and define a
``styles`` dict using standard `Pygments token types
<https://pygments.org/docs/tokens/>`__:

.. code:: python

    from pygments.token import Keyword, Name, Number, String, Text
    from vulcano.themes import VulcanoStyle

    class MyTheme(VulcanoStyle):
        styles = {
            Text:    "#ffffff",
            Keyword: "bold #ff0000",
            Name:    "#00ff00",
            Number:  "#0000ff",
            String:  "#ffff00",
        }

    app.run(theme=MyTheme)


The snippet above registers the following commands:
``i_am``, ``whoami``, ``bye``, ``sum_numbers``, ``multiply``,
``reverse_word``, ``random_upper_word``, and ``greet``.
See `Command Groups`_ below to learn how to organise commands into
named sub-contexts.

Commands that ``return`` a value have their result printed automatically
and stored in ``context["last_result"]``, making it available for
subsequent commands via templating.

**REPL mode** — launch with no arguments to start the interactive shell:

.. code:: text

    $ python simple_example.py
    🌋   i_am name=Alice
    🌋   whoami
    Alice
    🌋   reverse_word word=vulcano
    onacluv
    🌋   multiply number1=6 number2=7
    42
    🌋   bye
    Bye User!
    🌋   help command=reverse_word
    ╭────────────────────────── ⚙️  reverse_word ─────────────────────────╮
    │ Return the word reversed.                                            │
    │                                                                      │
    │   Argument   Type   Default   Description                            │
    │  ────────────────────────────────────────────────────────  │
    │   ⚡ word    str              The word to reverse.                   │
    │                                                                      │
    ╰────────────────────────────────────────────────────────────────────────╯
    🌋   greet name=Alice role=admin
    Hello, Admin Alice!
    🌋   multiply number1=6 number2=7 and reverse_word word=vulcano
    42
    onacluv
    🌋   exit
    👋  See you soon!

**Argument mode** — pass commands directly; chain with ``and``:

.. code:: bash

    $ python simple_example.py multiply number1=6 number2=7 and reverse_word word=vulcano
    42
    onacluv
    $ python simple_example.py reverse_word "Hello Baby! This is awesome" and random_upper_word "{last_result}"
    emosewa si sihT !ybaB olleH
    eMOsEwa SI SIHT !YbaB OLlEH


Practical usage notes
---------------------

A few behaviors are especially useful when you start building non-trivial apps:

- Commands that ``return`` a value have that value printed automatically.
- Returned values are also stored in ``context["last_result"]`` and can be reused
  in later commands.
- ``print(...)`` is useful for side-effect-style commands, while ``return`` works
  better for commands whose output should be reused.
- Group commands can be executed either by entering the group in the REPL or by
  using dot-path syntax directly.
- ``arg_opts`` can be static lists or dynamic callables, which makes it possible
  to offer context-aware suggestions.

Context templating
~~~~~~~~~~~~~~~~~~

Vulcano stores command results in ``context["last_result"]``. By default, inline
commands can reference context values using Python-style placeholders such as
``{last_result}``.

For example:

.. code:: bash

    python simple_example.py reverse_word word=vulcano and random_upper_word word="{last_result}"

This works because inline command parsing accepts placeholder braces and Vulcano
formats arguments with the current context before execution.

If you want to disable this behavior and treat placeholders literally, you can
set it either at construction time or afterwards:

.. code:: python

    app = VulcanoApp(enable_context_formatting=False)
    # or later:
    app.enable_context_formatting = False

When disabled, values such as ``{last_result}`` are passed through as plain text
instead of being substituted from the context.

For a more realistic reference app, prefer ``examples/simple_example.py`` over
minimal one-function snippets.

Development
-----------

The project ships a ``Makefile`` that wraps all common development tasks.
Run ``make help`` (or just ``make``) to see the full list of targets:

.. code:: bash

    make fmt        # Format code with black and isort
    make black      # Format with black only
    make isort      # Sort imports with isort only
    make lint       # Check style with flake8
    make flake8     # Run flake8 only
    make security   # Scan with bandit
    make bandit     # Run bandit only
    make test       # Run the test suite
    make check      # All checks without modifying files (CI-friendly)
    make all        # Format, check, and test in one step


Contributing
------------

Contributions of all kinds are welcome — bug reports, feature requests,
documentation improvements, and pull requests.

Before submitting a pull request, please ensure that:

1. All existing tests pass (``make test``).
2. New functionality is covered by tests.
3. Code is formatted and all checks pass (``make check``).

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
