import os
import unittest

from core.enums.device_type import DeviceType
from core.settings import Settings
from core.utils.device.device import Device
from core.utils.file_utils import File


# noinspection PyMethodMayBeStatic
class RunTests(unittest.TestCase):

    def test_01_get_device_logs_of_missing_device(self):
        for device_type in [DeviceType.EMU, DeviceType.ANDROID, DeviceType.IOS]:
            device = Device(id='123', name='not_existing_device', type=device_type, version=7.0)
            log = device.get_log()
            File.write(path=os.path.join(Settings.TEST_OUT_LOGS, device.name + '.log'), text=log)
