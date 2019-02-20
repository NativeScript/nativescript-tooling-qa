
import os

from nose_parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import File
from data.apps import Apps
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
class CreateTests(TnsTest):
    app_name = Settings.AppName.DEFAULT

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(app_name=Settings.AppName.DEFAULT, app_data=Apps.HELLO_WORLD_JS, update=False)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_100_plugin_add_before_platform_add_android(self):
        Tns.platform_remove(app_name=Settings.AppName.DEFAULT, platform=Platform.ANDROID, verify=False)
        Tns.plugin_add(plugin_name='tns-plugin', path=Settings.AppName.DEFAULT)
        # Tns.plugin_remove(plugin_name='nativescript-camera', path=Settings.AppName.DEFAULT)
        assert File.exists(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'tns-plugin', 'index.js'))
        assert File.exists(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'tns-plugin', 'package.json'))

        result = File.read(os.path.join(Settings.AppName.DEFAULT, 'package.json'))
        assert "org.nativescript.TestApp" in result.output
        assert "dependencies" in result.output
        assert "tns-plugin" in result.output

    def test_101_plugin_add_after_platform_add_android(self):
        Tns.plugin_add(plugin_name='tns-plugin', path=Settings.AppName.DEFAULT)
        assert File.exists(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'tns-plugin', 'index.js'))
        assert File.exists(os.path.join(Settings.AppName.DEFAULT, 'node_modules', 'tns-plugin', 'package.json'))

        result = File.read(os.path.join(Settings.AppName.DEFAULT, 'package.json'))
        assert "org.nativescript.TestApp" in result.output
        assert "dependencies" in result.output
        assert "tns-plugin" in result.output

