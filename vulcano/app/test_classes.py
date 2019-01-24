# -* coding: utf-8 *-
# System imports
import unittest

# Third-party imports
# Local imports
from .classes import VulcanoApp


class TestVulcanoApp(unittest.TestCase):
    """
    Test the Vulcano APP
    """

    def setUp(self):
        self.vulcano_app = VulcanoApp()

    def tearDown(self):
        # Remove the singleton instances before continue next test
        VulcanoApp._instance = None

    def test_it_should_register_and_execute_commands_with_args(self):
        """
        Vulcano app should be able to register commands with normal arguments
        """
        def test_function(what):
            return what

        self.vulcano_app.register_command(
            test_function, 'test_function', 'This is just a test function'
        )
        result = self.vulcano_app.run('test_function', 'Passed!')
        self.assertEquals(result, 'Passed!')

    def test_it_should_register_and_execute_commands_with_kwargs(self):
        """
        Vulcano app should be able to register commands with known arguments
        """
        def test_function(arg1=None, arg2=None):
            return arg1

        self.vulcano_app.register_command(
            test_function, 'test_function', 'This is just a test function'
        )
        result = self.vulcano_app.run('test_function', arg2='No one',
                                      arg1='Passed!')
        self.assertEquals(result, 'Passed!')

    def test_it_should_not_register_commands_with_same_name(self):
        """
        Vulcano app cannot register two commands with same name
        """
        self.vulcano_app.register_command(
            lambda x: None, 'foo', 'Dummy function'
        )
        with self.assertRaises(NameError):
            self.vulcano_app.register_command(
                lambda x: None, 'foo', 'Dummy function'
            )

    def test_it_should_register_with_default(self):
        """
        Vulcano app should be able to register commands without having to pass
        name and/or description
        """
        def test_function():
            """ Test function documentation """
            pass

        self.vulcano_app.register_command(test_function)
        command = self.vulcano_app.get('test_function')
        self.assertEquals(command.name, 'test_function')
        self.assertEquals(command.description, " Test function documentation ")

    def test_register_decorator(self):
        @self.vulcano_app.register()
        def foo_function(arg1=0, arg2=0):
            """ Docstring """
            return arg1 + arg2

        command = self.vulcano_app.get('foo_function')
        self.assertEquals(command.name, 'foo_function')
        self.assertEquals(command.description, ' Docstring ')
        self.assertEquals(foo_function(1, 1), 2)
