import unittest

from core.base_test.tns_test import TnsTest
from core.enums.app_type import AppType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.device.simctl import Simctl
from data.legacy_app import LegacyApp
from data.sync.hello_world_ng import sync_hello_world_ng
from products.nativescript.tns import Tns


class NGRegressionTests(TnsTest):
    ng_app = Settings.AppName.DEFAULT + 'NG'

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            # Run regression tests on older iOS (since old modules might not be compatible with latest iOS).
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.SIM_IOS11)
            Simctl.uninstall_all(cls.sim)
        LegacyApp.create(app_name=cls.ng_app, app_type=AppType.NG)

    def setUp(self):
        TnsTest.setUp(self)
        Adb.open_home(self.emu.id)
        if Settings.HOST_OS is OSType.OSX:
            Simctl.stop_all(self.sim)

    def test_100_run_android(self):
        sync_hello_world_ng(app_name=self.ng_app, platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_101_run_ios(self):
        sync_hello_world_ng(app_name=self.ng_app, platform=Platform.IOS, device=self.sim)

    def test_200_build_android_release(self):
        if Settings.HOST_OS != OSType.WINDOWS:
            Tns.build_android(app_name=self.ng_app, release=True, bundle=True, aot=True, uglify=True, snapshot=True)
        else:
            Tns.build_android(app_name=self.ng_app, release=True, snapshot=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_201_build_ios_release(self):
        Tns.build_ios(app_name=self.ng_app, release=True, for_device=True, bundle=True, aot=True, uglify=True)
