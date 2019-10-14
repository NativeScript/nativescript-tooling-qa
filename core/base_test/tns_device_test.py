from core.base_test.tns_test import TnsTest
from core.enums.device_type import DeviceType
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager


class TnsDeviceTest(TnsTest):
    android_device = None
    ios_device = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.android_device = DeviceManager.get_devices(
            device_type=DeviceType.ANDROID)[0]
        assert cls.android_device is not None, 'Failed to find android device.'
        if Settings.HOST_OS == OSType.OSX:
            cls.ios_device = DeviceManager.get_devices(
                device_type=DeviceType.IOS)[0]
            assert cls.ios_device is not None, 'Failed to find ios device.'

    def setUp(self):
        TnsTest.setUp(self)
        Adb.open_home(device_id=self.android_device.id)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
