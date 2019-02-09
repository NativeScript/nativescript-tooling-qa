from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager


class TnsRunIOSTest(TnsTest):
    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)
