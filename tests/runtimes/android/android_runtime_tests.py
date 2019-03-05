"""
Test for specific needs of Android runtime.
"""
# pylint: disable=invalid-name
import os

from core.base_test.tns_test import TnsTest
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
    custom_js_file = os.path.join(APP_NAME, "app", "my-custom-class.js")
    tns_folder = os.path.join(APP_NAME, 'platforms', 'android/', 'app', 'src', 'main', "java", "com", "tns")
    gen_folder = os.path.join(tns_folder, "gen")
    generated_java_file = os.path.join(tns_folder, "MyJavaClass.java")

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emulator = DeviceManager.Emulator.ensure_available(Emulators.DEFAULT)
        Folder.clean('./' + APP_NAME)

    def tearDown(self):
        Tns.kill()
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(APP_NAME)

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
        Wait.until(lambda: 'we got called from onCreate of custom-activity.js' in Adb.get_logcat(
            device_id=self.emulator.id))
        output = Adb.get_logcat(device_id=self.emulator.id)

        # make sure app hasn't crashed
        assert "Displayed org.nativescript.TNSApp/com.tns.ErrorReportActivity" not in output, \
            "App crashed with error activity"
        # check if we got called from custom activity that overrides the default one
        assert "we got called from onCreate of custom-activity.js" in output, "Expected output not found"
        # make sure we called custom activity declared in manifest
        assert "we got called from onCreate of my-custom-class.js" in output, "Expected output not found"

    def test_300_verbose_log_android(self):
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
        File.copy(src=source_js, target=target_js)

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
        File.copy(src=source_js, target=target_js)

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1119',
                                 'app.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js')
        File.copy(src=source_js, target=target_js)

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1119',
                                 'main-view-model.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js')
        File.copy(src=source_js, target=target_js)

        # Change app package.json so it contains the options for discardUncaughtJsExceptions
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1119',
                                 'package.json')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'package.json')
        File.copy(src=source_js, target=target_js)

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
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)

        source = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1160',
                              'testActivity.android.js')
        target = os.path.join(TEST_RUN_HOME, APP_NAME, 'app')
        File.copy(src=source, target=target)

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
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1235',
                                 'package.json')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'package.json')
        File.copy(src=source_js, target=target_js)

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
        File.copy(src=source_js, target=target_js)
        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        log = Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=False).output

        assert "FAILURE: Build failed with an exception" in log
        assert "JSParser Error: Not enough or too many arguments passed(0) when trying to extend interface: " \
               "java.util.List in file: main-page" in log
        assert "Execution failed for task ':app:runSbg'" in log
