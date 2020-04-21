# pylint: disable=unused-argument
# pylint: disable=undefined-variable

import unittest

from parameterized import parameterized

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from data.changes import Changes
from data.templates import Template
from products.nativescript.perf_helpers import Helpers


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class PrepareAndBuildPerfTests(TnsTest):
    TEST_DATA = [
        ('hello-world-ng', Template.HELLO_WORLD_NG.local_package, Changes.NGHelloWorld.TS)
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
        Helpers.prepare_data(template, template_package, change_set)

    @parameterized.expand(TEST_DATA)
    def test_200_prepare_android_initial(self, template, template_package, change_set):
        Helpers.prepare_android_initial(template)

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_201_prepare_ios_initial(self, template, template_package, change_set):
        Helpers.prepare_ios_initial(template)

    @parameterized.expand(TEST_DATA)
    def test_300_build_android_initial(self, template, template_package, change_set):
        Helpers.build_android_initial(template)

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_301_build_ios_initial(self, template, template_package, change_set):
        Helpers.build_ios_initial(template)

    @parameterized.expand(TEST_DATA)
    def test_310_build_android_incremental(self, template, template_package, change_set):
        Helpers.build_android_incremental(template)

    @parameterized.expand(TEST_DATA)
    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_311_build_ios_incremental(self, template, template_package, change_set):
        Helpers.build_ios_incremental(template)
