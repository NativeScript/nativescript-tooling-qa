# pylint: disable=broad-except
import inspect
import os
import unittest

from core.base_test.test_context import TestContext
from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.appium.appium_driver import AppiumDriver
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder, File
from core.utils.gradle import Gradle
from core.utils.process import Process
from core.utils.xcode import Xcode
from products.nativescript.tns import Tns


# noinspection PyBroadException
class TnsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get class name and log
        TestContext.STARTED_PROCESSES = []
        TestContext.STARTED_DEVICES = []
        TestContext.TEST_APP_NAME = None
        TestContext.CLASS_NAME = cls.__name__
        try:
            for item in inspect.stack():
                TestContext.CLASS_NAME = item[0].f_locals['cls'].__name__
        except Exception:
            pass
        Log.test_class_start(class_name=TestContext.CLASS_NAME)

        # Kill processes
        Adb.restart()
        Tns.kill()
        Gradle.kill()
        TnsTest.kill_emulators()
        TnsTest.__clean_backup_folder_and_dictionary()
        # Ensure log folders are create
        Folder.create(Settings.TEST_OUT_HOME)
        Folder.create(Settings.TEST_OUT_LOGS)
        Folder.create(Settings.TEST_OUT_IMAGES)
        Folder.create(Settings.TEST_OUT_TEMP)

        # Set default simulator based on Xcode version
        if Settings.HOST_OS == OSType.OSX:
            if Xcode.get_version() < 10:
                Settings.Simulators.DEFAULT = Settings.Simulators.SIM_IOS11
            else:
                if Xcode.get_version() < 11:
                    Settings.Simulators.DEFAULT = Settings.Simulators.SIM_IOS12
                else:
                    Settings.Simulators.DEFAULT = Settings.Simulators.SIM_IOS13

    def setUp(self):
        TestContext.TEST_NAME = self._testMethodName
        Log.test_start(test_name=TestContext.TEST_NAME)
        Tns.kill()
        Gradle.kill()
        AppiumDriver.kill()
        TnsTest.__clean_backup_folder_and_dictionary()

    def tearDown(self):
        # pylint: disable=no-member

        # Kill processes
        Tns.kill()
        AppiumDriver.kill()
        Gradle.kill()
        Process.kill_all_in_context()
        TnsTest.restore_files()
        # Analise test result
        if Settings.PYTHON_VERSION < 3:
            # noinspection PyUnresolvedReferences
            result = self._resultForDoCleanups
        else:
            # noinspection PyUnresolvedReferences
            result = self._outcome.result

        outcome = 'FAILED'
        if result.errors == [] and result.failures == []:
            outcome = 'PASSED'
        else:
            self.get_screenshots()
            self.archive_apps()
        Log.test_end(test_name=TestContext.TEST_NAME, outcome=outcome)

    @classmethod
    def tearDownClass(cls):
        """
        Logic executed after all core_tests in class.
        """
        Tns.kill()
        TnsTest.kill_emulators()
        Process.kill_all_in_context()
        Folder.clean(Settings.TEST_OUT_TEMP)
        Log.test_class_end(TestContext.CLASS_NAME)

    @staticmethod
    def kill_emulators():
        DeviceManager.Emulator.stop()
        if Settings.HOST_OS is OSType.OSX:
            DeviceManager.Simulator.stop()
        TestContext.STARTED_DEVICES = []

    @staticmethod
    def get_screenshots():
        for device in TestContext.STARTED_DEVICES:
            try:
                base_path = os.path.join(Settings.TEST_OUT_IMAGES,
                                         TestContext.CLASS_NAME,
                                         TestContext.TEST_NAME)
                png_path = os.path.join(base_path, device.name + '.png')
                File.delete(png_path)
                device.get_screen(png_path)
            except AssertionError:
                Log.warning('Failed to take screenshot of {0}'.format(
                    device.id))

    @staticmethod
    def archive_apps():
        if TestContext.TEST_APP_NAME is not None:
            app_path = os.path.join(Settings.TEST_RUN_HOME,
                                    TestContext.TEST_APP_NAME)
            if Folder.exists(app_path):
                archive_path = os.path.join(
                    Settings.TEST_OUT_HOME, TestContext.CLASS_NAME,
                    TestContext.TEST_NAME, TestContext.TEST_APP_NAME)
                Log.info('Archive app under test at: {0}'.format(archive_path))

    @staticmethod
    def __clean_backup_folder_and_dictionary():
        TestContext.BACKUP_FILES.clear()
        Folder.clean(Settings.BACKUP_FOLDER)

    @staticmethod
    def restore_files():
        if TestContext.BACKUP_FILES:
            for file_path in TestContext.BACKUP_FILES:
                file_name = TestContext.BACKUP_FILES[file_path]
                file_temp_path = os.path.join(Settings.BACKUP_FOLDER,
                                              file_name)
                # delete file not from the original template
                if not File.exists(file_temp_path):
                    File.delete(file_path)
                else:
                    File.copy(file_temp_path, file_path)
                    File.delete(file_temp_path)
            TnsTest.__clean_backup_folder_and_dictionary()
        else:
            Log.info('No files to restore!')


if __name__ == '__main__':
    unittest.main()
