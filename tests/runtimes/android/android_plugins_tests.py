"""
Test for specific needs of Android runtime.
"""
# pylint: disable=invalid-name
import os
import json

from core.base_test.tns_test import TnsTest
from core.utils.assertions import Assert
from core.utils.device.adb import Adb
from core.utils.device.device import Device
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from core.utils.wait import Wait
from core.settings.Settings import Emulators, Android, TEST_RUN_HOME, AppName
from core.enums.platform_type import Platform
from data.templates import Template
from products.nativescript.tns import Tns

PLATFORM_ANDROID_APK_DEBUG_PATH = os.path.join('platforms', 'android', 'app', 'build', 'outputs', 'apk', 'debug')
APP_NAME = AppName.DEFAULT
APK_DEBUG_PATH = os.path.join(TEST_RUN_HOME, APP_NAME, PLATFORM_ANDROID_APK_DEBUG_PATH, "app-debug.apk")
ANALYTICS_FILE = os.path.join(TEST_RUN_HOME, APP_NAME, 'platforms', 'android', 'analytics', 'build-statistics.json')


class AndroidRuntimePluginTests(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emulator = DeviceManager.Emulator.ensure_available(Emulators.DEFAULT)
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))

    def test_308_native_package_in_plugin_include_gradle_with_compile(self):
        """
         Test native packages in plugin could be used with compile in include gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """
        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins", 'compile', 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        # Change app include.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "compile", 'app.gradle')
        target_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins",
                                 'without_dependency', 'src', 'platforms', 'android', 'include.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins", 'app.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)

        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                   "plugins",
                                   'without_dependency', 'src')
        output = Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)
        assert "Successfully installed plugin mylib" in output.output, "mylib plugin not installed correctly!"
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application', '###TEST COMPILE PLUGIN PASSED###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Native packages could not be used in plugin with compile in include gradle'
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)

    def test_309_native_package_in_plugin_include_gradle_with_implementation(self):
        """
         Test native packages in plugin could be used with implementation in include gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """
        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins", 'implementation', 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        # Change app include.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "implementation", 'app.gradle')
        target_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins",
                                 'without_dependency', 'src', 'platforms', 'android', 'include.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins", 'app.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)

        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                   "plugins",
                                   'without_dependency', 'src')
        output = Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)
        assert "Successfully installed plugin mylib" in output.output, "mylib plugin not installed correctly!"

        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application', '###TEST IMPLEMENTATION PLUGIN PASSED###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Native packages could not be used in plugin with implementation in include gradle'
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)

    def test_310_native_package_in_plugin_include_gradle_with_api(self):
        """
         Test native packages in plugin could be used with api in include gradle
         https://github.com/NativeScript/android-runtime/issues/993
        """

        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins", 'api', 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        # Change app include.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993', "api",
                                 'app.gradle')
        target_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins",
                                 'without_dependency', 'src', 'platforms', 'android', 'include.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)
        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins", 'app.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)

        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                   "plugins",
                                   'without_dependency', 'src')
        output = Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)
        assert "Successfully installed plugin mylib" in output.output, "mylib plugin not installed correctly!"
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application', '###TEST API PLUGIN PASSED###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Native packages could not be used in plugin with api in include gradle'
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)

    def test_311_native_package_in_arr_plugin(self):
        """
         Test native packages in arr plugin
         https://github.com/NativeScript/android-runtime/issues/993
        """

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins",
                                 'with_dependency', 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)

        # Change app app.gradle so it contains the dependencies to com.github.myinnos:AwesomeImagePicker:1.0.2
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                 "plugins", 'app.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)
        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-993',
                                   "plugins",
                                   'with_dependency', 'src')
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)
        output = Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)
        assert "Successfully installed plugin mylib" in output.output, "mylib plugin not installed correctly!"
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application', '###TEST ARR PLUGIN PASSED###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Native packages could not be used in arr plugin'
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)

    def test_312_check_minsdk_error_when_building_plugin_with_api23(self):
        """
         Test plugin with minSdk(23) fails when build with default minSdk(17)
         https://github.com/NativeScript/android-runtime/issues/1104
        """

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1104',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)

        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        if File.exists(target_js):
            File.delete(target_js, True)
        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1104',
                                   "plugin", 'src')
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)
        output = Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)
        assert "Successfully installed plugin mylib" in output.output, "mylib plugin not installed correctly!"
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = [
            'uses-sdk:minSdkVersion 17 cannot be smaller than version 23 declared in library [:com.tns-release:]',
            'as the library might be using APIs not available in 17',
            'Suggestion: use a compatible library with a minSdk of at most 17',
            'or increase this project\'s minSdk version to at least 23',
            'or use tools:overrideLibrary="com.example.comtns" to force usage (may lead to runtime failures)']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Should not be able to build with plugin which minsdk version is 23!'
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)

    def test_313_check_minsdk_could_be_set_in_app_gradle(self):
        """
         Test minSdk works in app.gradle
         https://github.com/NativeScript/android-runtime/issues/1104
        """

        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1104',
                                 'app.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1104',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)

        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)
        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1104',
                                   "plugin", 'src')
        output = Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)
        assert "Successfully installed plugin mylib" in output.output, "mylib plugin not installed correctly!"

        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application', '### TEST SHOULD NOT CRASH ###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Minsdk set in app.gradle is not working! Logs: ' + File.read(log.log_file)
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)

    def test_314_check_minsdk_set_in_app_gradle_18(self):
        """
         Test minSdk in app.gradle set to 18
         https://github.com/NativeScript/android-runtime/issues/1104
        """
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1104',
                                 'api18_gradle', 'app.gradle')
        File.copy(source=source_js, target=target_js, backup_files=True)
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1104',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js, backup_files=True)

        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)
        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1104',
                                   "plugin", 'src')
        output = Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)
        assert "Successfully installed plugin mylib" in output.output, "mylib plugin not installed correctly!"

        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Manifest merger failed : uses-sdk:minSdkVersion 18',
                   'cannot be smaller than version 23 declared in library ',
                   'as the library might be using APIs not available in 18']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        error_message = 'Test minSdk in AndroidManifest set to 23 and app.gradle set to 17 fails! Logs: '
        assert test_result, error_message + File.read(log.log_file)
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)

    def test_360_applying_before_plugins_gradle(self):
        """
        Applying before-plugin.gradle file before plugin's include.gradle

        https://github.com/NativeScript/android-runtime/issues/1183
        """

        source = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1183',
                              'before-plugins.gradle')
        target = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source, target=target, backup_files=True)

        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)
        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'sample-plugin', 'src')
        Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)
        output = Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=False)
        messages = "MESSAGE: Before plugins gradle is applied!\nMESSAGE: Plugin include gradle is applied!"
        assert messages in output.output, "FAIL: before-plugins.gradle is NOT applied correctly!"
        Tns.plugin_remove("sample-plugin", verify=False, path=APP_NAME)

    def test_451_support_external_buildscript_config_in_plugin(self):
        """
        Support external buildscript configurations - buildscript.gradle file placed in plugin folder
        https://github.com/NativeScript/android-runtime/issues/1279
        """
        Tns.plugin_remove("sample-plugin", verify=False, path=APP_NAME)

        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1279',
                                         'in-plugin', 'app.gradle')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)

        source_build_script_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                                  'android-runtime-1279', 'buildscript.gradle')
        target_build_script_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source_build_script_gradle, target=target_build_script_gradle, backup_files=True)

        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1279',
                                   'in-plugin',
                                   'sample-plugin-2', 'src')
        Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)

        Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=True)
        Tns.plugin_remove("sample-plugin-2", verify=False, path=APP_NAME)

    @staticmethod
    def assert_kotlin_is_working(emulator):
        assert File.exists(APK_DEBUG_PATH)
        assert File.is_file_in_zip(APK_DEBUG_PATH, os.path.join("kotlin")), "Kotlin is not working!"
        Device.click(emulator, text="TAP", case_sensitive=True)
        error_message = "Kotlin code is not executed correctly! Logs: "
        assert "Kotlin is here!" in Adb.get_logcat(emulator.id), error_message + Adb.get_logcat(emulator.id)

    def test_452_support_gradle_properties_for_enable_Kotlin_with_jar(self):
        """
        Support gradle.properties file for enable Kotlin
        https://github.com/NativeScript/android-runtime/issues/1459
        https://github.com/NativeScript/android-runtime/issues/1463
        """
        Tns.plugin_remove("sample-plugin-2", verify=False, path=APP_NAME)
        Adb.clear_logcat(self.emulator.id)
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                         'android-runtime-1463-1459', 'gradle.properties')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                         'android-runtime-1463-1459', 'test-jar-1.0-SNAPSHOT.jar')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'libs')
        Folder.create(target_app_gradle)
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1463-1459',
                                 'main-view-model.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application']
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        messages = "App with Kotlin enabled and kotlin jar not build correctly! Logs: "
        assert test_result, messages + File.read(log.log_file)

        self.assert_kotlin_is_working(self.emulator)
        with open(ANALYTICS_FILE, "r") as read_file:
            data = json.load(read_file)
            error_message = "kotlinUsage->hasKotlinRuntimeClasses is not set to True! Analytics is not correct!"
            assert data["kotlinUsage"]["hasKotlinRuntimeClasses"] is True, error_message
            error_message = "kotlinUsage->hasUseKotlinPropertyInApp is not set to True! Analytics is not correct!"
            assert data["kotlinUsage"]["hasUseKotlinPropertyInApp"] is True, error_message

    def test_453_support_Kotlin_with_jar_without_use_kotlin(self):
        """
        Support gradle.properties file for enable Kotlin
        https://github.com/NativeScript/android-runtime/issues/1459
        https://github.com/NativeScript/android-runtime/issues/1463
        """

        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                         'android-runtime-1463-1459', 'analytics', 'gradle.properties')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                         'android-runtime-1463-1459', 'test-jar-1.0-SNAPSHOT.jar')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'libs')
        Folder.create(target_app_gradle)
        Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=True)

        with open(ANALYTICS_FILE, "r") as read_file:
            data = json.load(read_file)
            error_message = "kotlinUsage->hasKotlinRuntimeClasses is not set to False! Analytics is not correct!"
            assert data["kotlinUsage"]["hasKotlinRuntimeClasses"] is False, error_message
            error_message = "kotlinUsage->hasUseKotlinPropertyInApp is not set to False! Analytics is not correct!"
            assert data["kotlinUsage"]["hasUseKotlinPropertyInApp"] is False, error_message

        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)
        # Not working https://github.com/NativeScript/android-runtime/issues/1522
        # Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=True).output
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1463-1459',
                                 'main-view-model.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Successfully synced application org.nativescript.TestApp on device ']
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        messages = "App with Kotlin enabled and kotlin jar not build correctly! Logs: "
        assert test_result, messages + File.read(log.log_file)
        self.assert_kotlin_is_working(self.emulator)
        with open(ANALYTICS_FILE, "r") as read_file:
            data = json.load(read_file)
            error_message = "kotlinUsage->hasKotlinRuntimeClasses is not set to True! Analytics is not correct!"
            assert data["kotlinUsage"]["hasKotlinRuntimeClasses"] is True, error_message
            error_message = "kotlinUsage->hasUseKotlinPropertyInApp is not set to False! Analytics is not correct!"
            assert data["kotlinUsage"]["hasUseKotlinPropertyInApp"] is False, error_message

    def test_454_support_gradle_properties_for_enable_Kotlin_with_kotlin_file(self):
        """
        Support gradle.properties file for enable Kotlin
        https://github.com/NativeScript/android-runtime/issues/1459
        https://github.com/NativeScript/android-runtime/issues/1463
        """
        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)

        Adb.clear_logcat(self.emulator.id)
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                         'android-runtime-1463-1459', 'gradle.properties')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                         'android-runtime-1463-1459', 'Test.kt')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'src', 'main',
                                         'java', 'com')
        Folder.create(target_app_gradle)
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1463-1459',
                                 'main-view-model.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        messages = "App with Kotlin enabled and kotlin jar not build correctly! Logs: "
        assert test_result, messages + File.read(log.log_file)
        self.assert_kotlin_is_working(self.emulator)
        with open(ANALYTICS_FILE, "r") as read_file:
            data = json.load(read_file)
            error_message = "kotlinUsage->hasKotlinRuntimeClasses is not set to False! Analytics is not correct!"
            assert data["kotlinUsage"]["hasKotlinRuntimeClasses"] is True, error_message
            error_message = "kotlinUsage->hasUseKotlinPropertyInApp is not set to True! Analytics is not correct!"
            assert data["kotlinUsage"]["hasUseKotlinPropertyInApp"] is True, error_message

    def test_455_analytics_not_generated_when_not_set_as_property_for_enable_Kotlin_with_jar(self):
        """
        Support gradle.properties file for enable Kotlin
        https://github.com/NativeScript/android-runtime/issues/1459
        https://github.com/NativeScript/android-runtime/issues/1463
        """
        # caused by https://github.com/NativeScript/nativescript-cli/issues/5083
        kotlin_file_in_src = os.path.join(TEST_RUN_HOME, APP_NAME, 'platforms', 'android', 'app', 'src', 'main', 'java',
                                          'com',
                                          'Test.kt')
        kotlin_file_in_build = os.path.join(TEST_RUN_HOME, APP_NAME, 'platforms', 'android', 'app', 'build', 'tmp',
                                            'kotlin-classes', 'debug', 'com',
                                            'Test.class')
        if File.exists(kotlin_file_in_src):
            File.delete(kotlin_file_in_src)
        if File.exists(kotlin_file_in_build):
            File.delete(kotlin_file_in_build)
        else:
            assert False, "Temp gradle folder is missing for generated kotlin file!"

        # bug ends here
        if File.exists(ANALYTICS_FILE):
            File.delete(ANALYTICS_FILE)
        Adb.clear_logcat(self.emulator.id)
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                         'android-runtime-1463-1459', 'no-analytics', 'gradle.properties')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                         'android-runtime-1463-1459', 'test-jar-1.0-SNAPSHOT.jar')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'libs')
        Folder.create(target_app_gradle)
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1463-1459',
                                 'main-view-model.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-view-model.js')
        File.copy(source=source_js, target=target_js, backup_files=True)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application']
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        messages = "App with Kotlin enabled and kotlin jar not build correctly! Logs: "
        assert test_result, messages + File.read(log.log_file)
        error_message = "Analytics data should NOT be generated when gatherAnalyticsData is not set!"
        assert not File.exists(ANALYTICS_FILE), error_message

    def test_456_analytics_working_corrext_when_property_is_set_without_Kotlin(self):
        """
        Support gradle.properties file for enable Kotlin
        https://github.com/NativeScript/android-runtime/issues/1459
        https://github.com/NativeScript/android-runtime/issues/1463
        """
        Adb.clear_logcat(self.emulator.id)
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                         'android-runtime-1463-1459', 'analytics', 'gradle.properties')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)

        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application']
        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        messages = "App with Kotlin enabled and kotlin jar not build correctly! Logs: "
        assert test_result, messages + File.read(log.log_file)
        error_message = "Analytics data should be generated when gatherAnalyticsData is set!"
        assert File.exists(ANALYTICS_FILE), error_message
        with open(ANALYTICS_FILE, "r") as read_file:
            data = json.load(read_file)
            error_message = "kotlinUsage->hasKotlinRuntimeClasses is not set to False! Analytics is not correct!"
            assert data["kotlinUsage"]["hasKotlinRuntimeClasses"] is False, error_message
            error_message = "kotlinUsage->hasUseKotlinPropertyInApp is not set to True! Analytics is not correct!"
            assert data["kotlinUsage"]["hasUseKotlinPropertyInApp"] is False, error_message

    def test_457_gradle_hooks(self):
        """
        Test gradle hooks works correctly
        https://docs.nativescript.org/core-concepts/android-runtime/advanced-topics/gradle-hooks
        """
        source_app_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                         'android-runtime-gradle-hooks', 'app.gradle')
        target_app_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android', 'app.gradle')
        File.copy(source=source_app_gradle, target=target_app_gradle, backup_files=True)

        source_build_script_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                                  'android-runtime-gradle-hooks', 'buildscript.gradle')
        target_build_script_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source_build_script_gradle, target=target_build_script_gradle, backup_files=True)

        source_build_script_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                                  'android-runtime-gradle-hooks', 'before-plugins.gradle')
        target_build_script_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source_build_script_gradle, target=target_build_script_gradle, backup_files=True)

        source_build_script_gradle = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                                  'android-runtime-gradle-hooks', 'gradle.properties')
        target_build_script_gradle = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'App_Resources', 'Android')
        File.copy(source=source_build_script_gradle, target=target_build_script_gradle, backup_files=True)

        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files',
                                   'sample-plugin', 'src')
        Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)

        result = Tns.build_android(os.path.join(TEST_RUN_HOME, APP_NAME), verify=True).output
        log_regex = r"""MESSAGE: buildscript\.gradle in app is applied!
.+
MESSAGE: buildscript\.gradle in plugin is applied!
.+
.+
MESSAGE: before-plugins\.gradle is applied!
Test variable is set to true in plugin before-plugins\.gradle
MESSAGE: Plugin include gradle is applied!
Test variable is set to true in plugin include\.gradle
.+
MESSAGE: app\.gradle is applied!
Test variable is set to true in plugin app\.gradle"""  # noqa: E501
        Assert.assert_with_regex(result, log_regex)

        Tns.plugin_remove("sample-plugin", verify=False, path=APP_NAME)
