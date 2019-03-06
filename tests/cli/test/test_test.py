# pylint: disable=unused-argument
# pylint: disable=undefined-variable

import os

from parameterized import parameterized

from core.base_test.tns_run_test import TnsRunTest
from core.enums.framework_type import FrameworkType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.npm import Npm
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_assert import TnsAssert

APP_NAME = Settings.AppName.DEFAULT

TEST_DATA = [
    ('jasmine-js-android', FrameworkType.JASMINE, Template.HELLO_WORLD_JS, Platform.ANDROID),
    ('jasmine-ng-android', FrameworkType.JASMINE, Template.HELLO_WORLD_NG, Platform.ANDROID),
    ('mocha-js-android', FrameworkType.MOCHA, Template.HELLO_WORLD_JS, Platform.ANDROID),
    ('mocha-ng-android', FrameworkType.MOCHA, Template.HELLO_WORLD_NG, Platform.ANDROID),
    ('qunit-js-android', FrameworkType.QUNIT, Template.HELLO_WORLD_JS, Platform.ANDROID),
]

TEST_DATA_OSX = [
    ('jasmine-js-android', FrameworkType.JASMINE, Template.HELLO_WORLD_JS, Platform.ANDROID),
    ('jasmine-js-ios', FrameworkType.JASMINE, Template.HELLO_WORLD_JS, Platform.IOS),
    ('jasmine-ng-android', FrameworkType.JASMINE, Template.HELLO_WORLD_NG, Platform.ANDROID),
    ('jasmine-ng-ios', FrameworkType.JASMINE, Template.HELLO_WORLD_NG, Platform.IOS),
    ('mocha-js-android', FrameworkType.MOCHA, Template.HELLO_WORLD_JS, Platform.ANDROID),
    ('mocha-js-ios', FrameworkType.MOCHA, Template.HELLO_WORLD_JS, Platform.IOS),
    ('mocha-ng-android', FrameworkType.MOCHA, Template.HELLO_WORLD_NG, Platform.ANDROID),
    ('mocha-ng-ios', FrameworkType.MOCHA, Template.HELLO_WORLD_NG, Platform.IOS),
    ('qunit-js-android', FrameworkType.QUNIT, Template.HELLO_WORLD_JS, Platform.ANDROID),
    ('qunit-js-ios', FrameworkType.QUNIT, Template.HELLO_WORLD_JS, Platform.IOS),
]


def get_data():
    if Settings.HOST_OS == OSType.OSX:
        return TEST_DATA_OSX
    else:
        return TEST_DATA


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class TestsForTnsTest(TnsRunTest):

    @parameterized.expand(get_data())
    def test_100(self, title, framework, template, platform):
        # Create app
        Tns.create(app_name=APP_NAME, template=template.local_package)

        # Add platforms
        if platform == Platform.ANDROID:
            Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)
        elif platform == Platform.IOS:
            Tns.platform_add_ios(app_name=APP_NAME, framework_path=Settings.IOS.FRAMEWORK_PATH)
        else:
            raise Exception('Unknown platform: ' + str(platform))

        # Init tests and run tests
        if Settings.HOST_OS == OSType.WINDOWS and framework == FrameworkType.QUNIT:
            # Hack for qunit on windows (see https://github.com/NativeScript/nativescript-cli/issues/4333)
            Npm.install(package='qunit@2', option='--save-dev', folder=os.path.join(Settings.TEST_RUN_HOME, APP_NAME))
            # Tns test init will still fail with exit code 1, so we use `verify=False` and then assert logs.
            result = Tns.test_init(app_name=APP_NAME, framework=framework, verify=False)
            TnsAssert.test_initialized(app_name=APP_NAME, framework=framework, output=result.output)
        else:
            Tns.test_init(app_name=APP_NAME, framework=framework)

        # Run Tests
        Tns.test(app_name=APP_NAME, platform=Platform.ANDROID, emulator=True, just_launch=True)

    def test_400_invalid_framework_name(self):
        result = Tns.create(app_name=APP_NAME, template=Template.MIN_JS.local_package, update=False, verify=False)
        TnsAssert.created(app_name=APP_NAME, output=result.output, theme=False, webpack=False)
        result = Tns.test_init(app_name=APP_NAME, framework='jasmin', verify=False)
        assert 'Unknown or unsupported unit testing framework: jasmin' in result.output
