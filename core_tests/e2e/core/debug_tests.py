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
        dev_tools = ChromeDevTools(self.chrome, port=None)

        # Verify all tabs
        dev_tools.open_tab(ChromeDevToolsTabs.SOURCES)
        assert dev_tools.wait_element_by_text(text="Drop in a folder to add to workspace", timeout=10) is not None
        dev_tools.open_tab(ChromeDevToolsTabs.CONSOLE)
        assert dev_tools.wait_element_by_text(text="Default levels", timeout=10) is not None
        dev_tools.open_tab(ChromeDevToolsTabs.ELEMENTS)
        assert dev_tools.wait_element_by_text(text="Styles", timeout=10) is not None


if __name__ == '__main__':
    unittest.main()
