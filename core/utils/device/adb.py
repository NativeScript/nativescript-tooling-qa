import logging
import os

import time

from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.process import Process
from core.utils.run import run

ANDROID_HOME = os.environ.get('ANDROID_HOME')
ADB_PATH = os.path.join(ANDROID_HOME, 'platform-tools', 'adb')


class Adb(object):
    @staticmethod
    def __run_adb_command(command, device_id=None, wait=True, timeout=60, fail_safe=False, log_level=logging.DEBUG):
        if device_id is None:
            command = '{0} {1}'.format(ADB_PATH, command)
        else:
            command = '{0} -s {1} {2}'.format(ADB_PATH, device_id, command)
        return run(cmd=command, wait=wait, timeout=timeout, fail_safe=fail_safe, log_level=log_level)

    @staticmethod
    def __get_ids(include_emulator=False):
        """
        Get IDs of available android devices.
        """
        devices = []
        output = Adb.__run_adb_command('devices -l').output
        # Example output:
        # emulator-5554          device product:sdk_x86 model:Android_SDK_built_for_x86 device:generic_x86
        # HT46BWM02644           device usb:336592896X product:m8_google model:HTC_One_M8 device:htc_m8
        for line in output.splitlines():
            if 'model' in line and ' device ' in line:
                device_id = line.split(' ')[0]
                if include_emulator:
                    devices.append(device_id)
        return devices

    @staticmethod
    def restart():
        Log.info("Restart adb.")
        Adb.__run_adb_command('kill-server')
        Process.kill(proc_name='adb')
        Adb.__run_adb_command('start-server')

    @staticmethod
    def get_devices(include_emulators=False):
        # pylint: disable=unused-argument
        # TODO: Implement it!
        return []

    @staticmethod
    def is_running(device_id):
        """
        Check if device is is currently running.
        :param device_id: Device id.
        :return: True if running, False if not running.
        """
        if Settings.HOST_OS is OSType.WINDOWS:
            command = "shell dumpsys window windows | findstr mFocusedApp"
        else:
            command = "shell dumpsys window windows | grep -E 'mFocusedApp'"
        result = Adb.__run_adb_command(command=command, device_id=device_id, timeout=10, fail_safe=True)
        return bool('ActivityRecord' in result.output)

    @staticmethod
    def wait_until_boot(device_id, timeout=180, check_interval=3):
        """
        Wait android device/emulator is up and running.
        :param device_id: Device identifier.
        :param timeout: Timeout until device is ready (in seconds).
        :param check_interval: Sleep specified time before check again.
        :return: True if device is ready before timeout, otherwise - False.
        """
        booted = False
        start_time = time.time()
        end_time = start_time + timeout
        while not booted:
            time.sleep(check_interval)
            booted = Adb.is_running(device_id=device_id)
            if (booted is True) or (time.time() > end_time):
                break
        return booted

    @staticmethod
    def reboot(device_id):
        Adb.__run_adb_command(command='reboot', device_id=device_id)
        Adb.wait_until_boot(device_id=device_id)

    @staticmethod
    def prevent_screen_lock(device_id):
        """
        Disable screen lock after time of inactivity.
        :param device_id: Device identifier.
        """
        Adb.__run_adb_command(command='shell settings put system screen_off_timeout -1', device_id=device_id)

    @staticmethod
    def pull(device_id, source, target):
        return Adb.__run_adb_command(command='pull {0} {1}'.format(source, target), device_id=device_id)

    @staticmethod
    def get_page_source(device_id):
        temp_file = os.path.join(Settings.TEST_OUT_HOME, 'window_dump.xml')
        File.delete(temp_file)
        Adb.__run_adb_command(command='shell rm /sdcard/window_dump.xml', device_id=device_id)
        result = Adb.__run_adb_command(command='shell uiautomator dump', device_id=device_id)
        if 'UI hierchary dumped to' in result.output:
            time.sleep(1)
            Adb.pull(device_id=device_id, source='/sdcard/window_dump.xml', target=temp_file)
            if File.exists(temp_file):
                result = File.read(temp_file)
                File.delete(temp_file)
                return result
            else:
                return ''
        else:
            # Sometimes adb shell uiatomator dump fails, for example with:
            # adb: error: remote object '/sdcard/window_dump.xml' does not exist
            # In such cases return empty string.
            return ''

    # noinspection PyPep8Naming
    @staticmethod
    def is_text_visible(device_id, text, case_sensitive=False):
        import xml.etree.ElementTree as ET
        page_source = Adb.get_page_source(device_id)
        if page_source != '':
            xml = ET.ElementTree(ET.fromstring(page_source))
            elements = xml.findall("//node[@text]")
            if elements:
                for element in elements:
                    if case_sensitive:
                        if text in element.attrib['text']:
                            return True
                    else:
                        if text.lower() in element.attrib['text'].lower():
                            return True
        return False

    @staticmethod
    def get_screen(device_id, file_path):
        File.delete(path=file_path)
        if Settings.HOST_OS == OSType.WINDOWS:
            Adb.__run_adb_command(command='exec-out screencap -p > ' + file_path,
                                  device_id=device_id,
                                  log_level=logging.DEBUG)
        else:
            Adb.__run_adb_command(command="shell screencap -p | perl -pe 's/\\x0D\\x0A/\\x0A/g' > " + file_path,
                                  device_id=device_id)
        if File.exists(file_path):
            return
        else:
            raise Exception('Failed to get screen of {0}.'.format(device_id))

    @staticmethod
    def get_device_version(device_id):
        result = Adb.__run_adb_command(command='shell getprop ro.build.version.release', device_id=device_id)
        if result.exit_code == 0:
            return result.output
        else:
            raise Exception('Failed to get version of {0}.'.format(device_id))

    @staticmethod
    def open_home(device_id):
        cmd = 'shell am start -a android.intent.action.MAIN -c android.intent.category.HOME'
        Adb.__run_adb_command(command=cmd, device_id=device_id)
        Log.info('Open home screen of {0}.'.format(str(device_id)))

    @staticmethod
    def install(apk_path, device_id):
        """
        Install application.
        :param apk_path: File path to .apk.
        :param device_id: Device id.
        """
        result = Adb.__run_adb_command(command='install -r {0} {1}'.format(apk_path, device_id), timeout=60)
        assert 'Success' in result.output, 'Failed to install {0}. Output: {1}'.format(apk_path, result.output)
        Log.info('{0} installed successfully on {1}.'.format(apk_path, device_id))
