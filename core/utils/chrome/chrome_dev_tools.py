from time import sleep

from aenum import IntEnum
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.wait import Wait


class ChromeDevToolsTabs(IntEnum):
    _init_ = 'value string'

    ELEMENTS = 1, 'tab-elements'
    CONSOLE = 2, 'tab-console'
    SOURCES = 3, 'tab-sources'

    def __str__(self):
        return self.string


class ChromeDevTools(object):
    chrome = None
    main_panel = None
    source_panel = None
    shadow_root_element_script = "return arguments[0].shadowRoot"
    shadow_inner_element_script = "return arguments[0].querySelector(arguments[1]).shadowRoot"

    def __init__(self, chrome, port=40000):
        # Start Chrome and open debug url
        self.chrome = chrome
        debug_url = 'chrome-devtools://devtools/bundled/inspector.html'
        if port is not None:
            debug_url = debug_url + '?experiments=true&ws=localhost:' + str(port)
        self.chrome.open(url=debug_url)

        # Locate main panel
        self.__refresh_main_panel()
        self.__expand_main_panel()
        Log.info('Chrome dev tools loaded.')

    def __expand_shadow_element(self, element):
        return self.chrome.driver.execute_script(self.shadow_root_element_script, element)

    def __get_shadow_element_in_shadow_dom(self, value, shadow_dom_root_element):
        return self.chrome.driver.execute_script(self.shadow_inner_element_script, shadow_dom_root_element, value)

    def __refresh_main_panel(self):
        content_panel_selector = "div[slot='insertion-point-main'][class='vbox flex-auto tabbed-pane']"
        content_holder = self.chrome.driver.find_element(By.CSS_SELECTOR, content_panel_selector)
        self.main_panel = self.__expand_shadow_element(content_holder)
        assert self.main_panel is not None, 'Failed to load chrome dev tools.'

    def __expand_main_panel(self):
        button_container = self.main_panel.find_element(By.CSS_SELECTOR, 'div.tabbed-pane-left-toolbar.toolbar')
        button_root = self.__expand_shadow_element(button_container)
        button = button_root.find_element(By.CSS_SELECTOR, "button[aria-label='Toggle screencast']")
        if 'toolbar-state-on' in button.get_attribute("class"):
            Log.info('Expand dev tools main pannel.')
            button.click()
        else:
            Log.info("Deb tools main panel already expanded.")

    def find_element_by_text(self, text, control='*', exact_match=False):
        self.__refresh_main_panel()
        for element in self.main_panel.find_elements_by_css_selector(control):
            if exact_match:
                if text == element.text:
                    return element
            else:
                if text in element.text:
                    return element
        return None

    def wait_element_by_text(self, text, timeout=30):
        self.chrome.driver.implicitly_wait(1)
        result = Wait.until(lambda: self.find_element_by_text(text) is not None, timeout=timeout, period=1)
        self.chrome.driver.implicitly_wait(self.chrome.implicitly_wait)
        assert result, 'Failed to find element by "{0}" text.'.format(text)
        Log.debug('Element with text "{0}" found.'.format(text))
        return self.find_element_by_text(text)

    def open_tab(self, tab):
        """
        Opens chrome dev tools tab.
        :param tab: ChromeDevToolsTabs enum value.
        """
        Log.info('Navigate to {0}.'.format(str(tab)))
        element = self.main_panel.find_element(By.ID, str(tab))
        element.click()
        self.__refresh_main_panel()

    def load_source_file(self, file_name):
        """
        Open file on Sources tab of Chrome Dev Tools.
        :param file_name: Name of file.
        """
        actions = ActionChains(self.chrome.driver)
        if Settings.HOST_OS == OSType.OSX:
            actions.send_keys(Keys.COMMAND, 'p').perform()
        else:
            actions.send_keys(Keys.CONTROL, 'p').perform()
        sleep(1)
        shadow_dom_element = self.chrome.driver.find_element(By.CSS_SELECTOR,
                                                             "div[style='z-index: 3000;'][class='vbox flex-auto']")
        shadow_root = self.__expand_shadow_element(shadow_dom_element)

        popup = self.__get_shadow_element_in_shadow_dom(".vbox.flex-auto", shadow_root)
        search_box = popup.find_element(By.CSS_SELECTOR, "span > div > div")
        search_box.click()
        search_box.clear()
        search_box.send_keys(file_name)
        search_box.click()
        search_box.clear()
        search_box.send_keys(file_name)
        search_box.click()
        search_box.send_keys(Keys.ENTER)

    def breakpoint(self, line):
        """
        Toggle breakpoint on line number.
        :param line: Line number
        """

        source = self.chrome.driver.find_element(By.ID, "sources-panel-sources-view")
        assert source is not None, "Failed to find sources."
        lines = source.find_elements(By.CSS_SELECTOR, "div[class=\'CodeMirror-linenumber CodeMirror-gutter-elt\']")
        length = len(lines)
        assert len(lines) >= line, "Line {0} not found! Total lines of code: {1}".format(str(line), str(length))
        lines[line - 1].click()
        Log.info("Toggle breakpoint on line {0}".format(str(line)))

    def continue_debug(self):
        """
        Click continue debug button when breakpoint is hit.
        """
        debug_holder = self.chrome.driver.find_element(By.CSS_SELECTOR, "*[class='scripts-debug-toolbar toolbar']")
        debug_panel = self.__expand_shadow_element(debug_holder)
        button = debug_panel.find_element(By.CSS_SELECTOR, "button[aria-label='Pause script execution']")
        assert 'toolbar-state-on' in button.get_attribute("class"), "Continue button not enabled!"
        button.click()

    def __find_span_by_text(self, text):
        shadow_dom_element = self.chrome.driver.find_element(By.CSS_SELECTOR, "div[id='elements-content'] > div")
        shadow_root = self.__expand_shadow_element(shadow_dom_element)

        for line in shadow_root.find_elements(By.CSS_SELECTOR, "li"):
            if text in line.text:
                spans = line.find_elements(By.CSS_SELECTOR, "span")
                for span in spans:
                    if span.text == text:
                        return span
        return None

    def edit_text(self, old_text, new_text):
        """
        Edit text on element tab.
        :param old_text: Old text.
        :param new_text: New text.
        """
        span = self.__find_span_by_text(text=old_text)
        assert span is not None, "Failed to find element with text " + old_text
        actions = ActionChains(self.chrome.driver)
        actions.double_click(span).perform()
        self.chrome.driver.execute_script('arguments[0].innerHTML = "{0}";'.format(new_text), span)
        actions.double_click(span).perform()
        actions.send_keys(Keys.ENTER).perform()
        Log.info('Replace "{0}" with "{1}".'.format(old_text, new_text))
