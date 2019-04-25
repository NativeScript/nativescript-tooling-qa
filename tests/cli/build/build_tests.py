import datetime
import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.settings.Settings import TEST_RUN_HOME
from core.utils.device.adb import Adb
from core.utils.file_utils import File, Folder
from core.utils.npm import Npm
from core.utils.run import run
from data.apps import Apps
from products.nativescript.tns import Tns
from products.nativescript.tns_paths import TnsPaths


class BuildTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_name_with_space = Settings.AppName.WITH_SPACE
    app_path = TnsPaths.get_app_path(app_name=app_name)
    app_temp_path = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', 'TestApp')
    debug_apk = "app-debug.apk"
    release_apk = "app-release.apk"
    app_identifier = "org.nativescript.testapp"

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(cls.app_name, app_data=Apps.MIN_JS, update=False)
        Tns.create(cls.app_name_with_space, update=False)
        Tns.platform_add_android(cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.platform_add_android(app_name='"' + cls.app_name_with_space + '"', framework_path=Settings.Android.FRAMEWORK_PATH, verify=False)
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
        Tns.build_android(self.app_name, bundle=True)
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.plist'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.android.js'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.ios.js'))

        src = os.path.join(self.app_name, 'app', 'app.js')
        dest_1 = os.path.join(self.app_name, 'app', 'new.android.js')
        dest_2 = os.path.join(self.app_name, 'app', 'new.ios.js')
        File.copy(src, dest_1)
        File.copy(src, dest_2)

        before_build = datetime.datetime.now()
        result = Tns.build_android(self.app_name, bundle=True)
        after_build = datetime.datetime.now()
        assert "Gradle build..." in result.output, "Gradle build not called."
        assert result.output.count("Gradle build...") is 1, "Only one gradle build is triggered."
        assert (after_build - before_build).total_seconds() < 20, "Incremental build takes more then 20 sec."

        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.plist'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.android.js'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.ios.js'))

        #Verify apk does not contain aar files
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
        before_build = datetime.datetime.now()
        result = Tns.exec_command(command='build --clean', bundle=True, path=self.app_name,
                                  platform=Platform.ANDROID)
        after_build = datetime.datetime.now()
        build_time = (after_build - before_build).total_seconds()
        assert "Gradle clean..." in result.output, "Gradle clean is not called."
        assert "Gradle build..." in result.output, "Gradle build is not called."
        assert result.output.count("Gradle build...") is 1, "More than 1 gradle build is triggered."
        assert build_time > 10, "Clean build takes less then 15 sec."
        assert build_time < 90, "Clean build takes more than 90 sec."

    def test_002_build_android_release(self):
        Tns.build_android(self.app_name, bundle=True, release=True)

        # Configs are respected
        assert File.exists(os.path.join(TnsPaths.get_apk_path(self.app_name), 'release', self.release_apk))

        # Create zip
        command = "tar -czf " + self.app_name + "/app/app.tar.gz " + self.app_name + "/app/app.js"
        run(command, wait=False)
        assert File.exists(os.path.join(self.app_name, 'app', 'app.tar.gz'))

    def test_301_build_project_with_space_release(self):

        # TO DO Ensure ANDROID_KEYSTORE_PATH contain spaces (verification for CLI issue 2650)
        Folder.create("with space")
        base_path, file_name = os.path.split(Settings.Android.ANDROID_KEYSTORE_PATH)
        cert_with_space_path = os.path.join("with space", file_name)
        File.copy(Settings.Android.ANDROID_KEYSTORE_PATH, cert_with_space_path)

        Tns.build_android(app_name='"' + self.app_name_with_space + '"', bundle=True, release=True)
        output = File.read(os.path.join(self.app_name_with_space, "package.json"))
        assert self.app_identifier in output.lower()

        output = File.read(os.path.join(TnsPaths.get_platforms_android_src_main_path(self.app_name_with_space),
                                        'AndroidManifest.xml'))
        assert self.app_identifier in output.lower()

    def test_302_build_project_with_space_debug_with_plugin(self):
        Tns.platform_remove(app_name='"' + self.app_name_with_space + '"', platform=Platform.ANDROID)
        Npm.install(package='nativescript-mapbox', option='--save', folder=self.app_name_with_space)
        result = Tns.build_android(app_name='"' + self.app_name_with_space + '"', bundle=True)
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
        target_app = os.path.join(self.app_name)
        source_app = os.path.join(TEST_RUN_HOME, 'assets', 'apps', 'test-app-js-41')
        Folder.clean(target_app)
        Folder.copy(source_app, target_app)

        result = Tns.exec_command(command='resources update android', path=self.app_name)

        assert "Successfully updated your project's application resources '/Android' directory structure" in \
               result.output
        assert "The previous version of your Android application resources has been renamed to '/Android-Pre-v4'" in \
               result.output
        assert File.exists(os.path.join(TnsPaths.get_path_app_resources(self.app_name), 'Android-Pre-v4', 'app.gradle'))
        assert File.exists(os.path.join(TnsPaths.get_path_app_resources(self.app_name), 'Android', 'app.gradle'))
        assert File.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name), 'AndroidManifest.xml'))
        assert Folder.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name), 'assets'))
        assert Folder.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name), 'java'))
        assert Folder.exists(os.path.join(TnsPaths.get_path_app_resources_main_android(self.app_name), 'res', 'values'))

        Tns.prepare_android(self.app_name)
        assert File.exists(
            os.path.join(TnsPaths.get_platforms_android_src_main_path(self.app_name), 'AndroidManifest.xml'))

    def test_451_resources_update(self):
        target_app = os.path.join(self.app_name)
        source_app = os.path.join(TEST_RUN_HOME, 'assets', 'apps', 'test-app-js-41')
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
