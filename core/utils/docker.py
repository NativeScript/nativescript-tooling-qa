import os
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
            docker = os.environ.get("DOCKER_HOME")
            if not Process.is_running_by_name('Docker Desktop'):
                if docker is not None:
                    cmd = '"' + os.path.join(docker, 'Docker Desktop.exe') + '"'
                    run(cmd=cmd, wait=False)
                    Log.info('Starting docker!')
                else:
                    cmd = r'"C:\Program Files\Docker\Docker\Docker Desktop.exe"'
                    run(cmd=cmd, wait=False)
                    Log.info('Starting docker!')
        elif OSUtils.is_catalina():
            if not Process.is_running_by_name('Docker'):
                cmd = 'open --background -a Docker'
                run(cmd=cmd, wait=False)
                Log.info('Starting docker!')
        else:
            Log.info('No need to start docker!')

    @staticmethod
    def stop():
        if OSUtils.is_catalina():
            Process.kill('Docker')
