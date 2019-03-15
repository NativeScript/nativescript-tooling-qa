from selenium.webdriver.common.by import By

from core.log.log import Log
from core.utils.wait import Wait


class Debug(object):
    root_element = None
    left_toolbar = None
    content = None
    chrome = None
    shadow_root_element_script = "return arguments[0].shadowRoot"
    shadow_inner_element_script = "return arguments[0].querySelector(arguments[1]).shadowRoot"

    def __init__(self, chrome, reconnect_to_dev_tools=True):
        self.chrome = chrome
        if reconnect_to_dev_tools:
            self.reconnect_to_devtools()
        root_element_selector = "div[slot='insertion-point-main'][class='vbox flex-auto tabbed-pane']"
        shadow_dom_element = self.chrome.driver.find_element(By.CSS_SELECTOR, root_element_selector)
        self.root_element = self.chrome.driver.execute_script(self.shadow_root_element_script, shadow_dom_element)
        self.left_toolbar = self.get_shadow_element_in_shadow_dom("div.tabbed-pane-left-toolbar.toolbar")
        content_element = self.chrome.driver.find_element(By.XPATH, '//*[@id="elements-content"]/div')
        self.content = self.chrome.driver.execute_script(self.shadow_root_element_script, content_element)
        self.wait_until_shadow_dom_element_located(By.CSS_SELECTOR,
                                                   "button[aria-label='Toggle screencast']",
                                                   shadow_dom_root_element=self.left_toolbar, timeout=15)
        toggle_screencast_button = self.get_element_in_shadow_dom(By.CSS_SELECTOR,
                                                                  "button[aria-label='Toggle screencast']",
                                                                  self.left_toolbar)
        if str(toggle_screencast_button.get_attribute("aria-pressed")) == "true":
            toggle_screencast_button.click()

    def get_root_element(self):
        return self.root_element

    def get_element_in_shadow_dom(self, by_expression, value, shadow_dom_root_element=None):
        if shadow_dom_root_element:
            return shadow_dom_root_element.find_element(by_expression, value)
        else:
            return self.root_element.find_element(by_expression, value)

    def get_elements_in_shadow_dom(self, by_expression, value, shadow_dom_root_element=None):
        if shadow_dom_root_element:
            return shadow_dom_root_element.find_elements(by_expression, value)
        else:
            return self.root_element.find_elements(by_expression, value)

    def get_shadow_element_in_shadow_dom(self, value, shadow_dom_root_element=None):
        if shadow_dom_root_element:
            return self.chrome.driver.execute_script(self.shadow_inner_element_script, shadow_dom_root_element, value)
        else:
            return self.chrome.driver.execute_script(self.shadow_inner_element_script, self.root_element, value)

    def get_element_by_css_selector_and_text(self, value, text, shadow_dom_root_element=None, contains_text=False):
        if shadow_dom_root_element:
            for element in shadow_dom_root_element.find_elements(By.CSS_SELECTOR, value):
                if contains_text:
                    if text in (''.join(element.text)).encode('utf-8'):
                        return element
                else:
                    if (''.join(element.text)).encode('utf-8') == text:
                        return element
        else:
            for element in self.root_element.find_elements(By.CSS_SELECTOR, value):
                if contains_text:
                    if text in (''.join(element.text)).encode('utf-8'):
                        return element
                else:
                    if (''.join(element.text)).encode('utf-8') == text:
                        return element
        return None

    def wait_until_shadow_dom_element_located(self, by_expression, value, shadow_dom_root_element=None,
                                              assert_element=True, timeout=60):
        test_result = Wait.until(
            lambda: len(self.get_elements_in_shadow_dom(by_expression, value, shadow_dom_root_element)) != 0,
            timeout=timeout,
            period=5)
        if assert_element:
            assert test_result, "Element searched by " + str(
                by_expression) + " with value " + value + " not found for " + str(timeout) + " !"
        elif test_result:
            Log.info(
                "Element " + value + " by expression " + by_expression + " for " + str(timeout) + " is not located!")

    def reconnect_to_devtools(self):
        self.chrome.wait_until_element_is_visible(By.CSS_SELECTOR, 'div.vbox.flex-auto.dimmed-pane', timeout=15)
        shadow_dom_element = self.chrome.driver.find_elements(By.CSS_SELECTOR, 'div.vbox.flex-auto.dimmed-pane')
        if shadow_dom_element:
            shadow_div_element = self.chrome.driver.execute_script(self.shadow_root_element_script,
                                                                   shadow_dom_element[0])
            shadow_elements = self.get_shadow_element_in_shadow_dom(".vbox.flex-auto", shadow_div_element)
            reconnect_button = self.get_element_by_css_selector_and_text("button", "Reconnect DevTools",
                                                                         shadow_elements)
            if reconnect_button is not None:
                reconnect_button.click()
