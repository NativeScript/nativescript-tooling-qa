import unittest

from selenium.webdriver.common.by import By

import run_common
from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.appium.appium_driver import AppiumDriver
from data.changes import Changes
from data.templates import Template
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs
from products.nativescript.tns_paths import TnsPaths

APP_NAME = Settings.AppName.DEFAULT
BUNDLE_ID = TnsPaths.get_bundle_id(APP_NAME)


# noinspection PyMethodMayBeStatic
class AppiumTests(TnsRunTest):

    @classmethod
    def setUpClass(cls):
        run_common.prepare(clone_templates=True, install_ng_cli=False)
        TnsRunTest.setUpClass()
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=APP_NAME, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def setUp(self):
        TnsRunTest.setUp(self)

    def tearDown(self):
        self.appium.stop()
        TnsRunTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsRunTest.tearDownClass()

    def test_001_run_android_js(self):
        self.__test(platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_002_run_ios_js(self):
        self.__test(platform=Platform.IOS, device=self.sim)

    def __test(self, platform, device):
        result = Tns.run(app_name=APP_NAME, platform=platform, emulator=True, wait=False)
        strings = TnsLogs.run_messages(app_name=APP_NAME, platform=platform, run_type=RunType.UNKNOWN)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=240)
        device.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
        device.wait_for_text(text=Changes.JSHelloWord.XML.old_text)

        self.appium = AppiumDriver(platform=platform, device=device, bundle_id=BUNDLE_ID)
        if platform == Platform.ANDROID:
            self.appium.driver.find_element(By.XPATH, "//*[@text='TAP']").click()
            assert self.appium.driver.find_element(By.XPATH, "//*[@text='41 taps left']").is_displayed()
        if platform == Platform.IOS:
            self.appium.driver.find_element(By.ID, 'TAP').click()
            assert self.appium.driver.find_element(By.ID, '41 taps left').is_displayed()
