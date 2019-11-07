import os
import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.docker import Docker
from core.utils.file_utils import Folder
from data.sync.master_details_ng import sync_master_detail_ng, run_master_detail_ng
from data.templates import Template
from products.nativescript.tns import Tns


class TnsRunMasterDetailTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        Docker.start()

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.MASTER_DETAIL_NG.local_package, update=True)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsRunTest.setUp(self)
        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        source_src = os.path.join(self.target_project_dir, 'src')
        target_src = os.path.join(self.source_project_dir, 'src')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)

    @classmethod
    def tearDownClass(cls):
        TnsRunTest.tearDownClass()
        Docker.stop()

    def test_100_run_android(self):
        sync_master_detail_ng(self.app_name, Platform.ANDROID, self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_100_run_ios(self):
        sync_master_detail_ng(self.app_name, Platform.IOS, self.sim)

    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, 'temporary skip on windows')
    # TODO: remove skip when https://github.com/NativeScript/nativescript-dev-webpack/issues/1021 fixed
    def test_300_run_android_bundle_aot(self):
        sync_master_detail_ng(self.app_name, Platform.ANDROID, self.emu, aot=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_300_run_ios_bundle_aot(self):
        sync_master_detail_ng(self.app_name, Platform.IOS, self.sim, aot=True)

    @unittest.skip('Ignore because of https://github.com/NativeScript/nativescript-ui-feedback/issues/1297')
    def test_310_run_android_bundle_uglify(self):
        sync_master_detail_ng(self.app_name, Platform.ANDROID, self.emu, uglify=True)

    @unittest.skip('Ignore because of https://github.com/NativeScript/nativescript-ui-feedback/issues/1297')
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_310_run_ios_bundle_uglify(self):
        sync_master_detail_ng(self.app_name, Platform.IOS, self.sim, uglify=True)

    @unittest.skip('Ignore because of https://github.com/NativeScript/nativescript-ui-feedback/issues/1297')
    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, 'temporary skip on windows')
    # TODO: remove skip when https://github.com/NativeScript/nativescript-dev-webpack/issues/1021 fixed
    def test_320_run_android_bundle_aot_and_uglify(self):
        sync_master_detail_ng(self.app_name, Platform.ANDROID, self.emu, aot=True, uglify=True)

    @unittest.skip('Ignore because of https://github.com/NativeScript/nativescript-ui-feedback/issues/1297')
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_320_run_ios_bundle_aot_and_uglify(self):
        sync_master_detail_ng(self.app_name, Platform.IOS, self.sim, aot=True, uglify=True)

    @unittest.skip('Ignore because of https://github.com/NativeScript/nativescript-ui-feedback/issues/1297')
    def test_330_run_android_release_snapshot_aot_and_uglify(self):
        run_master_detail_ng(self.app_name, Platform.ANDROID, self.emu, aot=True, uglify=True,
                             release=True, snapshot=True)
