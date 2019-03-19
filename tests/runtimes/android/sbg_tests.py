# -*- coding: utf-8 -*-

"""
Test for android runtime static binding generator
"""
# pylint: disable=invalid-name

import os

from core.base_test.tns_test import TnsTest
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from core.settings.Settings import Emulators, Android, TEST_RUN_HOME, AppName
from data.templates import Template
from products.nativescript.tns import Tns

APP_NAME = AppName.DEFAULT


class SBGTests(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emulator = DeviceManager.Emulator.ensure_available(Emulators.DEFAULT)
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))

    def test_300_fail_build_when_sbg_bindings_file_is_missing(self):
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'android-runtime-1286', 'webpack.config.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'webpack.config.js'))
        result = Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=False, bundle=True)

        sbg_bindings_path = os.path.join(TEST_RUN_HOME, APP_NAME, 'platforms', 'android', 'build-tools',
                                         'sbg-bindings.txt')
        js_parser_path = os.path.join(TEST_RUN_HOME, APP_NAME, 'platforms', 'android', 'build-tools',
                                      'jsparser', 'js_parser.js')
        exception_text = "Exception in thread \"main\" java.io.IOException: Couldn\'t find \'{0}\' bindings input " \
                         "file. Most probably there\'s an error in the JS Parser execution. You can run JS Parser " \
                         "with verbose logging by executing \"node \'{1}\' enableErrorLogging\"" \
            .format(sbg_bindings_path, js_parser_path)
        assert "BUILD FAILED" in result.output, "Expected output not found"
        assert exception_text in result.output, "Expected output not found"
