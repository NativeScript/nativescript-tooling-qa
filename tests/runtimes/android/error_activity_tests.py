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
from core.utils.device.device_manager import DeviceManager
from data.changes import Sync, ChangeSet
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
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)

    def test_200_error_activity_shown_on_error(self):
        result = Tns.run_android(app_name=APP_NAME, emulator=True, wait=False)
        self.emu.wait_for_text('TAP', timeout=180, retry_delay=10)

        # Break the app to test error activity
        # add workaround with for-cycle for https://github.com/NativeScript/nativescript-cli/issues/3812
        code = 'for (var i = 0; i < 1000000000; i++) {var text = i;} throw new Error("Kill the app!");'
        change = ChangeSet(file_path=os.path.join(Settings.TEST_RUN_HOME, APP_NAME, 'app', 'app.js'),
                           old_value='application.run({ moduleName: "app-root" });',
                           new_value=code)
        Sync.replace(app_name=APP_NAME, change_set=change)

        # Verify logs and screen
        TnsLogs.wait_for_log(log_file=result.log_file,
                             string_list=['StackTrace:', 'Error: Kill the app!', 'line:', 'column:'])
        self.emu.wait_for_text('Exception')
        self.emu.wait_for_text('Logcat')
        self.emu.wait_for_text('Error: Kill the app!')

    def test_400_no_error_activity_in_release_builds(self):
        Tns.run_android(app_name=APP_NAME, release=True, emulator=True, wait=False)
        self.emu.wait_for_text('Unfortunately', timeout=180, retry_delay=10)
        self.emu.is_text_visible('Exception')
