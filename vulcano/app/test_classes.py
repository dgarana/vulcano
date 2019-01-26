from unittest import TestCase
from mock import patch
from vulcano.app.classes import VulcanoApp


class TestVulcanoApp(TestCase):

    @patch('vulcano.app.classes.prompt')
    def test_should_register_builin_functions_before_run(self, prompt_mock):
        prompt_mock.return_value = "help"
        app = VulcanoApp()
        app.run()