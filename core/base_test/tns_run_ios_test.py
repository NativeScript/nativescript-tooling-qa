from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.device.simctl import Simctl


class TnsRunIOSTest(TnsTest):
    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)
        Simctl.uninstall_all(cls.sim)

    def setUp(self):
        TnsTest.setUp(self)
        Simctl.stop_all(self.sim)
