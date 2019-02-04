# pylint: disable=unused-argument
# pylint: disable=undefined-variable

import os

from parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.json_utils import JsonUtils
from data.templates import Template
from products.nativescript.tns import Tns

RETRY_COUNT = 3
TOLERANCE = 0.20
APP_NAME = Settings.AppName.DEFAULT
EXPECTED_RESULTS = JsonUtils.read(os.path.join(Settings.TEST_RUN_HOME, 'tests', 'perf', 'data.json'))


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class PrepareAndBuildPerfTests(TnsTest):
    TEST_DATA = [
        ('jasmine-js-android', 'jasmine', Template.HELLO_WORLD_JS, Platform.ANDROID),
        ('jasmine-js-ios', 'jasmine', Template.HELLO_WORLD_JS, Platform.IOS),
        ('jasmine-ng-android', 'jasmine', Template.HELLO_WORLD_NG, Platform.ANDROID),
        ('jasmine-ng-ios', 'jasmine', Template.HELLO_WORLD_NG, Platform.IOS),
        ('mocha-js-android', 'mocha', Template.HELLO_WORLD_JS, Platform.ANDROID),
        ('mocha-js-ios', 'mocha', Template.HELLO_WORLD_JS, Platform.IOS),
        ('mocha-ng-android', 'mocha', Template.HELLO_WORLD_NG, Platform.ANDROID),
        ('mocha-ng-ios', 'mocha', Template.HELLO_WORLD_NG, Platform.IOS),
        ('qunit-js-android', 'qunit', Template.HELLO_WORLD_JS, Platform.ANDROID),
        ('qunit-js-ios', 'qunit', Template.HELLO_WORLD_JS, Platform.IOS),
    ]

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)
        if Settings.HOST_OS is OSType.OSX:
            cls.sim = DeviceManager.Simulator.ensure_available(Settings.Simulators.DEFAULT)

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    @parameterized.expand(TEST_DATA)
    def test_100(self, title, framework, template, platform):
        # Create app
        Tns.create(app_name=Settings.AppName.DEFAULT, template=template.local_package)

        # Add platforms
        if platform == Platform.ANDROID:
            Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)
        elif platform == Platform.IOS:
            Tns.platform_add_ios(app_name=APP_NAME, framework_path=Settings.IOS.FRAMEWORK_PATH)
        else:
            raise Exception('Unknown platform: ' + str(platform))

        # Init tests and run tests
        Tns.test_init(app_name=Settings.AppName.DEFAULT, framework=framework)
        Tns.test(app_name=Settings.AppName.DEFAULT, platform=Platform.ANDROID, emulator=True, justlaunch=True)

    def test_400_invalid_framework(self):
        Tns.create(app_name=Settings.AppName.DEFAULT, template=Template.HELLO_WORLD_JS.local_package)
        result = Tns.test_init(app_name=Settings.AppName.DEFAULT, framework='jasmin', verify=False)
        assert 'unknown or unsupported unit testing framework: jasmin' in result.output
