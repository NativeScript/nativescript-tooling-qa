"""
Application type enum.
"""
from aenum import Enum


class AppType(Enum):
    _init_ = 'value string'

    JS = 1, 'js'
    TS = 2, 'ts'
    NG = 3, 'ng'
    VUE = 4, 'vue'
    SHARED_NG = 5, 'shared_ng'

    def __str__(self):
        return self.string
