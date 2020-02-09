"""
Tests for migrating Angular web project to shared project.
Note: Those tests are ordered (can not run last if first fails).
"""
# pylint: disable=unused-argument
import os
import unittest

from parameterized import parameterized
from selenium.webdriver.common.by import By

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.chrome.chrome import Chrome
from products.angular.ng import NG, DEFAULT_WEB_URL
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
@unittest.skip("No support for Angular 9.")
class MigrateWebToMobileTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    app_folder = os.path.join(Settings.TEST_RUN_HOME, app_name)
    chrome = None

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        NG.kill()
        NG.new(collection=None, project=cls.app_name)
        cls.chrome = Chrome()

    def setUp(self):
        TnsRunTest.setUp(self)
        NG.kill()

    def tearDown(self):
        NG.kill()
        TnsRunTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        cls.chrome.kill()
        TnsRunTest.tearDownClass()

    def test_01_ng_serve_web(self):
        self.ng_serve(prod=False)
        self.chrome.open(url='https://google.com/ncr')  # change url to be sure next serve do not assert previous serve
        self.ng_serve(prod=True)

    def test_02_add_nativescript(self):
        # Add {N} to existing web project
        result = NG.add(project=self.app_name, schematics_package=Settings.Packages.NS_SCHEMATICS)

        # Verify output
        assert 'Adding @nativescript/schematics to angular.json' in result.output
        assert 'Adding {N} files' in result.output
        assert 'Adding NativeScript specific exclusions to .gitignore' in result.output
        assert 'Adding NativeScript run scripts to package.json' in result.output
        assert 'Modifying web tsconfig' in result.output
        assert 'Adding Sample Shared Component' in result.output
        assert 'Adding npm dependencies' in result.output

        # NG Serve (to check web is not broken by {N})
        self.ng_serve(prod=False)
        self.chrome.open(url='https://google.com/ncr')  # change url to be sure next serve do not assert previous serve
        self.ng_serve(prod=True)

    # noinspection PyUnusedLocal
    @parameterized.expand([
        ('android', Platform.ANDROID, False, False),
        ('ios', Platform.IOS, False, False),
        ('android_aot', Platform.ANDROID, True, False),
        ('ios_aot', Platform.IOS, True, False),
        ('android_aot_uglify', Platform.ANDROID, True, True),
        ('ios_aot_uglify', Platform.IOS, True, True),
    ])
    def test_10_run(self, name, platform, aot, uglify):
        if (platform == Platform.IOS) and (Settings.HOST_OS == OSType.WINDOWS or Settings.HOST_OS == OSType.LINUX):
            unittest.skip('Can not run iOS tests on Windows or Linux.')
        else:
            ng_app_text = 'auto-generated works!'
            Tns.run(platform=platform, app_name=self.app_name, aot=aot, uglify=uglify, emulator=True)
            if platform == Platform.ANDROID:
                self.emu.wait_for_text(text=ng_app_text, timeout=300)
            if platform == Platform.IOS:
                self.sim.wait_for_text(text=ng_app_text, timeout=300)

    def ng_serve(self, prod=False):
        NG.serve(project=self.app_name, prod=prod)
        self.chrome.open(DEFAULT_WEB_URL)
        if "Angular CLI: 8.3" in NG.exec_command(command="version").output:
            element = self.chrome.driver.find_element(By.XPATH, '//*[contains(text(), "TestApp app is running!")]')
        else:
            element = self.chrome.driver.find_element(By.XPATH, '//*[contains(text(), "Welcome")]')
        assert element.is_displayed(), 'Failed to serve default NG project.'
        Log.info('Default NG web project loaded!')
        NG.kill()
