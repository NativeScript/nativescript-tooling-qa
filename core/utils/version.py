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
