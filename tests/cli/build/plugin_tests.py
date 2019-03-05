
import os
import unittest

from nose_parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.file_utils import File, Folder
from core.utils.npm import Npm
from data.apps import Apps
from products.nativescript.tns import Tns


class CreateTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_path = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', 'TestApp')

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(cls.app_name, app_data=Apps.HELLO_WORLD_JS, update=False)
        Tns.platform_add_android(cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.platform_add_ios(cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)
        Folder.copy(cls.app_name, cls.app_path)

    def setUp(self):
        TnsTest.setUp(self)
        Folder.copy(self.app_path, self.app_name)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(cls.app_path)

    def tearDown(self):
        TnsTest.tearDown(self)
        Folder.clean(self.app_name)

    def test_100_plugin_add_after_platform_add_android(self):
        result = Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name)
        assert "Successfully installed plugin tns-plugin" in result.output
        assert File.exists(os.path.join(Settings.Paths.tns_plugin, 'index.js'))
        assert File.exists(os.path.join(Settings.Paths.tns_plugin, 'package.json'))

        output = File.read(os.path.join(self.app_name, 'package.json'))
        assert "org.nativescript.TestApp" in output
        assert "dependencies" in output
        assert "tns-plugin" in output

    def test_101_plugin_add_prepare_verify_apk_android(self):
        Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name, verify=False)
        Tns.build_android(app_name=self.app_name)
        assert File.exists(os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_APK_DEBUG_PATH,
                                        'app-debug.apk'))
        assert File.exists(os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH,
                                        'tns-plugin', 'index.js'))

    def test_102_plugin_add_verify_command_list_used_plugins_android(self):
        Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name, verify=False)
        Tns.prepare_android(app_name=self.app_name)
        result = Tns.exec_command(command="plugin", path=self.app_name)
        assert "tns-plugin" in result.output

    def test_200_plugin_platforms_should_not_exist_in_tns_modules_android(self):
        """
        Test for issue https://github.com/NativeScript/nativescript-cli/issues/3932
        """
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
        folder_path = os.path.join(self.app_name, 'nativescript-ui-listview')
        Npm.install(option='--ignore-scripts', folder=folder_path)
        Tns.build_android(app_name=self.app_name)
        app_path = os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH)
        assert not File.exists(os.path.join(app_path, 'nativescript-ui-listview', 'node_modules',
                                            'nativescript-ui-core', 'platforms'))

    def test_210_plugin_with_promise_in_hooks_android(self):
        Tns.plugin_add(plugin_name='nativescript-fabric@1.0.6', path=self.app_name, verify=False)
        result = Tns.prepare_android(app_name=self.app_name, verify=False)
        assert "Failed to execute hook" in result.output
        assert "nativescript-fabric.js" in result.output
        assert "TypeError" not in result.output
        assert "Cannot read property" not in result.output

    def test_302_plugin_and_npm_modules_in_same_project_android(self):
        Tns.plugin_add(plugin_name='nativescript-social-share', path=self.app_name, verify=False)
        output = Npm.install(package='nativescript-appversion', option='--save', folder=self.app_name)
        assert "ERR!" not in output
        assert "nativescript-appversion@" in output

        Tns.build_android(app_name=self.app_name, verify=False)
        # Verify plugin and npm module files
        base_path = os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID_NPM_MODULES_PATH)
        assert File.exists(os.path.join(base_path, "nativescript-social-share/package.json"))
        assert File.exists(os.path.join(base_path, "nativescript-social-share/social-share.js"))
        assert not File.exists(os.path.join(base_path, "nativescript-social-share/social-share.android.js"))
        assert not File.exists(os.path.join(base_path, "nativescript-social-share/social-share.ios.js"))
        assert File.exists(os.path.join(base_path, "nativescript-appversion/package.json"))
        assert File.exists(os.path.join(base_path, "nativescript-appversion/appversion.js"))
        assert not File.exists(os.path.join(base_path, "nativescript-appversion/appversion.android.js"))
        assert not File.exists(os.path.join(base_path, "nativescript-appversion/appversion.ios.js"))

    def test_400_plugin_add_invalid_plugin_android(self):
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

    def test_410_plugin_remove_should_not_fail_if_plugin_name_has_dot_android(self):
        """
        Test for issue https://github.com/NativeScript/nativescript-cli/issues/3451
        """
        Tns.platform_remove(app_name=self.app_name, platform=Platform.ANDROID)
        Tns.plugin_add(plugin_name='nativescript-socket.io', path=self.app_name, verify=False)
        assert Folder.exists(os.path.join(self.app_name, 'node_modules', 'nativescript-socket.io'))
        result = Tns.plugin_remove(plugin_name='nativescript-socket.io', path=self.app_name, log_trace=True)
        assert "Successfully removed plugin nativescript-socket.io" in result.output
        assert "stdout: removed 1 package" in result.output
        assert "Exec npm uninstall nativescript-socket.io --save" in result.output
        output = File.read(os.path.join(self.app_name, 'package.json'))
        assert "nativescript-socket.io" not in output

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_101_plugin_add_prepare_verify_app_ios(self):
        Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name, verify=False)
        Tns.build_ios(app_name=self.app_name)
        # path_app = os.path.join(self.app_name, Settings.Paths.PLATFORM_IOS_APP_PATH, "TestApp.app")
        # assert File.exists(path_app)
        assert File.exists(os.path.join(self.app_name, Settings.Paths.PLATFORM_IOS_NPM_MODULES_PATH,
                                        'tns-plugin', 'index.js'))

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_201_build_app_for_both_platforms(self):
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
        output = Adb.get_package_permission(apk_path)
        assert "android.permission.READ_EXTERNAL_STORAGE" in output
        assert "android.permission.WRITE_EXTERNAL_STORAGE" in output
        assert "android.permission.INTERNET" in output

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_311_plugin_platforms_should_not_exist_in_tnsmodules_ios(self):
        """
        Test for issue https://github.com/NativeScript/nativescript-cli/issues/3932
        """
        Tns.platform_remove(app_name=self.app_name, platform=Platform.IOS)
        Tns.plugin_add(plugin_name='nativescript-ui-listview', path=self.app_name, verify=False)
        Folder.clean(os.path.join(self.app_name, 'node_modules'))
        File.delete(os.path.join(self.app_name, 'package.json'))
        copy = os.path.join('assets', 'issues', 'nativescript-cli-3932', 'nativescript-ui-listview')
        paste = os.path.join(self.app_name, 'nativescript-ui-listview')
        Folder.copy(copy, paste)
        src = os.path.join('assets', 'issues', 'nativescript-cli-3932', 'package.json')
        target = os.path.join(self.app_name)
        File.copy(src=src, target=target)
        Tns.platform_add_ios(app_name=self.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)
        folder_path = os.path.join(self.app_name, 'nativescript-ui-listview')
        Npm.install(option='--ignore-scripts', folder=folder_path)
        Tns.build_ios(app_name=self.app_name)
        app_path = os.path.join(self.app_name, Settings.Paths.PLATFORM_IOS)
        assert not File.exists(os.path.join(app_path, 'nativescript-ui-listview', 'node_modules',
                                                'nativescript-ui-core', 'platforms'))

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_320_CFBundleURLTypes_overridden_from_plugin_ios(self):
        """
        Test for issue https://github.com/NativeScript/nativescript-cli/issues/2936
        """
        Tns.platform_remove(app_name=self.app_name, platform=Platform.IOS)
        plugin_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'plugins', 'CFBundleURLName-Plugin.tgz')
        Tns.plugin_add(plugin_path, path=self.app_name)
        Tns.prepare_ios(app_name=self.app_name)
        plist = File.read(os.path.join(self.app_name, Settings.Paths.PLATFORM_IOS, self.app_name,
                                       self.app_name + "-Info.plist"))
        assert "<key>NSAllowsArbitraryLoads</key>" in plist, \
            "NSAppTransportSecurity from plugin is not found in final Info.plist"
        assert "<string>bar</string>" in plist, "CFBundleURLTypes from plugin is not found in final Info.plist"

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_401_plugin_add_invalid_plugin_ios(self):
        Tns.platform_remove(app_name=self.app_name, platform=Platform.IOS)
        Tns.platform_remove(app_name=self.app_name, platform=Platform.ANDROID)
        result = Tns.plugin_add(plugin_name='wd', path=self.app_name, verify=False)
        assert "wd is not a valid NativeScript plugin" in result.output
        assert "Verify that the plugin package.json file " + \
               "contains a nativescript key and try again" in result.output
        Tns.platform_add_android(self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.platform_add_ios(self.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Verify iOS only plugin
        result = Tns.plugin_add(plugin_name='tns-plugin@1.0.2', path=self.app_name, verify=False)
        assert "tns-plugin is not supported for android" in result.output
        assert "Successfully installed plugin tns-plugin" in result.output

        # Verify Android only plugin
        result = Tns.plugin_add(plugin_name='acra-telerik-analytics', path=self.app_name, verify=False)
        assert "acra-telerik-analytics is not supported for ios" in result.output
        assert "Successfully installed plugin acra-telerik-analytics" in result.output

        Tns.build_ios(app_name=self.app_name)
        ios_path = os.path.join(self.app_name, Settings.Paths.PLATFORM_IOS)
        assert not File.pattern_exists(ios_path, pattern="*.aar")
        assert not File.pattern_exists(ios_path, pattern="*acra*")

        Tns.build_android(app_name=self.app_name)
        android_path = os.path.join(self.app_name, Settings.Paths.PLATFORM_ANDROID)
        assert File.pattern_exists(android_path, pattern="*.aar")
        assert File.pattern_exists(android_path, pattern="*acra*")
