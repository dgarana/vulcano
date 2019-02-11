Vulcano
[![Build Status](https://travis-ci.org/dgarana/vulcano.svg?branch=master)](https://travis-ci.org/dgarana/vulcano)
[![codecov](https://codecov.io/gh/dgarana/vulcano/branch/master/graph/badge.svg)](https://codecov.io/gh/dgarana/vulcano)
[![readthedocs](https://readthedocs.org/projects/vulcano/badge/?version=latest)](https://vulcano.readthedocs.org)
[![py27build](http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%202.7%20Unit%20Test.svg)](https://travis-ci.org/dgarana/vulcano)
[![py34build](http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.4%20Unit%20Test.svg)](https://travis-ci.org/dgarana/vulcano)
[![py35build](http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.5%20Unit%20Test.svg)](https://travis-ci.org/dgarana/vulcano)
[![py36build](http://travimg.dgarana.com/v1/dgarana/vulcano/master/Pytnon%203.6%20Unit%20Test.svg)](https://travis-ci.org/dgarana/vulcano)
[![py37build](http://travimg.dgarana.com/v1/dgarana/vulcano/master/Python%203.7%20Unit%20Test.svg)](https://travis-ci.org/dgarana/vulcano)
=======

What is Vulcano?

Vulcano is a framework for creating command line utils.

Here's a simple example:

```python
from vulcano.app.classes import VulcanoApp


app = VulcanoApp()


@app.register()
def my_command(arg1=1, arg2=2):
    """ Just some help """
    return arg1 + arg2


@app.register('another_command', 'Just some help here')
def my_command_two()
    pass

if __name__ == '__main__':
    app.run()
```

This will create two commands:
- my_command: Just some help
- another_command: Just some help here
