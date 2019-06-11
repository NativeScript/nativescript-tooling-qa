import os

from core.base_test.tns_test import TnsTest
from core.enums.os_type import OSType
from core.settings import Settings
from data.templates import Template
from products.nativescript.app import App
from products.nativescript.tns import Tns
from products.nativescript.tns_assert import TnsAssert


# noinspection PyMethodMayBeStatic
class DoctorTests(TnsTest):
    APP_NAME = Settings.AppName.DEFAULT
    ANDROID_HOME = os.environ.get('ANDROID_HOME')
    JAVA_HOME = os.environ.get('JAVA_HOME')

    @classmethod
    def setUpClass(cls):
        TnsTest.setUpClass()

    def setUp(self):
        TnsTest.setUp(self)
        os.environ['ANDROID_HOME'] = self.ANDROID_HOME
        os.environ['JAVA_HOME'] = self.JAVA_HOME

    @classmethod
    def tearDownClass(cls):
        TnsTest.tearDownClass()

    def test_001_doctor(self):
        result = Tns.doctor()
        assert result.exit_code == 0, 'Doctor exit with non zero exit code.'

        output = result.output
        assert 'No issues were detected.' in output
        assert 'Your ANDROID_HOME environment variable is set and points to correct directory.' in output
        assert 'Your adb from the Android SDK is correctly installed.' in output
        assert 'The Android SDK is installed.' in output
        assert 'A compatible Android SDK for compilation is found.' in output
        assert 'Javac is installed and is configured properly.' in output
        assert 'The Java Development Kit (JDK) is installed and is configured properly.' in output
        if Settings.HOST_OS != OSType.OSX:
            assert 'Local builds for iOS can be executed only on a macOS system. To build for iOS on a different ' \
                   'operating system, you can use the NativeScript cloud infrastructure.' in output
        else:
            assert 'Xcode is installed and is configured properly.' in output
            assert 'xcodeproj is installed and is configured properly.' in output
            assert 'CocoaPods are installed.' in output
            assert 'CocoaPods update is not required.' in output
            assert 'CocoaPods are configured properly.' in output
            assert 'Your current CocoaPods version is newer than 1.0.0' in output
            assert 'Python installed and configured correctly.' in output
            assert "The Python 'six' package is found." in output

    def test_200_doctor_show_warning_when_new_components_are_available(self):
        result = Tns.create(app_name=self.APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=False, verify=False)
        TnsAssert.created(app_name=self.APP_NAME, output=result.output, theme=False, webpack=False)
        Tns.platform_add_android(app_name=self.APP_NAME, version='4')
        App.install_dependency(app_name=self.APP_NAME, dependency='tns-core-modules', version='4')

        doctor_result = Tns.doctor(app_name=self.APP_NAME)
        doctor_output = doctor_result.output

        info_result = Tns.info(app_name=self.APP_NAME)
        info_output = info_result.output

        for output in (doctor_output, info_output):
            assert 'Update available for component tns-core-modules' in output
            assert 'Update available for component tns-android' in output

    def test_400_doctor_should_detect_wrong_path_to_android_sdk(self):
        os.environ['ANDROID_HOME'] = 'WRONG_PATH'
        output = Tns.doctor().output
        assert 'There seem to be issues with your configuration.' in output
        assert 'The ANDROID_HOME environment variable is not set or it points to a non-existent directory' in output

    def test_401_doctor_should_detect_wrong_path_to_java(self):
        os.environ['JAVA_HOME'] = 'WRONG_PATH'
        output = Tns.doctor().output
        assert "Error executing command 'javac'." in output
        assert 'The Java Development Kit (JDK) is not installed or is not configured properly.' in output
