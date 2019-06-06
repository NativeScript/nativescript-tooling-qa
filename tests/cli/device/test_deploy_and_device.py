"""
Tests for `tns devices` and `tns deploy` commands.
"""
import os
import unittest
from time import sleep

from core.base_test.tns_run_test import TnsRunTest
from core.enums.device_type import DeviceType
from core.enums.os_type import OSType
from core.enums.platform_type import Platform
from core.settings import Settings
from core.utils.device.adb import Adb
from core.utils.device.device_manager import DeviceManager
from core.utils.file_utils import File
from data.changes import Changes
from data.templates import Template
from products.nativescript.tns import Tns
from products.nativescript.tns_assert import TnsAssert
from products.nativescript.tns_logs import TnsLogs
from products.nativescript.tns_paths import TnsPaths

APP_NAME = Settings.AppName.DEFAULT


# noinspection PyMethodMayBeStatic
class TnsDeviceTests(TnsRunTest):
    ANDROID_DEVICES = DeviceManager.get_devices(device_type=DeviceType.ANDROID)
    assert ANDROID_DEVICES, 'Android devices not found.'
    if Settings.HOST_OS == OSType.OSX:
        IOS_DEVICES = DeviceManager.get_devices(device_type=DeviceType.IOS)
        assert IOS_DEVICES, 'iOS devices not found.'

    PATH = os.environ.get('PATH')
    ANDROID_HOME = os.environ.get('ANDROID_HOME')

    @classmethod
    def setUpClass(cls):
        TnsRunTest.setUpClass()
        Tns.create(app_name=APP_NAME, template=Template.HELLO_WORLD_JS.local_package, update=True, verify=False)
        Tns.platform_add_android(app_name=APP_NAME, framework_path=Settings.Android.FRAMEWORK_PATH)
        if Settings.HOST_OS == OSType.OSX:
            Tns.platform_add_ios(app_name=APP_NAME, framework_path=Settings.IOS.FRAMEWORK_PATH)

    def setUp(self):
        TnsRunTest.setUp(self)
        os.environ['PATH'] = self.PATH
        os.environ['ANDROID_HOME'] = self.ANDROID_HOME

    def tearDown(self):
        TnsRunTest.tearDown(self)
        os.environ['PATH'] = self.PATH
        os.environ['ANDROID_HOME'] = self.ANDROID_HOME

    def test_100_list_devices(self):
        # Verify both device and devices are valid and return correct results
        device_result = Tns.exec_command(command='device')
        devices_result = Tns.exec_command(command='devices')

        for result in [device_result, devices_result]:
            # Verify emulator and simulator are listed as devices
            assert self.emu.name in result.output
            assert self.emu.id in result.output
            if Settings.HOST_OS == OSType.OSX:
                assert self.sim.name in result.output
                assert self.sim.id in result.output

            # Verify real devices
            for android in self.ANDROID_DEVICES:
                assert android.id in result.output
            if Settings.HOST_OS == OSType.OSX:
                for ios in self.IOS_DEVICES:
                    assert ios.id in result.output

        # Ensure when simulator is stopped real device are listed
        if Settings.HOST_OS is OSType.OSX:
            DeviceManager.Simulator.stop()
            sleep(10)
            result = Tns.exec_command(command='device')
            assert self.sim.name not in result.output
            assert self.sim.id not in result.output
            for ios in self.IOS_DEVICES:
                assert ios.id in result.output

    def test_200_list_available_devices(self):
        result = Tns.exec_command(command='device android --available-devices')
        assert self.emu.name in result.output
        assert self.emu.id in result.output
        assert Settings.Emulators.EMU_API_19.avd in result.output
        assert str(Settings.Emulators.EMU_API_19.os_version) in result.output
        if Settings.HOST_OS == OSType.OSX:
            DeviceManager.Simulator.stop()
            result = Tns.exec_command(command='device ios --available-devices')
            assert self.sim.name in result.output
            assert self.sim.id in result.output
            assert str(self.sim.version) in result.output
            assert 'Device Name' and 'Platform' and 'Version' and 'Device Identifier' in result.output
            assert 'iPhone' and 'iPad' in result.output
            assert not DeviceManager.Simulator.is_running(
                Settings.Simulators.DEFAULT), 'Simulator is started after "tns device ios --available-devices"!'

    def test_300_deploy_list_and_run_applications(self):
        # Deploy test application
        app_id = TnsPaths.get_bundle_id(app_name=APP_NAME)
        result = Tns.deploy(app_name=APP_NAME, platform=Platform.ANDROID, just_launch=True, wait=True)
        for device in self.ANDROID_DEVICES:
            assert device.id in result.output
        if Settings.HOST_OS == OSType.OSX:
            result = Tns.deploy(app_name=APP_NAME, platform=Platform.IOS, just_launch=True, wait=True)
            for device in self.IOS_DEVICES:
                assert device.id in result.output

        # Verify list-applications command list default android apps and the app we've just deployed
        for device in self.ANDROID_DEVICES:
            result = Tns.exec_command('device list-applications --device {0}'.format(device.id))
            assert 'com.android' in result.output
            assert app_id in result.output

        # Verify `device run <bundle-id>` will start the app
        device = self.ANDROID_DEVICES[0]
        Adb.stop_application(device_id=device.id, app_id=app_id)
        assert not device.is_text_visible(text=Changes.JSHelloWord.JS.old_value), 'Failed to stop the app.'
        Tns.exec_command(command='device run {0}'.format(app_id), device=device.id, wait=True, just_launch=True)
        device.wait_for_text(text=Changes.JSHelloWord.JS.old_value)

        # Get Android device logs
        result = Tns.exec_command(command='device log', device=device.id, wait=False)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=['beginning of'], timeout=120)
        assert 'I' or 'D' or 'W' in File.read(result.log_file), 'Log does not contain INFO, DEBUG or WARN messages.'

        # Get iOS device logs
        if Settings.HOST_OS == OSType.OSX:
            device = self.IOS_DEVICES[0]
            result = Tns.exec_command(command='device log', device=device.id, wait=False)
            TnsLogs.wait_for_log(log_file=result.log_file, string_list=['>:'], timeout=120)
            assert "<Notice>:" or "<Error>:" in File.read(result.log_file), 'tns device log fails to get ios logs.'

    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, 'Skip on Windows machines.')
    def test_310_device_log_android_two_devices(self):
        if len(self.ANDROID_DEVICES) + len(self.IOS_DEVICES) > 2:
            result = Tns.exec_command('device log')
            assert 'More than one device found. Specify device explicitly.' in result.output

    def test_400_device_and_deploy_invalid_platform(self):
        invalid_platform = 'fakePlatform'
        result = Tns.exec_command(command='device {0}'.format(invalid_platform))
        assert "'{0}' is not a valid device platform.".format(invalid_platform) in result.output

    def test_402_deploy_invalid_platform(self):
        result = Tns.exec_command(command='deploy platform', path=APP_NAME)
        assert "Invalid platform platform. Valid platforms are ios or android." in result.output

    def test_403_deploy_command_with_invalid_device_id(self):
        invalid_device_id = 'fakeDevice'
        output = Tns.exec_command(command='deploy android --device {0}'.format(invalid_device_id),
                                  path=APP_NAME).output
        assert "Emulator start failed with: No emulator image available for device identifier 'fakeDevice'" in output
        assert "To list currently connected devices and verify that the specified identifier exists" in output

    @unittest.skipIf(Settings.HOST_OS == OSType.WINDOWS, 'Skip on Windows machines.')
    def test_410_list_devices_without_android_sdk(self):
        path_without_android = ''
        for path in self.PATH.split(':'):
            if self.ANDROID_HOME not in path:
                path_without_android = path_without_android + path + ':'
        os.environ['PATH'] = path_without_android
        os.environ['ANDROID_HOME'] = 'WRONG_PATH'
        result = Tns.exec_command(command='device')
        assert self.emu.name in result.output
        assert self.emu.id in result.output
