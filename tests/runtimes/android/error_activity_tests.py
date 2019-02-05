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

APP_NAME = Settings.AppName.DEFAULT


class AndroidErrorActivityTests(TnsTest):
    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)

        # Break the app to test error activity
        change = ChangeSet(file_path=os.path.join(Settings.TEST_RUN_HOME, APP_NAME, 'app', 'app.js'),
                           old_value='application.run({ moduleName: "app-root" });',
                           new_value='throw new Error("Kill the app!");')
        Sync.replace(app_name=APP_NAME, change_set=change)

        # Start emulator
        cls.emu = DeviceManager.Emulator.ensure_available(Settings.Emulators.DEFAULT)

    def test_200_error_activity_shown_on_error(self):
        Tns.run_android(app_name=APP_NAME, emulator=True, wait=False)
        self.emu.wait_for_text('Exception', timeout=180, retry_delay=10), 'Error activity not found on device!'
        self.emu.wait_for_text('Logcat'), 'Error activity not found on device!'
        self.emu.wait_for_text('Error: Kill the app!'), 'Error activity not found on device!'
        # TODO: Verify stack trace of the error is printed in console (waiting nativescript-tooling-qa/pull/26).

    def test_400_no_error_activity_in_release_builds(self):
        Tns.run_android(app_name=APP_NAME, release=True, emulator=True, wait=False)
        self.emu.wait_for_text('Unfortunately', timeout=180, retry_delay=10), 'No error that app crashed!'
        self.emu.is_text_visible('Exception'), 'Error activity found on device!'
