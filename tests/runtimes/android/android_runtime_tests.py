"""
Test for specific needs of Android runtime.
"""
# pylint: disable=invalid-name
import datetime
import os
import re
import time

import pytz

from core.base_test.tns_test import TnsTest
from core.utils.npm import Npm
from core.utils.run import run
from core.utils.device.device import Device, Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from core.utils.wait import Wait
from core.settings.Settings import Emulators, Android, TEST_RUN_HOME, AppName
from core.enums.platform_type import Platform
from data.templates import Template
from products.nativescript.app import App
from products.nativescript.tns import Tns

APP_NAME = AppName.DEFAULT


class AndroidRuntimeTests(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emulator = DeviceManager.Emulator.ensure_available(Emulators.DEFAULT)
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))

    def test_200_calling_custom_generated_classes_declared_in_manifest(self):
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'calling_custom_generated_classes_declared_in_manifest', 'AndroidManifest.xml'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'src', 'main',
                               'AndroidManifest.xml'))
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'calling_custom_generated_classes_declared_in_manifest', 'my-custom-class.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'my-custom-class.js'))
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                               'calling_custom_generated_classes_declared_in_manifest',
                               'custom-activity.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'custom-activity.js'))
        Adb.clear_logcat(device_id=self.emulator.id)
        Tns.run_android(APP_NAME, device=self.emulator.id, just_launch=True, wait=True)
        assert_result = Wait.until(lambda: 'we got called from onCreate of custom-activity.js' in Adb.get_logcat(
            device_id=self.emulator.id))
        output = Adb.get_logcat(device_id=self.emulator.id)

        # make sure app hasn't crashed
        assert "Displayed org.nativescript.TNSApp/com.tns.ErrorReportActivity" not in output, \
            "App crashed with error activity"
        # check if we got called from custom activity that overrides the default one
        assert assert_result, "Expected output not found! Logs: " + Adb.get_logcat(device_id=self.emulator.id)
        assert_result = Wait.until(lambda: "we got called from onCreate of my-custom-class.js" in Adb.get_logcat(
            device_id=self.emulator.id))
        # make sure we called custom activity declared in manifest
        assert assert_result, "Expected output not found! Logs: " + Adb.get_logcat(device_id=self.emulator.id)

    def test_300_verbose_log_android(self):
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)

        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        File.copy(os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'verbose_log', 'app.js'),
                  os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js'))
        output = File.read(os.path.join(TEST_RUN_HOME, APP_NAME, "app", "app.js"))
        assert "__enableVerboseLogging()" in output, "Verbose logging not enabled in app.js"

        # `tns run android` and wait until app is deployed
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built', 'Successfully installed on device with identifier',
                   'TNS.Native', 'TNS.Java', self.emulator.id]

        Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=240, period=5)
        log = File.read(log.log_file)
        assert "TNS.Native" in log, "__enableVerboseLogging() do not enable TNS.Native logs!"
        assert "TNS.Java" in log, "__enableVerboseLogging() do not enable TNS.Java logs!"

    def test_304_support_HeapByteBuffer_to_ArrayBuffer(self):
        """
         Test support HeapByteBuffer to ArrayBuffer
         https://github.com/NativeScript/android-runtime/issues/1060
        """
        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1060',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js)

        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)
        strings = ['Successfully synced application', '###TEST PASSED###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'HeapByteBuffer to ArrayBuffer conversion is not working'

    def test_317_check_native_crash_will_not_crash_when_discardUncaughtJsExceptions_used(self):
        """
         Test native crash will not crash the app when discardUncaughtJsExceptions used
         https://github.com/NativeScript/android-runtime/issues/1119
        """
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1119',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js)

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1119',
                                 'app.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js')
        File.copy(source=source_js, target=target_js)

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1119',
                                 'main-view-model.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js)

        # Change app package.json so it contains the options for discardUncaughtJsExceptions
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1119',
                                 'package.json')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'package.json')
        File.copy(source=source_js, target=target_js)

        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)
        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Application is not build successfully!'
        Device.wait_for_text(self.emulator, "TAP")
        Adb.is_text_visible(self.emulator.id, "TAP", True)
        Device.click(self.emulator, "TAP", True)

        strings = ["Error: java.lang.Exception: Failed resolving method createTempFile on class java.io.File",
                   "Caused by: java.lang.Exception: Failed resolving method createTempFile on class java.io.File"]

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Native crash should not crash the app when discardUncaughtJsExceptions used fails!'
        Device.screen_match(self.emulator,
                            os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'images',
                                         'Emulator-Api23-Default',
                                         "No-crash-image.png"), timeout=120, tolerance=1)

    def test_318_generated_classes_not_be_deleted_on_rebuild(self):
        """
            https://github.com/NativeScript/nativescript-cli/issues/3560
        """
        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        target = os.path.join(TEST_RUN_HOME, APP_NAME, 'app')
        source = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-904',
                              'MyActivity.js')
        File.copy(source, target)

        Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME))

        assert File.exists(os.path.join(TEST_RUN_HOME, APP_NAME, "app", "MyActivity.js"))
        assert File.exists(
            os.path.join(TEST_RUN_HOME, APP_NAME, "platforms", "android", "app", "src", "main", "java", "com", "tns",
                         "MyActivity.java"))

        File.delete(os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'MyActivity.js'))

        Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME))

        assert not File.exists(
            os.path.join(TEST_RUN_HOME, APP_NAME, "platforms", "android", "app", "src", "main", "java", "com", "tns",
                         "MyActivity.java"))

    def test_350_sgb_fails_generating_custom_activity(self):
        """
        Static Binding Generator fails if class has static properties that are used within the class
        https://github.com/NativeScript/android-runtime/issues/1160
        """
        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)

        source = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1160',
                              'testActivity.android.js')
        target = os.path.join(TEST_RUN_HOME, APP_NAME, 'app')
        File.copy(source=source, target=target)

        Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME))
        activity_class_path = os.path.join(TEST_RUN_HOME, APP_NAME, "platforms", "android", "app", "src", "main",
                                           "java", "com",
                                           "test")

        if File.exists(os.path.join(activity_class_path, "Activity.java")):
            assert True
        else:
            assert False, "Fail: Custom activity class is NOT generated in {0} !".format(activity_class_path)

    def test_390_code_cache_option(self):
        """
        CodeCache option is broken since Android Runtime 4.1.0

        https://github.com/NativeScript/android-runtime/issues/1235
        """
        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1235',
                                 'package.json')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'package.json')
        File.copy(source=source_js, target=target_js)

        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)

        # `tns run android` and wait until app is deployed
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application']
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)

        assert test_result, 'Application not build successfully!'

        code_cache_files = ['app.js.cache', 'main-page.js.cache', 'main-view-model.js.cache']
        json = App.get_package_json(app_name=APP_NAME)
        app_id = json['nativescript']['id']

        # Check that for each .js file, there's a corresponding .js.cache file created on the device
        for code_cache_file in code_cache_files:
            error_message = '{0} file is not found on {1}'.format(code_cache_file, self.emulator.id)
            assert Adb.file_exists(device_id=self.emulator.id, package_id=app_id,
                                   file_name='app/{0}'.format(code_cache_file)), error_message

        # Verify app looks correct inside emulator
        Device.screen_match(self.emulator,
                            os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'images',
                                         'Emulator-Api23-Default',
                                         "hello-world-js.png"), timeout=120, tolerance=1)

    def test_430_verify_JSParser_in_SBG_is_failing_the_build_when_there_is_an_error(self):
        """
         JSParser in SBG fail the build when there is an error
        https://github.com/NativeScript/android-runtime/issues/1152
        """

        # Change main-page.js with sbg Error
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1152',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js)
        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        log = Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=False).output

        assert "FAILURE: Build failed with an exception" in log
        assert "JSParser Error: Not enough or too many arguments passed(0) when trying to extend interface: " \
               "java.util.List in file: main-page" in log
        assert "Execution failed for task ':app:runSbg'" in log

    def test_440_tns_run_android_new_date_work_as_expected_when_changing_timezone(self):
        """
         Test new date is working as expected. Test in different timezones
        """
        output = Adb.run_adb_command("shell settings put global auto_time_zone 0", self.emulator.id, wait=True)
        assert output.output == '', "Failed to change auto timezone!"

        output = Adb.run_adb_command("shell settings put system time_12_24 24", self.emulator.id, wait=True)
        assert output.output == '', "Failed to change system format to 24!"

        output = Adb.run_adb_command("shell settings put global time_zone UTC", self.emulator.id, wait=True)
        assert output.output == '', "Failed to change timezone!"
        output = Adb.run_adb_command("shell setprop persist.sys.timezone UTC", self.emulator.id, wait=True)
        assert output.output == '', "Failed to change timezone!"

        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-961',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js)
        # Change main-view-model.js so it contains the new date logging functionality
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-961',
                                 'main-view-model.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js)
        # Change app package.json so it contains the options for remove V8 date cache
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-961',
                                 'package.json')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'package.json')

        File.copy(source=source_js, target=target_js)

        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application', '### TEST END ###']
        assert_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=240,
                                   period=5)
        assert assert_result, "Application not build correct! Logs: " + File.read(log.log_file)
        # Get UTC date and time
        time_utc = datetime.datetime.utcnow()

        # Generate regex for asserting date and time
        date_to_find_gmt = time_utc.strftime(r'%a %b %d %Y %H:.{2}:.{2}') + r" GMT\+0000 \(UTC\)"
        test_result = Wait.until(lambda: Device.is_text_visible(self.emulator, "TAP", True), timeout=200,
                                 period=5)
        assert test_result, "TAP Button is missing on the device"
        Device.click(self.emulator, text="TAP", case_sensitive=True)
        assert_result = Wait.until(lambda: "GMT+0000 (UTC)" in File.read(log.log_file), timeout=30, period=5)
        assert assert_result, "Missing log for time! Logs: " + File.read(log.log_file)
        # Assert date time is correct
        assert_result = Wait.until(lambda: re.search(date_to_find_gmt, File.read(log.log_file)), timeout=20,
                                   period=5)
        assert assert_result, 'Date {0} was not found! \n Log: \n {1}'.format(date_to_find_gmt, file.read(file(log)))
        # Get Los Angeles date and time
        los_angeles_time = time_utc.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("America/Los_Angeles"))

        # Open Date and time settings to change the timezone
        output = Adb.run_adb_command("shell am start -a android.settings.DATE_SETTINGS", self.emulator.id, wait=True)
        assert_text = 'Starting: Intent { act=android.settings.DATE_SETTINGS }'
        assert assert_text in output.output, "Failed to start Date and Time settings activity!"

        # Change TimeZone
        test_result = Wait.until(lambda: Device.is_text_visible(self.emulator, "Select time zone", True), timeout=30,
                                 period=5)
        assert test_result, "Select time zone Button is missing on the device"
        Device.click(self.emulator, text="Select time zone")
        test_result = Wait.until(lambda: Device.is_text_visible(self.emulator, "Pacific Daylight Time", True),
                                 timeout=30, period=5)
        assert test_result, "Pacific Daylight Time Button is missing on the device"
        Device.click(self.emulator, text="Pacific Daylight Time")

        # Open the test app again
        output = Adb.run_adb_command("shell am start -n org.nativescript.TestApp/com.tns.NativeScriptActivity",
                                     self.emulator.id, wait=True)
        assert_text = 'Starting: Intent { cmp=org.nativescript.TestApp/com.tns.NativeScriptActivity }'
        assert assert_text in output.output, "Failed to start Nativescript test app activity!"
        test_result = Wait.until(lambda: Device.is_text_visible(self.emulator, "TAP", True), timeout=30,
                                 period=5)
        assert test_result, "TAP Button is missing on the device"
        Device.click(self.emulator, text="TAP", case_sensitive=True)
        assert_result = Wait.until(lambda: "GMT-0700 (PDT)" in File.read(log.log_file), timeout=240, period=5)
        assert assert_result, "Missing log for time! Logs: " + File.read(log.log_file)
        # Generate regex for asserting date and time
        date_to_find_los_angeles = los_angeles_time.strftime(r'%a %b %d %Y %H:.{2}:.{2}') + r" GMT\-0700 \(PDT\)"
        # Assert date time is correct
        assert_result = Wait.until(lambda: re.search(date_to_find_los_angeles, File.read(log.log_file)), timeout=20,
                                   period=5)
        assert assert_result, 'Date {0} was not found! \n Log: \n {1}'.format(date_to_find_los_angeles,
                                                                              file.read(file(log)))

    def test_442_assert_arm64_is_enabled_by_default(self):
        """
         Test arm64-v8 is enabled by default
        """
        Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=True)
        apk_folder = os.path.join(TEST_RUN_HOME, APP_NAME, "platforms", "android", "app", "build", "outputs", "apk",
                                  "debug")
        apk_file = os.path.join(apk_folder, "app-debug.apk")
        apk_folder_to_unzip = os.path.join(apk_folder, "apk")
        Folder.create(apk_folder_to_unzip)
        command = "unzip " + apk_file + " -d " + apk_folder_to_unzip
        run(command, wait=False)
        time.sleep(20)
        unzip_apk_folder = os.path.join(apk_folder, "apk")
        arm64_folder = os.path.join(unzip_apk_folder, "lib", "arm64-v8a")
        assert Folder.exists(arm64_folder), "arm64-v8a architecture is missing!"
        error_message = "libNativeScript.so in arm64-v8a folder is missing!"
        assert File.exists(os.path.join(arm64_folder, "libNativeScript.so")), error_message

    def test_443_build_app_and_assert_that_tns_core_modules_could_be_updated(self):
        """
         Test update of tns-core-modules works correctly if you have build the app first
         https://github.com/NativeScript/android-runtime/issues/1257
        """
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Successfully synced application', 'on device', self.emulator.id]

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=240,
                                 period=5)
        assert test_result, "App not build correctly ! Logs: " + File.read(log.log_file)
        Npm.install(package="tns-core-modules@next", folder=os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.plugin_add(plugin_name="nativescript-ui-dataform", path=os.path.join(TEST_RUN_HOME, APP_NAME))
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Successfully synced application', 'on device', self.emulator.id]

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=120,
                                 period=5)
        assert test_result, "App not build correctly after updating tns-core modules! Logs: " + File.read(log.log_file)
        test_result = Wait.until(lambda: Device.is_text_visible(self.emulator, "TAP", True), timeout=90,
                                 period=5)
        assert test_result, "TAP Button is missing on the device! Update of tns-core-modules not successful!"
