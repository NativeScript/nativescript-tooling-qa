import os
import unittest
from core.base_test.tns_test import TnsTest
from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.file_utils import File, Folder
from data.sync.hello_world_ng import preview_sync_hello_world_ng
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.preview_helpers import Preview


class TnsPreviewNGTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()

        # Download Preview and Playground packages
        Preview.get_app_packages()

        # Install Preview and Playground
        Preview.install_preview_app(cls.emu, Platform.ANDROID)
        if Settings.HOST_OS is OSType.OSX:
            Preview.install_preview_app(cls.sim, Platform.IOS)
            Preview.install_playground_app(cls.sim, Platform.IOS)

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_NG.local_package, update=True)
        src = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'logs', 'hello-world-ng', 'main.ts')
        target = os.path.join(Settings.TEST_RUN_HOME, cls.app_name, 'src')
        File.copy(src=src, target=target)
        src = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'logs', 'hello-world-ng', 'items.component.ts')
        target = os.path.join(Settings.TEST_RUN_HOME, cls.app_name, 'src', 'app', 'item')
        File.copy(src=src, target=target)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsTest.setUp(self)
        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        source_src = os.path.join(self.target_project_dir, 'src')
        target_src = os.path.join(self.source_project_dir, 'src')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)


class PreviewNGTests(TnsPreviewNGTests):

    def test_100_preview_android(self):
        """Preview project on emulator. Make valid changes in TS, CSS and HTML"""
        preview_sync_hello_world_ng(app_name=self.app_name, platform=Platform.ANDROID,
                                    device=self.emu, instrumented=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_100_preview_ios(self):
        """Preview project on simulator. Make valid changes in TS, CSS and HTML"""
        preview_sync_hello_world_ng(app_name=self.app_name, platform=Platform.IOS,
                                    device=self.sim, instrumented=True)

    def test_200_preview_android_bundle(self):
        """Preview project on emulator with --bundle. Make valid changes in TS, CSS and HTML"""
        preview_sync_hello_world_ng(app_name=self.app_name, platform=Platform.ANDROID,
                                    device=self.emu, instrumented=True, bundle=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_200_preview_ios_hmr(self):
        """Preview project on simulator with --bundle. Make valid changes in TS, CSS and HTML"""
        preview_sync_hello_world_ng(app_name=self.app_name, platform=Platform.IOS,
                                    device=self.sim, instrumented=True, bundle=True)

    def test_205_preview_android_hmr(self):
        """Preview project on emulator with --hmr. Make valid changes in TS, CSS and HTML"""
        preview_sync_hello_world_ng(app_name=self.app_name, platform=Platform.ANDROID,
                                    device=self.emu, instrumented=True, hmr=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_205_preview_ios_hmr(self):
        """Preview project on simulator with --hmr. Make valid changes in TS, CSS and HTML"""
        preview_sync_hello_world_ng(app_name=self.app_name, platform=Platform.IOS,
                                    device=self.sim, instrumented=True, hmr=True)
