"""
Device type enum.
"""
from aenum import Enum


class DeviceType(Enum):
    _init_ = 'value string'

    EMU = 1, 'emulator'
    SIM = 2, 'simulator'
    ANDROID = 3, 'android device'
    IOS = 3, 'ios device'

    def __str__(self):
        return self.string
