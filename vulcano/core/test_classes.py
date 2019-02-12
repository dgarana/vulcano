# -* coding: utf-8 *-
# System imports
import unittest

# Third-party imports
# Local imports
from .classes import Singleton


class TestSingleton(unittest.TestCase):
    """
    Test Singleton pattern class
    """

    def setUp(self):
        self.obj_1, self.obj_2 = Singleton(), Singleton()

    def test_it_should_return_the_same_instance(self):
        """
        It should return the same instance even if we call it
        20 or 300 times.
        """
        self.assertEqual(self.obj_1, self.obj_2)

    def test_it_should_change_attributes_across_instances(self):
        """
        It should change attributes on all instances of the same class
        """
        self.obj_1.new_attribute = True
        self.assertEqual(self.obj_1.new_attribute, self.obj_2.new_attribute)
