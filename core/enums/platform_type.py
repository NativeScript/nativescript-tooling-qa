"""
{N} Platform Type.
"""
from aenum import IntEnum


class Platform(IntEnum):
    _init_ = 'value string'

    ANDROID = 1, 'android'
    IOS = 2, 'ios'
    NONE = 3, ''
    BOTH = 4, 'ios and android'

    def __str__(self):
        return self.string
