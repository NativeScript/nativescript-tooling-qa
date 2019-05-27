import os
import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder, File
from data.changes import Changes
from data.sync.hello_world_js import sync_hello_world_ts
from data.templates import Template
from products.nativescript.tns import Tns


class TnsRunTSTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_TS.local_package, update=True)
        src = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'logs', 'hello-world-ts', 'app.ts')
        target = os.path.join(Settings.TEST_RUN_HOME, cls.app_name, 'app')
        File.copy(source=src, target=target)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS is OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsRunTest.setUp(self)
        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        for change in [Changes.TSHelloWord.CSS, Changes.TSHelloWord.XML, Changes.TSHelloWord.TS]:
            source_src = os.path.join(self.target_project_dir, 'app', os.path.basename(change.file_path))
            target_src = os.path.join(self.source_project_dir, change.file_path)
            File.clean(path=target_src)
            File.copy(source=source_src, target=target_src)

    def test_100_run_android(self):
        sync_hello_world_ts(self.app_name, Platform.ANDROID, self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_100_run_ios(self):
        sync_hello_world_ts(self.app_name, Platform.IOS, self.sim)

    def test_200_run_android_no_hmr(self):
        sync_hello_world_ts(self.app_name, Platform.ANDROID, self.emu, hmr=False)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_200_run_ios_no_hmr(self):
        sync_hello_world_ts(self.app_name, Platform.IOS, self.sim, hmr=False)

    def test_300_run_android_bundle_aot(self):
        sync_hello_world_ts(self.app_name, Platform.ANDROID, self.emu, aot=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_300_run_ios_bundle_aot(self):
        sync_hello_world_ts(self.app_name, Platform.IOS, self.sim, aot=True)

    def test_310_run_android_bundle_uglify(self):
        sync_hello_world_ts(self.app_name, Platform.ANDROID, self.emu, uglify=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_310_run_ios_bundle_uglify(self):
        sync_hello_world_ts(self.app_name, Platform.IOS, self.sim, uglify=True)

    def test_320_run_android_bundle_aot_and_uglify(self):
        sync_hello_world_ts(self.app_name, Platform.ANDROID, self.emu, aot=True, uglify=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_320_run_ios_bundle_aot_and_uglify(self):
        sync_hello_world_ts(self.app_name, Platform.IOS, self.sim, aot=True, uglify=True)
