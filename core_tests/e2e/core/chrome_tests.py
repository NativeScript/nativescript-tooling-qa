"""
Tests for chrome util.
"""
import unittest

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


if __name__ == '__main__':
    unittest.main()
