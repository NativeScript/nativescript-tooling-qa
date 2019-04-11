"""
Version utils
"""
import platform

from core.enums.os_type import OSType
from core.settings import Settings


class Version(object):
    @staticmethod
    def get(version):
        """
        Convert version string to float.
        :param version: Version string.
        :return: Version as float.
        """
        split = version.split('.')
        if split:
            return float(split[0] + '.' + split[1])
        else:
            return float(split[0])

    @staticmethod
    def is_os_mojave():
        """
        Check whether a machine OS is Mac Mojave.
        :return: boolean.
        """
        is_machine_mojave = False
        if Settings.HOST_OS is OSType.OSX:
            version, _, _ = platform.mac_ver()
            version = float('.'.join(version.split('.')[:2]))
            if version == 10.14:
                is_machine_mojave = True

        return is_machine_mojave
