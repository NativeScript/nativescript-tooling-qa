"""
Host OS enum.
"""
from aenum import IntEnum


class OSType(IntEnum):
    _init_ = 'value string'

    WINDOWS = 1, 'Windows'
    LINUX = 2, 'Linux'
    OSX = 3, 'macOS'

    def __str__(self):
        return self.string
