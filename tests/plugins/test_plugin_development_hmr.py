import os
import unittest

from nose_parameterized import parameterized

from core.base_test.tns_run_test import TnsRunTest
from core.enums.app_type import AppType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.utils.git import Git
from core.utils.npm import Npm
from data.sync.plugin_src import sync_plugin_platform_spec
from data.sync.plugin_src import verify_demo_initial_state
from data.sync.plugin_src import sync_plugin_common
from data.sync.plugin_src import run_demo_app


class DateTimePickerHmrTests(TnsRunTest):
    app_name = 'datetimepicker.demo'
    plugin_name = 'nativescript-datetimepicker'
    plugin_folder = os.path.join(Settings.TEST_SUT_HOME, plugin_name)
    plugin_repo = 'https://github.com/NativeScript/nativescript-datetimepicker'

    test_data = [
        ('TS_HMR', AppType.TS, True),
        ('TS_NO_HMR', AppType.TS, False),
        ('NG_HMR', AppType.NG, True),
        ('NG_NO_HMR', AppType.NG, False),
        ('VUE_HMR', AppType.VUE, True),
        ('VUE_NO_HMR', AppType.VUE, False)
    ]

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()

        # Clone the plugin
        Git.clone(repo_url=DateTimePickerHmrTests.plugin_repo, local_folder=DateTimePickerHmrTests.plugin_folder,
                  branch="master")

    def setUp(self):
        TnsRunTest.setUp(self)
        # Clean the demo folder and src folder with `git clean -fdx` and `git reset` command to ensure
        # every test starts with initial app setup
        Git.clean_repo_changes(self.plugin_folder)

        # Build the plugin
        cmd = 'run build'
        Npm.run_npm_command(cmd, os.path.join(DateTimePickerHmrTests.plugin_folder, 'src'))

    @parameterized.expand(test_data)
    @unittest.skipIf(Settings.HOST_OS == OSType.OSX, 'Android tests will be executed on linux.')
    def test_101_run_android_typescript_common(self, test_id, app_type, hmr):
        Log.info(test_id)
        result = run_demo_app(app_name=self.app_name, app_type=app_type, plugin_name=self.plugin_name,
                              platform=Platform.ANDROID, hmr=hmr)
        verify_demo_initial_state(self.emu)
        sync_plugin_common(app_name=self.app_name, app_type=app_type, platform=Platform.ANDROID,
                           device=self.emu, log_result=result, hmr=hmr)

    @parameterized.expand(test_data)
    @unittest.skipIf(Settings.HOST_OS == OSType.OSX, 'Android tests will be executed on linux.')
    def test_102_run_android_typescript_platform_spec(self, test_id, app_type, hmr):
        Log.info(test_id)
        result = run_demo_app(app_name=self.app_name, app_type=app_type, plugin_name=self.plugin_name,
                              platform=Platform.ANDROID, hmr=hmr)
        verify_demo_initial_state(self.emu)
        sync_plugin_platform_spec(app_name=self.app_name, app_type=app_type,
                                  platform=Platform.ANDROID, device=self.emu, log_result=result, hmr=hmr)

    @parameterized.expand(test_data)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_103_run_ios_typescript_common(self, test_id, app_type, hmr):
        Log.info(test_id)
        result = run_demo_app(app_name=self.app_name, app_type=app_type, plugin_name=self.plugin_name,
                              platform=Platform.IOS, hmr=hmr)
        verify_demo_initial_state(self.sim)
        sync_plugin_common(app_name=self.app_name, app_type=app_type, platform=Platform.IOS,
                           device=self.sim, log_result=result, hmr=hmr)

    @parameterized.expand(test_data)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_104_run_ios_typescript_platform_spec(self, test_id, app_type, hmr):
        Log.info(test_id)
        result = run_demo_app(app_name=self.app_name, app_type=app_type, plugin_name=self.plugin_name,
                              platform=Platform.IOS, hmr=hmr)
        verify_demo_initial_state(self.sim)
        sync_plugin_platform_spec(app_name=self.app_name, app_type=app_type, platform=Platform.IOS,
                                  device=self.sim, log_result=result, hmr=hmr)
