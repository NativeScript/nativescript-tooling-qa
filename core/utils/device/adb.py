import logging
import os
import time

from core.enums.os_type import OSType
from core.settings import Settings
from core.utils.file_utils import File
from core.utils.process import Process
from utils.run import run

ANDROID_HOME = os.environ.get('ANDROID_HOME')
ADB_PATH = os.path.join(ANDROID_HOME, 'platform-tools', 'adb')


# noinspection PyShadowingBuiltins
class Adb(object):
    @staticmethod
    def __run_adb_command(command, id=None, wait=True, timeout=60, fail_safe=False, log_level=logging.DEBUG):
        if id is None:
            command = '{0} {1}'.format(ADB_PATH, command)
        else:
            command = '{0} -s {1} {2}'.format(ADB_PATH, id, command)
        return run(cmd=command, wait=wait, timeout=timeout, fail_safe=fail_safe, log_level=log_level)

    @staticmethod
    def __get_ids(include_emulator=False):
        """
        Get IDs of available android devices.
        """
        devices = []
        output = Adb.__run_adb_command('devices -l').output
        '''
        Example output:
        emulator-5554          device product:sdk_x86 model:Android_SDK_built_for_x86 device:generic_x86
        HT46BWM02644           device usb:336592896X product:m8_google model:HTC_One_M8 device:htc_m8
        '''
        for line in output.splitlines():
            if 'model' in line and ' device ' in line:
                id = line.split(' ')[0]
                if include_emulator:
                    devices.append(id)
        return devices

    @staticmethod
    def restart():
        Adb.__run_adb_command('kill-server')
        Process.kill(proc_name='adb')
        Adb.__run_adb_command('start-server')

    @staticmethod
    def get_devices(include_emulators=False):
        pass

    @staticmethod
    def is_running(id):
        """
        Check if device is is currently running.
        :param id: Device id.
        :return: True if running, False if not running.
        """
        if Settings.HOST_OS is OSType.WINDOWS:
            command = "shell dumpsys window windows | findstr mFocusedApp"
        else:
            command = "shell dumpsys window windows | grep -E 'mFocusedApp'"
        result = Adb.__run_adb_command(command=command, id=id, timeout=10, fail_safe=True)
        if 'ActivityRecord' in result.output:
            return True
        else:
            return False

    @staticmethod
    def wait_until_boot(id, timeout=180, check_interval=3):
        """
        Wait android device/emulator is up and running.
        :param id: Device identifier.
        :param timeout: Timeout until device is ready (in seconds).
        :param check_interval: Sleep specified time before check again.
        :return: True if device is ready before timeout, otherwise - False.
        """
        booted = False
        start_time = time.time()
        end_time = start_time + timeout
        while not booted:
            time.sleep(check_interval)
            booted = Adb.is_running(id=id)
            if (booted is True) or (time.time() > end_time):
                break
        return booted

    @staticmethod
    def reboot(id):
        Adb.__run_adb_command(command='reboot', id=id)
        Adb.wait_until_boot(id=id)

    @staticmethod
    def prevent_screen_lock(id):
        """
        Disable screen lock after time of inactivity.
        :param id: Device identifier.
        """
        Adb.__run_adb_command(command='shell settings put system screen_off_timeout -1', id=id)

    @staticmethod
    def pull(id, source, target):
        return Adb.__run_adb_command(command='pull {0} {1}'.format(source, target), id=id)

    @staticmethod
    def get_page_source(id):
        temp_file = os.path.join(Settings.TEST_OUT_HOME, 'window_dump.xml')
        File.clean(temp_file)
        Adb.__run_adb_command(command='shell rm /sdcard/window_dump.xml', id=id)
        result = Adb.__run_adb_command(command='shell uiautomator dump', id=id)
        if 'UI hierchary dumped to' in result.output:
            time.sleep(1)
            Adb.pull(id=id, source='/sdcard/window_dump.xml', target=temp_file)
            if File.exists(temp_file):
                return File.read(temp_file)
            else:
                return ''
        else:
            """
            Sometimes adb shell uiatomator dump fails, for example with:
            adb: error: remote object '/sdcard/window_dump.xml' does not exist
            In such cases return empty string.
            """
            return ''

    # noinspection PyPep8Naming
    @staticmethod
    def is_text_visible(id, text, case_sensitive=False):
        import xml.etree.ElementTree as ET
        page_source = Adb.get_page_source(id)
        if page_source is not '':
            xml = ET.ElementTree(ET.fromstring(page_source))
            elements = xml.findall("//node[@text]")
            if len(elements) > 0:
                for e in elements:
                    if case_sensitive:
                        if text in e.attrib['text']:
                            return True
                    else:
                        if text.lower() in e.attrib['text'].lower():
                            return True
        return False

    @staticmethod
    def get_screen(id, file_path):
        File.clean(path=file_path)
        if Settings.OSType == OSType.WINDOWS:
            Adb.__run_adb_command(command='exec-out screencap -p > ' + file_path, id=id, log_level=logging.DEBUG)
        else:
            Adb.__run_adb_command(command='shell rm /sdcard/screen.png', id=id)
            Adb.__run_adb_command(command='shell screencap -p /sdcard/screen.png', id=id)
            Adb.pull(id=id, source='/sdcard/screen.png', target=file_path)
        if File.exists(file_path):
            return
        else:
            raise Exception('Failed to get screen of {0}.'.format(id))

    @staticmethod
    def get_device_version(id):
        result = Adb.__run_adb_command(command='shell getprop ro.build.version.release', id=id)
        if result.exit_code is 0:
            return result.output
        else:
            raise Exception('Failed to get version of {0}.'.format(id))
