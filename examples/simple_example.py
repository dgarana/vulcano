from __future__ import print_function
import random
from vulcano.app.classes import VulcanoApp
from vulcano.app.lexer import MonokaiTheme


app = VulcanoApp()

@app.command("hi", "Salute people given form parameter")
def salute_method_here(name, title="Mr."):
    """Salute to someone

    :param str name: Name of who you want to say hi!
    :param str title: Title of this person
    """
    print("Hi! {} {} :) Glad to see you.".format(title, name))


def has_context_name():
    """Function to hide a command from command line

    This function is to prevent showing help and autocomplete for commands that need the name
    to be set up on the context.
    """
    return 'name' in app.context


@app.command
def i_am(name):
    """Set your name

    :param str name: Your name goes here!
    """
    app.context['name'] = name


@app.command(show_if=has_context_name)
def whoami():
    """Returns your name from the context

    This is only shown where you've set your name
    """
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
