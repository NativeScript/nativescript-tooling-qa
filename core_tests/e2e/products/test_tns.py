import unittest

from core.utils.appium.appium_driver import AppiumDriver
from selenium.webdriver.common.by import By

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from data.sync.hello_world_js import sync_hello_world_js
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_paths import TnsPaths

APP_NAME = Settings.AppName.DEFAULT
BUNDLE_ID = TnsPaths.get_bundle_id(APP_NAME)


class TnsSmokeTests(TnsRunTest):
    appium = None

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=APP_NAME, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def setUp(self):
        TnsRunTest.setUp(self)

    def tearDown(self):
        TnsRunTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsRunTest.tearDownClass()

    def test_001_run_android_js(self):
        sync_hello_world_js(app_name=APP_NAME, platform=Platform.ANDROID, device=self.emu, instrumented=False)
        self.__test_appium(platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_002_run_ios_js(self):
        sync_hello_world_js(app_name=APP_NAME, platform=Platform.IOS, device=self.sim, instrumented=False)
        self.__test_appium(platform=Platform.IOS, device=self.sim)

    def __test_appium(self, platform, device):
        self.appium = AppiumDriver(platform=platform, device=device, bundle_id=BUNDLE_ID)
        if platform == Platform.ANDROID:
            self.appium.driver.find_element(By.XPATH, "//*[@text='TAP']").click()
            assert self.appium.driver.find_element(By.XPATH, "//*[@text='41 taps left']").is_displayed()
        if platform == Platform.IOS:
            self.appium.driver.find_element(By.ID, 'TAP').click()
            assert self.appium.driver.find_element(By.ID, '41 taps left').is_displayed()
