import unittest

from core.base_test.tns_test import TnsTest
from core.enums.app_type import AppType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from data.sync.hello_world_ng import sync_hello_world_ng
from products.nativescript.tns import Tns
from tests.cli.regression.create_legacy_app import create


class NGRegressionTests(TnsTest):
    emu = None
    sim = None
    ng_app = Settings.AppName.DEFAULT + 'NG'

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

        # Boot emulator and simulator
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS == OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

        # Create legacy NG app
        create(app_name=cls.ng_app, app_type=AppType.NG)

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_100_run_android(self):
        sync_hello_world_ng(app_name=self.ng_app, platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_101_run_ios(self):
        sync_hello_world_ng(app_name=self.ng_app, platform=Platform.IOS, device=self.sim)

    def test_200_build_android_release(self):
        Tns.build_android(app_name=self.ng_app, release=True, bundle=True, aot=True, uglify=True, snapshot=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_201_build_ios_release(self):
        Tns.build_ios(app_name=self.ng_app, release=True, for_device=True, bundle=True, aot=True, uglify=True)
