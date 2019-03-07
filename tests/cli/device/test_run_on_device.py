"""
Tests for `tns devices` and `tns deploy` commands.
"""
import os

from core.base_test.tns_device_test import TnsDeviceTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from data.changes import Changes, Sync
from data.templates import Template
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


# noinspection PyMethodMayBeStatic
class TnsRunOnDevices(TnsDeviceTest):
    app_name = Settings.AppName.DEFAULT

    @classmethod
    def setUpClass(cls):
        TnsDeviceTest.setUpClass()

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def test_100_run_on_all_devices(self):
        result = Tns.run(app_name=self.app_name, platform=Platform.NONE, bundle=True, hmr=True)

        # Wait for logs
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID, run_type=RunType.FULL,
                                       bundle=True, hmr=True)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=300)

        # Verify it looks properly
        for device in DeviceManager.get_devices(device_type=any):
            device.wait_for_text(text=Changes.JSHelloWord.JS.old_text)
            device.wait_for_text(text=Changes.JSHelloWord.XML.old_text)

        # Edit JS file and verify changes are applied
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)

        # Verify logs
        file_name = os.path.basename(Changes.JSHelloWord.JS.file_path)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=Platform.ANDROID, run_type=RunType.INCREMENTAL,
                                       bundle=True, hmr=True, file_name=file_name)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)

        # Verify change is applied on all devices
        for device in DeviceManager.get_devices(device_type=any):
            device.wait_for_text(text=Changes.JSHelloWord.JS.new_text)
