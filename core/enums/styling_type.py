"""
Styling type enum.
"""
from aenum import IntEnum


class StylingType(IntEnum):
    _init_ = 'value string'

    CSS = 1, 'css'
    SCSS = 2, 'scss'

    def __str__(self):
        return self.string
