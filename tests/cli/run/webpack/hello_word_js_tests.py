import os
import unittest

from core.base_test.base_test import BaseTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder, File
from core.utils.wait import Wait
from data.changes import Changes, Sync
from data.const import Colors
from data.templates import Template
from products.nativescript.app import App
from products.nativescript.tns import Tns


class TnsRunJSTests(BaseTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)
    emu = None
    sim = None

    @classmethod
    def setUpClass(cls):
        BaseTest.setUpClass()

        # Boot emulator and simulator
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS == OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        App.ensure_webpack_installed(app_name=cls.app_name)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        BaseTest.setUp(self)
        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        source_src = os.path.join(self.target_project_dir, 'app')
        target_src = os.path.join(self.source_project_dir, 'app')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)

    @classmethod
    def tearDownClass(cls):
        BaseTest.tearDownClass()


class RunAndroidJSTests(TnsRunJSTests):
    def test_100_run_android(self):
        sync(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu)

    def test_200_run_android_bundle(self):
        sync(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True)

    def test_300_run_android_bundle_aot(self):
        sync(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True, aot=True)

    def test_310_run_android_bundle_uglify(self):
        sync(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True, uglify=True)

    def test_320_run_android_bundle_aot_and_uglify(self):
        sync(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True, aot=True, uglify=True)

    def test_390_run_android_bundle_aot_uglify_snapshot(self):
        sync(app_name=self.app_name, platform=Platform.ANDROID, device=self.emu, bundle=True, aot=True, uglify=True,
             snapshot=True)


@unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
class RunIOSJSTests(TnsRunJSTests):
    def test_100_run_ios(self):
        sync(app_name=self.app_name, platform=Platform.IOS, device=self.sim)

    def test_200_run_ios_bundle(self):
        sync(app_name=self.app_name, platform=Platform.IOS, device=self.sim, bundle=True)

    def test_300_run_ios_bundle_aot(self):
        sync(app_name=self.app_name, platform=Platform.IOS, device=self.sim, bundle=True, aot=True)

    def test_310_run_ios_bundle_uglify(self):
        sync(app_name=self.app_name, platform=Platform.IOS, device=self.sim, bundle=True, uglify=True)

    def test_320_run_ios_bundle_aot_and_uglify(self):
        sync(app_name=self.app_name, platform=Platform.IOS, device=self.sim, bundle=True, aot=True, uglify=True)


def sync(app_name, platform, device, bundle=False, uglify=False, aot=False, snapshot=False):
    result = Tns.run(app_name=app_name, platform=platform, device=device.id, wait=False,
                     bundle=bundle, uglify=uglify, aot=aot, snapshot=snapshot)

    # Verify if snapshot flag is passed it it skipped
    if snapshot:
        msg = "Bear in mind that snapshot is only available in release builds and is NOT available on Windows systems"
        skip_snapshot = Wait.until(lambda: 'Stripping the snapshot flag' in File.read(result.log_file), timeout=180)
        assert skip_snapshot, "Not message that snapshot is skipped."
        assert msg in File.read(result.log_file), "No message that snapshot is NOT available on Windows."

    # Verify it looks properly
    device.wait_for_text(text=Changes.JSHelloWord.JS.old_value, timeout=180, retry_delay=5)
    device.wait_for_text(text=Changes.JSHelloWord.XML.old_value)
    blue_count = device.get_pixels_by_color(color=Colors.LIGHT_BLUE_ANDROID)
    assert blue_count > 100, 'Failed to find blue color on {0}'.format(device.name)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)

    # Edit JS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=Changes.JSHelloWord.JS)
    device.wait_for_text(text=Changes.JSHelloWord.JS.new_value)

    # Edit XML file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=Changes.JSHelloWord.XML)
    device.wait_for_text(text=Changes.JSHelloWord.XML.new_value)
    device.wait_for_text(text=Changes.JSHelloWord.JS.new_value)

    # Edit CSS file and verify changes are applied
    Sync.replace(app_name=app_name, change_set=Changes.JSHelloWord.CSS)
    device.wait_for_text(text=Changes.JSHelloWord.XML.new_value)
    device.wait_for_text(text=Changes.JSHelloWord.JS.new_value)
    device.wait_for_color(color=Colors.LIGHT_BLUE_ANDROID, pixel_count=blue_count * 2, delta=25)

    # Revert all the changes
    Sync.revert(app_name=app_name, change_set=Changes.JSHelloWord.JS)
    device.wait_for_text(text=Changes.JSHelloWord.JS.old_value)
    device.wait_for_text(text=Changes.JSHelloWord.XML.new_value)

    Sync.revert(app_name=app_name, change_set=Changes.JSHelloWord.XML)
    device.wait_for_text(text=Changes.JSHelloWord.XML.old_value)
    device.wait_for_text(text=Changes.JSHelloWord.JS.old_value)

    Sync.revert(app_name=app_name, change_set=Changes.JSHelloWord.CSS)
    device.wait_for_color(color=Colors.LIGHT_BLUE_ANDROID, pixel_count=blue_count)
    device.wait_for_text(text=Changes.JSHelloWord.XML.old_value)
    device.wait_for_text(text=Changes.JSHelloWord.JS.old_value)

    # Assert final and initial states are same
    device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)
