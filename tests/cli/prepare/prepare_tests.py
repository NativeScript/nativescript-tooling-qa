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
from data.apps import Apps
from products.nativescript.tns import Tns
from products.nativescript.tns_paths import TnsPaths


class PrepareTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_name_with_space = Settings.AppName.WITH_SPACE
    app_path = TnsPaths.get_app_path(app_name=app_name)
    app_temp_path = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', 'TestApp')
    debug_apk = "app-debug.apk"
    release_apk = "app-release.apk"
    app_identifier = "org.nativescript.testapp"
    CHANGE_XML_INVALID_SYNTAX = ['app/main-page.xml', '</Page>', '</Page']

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(cls.app_name, app_data=Apps.MIN_JS, update=False)
        Tns.create(cls.app_name_with_space, update=False)
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
        Tns.prepare_android(self.app_name, bundle=True)

        Tns.prepare_android(self.app_name, bundle=True)

        src = os.path.join(self.app_name, 'app', 'app.js')
        dest_1 = os.path.join(self.app_name, 'app', 'new.android.js')
        File.copy(src, dest_1)

        result = Tns.build_android(self.app_name, bundle=True)
        assert "Gradle build..." in result.output, "Gradle build not called."
        assert result.output.count("Gradle build...") == 1, "Only one gradle build is triggered."

    def test_201_prepare_xml_error(self):
        Tns.platform_remove(self.app_name, platform=Platform.ANDROID)
        main_page = os.path.join(Settings.TEST_RUN_HOME, self.app_name, 'app', 'main-main-page.xml')
        File.replace(path=main_page, old_string='<Page>', new_string='<Page')
        result = Tns.prepare_android(self.app_name, bundle=True)
        assert "main-page.xml has syntax errors." in result.output
        assert "unclosed xml attribute" in result.output

    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, "Skip on Windows")
    def test_210_platform_not_need_remove_after_bitcode_error(self):
        # https://github.com/NativeScript/nativescript-cli/issues/3741
        Tns.platform_remove(self.app_name, platform=Platform.ANDROID)
        Folder.navigate_to(self.app_name + "/app")
        path = os.path.join(self.app_name + "/app")
        run("touch a")
        run("ln -s a b")
        run("rm a")
        Folder.navigate_to(folder=TEST_RUN_HOME, relative_from_current_folder=False)
        result = Tns.prepare_android(self.app_name, bundle=True)
        assert "Project successfully prepared" in result.output

    def test_330_prepare_android_next(self):
        Tns.platform_remove(self.app_name, platform=Platform.ANDROID)
        Tns.platform_add_android(cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH, version=next)
        Folder.clean(os.path.join(self.app_name, "node_modules"))
        Folder.clean(os.path.join(self.app_name, "platforms"))
        android_version = Npm.get_version("tns-android@next")
        File.replace(file_path=os.path.join(self.app_name, 'package.json'), str1=android_version, str2="next")
        Tns.prepare_android(self.app_name, bundle=True)
