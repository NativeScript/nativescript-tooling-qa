import os

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.chrome import Chrome
from core.utils.device.device_manager import DeviceManager


# noinspection PyMethodMayBeStatic
from products.angular.ng import NG
from products.nativescript.tns import Tns


class MigrateWebToMobileTests(TnsTest):
    app_name = Settings.AppName.DEFAULT
    app_folder = os.path.join(Settings.TEST_RUN_HOME, app_name)
    emu = None
    sim = None
    chrome = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        NG.new(collection=None, project=cls.app_name)
        cls.chrome = Chrome()
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

    def setUp(self):
        TnsTest.setUp(self)

    def tearDown(self):
        NG.kill()
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        cls.chrome.kill()
        TnsTest.tearDownClass()

    def ng_serve(self):
        NG.serve(project=self.app_name)
        self.chrome.open('http://localhost:4200/')
        welcome_element = self.chrome.driver.find_element_by_xpath('//h1')
        assert 'Welcome to' in welcome_element.text, 'Failed to find welcome message.'

    def test_01_ng_serve_web(self):
        self.ng_serve()

    def test_02_add_nativescript(self):
        # Add {N} to existing web project
        result = NG.add(project=self.app_name, schematics_package=Settings.Packages.NS_SCHEMATICS)

        # Verify output
        assert 'Adding @nativescript/schematics to angular.json' in result.output
        assert 'Adding {N} files' in result.output
        assert 'Adding NativeScript specific exclusions to .gitignore' in result.output
        assert 'Adding NativeScript run scripts to package.json' in result.output
        assert 'Excluding NativeScript files from web tsconfig' in result.output
        assert 'Adding Sample Shared Component' in result.output
        assert 'Adding npm dependencies' in result.output

        # NG Serve (to check web is not broken by {N})
        self.ng_serve()

    def test_03_run_android(self):
        Tns.run_android(app_name=self.app_name, bundle=True, device=self.emu.id)

    def test_04_run_ios(self):
        Tns.run_ios(app_name=self.app_name, bundle=True, device=self.sim.id)

    def test_05_run_android_aot(self):
        Tns.run_android(app_name=self.app_name, bundle=True, aot=True, device=self.emu.id)

    def test_06_run_ios_aot(self):
        Tns.run_ios(app_name=self.app_name, bundle=True, aot=True, device=self.sim.id)

    def test_07_run_android_aot(self):
        Tns.run_android(app_name=self.app_name, bundle=True, aot=True, uglify=True, device=self.emu.id)

    def test_08_run_ios_aot(self):
        Tns.run_ios(app_name=self.app_name, bundle=True, aot=True, uglify=True, device=self.sim.id)
