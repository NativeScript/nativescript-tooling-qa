import os

from core.base_test.tns_test import TnsTest
from core.log.log import Log
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
# noinspection PyMethodMayBeStatic
from core.utils.file_utils import File


class AdbTests(TnsTest):
    emu = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        DeviceManager.Emulator.stop()
        cls.emu = DeviceManager.Emulator.start(Settings.Emulators.DEFAULT, wipe_data=False)

    def setUp(self):
        TnsTest.setUp(self)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_01_adb_get_source(self):
        page_source = Adb.get_page_source(id=self.emu.id)
        assert '</hierarchy>' in page_source

    def test_02_adb_get_screen(self):
        path = os.path.join(Settings.TEST_OUT_HOME, 'temp.png')
        File.clean(path)
        Adb.get_screen(id=self.emu.id, file_path=path)
