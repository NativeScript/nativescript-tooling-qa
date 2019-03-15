"""
Tests for debug util.
"""
import unittest

from selenium.webdriver.common.by import By
from core.utils.chrome import Chrome


# noinspection PyMethodMayBeStatic
from core.utils.debug import Debug


class DebugTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.chrome = Chrome()
        cls.chrome.open(url='chrome-devtools://devtools/bundled/inspector.html')
        cls.debug = Debug(cls.chrome.driver)

    @classmethod
    def tearDownClass(cls):
        cls.chrome.kill()

    def test_01_assert_elements_are_loaded(self):
        assert self.debug.left_toolbar is not None
        assert self.debug.content is not None
        assert self.debug.root_element is not None
        assert self.debug.get_root_element() is not None

    def test_02_assert_dev_tools_is_setup_correctly(self):
        toggle_screencast_button = self.debug.get_element_in_shadow_dom(By.CSS_SELECTOR,
                                                                        "button[aria-label='Toggle screencast']",
                                                                        self.debug.left_toolbar)
        assert str(
            toggle_screencast_button.get_attribute("aria-pressed")) == "false", "Screencast is not configure correctly!"

    def test_03_assert_get_element_in_shadow_dom_is_working(self):
        assert_message = "get_element_in_shadow_dom method is not working with default root element!"
        assert self.debug.get_element_in_shadow_dom(By.CSS_SELECTOR,
                                                    "div.widget.vbox") is not None, assert_message
        assert_message = "get_element_in_shadow_dom method is not working with not default root element!"
        assert self.debug.get_element_in_shadow_dom(By.CSS_SELECTOR, "div.widget.vbox",
                                                    self.debug.root_element), assert_message
        assert_message = "get_element_in_shadow_dom method has different value for default and not " \
                         "default root element!"
        with_default_root_element = self.debug.get_element_in_shadow_dom(By.CSS_SELECTOR, "div.widget.vbox")
        without_default_root_element = self.debug.get_element_in_shadow_dom(By.CSS_SELECTOR, "div.widget.vbox",
                                                                            self.debug.root_element)
        assert with_default_root_element == without_default_root_element, assert_message

    def test_04_assert_get_elements_in_shadow_dom_is_working(self):
        assert_message = "get_elements_in_shadow_dom method is not working with default root element!"
        assert self.debug.get_elements_in_shadow_dom(By.CSS_SELECTOR, "div.widget.vbox"), assert_message
        assert_message = "get_elements_in_shadow_dom method is not working with not default root element!"
        assert self.debug.get_elements_in_shadow_dom(By.CSS_SELECTOR, "div.widget.vbox",
                                                     self.debug.root_element), assert_message
        assert_message = "get_elements_in_shadow_dom method has different value for default and not " \
                         "default root element!"
        with_default_root_element = self.debug.get_elements_in_shadow_dom(By.CSS_SELECTOR, "div.widget.vbox")
        without_default_root_element = self.debug.get_elements_in_shadow_dom(By.CSS_SELECTOR, "div.widget.vbox",
                                                                             self.debug.root_element)
        assert with_default_root_element == without_default_root_element, assert_message

    def test_05_assert_get_shadow_element_in_shadow_dom_is_working(self):
        assert_message = "get_shadow_element_in_shadow_dom method is not working with default root element!"
        assert self.debug.get_shadow_element_in_shadow_dom(
            "div.tabbed-pane-left-toolbar.toolbar") is not None, assert_message
        assert_message = "get_shadow_element_in_shadow_dom method is not working with not default root element!"
        assert self.debug.get_shadow_element_in_shadow_dom("div.tabbed-pane-left-toolbar.toolbar",
                                                           self.debug.root_element) is not None, assert_message
        assert_message = "get_shadow_element_in_shadow_dom method has different value for default and not " \
                         "default root element!"
        with_default_root_element = self.debug.get_shadow_element_in_shadow_dom("div.tabbed-pane-left-toolbar.toolbar")
        without_default_root_element = self.debug.get_shadow_element_in_shadow_dom(
            "div.tabbed-pane-left-toolbar.toolbar", self.debug.root_element)
        assert with_default_root_element == without_default_root_element, assert_message

    def test_06_assert_wait_until_shadow_dom_element_located_is_working(self):
        self.debug.wait_until_shadow_dom_element_located(By.CSS_SELECTOR,
                                                         "button[aria-label='Toggle screencast']",
                                                         shadow_dom_root_element=self.debug.left_toolbar, timeout=15,
                                                         assert_element=True)
        toggle_screencast_button = self.debug.get_elements_in_shadow_dom(By.CSS_SELECTOR,
                                                                         "button[aria-label='Toggle screencast']",
                                                                         self.debug.left_toolbar)
        assert_message = "wait_until_shadow_dom_element_located method is not working!"
        assert toggle_screencast_button, assert_message
        self.debug.wait_until_shadow_dom_element_located(By.CSS_SELECTOR,
                                                         "button.toolbarcccc",
                                                         shadow_dom_root_element=self.debug.left_toolbar, timeout=15,
                                                         assert_element=False)
        toggle_screencast_button = self.debug.get_elements_in_shadow_dom(By.CSS_SELECTOR,
                                                                         "button.toolbarcccc",
                                                                         self.debug.left_toolbar)
        assert_message = "wait_until_shadow_dom_element_located method is not working!"
        assert not toggle_screencast_button, assert_message

    def test_07_assert_wait_until_element_is_visible_is_working(self):
        self.debug.wait_until_element_is_visible(By.CSS_SELECTOR, 'body#-blink-dev-tools', timeout=15)
        element = self.debug.driver.find_elements(By.CSS_SELECTOR, 'body#-blink-dev-tools',)
        assert_message = "wait_until_element_is_visible method is not working!"
        assert element, assert_message
        self.debug.wait_until_element_is_visible(By.CSS_SELECTOR, 'body#-blink-dev-tools2222222222', timeout=15)
        element = self.debug.driver.find_elements(By.CSS_SELECTOR, 'body#-blink-dev-tools2222222222', )
        assert_message = "wait_until_element_is_visible method is not working!"
        assert not element, assert_message


if __name__ == '__main__':
    unittest.main()
