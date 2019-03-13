Vulcano
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Build Status](https://travis-ci.org/dgarana/vulcano.svg?branch=master)](https://travis-ci.org/dgarana/vulcano)
[![codecov](https://codecov.io/gh/dgarana/vulcano/branch/master/graph/badge.svg)](https://codecov.io/gh/dgarana/vulcano)
[![readthedocs](https://readthedocs.org/projects/vulcano/badge/?version=latest)](https://vulcano.readthedocs.org)
[![py27build](http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%202.7%20Unit%20Test.svg)](https://travis-ci.org/dgarana/vulcano)
[![py34build](http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.4%20Unit%20Test.svg)](https://travis-ci.org/dgarana/vulcano)
[![py35build](http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.5%20Unit%20Test.svg)](https://travis-ci.org/dgarana/vulcano)
[![py36build](http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.6%20Unit%20Test.svg)](https://travis-ci.org/dgarana/vulcano)
[![py37build](http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.7%20Unit%20Test.svg)](https://travis-ci.org/dgarana/vulcano)
[![Downloads](https://pepy.tech/badge/vulcano)](https://pepy.tech/project/vulcano)
=======

What is Vulcano?

Vulcano is a framework for creating command line utils.

Here's a simple example:

```python
from __future__ import print_function
import random
from vulcano.app.classes import VulcanoApp
from vulcano.app.lexer import dark_theme


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
    return "".join(random.choice([letter.upper(), letter ]) for letter in word)


if __name__ == '__main__':
    app.run(theme=dark_theme)
```

This will create two commands:
- hi: Registered by wrapping the salute_method_here
- bye: Just registered directly with the bye function

You can execute from `repl` mode:

```bash
$ python simple_example.py
>> reverse_word "Hello Baby! This is awesome"
emosewa si sihT !ybaB olleH
>> random_upper_word "{last_result}"
EMosEWa si SiHT !ybAB OlLEH
>> exit
```

And also can be executed from `args` mode:
```bash
$ python simple_example.py reverse_word \"Hello Baby! This is awesome\" and random_upper_word \"{last_result}\"
emosewa si sihT !ybaB olleH
EMOSEWa Si siHT !YbAB olLeH
```

More or less, something like this:

![Demo gif video](docs/_static/demo.gif?raw=true "Demo gif video")

Nice, right?

Key features
------------
- Autocomplete: Vulcano will inspect all the functions you register, and will create a list of autocomplete with your command name and it's arguments.
- Help: It will create help based on your functions docstrings or the help provided during the registration process.
- History: Use up & down arrows to select a command from your history.
- Register modules: It can register all the functions inside a module just by calling the register module function. It will help you to prevent modifying the source module.
- Lexer: Of course, we use lexer with pygments to colorize your command line ;)
- Nested commands: You want to execute more than one command at once from the command line arguments? Just use the "and". `python your_script.py my_func arg=\"something\˝ and my_func_2 arg=\"another thing here\"` , such hacker!
- Context: If you want to communicate different functions between them, you can use the VulcanoApp.context (it's just a dictionary where you store and read data).
- Command templating: You can use whatever is on the context to format your command and generate it with data from the context.
