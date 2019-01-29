"""
Enum for build types.
"""
from aenum import IntEnum


class SyncType(IntEnum):
    _init_ = 'value string'

    REFRESH = 1, 'refresh'  # Only refresh is performed.
    RESTART = 2, 'restart'  # Restart of the app (its process) is performed.
    REINSTALL = 3, 're-install'  # App is re-installed on the device.

    def __str__(self):
        return self.string
