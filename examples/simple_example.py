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
    return "".join(random.choice([letter.upper(), letter]) for letter in word)


if __name__ == '__main__':
    app.run(theme=dark_theme)
