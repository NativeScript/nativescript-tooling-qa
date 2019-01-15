"""
Environment type.
"""
from aenum import IntEnum


class EnvironmentType(IntEnum):
    _init_ = 'value string'

    PR = 0, 'pr'
    NEXT = 1, 'next'
    RC = 2, 'rc'
    LIVE = 3, 'latest'

    def __str__(self):
        return self.string
