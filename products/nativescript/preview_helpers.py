import os
import re
import urllib
from core.enums.platform_type import Platform
from core.settings import Settings
from core.settings.Settings import TEST_SUT_HOME, TEST_RUN_HOME
from core.utils.file_utils import File
from core.utils.device.simctl import Simctl
from core.utils.device.adb import Adb
from core.utils.run import run

class Preview(object):

    @staticmethod
    def get_app_packages():
        """Copy Preview App packages from Shares to local folder"""
        File.copy(src=Settings.Packages.PREVIEW_APP_IOS, target=TEST_SUT_HOME)
        File.copy(src=Settings.Packages.PREVIEW_APP_ANDROID, target=TEST_SUT_HOME)
        File.copy(src=Settings.Packages.PLAYGROUND_APP_IOS, target=TEST_SUT_HOME)
        File.copy(src=Settings.Packages.PLAYGROUND_APP_ANDROID, target=TEST_SUT_HOME)

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
            #Unpack the .tgz file to get the nsplaydev.app
            File.unpack_tar(os.path.join(TEST_SUT_HOME, 'nsplaydev.tgz'), TEST_SUT_HOME)
            Simctl.install(device_info, package_ios)
        elif platform is Platform.ANDROID:
            Adb.install(package_android, device_info)

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
            Adb.install(package_android, device_info)

    @staticmethod
    def get_url(output):
        """Get preview URL form tns log.This is the url you need to load in Preview app
           in order to see and sync your project"""
        url = re.findall("(nsplay[^\s']+)", output)[0]
        url = urllib.unquote(url)
        url = url.replace('?', '\?')
        url = url.replace('&', '\&')
        return url

    @staticmethod
    def run_app(url, device_id, platform):
        """Runs your project in the Preview App on simulator or emulator"""
        if platform is Platform.IOS:
            cmd = "xcrun simctl openurl {0} {1}.".format(device_id, url)
            result = run(cmd)
            assert not 'error' in result.output
        elif platform is Platform.ANDROID:
            cmd = 'adb -s {0} shell am start -a android.intent.action.VIEW -d \
            "{1}" org.nativescript.preview'.format(device_id, url)
            result = run(cmd)
            assert not 'error' in result.output

    @staticmethod
    def dismiss_simulator_alert():
        """When preview url is loaded in simulator there is alert for confirmation.
           This method will dismiss it. It is implemented only for one instance of simulator for the moment"""
        dismiss_sim_alert = os.path.join(TEST_RUN_HOME, 'data', 'scripts', 'send_enter_to_simulator.scpt')
        command = "osascript " + dismiss_sim_alert
        run(command)
