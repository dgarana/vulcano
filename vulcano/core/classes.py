# -* coding: utf-8 *-
"""
:py:mod:`vulcano.core.classes`
------------------------------
"""


__all__ = ["Singleton"]


class Singleton(object):
    """
    Singleton Pattern class.

    Following the singleton pattern, it will return or create an instance
    depending if it already exists or not.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance
