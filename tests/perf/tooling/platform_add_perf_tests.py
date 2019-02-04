import os
import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.json_utils import JsonUtils
from core.utils.npm import Npm
from core.utils.perf_utils import PerfUtils
from data.templates import Template
from products.nativescript.tns import Tns

RETRY_COUNT = 3
TOLERANCE = 0.30
APP_NAME = Settings.AppName.DEFAULT
EXPECTED_RESULTS = JsonUtils.read(os.path.join(Settings.TEST_RUN_HOME, 'tests', 'perf', 'data.json'))


# noinspection PyMethodMayBeStatic
class PlatformAddPerfTests(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_100_platform_add_android(self):
        total_time = 0
        for _ in range(RETRY_COUNT):
            Npm.cache_clean()
            Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=False)
            time = Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH).duration
            total_time = total_time + time
        actual = total_time / RETRY_COUNT
        expected = EXPECTED_RESULTS['hello-world-js']['platform_add_android']
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Time for platform add android is not OK.'

    @unittest.skipIf(Settings.HOST_OS is not OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_101_platform_add_ios(self):
        total_time = 0
        for _ in range(RETRY_COUNT):
            Npm.cache_clean()
            Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=False)
            time = Tns.platform_add_ios(app_name=APP_NAME, framework_path=Settings.IOS.FRAMEWORK_PATH).duration
            total_time = total_time + time
        actual = total_time / RETRY_COUNT
        expected = EXPECTED_RESULTS['hello-world-js']['platform_add_ios']
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Time for platform add ios is not OK.'
