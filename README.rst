Vulcano
=======
|PyPI version| |Code style: black| |Build Status| |codecov|
|readthedocs| |py27build| |py34build| |py35build| |py36build|
|py37build| |Downloads|

What is Vulcano?
----------------

Vulcano is a framework for creating command line utils.

Built on top of
`prompt\_toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`__,
it helps you to create human-friendly modern command line utils.

It's simplicity makes it suitable in a lot of scenarios where you just
want to run already-created functions in a REPL/ARGS mode.

.. note:: Important notes
   Due some design changes we are working on, we recommend you to
   avoid using this framework on a production environment.
   We're still looking forward having a more idiomatic module name
   convention. If you're happy with the current state, just use it ;)

Key features
------------

-  *Autocomplete*: Vulcano will inspect all the functions you register,
   and will create a list of autocomplete with your command name and
   it's arguments.
-  *Help*: It will create help based on your functions docstrings or the
   help provided during the registration process.
-  *History*: Use up & down arrows to select a command from your
   history.
-  *Register modules*: It can register all the functions inside a module
   just by calling the register module function. It will help you to
   prevent modifying the source module.
-  *Lexer*: Of course, we use lexer with pygments to colorize your
   command line ;)
-  *Concatenated commands*: You want to execute more than one command at
   once from the command line arguments? Just use the "and".
   ``python your_script.py my_func arg=\"something\˝ and my_func_2 arg=\"another thing here\"``
   , such hacker!
-  *Context*: If you want to communicate different functions between
   them, you can use the VulcanoApp.context (it's just a dictionary
   where you store and read data).
-  *Command templating*: You can use whatever is on the context to
   format your command and generate it with data from the context.
-  *Inspect commands source code*: With vulcano, you can inspect a
   command sourcecode by just typing ``?`` at the end of the command.
   For example: ``>> bye?`` it will print this function source with
   syntax highlight.

   .. code:: python

       >> bye?
       @app.command
       def bye(name="User"):
           """ Say goodbye to someone """
           return "Bye {}!".format(name)
       >> 

Installation
------------

Vulcano is automatically delivered through TravisCI, which means that we
usually keep the pip package up to date, this will help you to install
the vulcano latest version by just executing the:
``pip install vulcano``

But in case you're looking for installing a non-delivered version or
just a custom branch, you can install it by cloning the repository and
executing the: ``python setup.py install``

Lets keep things simple.

Learn by example
----------------

The repository usually holds a simple sample ready to execute which
brings an example of almost all the features.

In case you don't want to clone it, you can copy paste it:

.. code:: python

    from __future__ import print_function
    import random
    from vulcano.app.classes import VulcanoApp
    from vulcano.app.lexer import MonokaiTheme


    app = VulcanoApp()

    @app.command("hi", "Salute people given form parameter")
    def salute_method_here(name, title="Mr."):
        print("Hi! {} {} :) Glad to see you.".format(title, name))


    @app.command
    def i_am(name):
        app.context['name'] = name


    @app.command
    def whoami():
        return app.context['name']


    @app.command
    def bye(name="User"):
        """ Say goodbye to someone """
        return "Bye {}!".format(name)


    @app.command
    def sum_numbers(*args):
        """ Sums all numbers passed as parameters """
        return sum(args)


    @app.command
    def multiply(number1, number2):
        """ Just multiply two numbers """
        return number1 * number2


    @app.command
    def reverse_word(word):
        """ Reverse a word """
        return word[::-1]


    @app.command
    def random_upper_word(word):
        """ Returns the word with random upper letters """
        return "".join(random.choice([letter.upper(), letter]) for letter in word)


    if __name__ == '__main__':
        app.run(theme=MonokaiTheme)

This will create next commands: - hi - bye - i\_am - whoami -
sum\_numbers - multiply - reverse\_word - random\_upper\_word

Those commands can ``return`` data that will be printed (if there's
something) and the result will be stored inside the context under the
``last_result`` node. This helps you to be able to use it on the command
line templating.

You can execute from ``repl`` mode:

.. code:: bash

    $ python simple_example.py
    >> reverse_word "Hello Baby! This is awesome"
    emosewa si sihT !ybaB olleH
    >> random_upper_word "{last_result}"
    EMosEWa si SiHT !ybAB OlLEH
    >> exit

And also can be executed from ``args`` mode:

.. code:: bash

    $ python simple_example.py reverse_word \"Hello Baby! This is awesome\" and random_upper_word \"{last_result}\"
    emosewa si sihT !ybaB olleH
    EMOSEWa Si siHT !YbAB olLeH

Here is how the REPL mode looks like (with default theme):

.. figure:: https://github.com/dgarana/vulcano/raw/master/docs/_static/repl_demo.gif?raw=true
   :alt: REPL Demo gif video

   REPL Demo gif video
Nice, right?

Contribute
----------

If you have an idea, you want to help improving something ... or
whatever you think you can help, you're welcome.

All the pull requests will be checked (and also the bugs you report).

.. |PyPI version| image:: https://badge.fury.io/py/vulcano.svg
   :target: https://badge.fury.io/py/vulcano
.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
.. |Build Status| image:: https://travis-ci.org/dgarana/vulcano.svg?branch=master
   :target: https://travis-ci.org/dgarana/vulcano
.. |codecov| image:: https://codecov.io/gh/dgarana/vulcano/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/dgarana/vulcano
.. |readthedocs| image:: https://readthedocs.org/projects/vulcano/badge/?version=latest
   :target: https://vulcano.readthedocs.org
.. |py27build| image:: http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%202.7%20Unit%20Test.svg
   :target: https://travis-ci.org/dgarana/vulcano
.. |py34build| image:: http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.4%20Unit%20Test.svg
   :target: https://travis-ci.org/dgarana/vulcano
.. |py35build| image:: http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.5%20Unit%20Test.svg
   :target: https://travis-ci.org/dgarana/vulcano
.. |py36build| image:: http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.6%20Unit%20Test.svg
   :target: https://travis-ci.org/dgarana/vulcano
.. |py37build| image:: http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.7%20Unit%20Test.svg
   :target: https://travis-ci.org/dgarana/vulcano
.. |Downloads| image:: https://pepy.tech/badge/vulcano
   :target: https://pepy.tech/project/vulcano
