# -* coding: utf-8 *-
# System imports
import unittest

# Third-party imports
# Local imports
from .classes import Magma


# FIXME: Dummy function to test registration this should go into another module
def test_function():
    pass


# FIXME: Same with this function
def _no_register_func():
    pass


class TestMagma(unittest.TestCase):
    """
    Test the Magic Manager
    """

    def setUp(self):
        self.magma = Magma()

    def tearDown(self):
        # Remove the singleton instances before continue next test
        Magma._instance = None

    def test_it_should_register_and_execute_commands_with_args(self):
        """
        Vulcano app should be able to command commands with positional
        arguments
        """

        def test_function(what, happened, here):
            return what, happened, here

        self.magma.register_command(test_function)
        result = self.magma.run("test_function", "This", "Just", "Happened")
        self.assertEqual(result, ("This", "Just", "Happened"))

    def test_it_should_register_and_execute_commands_with_kwargs(self):
        """
        Vulcano app should be able to command commands with known arguments
        """

        def test_function(arg1=None, arg2=None):
            return arg1, arg2

        self.magma.register_command(test_function)
        result = self.magma.run("test_function", arg2="No one", arg1="Passed!")
        self.assertEqual(result, ("Passed!", "No one"))

    def test_it_should_register_and_execute_commands_with_both(self):
        """
        Vulcano app should be able to command commands with positional and
        known arguments
        """

        def test_function(arg1, arg2=None):
            return arg1, arg2

        self.magma.register_command(test_function)
        result = self.magma.run("test_function", "First", arg2="Second")
        self.assertEqual(result, ("First", "Second"))

    def test_it_should_not_register_commands_with_same_name(self):
        """
        Vulcano app cannot command two commands with same name
        """
        self.magma.register_command(lambda x: None, "foo", "Dummy function")
        with self.assertRaises(NameError):
            self.magma.register_command(lambda x: None, "foo", "Dummy function")

    def test_it_should_register_with_default_name(self):
        """
        Vulcano app should be able to command commands without having to pass
        name.
        """

        def test_function():
            pass

        self.magma.register_command(test_function)
        command = self.magma.get("test_function")
        self.assertEqual(command.name, "test_function")

    def test_it_should_register_with_default_description(self):
        """
        Vulcano app should be able to command commands without having to pass
        name and/or description
        """

        def test_function():
            """ This is just a description form Docstrings """
            pass

        self.magma.register_command(test_function)
        command = self.magma.get("test_function")
        self.assertEqual(
            command.description, " This is just a description form Docstrings "
        )

    def test_register_decorator(self):
        @self.magma.command()
        def foo_function(arg1=0, arg2=0):
            """ Docstring """
            return arg1 + arg2

        command = self.magma.get("foo_function")
        self.assertEqual(command.name, "foo_function")
        self.assertEqual(command.description, " Docstring ")
        self.assertEqual(foo_function(1, 1), 2)

    def test_register_decorator_without_parentheses(self):
        @self.magma.command
        def foo_function(arg1=0, arg2=0):
            """ Docstring """
            return arg1 + arg2

        command = self.magma.get("foo_function")
        self.assertEqual(command.name, "foo_function")
        self.assertEqual(command.description, " Docstring ")
        self.assertEqual(foo_function(1, 1), 2)

    def test_register_module_from_string(self):
        self.magma.module("vulcano.command.test_classes")
        self.assertListEqual(self.magma.command_names, ["test_function"])

    def test_register_module_from_import(self):
        # TODO: Same as dummy_function, should be into another module
        from vulcano.command import test_classes as t_classes

        self.magma.module(t_classes)
        self.assertListEqual(self.magma.command_names, ["test_function"])
