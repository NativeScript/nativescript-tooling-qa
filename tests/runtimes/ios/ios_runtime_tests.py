# -*- coding: utf-8 -*-
"""
Test for `tns run ios` command with Angular apps (on simulator).
"""
# pylint: disable=invalid-name

import os

from nose.tools import timed

from core.base_test.tns_test import TnsTest
from core.log.log import Log
from core.utils.device.device import Device
from core.utils.device.device_manager import DeviceManager
from core.utils.wait import Wait
from core.utils.npm import Npm
from core.utils.file_utils import File, Folder
from core.settings import Settings
from core.settings.Settings import Simulators, IOS, TEST_RUN_HOME, AppName
from core.utils.device.simctl import Simctl
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs
from data.templates import Template

APP_NAME = AppName.DEFAULT
APP_PATH = os.path.join(Settings.TEST_RUN_HOME, APP_NAME)
TAP_THE_BUTTON = 'Tap the button'


class IOSRuntimeTests(TnsTest):
    plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'plugins', 'sample-plugin', 'src')

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.sim = DeviceManager.Simulator.ensure_available(Simulators.DEFAULT)
        Simctl.uninstall_all(cls.sim)
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_ios(APP_NAME, framework_path=IOS.FRAMEWORK_PATH)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))

    @timed(360)
    def test_201_test_init_mocha_js_stacktrace(self):
        # https://github.com/NativeScript/ios-runtime/issues/565
        Npm.install(package='mocha', folder=APP_PATH)
        Tns.exec_command("test init --framework", cwd=APP_PATH, platform='mocha')

        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-565', 'example.js'),
                  os.path.join(APP_PATH, 'app', 'tests'), True)

        result = File.read(os.path.join(APP_PATH, 'app', 'tests', 'example.js'))
        assert "Mocha test" in result
        assert "Test" in result
        assert "Array" not in result

        result = Tns.exec_command("test ios", cwd=APP_PATH, emulator=True, wait=False)
        # TODO: Bundle: Add path to stack trace assert, (e.g. @file:///app/tests/example.js:5:25')
        # https://github.com/NativeScript/nativescript-cli/issues/4524
        strings = ['JavaScript stack trace',
                   'JS ERROR AssertionError: expected -1 to equal 1']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=120)

    def test_380_tns_run_ios_plugin_dependencies(self):
        """
        https://github.com/NativeScript/ios-runtime/issues/890
        Check app is running when reference plugin A - plugin A depends on plugin B which depends on plugin C.
        Plugin A has dependency only to plugin B.
        Old behavior (version < 4.0.0) was in plugin A to reference plugin B and C.
        """
        # Add plugin with specific dependencies
        Tns.plugin_add(self.plugin_path, path=APP_NAME)

        # `tns run ios` and wait until app is deployed
        result = Tns.run_ios(app_name=APP_NAME, emulator=True, wait=False, verify=False)
        strings = ['Project successfully built', 'Successfully installed on device with identifier', self.sim.id]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=150, check_interval=10)

        # Verify app is running on device
        Device.wait_for_text(self.sim, text=TAP_THE_BUTTON)

        tns_core_framework = 'TNSCore.framework'
        path_to_file = os.path.join(APP_PATH, 'platforms', 'ios', 'TestApp.xcodeproj', 'project.pbxproj')
        if tns_core_framework in File.read(path_to_file):
            Log.info("{0} found in {1}".format(tns_core_framework, path_to_file))
            assert True
        else:
            assert False, "Cannot find {0} in {1}".format(tns_core_framework, path_to_file)

    def test_384_check_for_native_and_js_callstacks(self):
        """
        https://github.com/NativeScript/ios-runtime/pull/1144
        """
        # Replace main-page.js so there is an error
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-pr-1144', 'main-page.js'),
                  os.path.join(APP_PATH, 'app', 'main-page.js'), True)

        result = Tns.run_ios(app_name=APP_NAME, emulator=True, wait=False, verify=False)
        strings = ['Native Stack:',
                   'sig_handler(int)',
                   'JS Stack:',
                   '[native code]',
                   'at onNavigatingTo(file:///app/main-page.js:34:0']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=150, check_interval=10)

        # Verify app is NOT running on device
        test_result = Wait.until(lambda: Simctl.is_process_running(self.sim, 'org.nativescript.' + APP_NAME) is False,
                                 timeout=120, period=5)
        assert test_result, "It seems that " + APP_NAME + " is still running when it should not!"

    def test_385_methods_with_same_name_and_different_parameters(self):
        """
        https://github.com/NativeScript/ios-runtime/issues/877
        PR https://github.com/NativeScript/ios-runtime/pull/1013
        """
        # Replace main-page.js to call methods with the same name but different parameters count
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-877', 'main-page.js'),
                  os.path.join(APP_PATH, 'app', 'main-page.js'), True)

        result = Tns.run_ios(app_name=APP_NAME, emulator=True, wait=False, verify=False)
        strings = ['Successfully synced application',
                   'SayName no param!', 'SayName with 1 param!', 'SayName with 2 params!']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=150, check_interval=10)

        # Verify app is running on device
        Device.wait_for_text(self.sim, text=TAP_THE_BUTTON)

    def test_386_check_native_crash_will_not_crash_when_discardUncaughtJsExceptions_used(self):
        """
        Test native crash will not crash the app when discardUncaughtJsExceptions used
        https://github.com/NativeScript/ios-runtime/issues/1051
        """
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-1051', 'app.js'),
                  os.path.join(APP_PATH, 'app', 'app.js'), True)
        File.copy(
            os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-1051', 'main-view-model.js'),
            os.path.join(APP_PATH, 'app', 'main-view-model.js'), True)
        # Change app package.json so it contains the options for discardUncaughtJsExceptions
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-1051', 'package.json'),
                  os.path.join(APP_PATH, 'app', 'package.json'), True)

        log = Tns.run_ios(app_name=APP_NAME, emulator=True)

        strings = ['CONSOLE LOG file:///app/app.js:47:0: The folder “not-existing-path” doesn’t exist.',
                   'JS:\ncontentsOfDirectoryAtPathError(file:///app/main-view-model.js:6:0)']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)

        # Verify app is running on device
        Device.wait_for_text(self.sim, text=TAP_THE_BUTTON)

        message = 'Native crash should not crash the app when discardUncaughtJsExceptions is used! Logs'
        assert test_result, message + File.read(log.log_file)

    def test_387_test_pointers_and_conversions_to_string(self):
        """
        Test pointers and conversions to strings
        https://github.com/NativeScript/ios-runtime/pull/1069
        https://github.com/NativeScript/ios-runtime/issues/921
        """
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-921', 'special-value',
                               'main-view-model.js'),
                  os.path.join(APP_PATH, 'app', 'main-view-model.js'), True)

        log = Tns.run_ios(app_name=APP_NAME, emulator=True)

        strings = ["<Pointer: 0xfffffffffffffffe>",
                   "<Pointer: 0xffffffffffffffff>",
                   "<Pointer: 0x800000000>"]

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, '-1 pointer is not correct(interop.Pointer)!'

        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-921', 'wrapped-value',
                               'main-view-model.js'),
                  os.path.join(APP_PATH, 'app', 'main-view-model.js'), True)

        strings = ["wrapped: <Pointer: 0xfffffffffffffffe>",
                   "wrapped: <Pointer: 0xffffffffffffffff>",
                   "wrapped: <Pointer: 0x800000000>"]

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'wrapped pointers are not working correctly(interop.Pointer(new Number(value)))!'

        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-921',
                               'toHexString-and-toDecimalString',
                               'main-view-model.js'),
                  os.path.join(APP_PATH, 'app', 'main-view-model.js'), True)

        strings = ["Hex: 0xfffffffffffffffe",
                   "Decimal: -2",
                   "Hex: 0xffffffffffffffff",
                   "Decimal: -1",
                   "Hex: 0x800000000",
                   "Decimal: 34359738368"]

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'toHexString and toDecimalString are not working correctly!'

    def test_388_unicode_char_in_xml(self):
        """
        Test app does not crash when xml includes Unicode characters outside of the basic ASCII set
        https://github.com/NativeScript/ios-runtime/issues/1130
        """
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-1130',
                               'main-page.xml'),
                  os.path.join(APP_PATH, 'app', 'main-page.xml'), True)

        log = Tns.run_ios(app_name=APP_NAME, emulator=True)
        error = ['JS ERROR Error: Invalid autocapitalizationType value:undefined']
        is_error_thrown = Wait.until(lambda: all(er in File.read(log.log_file) for er in error), timeout=30,
                                     period=5)
        assert is_error_thrown is False, 'App should not crash when xml includes Unicode characters outside of the ' \
                                         'basic ASCII set'

        # Verify app is running on device
        Device.wait_for_text(self.sim, text='Tap the button')

    def test_389_add_swift_files_to_xcode_project(self):
        """
        Test that users are be able to add swift files and use it
        https://github.com/NativeScript/ios-runtime/issues/1131
        """

        Folder.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-1131', 'src'),
                    os.path.join(APP_PATH, 'app', 'App_Resources', 'iOS', 'src'), True)

        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-1131',
                               'main-page.js'),
                  os.path.join(APP_PATH, 'app', 'main-page.js'), True)
        log = Tns.run_ios(app_name=APP_NAME, emulator=True)

        # Verify app is running on device
        Device.wait_for_text(self.sim, text='Tap the button')

        strings = ['Swift class property: 123', 'Swift class method: GREAT!']
        result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                            period=5)
        assert result, 'It seems that there\'s a problem with using swift files that are added in App_Resources'

    def test_390_check_correct_name_of_internal_class_is_returned(self):
        """
        Test that NSStringFromClass function returns correct name of iOS internal class
        https://github.com/NativeScript/ios-runtime/issues/1120
        """

        # Delete src folder from the previous test till Folder copy strt to backup folders too
        Folder.clean(os.path.join(APP_PATH, 'app', 'App_Resources', 'iOS', 'src'))

        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-1120',
                               'main-page.js'),
                  os.path.join(APP_PATH, 'app', 'main-page.js'), True)

        log = Tns.run_ios(app_name=APP_NAME, emulator=True)

        # Verify app is running on device
        Device.wait_for_text(self.sim, text='Tap the button')

        string = ['Internal class: UITableViewCellContentView']
        result = Wait.until(lambda: all(st in File.read(log.log_file) for st in string), timeout=60,
                            period=5)
        assert result, 'NSStringFromClass function returns INCORRECT name of iOS internal class!'

    def test_391_native_properties_provided_by_internal_classes_are_available(self):
        """
        Test native properties provided by internal classes are available
        https://github.com/NativeScript/ios-runtime/issues/1149
        """

        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-1149',
                               'main-view-model.js'),
                  os.path.join(APP_PATH, 'app', 'main-view-model.js'), True)

        log = Tns.run_ios(app_name=APP_NAME, emulator=True)

        # Verify app is running on device
        Device.wait_for_text(self.sim, text='Tap the button')

        strings = ['response1:  <NSHTTPURLResponse:', 'response2:  <NSHTTPURLResponse:', 'Status Code: 200']
        result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                            period=5)
        assert result, 'It seems that native properties provided by internal classes are not available'

    def test_392_use_objective_c_plus_plus_file(self):
        """
        https://github.com/NativeScript/ios-runtime/issues/1203
        """

        Folder.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-1203', 'src'),
                    os.path.join(APP_PATH, 'app', 'App_Resources', 'iOS', 'src'), True)

        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-1203',
                               'main-page.js'),
                  os.path.join(APP_PATH, 'app', 'main-page.js'), True)
        log = Tns.run_ios(app_name=APP_NAME, emulator=True)

        strings = ['NativeScript logInfo method called']
        result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                            period=5)

        # Verify app is running on device
        Device.wait_for_text(self.sim, text='Tap the button')

        assert result, 'It seems that there\'s a problem with using objective C++ files that are added in App_Resources'

    def test_398_tns_run_ios_console_time(self):
        # Delete src folder from the previous test till Folder copy strt to backup folders too
        Folder.clean(os.path.join(APP_PATH, 'app', 'App_Resources', 'iOS', 'src'))

        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_NG.local_package, update=True)
        Tns.platform_add_ios(APP_NAME, framework_path=IOS.FRAMEWORK_PATH)
        # Replace app.component.ts to use console.time() and console.timeEnd()

        File.copy(
            os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-843', 'app.component.ts'),
            os.path.join(APP_PATH, 'src', 'app', 'app.component.ts'), True)

        # `tns run ios` and wait until app is deployed
        result = Tns.run_ios(app_name=APP_NAME, emulator=True, wait=False, verify=False)

        # Verify initial state of the app
        strings = ['Project successfully built', 'Successfully installed on device with identifier', self.sim.id]
        assert_result = Wait.until(lambda: all(st in File.read(result.log_file) for st in strings), timeout=200,
                                   period=5)

        assert assert_result, 'App not build correctly! Logs: ' + File.read(result.log_file)

        Device.wait_for_text(self.sim, text="Ter Stegen", timeout=30)

        # Verify console.time() works - issue https://github.com/NativeScript/ios-runtime/issues/843
        console_time = ['CONSOLE INFO startup:']
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=console_time)

    def test_399_tns_run_ios_console_dir(self):
        # NOTE: This test depends on creation of app in test_391_tns_run_ios_console_time
        # Replace app.component.ts to use console.time() and console.timeEnd()

        File.copy(
            os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'ios', 'files', 'ios-runtime-875', 'items.component.ts'),
            os.path.join(APP_PATH, 'src', 'app', 'item', 'items.component.ts'), True)

        # `tns run ios` and wait until app is deployed
        result = Tns.run_ios(app_name=APP_NAME, emulator=True, wait=False,
                             verify=False)

        # Verify sync and initial state of the app
        strings = ['name: Ter Stegen', 'role: Goalkeeper', 'object dump end', self.sim.id]
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings, timeout=90, check_interval=10)
