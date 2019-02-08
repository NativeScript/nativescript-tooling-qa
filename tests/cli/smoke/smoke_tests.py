import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from data.sync.hello_world_js import sync_hello_world_js
from data.sync.hello_world_ng import sync_hello_world_ng
from data.templates import Template
from products.nativescript.tns import Tns


class SmokeTests(TnsTest):
    js_app = Settings.AppName.DEFAULT + 'JS'
    ng_app = Settings.AppName.DEFAULT + 'NG'

    emu = None
    sim = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

        # Boot emulator and simulator
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS == OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

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

    def test_001_run_android_js(self):
        sync_hello_world_js(app_name=self.js_app, platform=Platform.ANDROID, device=self.emu, instrumented=False)

    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_002_run_ios_js(self):
        sync_hello_world_js(app_name=self.js_app, platform=Platform.IOS, device=self.sim, instrumented=False)

    def test_100_run_android_ng(self):
        sync_hello_world_ng(app_name=self.ng_app, platform=Platform.ANDROID, device=self.emu, bundle=True,
                            instrumented=False)

    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_101_run_ios_ng(self):
        sync_hello_world_ng(app_name=self.ng_app, platform=Platform.IOS, device=self.sim, bundle=True,
                            instrumented=False)
