"""
Test for specific needs of Android runtime.
"""
# pylint: disable=invalid-name
import os

from core.base_test.tns_test import TnsTest
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File, Folder
from core.utils.wait import Wait
from core.settings.Settings import Emulators, Android, TEST_RUN_HOME, AppName
from core.enums.platform_type import Platform
from data.templates import Template
from products.nativescript.tns import Tns

APP_NAME = AppName.DEFAULT


class AndroidRuntimeInterfaceTests(TnsTest):

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()
        cls.emulator = DeviceManager.Emulator.ensure_available(Emulators.DEFAULT)
        Folder.clean('./' + APP_NAME)

    def tearDown(self):
        TnsTest.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()
        Folder.clean(APP_NAME)

    def test_302_check_if_class_implements_java_interface_javascript(self):
        """
         Test if java class implements java interface
         https://github.com/NativeScript/android-runtime/issues/739
        """
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True)
        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-739',
                                 'javascript', 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js)

        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application',
                   "### TEST PASSED ###"]

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Javascript : Check(instanceof) for java class implements java interface does not work' \
                            '(myRunnable instanceof java.lang.Runnable)'

    def test_303_check_if_class_implements_java_interface_java(self):
        """
         Test if java class implements java interface
         https://github.com/NativeScript/android-runtime/issues/739
        """
        # Change main-page.js so it contains only logging information
        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-739', 'java',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        File.copy(source=source_js, target=target_js)

        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application',
                   "### TEST PASSED ###"]

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'JAVA : Check(instanceof) for java class implements java interface does not work' \
                            '(myRunnable instanceof java.lang.Runnable)'

    def test_320_check_public_method_in_abstract_interface_could_be_called_api23(self):
        """
         Test public method in abstract interface could be called
         https://github.com/NativeScript/android-runtime/issues/1157
        """

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1157',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        if File.exists(target_js):
            File.delete(target_js)
        File.copy(source=source_js, target=target_js)
        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1157',
                                   'API23', 'src')
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)
        output = Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)
        assert "Successfully installed plugin mylib" in output.output, "mylib plugin not installed correctly!"
        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application', '###TEST CALL PUBLIC METHOD IN ABSTRACT INTERFACE PASSED###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Test public method in abstract interface could be called fails for api23!'

    def test_321_check_public_method_in_abstract_interface_could_be_called_api25(self):
        """
         Test public method in abstract interface could be called
         https://github.com/NativeScript/android-runtime/issues/1157
        """

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1157',
                                 'main-page.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'main-page.js')
        if File.exists(target_js):
            File.delete(target_js)
        File.copy(source=source_js, target=target_js)
        plugin_path = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1157',
                                   'API25', 'src')
        Tns.plugin_remove("mylib", verify=False, path=APP_NAME)
        output = Tns.plugin_add(plugin_path, path=APP_NAME, verify=False)
        assert "Successfully installed plugin mylib" in output.output, "mylib plugin not installed correctly!"
        Tns.platform_remove(app_name=APP_NAME, platform=Platform.ANDROID)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)
        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application', '###TEST CALL PUBLIC METHOD IN ABSTRACT INTERFACE PASSED###']

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Test public method in abstract interface could be called fails for api25!'

    def test_322_extends_method_is_working_in_non_native_inheritance(self):
        """
        Test __extends is working non native inheritance
        https://github.com/NativeScript/android-runtime/issues/1181
        """
        Folder.clean(os.path.join(TEST_RUN_HOME, APP_NAME))
        Tns.create(APP_NAME, template=Template.VUE_BLANK.local_package, verify=False)
        Tns.platform_add_android(APP_NAME, framework_path=Android.FRAMEWORK_PATH)

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1181', 'js',
                                 'app.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js')
        if File.exists(target_js):
            File.delete(target_js)
        File.copy(source=source_js, target=target_js)

        log = Tns.run_android(APP_NAME, device=self.emulator.id, wait=False, verify=False, bundle=True)

        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', self.emulator.id,
                   'Successfully synced application',
                   "'NativeScript-Vue has \"Vue.config.silent\" set to true, to see output logs set it to false.'"]

        test_result = Wait.until(lambda: all(string in File.read(log.log_file) for string in strings), timeout=300,
                                 period=5)
        assert test_result, 'Test __extends is working non native inheritance ts code fails!'

        source_js = os.path.join(TEST_RUN_HOME, 'assets', 'runtime', 'android', 'files', 'android-runtime-1181', 'ts',
                                 'app.js')
        target_js = os.path.join(TEST_RUN_HOME, APP_NAME, 'app', 'app.js')
        if File.exists(target_js):
            File.delete(target_js)
        File.copy(source=source_js, target=target_js)

        test_result = Wait.until(
            lambda: "'NativeScript-Vue has \"Vue.config.silent\" set to true, to see output logs set it to false.'"
            in File.read(log.log_file), timeout=300, period=5)

        assert test_result, 'Test extends is working non native inheritance fails for js code!'
