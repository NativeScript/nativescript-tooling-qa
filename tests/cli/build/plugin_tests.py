
import os

from nose_parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.file_utils import File, Folder
from core.utils.npm import Npm
from data.apps import Apps
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
from products.nativescript.tns_paths import TnsPaths


class CreateTests(TnsTest):
    app_name = Settings.AppName.DEFAULT

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(cls.app_name, app_data=Apps.HELLO_WORLD_JS, update=False)
        Tns.platform_add_android(cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.platform_add_ios(cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_100_plugin_add_after_platform_add(self):
        result = Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name)
        assert "Successfully installed plugin tns-plugin" in result.output
        assert File.exists(os.path.join(Settings.Paths.tns_plugin, 'index.js'))
        assert File.exists(os.path.join(Settings.Paths.tns_plugin, 'package.json'))

        result = File.read(os.path.join(self.app_name, 'package.json'))
        assert "org.nativescript.TestApp" in result.output
        assert "dependencies" in result.output
        assert "tns-plugin" in result.output

    def test_101_plugin_add_prepare_verify_apk_android(self):
        Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name, verify=False)
        Tns.prepare_android(app_name=self.app_name)
        assert File.exists(os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_APK_DEBUG_PATH,
                                        'app-debug.apk'))
        assert File.exists(os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH,
                                        'tns-plugin', 'index.js'))

    def test_102_plugin_add_verify_command_list_used_plugins(self):
        Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name, verify=False)
        Tns.prepare_android(app_name=self.app_name)
        result = Tns.exec_command(command="plugin", path=self.app_name)
        assert "tns-plugin" in result.output

    def test_200_plugin_platforms_should_not_exist_in_tns_modules(self):
        # https://github.com/NativeScript/nativescript-cli/issues/3932
        Tns.platform_remove(app_name=self.app_name, platform=Platform.ANDROID)
        Tns.plugin_add(plugin_name='nativescript-ui-listview', path=self.app_name, verify=False)
        Folder.clean(os.path.join(self.app_name, 'node_modules'))
        File.delete(os.path.join(self.app_name, 'package.json'))
        copy = os.path.join('assets', 'issues', 'nativescript-cli-3932', 'nativescript-ui-listview')
        paste = os.path.join(self.app_name, 'nativescript-ui-listview')
        Folder.copy(copy, paste)
        src = os.path.join('assets', 'issues', 'nativescript-cli-3932', 'package.json')
        target = os.path.join(self.app_name)
        File.copy(src=src, target=target)
        Tns.platform_add_android(app_name=self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Folder.navigate_to(os.path.join(self.app_name, 'nativescript-ui-listview'))
        Npm.install(option='--ignore-scripts')
        Folder.navigate_to(os.path.join(Settings.TEST_RUN_HOME))
        Tns.prepare_android(app_name=self.app_name)
        app_path = os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH)
        assert not File.exists(os.path.join(self.app_name, 'nativescript-ui-listview', 'node_modules',
                                            'nativescript-ui-core', 'platforms'))

    def test_210_plugin_with_promise_in_hooks(self):
        Tns.plugin_add(plugin_name='nativescript-fabric@1.0.6', path=self.app_name, verify=False)
        result = Tns.prepare_android(app_name=self.app_name, verify=False)
        assert "Failed to execute hook" in result.output
        assert "nativescript-fabric.js" in result.output
        assert "TypeError" not in result.output
        assert "Cannot read property" not in result.output

    def test_400_plugin_add_invalid_plugin(self):
        result = Tns.plugin_add(plugin_name='fakePlugin', path=self.app_name, verify=False)
        assert "npm ERR!" in result.output
        result = Tns.plugin_add(plugin_name='wd', path=self.app_name, verify=False)
        assert "wd is not a valid NativeScript plugin" in result.output
        assert "Verify that the plugin package.json file contains a nativescript key and try again" in result.output
        Folder.clean(os.path.join(self.app_name))
        Tns.create(app_name=self.app_name, app_data=Apps.HELLO_WORLD_JS, update=False)
        Tns.platform_add_android(app_name=self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        result = Tns.plugin_add(plugin_name='tns-plugin@1.0.2', path=self.app_name, verify=False)
        assert "tns-plugin is not supported for android" in result.output
        assert "Successfully installed plugin tns-plugin" in result.output

    def test_410_plugin_remove_should_not_fail_if_plugin_name_has_dot(self):
        # https://github.com/NativeScript/nativescript-cli/issues/3451
        Tns.platform_remove(app_name=self.app_name, platform=Platform.ANDROID)
        Tns.plugin_add(plugin_name='nativescript-socket.io', path=self.app_name, verify=False)
        assert Folder.exists(os.path.join(self.app_name, 'node_modules', 'nativescript-socket.io'))
        result = Tns.plugin_remove(plugin_name='nativescript-socket.io', path=self.app_name, log_trace=True)
        assert "Successfully removed plugin nativescript-socket.io" in result.output
        assert "stdout: removed 1 package" in result.output
        assert "Exec npm uninstall nativescript-socket.io --save" in result.output
        result = File.read(os.path.join(self.app_name, 'package.json'))
        assert "nativescript-socket.io" not in result.output

    def test_101_plugin_add_prepare_verify_app_ios(self):
        Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name, verify=False)
        Tns.build_ios(app_name=self.app_name)
        # path_app = os.path.join(self.app_name, Settings.Paths.PLATFORM_IOS_APP_PATH, "TestApp.app")
        # assert File.exists(path_app)
        assert File.exists(os.path.join(self.app_name, Settings.Paths.PLATFORM_IOS_NPM_MODULES_PATH,
                                        'tns-plugin', 'index.js'))

    def test_201_build_app_for_both_platforms(self):
        Tns.platform_add_android(app_name=self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name, verify=False)

        # Verify files of the plugin
        assert File.exists(os.path.join(Settings.Paths.tns_plugin, 'index.js'))
        assert File.exists(os.path.join(Settings.Paths.tns_plugin, 'package.json'))
        assert File.exists(os.path.join(Settings.Paths.tns_plugin, 'test.android.js'))
        assert File.exists(os.path.join(Settings.Paths.tns_plugin, 'test.ios.js'))
        assert File.exists(os.path.join(Settings.Paths.tns_plugin, 'test2.android.xml'))
        assert File.exists(os.path.join(Settings.Paths.tns_plugin, 'test2.ios.xml'))

        Tns.build_ios(app_name=self.app_name)
        Tns.build_android(app_name=self.app_name)

        # # Verify platform specific files
        assert File.exists(os.path.join(Settings.Paths.tns_plugin_platform_ios, 'test.js'))
        assert File.exists(os.path.join(Settings.Paths.tns_plugin_platform_ios, 'test2.xml'))
        assert not File.exists(os.path.join(Settings.Paths.tns_plugin_platform_ios, 'test.ios.js'))
        assert not File.exists(os.path.join(Settings.Paths.tns_plugin_platform_ios, 'test2.ios.xml'))
        assert not File.exists(os.path.join(Settings.Paths.tns_plugin_platform_ios, 'test.android.js'))
        assert not File.exists(os.path.join(Settings.Paths.tns_plugin_platform_ios, 'test2.android.xml'))
        #
        assert File.exists(
            os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH, "tns-plugin/test.js"))
        assert File.exists(
            os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH, "tns-plugin/test2.xml"))
        assert not File.exists(
            os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH, "tns-plugin/test.ios.js"))
        assert not File.exists(
            os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH, "tns-plugin/test2.ios.xml"))
        assert not File.exists(
            os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH, "tns-plugin/test.android.js"))
        assert not File.exists(
            os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH, "tns-plugin/test2.android.xml"))

        apk_path = os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_APK_DEBUG_PATH, "app-debug.apk")
        result = Adb.get_package_permission(apk_path)
        assert "android.permission.READ_EXTERNAL_STORAGE" in result.output
        assert "android.permission.WRITE_EXTERNAL_STORAGE" in result.output
        assert "android.permission.INTERNET" in result.output
        assert "android.permission.FLASHLIGHT" in result.output
        assert "android.permission.CAMERA" in result.output




