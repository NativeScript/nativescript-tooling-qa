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
from core.utils.wait import Wait
from data.templates import Template
from products.nativescript.tns import Tns

APP_NAME = AppName.DEFAULT


class SBGTests(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emulator = DeviceManager.Emulator.ensure_available(Emulators.DEFAULT)
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)

    def tearDown(self):
        TnsTest.tearDown(self)

    def test_300_fail_build_when_sbg_bindings_file_is_missing(self):
        # edit webpack.config.js where devtool: "eval"
        webpack_config = os.path.join(TEST_RUN_HOME, APP_NAME, 'webpack.config.js')
        old_str = "devtool: hiddenSourceMap ? \"hidden-source-map\" : (sourceMap ? \"inline-source-map\" : \"none\"),"
        new_str = "devtool: \"eval\","

        File.replace(path=webpack_config, old_string=old_str, new_string=new_str, backup_files=True)
        result = Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=False, bundle=True)

        sbg_bindings_path = os.path.join(TEST_RUN_HOME, APP_NAME, 'platforms', 'android', 'build-tools',
                                         'sbg-bindings.txt')
        js_parser_path = os.path.join(TEST_RUN_HOME, APP_NAME, 'platforms', 'android', 'build-tools',
                                      'jsparser', 'js_parser.js')
        exception_text = "Error executing Static Binding Generator: Couldn\'t find \'{0}\' bindings input " \
                         "file. Most probably there\'s an error in the JS Parser execution. You can run JS Parser " \
                         "with verbose logging by executing \"node \'{1}\' enableErrorLogging\"" \
            .format(sbg_bindings_path, js_parser_path)
        assert exception_text in result.output, "Expected output not found"

    def test_301_check_if_sbg_is_working_correctly_with_nativescript_purchase_plugin(self):
        """
        https://github.com/NativeScript/android-runtime/issues/1329
        """
        Tns.plugin_add("nativescript-purchase", path=APP_NAME, verify=False)

        Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=True)

    def test_302_test_SBG_works_when_you_have_nativescript_property_in_package_json(self):
        """
         https://github.com/NativeScript/android-runtime/issues/1409
        """

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1409',
                                 'package.json')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'package.json')
        File.copy(source=source_js, target=target_js, backup_files=True)
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1409',
                                 'new', 'package.json')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'new', 'package.json')
        new_folder = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'new')
        Folder.create(new_folder)
        File.copy(source=source_js, target=target_js, backup_files=True)
        webpack_config = os.path.join(TEST_RUN_HOME, APP_NAME, 'webpack.config.js')
        old_string = 'new nsWebpack.GenerateNativeScriptEntryPointsPlugin("bundle"),'
        new_string = 'new CopyWebpackPlugin(dataToCopy), new nsWebpack.GenerateNativeScriptEntryPointsPlugin("bundle"),'
        File.replace(path=webpack_config, old_string=old_string, new_string=new_string, backup_files=True)
        old_string = 'const dist = resolve(projectRoot, nsWebpack.getAppPath(platform, projectRoot));'
        new_string = """    const dist = resolve(projectRoot, nsWebpack.getAppPath(platform, projectRoot));
        const fileName = "package.json"
        const dataInfo =  {
            from: `../app/new/${fileName}`,
            to: `${dist}/new/${fileName}`,
        }
        env.externals = [fileName];
        const dataToCopy = [dataInfo];"""
        File.replace(path=webpack_config, old_string=old_string, new_string=new_string, backup_files=False)
        log = Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=False).output
        test_result = Wait.until(lambda: "Project successfully built." in log, timeout=300, period=5)
        assert test_result, 'App not build correct! Logs:' + log
