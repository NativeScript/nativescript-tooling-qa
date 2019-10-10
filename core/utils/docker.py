from core.utils.process import Process
from core.utils.run import run
from core.utils.os_utils import OSUtils
from core.log.log import Log
from core.settings import Settings
from core.enums.os_type import OSType


class Docker(object):

    @staticmethod
    def start():
        if Settings.HOST_OS == OSType.WINDOWS:
            cmd = r'"C:\Program Files\Docker\Docker\Docker Desktop.exe"'
            run(cmd=cmd, wait=False)
        if OSUtils.is_catalina():
            cmd = 'open --background -a Docker'
            run(cmd=cmd, wait=False)
        else:
            Log.info('No need to start docker!')

    @staticmethod
    def stop():
        if Settings.HOST_OS == OSType.WINDOWS:
            Process.kill('Docker Desktop')
            Process.kill('Docker.Watchguard')
            Process.kill('com.docker.backend')
            Process.kill('com.docker.proxy')
        if OSUtils.is_catalina():
            Process.kill('Docker')