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
        print "Hello"
        def test_function(what):
            return what

        self.vulcano_app.register('test_function', test_function,
                             'This is just a test function')
        result = self.vulcano_app.run('test_function', 'Passed!')
        self.assertEquals(result, 'Passed!')

    def test_it_should_register_and_execute_commands_with_kwargs(self):
        """
        Vulcano app should be able to register commands with known arguments
        """
        def test_function(arg1=None, arg2=None):
            return arg1

        self.vulcano_app.register('test_function', test_function,
                             'This is just a test function')
        result = self.vulcano_app.run('test_function', arg2='No one',
                                      arg1='Passed!')
        self.assertEquals(result, 'Passed!')

    def test_it_should_not_register_commands_with_same_name(self):
        """
        Vulcano app cannot register two commands with same name
        """
        self.vulcano_app.register('foo', lambda x: None, 'Dummy function')
        with self.assertRaises(NameError):
            self.vulcano_app.register('foo', lambda x: None, 'Dummy function')
