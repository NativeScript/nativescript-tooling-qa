import os
import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.app_type import AppType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder, File
from core.utils.git import Git
from core.utils.npm import Npm
from data.sync.plugin_src import sync_plugin_verify_demo
from data.templates import Template
from products.nativescript.tns import Tns
plugin_name = 'nativescript-datetimepicker'
plugin_repo = 'https://github.com/NativeScript/nativescript-datetimepicker'


class DateTimePickerHmrTests(TnsRunTest):
    app_name = 'datetimepicker.demo'
    plugin_name = 'nativescript-datetimepicker'

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        plugin_folder = os.path.join(Settings.TEST_SUT_HOME, plugin_name)

        # Clone the plugin
        Git.clone(repo_url=plugin_repo, local_folder=plugin_folder, branch="master")

        # Build the plugin
        cmd = 'run build'
        Npm.run_command(cmd, os.path.join(plugin_folder, 'src'))

    def setUp(self):
        TnsRunTest.setUp(self)

    def test_100_run_android_bundle(self):
        print("PASS")
        sync_plugin_verify_demo(app_name=self.app_name, app_type=AppType.NG, plugin_name=self.plugin_name,
                                platform=Platform.ANDROID, device=self.emu)

    # @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    # def test_100_run_ios_bundle(self):
    #     sync_master_detail_vue(self.app_name, Platform.IOS, self.sim)
