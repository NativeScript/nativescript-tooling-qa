# pylint: disable=unused-argument
# pylint: disable=undefined-variable

import unittest

from parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.perf_utils import PerfUtils
from data.changes import Changes
from data.templates import Template
from products.nativescript.perf_helpers import Helpers

TOLERANCE = 0.20


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class PrepareAndBuildPerfTests(TnsTest):
    TEST_DATA = [
        ('hello-world-js', Template.HELLO_WORLD_JS.local_package, Changes.JSHelloWord.JS)
    ]

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    @parameterized.expand(TEST_DATA)
    def test_001_prepare_data(self, template, template_package, change_set):
        android_result_file = Helpers.get_result_file_name(template, Platform.ANDROID)
        ios_result_file = Helpers.get_result_file_name(template, Platform.IOS)
        Helpers.prepare_and_build(template=template_package, platform=Platform.ANDROID,
                                  change_set=change_set, result_file=android_result_file)
        Helpers.prepare_and_build(template=template_package, platform=Platform.IOS,
                                  change_set=change_set, result_file=ios_result_file)

    @parameterized.expand(TEST_DATA)
    def test_200_prepare_android_initial(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, 'prepare_initial')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, 'prepare_initial')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Initial android prepare time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_201_prepare_ios_initial(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.IOS, 'prepare_initial')
        expected = Helpers.get_expected_result(template, Platform.IOS, 'prepare_initial')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Initial ios prepare time is not OK.'

    @parameterized.expand(TEST_DATA)
    def test_300_build_android_initial(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, 'build_initial')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, 'build_initial')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Initial android build time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_301_build_ios_initial(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.IOS, 'build_initial')
        expected = Helpers.get_expected_result(template, Platform.IOS, 'build_initial')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Initial ios build time is not OK.'

    @parameterized.expand(TEST_DATA)
    def test_310_build_android_incremental(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.ANDROID, 'build_incremental')
        expected = Helpers.get_expected_result(template, Platform.ANDROID, 'build_incremental')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Incremental android build time is not OK.'

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_311_build_ios_incremental(self, template, template_package, change_set):
        actual = Helpers.get_actual_result(template, Platform.IOS, 'build_incremental')
        expected = Helpers.get_expected_result(template, Platform.IOS, 'build_incremental')
        assert PerfUtils.is_value_in_range(actual, expected, TOLERANCE), 'Incremental ios build time is not OK.'
