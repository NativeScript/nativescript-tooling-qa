import os
import re
import time

from core.enums.device_type import DeviceType
from core.enums.platform_type import Platform
from core.log.log import Log
from core.settings import Settings
from core.settings.Settings import TEST_SUT_HOME, TEST_RUN_HOME
from core.utils.device.adb import Adb
from core.utils.device.simctl import Simctl
from core.utils.file_utils import File
from core.utils.run import run
from products.nativescript.tns import Tns
from products.nativescript.tns_logs import TnsLogs


class Preview(object):

    @staticmethod
    def get_app_packages():
        """Copy Preview App packages from Shares to local folder"""
        File.copy(source=Settings.Packages.PREVIEW_APP_IOS, target=TEST_SUT_HOME)
        File.copy(source=Settings.Packages.PREVIEW_APP_ANDROID, target=TEST_SUT_HOME)
        File.copy(source=Settings.Packages.PLAYGROUND_APP_IOS, target=TEST_SUT_HOME)
        File.copy(source=Settings.Packages.PLAYGROUND_APP_ANDROID, target=TEST_SUT_HOME)

    @staticmethod
    def unpack_ios_simulator_packages():
        """Unpack the .tgz file to get the nsplaydev.app"""
        File.unpack_tar(os.path.join(TEST_SUT_HOME, 'nsplaydev.tgz'), TEST_SUT_HOME)
        File.unpack_tar(os.path.join(TEST_SUT_HOME, 'nsplay.tgz'), TEST_SUT_HOME)

    @staticmethod
    def install_preview_app(device_info, platform):
        """Installs Preview App on emulator and simulator"""
        package_android = os.path.join(TEST_SUT_HOME, 'app-universal-release.apk')
        package_ios = os.path.join(TEST_SUT_HOME, 'nsplaydev.app')
        if platform is Platform.IOS:
            # Unpack the .tgz file to get the nsplaydev.app
            File.unpack_tar(os.path.join(TEST_SUT_HOME, 'nsplaydev.tgz'), TEST_SUT_HOME)
            Simctl.install(device_info, package_ios)
        elif platform is Platform.ANDROID:
            Adb.install(package_android, device_info.id)

    @staticmethod
    def install_preview_app_no_unpack(device_info, platform, uninstall=True):
        """Installs Preview App on emulator and simulator"""
        package_android = os.path.join(TEST_SUT_HOME, 'app-universal-release.apk')
        package_ios = os.path.join(TEST_SUT_HOME, 'nsplaydev.app')
        if platform is Platform.IOS:
            if uninstall:
                Simctl.uninstall(device_info, Settings.Packages.PREVIEW_APP_ID)
            Simctl.install(device_info, package_ios)
        elif platform is Platform.ANDROID:
            if uninstall:
                Adb.uninstall(Settings.Packages.PREVIEW_APP_ID, device_info.id, False)
            Adb.install(package_android, device_info.id)

    @staticmethod
    def install_playground_app(device_info, platform):
        """Installs Playground App on emulator and simulator"""
        package_android = os.path.join(TEST_SUT_HOME, "app-release.apk")
        package_ios = os.path.join(TEST_SUT_HOME, 'nsplay.app')
        if platform is Platform.IOS:
            # Unpack the .tgz file to get the nsplay.app
            File.unpack_tar(os.path.join(TEST_SUT_HOME, 'nsplay.tgz'), TEST_SUT_HOME)
            Simctl.install(device_info, package_ios)
        elif platform is Platform.ANDROID:
            Adb.install(package_android, device_info.id)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def get_url(output):
        # pylint: disable=no-member
        # pylint: disable=no-name-in-module
        # pylint: disable=import-error
        """
        Get preview URL form tns log.
        This is the url you need to load in Preview app in order to see and sync your project.
        :param output: Output of `tns preview` command.
        :return: Playground url.
        """
        url = re.findall(r"(nsplay[^\s']+)", output)[0]
        if Settings.PYTHON_VERSION < 3:
            import urllib
            url = urllib.unquote(url)
        else:
            from urllib.parse import unquote
            url = unquote(url, 'UTF-8')
        return url

    @staticmethod
    def run_url(url, device):
        """
        Runs project in the Preview App.
        :param url: Playground url.
        :param device: DeviceInfo object.
        """
        # Url needs to be escaped before open with adb or simctl
        url = url.replace(r'?', r'\?')
        url = url.replace(r'&', r'\&')

        # Run url
        Log.info('Open "{0}" on {1}.'.format(url, device.name))
        if device.type == DeviceType.EMU or device.type == DeviceType.ANDROID:
            cmd = 'shell am start -a android.intent.action.VIEW -d "{0}" org.nativescript.preview'.format(url)
            result = Adb.run_adb_command(command=cmd, device_id=device.id)
            assert 'error' not in result.output
        elif device.type == DeviceType.SIM:
            result = Simctl.run_simctl_command(command='openurl {0} {1}.'.format(device.id, url))
            assert 'error' not in result.output
        else:
            raise NotImplementedError('Open url not implemented for real iOS devices.')

    @staticmethod
    def dismiss_simulator_alert():
        """When preview url is loaded in simulator there is alert for confirmation.
           This method will dismiss it. It is implemented only for one instance of simulator for the moment"""
        dismiss_sim_alert = os.path.join(TEST_RUN_HOME, 'assets', 'scripts', 'send_enter_to_simulator.scpt')
        command = "osascript " + dismiss_sim_alert
        run(command)

    @staticmethod
    def run_app(app_name, platform, device, bundle=False, hmr=False, instrumented=False):
        result = Tns.preview(app_name=app_name, bundle=bundle, hmr=hmr)

        # Read the log and extract the url to load the app on emulator
        log = File.read(result.log_file)
        url = Preview.get_url(log)
        Preview.run_url(url=url, device=device)
        # When you run preview on ios simulator on first run confirmation dialog is shown.
        if device.type == DeviceType.SIM:
            time.sleep(2)
            Preview.dismiss_simulator_alert()

        # Verify logs
        strings = TnsLogs.preview_initial_messages(platform=platform, hmr=hmr, bundle=bundle, instrumented=instrumented)
        TnsLogs.wait_for_log(log_file=result.log_file, string_list=strings)
        return result

    @staticmethod
    def is_running_on_ios(device_info, app_id):
        """
        Get preview URL form tns log.
        This is the url you need to load in Preview app in order to see and sync your project.
        :param device_info: Information about the device we will search in.
        :param app_id: the App ID of the process.
        :return: boolean.
        """
        return Simctl.is_process_running(device_info, app_id)
