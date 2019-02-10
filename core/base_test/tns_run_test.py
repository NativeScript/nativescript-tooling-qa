from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.device.simctl import Simctl


class TnsRunTest(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)
            Simctl.uninstall_all(cls.sim)

    def setUp(self):
        TnsTest.setUp(self)
        Adb.open_home(self.emu.id)
        if Settings.HOST_OS is OSType.OSX:
            Simctl.stop_all(self.sim)
