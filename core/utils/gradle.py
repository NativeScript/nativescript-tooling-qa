"""
A wrapper around Gradle.
"""

import os

from core.enums.os_type import OSType
from core.log.log import Log
from core.settings import Settings
from core.utils.process import Run, Process


class Gradle(object):
    @staticmethod
    def kill():
        Log.info("Kill gradle processes.")
        if Settings.HOST_OS is OSType.WINDOWS:
            Process.kill(proc_name='java.exe', proc_cmdline='gradle')
        else:
            command = "ps -ef  | grep '.gradle/wrapper' | grep -v grep | awk '{ print $2 }' | xargs kill -9"
            Run.command(cmd=command)

    @staticmethod
    def cache_clean():
        Log.info("Clean gradle cache.")
        if Settings.HOST_OS is OSType.WINDOWS:
            Run.command(cmd="rmdir /s /q {USERPROFILE}\\.gradle".format(**os.environ))
        else:
            Run.command(cmd="rm -rf ~/.gradle")
