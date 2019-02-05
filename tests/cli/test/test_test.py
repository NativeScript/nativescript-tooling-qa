# pylint: disable=unused-argument
# pylint: disable=undefined-variable

import os

from parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.device_manager import DeviceManager
from core.utils.npm import Npm
from data.templates import Template
from products.nativescript.tns import Tns

APP_NAME = Settings.AppName.DEFAULT

TEST_DATA = [
    ('jasmine-js-android', 'jasmine', Template.HELLO_WORLD_JS, Platform.ANDROID),
    ('jasmine-ng-android', 'jasmine', Template.HELLO_WORLD_NG, Platform.ANDROID),
    ('mocha-js-android', 'mocha', Template.HELLO_WORLD_JS, Platform.ANDROID),
    ('mocha-ng-android', 'mocha', Template.HELLO_WORLD_NG, Platform.ANDROID),
    ('qunit-js-android', 'qunit', Template.HELLO_WORLD_JS, Platform.ANDROID),
]

TEST_DATA_OSX = [
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


def get_data():
    if Settings.HOST_OS == OSType.OSX:
        return TEST_DATA_OSX
    else:
        return TEST_DATA


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class PrepareAndBuildPerfTests(TnsTest):

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

    @parameterized.expand(get_data())
    def test_100(self, title, framework, template, platform):
        # Create app
        Tns.create(app_name=APP_NAME, template=template.local_package)

        # Add platforms
        if platform == Platform.ANDROID:
            Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)
            Tns.prepare_android(app_name=APP_NAME)
            if Settings.HOST_OS == OSType.WINDOWS:
                Tns.run_android(app_name=APP_NAME, emulator=True, justlaunch=True)
        elif platform == Platform.IOS:
            Tns.platform_add_ios(app_name=APP_NAME, framework_path=Settings.IOS.FRAMEWORK_PATH)
            Tns.prepare_ios(app_name=APP_NAME)
        else:
            raise Exception('Unknown platform: ' + str(platform))

        # First Run
        # Init tests and run tests
        if Settings.HOST_OS == OSType.WINDOWS and framework == 'qunit':
            # Hack for qunit on windows (see https://github.com/NativeScript/nativescript-cli/issues/4333)
            Npm.install(package='qunit@2', option='--save-dev', folder=os.path.join(Settings.TEST_RUN_HOME, APP_NAME))
            result = Tns.test_init(app_name=APP_NAME, framework=framework, verify=False)
            assert 'Successfully installed plugin nativescript-unit-test-runner' in result.output
            assert 'Example test file created in' in result.output
            assert 'Run your tests using the' in result.output
        else:
            Tns.test_init(app_name=APP_NAME, framework=framework)

        # Run Tests
        Tns.test(app_name=APP_NAME, platform=Platform.ANDROID, emulator=True, justlaunch=True)

    def test_400_invalid_framework_name(self):
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package)
        result = Tns.test_init(app_name=APP_NAME, framework='jasmin', verify=False)
        assert 'Unknown or unsupported unit testing framework: jasmin' in result.output
