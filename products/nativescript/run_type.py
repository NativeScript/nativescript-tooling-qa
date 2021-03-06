"""
Enum for build types.
"""
from aenum import IntEnum


class RunType(IntEnum):
    _init_ = 'value string'

    SKIP = 1, 'skip'  # Prepare is skipped at all (no files changed).
    INCREMENTAL = 2, 'incremental'  # Some js/xml/css file is changed and incremental prepare is triggered.
    FULL = 3, 'full'  # Full prepare. Rebuild native frameworks.
    FIRST_TIME = 4, 'full (no platforms)'  # When platforms are not added to project prepare should add them.
    JUST_LAUNCH = 5, 'just launch'  # When you build with just launch.
    UNKNOWN = 9, 'unknown'  # When you are not sure what is the run type.

    def __str__(self):
        return self.string
