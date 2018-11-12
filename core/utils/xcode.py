"""
A wrapper around Xcode.
"""
from core.utils.process import Run
from core.utils.version import Version


class Xcode(object):
    @staticmethod
    def cache_clean():
        """
        Cleanup Xcode cache and derived data
        """
        Run.command(cmd="rm -rf ~/Library/Developer/Xcode/DerivedData/*")

    @staticmethod
    def get_version():
        """
        Get Xcode version
        :return: Version as int.
        """
        # noinspection SpellCheckingInspection
        result = Run.command(cmd='xcodebuild -version').output.splitlines()[0].replace(' ', '').replace('Xcode', '')
        return Version.get(result)
