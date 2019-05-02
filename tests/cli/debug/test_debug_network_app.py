import os
import unittest
from time import sleep

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.chrome.chrome import Chrome
from core.utils.chrome.chrome_dev_tools import ChromeDevTools, ChromeDevToolsTabs
from core.utils.file_utils import Folder, File
from core.utils.git import Git
from products.nativescript.app import App
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs

ACTION_BAR_TITLE = 'Debugging'
HOME_CONSOLE_BUTTON = 'TAP - Console logs'
HOME_NETWORK_BUTTON = 'TAP - Network requests'
HOME_ADD_CHILD_BUTTON = 'TAP - Add view children'
HOME_REMOVE_CHILD_BUTTON = 'TAP - Remove random view child'
NET_GET_WITHOUT_BODY = 'GET without body'
NET_GET_WITH_BODY = 'GET with body'
NET_GET_UNAUTHORIZED = 'GET with unauthorized'
NET_GET_DELAYED_RESPONSE = 'GET with delayed response'
NET_GET_IMAGE = 'GET with image response'
NET_GET_BINARY = 'GET binary data (download)'
NET_POST = 'POST with headers'


class DebugNetworkTests(TnsRunTest):
    app_name = Settings.AppName.DEFAULT
    chrome = None
    dev_tools = None

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        app_folder = os.path.join(Settings.TEST_RUN_HOME, cls.app_name)
        Folder.clean(app_folder)
        Git.clone(repo_url='https://github.com/NativeScript/chrome-devtools-test-app', local_folder=app_folder)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS == OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)
        App.update(app_name=cls.app_name)

    def setUp(self):
        TnsRunTest.setUp(self)
        self.chrome = Chrome()

    def tearDown(self):
        self.chrome.kill()
        TnsRunTest.tearDown(self)

    def test_010_debug_android_elements(self):
        self.__debug_elements(platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Can not debug iOS on non macOS hosts.')
    def test_010_debug_ios_elements(self):
        self.__debug_elements(platform=Platform.IOS, device=self.sim)

    def test_020_debug_android_console(self):
        self.__debug_console(platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Can not debug iOS on non macOS hosts.')
    def test_020_debug_ios_console(self):
        self.__debug_console(platform=Platform.IOS, device=self.sim)

    def test_030_debug_android_sources(self):
        self.__debug_sources(platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Can not debug iOS on non macOS hosts.')
    def test_030_debug_ios_sources(self):
        self.__debug_sources(platform=Platform.IOS, device=self.sim)

    def test_040_debug_android_network(self):
        self.__debug_network(platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Can not debug iOS on non macOS hosts.')
    def test_040_debug_ios_network(self):
        self.__debug_network(platform=Platform.IOS, device=self.sim)

    def __debug_elements(self, platform, device):
        Tns.debug(app_name=self.app_name, platform=platform, emulator=True)
        self.dev_tools = ChromeDevTools(self.chrome, tab=ChromeDevToolsTabs.ELEMENTS)
        self.dev_tools.wait_element_by_text(text=ACTION_BAR_TITLE)
        device.click(text=HOME_ADD_CHILD_BUTTON)
        self.dev_tools.doubleclick_line(text='StackLayout')
        self.dev_tools.doubleclick_line(text='ScrollView')
        self.dev_tools.doubleclick_line(text='FlexboxLayout')
        assert self.dev_tools.wait_element_by_text(text='StackLayout id=') is not None
        device.click(text=HOME_REMOVE_CHILD_BUTTON)
        sleep(1)
        assert self.dev_tools.find_element_by_text(text='StackLayout id=') is None

    def __debug_console(self, platform, device):
        Tns.debug(app_name=self.app_name, platform=platform, emulator=True)
        self.dev_tools = ChromeDevTools(self.chrome, tab=ChromeDevToolsTabs.CONSOLE)
        device.click(text=HOME_CONSOLE_BUTTON)
        self.dev_tools.wait_element_by_text(text='main-view-model.ts:34')

    def __debug_sources(self, platform, device):
        # Run debug, to network page and open network tab in CDT
        result = Tns.debug(app_name=self.app_name, platform=platform, emulator=True)
        device.click(text=HOME_NETWORK_BUTTON)
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(tab=ChromeDevToolsTabs.SOURCES, verify=False)

        # Place breakpoint and verify it is hit
        self.dev_tools.load_source_file('network-page.ts')
        self.dev_tools.breakpoint(line=28)
        device.click(text=NET_GET_WITHOUT_BODY)
        self.dev_tools.wait_element_by_text(text='Paused on breakpoint', timeout=10)
        assert 'httpbin.org' not in File.read(result.log_file)
        self.dev_tools.continue_debug()
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=['httpbin.org'])

        # Add one more breakpoint and hit it
        self.dev_tools.load_source_file('network-page.ts')
        self.dev_tools.breakpoint(line=46)
        device.click(text=NET_GET_WITH_BODY)
        self.dev_tools.wait_element_by_text(text='Paused on breakpoint', timeout=10)
        assert 'My custom Arbitrary Header value' not in File.read(result.log_file)
        self.dev_tools.continue_debug()
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=['My custom Arbitrary Header value'])

    def __debug_network(self, platform, device):
        Tns.debug(app_name=self.app_name, platform=platform, emulator=True)
        self.dev_tools = ChromeDevTools(self.chrome, tab=ChromeDevToolsTabs.NETWORK)
        device.click(text=HOME_NETWORK_BUTTON)

        # Request without body
        device.click(text=NET_GET_WITHOUT_BODY)
        assert self.dev_tools.wait_element_by_text(text='get') is not None
        assert self.dev_tools.wait_element_by_text(text='200') is not None
        assert self.dev_tools.wait_element_by_text(text='0 B') is not None
        self.dev_tools.clean_network_tab()

        # Request with body
        device.click(text=NET_GET_WITH_BODY)
        assert self.dev_tools.wait_element_by_text(text='get') is not None
        assert self.dev_tools.wait_element_by_text(text='200') is not None
        assert self.dev_tools.wait_element_by_text(text='246 B') is not None
        self.dev_tools.clean_network_tab()

        # TODO: Add tests for all requests
