"""
Tests for chrome util.
"""
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from core.utils.chrome import Chrome


# noinspection PyMethodMayBeStatic
class ChromeTests(unittest.TestCase):

    def setUp(self):
        self.chrome = Chrome()

    def tearDown(self):
        self.chrome.kill()

    def test_01_smoke(self):
        self.chrome.open(url='https://www.google.com/ncr')
        search_box = self.chrome.driver.find_element_by_name('q')
        search_box.send_keys('NativeScript')
        search_box.send_keys(Keys.ENTER)
        web_site_link = self.chrome.driver.find_element_by_partial_link_text('nativescript.org')
        assert web_site_link is not None

    def test_02_assert_wait_until_element_is_visible_is_working(self):
        self.chrome.open(url='chrome-devtools://devtools/bundled/inspector.html')
        self.chrome.wait_until_element_is_visible(By.CSS_SELECTOR, 'body#-blink-dev-tools', timeout=15)
        element = self.chrome.driver.find_elements(By.CSS_SELECTOR, 'body#-blink-dev-tools',)
        assert_message = "wait_until_element_is_visible method is not working!"
        assert element, assert_message
        self.chrome.wait_until_element_is_visible(By.CSS_SELECTOR, 'body#-blink-dev-tools2222222222', timeout=15)
        element = self.chrome.driver.find_elements(By.CSS_SELECTOR, 'body#-blink-dev-tools2222222222', )
        assert_message = "wait_until_element_is_visible method is not working!"
        assert not element, assert_message


if __name__ == '__main__':
    unittest.main()
