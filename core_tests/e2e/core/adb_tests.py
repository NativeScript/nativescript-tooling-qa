import os
import time

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File


# noinspection PyMethodMayBeStatic
class AdbTests(TnsTest):
    emu = None
    apk_path = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        DeviceManager.Emulator.stop()
        cls.emu = DeviceManager.Emulator.start(Settings.Emulators.DEFAULT)
        url = "https://github.com/webdriverio/native-demo-app/releases/download/0.2.1/Android-NativeDemoApp-0.2.1.apk"
        File.download_file("test.apk", url)
        cls.apk_path = os.path.join(Settings.TEST_RUN_HOME, "test.apk")

    def setUp(self):
        TnsTest.setUp(self)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_01_adb_get_source(self):
        page_source = Adb.get_page_source(device_id=self.emu.id)
        assert '</hierarchy>' in page_source

    def test_02_adb_get_screen(self):
        path = os.path.join(Settings.TEST_OUT_HOME, 'temp.png')
        File.delete(path)
        Adb.get_screen(device_id=self.emu.id, file_path=path)

    def test_03_get_active_services(self):
        services = Adb.get_active_services(self.emu.id)
        assert services != ""
        assert "ACTIVITY MANAGER SERVICES" in services

    def test_03_get_process_pid(self):
        services = Adb.get_process_pid(self.emu.id, "com.android.systemui")
        assert services != ""

    def test_04_install(self):
        Adb.install(self.apk_path, self.emu.id)
        Adb.uninstall("com.wdiodemoapp", self.emu.id)

    def test_05_start_application(self):
        if not Adb.is_application_installed(self.emu.id, "com.wdiodemoapp"):
            Adb.install(self.apk_path, self.emu.id)
        Adb.start_application(self.emu.id, "com.wdiodemoapp")
        Adb.uninstall("com.wdiodemoapp", self.emu.id)

    def test_06_kill_process(self):
        if not Adb.is_application_installed(self.emu.id, "com.wdiodemoapp"):
            Adb.install(self.apk_path, self.emu.id)
        Adb.start_application(self.emu.id, "com.wdiodemoapp")
        time.sleep(5)
        Adb.kill_process(self.emu.id, "com.wdiodemoapp")
        service_info = Adb.get_active_services(self.emu.id, "com.wdiodemoapp").replace("\r", "").replace("\n", "")
        pid = Adb.get_process_pid(self.emu.id, "com.wdiodemoapp")
        assert pid == "", "Application not killed! PID " + pid
        error_message = "Service is not killed. Log: " + service_info
        assert service_info == "ACTIVITY MANAGER SERVICES (dumpsys activity services)  (nothing)", error_message
        Adb.uninstall("com.wdiodemoapp", self.emu.id)
