# pylint: disable=unused-argument

from core.log.log import Log
from core.utils.file_utils import File
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
    def get_name(device_id):
        result = run(cmd='ideviceinfo -u {0} | grep ProductType'.format(device_id))
        if result.exit_code == 0:
            return result.output.replace(',', '').replace('ProductType:', '').strip(' ')
        else:
            return device_id

    @staticmethod
    def get_screen(device_id, file_path):
        """
        Save screen of iOS real device.
        :param device_id: Device identifier.
        :param file_path: Path where image will be saved.
        """
        tiff_image_path = file_path.replace('.png', '.tiff')

        run(cmd="idevicescreenshot -u {0} {1}".format(device_id, tiff_image_path))
        run(cmd="sips -s format png {0} --out {1}".format(tiff_image_path, file_path))
        File.clean(tiff_image_path)

    @staticmethod
    def get_log(device_id):
        """
        Get device logs as string.
        :param device_id: Device id.
        """
        return device_id
