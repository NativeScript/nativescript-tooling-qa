"""
Test for specific needs of service tests.
"""
# pylint: disable=invalid-name
import os
import time


from core.base_test.tns_test import TnsTest
from core.utils.device.device import Device, Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from core.utils.wait import Wait
from core.settings.Settings import Emulators, Android, TEST_RUN_HOME, AppName
from data.templates import Template
from products.nativescript.tns import Tns

APP_NAME = AppName.DEFAULT


class AndroidServiceTests(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emulator = DeviceManager.Emulator.ensure_available(Emulators.DEFAULT)
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))

    def test_200_test_foreground_sticky_services_are_working(self):
        """
         https://github.com/NativeScript/android-runtime/issues/1347
        """
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1347', 'AndroidManifest.xml'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'src', 'main',
                               'AndroidManifest.xml'), True)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1347', 'sticky', 'app.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js'), True)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1347', 'main-view-model.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js'), True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)
        strings = ['Successfully synced application', 'on device', self.emulator.id]
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=240,
                                 period=5)
        assert test_result, "App not build correctly ! Logs: " + File.read(log.log_file)

        Device.wait_for_text(self.emulator, text='TAP', timeout=20)
        Device.click(self.emulator, text="TAP", case_sensitive=True)
        time.sleep(5)
        test_result = Wait.until(lambda: "Create Foreground Service!" in File.read(log.log_file), timeout=30,
                                 period=5)
        assert test_result, "OnCreate foreground service log not found! Logs: " + File.read(log.log_file)

        service_name = "com.nativescript.location.BackgroundService"
        service_info = Adb.get_active_services(self.emulator.id, service_name)
        assert service_name in service_info, "{0} service not found! Logs: {1}".format(service_name, service_info)

        pid = Adb.get_process_pid(self.emulator.id, "org.nativescript.TestApp")
        Adb.kill_process(self.emulator.id, "org.nativescript.TestApp")
        services = Adb.get_active_services(self.emulator.id)
        assert service_name in services, "{0} service not found! Logs: {1}".format(service_name, services)

        service_info = Adb.get_active_services(self.emulator.id, service_name)
        assert service_name in service_info, "{0} service not found! Logs: {1}".format(service_name, service_info)
        assert pid not in service_info, "{0} service with id {1} found! Logs: {2}".format(service_name, pid,
                                                                                          service_info)

    def test_201_test_foreground_not_sticky_services_are_working(self):
        """
         https://github.com/NativeScript/android-runtime/issues/1347
        """
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1347', 'AndroidManifest.xml'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'src', 'main',
                               'AndroidManifest.xml'), True)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1347', 'not_sticky', 'app.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js'), True)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1347', 'main-view-model.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js'), True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)
        strings = ['Successfully synced application', 'on device', self.emulator.id]
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=240,
                                 period=5)

        assert test_result, "App not build correctly ! Logs: " + File.read(log.log_file)
        Device.wait_for_text(self.emulator, text='TAP', timeout=20)
        Device.click(self.emulator, text="TAP", case_sensitive=True)
        time.sleep(5)
        test_result = Wait.until(lambda: "Create Foreground Service!" in File.read(log.log_file), timeout=30,
                                 period=5)
        assert test_result, "OnCreate foreground service log not found! Logs: " + File.read(log.log_file)

        service_name = "com.nativescript.location.BackgroundService"
        service_info = Adb.get_active_services(self.emulator.id, service_name)
        assert service_name in service_info, "{0} service not found! Logs: {1}".format(service_name, service_info)

        pid = Adb.get_process_pid(self.emulator.id, "org.nativescript.TestApp")
        Adb.kill_process(self.emulator.id, "org.nativescript.TestApp")
        services = Adb.get_active_services(self.emulator.id)
        assert service_name not in services, "{0} service found! Logs: {1}".format(service_name, services)

        service_info = Adb.get_active_services(self.emulator.id, service_name)
        assert service_name not in service_info, "{0} service found! Logs: {1}".format(service_name, service_info)
        assert pid not in service_info, "{0} service with id {1} found! Logs: {2}".format(service_name, pid,
                                                                                          service_info)

    def test_202_test_foreground_service_without_oncreate_method_is_working(self):
        """
         https://github.com/NativeScript/android-runtime/issues/1373
        """
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1347', 'AndroidManifest.xml'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'src', 'main',
                               'AndroidManifest.xml'), True)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1347', 'without_oncreate_method', 'app.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js'), True)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1347', 'main-view-model.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js'), True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)
        strings = ['Successfully synced application', 'on device', self.emulator.id]
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=240,
                                 period=5)
        assert test_result, "App not build correctly ! Logs: " + File.read(log.log_file)

        Device.wait_for_text(self.emulator, text='TAP', timeout=20)
        Device.click(self.emulator, text="TAP", case_sensitive=True)
        time.sleep(5)
        test_result = Wait.until(lambda: "Create Foreground Service!" in File.read(log.log_file), timeout=30,
                                 period=5)
        assert test_result, "OnCreate foreground service log not found! Logs: " + File.read(log.log_file)

        service_name = "com.nativescript.location.BackgroundService"
        service_info = Adb.get_active_services(self.emulator.id, service_name)
        assert service_name in service_info, "{0} service not found! Logs: {1}".format(service_name, service_info)

        pid = Adb.get_process_pid(self.emulator.id, "org.nativescript.TestApp")
        Adb.kill_process(self.emulator.id, "org.nativescript.TestApp")
        services = Adb.get_active_services(self.emulator.id)
        assert service_name not in services, "{0} service found! Logs: {1}".format(service_name, services)

        service_info = Adb.get_active_services(self.emulator.id, service_name)
        assert service_name not in service_info, "{0} service found! Logs: {1}".format(service_name, service_info)
        assert pid not in service_info, "{0} service with id {1} found! Logs: {2}".format(service_name, pid,
                                                                                          service_info)

    def test_203_test_foreground__intent_service_without_oncreate_method_is_working_api23(self):
        """
         https://github.com/NativeScript/android-runtime/issues/1426
        """
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1426', 'AndroidManifest.xml'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'src', 'main',
                               'AndroidManifest.xml'), True)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1426', 'app.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js'), True)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1426', 'main-view-model.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js'), True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)
        strings = ['Successfully synced application', 'on device', self.emulator.id]
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=240,
                                 period=5)
        assert test_result, "App not build correctly ! Logs: " + File.read(log.log_file)

        Device.wait_for_text(self.emulator, text='TAP', timeout=20)
        Device.click(self.emulator, text="TAP", case_sensitive=True)
        time.sleep(5)
        test_result = Wait.until(lambda: "Intent Handled!" in File.read(log.log_file), timeout=30,
                                 period=5)
        assert test_result, "Intent service is not working! Missing Log! Logs: " + File.read(log.log_file)

    def test_204_test_foreground__intent_service_without_oncreate_method_is_working_api28(self):
        """
         https://github.com/NativeScript/android-runtime/issues/1426
        """
        DeviceManager.Emulator.stop()
        self.emulator = DeviceManager.Emulator.ensure_available(Emulators.EMU_API_28)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1426', 'AndroidManifest.xml'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'src', 'main',
                               'AndroidManifest.xml'), True)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1426', 'app.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js'), True)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1426', 'main-view-model.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js'), True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)
        strings = ['Successfully synced application', 'on device', self.emulator.id]
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=240,
                                 period=5)
        assert test_result, "App not build correctly ! Logs: " + File.read(log.log_file)

        Device.wait_for_text(self.emulator, text='TAP', timeout=20, case_sensitive=True)
        Device.click(self.emulator, text="TAP", case_sensitive=True)
        time.sleep(5)
        test_result = Wait.until(lambda: "Intent Handled!" in File.read(log.log_file), timeout=30,
                                 period=5)
        assert test_result, "Intent service is not working! Missing Log! Logs: " + File.read(log.log_file)
        DeviceManager.Emulator.stop()
        self.emulator = DeviceManager.Emulator.ensure_available(Emulators.DEFAULT)
