import os
import unittest

import time

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.settings.Settings import TEST_RUN_HOME
from core.utils.file_utils import File, Folder
from core.utils.npm import Npm
from core.utils.run import run
from data.apps import Apps
from data.changes import Sync, Changes
from products.nativescript.tns import Tns
from products.nativescript.tns_paths import TnsPaths


class PrepareTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_path = TnsPaths.get_app_path(app_name=app_name)
    app_temp_path = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', 'TestApp')

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(cls.app_name, app_data=Apps.MIN_JS, update=False)
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
        Folder.clean(cls.app_name_with_space)

    # def test_101_prepare_android(self):
    #     Tns.prepare_android(self.app_name)
    #     result = Tns.prepare_android(self.app_name)
    #     assert "Skipping prepare" in result.output
    #     Sync.replace(app_name=self.app_name, change_set=self.js_change)
    #     result = Tns.prepare_android(self.app_name)
    #     assert "Preparing project..." in result.output

    def test_201_prepare_xml_error(self):
        Tns.platform_remove(self.app_name, platform=Platform.ANDROID)
        self.replace(self.app_name, self.CHANGE_XML_INVALID_SYNTAX)
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.CHANGE_XML_INVALID_SYNTAX)
        result = Tns.prepare_android(self.app_name)
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
        result = Tns.prepare_android(self.app_name)
        assert "Project successfully prepared" in result.output

    def test_330_prepare_android_next(self):
        Tns.platform_remove(self.app_name, platform=Platform.ANDROID)
        Tns.platform_add_android(self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH, version=next)
        Folder.clean(os.path.join(self.app_name, "node_modules"))
        Folder.clean(os.path.join(self.app_name, "platforms"))
        android_version = Npm.get_version("tns-android@next")
        File.replace(file_path=os.path.join(self.app_name, 'package.json'), str1=android_version, str2="next")
        Tns.prepare_android(self.app_name)

