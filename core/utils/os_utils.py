import platform

from core.enums.os_type import OSType
from core.settings.Settings import HOST_OS
from core.utils.version import Version


class OSUtils(object):
    @staticmethod
    def get_version():
        """
        Get OS version
        :return: Version as double.
        """
        result = platform.release()
        version_string = ".".join(result.split(".", 2)[:2])
        return Version.get(version_string)

    @staticmethod
    def is_catalina():
        """
        Check if current os is macOS Catalina.
        :return: True if host OS is Catalina.
        """
        return HOST_OS is OSType.OSX and OSUtils.get_version() >= 19.0
