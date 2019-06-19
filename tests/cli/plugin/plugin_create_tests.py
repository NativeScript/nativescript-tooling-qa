import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.file_utils import Folder
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
class PluginCreateTests(TnsTest):
    plugin_name = "nativescript-test-plugin"
    plugin_path = os.path.join(Settings.TEST_RUN_HOME, plugin_name)

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)
        Folder.clean(self.plugin_path)

    def tearDown(self):
        TnsTest.tearDown(self)
        Folder.clean(self.plugin_path)
        Folder.clean(os.path.join(Settings.TEST_RUN_HOME, "plugin-folder"))

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(cls.plugin_name)

    def test_100_plugin_create(self):
        Tns.plugin_create(plugin_name=self.plugin_name, type_script=True)

    def test_200_plugin_create_with_path(self):
        Tns.plugin_create(plugin_name=self.plugin_name, type_script=True, path="plugin-folder", verify=False)

    def test_201_plugin_create_custom_template(self):
        template_url = "https://github.com/NativeScript/nativescript-plugin-seed/tarball/master"
        output = Tns.plugin_create(plugin_name=self.plugin_name, type_script=True, template=template_url, verify=True)
        assert "Make sure your custom template is compatible with the Plugin Seed" in output

    def test_202_plugin_create_custom_user_and_plugin_name(self):
        Tns.exec_command(command="plugin create --includeTypeScriptDemo=y nativescript-test-plugin "
                                 "--username gitUser --pluginName customName")
        # TODO: Assert username and pluginName are replaced in generated files.

    @unittest.skip("Webpack only, must upgrade plugin")
    def test_300_build_demo(self):
        # TODO: Run npm scripts from plugin seed (build plugin, link plugin and then build the app).
        Tns.plugin_create(self.plugin_name, type_script=True)
        demo_path = os.path.join(self.plugin_name, 'demo')
        Tns.build_android(demo_path)
        if Settings.HOST_OS is OSType.OSX:
            Tns.build_ios(demo_path)
