import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.app_type import AppType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from data.legacy_app import LegacyApp
from data.sync.hello_world_js import sync_hello_world_js
from products.nativescript.tns import Tns


class JSRegressionTests(TnsRunTest):
    js_app = Settings.AppName.DEFAULT + 'JS'

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        LegacyApp.create(app_name=cls.js_app, app_type=AppType.JS)

    def test_100_run_android(self):
        sync_hello_world_js(app_name=self.js_app, platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_101_run_ios(self):
        sync_hello_world_js(app_name=self.js_app, platform=Platform.IOS, device=self.sim)

    def test_200_build_android_release(self):
        if Settings.HOST_OS != OSType.WINDOWS:
            Tns.build_android(app_name=self.js_app, release=True, bundle=True, aot=True, uglify=True, snapshot=True)
        else:
            Tns.build_android(app_name=self.js_app, release=True, snapshot=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_201_build_ios_release(self):
        Tns.build_ios(app_name=self.js_app, release=True, for_device=True, bundle=True, aot=True, uglify=True)
