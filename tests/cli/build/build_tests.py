import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.settings.Settings import TEST_RUN_HOME
from core.utils.file_utils import File, Folder
from core.utils.npm import Npm
from core.utils.run import run
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_paths import TnsPaths


class BuildTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_name_with_space = Settings.AppName.WITH_SPACE
    app_path = TnsPaths.get_app_path(app_name=app_name)
    app_temp_path = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', 'TestApp')
    debug_apk = "app-debug.apk"
    app_identifier = "org.nativescript.testapp"

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.create(cls.app_name_with_space, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Folder.clean(os.path.join(cls.app_name, 'hooks'))
        Folder.clean(os.path.join(cls.app_name, 'node_modules'))
        Folder.clean(os.path.join(cls.app_name_with_space, 'hooks'))
        Folder.clean(os.path.join(cls.app_name_with_space, 'node_modules'))
        Tns.platform_add_android(cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.platform_add_android(app_name='"' + cls.app_name_with_space + '"',
                                 framework_path=Settings.Android.FRAMEWORK_PATH, verify=False)
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
        Folder.clean(cls.app_name_with_space)

    def test_001_build_android(self):
        Tns.build_android(self.app_name)
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.plist'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.android.js'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.ios.js'))

        src = os.path.join(self.app_name, 'app', 'app.js')
        dest_1 = os.path.join(self.app_name, 'app', 'new.android.js')
        dest_2 = os.path.join(self.app_name, 'app', 'new.ios.js')
        File.copy(src, dest_1)
        File.copy(src, dest_2)

        result = Tns.build_android(self.app_name)
        assert "Gradle build..." in result.output, "Gradle build not called."
        assert result.output.count("Gradle build...") == 1, "Only one gradle build is triggered."

        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.plist'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.android.js'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.ios.js'))

        # Verify apk does not contain aar files
        archive = os.path.join(TnsPaths.get_apk_path(self.app_name), self.debug_apk)
        File.unzip(archive, 'temp')
        # Clean META-INF folder. It contains com.android.support.... files which are expected to be there due to
        # https://github.com/NativeScript/nativescript-cli/pull/3923
        Folder.clean(os.path.join(self.app_name, 'temp', 'META-INF'))
        temp_folder = os.path.join(self.app_name, 'temp')
        assert not File.pattern_exists(temp_folder, '*.aar')
        assert not File.pattern_exists(temp_folder, '*.plist')
        assert not File.pattern_exists(temp_folder, '*.android.*')
        assert not File.pattern_exists(temp_folder, '*.ios.*')
        Folder.clean(temp_folder)

        # Verify incremental native build
        result = Tns.exec_command(command='build --clean', bundle=True, path=self.app_name,
                                  platform=Platform.ANDROID)
        assert "Gradle clean..." in result.output, "Gradle clean is not called."
        assert "Gradle build..." in result.output, "Gradle build is not called."
        assert result.output.count("Gradle build...") == 1, "More than 1 gradle build is triggered."

    def test_002_build_android_release(self):
        Tns.build_android(self.app_name, release=True)

        # Configs are respected
        assert File.exists(TnsPaths.get_apk_path(self.app_name, release=True))

        # Create zip
        command = "tar -czf " + self.app_name + "/app/app.tar.gz " + self.app_name + "/app/app.js"
        run(command, wait=True)
        assert File.exists(os.path.join(self.app_name, 'app', 'app.tar.gz'))

    def test_301_build_project_with_space_release(self):

        # Ensure ANDROID_KEYSTORE_PATH contain spaces (verification for CLI issue 2650)
        Folder.create("with space")
        file_name = os.path.basename(Settings.Android.ANDROID_KEYSTORE_PATH)
        cert_with_space_path = os.path.join("with space", file_name)
        File.copy(Settings.Android.ANDROID_KEYSTORE_PATH, cert_with_space_path)

        Tns.build_android(app_name='"' + self.app_name_with_space + '"', release=True)
        output = File.read(os.path.join(self.app_name_with_space, "package.json"))
        assert self.app_identifier in output.lower()

        output = File.read(os.path.join(TnsPaths.get_platforms_android_src_main_path(self.app_name_with_space),
                                        'AndroidManifest.xml'))
        assert self.app_identifier in output.lower()

    def test_302_build_project_with_space_debug_with_plugin(self):
        # skip remove platform because androidx is not released official
        # Tns.platform_remove(app_name='"' + self.app_name_with_space + '"', platform=Platform.ANDROID)
        Npm.install(package='nativescript-mapbox', option='--save', folder=self.app_name_with_space)
        result = Tns.build_android(app_name='"' + self.app_name_with_space + '"')
        assert "Project successfully built" in result.output

    def test_310_build_android_with_custom_compile_sdk_new(self):
        Tns.platform_remove(self.app_name, platform=Platform.ANDROID)
        Tns.platform_add_android(self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.exec_command(command='build --compileSdk 28', path=self.app_name,
                         platform=Platform.ANDROID, bundle=True)

        File.delete(self.debug_apk)
        Tns.exec_command(command='build --copy-to ./', path=self.app_name,
                         platform=Platform.ANDROID, bundle=True)
        assert File.exists(self.debug_apk)
        File.delete(self.debug_apk)

    def test_441_android_typings(self):
        Tns.exec_command(command='build --androidTypings', path=self.app_name,
                         platform=Platform.ANDROID, bundle=True)
        assert File.exists(os.path.join(self.app_name, 'android.d.ts'))
        assert File.exists(os.path.join(self.app_name, 'android-declarations.d.ts'))

    def test_450_resources_update_android(self):
        target_app = os.path.join(self.app_name, 'app', 'App_Resources')
        source_app = os.path.join(TEST_RUN_HOME, 'assets', 'apps', 'test-app-js-41', 'app', 'App_Resources')
        Folder.clean(target_app)
        Folder.copy(source_app, target_app)

        result = Tns.exec_command(command='resources update android', path=self.app_name)

        assert "Successfully updated your project's application resources '/Android' directory structure" in \
               result.output
        assert "The previous version of your Android application resources has been renamed to '/Android-Pre-v4'" in \
               result.output
        assert File.exists(os.path.join(TnsPaths.get_path_app_resources(self.app_name), 'Android-Pre-v4', 'app.gradle'))
        assert File.exists(os.path.join(TnsPaths.get_path_app_resources(self.app_name), 'Android', 'app.gradle'))
        assert File.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name),
                                        'AndroidManifest.xml'))
        assert Folder.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name), 'assets'))
        assert Folder.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name), 'java'))
        assert Folder.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name), 'res', 'values'))

        Tns.prepare_android(self.app_name)
        assert File.exists(
            os.path.join(TnsPaths.get_platforms_android_src_main_path(self.app_name), 'AndroidManifest.xml'))

    def test_451_resources_update(self):
        target_app = os.path.join(self.app_name, 'app', 'App_Resources')
        source_app = os.path.join(TEST_RUN_HOME, 'assets', 'apps', 'test-app-js-41', 'app', 'App_Resources')
        Folder.clean(target_app)
        Folder.copy(source_app, target_app)

        result = Tns.exec_command(command='resources update', path=self.app_name)

        assert "Successfully updated your project's application resources '/Android' directory structure" in \
               result.output
        assert "The previous version of your Android application resources has been renamed to '/Android-Pre-v4'" in \
               result.output
        assert File.exists(os.path.join(TnsPaths.get_path_app_resources(self.app_name), 'Android-Pre-v4', 'app.gradle'))
        assert File.exists(os.path.join(TnsPaths.get_path_app_resources(self.app_name), 'Android', 'app.gradle'))
        assert File.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name),
                                        'AndroidManifest.xml'))
        assert Folder.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name), 'assets'))
        assert Folder.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name), 'java'))
        assert Folder.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name), 'res', 'values'))
        Tns.prepare_android(self.app_name)
        assert File.exists(
            os.path.join(TnsPaths.get_platforms_android_src_main_path(self.app_name), 'AndroidManifest.xml'))
    #
    # @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    # def test_001_build_ios(self):
    #     Tns.platform_remove(self.app_name, platform=Platform.ANDROID)
    #     Tns.build_ios(self.app_name)
    #     Tns.build_ios(self.app_name, release=True)
    #     Tns.build_ios(self.app_name, for_device=True)
    #     Tns.build_ios(self.app_name, for_device=True, release=True)
    #     assert not File.exists(os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name), '*.aar'))
    #     assert not File.exists(os.path.join(TnsPaths.get_platforms_ios_npm_modules(self.app_name), '*.framework'))
    #
    #     # Verify ipa has both armv7 and arm64 archs
    #     ipa_path = TnsPaths.get_ipa_path(app_name=self.app_name, release=True, for_device=True)
    #     run("mv " + ipa_path + " TestApp-ipa.tgz")
    #     run("unzip -o TestApp-ipa.tgz")
    #     result = run("lipo -info Payload/TestApp.app/TestApp")
    #     Folder.clean("Payload")
    #     assert "Architectures in the fat file: Payload/TestApp.app/TestApp are: armv7 arm64" in result.output
    #
    # @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    # def test_190_build_ios_distribution_provisions(self):
    #     Tns.platform_remove(self.app_name, platform=Platform.ANDROID)
    #     result = Tns.exec_command(command='build ios --provision', path=self.app_name)
    #     assert "Provision Name" in result.output
    #     assert "Provision UUID" in result.output
    #     assert "App Id" in result.output
    #     assert "Team" in result.output
    #     assert "Type" in result.output
    #     assert "Due" in result.output
    #     assert "Devices" in result.output
    #     assert Settings.IOS.PROVISIONING in result.output
    #     assert Settings.IOS.DISTRIBUTION_PROVISIONING in result.output
    #     assert Settings.IOS.DEVELOPMENT_TEAM in result.output
    #
    #     # Build with correct distribution provision
    #     Tns.build_ios(self.app_name, provision=Settings.IOS.DISTRIBUTION_PROVISIONING, for_device=True, release=True)
    #
    #     # Verify that passing wrong provision shows user friendly error
    #     result = Tns.build_ios(self.app_name, provision="fake", verify=False)
    #     assert "Failed to find mobile provision with UUID or Name: fake" in result.output
    #
    # @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    # def test_310_build_ios_with_copy_to(self):
    #     Tns.platform_remove(self.app_name, platform=Platform.IOS)
    #     Tns.exec_command(command='build --copy-to ' + TEST_RUN_HOME, path=self.app_name,
    #                      platform=Platform.IOS, bundle=True)
    #     assert Folder.exists(os.path.join(TEST_RUN_HOME, 'TestApp.app'))
    #     Tns.exec_command(command='build --copy-to ' + TEST_RUN_HOME, path=self.app_name, platform=Platform.IOS,
    #                      bundle=True, for_device=True, release=True, provision=Settings.IOS.PROVISIONING)
    #     assert File.exists(os.path.join(TEST_RUN_HOME, 'TestApp.ipa'))
    #
    # @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    # def test_320_build_ios_with_custom_entitlements(self):
    #     # Add entitlements in app/App_Resources/iOS/app.entitlements
    #     source = os.path.join(TEST_RUN_HOME, 'assets', 'entitlements', 'app.entitlements')
    #     target = os.path.join(self.app_name, 'app', 'App_Resources', 'iOS', 'app.entitlements')
    #     File.copy(source, target)
    #
    #     # Build again and verify entitlements are merged
    #     Tns.build_ios(self.app_name)
    #     entitlements_path = os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name), self.app_name,
    #                                      'TestApp.entitlements')
    #     assert File.exists(entitlements_path), "Entitlements file is missing!"
    #     entitlements_content = File.read(entitlements_path)
    #     assert '<key>aps-environment</key>' in entitlements_content, "Entitlements file content is wrong!"
    #     assert '<string>development</string>' in entitlements_content, "Entitlements file content is wrong!"
    #
    #     # Install plugin with entitlements, build again and verify entitlements are merged
    #     plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'plugins', 'nativescript-test-entitlements-1.0.0.tgz')
    #     Npm.install(package=plugin_path, option='--save', folder=self.app_name)
    #
    #     Tns.build_ios(self.app_name)
    #     entitlements_content = File.read(entitlements_path)
    #     assert '<key>aps-environment</key>' in entitlements_content, "Entitlements file content is wrong!"
    #     assert '<string>development</string>' in entitlements_content, "Entitlements file content is wrong!"
    #     assert '<key>inter-app-audio</key>' in entitlements_content, "Entitlements file content is wrong!"
    #     assert '<true/>' in entitlements_content, "Entitlements file content is wrong!"
    #
    #     # Build in release, for device (provision without entitlements)
    #     result = Tns.build_ios(self.app_name, for_device=True, release=True, verify=False)
    #     assert "Provisioning profile" in result.output
    #     assert "doesn't include the aps-environment and inter-app-audio entitlements" in result.output
