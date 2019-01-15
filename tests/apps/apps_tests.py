import os
import unittest

from nose_parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import Folder
from core.utils.git import Git
from products.nativescript.tns import Tns


# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class SampleAppsTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_folder = os.path.join(Settings.TEST_RUN_HOME, app_name)
    emu = None
    sim = None

    test_data = [
        ('nativescript-sdk-examples-ng', 'NativeScript', 'NativeScript Code Samples'),
        ('nativescript-sdk-examples-js', 'NativeScript', 'Cookbook'),
        ('sample-Groceries', 'NativeScript', 'Login'),
        # ('nativescript-marketplace-demo', 'NativeScript', 'GET STARTED'),
        # Ignored because of https://github.com/NativeScript/nativescript-marketplace-demo/issues/301
    ]

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

        for app in cls.test_data:
            org = app[1]
            repo = app[0]
            Folder.clean(os.path.join(Settings.TEST_RUN_HOME, repo))
            Git.clone(repo_url='https://github.com/{0}/{1}'.format(org, repo), local_folder=repo)

    def setUp(self):
        TnsTest.setUp(self)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        for app in cls.test_data:
            repo = app[0]
            Folder.clean(os.path.join(Settings.TEST_RUN_HOME, repo))
        TnsTest.tearDownClass()

    @parameterized.expand(test_data)
    def test_001_build_android(self, repo, org, text):
        Tns.build_android(app_name=repo, release=True, bundle=True, aot=True, uglify=True, snapshot=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Skip iOS core_tests on non macOS machines.')
    @parameterized.expand(test_data)
    def test_002_build_ios(self, repo, org, text):
        Tns.build_ios(app_name=repo, release=True, for_device=True, bundle=True, aot=True, uglify=True)

    @parameterized.expand(test_data)
    def test_003_run_android(self, repo, org, text):
        Tns.run_android(app_name=repo, device=self.emu.id, bundle=True, justlaunch=True, wait=True)
        self.emu.wait_for_text(text=text, timeout=30)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Skip iOS core_tests on non macOS machines.')
    @parameterized.expand(test_data)
    def test_004_run_ios(self, repo, org, text):
        Tns.run_ios(app_name=repo, device=self.sim.id, bundle=True, justlaunch=True, wait=True)
        self.sim.wait_for_text(text=text, timeout=30)
