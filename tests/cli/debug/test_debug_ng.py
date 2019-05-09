import unittest

from core.base_test.tns_run_test import TnsRunTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.chrome.chrome import Chrome
from core.utils.chrome.chrome_dev_tools import ChromeDevTools, ChromeDevToolsTabs
from data.changes import Sync, Changes
from data.templates import Template
from products.nativescript.tns import Tns


class DebugNGTests(TnsRunTest):
    ts_change = Changes.NGHelloWorld.TS
    xml_change = Changes.NGHelloWorld.XML_ACTION_BAR
    app_name = Settings.AppName.DEFAULT
    chrome = None
    dev_tools = None

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        Tns.create(app_name=cls.app_name, template=Template.HELLO_WORLD_NG.local_package, update=True)
        Tns.platform_add_android(app_name=cls.app_name, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS == OSType.OSX:
            Tns.platform_add_ios(app_name=cls.app_name, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def setUp(self):
        TnsRunTest.setUp(self)
        Sync.revert(app_name=self.app_name, change_set=self.ts_change, fail_safe=True)
        Sync.revert(app_name=self.app_name, change_set=self.xml_change, fail_safe=True)
        self.chrome = Chrome()

    def tearDown(self):
        self.chrome.kill()
        TnsRunTest.tearDown(self)

    def test_001_debug_android_elements(self):
        self.__debug_elements(platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Can not debug iOS on non macOS hosts.')
    def test_001_debug_ios_elements(self):
        self.__debug_elements(platform=Platform.IOS, device=self.sim)

    def test_020_debug_android_sources(self):
        self.__debug_sources(platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'Can not debug iOS on non macOS hosts.')
    def test_020_debug_ios_sources(self):
        self.__debug_sources(platform=Platform.IOS, device=self.sim)

    def __debug_elements(self, platform, device):
        # Run `tns debug` wait until app is visible on device
        Tns.debug(app_name=self.app_name, platform=platform, emulator=True)
        device.wait_for_text(text=self.ts_change.old_text, timeout=240)

        # Start debug session and verify elements tab
        self.dev_tools = ChromeDevTools(self.chrome, platform=platform, tab=ChromeDevToolsTabs.ELEMENTS)
        assert self.dev_tools.wait_element_by_text(text=self.xml_change.old_text) is not None, 'Elements tab is empty.'

        # Sync changes and verify elements tab is updated
        Sync.replace(app_name=self.app_name, change_set=self.xml_change)
        device.wait_for_text(text=self.xml_change.new_text)

        # Elements tab do not auto-update for NG apps and need to be refreshed manually
        self.dev_tools = ChromeDevTools(self.chrome, platform=platform, tab=ChromeDevToolsTabs.ELEMENTS)
        assert self.dev_tools.wait_element_by_text(
            text=self.xml_change.new_text) is not None, 'Elements tab not updated.'

        # Update label in CDT and verify it is updated on device
        self.dev_tools.edit_text(old_text=self.xml_change.new_text, new_text=self.xml_change.old_text)
        element = self.dev_tools.wait_element_by_text(text=self.xml_change.old_text)
        assert element is not None, 'Failed to change text in elements tab.'
        device.wait_for_text(text=self.xml_change.old_text)

        # Expand items
        self.dev_tools.doubleclick_line(text='ProxyViewContainer')
        self.dev_tools.doubleclick_line(text='GridLayout')
        self.dev_tools.doubleclick_line(text='ListView')
        self.dev_tools.doubleclick_line(text='StackLayout')
        self.dev_tools.wait_element_by_text(text='Label', timeout=10)

    def __debug_sources(self, platform, device):
        # Start debug and wait until app is deployed
        Tns.debug(app_name=self.app_name, platform=platform, emulator=True)
        device.wait_for_text(text=self.ts_change.old_text)

        # Open sources tab and verify content is loaded
        self.dev_tools = ChromeDevTools(self.chrome, platform=platform, tab=ChromeDevToolsTabs.SOURCES)

        # Open TS file and place breakpoint on line 21
        self.dev_tools.load_source_file('item-detail.component.ts')
        self.dev_tools.breakpoint(21)

        # Navigate to details page and check breakpoint is hit
        device.click(text=self.ts_change.old_text)
        pause_element = self.dev_tools.wait_element_by_text(text="Paused on breakpoint", timeout=10)
        assert pause_element is not None, 'Failed to pause on breakpoint.'

        # Resume execution
        self.dev_tools.continue_debug()
        device.wait_for_text(text='Goalkeeper', timeout=30)

        # Sync changes and verify sources tab is updated
        Sync.replace(app_name=self.app_name, change_set=self.ts_change)
        device.wait_for_text(text=self.ts_change.new_text)
        self.dev_tools.load_source_file('item.service.ts')
        self.dev_tools.wait_element_by_text(text=self.ts_change.new_text, timeout=10)

        # Navigate to details page and check breakpoint is hit
        device.click(text=self.ts_change.new_text)
        pause_element = self.dev_tools.wait_element_by_text(text="Paused on breakpoint", timeout=10)
        assert pause_element is not None, 'Failed to pause on breakpoint.'

        # Resume execution
        self.dev_tools.continue_debug()
        device.wait_for_text(text='Goalkeeper', timeout=30)
