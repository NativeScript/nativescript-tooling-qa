"""
Device type enum.
"""
from aenum import Enum


class LogLevel(Enum):
    _init_ = 'value string'

    TRACE = 1, 'trace'
    DEBUG = 2, 'debug'
    INFO = 3, 'info'
    WARN = 4, 'warn'
    ERROR = 5, 'error'

    def __str__(self):
        return self.string
