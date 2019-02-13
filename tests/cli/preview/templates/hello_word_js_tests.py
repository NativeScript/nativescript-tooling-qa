import os
import unittest
from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from data.changes import Changes
from data.const import Colors
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.preview_helpers import Preview
from products.nativescript.tns_logs import TnsLogs
from data.sync.hello_world_js import preview_hello_world_js_ts

class TnsPreviewJSTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)
    emu = None
    sim = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

        # Boot emulator and simulator
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS == OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

        # Download Preview and Playground packages
        Preview.get_app_packages()

        # Install Preview and Playground
        Preview.install_preview_app(cls.emu, Platform.ANDROID)
        Preview.install_preview_app(cls.sim, Platform.IOS)
        Preview.install_playground_app(cls.sim, Platform.IOS)

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        src = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'logs', 'hello-world-js', 'app.js')
        target = os.path.join(Settings.TEST_RUN_HOME, cls.app_name, 'app')
        File.copy(src=src, target=target)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

    def setUp(self):
        TnsTest.setUp(self)

        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        source_src = os.path.join(self.target_project_dir, 'app')
        target_src = os.path.join(self.source_project_dir, 'app')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

class PreviewAndroidJSTests(TnsPreviewJSTests):

    def test_100_preview_android(self):
        """Preview project on emulator. Make valid changes in JS, CSS and XML"""
        preview_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu)

@unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
class PreviewIOSJSTests(TnsPreviewJSTests):
    def test_100_preview_ios(self):
        """Preview project on simulator. Make valid changes in JS, CSS and XML"""
        preview_hello_world_js_ts(self.app_name, Platform.IOS, self.sim)

