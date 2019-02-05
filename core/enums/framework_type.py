"""
Test framework type enum.
"""
from aenum import IntEnum


class FrameworkType(IntEnum):
    _init_ = 'value string'

    JASMINE = 1, 'jasmine'
    MOCHA = 2, 'mocha'
    QUNIT = 3, 'qunit'

    def __str__(self):
        return self.string
