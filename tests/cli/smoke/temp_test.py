from core.base_test.tns_run_test import TnsRunTest
from core.enums.device_type import DeviceType
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager


class TempTest(TnsRunTest):
    android_device = None
    ios_device = None

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        cls.android_device = DeviceManager.get_devices(device_type=DeviceType.ANDROID)[0]
        assert cls.android_device is not None, 'Failed to find android device.'
        if Settings.HOST_OS == OSType.OSX:
            cls.ios_device = DeviceManager.get_devices(device_type=DeviceType.IOS)[0]
            assert cls.ios_device is not None, 'Failed to find ios device.'

    def test_001_run_android_js(self):
        assert False
