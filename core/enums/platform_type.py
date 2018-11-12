"""
{N} Platform Type.
"""
from aenum import Enum


class Platform(Enum):
    _init_ = 'value string'

    ANDROID = 1, 'android'
    IOS = 2, 'ios'
    NONE = 3, ''

    def __str__(self):
        return self.string
