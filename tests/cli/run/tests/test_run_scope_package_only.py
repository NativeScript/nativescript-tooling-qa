import os
import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.npm import Npm
from data.changes import Changes
from data.templates import Template
from products.nativescript.run_type import RunType
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


class TestRunWithScopePackageOnly(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    app_path = os.path.join(Settings.TEST_RUN_HOME, Settings.AppName.DEFAULT)

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_NG.local_package, update=True)
        Npm.uninstall(package='tns-core-modules', option='--save', folder=cls.app_path)
        Npm.install(package=Settings.Packages.NATIVESCRIPT_CORE, option='--save --save-exact', folder=cls.app_path)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def setUp(self):
        TnsRunTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsRunTest.tearDownClass()

    def test_100_run_android(self):
        self.run_app(Platform.ANDROID, self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_100_run_ios(self):
        self.run_app(Platform.IOS, self.sim)

    def run_app(self, platform, device):
        result = Tns.run(app_name=self.app_name, platform=platform, emulator=True, wait=False)
        strings = TnsLogs.run_messages(app_name=self.app_name, platform=platform, run_type=RunType.UNKNOWN,
                                       device=device)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=240)
        device.wait_for_text(text=Changes.NGHelloWorld.TS.old_text)
