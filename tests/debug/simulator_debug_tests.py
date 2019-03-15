"""
Test for specific needs of Debug tests.
"""
# pylint: disable=duplicate-code
import os
import time

from selenium.webdriver.common.by import By
from core.base_test.tns_test import TnsTest
from core.utils.chrome import Chrome
from core.utils.device.device import Device
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from core.utils.wait import Wait
from core.utils.debug import Debug
from core.settings.Settings import Simulators, IOS, TEST_RUN_HOME, AppName
from core.enums.platform_type import Platform
from data.templates import Template
from products.nativescript.tns import Tns

APP_NAME = AppName.DEFAULT


class EmulatorDebugTests(TnsTest):
    chrome = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.simulator = DeviceManager.Simulator.ensure_available(Simulators.DEFAULT)
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_ios(APP_NAME, framework_path=IOS.FRAMEWORK_PATH)
        cls.chrome = Chrome()
        cls.log = Tns.debug(APP_NAME, Platform.IOS, device=cls.simulator.id, wait=False, verify=False)
        strings = ['Project successfully built', 'Successfully installed on device with identifier', cls.simulator.id,
                   "chrome-devtools://devtools/bundled/inspector.html?experiments=true&ws=localhost:41000"]
        test_result = Wait.until(lambda: all(string in File.read(cls.log.log_file) for string in strings), timeout=240,
                                 period=5)
        assert test_result, "Debug built is not successful! Log: " + File.read(cls.log.log_file)
        test_result = Wait.until(lambda: Device.is_text_visible(cls.simulator, "TAP", True), timeout=60,
                                 period=5)
        assert test_result, "TAP Button is missing on the device"
        cls.chrome.open("chrome-devtools://devtools/bundled/inspector.html?experiments=true&ws=localhost:41000")

    def setUp(self):
        Tns.kill()
        self.log = Tns.debug(APP_NAME, Platform.IOS, device=self.simulator.id, wait=False, verify=False)
        strings = ['Successfully synced application', 'on device', self.simulator.id,
                   "chrome-devtools://devtools/bundled/inspector.html?experiments=true&ws=localhost:41000"]
        test_result = Wait.until(lambda: all(string in File.read(self.log.log_file) for string in strings), timeout=240,
                                 period=5)
        assert test_result, "Debug built is not successful! Log: " + File.read(self.log.log_file)
        test_result = Wait.until(lambda: Device.is_text_visible(self.simulator, "TAP", True), timeout=60,
                                 period=5)
        assert test_result, "TAP Button is missing on the device"
        self.debug = Debug(self.chrome.driver)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        cls.chrome.kill()

    def test_100_debug_session_could_be_start_for_simulator(self):
        """
         Test debug session could be start for simulator
        """
        self.debug.get_element_in_shadow_dom(By.ID, "tab-elements").click()
        element_to_find = '<ActionBar icon title="My App" className="action-bar"></ActionBar>'
        title_span = self.debug.get_element_by_css_selector_and_text("span",
                                                                     element_to_find, self.debug.content)
        assert title_span is not None, "Session is not opened successfully! App title is missing in Elements tab!"

    def test_101_console_log_is_shown_in_dev_tools_console_for_simulator(self):
        """
         Test console log is shown in devTools console for simulator
        """
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'debug', 'files', "console_log",
                                 'main-view-model.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js)
        strings = ['Successfully synced application ',
                   "chrome-devtools://devtools/bundled/inspector.html?experiments=true&ws=localhost:41000"]
        test_result = Wait.until(lambda: all(string in File.read(self.log.log_file) for string in strings), timeout=120,
                                 period=5)
        time.sleep(10)
        Device.clear_log(self.simulator)
        assert test_result, "Change not applied correctly! Log: " + File.read(self.log.log_file)
        test_result = Wait.until(lambda: Device.is_text_visible(self.simulator, "TAP", True), timeout=60,
                                 period=5)
        assert test_result, "TAP Button is missing on the device"
        self.debug = Debug(self.chrome.driver)
        self.debug.get_element_in_shadow_dom(By.ID, "tab-console").click()
        test_result = Wait.until(lambda: Device.is_text_visible(self.simulator, "TAP", True), timeout=60,
                                 period=5)
        assert test_result, "TAP Button is missing on the device"
        Device.click(self.simulator, "TAP", True)
        console_element = self.chrome.driver.find_element(By.ID, "console-messages")
        test_result = Wait.until(
            lambda: self.debug.get_element_by_css_selector_and_text("span", ": Test Debug!", console_element,
                                                                    True) is not None, timeout=20, period=5)
        assert test_result, "Console log is not shown in DevTools!"
        error_message = "Console log not found in device logs! Logs: " + Device.get_log(self.simulator)
        assert Device.is_text_in_log(self.simulator, "Test Debug!"), error_message
        assert "Test Debug!" in File.read(self.log.log_file), "Console log not found in tns logs! Logs: " + File.read(
            self.log.log_file)
