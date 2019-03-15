"""
Test for specific needs Android ABI Split.
"""
# pylint: disable=duplicate-code
import os

from core.base_test.tns_test import TnsTest
from core.enums.device_type import DeviceType
from core.settings.Settings import TEST_RUN_HOME, AppName
from core.utils.file_utils import Folder
from core.utils.device.device import Device, Adb
from data.templates import Template
from products.nativescript.app import App
from products.nativescript.tns import Tns
from runtime_helpers.abi_split_helper import AbiSplitHelper

APP_NAME = AppName.DEFAULT


class AbiSplitTestsForArmDevices(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_NG.local_package)
        json = App.get_package_json(app_name=APP_NAME)
        cls.app_id = json['nativescript']['id']
        devices = Adb.get_ids(include_emulators=False)
        device_id = None
        for device in devices:
            device_id = device
        if device_id is not None:
            cls.device = Device(id=device_id, name=device_id, type=DeviceType.ANDROID,
                                version=Adb.get_version(device_id))
        Adb.uninstall(cls.app_id, device_id, assert_success=False)

    def test_201_run_app_with_abi_split_and_snapshot_on_32_phone(self):
        """
         Test if the apk for arm devices is working
         https://github.com/NativeScript/android-runtime/issues/1234
        """
        AbiSplitHelper.assert_apk(
            os.path.join(TEST_RUN_HOME, "Test_apks",
                         "app-armeabi-v7a-release.apk"),
            self.device, self.app_id, os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'images',
                                                   'ARM-32-Phone', "abi-split-32-phone.png"))
