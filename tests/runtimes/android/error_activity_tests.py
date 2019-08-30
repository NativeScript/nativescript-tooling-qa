"""
Test for android error activity.

Verify that:
 - If error happens error activity is displayed (debug mode).
 - Stack trace of the error is printed in console.
 - No error activity in release builds.
"""
import os

from core.base_test.tns_test import TnsTest
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File
from core.utils.assertions import Assert
from core.utils.wait import Wait
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs

APP_NAME = Settings.AppName.DEFAULT


class AndroidErrorActivityTests(TnsTest):
    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)

        # Start emulator
        cls.emulator = DeviceManager.Emulator.ensure_available(Settings.Emulators.EMU_API_29)

    def test_200_error_activity_shown_on_error(self):
        result = Tns.run_android(app_name=APP_NAME, emulator=True, wait=False)
        self.emulator.wait_for_text('TAP', timeout=180, retry_delay=10)

        # Break the app to test error activity
        # add workaround with for-cycle for https://github.com/NativeScript/nativescript-cli/issues/3812
        wait_code = 'var e = new Date().getTime() + 3000; while (new Date().getTime() <= e) {} '
        exception_code = 'throw new Error("Kill the app!");'
        file_path = os.path.join(Settings.TEST_RUN_HOME, APP_NAME, 'app', 'app.js')
        old_value = 'application.run({ moduleName: "app-root" });'
        new_value = wait_code + exception_code
        File.replace(path=file_path, old_string=old_value, new_string=new_value, backup_files=True)
        # Verify logs and screen
        TnsLogs.wait_for_log(log_file=result.log_file,
                             string_list=['StackTrace:', 'Error: Kill the app!'])

        if self.emulator.version < 10.0:
            regex_to_check = r"""System\.err: Error: Kill the app!
System\.err: File: \(file:///app/app\.js:\d+:\d+\)
System.err: StackTrace: 
System\.err: 	\(file:///app/app.js:\d+:\d+\)
System\.err: 	at \./app\.js\(file:///data/data/org\.nativescript\.TestApp/files/app/bundle\.js:\d+:\d+\)
System\.err: 	at __webpack_require__\(file:///app/webpack/bootstrap:\d+:\d+\)
System\.err: 	at checkDeferredModules\(file:///app/webpack/bootstrap:\d+:\d+\)
System\.err: 	at webpackJsonpCallback\(file:///app/webpack/bootstrap:\d+:\d+\)
System\.err: 	at \(file:///data/data/org\.nativescript\.TestApp/files/app/bundle\.js:\d+:\d+\)
System\.err: 	at require\(:\d+:\d+\)""" # noqa: E501, E261, W291
        else:
            regex_to_check = r"""System\.err: Error: Kill the app!
System\.err: File: \(file:///app/app\.js:\d+:\d+\)
System.err: 
System.err: StackTrace: 
System\.err: 	\(file:///app/app.js:\d+:\d+\)
System\.err: 	at \./app\.js\(file:///data/data/org\.nativescript\.TestApp/files/app/bundle\.js:\d+:\d+\)
System\.err: 	at __webpack_require__\(file:///app/webpack/bootstrap:\d+:\d+\)
System\.err: 	at checkDeferredModules\(file:///app/webpack/bootstrap:\d+:\d+\)
System\.err: 	at webpackJsonpCallback\(file:///app/webpack/bootstrap:\d+:\d+\)
System\.err: 	at \(file:///data/data/org\.nativescript\.TestApp/files/app/bundle\.js:\d+:\d+\)
System\.err: 	at require\(:\d+:\d+\)"""  # noqa: E501, E261, W291

        Assert.assert_with_regex(File.read(result.log_file),
                                 regex_to_check)
        self.emulator.wait_for_text('Exception')
        self.emulator.wait_for_text('Logcat')
        self.emulator.wait_for_text('Error: Kill the app!')

    def test_400_no_error_activity_in_release_builds(self):
        # Break the app to test error activity
        # add workaround with for-cycle for https://github.com/NativeScript/nativescript-cli/issues/3812
        Adb.clear_logcat(self.emulator.id)
        wait_code = 'var e = new Date().getTime() + 3000; while (new Date().getTime() <= e) {} '
        exception_code = 'throw new Error("Kill the app!");'
        file_path = os.path.join(Settings.TEST_RUN_HOME, APP_NAME, 'app', 'app.js')
        old_value = 'application.run({ moduleName: "app-root" });'
        new_value = wait_code + exception_code
        File.replace(path=file_path, old_string=old_value, new_string=new_value, backup_files=True)
        Tns.run_android(app_name=APP_NAME, release=True, emulator=True, wait=False)
        if self.emulator.version < 10.0:
            self.emulator.wait_for_text('Unfortunately', timeout=180, retry_delay=10)
            self.emulator.is_text_visible('Exception')
        else:
            regex_to_check = r"""System\.err: Error: Kill the app!
.+System\.err: File: \(file:///data/data/org\.nativescript\.TestApp/files/app/bundle\.js:\d+:\d+\)
.+System\.err: 
.+System\.err: StackTrace: 
.+System\.err: 	\(file:///data/data/org\.nativescript\.TestApp/files/app/bundle\.js:\d+:\d+\)
.+System\.err: 	at \./app\.js\(file:///data/data/org\.nativescript\.TestApp/files/app/bundle\.js:\d+:\d+\)
.+System\.err: 	at __webpack_require__\(file:///data/data/org\.nativescript\.TestApp/files/app/runtime\.js:\d+:\d+\)
.+System\.err: 	at checkDeferredModules\(file:///data/data/org.nativescript.TestApp/files/app/runtime.js:\d+:\d+\)
.+System\.err: 	at webpackJsonpCallback\(file:///data/data/org.nativescript.TestApp/files/app/runtime.js:\d+:\d+\)
.+System\.err: 	at \(file:///data/data/org\.nativescript\.TestApp/files/app/bundle\.js:\d+:\d+\)
.+System\.err: 	at require\(:\d+:\d+\)"""  # noqa: E501, E261, W291
            Wait.until(lambda: "Error: Kill the app!" in Adb.get_logcat(self.emulator.id), timeout=240,
                       period=5)
            Assert.assert_with_regex(Adb.get_logcat(self.emulator.id),
                                     regex_to_check)
