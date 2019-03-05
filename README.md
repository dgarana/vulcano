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
=======

What is Vulcano?

Vulcano is a framework for creating command line utils.

Here's a simple example:

```python
from __future__ import print_function
from vulcano.app.classes import VulcanoApp


app = VulcanoApp()

@app.command("hi", "Salute people given form parameter")
def salute_method_here(name, title="Mr."):
    print("Hi! {} {} :) Glad to see you.".format(title, name))

@app.command()
def i_am(name):
    app.context['name'] = name

@app.command()
def whoami():
    print(app.context['name'])

@app.command()
def bye(name="User"):
    """ Say goodbye to someone """
    print("Bye {}!".format(name))


if __name__ == '__main__':
    app.run()
```

This will create two commands:
- hi: Registered by wrapping the salute_method_here
- bye: Just registered directly with the bye function

And this will generate something like this:

![Demo gif video](docs/_static/demo.gif?raw=true "Demo gif video")

Nice, right?
