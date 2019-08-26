"""
Tests for app size ot {N} apps.
"""
import logging
import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.file_utils import File, Folder
from core.utils.perf_utils import PerfUtils
from core.utils.run import run
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_paths import TnsPaths


class AppSizeTests(TnsTest):
    js_app = Settings.AppName.DEFAULT + 'JS'
    ng_app = Settings.AppName.DEFAULT + 'NG'

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

        # Create JS app and copy to temp data folder
        Tns.create(app_name=cls.js_app, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=cls.js_app, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.js_app, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Create NG app and copy to temp data folder
        Tns.create(app_name=cls.ng_app, template=Template.HELLO_WORLD_NG.local_package, update=True)
        Tns.platform_add_android(app_name=cls.ng_app, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.ng_app, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Build apps
        Tns.build_android(cls.js_app, release=True, bundle=True, aot=True, uglify=True, snapshot=True)
        Tns.build_android(cls.ng_app, release=True, bundle=True, aot=True, uglify=True, snapshot=True)
        if Settings.HOST_OS == OSType.OSX:
            Tns.build_ios(cls.js_app, release=True, bundle=True, aot=True, uglify=True, for_device=True)
            Tns.build_ios(cls.ng_app, release=True, bundle=True, aot=True, uglify=True, for_device=True)

    def test_001_js_app_app_resources(self):
        folder = os.path.join(TnsPaths.get_app_path(app_name=self.js_app), 'app')
        assert PerfUtils.is_value_in_range(actual=Folder.get_size(folder), expected=2991548, tolerance=0.1)

    def test_002_js_app_node_modules(self):
        folder = os.path.join(TnsPaths.get_app_path(app_name=self.js_app), 'node_modules')
        assert PerfUtils.is_value_in_range(actual=Folder.get_size(folder), expected=51791943, tolerance=0.2)

    def test_003_js_app_apk(self):
        # Extract APK
        apk = TnsPaths.get_apk_path(app_name=self.js_app, release=True)
        extracted_apk = os.path.join(Settings.TEST_OUT_TEMP, 'js-apk')
        File.unzip(file_path=apk, dest_dir=extracted_apk)

        res = os.path.join(extracted_apk, 'res')
        assets_app = os.path.join(extracted_apk, 'assets', 'app')
        assets_snapshots = os.path.join(extracted_apk, 'assets', 'snapshots')
        lib = os.path.join(extracted_apk, 'lib')
        run(cmd='du -hs *', cwd=lib, wait=True, log_level=logging.INFO)

        # Verify content of APK
        assert PerfUtils.is_value_in_range(actual=Folder.get_size(lib), expected=53997832, tolerance=0.1)
        assert PerfUtils.is_value_in_range(actual=Folder.get_size(res), expected=796627, tolerance=0.1)
        assert PerfUtils.is_value_in_range(actual=Folder.get_size(assets_app), expected=719734, tolerance=0.1)
        assert PerfUtils.is_value_in_range(actual=Folder.get_size(assets_snapshots), expected=8611480, tolerance=0.1)

        # Verify final apk size
        assert PerfUtils.is_value_in_range(actual=File.get_size(apk), expected=18216351, tolerance=0.05)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_102_js_app_ipa(self):
        ipa = TnsPaths.get_ipa_path(app_name=self.js_app, release=True, for_device=True)
        assert PerfUtils.is_value_in_range(actual=File.get_size(ipa), expected=16001936, tolerance=0.05)

    def test_100_ng_app_app_resources(self):
        app_folder = os.path.join(TnsPaths.get_app_path(app_name=self.ng_app), 'App_Resources')
        assert PerfUtils.is_value_in_range(actual=Folder.get_size(app_folder), expected=2986244, tolerance=0.1)

    def test_101_ng_app_node_modules(self):
        app_folder = os.path.join(TnsPaths.get_app_path(app_name=self.ng_app), 'node_modules')
        assert PerfUtils.is_value_in_range(actual=Folder.get_size(app_folder), expected=200248003, tolerance=0.2)

    def test_102_ng_app_apk(self):
        # Extract APK
        apk = TnsPaths.get_apk_path(app_name=self.ng_app, release=True)
        extracted_apk = os.path.join(Settings.TEST_OUT_TEMP, 'ng-apk')
        File.unzip(file_path=apk, dest_dir=extracted_apk)

        assets_app = os.path.join(extracted_apk, 'assets', 'app')
        assets_snapshots = os.path.join(extracted_apk, 'assets', 'snapshots')

        # No asserts for lib and res, since it is same as JS project
        assert PerfUtils.is_value_in_range(actual=Folder.get_size(assets_app), expected=1428593, tolerance=0.1)
        assert PerfUtils.is_value_in_range(actual=Folder.get_size(assets_snapshots), expected=18864972, tolerance=0.1)

        # Verify final apk size
        assert PerfUtils.is_value_in_range(actual=File.get_size(apk), expected=26965846, tolerance=0.05)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_102_ng_app_ipa(self):
        ipa = TnsPaths.get_ipa_path(app_name=self.ng_app, release=True, for_device=True)
        assert PerfUtils.is_value_in_range(actual=File.get_size(ipa), expected=16226626, tolerance=0.05)
