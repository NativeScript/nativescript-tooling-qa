"""
Tests for `tns devices` and `tns deploy` commands.
"""
import os

from core.base_test.tns_device_test import TnsDeviceTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.device.simctl import Simctl
from core.utils.file_utils import File, Folder
from data.changes import Changes, Sync
from data.templates import Template
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


# noinspection PyMethodMayBeStatic
class TnsRunOnDevices(TnsDeviceTest):
    emu = None
    sim = None
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)

    @classmethod
    def setUpClass(cls):
        TnsDeviceTest.setUpClass()

        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)
            Simctl.uninstall_all(cls.sim)

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsDeviceTest.setUp(self)
        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        for change in [Changes.JSHelloWord.CSS, Changes.JSHelloWord.XML, Changes.JSHelloWord.JS]:
            source_src = os.path.join(self.target_project_dir, 'app', os.path.basename(change.file_path))
            target_src = os.path.join(self.source_project_dir, change.file_path)
            File.clean(path=target_src)
            File.copy(source=source_src, target=target_src)

    def test_100_run_on_all_devices(self):
        result = Tns.run(app_name=self.app_name, platform=Platform.NONE)

        # Wait for logs
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID, run_type=RunType.FULL)
        for device in DeviceManager.get_devices(device_type=any):
            strings.append(device.id)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=360)

        # Verify it looks properly
        for device in DeviceManager.get_devices(device_type=any):
            device.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.old_text)

        # Edit JS file and verify changes are applied
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)

        # Verify logs
        file_name = os.path.basename(Changes.JSHelloWord.JS.file_path)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID, run_type=RunType.INCREMENTAL,
                                       file_name=file_name)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

        # Verify change is applied on all devices
        for device in DeviceManager.get_devices(device_type=any):
            device.wait_for_text(text=Changes.JSHelloWord.JS.new_text)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.new_text)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.new_text)

    def test_300_tns_run_on_specific_device(self):
        Adb.open_home(device_id=self.emu.id)
        Adb.open_home(device_id=self.android_device.id)
        result = Tns.run(app_name=self.app_name, platform=Platform.ANDROID, device=self.android_device.id)
        # Wait for logs
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID, run_type=RunType.UNKNOWN)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=300)

        # Verify it looks properly on device
        self.android_device.wait_for_text(text=Changes.JSHelloWord.JS.old_text)

        # Verify not working on emulator
        assert Changes.JSHelloWord.JS.old_text not in self.emu.get_text()
        assert self.emu.id not in File.read(result.log_file)
