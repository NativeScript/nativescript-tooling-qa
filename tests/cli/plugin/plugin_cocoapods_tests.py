import os

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.file_utils import File, Folder
from core.utils.run import run
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_paths import TnsPaths


class PluginCocoapodsTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_path = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', 'TestApp')
    app_identifier = "org.nativescript.testapp"

    if Settings.HOST_OS is OSType.OSX:
        @classmethod
        def setUpClass(cls):
            TnsTest.setUpClass()
            Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
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

        def test_100_plugin_add_multiple_pods(self):
            plugin_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'plugins', 'CocoaPods', 'carousel.tgz')
            result = Tns.plugin_add(plugin_path, path=Settings.AppName.DEFAULT)
            assert "Successfully installed plugin carousel." in result.output
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'carousel',
                                            'package.json'))
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'carousel', 'platforms',
                                            'ios', 'Podfile'))
            assert "carousel" in File.read(os.path.join(Settings.TEST_RUN_HOME, self.app_name, 'package.json'))

            plugin_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'plugins', 'CocoaPods', 'keychain.tgz')
            result = Tns.plugin_add(plugin_path, path=Settings.AppName.DEFAULT)
            assert "Successfully installed plugin keychain." in result.output
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'keychain',
                                            'package.json'))
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'keychain', 'platforms',
                                            'ios', 'Podfile'))
            assert "keychain" in File.read(os.path.join(Settings.TEST_RUN_HOME, self.app_name, 'package.json'))

            result = Tns.prepare_ios(self.app_name)
            assert "Installing pods..." in result.output
            # These asserts will be available again after we merge the webpack only branch for 6.0.0 release
            # assert "Successfully prepared plugin carousel for ios." in result.output
            # assert "Successfully prepared plugin keychain for ios." in result.output

            output = File.read(os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name), 'Podfile'))
            assert "use_frameworks!" in output
            assert "pod 'iCarousel'" in output
            assert "pod 'AFNetworking'" in output
            assert "pod 'UICKeyChainStore'" in output

        def test_202_plugin_add_pod_google_maps_after_platform_add_ios(self):
            plugin_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'plugins', 'CocoaPods', 'googlesdk.tgz')
            result = Tns.plugin_add(plugin_path, path=Settings.AppName.DEFAULT)
            assert "Successfully installed plugin googlesdk." in result.output
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'googlesdk',
                                            'package.json'))
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'googlesdk', 'platforms',
                                            'ios', 'Podfile'))

            output = File.read(os.path.join(self.app_name, 'package.json'))
            assert self.app_identifier in output.lower()
            assert "dependencies" in output
            assert "googlesdk" in output

            result = Tns.build_ios(self.app_name)
            assert "Installing pods..." in result.output

            output = File.read(os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name), 'Podfile'))
            assert "source 'https://github.com/CocoaPods/Specs.git'" in output
            assert "platform :ios, '8.1'" in output
            assert "pod 'GoogleMaps'" in output
            assert "use_frameworks!" in output

            output = File.read(os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name), 'TestApp.xcworkspace',
                                            'contents.xcworkspacedata'))
            assert "location = \"group:TestApp.xcodeproj\">" in output
            assert "location = \"group:Pods/Pods.xcodeproj\">" in output
            assert Folder.exists(os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name), 'Pods',
                                              'Pods.xcodeproj'))

            # This deployment target comes from the CLI
            output = File.read(os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name),
                                            'TestApp.xcodeproj', 'project.pbxproj'))
            assert "IPHONEOS_DEPLOYMENT_TARGET = 9.0;" in output

        def test_210_plugin_add_static_lib_universal(self):
            plugin_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'plugins', 'hello-plugin.tgz')
            result = Tns.plugin_add(plugin_path, path=Settings.AppName.DEFAULT, verify=False)
            assert "Successfully installed plugin hello." in result.output

            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'hello', 'package.json'))
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'hello',
                                            'hello-plugin.ios.js'))
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'hello', 'platforms',
                                            'ios', 'HelloLib.a'))
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'hello', 'platforms',
                                            'ios', 'include', 'HelloLib', 'Bye.h'))
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name), 'hello', 'platforms',
                                            'ios', 'include', 'HelloLib', 'Hello.h'))
            output = File.read(os.path.join(self.app_name, 'package.json'))
            assert "plugins/hello-plugin" in output

            # Require the plugin so webpack can pick it up
            main_js_file = os.path.join(Settings.TEST_RUN_HOME, self.app_name, 'app', 'main-page.js')
            File.append(main_js_file, 'const hello = require("hello");')

            Tns.prepare_ios(self.app_name)

            bundle_js = File.read(os.path.join(TnsPaths.get_platforms_ios_app_path(self.app_name), 'bundle.js'))
            vendor_js = File.read(os.path.join(TnsPaths.get_platforms_ios_app_path(self.app_name), 'vendor.js'))
            assert '__webpack_require__("../node_modules/hello/hello-plugin.js")' in bundle_js
            assert 'hello = Hello.alloc().init();' in vendor_js

            result = run(
                "cat " + os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name), 'TestApp.xcodeproj',
                                      'project.pbxproj | grep \"HelloLib.a\"'))
            assert "HelloLib.a in Frameworks" in result.output

        def test_401_plugin_add_invalid_pod(self):
            plugin_path = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'plugins', 'CocoaPods', 'invalidpod.tgz')
            result = Tns.plugin_add(plugin_path, path=Settings.AppName.DEFAULT)
            assert "Successfully installed plugin invalidpod." in result.output
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name),
                                            'invalidpod', 'package.json'))
            assert File.exists(os.path.join(TnsPaths.get_app_node_modules_path(self.app_name),
                                            'invalidpod', 'platforms', 'ios', 'Podfile'))

            output = File.read(os.path.join(self.app_name, 'package.json'))
            assert "invalidpod" in output

            result = Tns.prepare_ios(self.app_name, verify=False)
            assert "Installing pods..." in result.output
            assert "'pod install' command failed" in result.output
            assert "pod 'InvalidPod'" in File.read(os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name),
                                                                'Podfile'))

            assert not File.exists(os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name),
                                                'TestApp.xcworkspace'))
            assert not File.exists(os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name),
                                                'Pods', 'Pods.xcodeproj'))
