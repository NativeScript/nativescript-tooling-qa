import os
import unittest
from time import sleep

from core.base_test.tns_run_android_test import TnsRunAndroidTest
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.chrome.chrome import Chrome
from core.utils.chrome.chrome_dev_tools import ChromeDevTools, ChromeDevToolsTabs
from core.utils.file_utils import File
from data.changes import Sync, Changes
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


class DebugAndroidJSTests(TnsRunAndroidTest):
    app_name = Settings.AppName.DEFAULT
    change = Changes.JSHelloWord.XML_ACTION_BAR
    chrome = None
    dev_tools = None

    @classmethod
    def setUpClass(cls):
        TnsRunAndroidTest.setUpClass()
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_JS.local_package, update=False)

        # Instrument the app so it console log events.
        source_js = os.path.join(Settings.TEST_RUN_HOME, 'assets', 'runtime', 'debug', 'files', "console_log",
                                 'main-view-model.js')
        target_js = os.path.join(Settings.TEST_RUN_HOME, cls.app_name, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js)

        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)

    def setUp(self):
        TnsRunAndroidTest.setUp(self)
        self.chrome = Chrome()

    def tearDown(self):
        # Try to rollback changes we do in tests
        Sync.replace(app_name=self.app_name, change_set=self.change, fail_safe=True)
        self.chrome.kill()
        TnsRunAndroidTest.tearDown(self)

    def test_001_debug_elements(self):
        # Run `tns debug` wait until debug url is in the console
        Tns.debug(app_name=self.app_name, platform=Platform.ANDROID, emulator=True)

        # Wait until app is visible on device
        self.emu.wait_for_text(text='TAP')

        # Start debug session and verify elements tab
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(ChromeDevToolsTabs.ELEMENTS)
        assert self.dev_tools.wait_element_by_text(text=self.change.old_text) is not None, 'Elements tab is empty.'

        # Sync changes and verify elements tab is updated
        Sync.replace(app_name=self.app_name, change_set=self.change)
        self.emu.wait_for_text(text=self.change.new_text)
        assert self.dev_tools.wait_element_by_text(text=self.change.new_text) is not None, 'Elements tab not updated.'

        # Update label in CDT and verify it is updated on device
        self.dev_tools.edit_text(old_text=self.change.new_text, new_text=self.change.old_text)
        element = self.dev_tools.wait_element_by_text(text=self.change.old_text)
        assert element is not None, 'Failed to change text in elements tab.'
        self.emu.wait_for_text(text=self.change.old_text)

    def test_010_debug_console_log(self):
        # Run `tns debug` wait until debug url is in the console and app is loaded
        result = Tns.debug(app_name=self.app_name, platform=Platform.ANDROID, emulator=True)
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

    def test_011_debug_console_eval(self):
        # Run `tns debug` wait until debug url is in the console and app is loaded
        Tns.debug(app_name=self.app_name, platform=Platform.ANDROID, emulator=True)
        self.emu.wait_for_text(text='TAP')

        # Open Chrome Dev Tools -> Console
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(ChromeDevToolsTabs.CONSOLE)

        # Evaluate on console
        self.dev_tools.type_on_console("1024+1024")
        self.dev_tools.wait_element_by_text(text='2048', timeout=10)

    def test_020_debug_sources(self):
        # Start debug and wait until app is deployed
        result = Tns.debug(app_name=self.app_name, platform=Platform.ANDROID, emulator=True)
        logs = ['Webpack build done!', 'Restarting application', 'ActivityManager: Start proc']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=logs, timeout=60)
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

        # Test for https://github.com/NativeScript/nativescript-cli/issues/4227
        Sync.replace(app_name=self.app_name, change_set=self.change)
        xml_file_name = os.path.basename(self.change.file_path)
        logs = [xml_file_name, 'Webpack build done!', 'Refreshing application', 'Successfully synced application']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=logs)
        sleep(10)  # Give it some more time to crash
        logs = File.read(result.log_file)
        assert 'Unable to apply changes' not in logs
        assert 'Stopping webpack watch' not in logs
        self.dev_tools.open_tab(ChromeDevToolsTabs.ELEMENTS)  # Go to element tab and verify change is not applied
        assert self.dev_tools.wait_element_by_text(text=self.change.old_text) is not None, \
            'Changes applied while debug paused.'

        # Resume execution
        self.dev_tools.open_tab(ChromeDevToolsTabs.SOURCES)
        self.dev_tools.continue_debug()
        self.emu.wait_for_text(text='41 taps left')
        self.emu.wait_for_text(text=self.change.new_text)  # Verify change applied during debug in xml is applied

        # Go back to elements tab again and verify change is synced
        self.dev_tools.open_tab(ChromeDevToolsTabs.ELEMENTS)  # Go to element tab and verify change is not applied
        assert self.dev_tools.wait_element_by_text(text=self.change.new_text) is not None, \
            'Changes during paused debug are NOT applied after debug is resumed.'

    def test_021_debug_watch_expressions(self):
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

        # Add watch expression
        self.dev_tools.add_watch_expression(expression='console', expected_result='console: Object')
        self.dev_tools.add_watch_expression(expression='viewModel', expected_result='viewModel: Observable')

    @unittest.skip('Not Implemented.')
    def test_030_debug_network(self):
        # Ensure we verify https://github.com/NativeScript/nativescript-cli/issues/3187
        pass

    def test_040_debug_brk(self):
        # Hack to workaround https://github.com/NativeScript/nativescript-cli/issues/4567
        Tns.run_android(app_name=self.app_name, emulator=True, source_map=True, just_launch=True)
        self.emu.wait_for_text(text='TAP')

        Tns.debug(app_name=self.app_name, platform=Platform.ANDROID, emulator=True, debug_brk=True)
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(ChromeDevToolsTabs.SOURCES)
        pause_element = self.dev_tools.wait_element_by_text(text="Debugger paused", timeout=30)
        assert pause_element is not None, 'Failed to stop on first line of code.'
        assert self.dev_tools.find_element_by_text(text="function") is not None, 'Failed to stop on first line of code.'
        assert 'NativeScript' in self.emu.get_text(), 'Failed to stop on first line of code.'

    def test_050_debug_start(self):
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
