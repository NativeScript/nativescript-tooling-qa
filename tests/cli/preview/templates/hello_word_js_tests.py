import os
import unittest
from core.base_test.tns_test import TnsTest
from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.enums.app_type import AppType
from core.settings import Settings
from core.utils.file_utils import File, Folder
from core.utils.device.adb import Adb
from data.sync.hello_world_js import preview_sync_hello_world_js_ts, preview_hello_world_js_ts
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.preview_helpers import Preview
from products.nativescript.tns_logs import TnsLogs
from core.utils.device.device_manager import DeviceManager
from data.changes import Changes, Sync


class TnsPreviewJSTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        # Start second emulator for tests
        cls.emu_API28 = DeviceManager.Emulator.ensure_available(Settings.Emulators.EMU_API_28)

        # Download Preview and Playground packages
        Preview.get_app_packages()

        # Install Preview and Playground
        Preview.install_preview_app(cls.emu, Platform.ANDROID)
        Preview.install_preview_app(cls.emu_API28, Platform.ANDROID)
        if Settings.HOST_OS is OSType.OSX:
            Preview.install_preview_app(cls.sim, Platform.IOS)
            Preview.install_playground_app(cls.sim, Platform.IOS)

        # Create app
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=True)
        src = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'logs', 'hello-world-js', 'app.js')
        target = os.path.join(Settings.TEST_RUN_HOME, cls.app_name, 'app')
        File.copy(source=src, target=target)

        # Copy TestApp to data folder.
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)

        # Start second emulator for tests
        cls.emu_API26 = DeviceManager.Emulator.ensure_available(Settings.Emulators.EMU_API_26)

    def setUp(self):
        TnsTest.setUp(self)

        # "src" folder of TestApp will be restored before each test.
        # This will ensure failures in one test do not cause common failures.
        source_src = os.path.join(self.target_project_dir, 'app')
        target_src = os.path.join(self.source_project_dir, 'app')
        Folder.clean(target_src)
        Folder.copy(source=source_src, target=target_src)


class PreviewJSTests(TnsPreviewJSTests):

    def test_100_preview_android(self):
        """Preview project on emulator. Make valid changes in JS, CSS and XML"""
        preview_sync_hello_world_js_ts(app_type=AppType.JS, app_name=self.app_name, platform=Platform.ANDROID,
                                       device=self.emu, instrumented=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_100_preview_ios(self):
        """Preview project on simulator. Make valid changes in JS, CSS and XML"""
        preview_sync_hello_world_js_ts(app_type=AppType.JS, app_name=self.app_name, platform=Platform.IOS,
                                       device=self.sim)

    def test_200_preview_android_bundle(self):
        """Preview project on emulator with --bundle. Make valid changes in JS, CSS and XML"""
        preview_sync_hello_world_js_ts(app_type=AppType.JS, app_name=self.app_name, platform=Platform.ANDROID,
                                       device=self.emu, instrumented=True, bundle=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_200_preview_ios_bundle(self):
        """Preview project on simulator with --bundle. Make valid changes in JS, CSS and XML"""
        preview_sync_hello_world_js_ts(app_type=AppType.JS, app_name=self.app_name, platform=Platform.IOS,
                                       device=self.sim, instrumented=True, bundle=True)

    def test_205_preview_android_hmr(self):
        """Preview project on emulator with --hmr. Make valid changes in JS, CSS and XML"""
        # preview_hello_world_js_ts(self.app_name, Platform.ANDROID, self.emu)
        preview_sync_hello_world_js_ts(app_type=AppType.JS, app_name=self.app_name, platform=Platform.ANDROID,
                                       device=self.emu, instrumented=True, hmr=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_205_preview_ios_hmr(self):
        """Preview project on simulator with --hmr. Make valid changes in JS, CSS and XML"""
        preview_sync_hello_world_js_ts(app_type=AppType.JS, app_name=self.app_name, platform=Platform.IOS,
                                       device=self.sim, instrumented=True, hmr=True)

    def test_210_tns_preview_android_livesync_on_two_emulators(self):
        """
        Test when preview on second emulator only the current one is refreshed.
        Test changes are synced on both emulators.
        """
        # Preview on emulator
        result = Tns.preview(app_name=self.app_name)

        # Read the log and extract the url to load the app on emulator
        log = File.read(result.log_file)
        url = Preview.get_url(log)
        Preview.run_url(url=url, device=self.emu)
        strings = TnsLogs.preview_initial_messages(platform=Platform.ANDROID)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)

        # Click on TAP button on emulator
        Adb.click_element_by_text(self.emu.id, 'TAP', case_sensitive=True)

        # Preview on second emulator
        Preview.run_url(url=url, device=self.emu_API28)
        self.emu_API28.wait_for_text(text=Changes.JSHelloWord.JS.old_text)

        # Verify first emulator is not refreshed, state of app is preserved
        self.emu.wait_for_text(text='41 taps left', timeout=30)

        # Edit JS file and verify changes are applied on both emulators
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.new_text)
        self.emu_API28.wait_for_text(text=Changes.JSHelloWord.JS.new_text)

        # Edit XML file and verify changes are applied
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.XML)
        self.emu.wait_for_text(text=Changes.JSHelloWord.XML.new_text)
        self.emu_API28.wait_for_text(text=Changes.JSHelloWord.XML.new_text)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_210_tns_preview_on_simulator_and_emulator_livesync(self):
        """
        Preview app on simulator and emulator. Verify livesync.
        """
        # Preview on emulator
        result = Tns.preview(app_name=self.app_name)

        # Read the log and extract the url to load the app on emulator
        log = File.read(result.log_file)
        url = Preview.get_url(log)
        Preview.run_url(url=url, device=self.emu)
        strings = TnsLogs.preview_initial_messages(platform=Platform.ANDROID)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.old_text)

        # Click on TAP button on emulator
        Adb.click_element_by_text(self.emu.id, 'TAP', case_sensitive=True)

        # Preview on simulator
        Preview.run_url(url=url, device=self.sim)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.old_text)

        # Verify emulator is not refreshed, state of app is preserved
        self.emu.wait_for_text(text='41 taps left', timeout=30)

        # Edit JS file and verify changes are applied on both emulators
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.new_text)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.new_text)

        # Edit XML file and verify changes are applied
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.XML)
        self.emu.wait_for_text(text=Changes.JSHelloWord.XML.new_text)
        self.sim.wait_for_text(text=Changes.JSHelloWord.XML.new_text) 

    def test_240_tns_preview_android_verify_plugin_warnings(self):
        """Test if correct messages are shown if plugin is missing or versions differ in Preview App."""
        # Add some plugins
        Tns.plugin_add("nativescript-barcodescanner", path=self.app_name)
        Tns.plugin_add("nativescript-geolocation@3.0.1", path=self.app_name)
        result = preview_hello_world_js_ts(app_name=self.app_name, platform=Platform.ANDROID,
                                           device=self.emu)
        # Verify warnings for plugins
        strings = [
            'Plugin nativescript-barcodescanner is not included in preview app',
            'Local plugin nativescript-geolocation differs in major version from plugin in preview app',
            'Some features might not work as expected'
            ]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
