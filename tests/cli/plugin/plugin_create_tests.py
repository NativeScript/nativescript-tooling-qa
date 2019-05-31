import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.file_utils import File, Folder
from core.utils.npm import Npm
from data.apps import Apps
from products.nativescript.tns import Tns
from products.nativescript.tns_paths import TnsPaths


class PluginTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_path = TnsPaths.get_app_path(app_name=app_name)
    app_temp_path = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', 'TestApp')
    plugin_name = "nativescript-test-plugin"

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(cls.app_name, app_data=Apps.MIN_JS, update=False)
        Tns.platform_add_android(cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)
        Folder.copy(cls.app_path, cls.app_temp_path)

    def setUp(self):
        TnsTest.setUp(self)
        Folder.clean(self.app_path)
        Folder.copy(self.app_temp_path, self.app_path)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(cls.app_temp_path)

    def test_100_plugin_add_after_platform_add_android(self):
        Tns.pl
        result = Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name)
        assert 'Successfully installed plugin tns-plugin' in result.output
        assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'tns-plugin', 'index.js'))
        assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'tns-plugin',
                                        'package.json'))

        output = File.read(os.path.join(self.app_path, 'package.json'))
        assert 'org.nativescript.TestApp' in output
        assert 'dependencies' in output
        assert 'tns-plugin' in output




