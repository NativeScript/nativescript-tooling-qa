# pylint: disable=unused-argument
# pylint: disable=undefined-variable

import unittest

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from data.changes import Changes
from data.templates import Template
from products.nativescript.perf_helpers import Helpers


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class PrepareAndBuildPerfTests(TnsTest):
    template = Template.HELLO_WORLD_JS.local_package
    change_set = Changes.JSHelloWord.JS

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_001_prepare_data(self):
        Helpers.prepare_data(self.template, self.change_set)

    def test_200_prepare_android_initial(self):
        Helpers.prepare_android_initial(self.template)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_201_prepare_ios_initial(self):
        Helpers.prepare_ios_initial(self.template)

    def test_300_build_android_initial(self):
        Helpers.build_android_initial(self.template)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_301_build_ios_initial(self):
        Helpers.build_ios_initial(self.template)

    def test_310_build_android_incremental(self):
        Helpers.build_android_incremental(self.template)

    @unittest.skipIf(Settings.HOST_OS != OSType.OSX, 'iOS tests can be executed only on macOS.')
    def test_311_build_ios_incremental(self):
        Helpers.build_ios_incremental(self.template)
