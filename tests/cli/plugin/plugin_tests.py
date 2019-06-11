import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.file_utils import File, Folder
from core.utils.npm import Npm
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_paths import TnsPaths


class PluginTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_path = TnsPaths.get_app_path(app_name=app_name)
    app_temp_path = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', 'TestApp')

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
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

    def test_100_plugin_add(self):
        Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name)

        # Verify files of the plugin
        plugin_path = os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'tns-plugin')
        assert File.exists(os.path.join(plugin_path, 'index.js'))
        assert File.exists(os.path.join(plugin_path, 'package.json'))
        assert File.exists(os.path.join(plugin_path, 'test.android.js'))
        assert File.exists(os.path.join(plugin_path, 'test.ios.js'))
        assert File.exists(os.path.join(plugin_path, 'test2.android.xml'))
        assert File.exists(os.path.join(plugin_path, 'test2.ios.xml'))

        # Verify plugin list show installed plugins
        result = Tns.exec_command(command='plugin', path=self.app_name)
        assert 'tns-plugin' in result.output

    def test_101_plugin_add_and_build(self):
        Tns.plugin_add(plugin_name='tns-plugin', path=self.app_name)

        # Build Android
        Tns.build_android(app_name=self.app_name, bundle=False)

        # Verify permissions are merged
        apk_path = TnsPaths.get_apk_path(app_name=self.app_name, release=False)
        output = Adb.get_package_permission(apk_path)
        assert 'android.permission.READ_EXTERNAL_STORAGE' in output
        assert 'android.permission.WRITE_EXTERNAL_STORAGE' in output
        assert 'android.permission.INTERNET' in output

        # Verify Platforms files
        plugin_android_path = os.path.join(TnsPaths.get_platforms_android_npm_modules(self.app_name), 'tns-plugin')
        assert File.exists(os.path.join(plugin_android_path, 'index.js'))
        assert File.exists(os.path.join(plugin_android_path, 'test.js'))
        assert File.exists(os.path.join(plugin_android_path, 'test2.xml'))
        assert not File.exists(os.path.join(plugin_android_path, 'test.ios.js'))
        assert not File.exists(os.path.join(plugin_android_path, 'test2.ios.xml'))
        assert not File.exists(os.path.join(plugin_android_path, 'test.android.js'))
        assert not File.exists(os.path.join(plugin_android_path, 'test2.android.xml'))

        # Build IOS
        if Settings.HOST_OS is OSType.OSX:
            Tns.build_ios(app_name=self.app_name, bundle=False)
            plugin_ios_path = os.path.join(TnsPaths.get_platforms_ios_npm_modules(self.app_name), 'tns-plugin')
            assert File.exists(os.path.join(plugin_ios_path, 'index.js'))
            assert File.exists(os.path.join(plugin_ios_path, 'test.js'))
            assert File.exists(os.path.join(plugin_ios_path, 'test2.xml'))
            assert not File.exists(os.path.join(plugin_ios_path, 'test.ios.js'))
            assert not File.exists(os.path.join(plugin_ios_path, 'test2.ios.xml'))
            assert not File.exists(os.path.join(plugin_ios_path, 'test.android.js'))
            assert not File.exists(os.path.join(plugin_ios_path, 'test2.android.xml'))

    def test_200_plugin_platforms_should_not_exist_in_tns_modules_android(self):
        """
        Test for issue https://github.com/NativeScript/nativescript-cli/issues/3932
        """
        issue_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'issues', 'nativescript-cli-3932')
        Tns.platform_remove(app_name=self.app_name, platform=Platform.ANDROID)
        Tns.plugin_add(plugin_name='nativescript-ui-listview', path=self.app_name)
        Folder.clean(os.path.join(self.app_name, 'node_modules'))
        File.delete(os.path.join(self.app_name, 'package.json'))
        copy = os.path.join(issue_path, 'nativescript-ui-listview')
        paste = os.path.join(self.app_path, 'nativescript-ui-listview')
        Folder.copy(copy, paste)
        copy = os.path.join(issue_path, 'package.json')
        paste = os.path.join(self.app_name)
        File.copy(copy, paste)
        Tns.platform_add_android(app_name=self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        folder_path = os.path.join(self.app_path, 'nativescript-ui-listview')
        Npm.install(option='--ignore-scripts', folder=folder_path)
        Tns.build_android(app_name=self.app_name, bundle=False)
        app_path = os.path.join(TnsPaths.get_platforms_android_npm_modules(self.app_name))
        assert not File.exists(os.path.join(app_path, 'nativescript-ui-listview', 'node_modules',
                                            'nativescript-ui-core', 'platforms'))

    def test_210_plugin_with_promise_in_hooks_android(self):
        Tns.plugin_add(plugin_name='nativescript-fabric@1.0.6', path=self.app_name)
        result = Tns.prepare_android(app_name=self.app_name, verify=False)
        assert 'Failed to execute hook' in result.output
        assert 'nativescript-fabric.js' in result.output
        assert 'TypeError' not in result.output
        assert 'Cannot read property' not in result.output

    def test_302_plugin_and_npm_modules_in_same_project_android(self):
        Tns.plugin_add(plugin_name='nativescript-social-share', path=self.app_name)
        output = Npm.install(package='nativescript-appversion', option='--save', folder=self.app_path)
        assert 'ERR!' not in output
        assert 'nativescript-appversion@' in output

        Tns.build_android(app_name=self.app_name, bundle=False)

        # Verify plugin and npm module files
        assert File.exists(os.path.join(TnsPaths.get_platforms_android_npm_modules(self.app_name),
                                        'nativescript-social-share', 'package.json'))
        assert File.exists(os.path.join(TnsPaths.get_platforms_android_npm_modules(self.app_name),
                                        'nativescript-social-share', 'social-share.js'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_npm_modules(self.app_name),
                                            'nativescript-social-share', 'social-share.android.js'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_npm_modules(self.app_name),
                                            'nativescript-social-share', 'social-share.ios.js'))
        assert File.exists(os.path.join(TnsPaths.get_platforms_android_npm_modules(self.app_name),
                                        'nativescript-appversion', 'package.json'))
        assert File.exists(os.path.join(TnsPaths.get_platforms_android_npm_modules(self.app_name),
                                        'nativescript-appversion', 'appversion.js'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_npm_modules(self.app_name),
                                            'nativescript-appversion', 'appversion.android.js'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_npm_modules(self.app_name),
                                            'nativescript-appversion', 'appversion.ios.js'))

    def test_410_plugin_remove_should_not_fail_if_plugin_name_has_dot_android(self):
        """
        Test for issue https://github.com/NativeScript/nativescript-cli/issues/3451
        """
        Tns.platform_remove(app_name=self.app_name, platform=Platform.ANDROID)
        Tns.plugin_add(plugin_name='nativescript-socket.io', path=self.app_name)
        assert Folder.exists(os.path.join(self.app_path, 'node_modules', 'nativescript-socket.io'))
        result = Tns.plugin_remove(plugin_name='nativescript-socket.io', path=self.app_name, log_trace=True)
        assert 'Successfully removed plugin nativescript-socket.io' in result.output
        assert 'stdout: removed 1 package' in result.output
        assert 'Exec npm uninstall nativescript-socket.io --save' in result.output
        output = File.read(os.path.join(self.app_path, 'package.json'))
        assert 'nativescript-socket.io' not in output

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_311_plugin_platforms_should_not_exist_in_tns_modules_ios(self):
        """
        Test for issue https://github.com/NativeScript/nativescript-cli/issues/3932
        """
        Tns.platform_remove(app_name=self.app_name, platform=Platform.IOS)
        Tns.plugin_add(plugin_name='nativescript-ui-listview', path=self.app_name)
        Folder.clean(os.path.join(self.app_name, 'node_modules'))
        File.delete(os.path.join(self.app_name, 'package.json'))
        copy = os.path.join('assets', 'issues', 'nativescript-cli-3932', 'nativescript-ui-listview')
        paste = os.path.join(self.app_name, 'nativescript-ui-listview')
        Folder.copy(copy, paste)
        copy = os.path.join('assets', 'issues', 'nativescript-cli-3932', 'package.json')
        paste = os.path.join(self.app_name)
        File.copy(copy, paste)
        Tns.platform_add_ios(app_name=self.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)
        folder_path = os.path.join(self.app_name, 'nativescript-ui-listview')
        Npm.install(option='--ignore-scripts', folder=folder_path)
        Tns.build_ios(app_name=self.app_name, bundle=False)
        app_path = os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name))
        assert not File.exists(
            os.path.join(app_path, 'nativescript-ui-listview', 'node_modules', 'nativescript-ui-core', 'platforms'))

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_320_cfbundleurltypes_overridden_from_plugin_ios(self):
        """
        Test for issue https://github.com/NativeScript/nativescript-cli/issues/2936
        """
        Tns.platform_remove(app_name=self.app_name, platform=Platform.IOS)
        plugin_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'plugins', 'CFBundleURLName-Plugin.tgz')
        Tns.plugin_add(plugin_path, path=self.app_name)
        Tns.prepare_ios(app_name=self.app_name)
        plist = File.read(os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name), self.app_name,
                                       self.app_name + '-Info.plist'))
        assert '<key>NSAllowsArbitraryLoads</key>' in plist, \
            'NSAppTransportSecurity from plugin is not found in final Info.plist'
        assert '<string>bar</string>' in plist, 'CFBundleURLTypes from plugin is not found in final Info.plist'

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_401_plugin_add_invalid_plugin(self):
        Tns.platform_remove(app_name=self.app_name, platform=Platform.IOS)
        Tns.platform_remove(app_name=self.app_name, platform=Platform.ANDROID)
        result = Tns.plugin_add(plugin_name='wd', path=self.app_name, verify=False)
        assert 'wd is not a valid NativeScript plugin' in result.output
        assert 'Verify that the plugin package.json file ' + \
               'contains a nativescript key and try again' in result.output
        Tns.platform_add_android(self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.platform_add_ios(self.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Verify iOS only plugin
        result = Tns.plugin_add(plugin_name='tns-plugin@1.0.2', path=self.app_name)
        assert 'tns-plugin is not supported for android' in result.output
        assert 'Successfully installed plugin tns-plugin' in result.output

        # Verify Android only plugin
        result = Tns.plugin_add(plugin_name='acra-telerik-analytics', path=self.app_name)
        assert 'acra-telerik-analytics is not supported for ios' in result.output
        assert 'Successfully installed plugin acra-telerik-analytics' in result.output

        Tns.build_ios(app_name=self.app_name, bundle=False)
        ios_path = os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name))
        assert not File.pattern_exists(ios_path, pattern='*.aar')
        assert not File.pattern_exists(ios_path, pattern='*acra*')

        Tns.build_android(app_name=self.app_name, bundle=False)
        android_path = os.path.join(TnsPaths.get_platforms_android_folder(self.app_name))
        assert File.pattern_exists(android_path, pattern='*.aar')
        assert File.pattern_exists(android_path, pattern='*acra*')
