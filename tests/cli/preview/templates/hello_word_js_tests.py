import os
import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.base_test.tns_test import TnsTest
from core.enums.app_type import AppType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from data.changes import Changes, Sync
from data.sync.hello_world_js import preview_sync_hello_world_js_ts
from data.templates import Template
from products.nativescript.preview_helpers import Preview
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs
from products.nativescript.tns_assert import TnsAssert


class TnsPreviewJSTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name)
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name)

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        # Start second emulator for tests
        cls.emu_API24 = DeviceManager.Emulator.ensure_available(Settings.Emulators.EMU_API_24)

        # Download Preview and Playground packages
        Preview.get_app_packages()

        # Install Preview and Playground
        Preview.install_preview_app(cls.emu, Platform.ANDROID)
        Preview.install_preview_app(cls.emu_API24, Platform.ANDROID)
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
                                       device=self.sim, click_open_alert=True)

    def test_205_preview_android_no_hmr(self):
        """Preview project on emulator with --no-hmr. Make valid changes in JS, CSS and XML"""
        preview_sync_hello_world_js_ts(app_type=AppType.JS, app_name=self.app_name, platform=Platform.ANDROID,
                                       device=self.emu, hmr=False)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_205_preview_ios_no_hmr(self):
        """Preview project on simulator with --no-hmr. Make valid changes in JS, CSS and XML"""
        preview_sync_hello_world_js_ts(app_type=AppType.JS, app_name=self.app_name, platform=Platform.IOS,
                                       device=self.sim, hmr=False)

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
        Preview.run_url(url=url, device=self.emu_API24)
        # Here use bundle=False because on consecutive preview build is not executed again
        # and no bundle messages are displayed in log
        strings = TnsLogs.preview_initial_messages(platform=Platform.ANDROID, bundle=False)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.emu_API24.wait_for_text(text=Changes.JSHelloWord.JS.old_text)

        # Verify first emulator is not refreshed, state of app is preserved
        self.emu.wait_for_text(text='41 taps left', timeout=30)

        # Edit JS file and verify changes are applied on both emulators
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.new_text)
        self.emu_API24.wait_for_text(text=Changes.JSHelloWord.JS.new_text)

        # Edit XML file and verify changes are applied
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.XML)
        self.emu.wait_for_text(text=Changes.JSHelloWord.XML.new_text)
        self.emu_API24.wait_for_text(text=Changes.JSHelloWord.XML.new_text)

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
        strings = TnsLogs.preview_initial_messages(platform=Platform.IOS)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.old_text)

        # Verify emulator is not refreshed, state of app is preserved
        self.emu.wait_for_text(text='41 taps left', timeout=30)

        # Edit JS file and verify changes are applied on both emulators
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.JS)
        self.emu.wait_for_text(text=Changes.JSHelloWord.JS.new_text)
        self.sim.wait_for_text(text=Changes.JSHelloWord.JS.new_text)

        # Check changes are not synced more than once per platform
        # Extract the last part of the log
        log = File.read(result.log_file)
        log = File.extract_part_of_text(log, '[VERIFIED]')
        # Verify files are synced once
        TnsAssert.file_is_synced_once(log, Platform.ANDROID, 'main-view-model.js')
        TnsAssert.file_is_synced_once(log, Platform.IOS, 'main-view-model.js')
        # Mark that part of the log as verified before next sync
        File.append(result.log_file, '[VERIFIED]')

        # Edit XML file and verify changes are applied on both emulators
        Sync.replace(app_name=self.app_name, change_set=Changes.JSHelloWord.XML)
        self.emu.wait_for_text(text=Changes.JSHelloWord.XML.new_text)
        self.sim.wait_for_text(text=Changes.JSHelloWord.XML.new_text)

        # Check changes are not synced more than once per platform
        # Extract the last part of the log
        log = File.read(result.log_file)
        log = File.extract_part_of_text(log, '[VERIFIED]')
        # Verify files are synced once
        TnsAssert.file_is_synced_once(log, Platform.ANDROID, 'main-page.xml')
        TnsAssert.file_is_synced_once(log, Platform.IOS, 'main-page.xml')

    def test_240_tns_preview_android_verify_plugin_warnings(self):
        """
        Test if correct messages are shown if plugin is missing or versions differ in Preview App.
        """

        # Add some plugins
        Tns.plugin_add("nativescript-barcodescanner", path=self.app_name)
        Tns.plugin_add("nativescript-geolocation@5.1.0", path=self.app_name)

        result = Tns.preview(app_name=self.app_name)

        # Read the log and extract the url to load the app on emulator
        log = File.read(result.log_file)
        url = Preview.get_url(log)
        Preview.run_url(url=url, device=self.emu)

        # Verify warnings for plugins
        strings = [
            'Plugin nativescript-barcodescanner is not included in preview app',
            # 'Local plugin nativescript-geolocation differs in major version from plugin in preview app',
            # 'Some features might not work as expected'
            # TODO: Uncomment line above after we release preview app with version of nativescript-geolocation > 5.1.0
            # Notes:
            # Preview command will fail bacause CLI will detect project needs update, see:
            # https://github.com/NativeScript/nativescript-cli/
            # blob/b5f88a45fbde0ef5559dc02e8cee5fb95cefe882/lib/controllers/migrate-controller.ts#L58
        ]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
