import datetime
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
        result = Tns.build_android(self.app_name)
        after_build = datetime.datetime.now()
        assert "Gradle build..." in result.output, "Gradle build not called."
        assert result.output.count("Gradle build...") is 1, "Only one gradle build is triggered."
        assert (after_build - before_build).total_seconds() < 20, "Incremental build takes more then 20 sec."

        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.plist'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.android.js'))
        assert not File.exists(os.path.join(TnsPaths.get_platforms_android_folder(self.app_name), '*.ios.js'))

        # TO DO
        #Verify apk does not contain aar files

        before_build = datetime.datetime.now()
        result = Tns.exec_command(command='build android --clean', path=self.app_name, platform=Platform.ANDROID)
        # result = Tns.build_android(self.app_name, "--clean": "")
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
        assert File.exists(os.path.join(self.app_name, TnsPaths.get_apk_path(), self.release_apk))

    def test_301_build_project_with_space_release(self):
        Tns.platform_add_android(self.app_name_with_space, framework_path=Settings.Android.FRAMEWORK_PATH)

        # TO DO Ensure ANDROID_KEYSTORE_PATH contain spaces (verification for CLI issue 2650)

        Tns.build_android(self.app_name, bundle=True, release=True)
        output = File.read(os.path.join(self.app_name_with_space, "package.json"))
        assert self.app_identifier in output.lower()

        output = File.read(os.path.join(self.app_name_with_space, TnsPaths.get_platforms_android_src_main_path(),
                                        'AndroidManifest.xml'))
        assert self.app_identifier in output.lower()

    def test_302_build_project_with_space_debug_with_plugin(self):
        Tns.platform_remove(app_name=self.app_name, platform=Platform.ANDROID)
        Npm.install(package='nativescript-mapbox', option='--save', folder=self.app_name_with_space)
        result = Tns.build_android(self.app_name_with_space, bundle=True)
        assert "Project successfully built" in result.output

    def test_310_build_android_with_custom_compile_sdk_new(self):
        Folder.clean(self.app_path)
        Folder.copy(self.app_temp_path, self.app_path)
        Tns.platform_add_android(self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        Tns.build_android(self.app_name, bundle=True, release=True)
        
        # Tns.build_android(attributes={"--compileSdk": "28", "--path": self.app_name})

