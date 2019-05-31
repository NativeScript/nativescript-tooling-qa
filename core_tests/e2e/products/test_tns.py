import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from data.sync.hello_world_js import sync_hello_world_js
from data.templates import Template
from products.nativescript.tns import Tns

APP_NAME = Settings.AppName.DEFAULT


class TnsSmokeTests(TnsRunTest):

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=False)
        Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=APP_NAME, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def test_001_run_android_js(self):
        sync_hello_world_js(app_name=APP_NAME, platform=Platform.ANDROID, device=self.emu, instrumented=False)

    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_002_run_ios_js(self):
        sync_hello_world_js(app_name=APP_NAME, platform=Platform.IOS, device=self.sim, instrumented=False)
