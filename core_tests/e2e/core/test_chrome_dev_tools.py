"""
Tests for debug util.
"""
import unittest

from core.utils.chrome.chrome import Chrome
from core.utils.chrome.chrome_dev_tools import ChromeDevTools, ChromeDevToolsTabs


# noinspection PyMethodMayBeStatic
class DebugTests(unittest.TestCase):
    chrome = None

    @classmethod
    def setUpClass(cls):
        cls.chrome = Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.chrome.kill()

    def test_01_smoke(self):
        # Open chrome dev tools
        dev_tools = ChromeDevTools(self.chrome, platform=None)

        # Verify all tabs
        dev_tools.open_tab(ChromeDevToolsTabs.SOURCES, verify=False)
        assert dev_tools.wait_element_by_text(text="Drop in a folder to add to workspace", timeout=10) is not None
        dev_tools.open_tab(ChromeDevToolsTabs.CONSOLE, verify=False)
        assert dev_tools.wait_element_by_text(text="Default levels", timeout=10) is not None
        dev_tools.open_tab(ChromeDevToolsTabs.ELEMENTS, verify=False)
        assert dev_tools.wait_element_by_text(text="Styles", timeout=10) is not None

    def test_02_type_in_console(self):
        dev_tools = ChromeDevTools(self.chrome, platform=None)
        dev_tools.open_tab(ChromeDevToolsTabs.CONSOLE)
        dev_tools.type_on_console("1+1")


if __name__ == '__main__':
    unittest.main()
