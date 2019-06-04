"""
Tests for app size ot {N} apps.
"""
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from data.templates import Template
from products.nativescript.tns import Tns


class AppSizeTests(TnsTest):
    js_app = Settings.AppName.DEFAULT + 'JS'
    ng_app = Settings.AppName.DEFAULT + 'NG'

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

        # Create JS app and copy to temp data folder
        Tns.create(app_name=cls.js_app, template=Template.HELLO_WORLD_JS.local_package, update=False)
        Tns.platform_add_android(app_name=cls.js_app, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.js_app, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Create NG app and copy to temp data folder
        Tns.create(app_name=cls.ng_app, template=Template.HELLO_WORLD_NG.local_package, update=False)
        Tns.platform_add_android(app_name=cls.ng_app, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.ng_app, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def test_001_android_app_size_js(self):
        Tns.build_android(self.js_app, release=True, bundle=True, aot=True, uglify=True, snapshot=True)

    def test_002_android_app_size_ng(self):
        Tns.build_android(self.ng_app, release=True, bundle=True, aot=True, uglify=True, snapshot=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_001_ios_app_size_js(self):
        Tns.build_ios(self.js_app, release=True, bundle=True, aot=True, uglify=True, for_device=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_002_ios_appandroi_size_ng(self):
        Tns.build_ios(self.ng_app, release=True, bundle=True, aot=True, uglify=True, for_device=True)
