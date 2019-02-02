import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.npm import Npm
from data.sync.hello_world_js import sync_hello_world_js
from data.sync.hello_world_ng import sync_hello_world_ng
from products.nativescript.app import App
from products.nativescript.tns import Tns


class RegressionTests(TnsTest):
    js_app = Settings.AppName.DEFAULT + 'JS'
    ng_app = Settings.AppName.DEFAULT + 'NG'

    emu = None
    sim = None

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

        # Boot emulator and simulator
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS == OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

        # Create JS and NG apps with 4.* templates
        Tns.create(app_name=cls.js_app, template='tns-template-hello-world@4', update=False, verify=False)
        assert '~4.2.' in App.get_package_json(app_name=cls.js_app).get('dependencies').get('tns-core-modules')

        Tns.create(app_name=cls.ng_app, template='tns-template-hello-world-ng@4', update=False, verify=False)
        Npm.install(package='nativescript-dev-webpack@0.15', option='--save-dev',
                    folder=os.path.join(Settings.TEST_RUN_HOME, cls.ng_app))
        Npm.install(folder=os.path.join(Settings.TEST_RUN_HOME, cls.ng_app))
        assert '~4.2.' in App.get_package_json(app_name=cls.ng_app).get('dependencies').get('tns-core-modules')
        assert '~6.1.' in App.get_package_json(app_name=cls.ng_app).get('dependencies').get('nativescript-angular')
        assert '~6.1.' in App.get_package_json(app_name=cls.ng_app).get('dependencies').get('@angular/core')

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_001_run_android_js(self):
        sync_hello_world_js(app_name=self.js_app, platform=Platform.ANDROID, device=self.emu)
        assert '4.2' in App.get_platform_version(app_name=self.js_app, platform=Platform.ANDROID)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_002_run_ios_js(self):
        sync_hello_world_js(app_name=self.js_app, platform=Platform.IOS, device=self.sim)
        assert '4.2' in App.get_platform_version(app_name=self.js_app, platform=Platform.IOS)

    def test_100_run_android_ng(self):
        sync_hello_world_ng(app_name=self.ng_app, platform=Platform.ANDROID, device=self.emu)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_101_run_ios_ng(self):
        sync_hello_world_ng(app_name=self.ng_app, platform=Platform.IOS, device=self.sim)

    def test_200_build_android_js_release(self):
        Tns.build_android(app_name=self.ng_app, release=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_201_build_ios_js_release(self):
        Tns.build_ios(app_name=self.ng_app, release=True, for_device=True)

    def test_210_build_android_ng_release(self):
        Tns.build_android(app_name=self.ng_app, release=True, bundle=True, aot=True, uglify=True, snapshot=True)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_211_build_ios_ng_release(self):
        Tns.build_ios(app_name=self.ng_app, release=True, for_device=True, bundle=True, aot=True, uglify=True)
