"""
A wrapper around Xcode.
"""
from core.utils.version import Version
from utils.run import run


class Xcode(object):
    @staticmethod
    def cache_clean():
        """
        Cleanup Xcode cache and derived data
        """
        run(cmd="rm -rf ~/Library/Developer/Xcode/DerivedData/*")

    @staticmethod
    def get_version():
        """
        Get Xcode version
        :return: Version as int.
        """
        result = run(cmd='xcodebuild -version').output.splitlines()[0].replace(' ', '').replace('Xcode', '')
        return Version.get(result)
