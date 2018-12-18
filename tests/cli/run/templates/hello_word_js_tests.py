import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder
from data.sync_helpers import SyncHelpers
from data.templates import Template
from products.nativescript.tns import Tns
from utils.device.adb import Adb


class TnsRunJSTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)
    emu = None
    sim = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

        # Boot emulator and simulator
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS == OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsTest.setUp(self)
        Adb.open_home(self.emu.id)

        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        source_src = os.path.join(self.target_project_dir, 'app')
        target_src = os.path.join(self.source_project_dir, 'app')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()


class RunAndroidJSTests(TnsRunJSTests):
    def test_100_run_android(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu)

    def test_200_run_android_bundle(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True)

    def test_210_run_android_bundle_hmr(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True,
                                        hmr=True)

    def test_300_run_android_bundle_aot(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True,
                                        aot=True)

    def test_310_run_android_bundle_uglify(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True,
                                        uglify=True)

    def test_320_run_android_bundle_aot_and_uglify(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True,
                                        aot=True, uglify=True)

    def test_390_run_android_bundle_aot_uglify_snapshot(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True,
                                        aot=True, uglify=True,
                                        snapshot=True)


@unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
class RunIOSJSTests(TnsRunJSTests):
    def test_100_run_ios(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.IOS, device=self.sim)

    def test_200_run_ios_bundle(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.IOS, device=self.sim, bundle=True)

    def test_210_run_ios_bundle_hmr(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.IOS, device=self.sim, bundle=True,
                                        hmr=True)

    def test_300_run_ios_bundle_aot(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.IOS, device=self.sim, bundle=True,
                                        aot=True)

    def test_310_run_ios_bundle_uglify(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.IOS, device=self.sim, bundle=True,
                                        uglify=True)

    def test_320_run_ios_bundle_aot_and_uglify(self):
        SyncHelpers.sync_hello_world_js(app_name=self.app_name, platform=Platform.IOS, device=self.sim, bundle=True,
                                        aot=True, uglify=True)
