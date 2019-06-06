import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder
from core.utils.json_utils import JsonUtils
from data.apps import Apps
from products.nativescript.tns import Tns
from products.nativescript.tns_assert import TnsAssert


class BuildTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(cls.app_name, app_data=Apps.MIN_JS, update=False)
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsTest.setUp(self)
        Folder.clean(self.app_name)
        Folder.copy(source=self.target_project_dir, target=self.source_project_dir)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_100_platform_add_android(self):
        """ Default `tns platform add` command"""
        Tns.platform_add_android(self.app_name)

    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_100_platform_add_ios(self):
        """ Add platform from local package"""
        Tns.platform_add_ios(self.app_name)

    def test_110_platform_add_android_framework_path(self):
        Tns.platform_add_android(self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)

    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_110_platform_add_ios_framework_path(self):
        Tns.platform_add_ios(self.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def test_120_platform_add_android_inside_project(self):
        """ Add platform inside project folder (not using --path)"""
        project_path = os.path.join(Settings.TEST_RUN_HOME, self.app_name)
        Folder.navigate_to(self.app_name)
        command = 'platform add android'
        result = Tns.exec_command(command=command, cwd=project_path)
        TnsAssert.platform_added(app_name=self.app_name, platform=Platform.ANDROID, output=result.output)
        Folder.navigate_to(Settings.TEST_RUN_HOME)

    def test_130_platform_remove_and_platform_add_android_custom_version(self):
        """Verify platform add supports custom versions"""
        Folder.navigate_to(Settings.TEST_RUN_HOME)
        Tns.platform_add_android(self.app_name, version='5.0.0')
        Tns.platform_add_android(self.app_name, version='rc')
        Tns.platform_remove(self.app_name, platform=Platform.ANDROID)

    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_130_platform_remove_and_platform_add_ios_custom_version(self):
        """Verify platform add supports custom versions"""
        Tns.platform_add_ios(self.app_name, version='4.2.0')
        Tns.platform_add_ios(self.app_name, version='rc')
        Tns.platform_remove(self.app_name, platform=Platform.IOS)

    def test_140_platform_update_android(self):
        """Update platform"""

        # Create project with tns-android@4
        Tns.platform_add_android(self.app_name, version='4.0.0')

        # Update platform to 5
        Tns.platform_update(self.app_name, platform=Platform.ANDROID, version='5.0.0')

    @unittest.skip("Skip because of https://github.com/NativeScript/nativescript-cli/issues/4681")
    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_140_platform_update_ios(self):
        """Update platform"""

        # Create project with tns-ios@4
        Tns.platform_add_ios(self.app_name, version='4.0.1')

        # Update platform to 5
        Tns.platform_update(self.app_name, platform=Platform.IOS, version='5.0.0')

    def test_150_platform_update_android_when_platform_not_added(self):
        """`platform update` should work even if platform is not added"""
        runtime_version = '5.3.1'
        command = 'platform update android@{0}'.format(runtime_version)
        result = Tns.exec_command(command=command, path=self.app_name)
        TnsAssert.platform_added(app_name=self.app_name, platform=Platform.ANDROID,
                                 version=runtime_version, output=result.output)

    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_150_platform_update_ios_when_platform_not_added(self):
        """`platform update` should work even if platform is not added"""
        runtime_version = '5.3.1'
        command = 'platform update ios@{0}'.format(runtime_version)
        result = Tns.exec_command(command=command, path=self.app_name)
        TnsAssert.platform_added(app_name=self.app_name, platform=Platform.IOS,
                                 version=runtime_version, output=result.output)

    def test_160_platform_clean_android(self):
        """Prepare after `platform clean` should add the same version that was before clean"""

        # Create project with tns-android@5.0.0
        Tns.platform_add_android(self.app_name, version='5.0.0')

        # Clean platform and verify platform is 5.0.0
        Tns.platform_clean(self.app_name, platform=Platform.ANDROID)
        package_json = os.path.join(self.app_name, 'package.json')
        json = JsonUtils.read(package_json)
        assert json['nativescript']['tns-android']['version'] == '5.0.0'

    def test_180_platform_list(self):
        """Platform list command should list installed platforms and if app is prepared for those platforms"""

        # `tns platform list` on brand new project
        result = Tns.platform_list(self.app_name)
        TnsAssert.platform_list_status(output=result.output, prepared=Platform.NONE, added=Platform.NONE)

        # `tns platform list` when android is added
        Tns.platform_add_android(self.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        result = Tns.platform_list(self.app_name)
        TnsAssert.platform_list_status(output=result.output, prepared=Platform.NONE, added=Platform.ANDROID)

        # `tns platform list` when android is prepared
        Tns.prepare_android(self.app_name)
        result = Tns.platform_list(self.app_name)
        TnsAssert.platform_list_status(output=result.output, prepared=Platform.ANDROID, added=Platform.ANDROID)

        # `tns platform list` when ios is added
        Tns.platform_add_ios(self.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)
        result = Tns.platform_list(self.app_name)
        TnsAssert.platform_list_status(output=result.output, prepared=Platform.ANDROID, added=Platform.BOTH)

        # `tns platform list` when ios prepared android is already prepared
        Tns.prepare_ios(self.app_name)
        result = Tns.platform_list(self.app_name)
        TnsAssert.platform_list_status(output=result.output, prepared=Platform.BOTH, added=Platform.BOTH)
