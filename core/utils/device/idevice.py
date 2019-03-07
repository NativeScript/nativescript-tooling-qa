# pylint: disable=unused-argument
from core.log.log import Log
from core.utils.run import run


class IDevice(object):

    @staticmethod
    def get_devices():
        """
        Get available iOS devices (only real devices).
        """
        device_ids = list()
        output = run(cmd='idevice_id --list', timeout=60).output
        for line in output.splitlines():
            command = 'instruments -s | grep {0}'.format(line)
            check_connected = run(cmd=command, timeout=30).output
            if 'null' not in check_connected:
                device_ids.append(line)
            else:
                message = '{0} is not trusted!'.format(line)
                Log.error(message)
        return device_ids

    @staticmethod
    def is_text_visible(device_id, text):
        return False

    @staticmethod
    def get_screen(device_id, file_path):
        return None
