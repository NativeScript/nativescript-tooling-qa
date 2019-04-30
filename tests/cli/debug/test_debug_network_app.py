import os
import unittest
from time import sleep

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.chrome.chrome import Chrome
from core.utils.chrome.chrome_dev_tools import ChromeDevTools, ChromeDevToolsTabs
from core.utils.file_utils import Folder
from core.utils.git import Git
from products.nativescript.app import App
from products.nativescript.tns import Tns


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
        self.dev_tools.wait_element_by_text(text='Debugging')
        device.click(text='TAP - add view children')
        self.dev_tools.doubleclick_line(text='StackLayout')
        self.dev_tools.doubleclick_line(text='ScrollView')
        self.dev_tools.doubleclick_line(text='FlexboxLayout')
        assert self.dev_tools.wait_element_by_text(text='StackLayout id=') is not None
        device.click(text='TAP - remove random view child')
        sleep(1)
        assert self.dev_tools.find_element_by_text(text='StackLayout id=') is None

    def __debug_console(self, platform, device):
        Tns.debug(app_name=self.app_name, platform=platform, emulator=True)
        self.dev_tools = ChromeDevTools(self.chrome, tab=ChromeDevToolsTabs.CONSOLE)
        device.click(text='TAP - verify distinct console logs')
        self.dev_tools.wait_element_by_text(text='main-view-model.ts:34')

    def __debug_sources(self, platform, device):
        Tns.debug(app_name=self.app_name, platform=platform, emulator=True)
        self.dev_tools = ChromeDevTools(self.chrome)
        self.dev_tools.open_tab(tab=ChromeDevToolsTabs.SOURCES, verify=False)
        pass

    def __debug_network(self, platform, device):
        Tns.debug(app_name=self.app_name, platform=platform, emulator=True)
        self.dev_tools = ChromeDevTools(self.chrome, tab=ChromeDevToolsTabs.NETWORK)
        device.click(text='TAP - navigate to Network requests page')

        # Request without body
        device.click(text='TAP - simple GET request without body')
        assert self.dev_tools.wait_element_by_text(text='get') is not None
        assert self.dev_tools.wait_element_by_text(text='200') is not None
        assert self.dev_tools.wait_element_by_text(text='0 B') is not None
        self.dev_tools.clean_network_tab()

        # Request with body
        device.click(text='TAP - GET request with body')
        assert self.dev_tools.wait_element_by_text(text='get') is not None
        assert self.dev_tools.wait_element_by_text(text='200') is not None
        assert self.dev_tools.wait_element_by_text(text='246 B') is not None
        self.dev_tools.clean_network_tab()
