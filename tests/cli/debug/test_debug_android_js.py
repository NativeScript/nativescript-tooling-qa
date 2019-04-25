import os
import unittest
from time import sleep

from core.base_test.tns_run_android_test import TnsRunAndroidTest
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.chrome.chrome import Chrome
from core.utils.chrome.chrome_dev_tools import ChromeDevTools, ChromeDevToolsTabs
from core.utils.file_utils import File, Folder
from data.changes import Sync, Changes
from data.templates import Template
from products.nativescript.tns import Tns


class DebugAndroidJSTests(TnsRunAndroidTest):
    app_name = Settings.AppName.DEFAULT
    chrome = None
    dev_tools = None

    source_project_dir = os.path.join(Settings.TEST_RUN_HOME, app_name, 'app')
    target_project_dir = os.path.join(Settings.TEST_RUN_HOME, 'data', 'temp', app_name, 'app')

    @classmethod
    def setUpClass(cls):
        TnsRunAndroidTest.setUpClass()
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=False)
        Folder.copy(source=cls.source_project_dir, target=cls.target_project_dir)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)

    def setUp(self):
        TnsRunAndroidTest.setUp(self)
        self.chrome = Chrome()
        Folder.copy(source=self.target_project_dir, target=self.source_project_dir)

    def tearDown(self):
        self.chrome.kill()
        self.emu.wait_for_text(text='TAP', timeout=5)
        TnsRunAndroidTest.tearDown(self)

    def test_001_debug_elements(self):
        # Run `tns debug` wait until debug url is in the console
        Tns.debug(app_name=self.app_name, platform=Platform.ANDROID, emulator=True)

        # Define change we will do later
        change = Changes.JSHelloWord.XML_ACTION_BAR

        # Wait until app is visible on device
        self.emu.wait_for_text(text='TAP')

        # Start debug session and verify elements tab
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(ChromeDevToolsTabs.ELEMENTS)
        assert self.dev_tools.wait_element_by_text(text=change.old_text) is not None, 'Elements tab is empty.'

        # Sync changes and verify elements tab is updated
        Sync.replace(app_name=self.app_name, change_set=change)
        self.emu.wait_for_text(text=change.new_text)
        assert self.dev_tools.wait_element_by_text(text=change.new_text) is not None, 'Elements tab not updated.'

        # Update label in CDT and verify it is updated on device
        self.dev_tools.edit_text(old_text=change.new_text, new_text=change.old_text)
        element = self.dev_tools.wait_element_by_text(text=change.old_text)
        assert element is not None, 'Failed to change text in elements tab.'
        self.emu.wait_for_text(text=change.old_text)

    def test_010_debug_console_log(self):
        # Instrument the app so it console log events.
        source_js = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'runtime', 'debug', 'files', "console_log",
                                 'main-view-model.js')
        target_js = os.path.join(Settings.TEST_RUN_HOME, self.app_name, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js)

        # Run `tns debug` wait until debug url is in the console
        result = Tns.debug(app_name=self.app_name, platform=Platform.ANDROID, emulator=True)

        # Wait until app is visible on device
        self.emu.wait_for_text(text='TAP')

        # Open Chrome Dev Tools -> Console
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(ChromeDevToolsTabs.CONSOLE)

        # TAP the button to trigger console log
        self.emu.click(text='TAP', case_sensitive=True)

        # Ensure it is in device logs
        assert self.emu.wait_for_log(text='Test Debug!'), 'Console logs not avaiable in device logs.'

        # Ensure logs are available in tns logs
        tns_logs = File.read(result.log_file)
        assert "Test Debug!" in tns_logs, 'Console log messages not available in CLI output.' + os.linesep + tns_logs

        # Verify console logs are available in Chrome dev tools
        log = self.dev_tools.wait_element_by_text(text='Test Debug!')
        assert log is not None, 'Console logs not displayed in Chrome Dev Tools.'

    @unittest.skip('Not Implemented.')
    def test_011_debug_console_evaluate(self):
        pass

    @unittest.skip('Not Implemented.')
    def test_012_debug_watch_expressions(self):
        pass

    def test_020_debug_sources(self):
        # Start debug and wait until app is deployed
        Tns.debug(app_name=self.app_name, platform=Platform.ANDROID, emulator=True)
        self.emu.wait_for_text(text='TAP')

        # Open sources tab and verify content is loaded
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(ChromeDevToolsTabs.SOURCES)
        webpack_element = self.dev_tools.wait_element_by_text(text='webpack')
        assert webpack_element is not None, 'Failed to load app sources.'

        # Open JS file and place breakpoint on line 17
        self.dev_tools.load_source_file("main-view-model.js")
        self.dev_tools.breakpoint(17)

        # Tap on TAP button in emulator and check it is hit
        self.emu.click(text="TAP", case_sensitive=True)
        pause_element = self.dev_tools.wait_element_by_text(text="Paused on breakpoint", timeout=10)
        assert pause_element is not None, 'Failed to pause on breakpoint.'

        # Add steps to verify https://github.com/NativeScript/nativescript-cli/issues/4227

        # Notes:
        # - When breakpoint is hit adb can not get page source and methods like is_text_vibible() and click() fail!
        # - TODO: Check how to interact with app when paused on breakpoint.

    @unittest.skip('Not Implemented.')
    def test_030_debug_network(self):
        # Ensure we verify https://github.com/NativeScript/nativescript-cli/issues/3187
        pass

    @unittest.skip('Not Implemented.')
    def test_040_debug_brk(self):
        """
        Deploy on device/emulator, run the app and stop at the first code statement.
        """
        pass

    def test_050_debug_start(self):
        # Instrument the app so it console log events.
        source_js = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'runtime', 'debug', 'files', "console_log",
                                 'main-view-model.js')
        target_js = os.path.join(Settings.TEST_RUN_HOME, self.app_name, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js)

        # Run the app and verify it is deployed
        Tns.run_android(app_name=self.app_name, emulator=True, source_map=True, just_launch=True)
        self.emu.wait_for_text(text='TAP')

        # Attach debug session
        result = Tns.debug(app_name=self.app_name, platform=Platform.ANDROID, emulator=True, start=True)

        # Verify sources tab is loaded
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(ChromeDevToolsTabs.SOURCES)
        webpack_element = self.dev_tools.wait_element_by_text(text='webpack')
        assert webpack_element is not None, 'Failed to load app sources.'
        self.emu.wait_for_text(text='TAP')

        # Verify console log is working (covers https://github.com/NativeScript/nativescript-cli/issues/3629)
        self.dev_tools.open_tab(ChromeDevToolsTabs.CONSOLE)
        self.emu.click(text='TAP', case_sensitive=True)
        assert self.dev_tools.wait_element_by_text(text='Test Debug!') is not None, 'Console logs not displayed in CDT.'
        tns_logs = File.read(result.log_file)
        assert "Test Debug!" in tns_logs, 'Console log messages not available in CLI output.' + os.linesep + tns_logs

        # Verify debug is working (covers https://github.com/NativeScript/nativescript-cli/issues/2831)
        self.dev_tools.load_source_file("main-view-model.js")
        self.dev_tools.breakpoint(17)
        self.emu.click(text="TAP", case_sensitive=True)
        pause_element = self.dev_tools.wait_element_by_text(text="Paused on breakpoint", timeout=10)
        assert pause_element is not None, 'Failed to pause on breakpoint.'

    def test_100_reload_chrome_page(self):
        # Start debug and wait until app is deployed
        Tns.debug(app_name=self.app_name, platform=Platform.ANDROID, emulator=True)
        self.emu.wait_for_text(text='TAP')

        # Open CDT with debug url twice
        self.dev_tools = ChromeDevTools(self.chrome)
        sleep(1)
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(ChromeDevToolsTabs.SOURCES)
        webpack_element = self.dev_tools.wait_element_by_text(text='webpack')
        assert webpack_element is not None, 'Failed to load app sources.'
        self.emu.wait_for_text(text='TAP')

        # Open another site and then back to CDT
        self.chrome.open(url='https://www.nativescript.org')
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(ChromeDevToolsTabs.SOURCES)
        webpack_element = self.dev_tools.wait_element_by_text(text='webpack')
        assert webpack_element is not None, 'Failed to load app sources.'
        self.emu.wait_for_text(text='TAP')
