import os
import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import Folder, File
from core.utils.docker import Docker
from data.changes import Changes
from data.sync.hello_world_js import sync_hello_world_js, run_hello_world_js_ts
from data.templates import Template
from products.nativescript.tns import Tns


class TnsRunJSTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        Docker.start()

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        src = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'logs', 'hello-world-js', 'app.js')
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
        for change in [Changes.JSHelloWord.CSS, Changes.JSHelloWord.XML, Changes.JSHelloWord.JS]:
            source_src = os.path.join(self.target_project_dir, 'app', os.path.basename(change.file_path))
            target_src = os.path.join(self.source_project_dir, change.file_path)
            File.clean(path=target_src)
            File.copy(source=source_src, target=target_src)

    @classmethod
    def tearDownClass(cls):
        TnsRunTest.tearDownClass()
        Docker.stop()

    def test_100_run_android(self):
        sync_hello_world_js(self.app_name, Platform.ANDROID, self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_100_run_ios(self):
        sync_hello_world_js(self.app_name, Platform.IOS, self.sim)

    def test_310_run_android_bundle_uglify(self):
        sync_hello_world_js(self.app_name, Platform.ANDROID, self.emu, uglify=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_310_run_ios_bundle_uglify(self):
        sync_hello_world_js(self.app_name, Platform.IOS, self.sim, uglify=True)

    def test_320_run_android_release_snapshot_uglify(self):
        run_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu, uglify=True, release=True,
                              snapshot=True)
