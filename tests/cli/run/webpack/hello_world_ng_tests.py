import os
import unittest

from core.base_test.base_test import BaseTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder
from data.changes import Changes, Sync
from data.const import Colors
from data.templates import Template
from products.nativescript.app import App
from products.nativescript.tns import Tns


class TnsRunNGTests(BaseTest):
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
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_NG.local_package, update=True)
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
        source_src = os.path.join(self.target_project_dir, 'src')
        target_src = os.path.join(self.source_project_dir, 'src')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)

    @classmethod
    def tearDownClass(cls):
        BaseTest.tearDownClass()


class RunAndroidNGTests(TnsRunNGTests):
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


@unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
class RunIOSNGTests(TnsRunNGTests):
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


def sync(app_name, platform, device, bundle=False, uglify=False, aot=False):
    Tns.run(app_name=app_name, platform=platform, device=device.id, wait=False, bundle=bundle, aot=aot, uglify=uglify)

    # Verify it looks properly
    verify_initial_state(device)
    initial_state = os.path.join(Settings.TEST_OUT_IMAGES, device.name, 'initial_state.png')
    device.get_screen(path=initial_state)

    # Apply changes
    apply_ts(app_name=app_name, device=device)
    apply_html(app_name=app_name, device=device)
    apply_css(app_name=app_name, device=device)

    # Revert changes
    revert_html(app_name=app_name, device=device)
    revert_ts(app_name=app_name, device=device)
    revert_css(app_name=app_name, device=device)

    # Assert final and initial states are same
    device.screen_match(expected_image=initial_state, tolerance=1.0, timeout=30)


def verify_initial_state(device):
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_value, timeout=60, retry_delay=5)
    device.wait_for_main_color(color=Colors.WHITE)


def apply_ts(app_name, device):
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.new_value)


def apply_html(app_name, device):
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
    for number in ["8", "9"]:
        device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_value)


def apply_css(app_name, device):
    Sync.replace(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
    device.wait_for_main_color(color=Colors.DARK)
    for number in ["8", "9"]:
        device.wait_for_text(text=number)
    assert not device.is_text_visible(text=Changes.NGHelloWorld.TS.new_value)


def revert_html(app_name, device):
    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.HTML)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.new_value)


def revert_ts(app_name, device):
    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.TS)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_value)
    device.wait_for_main_color(color=Colors.DARK)


def revert_css(app_name, device):
    Sync.revert(app_name=app_name, change_set=Changes.NGHelloWorld.CSS)
    device.wait_for_main_color(color=Colors.WHITE)
    device.wait_for_text(text=Changes.NGHelloWorld.TS.old_value)
