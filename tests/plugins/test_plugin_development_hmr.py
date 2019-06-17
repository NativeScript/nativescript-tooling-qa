import os
import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.app_type import AppType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.git import Git
from core.utils.npm import Npm
# from data.sync.plugin_src import sync_plugin_platform_specific_verify_demo
from data.sync.plugin_src import sync_plugin_common_verify_demo
from data.sync.plugin_src import run_demo_app
plugin_repo = 'https://github.com/NativeScript/nativescript-datetimepicker'


class DateTimePickerHmrTests(TnsRunTest):
    app_name = 'datetimepicker.demo'
    plugin_name = 'nativescript-datetimepicker'
    plugin_folder = os.path.join(Settings.TEST_SUT_HOME, plugin_name)

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()

        # Clone the plugin
        Git.clone(repo_url=plugin_repo, local_folder=DateTimePickerHmrTests.plugin_folder, branch="master")

    def setUp(self):
        TnsRunTest.setUp(self)
        # Clean the demo folder and src folder with `git clean -fdx` and `git reset` command to ensure
        # every test starts with initial app setup
        Git.clean_repo_changes(self.plugin_folder)

        # Build the plugin
        cmd = 'run build'
        Npm.run_command(cmd, os.path.join(DateTimePickerHmrTests.plugin_folder, 'src'))

    def test_101_run_android_typescript_common(self):
        result = run_demo_app(app_name=self.app_name, app_type=AppType.TS, plugin_name=self.plugin_name,
                              platform=Platform.ANDROID)
        sync_plugin_common_verify_demo(app_name=self.app_name, app_type=AppType.TS, platform=Platform.ANDROID,
                                       device=self.emu, log_result=result)

    # def test_102_run_android_typescript_platform_spec(self):
    #     result = run_demo_app(app_name=self.app_name, app_type=AppType.TS, plugin_name=self.plugin_name,
    #                           platform=Platform.ANDROID)
    #     sync_plugin_platform_specific_verify_demo(app_name=self.app_name, app_type=AppType.TS,
    #                                               platform=Platform.ANDROID, device=self.emu, log_result=result)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_103_run_ios_typescript_common(self):
        result = run_demo_app(app_name=self.app_name, app_type=AppType.TS, plugin_name=self.plugin_name,
                              platform=Platform.IOS)
        sync_plugin_common_verify_demo(app_name=self.app_name, app_type=AppType.TS, platform=Platform.IOS,
                                       device=self.sim, log_result=result)

    # @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    # def test_104_run_ios_typescript_platform_spec(self):
    #     result = run_demo_app(app_name=self.app_name, app_type=AppType.TS, plugin_name=self.plugin_name,
    #                           platform=Platform.IOS)
    #     sync_plugin_platform_specific_verify_demo(app_name=self.app_name, app_type=AppType.TS, platform=Platform.IOS,
    #                                               device=self.sim, log_result=result)
