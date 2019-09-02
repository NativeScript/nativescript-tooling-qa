"""
Host OS enum.
"""
from aenum import IntEnum


class OSType(IntEnum):
    _init_ = 'value string'

    WINDOWS = 1, 'Windows'
    LINUX = 2, 'Linux'
    OSX = 3, 'macOS'
    OSX_CATALINA = 4, 'macOSCatalina'

    def __str__(self):
        return self.string
