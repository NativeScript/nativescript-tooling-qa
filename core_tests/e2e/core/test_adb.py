import os
import time

from core.base_test.tns_run_android_test import TnsRunAndroidTest
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.file_utils import File
from core.utils.process import Process


# noinspection PyMethodMayBeStatic
class AdbTests(TnsRunAndroidTest):
    emu = None
    apk_path = None

    @classmethod
    def setUpClass(cls):
        TnsRunAndroidTest.setUpClass()
        url = "https://github.com/webdriverio/native-demo-app/releases/download/0.2.1/Android-NativeDemoApp-0.2.1.apk"
        cls.apk_path = os.path.join(Settings.TEST_RUN_HOME, "test.apk")
        File.delete(path=cls.apk_path)
        File.download_file("test.apk", url)

    def setUp(self):
        TnsRunAndroidTest.setUp(self)

    def tearDown(self):
        TnsRunAndroidTest.tearDown(self)
        Process.kill(proc_name="adb")

    @classmethod
    def tearDownClass(cls):
        TnsRunAndroidTest.tearDownClass()

    def test_01_adb_get_source(self):
        page_source = Adb.get_page_source(device_id=self.emu.id)
        assert '</hierarchy>' in page_source

    def test_02_adb_get_screen(self):
        path = os.path.join(Settings.TEST_OUT_HOME, 'temp.png')
        File.delete(path)
        Adb.get_screen(device_id=self.emu.id, file_path=path)

    def test_03_get_active_services(self):
        services = Adb.get_active_services(self.emu.id)
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
