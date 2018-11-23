"""
Environment type.
"""
from aenum import Enum


class EnvironmentType(Enum):
    _init_ = 'value string'

    NEXT = 1, 'next'
    RC = 2, 'rc'
    LIVE = 3, 'latest'

    def __str__(self):
        return self.string
