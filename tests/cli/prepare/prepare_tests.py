import os
import re
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import File, Folder
from core.utils.run import run
from data.templates import Template
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
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)
        Tns.platform_add_android(cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
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

    def test_100_prepare_android(self):
        Tns.prepare_android(self.app_name)
        result = Tns.prepare_android(self.app_name)
        # assert "Skipping prepare" in result.output
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)
        result = Tns.prepare_android(self.app_name)
        assert "Preparing project..." in result.output

    @unittest.skip("https://github.com/NativeScript/nativescript-dev-webpack/issues/892")
    def test_200_prepare_xml_error(self):
        Tns.platform_remove(self.app_name, platform=Platform.ANDROID)
        Sync.replace(app_name=self.app_name, change_set=Changes.AppFileChanges.CHANGE_XML_INVALID_SYNTAX)
        result = Tns.prepare_android(self.app_name)
        assert "main-page.xml has syntax errors." in result.output
        assert "unclosed xml attribute" in result.output

    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, "Skip on Windows")
    def test_210_platform_not_need_remove_after_bitcode_error(self):
        # https://github.com/NativeScript/nativescript-cli/issues/3741
        Tns.platform_remove(self.app_name, platform=Platform.ANDROID)
        run("touch a", cwd=os.path.join(self.app_name, 'app'))
        run("ln -s a b", cwd=os.path.join(self.app_name, 'app'))
        run("rm a", cwd=os.path.join(self.app_name, 'app'))
        result = Tns.prepare_android(self.app_name)
        assert "Project successfully prepared" in result.output

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_100_prepare_ios(self):
        Tns.prepare_ios(self.app_name)
        result = Tns.prepare_ios(self.app_name)
        # assert "Skipping prepare" in result.output
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)
        result = Tns.prepare_ios(self.app_name)
        assert "Preparing project..." in result.output

        # Verify Xcode Schemes
        result = run("xcodebuild -project " + os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name),
                                                           'TestApp.xcodeproj', ' -list'))
        assert "This project contains no schemes." not in result.output
        result1 = re.search(r"Targets:\n\s*TestApp", result.output)
        assert result1 is not None
        result1 = re.search(r"Schemes:\n\s*TestApp", result.output)
        assert result1 is not None

        Tns.prepare_android(self.app_name)
        Tns.prepare_ios(self.app_name)
        result = Tns.prepare_ios(self.app_name)
        # assert "Skipping prepare" in result.output

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_200_prepare_additional_appresources(self):
        Tns.prepare_ios(self.app_name)

        # Create new files in AppResources
        File.copy(os.path.join(TnsPaths.get_path_app_resources(self.app_name), 'iOS', 'Assets.xcassets',
                               'AppIcon.appiconset', 'icon-76.png'),
                  os.path.join(TnsPaths.get_path_app_resources(self.app_name), 'iOS', 'newDefault.png'))

        Tns.prepare_ios(self.app_name)

        # Verify XCode Project include files from App Resources folder
        result = run("cat " + os.path.join(TnsPaths.get_platforms_ios_folder(self.app_name), 'TestApp.xcodeproj',
                                           'project.pbxproj | grep newDefault.png'))
        assert "newDefault.png" in result.output

    @unittest.skip("This test doesn't pass now. Remove skip after webpack only")
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_210_prepare_android_does_not_prepare_ios(self):
        Tns.plugin_add(plugin_name='nativescript-social-share', path=self.app_name)
        Tns.plugin_add(plugin_name='nativescript-iqkeyboardmanager@1.2.0', path=self.app_name)

        result = Tns.prepare_android(self.app_name)
        assert "Successfully prepared plugin nativescript-social-share for android" in result.output
        assert "nativescript-iqkeyboardmanager is not supported for android" in result.output

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_220_prepare_ios_with_provisioning(self):
        # Prepare with --provision (debug, emulator)
        Tns.prepare_ios(self.app_name, provision=Settings.IOS.PROVISIONING)

        # Prepare with --provision (release, emulator)
        Tns.prepare_ios(self.app_name, provision=Settings.IOS.PROVISIONING, release=True)

        # Prepare with --provision (debug, device)
        Tns.prepare_ios(self.app_name, for_device=True, provision=Settings.IOS.PROVISIONING)

        # Prepare with --provision (release, device)
        Tns.prepare_ios(self.app_name, release=True, for_device=True, provision=Settings.IOS.PROVISIONING)
