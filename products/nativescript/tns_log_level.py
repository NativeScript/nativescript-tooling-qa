"""
Tns log level enum.
"""
from aenum import Enum


class TnsLogLevel(Enum):
    _init_ = 'value string'

    TRACE = 1, 'trace'
    DEBUG = 2, 'debug'
    INFO = 3, 'info'

    def __str__(self):
        return self.string
