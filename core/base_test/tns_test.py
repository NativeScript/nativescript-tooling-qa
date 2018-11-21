import inspect
import os
import unittest

from core.base_test.test_context import TestContext
from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder
from core.utils.gradle import Gradle
from core.utils.process import Process
from core.utils.xcode import Xcode
from products.nativescript.tns import Tns


class TnsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get class name and log
        caller_class = inspect.stack()[1][0].f_locals['cls'].__name__
        Log.test_class_start(class_name=caller_class)

        # Kill processes
        Adb.restart()
        Tns.kill()
        Gradle.kill()
        TnsTest.kill_emulators()

        # Ensure log folders are create
        Folder.create(Settings.TEST_OUT_HOME)
        Folder.create(Settings.TEST_OUT_LOGS)
        Folder.create(Settings.TEST_OUT_IMAGES)

        # Set default simulator based on Xcode version
        if Settings.HOST_OS == OSType.OSX:
            if Xcode.get_version() < 10:
                Settings.Simulators.DEFAULT = Settings.Simulators.SIM_IOS11
            else:
                Settings.Simulators.DEFAULT = Settings.Simulators.SIM_IOS12

    def setUp(self):
        TestContext.TEST_NAME = self._testMethodName
        Log.test_start(test_name=TestContext.TEST_NAME)
        Tns.kill()
        Gradle.kill()

    def tearDown(self):
        Tns.kill()

        for process in TestContext.Processes.STARTED_PROCESSES:
            Log.info("Kill Process: " + os.linesep + process.commandline)
            Process.kill_pid(process.pid)

        # Analise test result
        result = self._resultForDoCleanups
        outcome = 'FAILED'
        if result.errors == [] and result.failures == []:
            outcome = 'PASSED'

        Log.test_end(test_name=TestContext.CurrentTest.TEST_NAME, outcome=outcome)

    @classmethod
    def tearDownClass(cls):
        """
        Logic executed after all core_tests in class.
        """
        Tns.kill()
        TnsTest.kill_emulators()
        for process in TestContext.Processes.STARTED_PROCESSES:
            Log.info("Kill Process: " + os.linesep + process.commandline)
            Process.kill_pid(process.pid)
        Log.test_class_end(class_name=cls.__name__)

    @staticmethod
    def kill_emulators():
        DeviceManager.Emulator.stop()
        if Settings.HOST_OS is OSType.OSX:
            DeviceManager.Simulator.stop()


if __name__ == '__main__':
    unittest.main()
